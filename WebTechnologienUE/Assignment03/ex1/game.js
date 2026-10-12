const MAX_ATTEMPTS = 3;

let welcome = document.getElementById("welcome");
let fieldset = document.getElementById("gameFieldset");
let input = document.getElementById("guessInput");
let checkButton = document.getElementById("checkButton");
let startButton = document.getElementById("startButton");
let buttons = document.getElementById("buttons");

// werden erst beim start erzeugt
let exitButton;
let messageDiv;
let guessesDiv;

let randomNumber;
let guesses = [];
let gameOver = false;

function startGame() {
    welcome.style.display = "none";
    startButton.style.display = "none";
    fieldset.style.display = "block";
    checkButton.style.display = "inline-block";

    // nur 1 bis 10 erlaubt
    input.min = 1;
    input.max = 10;
    input.required = true;
    input.value = "";

    // exit button dynamisch erzeugen
    exitButton = document.createElement("button");
    exitButton.textContent = "Exit Game";
    exitButton.style.backgroundColor = "red";
    exitButton.addEventListener("click", exitGame);
    buttons.appendChild(exitButton);

    // zwei divs fuer meldung und bisherige tipps, zwischen fieldset und buttons
    messageDiv = document.createElement("div");
    messageDiv.className = "feedback";
    guessesDiv = document.createElement("div");
    guessesDiv.className = "feedback";
    fieldset.after(messageDiv, guessesDiv);

    randomNumber = Math.floor(Math.random() * 10) + 1;
    guesses = [];
    gameOver = false;
    updateCheckButton();
}

// check nur aktiv wenn eine gueltige zahl drin steht
function updateCheckButton() {
    checkButton.disabled = gameOver || input.value === "" || !input.checkValidity();
}

function checkGuess() {
    let guess = Number(input.value);

    if (guess === randomNumber) {
        messageDiv.textContent = "Congratulations! " + guess + " is correct!";
        messageDiv.style.color = "green";
        gameOver = true;
    } else {
        messageDiv.textContent = guess > randomNumber ? "Too high!" : "Too low!";
        messageDiv.style.color = "black";
        guesses.push(guess);
        guessesDiv.textContent = "Previous guesses: " + guesses.join(", ");

        if (guesses.length >= MAX_ATTEMPTS) {
            messageDiv.textContent = "Game over! The correct number was " + randomNumber + ".";
            messageDiv.style.color = "red";
            gameOver = true;
        }
    }

    input.value = "";
    updateCheckButton();
}

function exitGame() {
    fieldset.style.display = "none";
    checkButton.style.display = "none";
    welcome.style.display = "block";
    startButton.style.display = "inline-block";

    guesses = [];
    messageDiv.remove();
    guessesDiv.remove();
    exitButton.remove();
}

startButton.addEventListener("click", startGame);
checkButton.addEventListener("click", checkGuess);
input.addEventListener("input", updateCheckButton);
