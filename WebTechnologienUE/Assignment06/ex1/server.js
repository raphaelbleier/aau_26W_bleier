let express = require('express');
const app = express();
app.use(express.static('public')); // host public folder
app.get('/', function (req, res) {

	// TODO: set the content type of output to be plain HTML
	res.setHeader('Content-Type', 'text/html');

    res.status(200).send("This is a simple application");
});

// TODO: provide the code to handle a route parameter
// :text ist der route parameter, steht dann in req.params.text
app.get('/:text', function (req, res) {
	res.setHeader('Content-Type', 'text/html');
	res.status(200).send("This is a simple application receiving " + req.params.text);
});

let port = 3000;
app.listen(port);
console.log("Server running at: http://localhost:"+port);
