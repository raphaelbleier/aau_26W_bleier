const express = require('express');
const router = express.Router();

const pool = require('./pool.js');

// login route creating/returning a session on successful login
// note that the path here is "/" as "/login" is defined for the whole module, so no further path is necessary
// this route will be still called on http://localhost:3000/login
router.post('/', (req, res) => {

    // TODO: get login parameters from request body
    let user = req.body.user;
    let pass = req.body.pass;

    // prepare DB query
    // parameter statt string zusammenbauen, sonst sql injection
    const query = {
        text: "SELECT login FROM users WHERE login = $1 AND password = $2",
        values: [user, pass]
    };

    // issue query (returns promise)
    pool.query(query)
        .then (results => {
            let resultRows = results.rows;

			// TODO: handle no match (login failed)
            if (resultRows.length === 0) {
                return res.status(401).json({ message: "login failed" });
            }

            // handle the case if everything is ok
            let resultUser = resultRows[0];

			// TODO: create the session here
            req.session.isAuth = true;
            req.session.username = resultUser.login;

			res.status(200).json({
                "message": "login successful",
                login: resultUser.login,
            });

        })
        .catch(error => {
            // handle the errors accessing the database
            console.log(error);
            res.status(500).json({ message: "Database error" });
        });

});

module.exports = router;
