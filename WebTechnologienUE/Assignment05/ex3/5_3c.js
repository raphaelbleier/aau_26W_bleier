

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

// c: gleiche rechnung mit async/await
async function calculate() {
	try {
		let result = await delayedCalc(5, 3);
		result = await delayedCalc(result, 7);
		result = await delayedCalc(result, 14);
		result = await delayedCalc(result, 23);
		result = await delayedCalc(result, 25);
		result = await delayedCalc(result, 1000);
		result = await delayedCalc(result, 1);
	} catch (error) {
		handleError(error);
	}
}

calculate();


function handleError(error) {
	alert(error);
}



