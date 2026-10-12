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
