export default async function showSetFileScene() {
    // 刪除 ScreenDiv
    const screenDiv = document.getElementById("screen");
    if (screenDiv) {
        screenDiv.remove();
    } else {
        console.error("Element to remove not found.");
    }

    let model_config = [];
    try {
        const response = await axios.get('http://127.0.0.1:5000/read_model_config');
        console.log(response.data.data.cameras);
        model_config = response.data.data.cameras;
        console.log(model_config)
    } catch (error) {
        console.error(error);
        return; // Exit the function if there's an error
    }

    let screen = `
        <a href="#" class="setFileBut setUpBut" id="setUpBut"><span>Set Up</span></a>
        <a href="#" class="setFileBut updateBut" id="updateBut"><span>Update</span></a>
        <div id="subScreen"></div>
    `;
    let funcScreen = document.getElementById('funcScreen');
    if (funcScreen) {
        funcScreen.innerHTML = screen;
    } else {
        console.error('目標元素不存在');
    }

    // set up and update button anime
    const btn1 = document.querySelector('.setUpBut');
    const btn2 = document.querySelector('.updateBut');
    btn1.onmousemove = function(e) {
        const x = e.pageX - btn1.offsetLeft;
        const y = e.pageY - btn1.offsetTop;
        btn1.style.setProperty('--x', x + 'px');
        btn1.style.setProperty('--y', y + 'px');
    }
    btn2.onmousemove = function(e) {
        const x = e.pageX - btn2.offsetLeft;
        const y = e.pageY - btn2.offsetTop;
        btn2.style.setProperty('--x', x + 'px');
        btn2.style.setProperty('--y', y + 'px');
    }

    let subScreen = document.getElementById('subScreen');
    let checkedname = []; //模型選擇
    let cameraSelect = ""//監視器選擇
    document.getElementById('setUpBut').onclick = function() {
        let sub = `
            <div class="dropdownFont">Camera: </div>
            <div class="dropdown" style="left: 38%; top: 54%;">
                <input type="text" class="text02" readonly placeholder="Select Camera">
                <div class="option">`
        for (let i = 0; i < model_config.length; i++) {
            sub += `
                <div>Camera${i+1}</div>
            `;
        }
        sub+=`
                </div>
            </div>
            <div class="dropdownFont fileFont">File: </div>
            <div class="menu">
                <div class="moduleToggle"><i class="fa-solid fa-plus"></i></div>
        `;
        
        // [衣物辨識 , "黑白名單", 武器辨識, 滑倒檢測, 危險區域]
        const i_class = ["shirt", "address-book", "gun", "person-falling", "person"]
        for (let i=0; i<i_class.length; i++) {
            sub += `
                <label style="--i:${i};">
                    <input type="checkbox" id="${i_class[i]}">
                    <i class="fa-solid fa-${i_class[i]}"></i>
                </label>
            `;
        }
        sub += `
                </div>
            </div>
            <a href="#" class="saveBut" style="left: 55%; top: 52.5%;">Save</a>
        `;
        subScreen.innerHTML = sub;
        
        document.querySelector('.text02').addEventListener('input', function() {
            console.log("text02 input");
            model_config.forEach(config => {
                if(config['name'] === document.querySelector('.text02').value) {
                    config['models'].forEach(model => {
                        if(model == "1") document.getElementById("gun").checked = true;
                        else if(model == "2") document.getElementById("shirt").checked = true;
                        else if(model == "3") document.getElementById("address-book").checked = true;
                        else if (model == "4")document.getElementById("person-falling").checked = true;
                        else if(model == "5") document.getElementById("person").checked = true;

                    });
                }
            });
        });
        
        // 取得模型選擇checkbox
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                checkedname= []
                for (let i of i_class) {
                    if (document.getElementById(i).checked) {
                        // checkedname.push(i);
                        if(i == "gun")  checkedname.push("1");
                        else if(i == "shirt")  checkedname.push("2");
                        else if(i == "address-book")  checkedname.push("3");
                        else if(i == "person-falling")  checkedname.push("4");
                        else if(i == "person")  checkedname.push("5");
                    }
                }
                console.log('Checked items on change:', checkedname);
            });
        });
        // option anime
        function show(a) {
            document.querySelector('.text02').value = a;
        }
       
        let options = document.querySelectorAll('.option div');
        
        options.forEach(option => {
            option.addEventListener('mouseover', function() {
                show(option.innerText);
                cameraSelect = parseInt(option.innerText.split("Camera")[1])-1
                // 在这里处理 config 的逻辑
                model_config.forEach(config => {
                    if(config['name'] === option.innerText.toLowerCase()) {
                        for (let i of i_class) {
                            document.getElementById(i).checked = false;
                        }
                        console.log(config['name'] +","+ option.innerText.toLowerCase())
                        config['models'].forEach(model => {
                            console.log(model)
                            if(model == "1") document.getElementById("gun").checked = true;
                            else if(model == "2") document.getElementById("shirt").checked = true;
                            else if(model == "3") document.getElementById("address-book").checked = true;
                            else if(model == "4") document.getElementById("person-falling").checked = true;
                            else if(model == "5") document.getElementById("person").checked = true;
                        });
                    }
                });
            });
        });
        let dropdown = document.querySelector('.dropdown');
        dropdown.onclick = function() {
            dropdown.classList.toggle('active');
        };
        
        // toggle anime
        let moduleToggle = document.querySelector(".moduleToggle");
        let menu = document.querySelector(".menu");
        moduleToggle.onclick = function() {
            menu.classList.toggle('active')
        }

        // saveBut anime
        const button = document.querySelector('.saveBut');
        button.addEventListener('click', function(e) {
            let x = e.clientX - e.target.offsetLeft;
            let y = e.clientY - e.target.offsetTop;
            let ripples = document.createElement('span');
            ripples.style.left = x + 'px';
            ripples.style.top = y + 'px';
            this.appendChild(ripples);
            let index = cameraSelect
            let models = checkedname
            let save_check = true
            // console.log(cameraSelect)
            // console.log(models)
            model_config.forEach(config => {
                console.log(models)
                console.log(models.includes("4"))
                console.log(config['safearea'].length === 0)
            
                if(config['name'] === document.querySelector('.text02').value.toLowerCase()) {
                    console.log("23")
                    if(models.includes("4") && config['safearea'].length === 0){
                        console.log("4")
                        alert("選擇跌倒偵測時，安全區域不得為空")
                        save_check = false
                    }
                }
            });
            if(save_check == true){
                // 執行結果
                axios.post('http://127.0.0.1:5000/setCameraSetting', Qs.stringify({
                    "name": `camera${index+1}`,
                    "index": index,
                    "models": JSON.stringify(models)
                }), {
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                })
                .then(response => {
                    console.log(response.data);
                    let model_text = ""
                    for(let i = 0;i<response.data['models'].length;i++){
                        if(i>0)  model_text += " , "
                        if(response.data['models'][i] == "1") model_text += "武器辨識模型" 
                        else if(response.data['models'][i] == "2") model_text += "衣物辨識模型"
                        else if(response.data['models'][i] == "3") model_text += "人臉辨識模型"
                        else if(response.data['models'][i] == "4") model_text += "跌倒偵測模型"
                        else if(response.data['models'][i] == "5") model_text += "人流計算模型"
                        
                    } 
                    alert(`${response.data['camera']}修改成功! 
                    模型設置:[${model_text}]`)
                })
                .catch(error => {
                    console.error(error);
                });
    
                setTimeout(() => {
                    ripples.remove()
                }, 1000);
            }
        });
    }

    document.getElementById('updateBut').onclick = function() {
        let sub = `
            <div class="inputBox">
                <input type="text" id="nameInput" required="required">
                <span>Name</span>
            </div>
            <div class="file">Photo: </div>
            <div class="updateScreen">            
                <label for="fileInput" class="fileLabel">Choose Photo</label>
                <input id="fileInput" type="file">
            </div>
            <div class="dropdown fileDropdown">
                <input type="text" class="text02" readonly placeholder="Select Name">
                <div class="option">
                    <div>Name1</div>
                    <div>Name2</div>
                    <div>Name3</div>
                    <div>Name4</div>
                </div>
            </div>
            <a href="#" class="saveBut updSaveBut">Save</a>
        `;

        subScreen.innerHTML = sub;

        // option anime
        function show(a) {
            document.querySelector('.text02').value = a;
        }
        let options = document.querySelectorAll('.option div');
        options.forEach(option => {
            option.addEventListener('mouseover', function() {
                show(option.innerText);
            });
        });
        let dropdown = document.querySelector('.dropdown');
        dropdown.onclick = function() {
            dropdown.classList.toggle('active');
        };

        // saveBut anime
        const button = document.querySelector('.saveBut');
        button.addEventListener('click', async function(e) {
            let x = e.clientX - e.target.offsetLeft;
            let y = e.clientY - e.target.offsetTop;
            let ripples = document.createElement('span');
            ripples.style.left = x + 'px';
            ripples.style.top = y + 'px';
            this.appendChild(ripples);

            setTimeout(() => {
                ripples.remove()
            }, 1000);

            // 1. 獲取名字和圖片的資料
            let nameInput = document.getElementById('nameInput').value;
            let fileInput = document.getElementById('fileInput').files[0];

            if (!nameInput || !fileInput) {
                alert("Please provide both name and photo.");
                return;
            }

            // 2. 創建 FormData 並添加文件
            let formData = new FormData();
            formData.append('name', nameInput);
            formData.append('photo', fileInput);

            // 3. 發送 POST 請求到後端
            // 執行結果
            await axios.post('http://127.0.0.1:5000/submit_face', formData,{
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            })
            // .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                alert('Data submitted successfully!');
            })
            .catch((error) => {
                console.error('Error:', error);
            });

            
        });

    }
}