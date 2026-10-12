// higher order function: nimmt eine funktion als parameter
function applyTwice(fn, value) {
    return fn(fn(value));
}

function double(x) {
    return x * 2;
}

console.log(applyTwice(double, 5)); // 20

// und eine die eine funktion zurueckgibt
function makeGreeting(greeting) {
    return name => greeting + ", " + name + "!";
}

let hallo = makeGreeting("Hallo");
console.log(hallo("Raphael")); // Hallo, Raphael!

// higher order functions die in js schon eingebaut sind
let prices = [2890, 1300, 900, 800];
console.log(prices.map(p => p * 1.2));            // map
console.log(prices.filter(p => p > 1000));        // filter
console.log(prices.reduce((sum, p) => sum + p, 0)); // reduce
setTimeout(() => console.log("setTimeout bekommt auch eine funktion"), 100);
