

let container = document.getElementById('productContainer');
// relativ, dann passt es egal wo der ordner im document root liegt
let productURL = "products.json";

initialize(productURL,container);

function initialize(jsonURL, domElement) {
	let xhr = new XMLHttpRequest();
	xhr.open("GET", jsonURL);

	xhr.onload = function () {
		if (xhr.status !== 200) {
			showError(domElement, "Could not load products (status " + xhr.status + ")");
			return;
		}
		try {
			let products = JSON.parse(xhr.responseText);
			for (let product of products) {
				renderProduct(product, domElement);
			}
		} catch (e) {
			showError(domElement, "Invalid product data: " + e.message);
		}
	};

	// netzwerkfehler, z.b. server nicht erreichbar
	xhr.onerror = function () {
		showError(domElement, "Network error while loading products");
	};

	xhr.send();
}

// ein produkt so wie auf dem letzten blatt als div.product rendern
function renderProduct(product, domElement) {
	let div = document.createElement("div");
	div.className = "product";
	div.dataset.prodid = product.id;

	let title = document.createElement("h2");
	title.textContent = product.title;

	let row = document.createElement("div");
	let desc = document.createElement("div");
	desc.className = "desc";
	desc.textContent = product.desc;
	let price = document.createElement("div");
	price.className = "price";
	price.textContent = product.price.toFixed(2).replace(".", ",");
	let buy = document.createElement("div");
	buy.className = "buy";
	let button = document.createElement("input");
	button.type = "button";
	button.value = "add to cart";
	buy.appendChild(button);

	row.append(desc, price, buy);
	div.append(title, row);
	domElement.appendChild(div);
}

function showError(domElement, text) {
	let p = document.createElement("p");
	p.style.color = "red";
	p.textContent = text;
	domElement.appendChild(p);
}
