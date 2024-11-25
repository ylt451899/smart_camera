import screenDivFunc from "../script.js";
const videoList = ['Video0','Video1','Video2','Video3']
export default async function showReplayScene() {
    let model_config = []
    // Use async/await to ensure the config is loaded before proceeding
    try {
        const response = await axios.get('http://127.0.0.1:5000/read_model_config');
        console.log(response.data.data.cameras);
        model_config = response.data.data.cameras;
    } catch (error) {
        console.error(error);
        return; // Exit the function if there's an error
    }

    let screen = `
        <div class="replay">
            <ul>
    `;
    for(let i = 0;i<model_config.length;i++) {
        screen += `
            <li><a href="javascript:void(0)">Video${i+1}</a></li>
        `;
    }
    screen += `
            </ul>
        </div>
    `;

    let funcScreen = document.getElementById('funcScreen');
    const activeCameras = [];
    if (funcScreen) {
        funcScreen.innerHTML = screen;
        // 按下video按鈕執行
        const videoLinks = funcScreen.querySelectorAll('.replay ul li a');
        videoLinks.forEach((link,index) => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();  // 确保事件不会冒泡
                console.log(index)
                this.classList.toggle('active');
                if(this.classList.contains('active')){
                    console.log(index)
                    activeCameras.push(index);
                } else {
                    const pop = activeCameras.indexOf(index);
                    activeCameras.splice(pop, 1);
                }
                // console.log(activeCameras)
                updateVideoScene(activeCameras,model_config);
            });
        });
    } else {
        console.error('目標元素不存在');
    }
    screenDivFunc();
    
}
function updateVideoScene(activeCameras,model_config) {
    console.log(activeCameras)
    let showVideoSceneHTML = '<div id="showVideoScene">';
    for(let i = 0;i<activeCameras.length;i++){
        console.log(model_config[activeCameras[i]].source)
        // if(i == 0){
        //     showVideoSceneHTML += `
        //     <div id="videoScene">
        //         <video controls width="100%" height="100%">
        //             <source src="/static/${activeCameras[i]}" type="video/mp4">
        //         </video>
        //     </div>
        // `;
        // }else{
            showVideoSceneHTML += `
                <div id="videoScene">
                    <video controls width="100%" height="100%">
                        <source src="/static/${model_config[activeCameras[i]].source}" type="video/mp4">
                    </video>
                </div>
            `;
        // }
    }
    showVideoSceneHTML += '</div>';
    document.getElementById('screen').innerHTML = showVideoSceneHTML;

    // Apply layout classes
    const showVideoScene = document.getElementById("showVideoScene");
    if (activeCameras.length === 1) {
        showVideoScene.classList.remove('double', 'many');
    } else if (activeCameras.length === 2) {
        showVideoScene.classList.remove('many');
        showVideoScene.classList.add('double');
    } else {
        showVideoScene.classList.remove('double');
        showVideoScene.classList.add('many');
    }
}