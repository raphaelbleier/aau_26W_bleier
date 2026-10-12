// code aus der angabe, zum ausprobieren
function myFunct(a, b, x) {
    let calc = function (i) {
        console.log(i + b);
        return i + b;
    }
    if (a < 20) return calc(a);
    else {
        console.log(a);
        return calc;
    }
}
let x = myFunct(12, 8);
let y = myFunct(21, 7);
y(14);
y(9, 33);
