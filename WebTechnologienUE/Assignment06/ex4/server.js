let cfg = require('./config.json')

let express = require('express');
let cors = require('cors')
const app = express();

app.use(express.static('public')); // host public folder
app.use(cors()); // allow all origins -> Access-Control-Allow-Origin: *

// the database pool, see EX3
const pool = require('./pool.js');

// this is necessary to implement session-based authentication 
const session = require('express-session');
// this is necessary to allow session data to be stored in the PostgreSQL database
const pgSession = require('connect-pg-simple')(session);

// EX3: this is necessary to allow parsing request bodies which contain json 
// it is also necessary to set the proper content type (application/json) in the request (e.g. in postman or RESTer)
let bodyParser = require('body-parser');
app.use(bodyParser.json());

// this is necessary to provide authentication to access the routes
const checkAuth = require('./check_auth');

app.use(session({
 resave: false,  // let it be like this
 saveUninitialized: false,  // let it be like this

// TODO: initialize further session parameters here
 // sessions werden in der db gespeichert, tabelle sessions
 store: new pgSession({
  pool: pool,
  tableName: 'sessions',
  createTableIfMissing: true
 }),
 cookie: { maxAge: 1000 * 60 * 60 }, // 1 hour
 secret: "secret"

}));

// the express router inherits the properties of the application
// including the session, so this has to be defined after the session is added to the app object
const loginRoutes = require('./login');
app.use("/login", loginRoutes);

// default route, no principal changes from EX3
app.get("/", (req, res) => {
    
	// TODO: set content type (from EX1)
	res.setHeader('Content-Type', 'text/html');

    res.status(200).send("EX4: This is a database-backed application which uses JWT");
});

// TODO: copy the /products and /product route handlers from EX3 here
// TODO: and add the authentication callback from check_auth.js to their definitions
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

// TODO: implement the logout handler here
app.get("/logout", (req, res) => {
    req.session.destroy(error => {
        // nach destroy sollte req.session nicht mehr existieren
        if (error || req.session !== undefined) {
            return res.status(500).json({ message: "Logout failed" });
        }
        res.status(200).json({ message: "Logout successful" });
    });
});
  
let port = 3000;
app.listen(port);
console.log("Server running at: http://localhost:"+port);
