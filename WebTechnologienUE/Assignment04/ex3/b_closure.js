// closure: die innere funktion merkt sich die variable count,
// auch wenn makeCounter schon fertig ist
function makeCounter() {
    let count = 0;
    return function () {
        count++;
        return count;
    };
}

let counterA = makeCounter();
let counterB = makeCounter();

console.log(counterA()); // 1
console.log(counterA()); // 2
console.log(counterA()); // 3
console.log(counterB()); // 1, eigener count
// von aussen kommt man an count nicht ran
console.log(typeof count); // undefined
