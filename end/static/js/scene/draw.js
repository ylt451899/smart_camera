export default async function showDrawScene() {
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
    } catch (error) {
        console.error(error);
        return; // Exit the function if there's an error
    }

    let screen = `
        <div class="dropdownFont drawFont">Camera: </div>
        <div class="dropdown drawDropdown">
            <input type="text" class="text02" readonly placeholder="Select Camera">
            <div class="option">`

    for (let i = 0; i < model_config.length; i++) {
        screen += `
            <div>Camera${i+1}</div>
        `;
    }
    screen += `
            </div>
        </div>
        <a href="#" class="saveBut drawSaveBut">Save</a>
        <a href="#" class="saveBut deleteBut">Delete</a>
        <div class="safe_danger_area">
            <div id="safe_area">
                <label>
                    <input type="radio" id="safe" name="area" value="safearea" checked />
                    <span>safe</span>
                </label>
                
            </div>
            <div id="danger_area">
                <label>
                    <input type="radio" id="danger" name="area" value="dangerarea" />
                    <span>danger</span>
                </label>
            </div>
        </div>
        <div class="showdrawcanva">
            <img id="cameraStream" src="" width="100%" height="100%" />
            <canvas id="drawingCanvas" ></canvas>
        </div>
    `;
    let funcScreen = document.getElementById('funcScreen');
    let cameraSelect = ""//監視器選擇
    if (funcScreen) {
        funcScreen.innerHTML = screen;
    } else {
        console.error('目標元素不存在');
    }

    // option anime
    function show(a) {
        document.querySelector('.text02').value = a;
    }
    let options = document.querySelectorAll('.option div');
    options.forEach(option => {
        option.addEventListener('mouseover', function() {
            show(option.innerText);
            cameraSelect = parseInt(option.innerText.split("Camera")[1])-1
            console.log(cameraSelect)
        });
    });
    let dropdown = document.querySelector('.dropdown');
    dropdown.onclick = function() {
        dropdown.classList.toggle('active');
    };
    // 當選擇相機時，更新顯示區域的圖像流
    const cameraStream = document.getElementById('cameraStream');
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    // const img_folder = ""
    document.querySelectorAll('.option div').forEach(option => {
        option.addEventListener('click', function() {
            // 根據選擇的相機更新圖像流
            cameraSelect = parseInt(option.innerText.split("Camera")[1]) - 1;
            cameraStream.src = `/images_model_feed/${cameraSelect}`;
            // img_folder = `/images_model_feed/${cameraSelect}`;
            // 確保圖片加載完成後，設置 canvas 的大小
            cameraStream.onload = function() {
                const imgWidth = cameraStream.naturalWidth;
                const imgHeight = cameraStream.naturalHeight;
                
                // 计算显示区域的宽高比例
                const aspectRatio = imgWidth / imgHeight;

                // 设置 canvas 的宽高，确保与图片大小同比例
                const containerWidth = cameraStream.offsetWidth;
                const containerHeight = containerWidth / aspectRatio;
                canvas.width = containerWidth;
                canvas.height = containerHeight;

                // 计算缩放比例
                scaleFactorX = imgWidth / canvas.width;
                scaleFactorY = imgHeight / canvas.height;
            };
        });
    });
    // saveBut anime
    const button = document.querySelector('.saveBut');
    button.addEventListener('click', async function(e) {
        let x = e.clientX - e.target.offsetLeft;
        let y = e.clientY - e.target.offsetTop;
        let ripples = document.createElement('span');
        ripples.style.left = x + 'px';
        ripples.style.top = y + 'px';
        this.appendChild(ripples);
        saveDrawArea(dots,cameraSelect);  // 在滑鼠放開時保存繪圖區域

        setTimeout(() => {
            ripples.remove()
        }, 1000);

    });
    const deleteButton = document.querySelector('.deleteBut');
    deleteButton.addEventListener('click', async function(e) {
        let x = e.clientX - e.target.offsetLeft;
        let y = e.clientY - e.target.offsetTop;
        let ripples = document.createElement('span');
        ripples.style.left = x + 'px';
        ripples.style.top = y + 'px';
        this.appendChild(ripples);
        deleteDrawArea(cameraSelect);  // 在滑鼠放開時保存繪圖區域
        setTimeout(() => {
            ripples.remove()
        }, 1000);

    });

    // 繪圖功能實現
    
    // 設置 canvas 的寬度和高度，使其與 CSS 中的尺寸保持一致
    // canvas.width = canvas.offsetWidth;
    // canvas.height = canvas.offsetHeight;
    
    let drawing = false;
    let dots = [];
    let scaleFactorX = 1;
    let scaleFactorY = 1;

    canvas.addEventListener('mousedown', (e) => {
        drawing = true;
        // 計算縮放比例（相對於原始圖片大小）
        scaleFactorX = cameraStream.naturalWidth / canvas.width;
        scaleFactorY = cameraStream.naturalHeight / canvas.height;
        dots = [[e.offsetX, e.offsetY]];  // 初始化點陣列
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!drawing) return;
        const currentX = e.offsetX;
        const currentY = e.offsetY;
        dots.push([currentX, currentY]);
        ctx.clearRect(0, 0, canvas.width, canvas.height);  // 清除畫布
        ctx.beginPath();
        ctx.moveTo(dots[0][0], dots[0][1]);
        dots.forEach(dot => ctx.lineTo(dot[0], dot[1]));  // 繪製點與點之間的連線
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'red';
        ctx.stroke();
    });

    canvas.addEventListener('mouseup', (e) => {
        drawing = false;
    });

    function saveDrawArea(dots,camera) {
        // console.log('Saving area:', dots);
        // 将 canvas 上的点位转换为原始图像的点位
        // const scaledDots = dots.map(([x, y]) => [x * scaleFactorX, y * scaleFactorY]);
        console.log(camera)
        // if(camera == "1"){
        //     dots = dots.map(([x, y]) => [x * scaleFactorX, y * scaleFactorY]);
        // }
        const areaSelectArea = document.querySelector('input[name="area"]:checked').value;
        // 發送繪製區域到後端
        fetch('/save_safe_area', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ camera_id: cameraSelect, dots: dots , area: areaSelectArea })
        }).then(response => {
            if (response.ok) {
                console.log(cameraSelect)
                console.log('Safe area saved.');
            } else {
                console.error('Failed to save area.');
            }
        });
        alert(`camera${camera+1} ${areaSelectArea}area 新增成功!`)
    }
    function deleteDrawArea(camera) {
        console.log('Delete area:', dots);
        const areaSelectArea = document.querySelector('input[name="area"]:checked').value;
        // 發送繪製區域到後端
        fetch('/delete_safe_area', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ camera_id: cameraSelect, area: areaSelectArea })
        }).then(response => {
            if (response.ok) {
                console.log(cameraSelect)
                console.log('Safe area deleted.');
            } else {
                console.error('Failed to delete area.');
            }
        });
        alert(`camera${camera+1} ${areaSelectArea}area 刪除成功!`)
    }

}