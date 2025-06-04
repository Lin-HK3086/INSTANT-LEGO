<!DOCTYPE html>
<html>
<head>
<title>拖放显示3D模型 (OBJ/MTL)</title>
<style>
body {
    margin: 0;
overflow: hidden;
background-color: #f0f0f0;
display: flex;
flex-direction: column;
align-items: center;
height: 100vh;
}

#objDropArea, #mtlDropArea {
border: 2px dashed #ddd;
padding: 20px;
border-radius: 8px;
text-align: center;
cursor: pointer;
background-color: white;
margin-bottom: 20px;
max-width: 80%;
box-sizing: border-box;
}

#objDropArea.dragover, #mtlDropArea.dragover {
background-color: #f0f0f0;
border-color: #aaa;
}

#canvasContainer {
width: 100%;
height: 100%;
position: relative;
}

canvas {
    display: block;
width: 100%;
height: 100%;
}

#loading {
position: absolute;
top: 10px;
left: 50%;
transform: translateX(-50%);
background-color: rgba(255, 255, 255, 0.7);
padding: 10px;
border-radius: 5px;
z-index: 10;
font-size: 16px;
}

#error {
position: absolute;
top: 10px;
left: 50%;
transform: translateX(-50%);
background-color: rgba(255, 0, 0, 0.7);
color: white;
padding: 10px;
border-radius: 5px;
z-index: 10;
font-size: 16px;
}
</style>
  </head>
    <body>
    <div id="objDropArea">
            <p>将 .obj 文件拖放到此处</p>
                                       </div>
                                         <div id="mtlDropArea">
                                                 <p>将 .mtl 文件拖放到此处</p>
                                                                            </div>
                                                                              <div id="canvasContainer">
                                                                                      <canvas id="threeCanvas"></canvas>
                                                                                                                 <div id="loading">Loading...</div>
                                                                                                                                               <div id="error" style="display:none;"></div>
                                                                                                                                                                                       </div>

                                                                                                                                                                                         <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                                                                                                                                                                                                                                                                           <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
                                                                                                                                                                                                                                                                                                                                                                       <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js"></script>

                                                                                                                                                                                                                                                                                                                                                                                                                                                                   <script>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                   let scene, camera, renderer, model;
let objLoader, mtlLoader;
let animationFrameId;
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };
let loadingIndicator, errorDisplay;
let objFile, mtlFile;

function init() {
    loadingIndicator = document.getElementById('loading');
errorDisplay = document.getElementById('error');

// 场景
scene = new THREE.Scene();
scene.background = new THREE.Color('white');

// 相机
camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
camera.position.z = 5;

// 渲染器
const canvas = document.getElementById('threeCanvas');
renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// 光照
const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(1, 1, 2);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 1024;
directionalLight.shadow.mapSize.height = 1024;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 10;
scene.add(directionalLight);

objLoader = new THREE.OBJLoader();
mtlLoader = new THREE.MTLLoader();

// 设置拖放监听器
const objDropArea = document.getElementById('objDropArea');
const mtlDropArea = document.getElementById('mtlDropArea');

objDropArea.addEventListener('dragover', handleDragOver);
objDropArea.addEventListener('dragleave', handleDragLeave);
objDropArea.addEventListener('drop', handleObjDrop);

mtlDropArea.addEventListener('dragover', handleDragOver);
mtlDropArea.addEventListener('dragleave', handleDragLeave);
mtlDropArea.addEventListener('drop', handleMtlDrop);

// 添加鼠标事件
canvas.addEventListener('mousedown', handleMouseDown);
canvas.addEventListener('mouseup', handleMouseUp);
canvas.addEventListener('mousemove', handleMouseMove);
canvas.addEventListener('wheel', handleMouseWheel);
window.addEventListener('resize', handleResize);

animate();
}

function handleDragOver(event) {
    event.preventDefault();
event.stopPropagation();
this.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
event.stopPropagation();
this.classList.remove('dragover');
}

function handleObjDrop(event) {
    event.preventDefault();
event.stopPropagation();
this.classList.remove('dragover');

const file = event.dataTransfer.files[0];
if (file && file.name.endsWith('.obj')) {
    objFile = file;
if (mtlFile) {
    loadModel();
}
} else {
    displayError('请拖入有效的 .obj 文件');
objFile = null;
}
}

function handleMtlDrop(event) {
    event.preventDefault();
event.stopPropagation();
this.classList.remove('dragover');

const file = event.dataTransfer.files[0];
if (file && file.name.endsWith('.mtl')) {
    mtlFile = file;
if (objFile) {
    loadModel();
}
} else {
    displayError('请拖入有效的 .mtl 文件');
mtlFile = null;
}
}

function loadModel() {
if (!objFile) {
    displayError('请先拖入 .obj 文件');
return;
}
loadingIndicator.style.display = 'block';
errorDisplay.style.display = 'none';
scene.remove(model);

const objReader = new FileReader();
objReader.onload = function (event) {
let objContent = event.target.result;

if (mtlFile) {
const mtlReader = new FileReader();
mtlReader.onload = function (event) {
const mtlContent = event.target.result;
loadModelWithMaterials(objContent, mtlContent);
};
mtlReader.onerror = function (error) {
console.error('MTL 文件读取错误:', error);
displayError('MTL 文件读取错误，请检查文件。');
loadingIndicator.style.display = 'none';
};
mtlReader.readAsText(mtlFile);
} else {
loadModelWithMaterials(objContent, null);
}
};

objReader.onerror = function (error) {
console.error('OBJ 文件读取错误:', error);
displayError('OBJ 文件读取错误，请检查文件。');
loadingIndicator.style.display = 'none';
};
objReader.readAsText(objFile);
}

function loadModelWithMaterials(objContent, mtlContent) {
if (mtlContent) {
mtlLoader.setMaterialOptions({ side: THREE.DoubleSide });
const materials = mtlLoader.parse(mtlContent);
// 尝试加速：直接将解析后的材质传递给OBJLoader
objLoader.setMaterials(materials);
}
try{
model = objLoader.parse(objContent);
model.traverse(child => {
if (child.isMesh) {
child.castShadow = true;
child.receiveShadow = true;
}
});
scene.add(model);
// Center the model
const boundingBox = new THREE.Box3().setFromObject(model);
const center = boundingBox.getCenter(new THREE.Vector3());
model.position.x -= center.x;
model.position.y -= center.y;
model.position.z -= center.z;

loadingIndicator.style.display = 'none';
}
catch(err){
    console.error("model parse error", err);
displayError('模型解析错误，请检查文件是否有效。');
loadingIndicator.style.display = 'none';
}
}

function displayError(message) {
errorDisplay.textContent = message;
errorDisplay.style.display = 'block';
}

function animate() {
animationFrameId = requestAnimationFrame(animate);
if (model) {
model.rotation.y += 0.02;
}
renderer.render(scene, camera);
}

function handleMouseDown(event) {
isDragging = true;
previousMousePosition = {
    x: event.clientX,
    y: event.clientY
};
}

function handleMouseUp() {
isDragging = false;
}

function handleMouseMove(event) {
if (isDragging && model) {
const deltaMove = {
x: event.clientX - previousMousePosition.x,
y: event.clientY - previousMousePosition.y
};

model.rotation.y += deltaMove.x * 0.01;

previousMousePosition = {
    x: event.clientX,
    y: event.clientY
};
}
}

function handleMouseWheel(event) {
event.preventDefault();
const zoomSpeed = 0.05;
camera.position.z += event.deltaY * zoomSpeed;
camera.position.z = Math.max(1, Math.min(camera.position.z, 10));
}

function handleResize() {
camera.aspect = window.innerWidth / window.innerHeight;
camera.updateProjectionMatrix();
renderer.setSize(window.innerWidth, window.innerHeight);
}

// 开始
init();
</script>
  </body>
    </html>
