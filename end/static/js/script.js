import showCameraScene from "./scene/camera.js";
import showSearchScene from "./scene/search.js";
import showReplayScene from "./scene/replay.js";
import showSetFileScene from "./scene/setFile.js";
import showDrawScene from "./scene/draw.js";

export function setActiveButton(buttonId, block) {
    // 移除所有按鈕的 active 類
    document.querySelectorAll(block).forEach(button => {
        button.classList.remove('active');
    });
    // 添加活動按鈕的 active 類
    document.getElementById(buttonId).classList.add('active');
}

// 顯示螢幕區塊
export default async function screenDivFunc() {
    if (document.getElementById("screen")) {
        document.getElementById('screen').remove();  // 這將删除元素
        console.log("ScreenDiv was removed");
    }
    // await axios.post('http://127.0.0.1:5000/close_all_cameras')
    //     .then(response => {
    //         console.log("關閉opencv畫面")
    //     })
    let body = document.getElementById("body");
    if (body) {
        let screenDiv = document.createElement("div");
        screenDiv.id = "screen";
        body.appendChild(screenDiv);
    } else {
        console.error("Element with id 'body' not found.");
    }
}

document.getElementById('cameraBut').onclick = async function() {
    let aElement = document.getElementById('cameraBut');
    if(!aElement.classList.contains('active')) {
        // await axios.post('http://127.0.0.1:5000/start_cameras');
        showCameraScene();
    } else {
        console.log('already choose');
    }
    setActiveButton('cameraBut', '.funcBut');
}
document.getElementById('searchBut').onclick = function() {
    let aElement = document.getElementById('searchBut');
    if(!aElement.classList.contains('active')) {
        showSearchScene();
    } else {
        console.log('already choose');
    }
    setActiveButton('searchBut', '.funcBut');
}
document.getElementById('replayBut').onclick = function() {
    let aElement = document.getElementById('replayBut');
    if(!aElement.classList.contains('active')) {
        showReplayScene();
    } else {
        console.log('already choose');
    }
    setActiveButton('replayBut', '.funcBut');
}
document.getElementById('setFileBut').onclick = function() {
    let aElement = document.getElementById('setFileBut');
    if(!aElement.classList.contains('active')) {
        showSetFileScene();
    } else {
        console.log('already choose');
    }
    setActiveButton('setFileBut', '.funcBut');
}
document.getElementById('drawBut').onclick = function() {
    let aElement = document.getElementById('drawBut');
    if(!aElement.classList.contains('active')) {
        showDrawScene();
    } else {
        console.log('already choose');
    }
    setActiveButton('drawBut', '.funcBut');
}

