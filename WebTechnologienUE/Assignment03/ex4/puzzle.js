// das bild das gerade an der maus haengt
let movingImg = null;
let source = document.getElementById("puzzleSource");
let cells = document.querySelectorAll("#puzzleTarget .puzzlePic");

// meldung unter dem puzzle
let message = document.createElement("p");
document.getElementById("puzzleTarget").after(message);

function pickUp(img, e) {
    movingImg = img;
    img.style.position = "fixed";
    // bild etwas versetzt zur maus, damit man sieht wo man hinklickt
    moveImg(e);
}

function moveImg(e) {
    if (movingImg) {
        movingImg.style.left = (e.clientX + 15) + "px";
        movingImg.style.top = (e.clientY + 15) + "px";
    }
}

function backToList(img) {
    img.style.position = "";
    img.style.left = "";
    img.style.top = "";
    source.appendChild(img);
}

function drop(cell) {
    // war schon ein bild im feld? dann zurueck in die liste
    if (cell.dataset.current) {
        let oldImg = document.createElement("img");
        oldImg.src = cell.dataset.current;
        oldImg.alt = cell.dataset.alt;
        source.appendChild(oldImg);
    }

    let file = movingImg.getAttribute("src");
    cell.style.backgroundImage = "url(" + file + ")";
    cell.style.backgroundSize = "cover";
    cell.dataset.current = file;
    cell.dataset.alt = movingImg.alt;
    movingImg.remove();

    checkPuzzle(cell);
}

function checkPuzzle(cell) {
    let allCorrect = true;
    for (let c of cells) {
        if (c.dataset.current !== c.dataset.result) {
            allCorrect = false;
        }
    }

    if (allCorrect) {
        message.textContent = "You won! The puzzle is solved.";
        message.style.color = "green";
    } else if (cell.dataset.current !== cell.dataset.result) {
        message.textContent = "Wrong placement, try another field.";
        message.style.color = "red";
    } else {
        message.textContent = "Correct, keep going!";
        message.style.color = "black";
    }
}

function handleClick(e) {
    if (movingImg === null) {
        // nur bilder aus der liste aufnehmen
        if (e.target.tagName === "IMG" && e.target.parentNode === source) {
            pickUp(e.target, e);
        }
        return;
    }

    // relevant ist das element unter der maus
    let target = document.elementFromPoint(e.clientX, e.clientY);
    if (target && target.classList.contains("puzzlePic")) {
        drop(target);
    } else {
        backToList(movingImg);
    }
    movingImg = null;
}

document.addEventListener("click", handleClick);
document.addEventListener("mousemove", moveImg);
