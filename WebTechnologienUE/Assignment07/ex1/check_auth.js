let cfg = require('./config.json')
const jwt = require('jsonwebtoken');

// EX TODO:
// - verify token using jwt_key of "secret"
// - set req.userData to the user information stored in the token's payload
module.exports = (req, res, next) => {
    try {
        // token kommt im authorization header, mit oder ohne "Bearer " davor
        let token = req.headers.authorization;
        if (token.startsWith("Bearer ")) {
            token = token.substring(7);
        }
        // wirft einen fehler wenn der token falsch oder abgelaufen ist
        const decoded = jwt.verify(token, cfg.auth.jwt_key);
        req.userData = decoded;
        next();
    } catch (error) {
        // auch wenn gar kein header da ist landet man hier (undefined.startsWith)
        return res.status(401).json({message: "Authentication failed"});
    }
};
