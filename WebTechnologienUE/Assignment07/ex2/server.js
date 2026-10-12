// take the connection pool capabilities from the pg module
const { Pool } = require('pg');

let cfg = require('./config.json')

let express = require('express');
let cors = require('cors')
const app = express();
app.use(express.static('public')); // host public folder
app.use(cors()); // allow all origins -> Access-Control-Allow-Origin: *

const pool = require('./pool.js');  // the database pool

// EX6.3: this is necessary to allow parsing request bodies which contain json
// it is also necessary to set the proper content type (application/json) in the request (e.g. in postman or RESTer)
let bodyParser = require('body-parser');
app.use(bodyParser.json()); // support json encoded bodies

app.get("/", (req, res) => {
    res.setHeader('Content-Type', 'text/html');
    res.status(200).send("EX: This is a simple database-backed application");
});

// TODO: write your REST handlers here

// ---- hilfsfunktionen ----

function dbError(res, error) {
    console.log(error);
    res.status(500).json({ message: "Database error" });
}

// produkt mit tags und rating zurueckgeben, rating = L/(L+D), null wenn noch keine bewertung
const PRODUCT_SELECT = `
    SELECT p.*,
           COALESCE(array_agg(pt.tag ORDER BY pt.tag) FILTER (WHERE pt.tag IS NOT NULL), '{}') AS tags,
           CASE WHEN p.likes_count + p.dislikes_count = 0 THEN NULL
                ELSE p.likes_count::float / (p.likes_count + p.dislikes_count) END AS rating
    FROM products p
    LEFT JOIN products_tags pt ON pt.id = p.id`;

// ohne primary key muss man alle spalten im group by angeben
const PRODUCT_GROUP = " GROUP BY p.id, p.title, p.description, p.price, p.likes_count, p.dislikes_count";

function getProduct(id) {
    return pool.query(PRODUCT_SELECT + " WHERE p.id = $1" + PRODUCT_GROUP, [id])
        .then(results => results.rows[0]);
}

// ---- liste + suche ----
// alle query parameter sind optional und lassen sich kombinieren:
// ?search=text  teilstring in titel, beschreibung oder tag
// ?minPrice=500&maxPrice=1000  preis intervall
// ?minRating=0.6&maxRating=0.8  rating intervall (1/5 schritte = sterne)
app.get("/products", (req, res) => {
    let where = [];
    let values = [];

    if (req.query.search) {
        values.push("%" + req.query.search + "%");
        let n = values.length;
        where.push(`(p.title ILIKE $${n} OR p.description ILIKE $${n}
            OR EXISTS (SELECT 1 FROM products_tags t WHERE t.id = p.id AND t.tag ILIKE $${n}))`);
    }

    // zahlen pruefen bevor sie in die query kommen
    let numbers = { minPrice: "p.price >=", maxPrice: "p.price <=" };
    for (let key in numbers) {
        if (req.query[key] !== undefined) {
            let value = Number(req.query[key]);
            if (isNaN(value)) {
                return res.status(400).json({ message: key + " must be a number" });
            }
            values.push(value);
            where.push(numbers[key] + " $" + values.length);
        }
    }

    let ratings = { minRating: ">=", maxRating: "<=" };
    for (let key in ratings) {
        if (req.query[key] !== undefined) {
            let value = Number(req.query[key]);
            if (isNaN(value) || value < 0 || value > 1) {
                return res.status(400).json({ message: key + " must be a number between 0 and 1" });
            }
            values.push(value);
            // produkte ohne bewertung fallen bei der rating suche raus
            where.push(`(p.likes_count + p.dislikes_count > 0 AND
                p.likes_count::float / (p.likes_count + p.dislikes_count) ${ratings[key]} $${values.length})`);
        }
    }

    let query = PRODUCT_SELECT;
    if (where.length > 0) {
        query += " WHERE " + where.join(" AND ");
    }
    query += PRODUCT_GROUP + " ORDER BY p.id";

    pool.query(query, values)
        .then(results => res.status(200).json(results.rows))
        .catch(error => dbError(res, error));
});

// ---- einzelnes produkt ----
app.get("/products/:id", (req, res) => {
    getProduct(req.params.id)
        .then(product => {
            if (!product) {
                return res.status(404).json({ message: "Product " + req.params.id + " not found" });
            }
            res.status(200).json(product);
        })
        .catch(error => dbError(res, error));
});

function validProduct(body) {
    return typeof body.title === "string" && body.title !== ""
        && typeof body.description === "string"
        && Number.isInteger(body.price) && body.price >= 0;
}

// ---- anlegen ----
app.post("/products", (req, res) => {
    let p = req.body;
    if (typeof p.id !== "string" || p.id === "" || !validProduct(p)) {
        return res.status(400).json({ message: "id, title, description and price (integer) are required" });
    }

    // die tabelle hat keinen primary key, deshalb selbst pruefen ob die id schon existiert
    getProduct(p.id)
        .then(existing => {
            if (existing) {
                return res.status(409).json({ message: "Product " + p.id + " already exists" });
            }
            return pool.query("INSERT INTO products (id, title, description, price, likes_count, dislikes_count) VALUES ($1, $2, $3, $4, 0, 0)",
                [p.id, p.title, p.description, p.price])
                .then(() => getProduct(p.id))
                .then(product => {
                    res.location("/products/" + p.id);
                    res.status(201).json(product);
                });
        })
        .catch(error => dbError(res, error));
});

// ---- aendern (ganzes produkt ersetzen, likes bleiben) ----
app.put("/products/:id", (req, res) => {
    if (!validProduct(req.body)) {
        return res.status(400).json({ message: "title, description and price (integer) are required" });
    }
    pool.query("UPDATE products SET title = $1, description = $2, price = $3 WHERE id = $4",
        [req.body.title, req.body.description, req.body.price, req.params.id])
        .then(results => {
            if (results.rowCount === 0) {
                return res.status(404).json({ message: "Product " + req.params.id + " not found" });
            }
            return getProduct(req.params.id).then(product => res.status(200).json(product));
        })
        .catch(error => dbError(res, error));
});

// ---- loeschen, zuerst die tag zuordnungen ----
app.delete("/products/:id", (req, res) => {
    pool.query("DELETE FROM products_tags WHERE id = $1", [req.params.id])
        .then(() => pool.query("DELETE FROM products WHERE id = $1", [req.params.id]))
        .then(results => {
            if (results.rowCount === 0) {
                return res.status(404).json({ message: "Product " + req.params.id + " not found" });
            }
            res.status(204).end();
        })
        .catch(error => dbError(res, error));
});

// ---- like / dislike ----
function vote(column) {
    return (req, res) => {
        pool.query(`UPDATE products SET ${column} = ${column} + 1 WHERE id = $1`, [req.params.id])
            .then(results => {
                if (results.rowCount === 0) {
                    return res.status(404).json({ message: "Product " + req.params.id + " not found" });
                }
                return getProduct(req.params.id).then(product => res.status(200).json(product));
            })
            .catch(error => dbError(res, error));
    };
}

app.post("/products/:id/likes", vote("likes_count"));
app.post("/products/:id/dislikes", vote("dislikes_count"));

// ---- tags ----
app.get("/products/:id/tags", (req, res) => {
    getProduct(req.params.id)
        .then(product => {
            if (!product) {
                return res.status(404).json({ message: "Product " + req.params.id + " not found" });
            }
            res.status(200).json(product.tags);
        })
        .catch(error => dbError(res, error));
});

app.post("/products/:id/tags", (req, res) => {
    let tag = req.body.tag;
    if (typeof tag !== "string" || tag.trim() === "") {
        return res.status(400).json({ message: "tag is required" });
    }
    tag = tag.trim().toLowerCase();

    getProduct(req.params.id)
        .then(product => {
            if (!product) {
                return res.status(404).json({ message: "Product " + req.params.id + " not found" });
            }
            if (product.tags.includes(tag)) {
                return res.status(409).json({ message: "Product already has tag " + tag });
            }
            // neuen tag in die tags tabelle, falls es ihn noch nicht gibt
            return pool.query("INSERT INTO tags (tag) SELECT $1::varchar WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag = $1::varchar)", [tag])
                .then(() => pool.query("INSERT INTO products_tags (id, tag) VALUES ($1, $2)", [req.params.id, tag]))
                .then(() => getProduct(req.params.id))
                .then(updated => res.status(201).json(updated.tags));
        })
        .catch(error => dbError(res, error));
});

app.delete("/products/:id/tags/:tag", (req, res) => {
    pool.query("DELETE FROM products_tags WHERE id = $1 AND tag = $2", [req.params.id, req.params.tag.toLowerCase()])
        .then(results => {
            if (results.rowCount === 0) {
                return res.status(404).json({ message: "Product " + req.params.id + " has no tag " + req.params.tag });
            }
            res.status(204).end();
        })
        .catch(error => dbError(res, error));
});
	
let port = 3000;
app.listen(port);
console.log("Server running at: http://localhost:"+port);
