import screenDivFunc from "../script.js";
const colorList = ['black','blue','brown','cyan','gray','green','orange','pink','purple','red','white','yellow']
const camera_list = ["camera1","camera2","camera3","camera4"]
export default function showSearchScene() {
    // 創建一個空的字典來存儲選擇的值
    let selectedOptions = {
        'camera':[],
        'time':{'start_date':"",'start_time':"",'end_date':"",'end_time':""},
        'shirt':{}
    };
    let screen = `
        <div class="buttons">
    `;
    const i_class = ["camera", "clock", "shirt"]
    for(let i=0; i<i_class.length; i++) {
        screen += `
            <label>
                <input type="radio" name="radio" id="radio${i+1}">
                <span></span>
                <i class="fa-solid fa-${i_class[i]}"></i>
            </label>
        `;
    }
    screen += `
        </div>
        <div id="subScreen"></div>
    `;

    let funcScreen = document.getElementById('funcScreen');
    if (funcScreen) {
        funcScreen.innerHTML = screen;
    } else {
        console.error('目標元素不存在');
    }

    var camera = document.getElementById('radio1');
    var time = document.getElementById('radio2');
    var shirt = document.getElementById('radio3');
    let subScreen = document.getElementById('subScreen');

    // 當 camera 被選中
    camera.addEventListener('change', function() {
        let sub = ``;
        sub += `
            <div class="cameraSel">
        `
        for (let i = 0; i < camera_list.length; i++) {
            const isChecked = selectedOptions['camera'].includes(camera_list[i]) ? 'checked' : ''; // 檢查是否已選擇
            sub += `
                <div>
                    <label>
                        <input type="checkbox" id="${camera_list[i]}" ${isChecked}>
                        <span>Camera${i + 1}</span>
                    </label>
                </div>
            `;
        }
        sub += `</div>`;
        subScreen.innerHTML = sub;
        for(let i=0; i<camera_list.length; i++) {
            document.getElementById(camera_list[i]).addEventListener('change', function() {
                const index = selectedOptions['camera'].indexOf(camera_list[i]);
                if (index !== -1) {
                    selectedOptions['camera'].splice(index, 1);
                } else {
                    selectedOptions['camera'].push(camera_list[i]);
                }
                console.log(selectedOptions['camera'])
            })
        }
    });

    // 當 shirt 被選中
    shirt.addEventListener('change', function() {
        let sub = ``;
        const shirtList = ["long sleeves", "trousers", "short sleeves", "shorts", "hat", "shoe", "pretend", "skirt"]
        sub += `
            <ul class="lightSQ shirtChooser">
        `;
        for(let i=0; i<shirtList.length; i++) {
            sub += `
                <li>
                    <label>
                        ${shirtList[i]}
                        <input type="checkbox" id="${shirtList[i]}">
                        <span class="check"></span>
                    </label>
                    <div id="colorSelector_${shirtList[i]}" class="color-selector">`
            for(let j = 0;j<colorList.length;j++){
                sub += `
                <label class="color-option">
                    <input type="radio" name="${shirtList[i]}-color" value="${colorList[j]}">
                    <span class="color-box" style="background-color: ${colorList[j]};"></span>
                </label>
                `
                // <div class="color-box" style="background-color: ${colorList[j]};"></div>
            }
            sub += `</div>
                </li>`
        }
        sub += `</ul>`;
        subScreen.innerHTML = sub;       
        for(let i=0; i<shirtList.length; i++) {
            if(shirtList[i] in selectedOptions['shirt']){
                document.getElementById(shirtList[i]).checked = true
                console.log(shirtList[i])
                const colorSelector = document.getElementById(`colorSelector_${shirtList[i]}`);
                colorSelector.classList.add('show'); // 添加 'show' 类来触发动画
                const radios = document.querySelectorAll(`input[name="${shirtList[i]}-color"]`);
                radios.forEach(radio => {
                    if (radio.value === selectedOptions['shirt'][shirtList[i]]) {
                        radio.checked = true; // 勾选匹配的 radio 按钮
                    } else {
                        radio.checked = false; // 取消勾选其他 radio 按钮
                    }
                });
            }
            document.getElementById(shirtList[i]).addEventListener('change', function() {
                const colorSelector = document.getElementById(`colorSelector_${shirtList[i]}`);
                if (this.checked) {
                    colorSelector.classList.add('show'); // 添加 'show' 类来触发动画
                } else {
                    colorSelector.classList.remove('show'); // 移除 'show' 类隐藏选择器
                    delete selectedOptions['shirt'][shirtList[i]];
                    console.log(selectedOptions['shirt']);
                }
            });

                // Update the selected color in selectedOptions
            const colorOptions = document.querySelectorAll(`input[name="${shirtList[i]}-color"]`);
            colorOptions.forEach(option => {
                option.addEventListener('change', function() {
                    if (this.checked) {
                        selectedOptions['shirt'][shirtList[i]] = this.value; // Set the selected color
                        // console.log(selectedOptions['shirt']);
                    }
                });
            });
        }
        var hat = document.getElementById('Hat');
        var glass = document.getElementById('Glass');
        var jacket = document.getElementById('Jacket');
        var shirt = document.getElementById('shirt');
        var short = document.getElementById('Short');
        var skirt = document.getElementById('Skirt');
        var shoes = document.getElementById('Shoes');
        var bag = document.getElementById('Bag');
    });
    // 當 time 被選中
    time.addEventListener('change', function() {
        const time_list = ['start_date','start_time','end_date','end_time'];
        let sub = ``;
        sub += `
            <div class="timeScreen">
                <p style="font-size: 35px;"><b>Start</b></p>
                <p>Date: <input type="date" id="start_date"></p>
                <p>Time: <input type="time" id="start_time"></p><br> <!-- 修正这里的引号 -->
                <p style="font-size: 35px;"><b>End</b></p>
                <p>Date: <input type="date" id="end_date"></p>
                <p>Time: <input type="time" id="end_time"></p>
            </div>
            <button id="SelectObjectButton">
                <a href="#" class="saveBut timeSaveBut" >Save</a>
            </button>
        `;
        subScreen.innerHTML = sub;
        //填入已選time資料
        for(let i = 0; i < time_list.length; i++) {
            if (selectedOptions['time'][time_list[i]]) {
                document.getElementById(time_list[i]).value = selectedOptions['time'][time_list[i]];
            }
        }

        for(let i=0; i<time_list.length; i++) {
            document.getElementById(time_list[i]).addEventListener('change', function() {
                selectedOptions['time'][time_list[i]] = document.getElementById(time_list[i]).value;
                console.log(selectedOptions['time'])
            });
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
            let shirt_feature = ""
            console.log("123");
            for(let key in selectedOptions['shirt']){
                if(shirt_feature == ""){
                    shirt_feature += `${selectedOptions['shirt'][key]} ${key.toLowerCase()}`
                }else{
                    shirt_feature += `,${selectedOptions['shirt'][key]} ${key.toLowerCase()}`
                }
            }
            // 合併成一個完整的日期時間字符串
            const start_datetime_str = `${selectedOptions['time']['start_date']} ${selectedOptions['time']['start_time']}`;
            const end_datetime_str = `${selectedOptions['time']['end_date']} ${selectedOptions['time']['end_time']}`;
            // console.log(start_datetime_str)
            
            selectPersonInformation(shirt_feature,selectedOptions['camera'],start_datetime_str,end_datetime_str);  // Add this function call
    
            setTimeout(() => {
                ripples.remove();
            }, 1000);
        });
    });

    screenDivFunc();
    document.getElementById('screen').innerHTML = `<div id="showSearchInformationScene"></div>`;
}
function selectPersonInformation(featureData,camera,start_datetime,end_datetime){
    // console.log(selectedOptions)
    let personInformation = []
    let picture = []
    let scene = ""
    // const featureData = 'gray shoe,yellow bag';  // 要傳送的 feature 字串
    const data = {
        "feature" : featureData,
        "camera" : camera,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
    }
    console.log(data)
    // const data = {
    //     "feature" : featureData,
    // }
    // 取得查詢資訊
    axios.post('http://127.0.0.1:5000/selectPersonInformation/info', data, {
        headers: { 'Content-Type': 'application/json' } // 設置內容類型為 JSON
    })
    .then(response => {
        personInformation = response.data.result;
        console.log(personInformation)
        const imagePromises = personInformation.map(data => {
            console.log(data)
            return axios.get(`http://127.0.0.1:5000/get_image_url/${data[0]}`)
                .then(response_picture_url => {
                    const url = response_picture_url.data;  // 取得圖片 URL
                    return `<div id="SearchInformationScene" class="search-scene">
                                <div id="picture"><img src="${url}" alt="${url}"></div>
                                <div id="information" class="info-box">
                                    <p>Camera: Camera${data[1]+1}</p>
                                    <p>Start Time: ${data[4]}</p>
                                    <p>End Time: ${data[5]}</p>
                                </div>
                            </div>`;
                });
        });
        console.log()
        // 等待所有異步操作完成
        return Promise.all(imagePromises);
    })
    .then(scenes => {
        // 將所有構建好的 HTML 拼接
        scene = scenes.join('');
        // 更新 DOM
        document.getElementById("showSearchInformationScene").innerHTML = scene;

        // 添加點擊事件
        document.querySelectorAll('.search-scene').forEach(element => {
            element.addEventListener('click', function() {
                const infoBox = this.querySelector('.info-box');
                infoBox.classList.toggle('visible');
            });
        });
    })
    .catch(error => {
        console.error('Error with POST request:', error);
    });
  }


