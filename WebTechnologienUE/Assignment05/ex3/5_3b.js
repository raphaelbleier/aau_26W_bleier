

const eventLog = document.getElementById('eventLog');

function delayedCalc(a,b) {
	const promise = new Promise(
		(resolve, reject) => {
			if (a > b) {
				setTimeout( 
					() => {
						let c = a+b;
						eventLog.innerHTML += a+" + "+b+" = "+c+"<br>";						
						resolve(c)
					}, 
					Math.floor(Math.random() * 2000));
			}
			else {
				reject('error: b larger than a');
				eventLog.innerHTML += "rejected<br>";						
			}
		});
	return promise;
}


// Change the code below to correctly use promises for a delayed incremental computation
// of 5+3+7+14+23+25+1000+1 

// b: jedes ergebnis wird an den naechsten aufruf weitergegeben,
// der naechste startet erst wenn der vorherige fertig ist
delayedCalc(5, 3)
	.then(result => delayedCalc(result, 7))
	.then(result => delayedCalc(result, 14))
	.then(result => delayedCalc(result, 23))
	.then(result => delayedCalc(result, 25))
	.then(result => delayedCalc(result, 1000))
	.then(result => delayedCalc(result, 1))
	.catch(error => handleError(error));


function handleError(error) {
	alert(error);
}



