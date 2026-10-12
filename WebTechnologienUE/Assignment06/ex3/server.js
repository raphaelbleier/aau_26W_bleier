// take the connection pool capabilities from the pg module
const { Pool } = require('pg');

let cfg = require('./config.json')

let express = require('express');
let cors = require('cors')
const app = express();
app.use(express.static('public')); // host public folder
app.use(cors()); // allow all origins -> Access-Control-Allow-Origin: *

const pool = require('./pool.js');  // the database pool

// EX3: this is necessary to allow parsing request bodies which contain json 
// it is also necessary to set the proper content type (application/json) in the request (e.g. in postman or RESTer)
let bodyParser = require('body-parser');
app.use(bodyParser.json()); // support json encoded bodies

app.get("/", (req, res) => {
    res.setHeader('Content-Type', 'text/html');
    res.status(200).send("EX3: This is a simple database-backed application");
});

app.get("/products", (req, res) => {

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
app.get("/product/:id", (req, res) => {
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
app.put("/product/:id", (req, res) => {
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
