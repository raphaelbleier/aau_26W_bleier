// absatz mit der doppelten ueberschrift loeschen
let heading = document.querySelector("h1");
for (let p of document.querySelectorAll("p")) {
    if (p.textContent.trim() === heading.textContent.trim()) {
        p.remove();
    }
}

// preisfeld nach der legend "Price" einfuegen
let priceInput = document.createElement("input");
priceInput.type = "text";
priceInput.id = "price";
priceInput.name = "price";
priceInput.readOnly = true;
priceInput.value = "-";

let priceLabel = document.createElement("label");
priceLabel.htmlFor = "price";
priceLabel.textContent = "price";

for (let legend of document.querySelectorAll("legend")) {
    if (legend.textContent === "Price") {
        legend.after(priceInput, priceLabel);
    }
}

function calculate(width, height, thickness) {
    // dicke ist in mm, alles andere in cm
    let thicknessCm = thickness / 10;

    // grau wenn r, g und b gleich sind, z.b. #808080
    let color = document.getElementById("color").value;
    let r = color.substring(1, 3);
    let g = color.substring(3, 5);
    let b = color.substring(5, 7);

    if (r === g && g === b) {
        return width * height * thicknessCm / 50;
    }
    return width * height * thicknessCm / 32;
}

function update() {
    let width = document.getElementById("width");
    let height = document.getElementById("height");
    // bei radio buttons reicht checkValidity auf einem, gilt fuer die ganze gruppe
    let thicknessRadio = document.getElementById("4mm");
    let checked = document.querySelector("input[name=thickness]:checked");

    if (width.value !== "" && height.value !== "" && checked
        && width.checkValidity() && height.checkValidity() && thicknessRadio.checkValidity()) {
        let price = calculate(Number(width.value), Number(height.value), Number(checked.value));
        priceInput.value = price.toFixed(2);
    } else {
        priceInput.value = "-";
    }
}

document.getElementById("width").addEventListener("input", update);
document.getElementById("height").addEventListener("input", update);
document.getElementById("color").addEventListener("input", update);
for (let radio of document.querySelectorAll("input[name=thickness]")) {
    radio.addEventListener("change", update);
}
