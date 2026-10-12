module.exports = (req, res, next) => {

	// verify if the session exists, if yes, call the next middleware function
	if (req.session && req.session.isAuth === true) {
		return next();
	}

	// if no, use the code below
	return res.status(401).json({message: "Authentication failed"});
};
