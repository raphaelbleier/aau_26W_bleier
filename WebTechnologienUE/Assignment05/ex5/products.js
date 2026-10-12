

let container = document.getElementById('productContainer');
let productURL = "products.json";

initialize(productURL,container);

function initialize(jsonURL, domElement) {
	fetch(jsonURL)
		.then(response => {
			// fetch wirft bei 404 keinen fehler, das muss man selbst pruefen
			if (!response.ok) {
				throw new Error("Could not load products (status " + response.status + ")");
			}
			return response.json();
		})
		.then(products => {
			for (let product of products) {
				renderProduct(product, domElement);
			}
		})
		.catch(error => showError(domElement, error.message));
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
