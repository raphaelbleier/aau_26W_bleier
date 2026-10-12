// normale funktion mit 3 parametern
function price(net, taxRate, discount) {
    return net * (1 + taxRate) * (1 - discount);
}

// curried: jede funktion nimmt nur einen parameter
function curriedPrice(net) {
    return function (taxRate) {
        return function (discount) {
            return net * (1 + taxRate) * (1 - discount);
        };
    };
}

console.log(price(100, 0.2, 0.1));          // 108
console.log(curriedPrice(100)(0.2)(0.1));   // 108

// vorteil: man kann teile vorbelegen
const withAustrianTax = net => curriedPrice(net)(0.2);
let lens = withAustrianTax(1300);
console.log(lens(0));    // 1560
console.log(lens(0.1));  // 1404

// kurz mit arrow functions
const add = a => b => c => a + b + c;
console.log(add(1)(2)(3)); // 6
