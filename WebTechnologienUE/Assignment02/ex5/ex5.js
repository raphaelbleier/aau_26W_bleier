document.querySelector('#button').addEventListener('click',function (event){
    console.log("inner:");
    console.log("target: "+event.target);
    console.log("currentTarget: "+event.currentTarget);
    console.log("this: "+this);
});

document.querySelector('#outerArea').addEventListener('click',function (event){
        console.log("outer:");
        console.log("target: " + event.target);
        console.log("currentTarget: " + event.currentTarget);
        console.log("this: " + this);
});
// 4. zweiter listener am button stoppt das bubbling,
// dadurch wird der listener vom outerArea nicht mehr ausgefuehrt wenn man den button klickt
document.querySelector('#button').addEventListener('click', function (event) {
    event.stopPropagation();
});
