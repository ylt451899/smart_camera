
import screenDivFunc from "../script.js";
const camera_list = ["camera1","camera2","camera3","camera4","camera5","camera6","camera7"]

export default async function showCameraScene() {
    let cameraStreamStarted = []; // 用于记录每个摄像头是否已经启动过视频流
    // Use async/await to ensure the config is loaded before proceeding
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
        <ul class="lightSQ">
        
    `;
    
    console.log(model_config)
    for(let i = 0;i<model_config.length;i++) {
        console.log(i)
        screen += `
            <li>
                <label>
                    Camera${i+1}
                    <input type="checkbox"  class="cameraCheckBox" id="camera${i+1}" name="camera${i+1}">
                    <span class="check"></span>
                </label>
            </li>
        `;
    }
    screen += `</ul>`;

    let funcScreen = document.getElementById('funcScreen');
    if (funcScreen) {
        funcScreen.innerHTML = screen;
    } else {
        console.error('目標元素不存在');
    }
    screenDivFunc();

    let cameraScene = `<div id="showCameraScene">`
    
    // WebSocket 初始化
    const socket = io('http://127.0.0.1:5000');
    // <button id="refresh">refresh</button>`;
    // camera畫面顯示
    for (let i = 0; i < model_config.length; i++) {
        cameraScene += `
            <div id="cameraScene${i}" class="cameraScene" style="display: none;">
                <img id="cameraImage${i}" width="100%" height="100%" />
            </div>
        `;
        // 動態接收每個攝影機的影像流
        socket.on(`camera_stream_camera${i+1}`, (data) => {
            const img = document.getElementById(`cameraImage${i}`);
            img.src = `data:image/jpeg;base64,${data.frame}`;
        });
    }
    // 舊版
    // for (let i = 0; i < model_config.length; i++) {
    //     cameraScene += `
    //         <div id="cameraScene${i}" class="cameraScene" style="display: none;">
    //             <img src="/video_model_feed/${i}" width="100%" height="100%" />
    //         </div>
    //     `;
    // }
    cameraScene += `</div>`;
    document.getElementById('screen').innerHTML = cameraScene;

    const checkboxes = document.querySelectorAll('.cameraCheckBox');
    checkboxes.forEach((checkbox, index) => {
        checkbox.onclick = function() {
            toggleCameraScene(index);
        }
    });
    // 刷新 按鈕
    // document.getElementById("refresh").addEventListener("click", function() {
    //     // Step 1: 關閉所有#cameraScene
    //     const cameraScenes = document.querySelectorAll(".cameraScene");
    //     cameraScenes.forEach(scene => {
    //         scene.style.display = "none";  // 隱藏所有攝影機畫面
    //     });
    
    //     // Step 2: 向後端發送請求以關閉攝影機
    //     axios.post('/close_all_cameras')
    //         .then(response => {
    //             console.log("All cameras closed:", response.data);
    //             // Step 3: 發送請求重新開啟攝影機
    //             return axios.post('/start_cameras');
    //         })
    //         .then(response => {
    //             console.log("Cameras restarted:", response.data);
    //             // Step 4: 重新顯示所有攝影機畫面
    //             cameraScenes.forEach(scene => {
    //                 scene.style.display = "block";  // 顯示攝影機畫面
    //             });
    //         })
    //         .catch(error => {
    //             console.error("Error in refreshing cameras:", error);
    //         });
    // });

    function toggleCameraScene(index) {
        const cameraSceneElement = document.getElementById(`cameraScene${index}`);
        if (checkboxes[index].checked) {
            cameraSceneElement.style.display = "block";
            if (!(index in cameraStreamStarted)) cameraStreamStarted.push(index);
        } else {
            cameraSceneElement.style.display = "none";
        }

        updateLayout();
    }

    function updateLayout() {
        const checkedCameras = Array.from(checkboxes).filter(checkbox => checkbox.checked).length;

        const showCameraScene = document.getElementById("showCameraScene");
        if (checkedCameras === 1) {
            showCameraScene.classList.remove('double', 'many');
        } else if (checkedCameras === 2) {
            showCameraScene.classList.remove('many');
            showCameraScene.classList.add('double');
        } else {
            showCameraScene.classList.remove('double');
            showCameraScene.classList.add('many');
        }
    }
    // let cameraScene = `<div id="showCameraScene">`
    // for(let i = 0;i<model_config.length;i++){
    //     cameraScene += `<div id="cameraScene">
    //             <img src="/video_model_feed/${i}" width="100%" height="100%" />
    //         </div>`
    // }
    // cameraScene += `</div>`
    // document.getElementById('screen').innerHTML = cameraScene;

    // // 查询所有已勾选的复选框
    // const checkboxes = document.querySelectorAll('.cameraCheckBox');
    // for(let i = 0;i<model_config.length;i++){
    //     document.getElementById(`camera${i+1}`).onclick = function(){
    //         setShowCameraScene()
    //     }
    // }

    // function setShowCameraScene() {
    //     const checkedCameras = [];
    //     checkboxes.forEach((checkbox, index) => {
    //         console.log("incheckbox")
    //         if(!(index in cameraStreamStarted)) cameraStreamStarted.push(index) 
    //         if (checkbox.checked) {
    //             checkedCameras.push(index);
    //             console.log('check');
    //         }
    //     });


    //     console.log('已勾选的复选框:', checkedCameras);
        

    //     // 添加活動按鈕的 active 類
    //     if(checkedCameras.length == 1){
    //         document.getElementById("showCameraScene").classList.remove('double');
    //     }else if(checkedCameras.length == 2){
    //         document.getElementById("showCameraScene").classList.remove('many');
    //         document.getElementById("showCameraScene").classList.add('double');
    //     }
    //     else{
    //         document.getElementById("showCameraScene").classList.remove('double');
    //         document.getElementById("showCameraScene").classList.add('many');
    //     }

    // }
}