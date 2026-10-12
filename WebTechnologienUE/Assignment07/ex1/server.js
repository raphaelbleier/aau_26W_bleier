let cfg = require('./config.json')

let express = require('express');
let cors = require('cors')
const app = express();
app.use(express.static('public')); // host public folder
app.use(cors()); // allow all origins -> Access-Control-Allow-Origin: *

const pool = require('./pool.js');

let bodyParser = require('body-parser');
app.use(bodyParser.json()); // support json encoded bodies

const checkAuth = require('./check_auth');

const loginRoutes = require('./login');
app.use("/login", loginRoutes);

// get products for logged in user as a list of JSON entries
app.get("/", (req, res) => {
    
	// TODO: set content type (from EX6.1)
	res.setHeader('Content-Type', 'text/html');

    res.status(200).send("EX: This is a database-backed application which uses JWT");
});

// TODO: the rest of the route handlers are mostly the same as in EX3 with important differences
// gleich wie in 6.4, checkAuth prueft jetzt aber den token statt der session
app.get("/products", checkAuth, (req, res) => {

// TODO: write your code here to get the list of products from the DB pool
    pool.query("SELECT id FROM products ORDER BY id")
        .then(results => {
            let ids = results.rows.map(row => row.id);
            res.status(200).json({ productIds: ids });
        })
        .catch(error => {
            console.log(error);
            res.status(500).json({ message: "Database error" });
        });
});

// TODO: write your route handler here to get a single product from the DB pool
// $1 als platzhalter, damit keine sql injection moeglich ist
app.get("/product/:id", checkAuth, (req, res) => {
    pool.query("SELECT * FROM products WHERE id = $1", [req.params.id])
        .then(results => {
            if (results.rows.length === 0) {
                return res.status(404).json({ message: "Product " + req.params.id + " not found" });
            }
            res.status(200).json(results.rows[0]);
        })
        .catch(error => {
            console.log(error);
            res.status(500).json({ message: "Database error" });
        });
});

// TODO: write your code here to update the description of the given product
app.put("/product/:id", checkAuth, (req, res) => {
    let description = req.body.description;
    if (typeof description !== "string" || description.trim() === "") {
        return res.status(400).json({ message: "Missing description in request body" });
    }

    pool.query("UPDATE products SET description = $1 WHERE id = $2 RETURNING *", [description, req.params.id])
        .then(results => {
            if (results.rowCount === 0) {
                return res.status(404).json({ message: "Product " + req.params.id + " not found" });
            }
            res.status(200).json(results.rows[0]);
        })
        .catch(error => {
            console.log(error);
            res.status(500).json({ message: "Database error" });
        });
});

  
let port = 3000;
app.listen(port);
console.log("Server running at: http://localhost:"+port);
