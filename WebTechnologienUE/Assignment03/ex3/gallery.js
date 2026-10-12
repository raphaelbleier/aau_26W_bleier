function showImg(e) {
   document.querySelector("#displayDIV .bigIMG").src=e.target.dataset.large;
   document.querySelector("#displayDIV .desc").innerHTML=e.target.alt;
   document.getElementById("displayDIV").style.display="block";
}

function hideImg(e) {
   e.currentTarget.style.display="none";
}

let images = document.querySelectorAll('.gallery img');
for (let i=0; i< images.length; i++) {
   images[i].addEventListener("click", showImg);
}
document.getElementById("displayDIV").addEventListener("click", hideImg);

// ---- ab hier eigener code: previous / next ----

// aktuell angezeigtes bild suchen, ueber data-large vergleichen
function currentIndex() {
   let bigSrc = document.querySelector("#displayDIV .bigIMG").getAttribute("src");
   for (let i = 0; i < images.length; i++) {
      if (images[i].dataset.large === bigSrc) {
         return i;
      }
   }
   return 0;
}

function showIndex(i) {
   document.querySelector("#displayDIV .bigIMG").src = images[i].dataset.large;
   document.querySelector("#displayDIV .desc").innerHTML = images[i].alt;
}

function showPrevious(e) {
   // sonst bubbelt der klick zum displayDIV und das bild wird geschlossen
   e.stopPropagation();
   let i = currentIndex() - 1;
   if (i < 0) {
      i = images.length - 1;
   }
   showIndex(i);
}

function showNext(e) {
   e.stopPropagation();
   let i = currentIndex() + 1;
   if (i >= images.length) {
      i = 0;
   }
   showIndex(i);
}

let prevButton = document.createElement("button");
prevButton.textContent = "previous";
prevButton.addEventListener("click", showPrevious);

let nextButton = document.createElement("button");
nextButton.textContent = "next";
nextButton.addEventListener("click", showNext);

document.getElementById("displayDIV").append(prevButton, nextButton);

// ---- assignment 3: slideshow mit play/pause und exit ----

let slideshowTimer = null;

let playButton = document.createElement("button");
playButton.textContent = "play";

let secondsInput = document.createElement("input");
secondsInput.type = "number";
secondsInput.min = 1;
secondsInput.value = 3;
secondsInput.style.width = "50px";

let secondsLabel = document.createElement("span");
secondsLabel.textContent = " seconds ";

let exitButton = document.createElement("button");
exitButton.textContent = "exit";

function startSlideshow() {
   let seconds = Number(secondsInput.value);
   if (!(seconds > 0)) {
      seconds = 3;
   }
   // showNext erwartet ein event wegen stopPropagation, deshalb ein leeres objekt
   slideshowTimer = setInterval(() => showNext({ stopPropagation() {} }), seconds * 1000);
   playButton.textContent = "pause";
}

function stopSlideshow() {
   clearInterval(slideshowTimer);
   slideshowTimer = null;
   playButton.textContent = "play";
}

function togglePlay(e) {
   e.stopPropagation();
   if (slideshowTimer === null) {
      startSlideshow();
   } else {
      stopSlideshow();
   }
}

function exitGallery(e) {
   e.stopPropagation();
   stopSlideshow();
   document.getElementById("displayDIV").style.display = "none";
}

// wenn die sekunden waehrend der slideshow geaendert werden, neu starten
function secondsChanged() {
   if (slideshowTimer !== null) {
      stopSlideshow();
      startSlideshow();
   }
}

playButton.addEventListener("click", togglePlay);
exitButton.addEventListener("click", exitGallery);
secondsInput.addEventListener("change", secondsChanged);
// klick ins eingabefeld soll das bild nicht schliessen
secondsInput.addEventListener("click", e => e.stopPropagation());
// beim schliessen durch klick aufs bild auch die slideshow stoppen
document.getElementById("displayDIV").addEventListener("click", stopSlideshow);

document.getElementById("displayDIV").append(playButton, secondsInput, secondsLabel, exitButton);
