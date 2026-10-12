// ---- a) objekt mit json syntax ----
let picture = {
    width: 1920,
    height: 1080,
    bitdepth: 24,
    computeSize: function () {
        this.pixels = this.width * this.height;
        // bits durch 8 = bytes
        this.rawsize = this.pixels * this.bitdepth / 8;
    }
};

picture.computeSize();
console.log("a) pixels:", picture.pixels, "rawsize:", picture.rawsize, "bytes");

// ---- b) konstruktor funktion ----
function Image(width, height, bitdepth) {
    this.width = width;
    this.height = height;
    this.bitdepth = bitdepth;
    this.pixels = width * height;
    this.rawsize = this.pixels * bitdepth / 8;

    // print haengt direkt am objekt, jedes objekt hat seine eigene kopie
    this.print = function () {
        for (let key in this) {
            // funktionen nicht mit ausgeben
            if (typeof this[key] !== "function") {
                console.log("  " + key + ": " + this[key]);
            }
        }
    };
}

let img1 = new Image(1920, 1080, 24);
let img2 = new Image(1080, 1350, 8);
let img3 = new Image(800, 800, 32);
console.log("b) print:");
img1.print();
img2.print();
img3.print();

// ---- c) printMore ueber den prototype ----
Image.prototype.printMore = function () {
    this.print();
    if (this.width > this.height) {
        console.log("  -> landscape");
    } else if (this.width < this.height) {
        console.log("  -> portrait");
    } else {
        console.log("  -> square");
    }
};

console.log("c) printMore:");
img1.printMore();
img2.printMore();
img3.printMore();

// ---- d) zuweisung zur laufzeit ----
// print ist eine normale property, man kann einfach eine andere funktion zuweisen
console.log("d) neue print funktion nur fuer img3:");
img3.print = function () {
    console.log("  kurz: " + this.width + "x" + this.height + ", " + this.rawsize + " bytes");
};
img3.print();
// printMore ruft this.print auf und nimmt jetzt automatisch die neue version
img3.printMore();
// img1 hat noch die alte
img1.print();
// achtung: img3.print = img3.printMore waere eine endlosschleife,
// weil printMore wieder this.print aufruft

// ---- e) Video erbt von Image ----
function Video(width, height, bitdepth, duration, framerate) {
    // konstruktor von Image aufrufen
    Image.call(this, width, height, bitdepth);
    this.duration = duration;
    this.framerate = framerate;
}

// prototype kette setzen, damit Video auch printMore bekommt
Video.prototype = Object.create(Image.prototype);
Video.prototype.constructor = Video;

Video.prototype.totalFrames = function () {
    return this.duration * this.framerate;
};

let video1 = new Video(1920, 1080, 24, 60, 30);
let video2 = new Video(1080, 1920, 24, 15, 60);
console.log("e) print und totalFrames:");
video1.print();
console.log("  totalFrames:", video1.totalFrames());
video2.print();
console.log("  totalFrames:", video2.totalFrames());

// ---- f) printMore auf Video ----
console.log("f) printMore auf Video:");
video2.printMore();
console.log("  video2 instanceof Image:", video2 instanceof Image);
