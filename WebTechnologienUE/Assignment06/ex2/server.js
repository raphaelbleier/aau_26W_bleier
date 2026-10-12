let express = require('express');
const app = express();
let fs = require('fs');
let cors = require('cors');
app.use(cors()); // allow all origins -> Access-Control-Allow-Origin: *
app.use(express.static('public')); // host public folder

// TODO: read the products.json file here into a string
// einmal beim start einlesen, __dirname damit es egal ist von wo man node startet
let productsString = fs.readFileSync(__dirname + '/products.json', 'utf8');
let products = JSON.parse(productsString);
console.log(products);

app.get('/', function (req, res) {

	// TODO: set a content type (from ex.1)
	res.setHeader('Content-Type', 'text/html');

    res.status(200).send("EX2: This is a simple application");
});
app.get('/products', function (req, res) {

	// write your code here to output the list of products as JSON
	let ids = products.map(p => p.id);
	res.status(200).json({ productIds: ids });
});

// write your route handler to output a single product by its ID as JSON here
app.get('/product/:id', function (req, res) {
	let product = products.find(p => p.id === req.params.id);
	if (!product) {
		return res.status(404).json({ message: "Product " + req.params.id + " not found" });
	}
	res.status(200).json(product);
});

let port = 3000;
app.listen(port);
console.log("Server running at: http://localhost:"+port);
