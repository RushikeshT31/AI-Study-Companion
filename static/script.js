// =========================================================
// READ ALOUD
// =========================================================

let speech = null;


// ---------------------------------------------------------
// READ TEXT
// ---------------------------------------------------------

function readText() {

    const textBox = document.getElementById("readText");

    if (!textBox) {
        return;
    }


    const text = textBox.value.trim();


    if (!text) {

        alert("Please enter some text first.");

        return;
    }


    // Stop previous speech

    window.speechSynthesis.cancel();


    speech = new SpeechSynthesisUtterance(text);


    // Reading speed

    const speedElement =
        document.getElementById("speed");


    if (speedElement) {

        speech.rate =
            parseFloat(speedElement.value);

    } else {

        speech.rate = 1;

    }


    // Normal pitch

    speech.pitch = 1;


    // Default volume

    speech.volume = 1;


    // Status

    speech.onstart = function () {

        updateSpeechStatus(
            "🔊 Reading..."
        );

    };


    speech.onend = function () {

        updateSpeechStatus(
            "✅ Reading completed!"
        );

    };


    speech.onerror = function () {

        updateSpeechStatus(
            "❌ Unable to read the text."
        );

    };


    window.speechSynthesis.speak(speech);

}


// ---------------------------------------------------------
// PAUSE
// ---------------------------------------------------------

function pauseText() {

    if (window.speechSynthesis.speaking) {

        window.speechSynthesis.pause();

        updateSpeechStatus(
            "⏸ Reading paused."
        );

    }

}


// ---------------------------------------------------------
// RESUME
// ---------------------------------------------------------

function resumeText() {

    if (window.speechSynthesis.paused) {

        window.speechSynthesis.resume();

        updateSpeechStatus(
            "▶ Reading resumed."
        );

    }

}


// ---------------------------------------------------------
// STOP
// ---------------------------------------------------------

function stopText() {

    window.speechSynthesis.cancel();

    updateSpeechStatus(
        "⏹ Reading stopped."
    );

}


// ---------------------------------------------------------
// UPDATE STATUS
// ---------------------------------------------------------

function updateSpeechStatus(message) {

    const status =
        document.getElementById("speechStatus");


    if (status) {

        status.textContent = message;

    }

}


// =========================================================
// SPEED CONTROL
// =========================================================

const speed =
    document.getElementById("speed");


const speedValue =
    document.getElementById("speedValue");


if (speed && speedValue) {

    speed.addEventListener(
        "input",
        function () {

            speedValue.textContent =
                this.value + "x";

        }
    );

}
// =========================================================
// STUDY TIMER
// =========================================================

let timerInterval = null;
let timerSeconds = 25 * 60;
let selectedMinutes = 25;
let timerRunning = false;


// =========================================================
// DISPLAY TIMER
// =========================================================

function updateTimerDisplay() {

    const display =
        document.getElementById("timerDisplay");

    if (!display) {
        return;
    }

    const minutes =
        Math.floor(timerSeconds / 60);

    const seconds =
        timerSeconds % 60;

    display.textContent =
        String(minutes).padStart(2, "0") +
        ":" +
        String(seconds).padStart(2, "0");
}


// =========================================================
// SET TIMER
// =========================================================

function setTimer(minutes) {

    clearInterval(timerInterval);

    timerRunning = false;

    selectedMinutes = minutes;

    timerSeconds = minutes * 60;

    updateTimerDisplay();

    updateTimerStatus(
        "Ready to study 📚"
    );
}


// =========================================================
// START TIMER
// =========================================================

function startTimer() {

    if (timerRunning) {
        return;
    }

    if (timerSeconds <= 0) {
        return;
    }

    timerRunning = true;

    updateTimerStatus(
        "🔥 Study session is running..."
    );


    timerInterval = setInterval(
        function () {

            if (timerSeconds > 0) {

                timerSeconds--;

                updateTimerDisplay();

            }


            // Timer completed

            if (timerSeconds <= 0) {

                clearInterval(timerInterval);

                timerRunning = false;

                updateTimerDisplay();

                updateTimerStatus(
                    "🎉 Study session completed!"
                );

                saveStudyTime(
                    selectedMinutes
                );

                alert(
                    "🎉 Great job! Your study session is completed."
                );
            }

        },
        1000
    );
}


// =========================================================
// PAUSE TIMER
// =========================================================

function pauseTimer() {

    if (!timerRunning) {
        return;
    }

    clearInterval(timerInterval);

    timerRunning = false;

    updateTimerStatus(
        "⏸ Timer paused."
    );
}


// =========================================================
// RESET TIMER
// =========================================================

function resetTimer() {

    clearInterval(timerInterval);

    timerRunning = false;

    timerSeconds =
        selectedMinutes * 60;

    updateTimerDisplay();

    updateTimerStatus(
        "Ready to study 📚"
    );
}


// =========================================================
// TIMER STATUS
// =========================================================

function updateTimerStatus(message) {

    const status =
        document.getElementById("timerStatus");

    if (status) {

        status.textContent = message;

    }
}


// =========================================================
// SAVE STUDY TIME
// =========================================================

function saveStudyTime(minutes) {

    fetch("/timer/save", {

        method: "POST",

        headers: {
            "Content-Type":
                "application/x-www-form-urlencoded"
        },

        body:
            "minutes=" +
            encodeURIComponent(minutes)

    })
    .then(function(response) {

        if (!response.ok) {

            throw new Error(
                "Failed to save study time."
            );

        }

        return response.text();

    })
    .then(function() {

        console.log(
            "Study time saved successfully."
        );

    })
    .catch(function(error) {

        console.error(
            "Timer save error:",
            error
        );

    });
}


// =========================================================
// INITIALIZE TIMER
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateTimerDisplay();

    }
);
