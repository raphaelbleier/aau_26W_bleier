'use strict';

let products = [];

const productList = {
	products: products,
	listProducts: function () {
		this.products.forEach((product, index) => {
			if (product.numInCart > 0) {
				const nextProductIndex = (index + 1) % this.products.length;
				const nextProduct = this.products[nextProductIndex];
				console.log(`${nextProduct.title};`);
			}
		});
	}
};

function updateCart() {
	let output = document.getElementById("orderedItems");
	output.innerHTML = "";
	let total = 0;
	for (let p of products) {
		// minus button nur aktiv wenn was im warenkorb ist
		p.minusButton.disabled = p.numInCart <= 0;
		if (p.numInCart > 0) {
			let newP = document.createElement("li");
			// b.b: gesamtpreis pro artikel mit anzeigen
			newP.appendChild(document.createTextNode(p.render() + " = " + p.getTotalPrice().toFixed(2)));
			output.appendChild(newP);
			total += p.getTotalPrice();
		}
	}
	document.getElementById("totalPrice").innerHTML = total.toFixed(2);
	console.log("Log: Updated cart: ");
	productList.listProducts();
}

// im konstruktor nur noch die daten und die buttons, methoden kommen ueber den prototype
function Product(el) {
	this.id = el.dataset.prodid;
	this.title = el.firstChild.nextSibling.firstChild.nodeValue;
	this.desc = el.getElementsByClassName('desc')[0].innerText;
	this.price = parseFloat(el.getElementsByClassName('price')[0].innerText);
	this.numInCart = 0;

	let clickButton = el.getElementsByClassName('buy')[0];
	clickButton.addEventListener('click', () => this.updateProduct());

	// b.a: zusaetzlicher button zum verringern
	this.minusButton = document.createElement("input");
	this.minusButton.type = "button";
	this.minusButton.value = "remove one";
	this.minusButton.disabled = true;
	this.minusButton.addEventListener('click', () => this.removeOneFromCart());
	// eigenes div neben dem buy div, sonst bubbelt der klick zum buy listener hoch
	let minusDiv = document.createElement("div");
	minusDiv.appendChild(this.minusButton);
	clickButton.after(minusDiv);
}

Product.prototype.updateProduct = function () {
	this.numInCart += 1;
	updateCart();
};

Product.prototype.removeOneFromCart = function () {
	if (this.numInCart > 0) {
		this.numInCart -= 1;
	}
	updateCart();
};

Product.prototype.render = function () {
	return this.title + " " + this.price + "(" + this.numInCart + ")";
};

// b.b: gesamtpreis fuer diesen artikel
Product.prototype.getTotalPrice = function () {
	return this.price * this.numInCart;
};

for (let pdiv of document.querySelectorAll("div.product")) {
	products.push(new Product(pdiv));
}

// b.c: nur das erste produkt bekommt eine eigene render methode,
// die ueberdeckt die vom prototype nur fuer dieses objekt
products[0].render = function () {
	return Product.prototype.render.call(this) + " New Arrival!";
};
