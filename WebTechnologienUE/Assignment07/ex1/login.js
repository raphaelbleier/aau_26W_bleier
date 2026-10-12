let cfg = require('./config.json')
const express = require('express');
const router = express.Router();

const pool = require('./pool.js');

const jwt = require('jsonwebtoken');

// login route creating/returning a token on successful login
router.post('/', (req, res) => {

    // TODO: get login parameters from request body
    let user = req.body.user;
    let pass = req.body.pass;

    // prepare DB query
    const query = {
        text: "SELECT login FROM users WHERE login = $1 AND password = $2",
        values: [user, pass]
    };

    // issue query (returns promise)
    pool.query(query)
        .then (results => {
            let resultRows = results.rows;

			// handle no match (login failed)
            if (resultRows.length === 0) {
                return res.status(401).json({ message: "login failed" });
            }

            // everything is ok
            let resultUser = resultRows[0];

            // im payload steht der login, damit man spaeter weiss wer eingeloggt ist
			const token = jwt.sign(
                { login: resultUser.login },
                cfg.auth.jwt_key,
                { expiresIn: cfg.auth.expiration }
            );

			res.status(200).json({
                "message": "login successful",
                login: resultUser.login,
                token: token
            });

        })
        .catch(error => {
            // handle error accessing db
            console.log(error);
            res.status(500).json({ message: "Database error" });
        });

});

module.exports = router;
