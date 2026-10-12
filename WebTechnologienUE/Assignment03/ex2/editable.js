let sections = document.querySelectorAll("section");
let lastSection = sections[sections.length - 1];

// formular zusammenbauen
let form = document.createElement("form");

let select = document.createElement("select");
let headingInput = document.createElement("input");
headingInput.type = "text";
let textarea = document.createElement("textarea");
textarea.rows = 10;
textarea.cols = 80;
let submitButton = document.createElement("button");
submitButton.type = "submit";
submitButton.textContent = "Update section";
submitButton.disabled = true;

form.append(select, document.createElement("br"),
    headingInput, document.createElement("br"),
    textarea, document.createElement("br"),
    submitButton);
lastSection.after(form);

// select mit den ueberschriften der sections befuellen
function fillSelect() {
    let selected = select.value;
    select.innerHTML = "";

    let empty = document.createElement("option");
    empty.value = "";
    empty.textContent = "-- choose a section --";
    select.appendChild(empty);

    for (let i = 0; i < sections.length; i++) {
        let h1 = sections[i].querySelector("h1");
        let option = document.createElement("option");
        option.value = i;
        option.textContent = h1 ? h1.textContent : "(section " + (i + 1) + " without heading)";
        select.appendChild(option);
    }
    // auswahl nach dem neu befuellen behalten
    select.value = selected;
}

function sectionSelected() {
    if (select.value === "") {
        headingInput.value = "";
        textarea.value = "";
        submitButton.disabled = true;
        return;
    }
    let section = sections[select.value];
    let h1 = section.querySelector("h1");
    headingInput.value = h1 ? h1.textContent : "";
    textarea.value = section.innerHTML;
    submitButton.disabled = false;
}

function updateSection(e) {
    // sonst wird die seite neu geladen
    e.preventDefault();
    let section = sections[select.value];
    section.innerHTML = textarea.value;

    // ueberschrift kommt immer aus dem input feld, nicht aus der textarea
    let h1 = section.querySelector("h1");
    if (headingInput.value.trim() !== "") {
        // falls der user das h1 im html geloescht hat, neu anlegen
        if (!h1) {
            h1 = document.createElement("h1");
            section.prepend(h1);
        }
        h1.textContent = headingInput.value;
    } else if (h1) {
        h1.remove();
    }

    fillSelect();
    sectionSelected();
}

fillSelect();
select.addEventListener("change", sectionSelected);
form.addEventListener("submit", updateSection);
