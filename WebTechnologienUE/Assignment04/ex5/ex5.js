// gleiche funktionalitaet wie ex4, nur mit es2015 klassen

// ---- a) bleibt ein normales objekt, dafuer braucht man keine klasse ----
let picture = {
    width: 1920,
    height: 1080,
    bitdepth: 24,
    computeSize() {
        this.pixels = this.width * this.height;
        this.rawsize = this.pixels * this.bitdepth / 8;
    }
};
picture.computeSize();
console.log("a) pixels:", picture.pixels, "rawsize:", picture.rawsize, "bytes");

// ---- b) + c) klasse Image ----
class Image {
    constructor(width, height, bitdepth) {
        this.width = width;
        this.height = height;
        this.bitdepth = bitdepth;
        this.pixels = width * height;
        this.rawsize = this.pixels * bitdepth / 8;
    }

    // methoden in der klasse landen automatisch im prototype
    print() {
        for (let key in this) {
            if (typeof this[key] !== "function") {
                console.log("  " + key + ": " + this[key]);
            }
        }
    }

    printMore() {
        this.print();
        if (this.width > this.height) {
            console.log("  -> landscape");
        } else if (this.width < this.height) {
            console.log("  -> portrait");
        } else {
            console.log("  -> square");
        }
    }
}

let img1 = new Image(1920, 1080, 24);
let img2 = new Image(1080, 1350, 8);
let img3 = new Image(800, 800, 32);
console.log("b) print:");
img1.print();
console.log("c) printMore:");
img2.printMore();
img3.printMore();

// ---- d) auch hier kann man zur laufzeit neu zuweisen ----
console.log("d) neue print funktion nur fuer img3:");
img3.print = function () {
    console.log("  kurz: " + this.width + "x" + this.height + ", " + this.rawsize + " bytes");
};
img3.printMore();
img1.print();

// ---- e) + f) Video erbt mit extends ----
class Video extends Image {
    constructor(width, height, bitdepth, duration, framerate) {
        // ruft den konstruktor von Image auf
        super(width, height, bitdepth);
        this.duration = duration;
        this.framerate = framerate;
    }

    totalFrames() {
        return this.duration * this.framerate;
    }
}

let video1 = new Video(1920, 1080, 24, 60, 30);
let video2 = new Video(1080, 1920, 24, 15, 60);
console.log("e) print und totalFrames:");
video1.print();
console.log("  totalFrames:", video1.totalFrames());
console.log("f) printMore auf Video:");
video2.printMore();
console.log("  totalFrames:", video2.totalFrames());
