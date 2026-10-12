// anzahl versuche pro spiel
const MAX_ATTEMPTS = 3;
// ob der user weiterspielen will
let keepPlaying = true;

while (keepPlaying) {
    // zufallszahl zwischen 1 und 10
    let randomNumber = Math.floor(Math.random() * 10) + 1;
    playNumberGame(randomNumber);

    keepPlaying = confirm("Do you want to play again?");
    if (!keepPlaying) {
        alert("Thank you for playing!");
    }
}

function playNumberGame(secretNumber) {
    let guesses = [];

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        let guess = getUserInput();
        guesses.push(guess);

        // bei falscher eingabe kommt der fehlertext zurueck statt einer zahl
        if (typeof guess !== "number") {
            alert(guess);
        } else if (guess === secretNumber) {
            alert("Correct! You needed " + attempt + " attempt(s).");
            return true;
        } else {
            if (guess > secretNumber) {
                alert("Too high! Attempts so far: " + attempt);
            } else {
                alert("Too low! Attempts so far: " + attempt);
            }
            // fehlertexte von ungueltigen eingaben nicht mit anzeigen
            let numbers = guesses.filter(g => typeof g === "number");
            alert("Your previous guesses: " + numbers.join(", "));
        }
    }

    alert("No attempts left. The correct number was " + secretNumber + ".");
    return false;
}

function getUserInput() {
    let input = prompt("Enter a number between 1 and 10:");
    let number = Number(input);

    try {
        // leere eingabe wird bei Number() zu 0, faellt also auch raus
        if (isNaN(number) || number < 1 || number > 10) {
            throw new Error("Invalid input. Please enter a number between 1 and 10.");
        }
        return number;
    } catch (error) {
        return error.message;
    }
}
