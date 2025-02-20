document.addEventListener("DOMContentLoaded", function () {
    let draggedItem = null;
    let score = 0;
    let matchedCount = 0;

    const numbers = document.querySelectorAll(".number");
    const slots = document.querySelectorAll(".sign-slot");
    const submitButton = document.getElementById("submit-btn");
    const timerElement = document.getElementById("time");
    const finalScoreInput = document.getElementById("final-score");
    const totalNumbers = numbers.length; // Total numbers to match

    let timeLeft = parseFloat(timerElement.textContent); // Get initial time from HTML

    // ✅ Initialize Drag-and-Drop functionality
    numbers.forEach((number) => {
        number.addEventListener("dragstart", function () {
            draggedItem = this;
        });
    });

    slots.forEach((slot) => {
        slot.addEventListener("dragover", function (event) {
            event.preventDefault();
        });

        slot.addEventListener("drop", function () {
            if (draggedItem) {
                let correctNumber = this.getAttribute("data-number");
                let selectedNumber = draggedItem.getAttribute("data-number");

                if (correctNumber === selectedNumber) {
                    this.appendChild(draggedItem);
                    score++;  // ✅ Increase score if correct
                    matchedCount++;

                    // Show correct message
                    this.innerHTML += `<p style="color:green; font-weight:bold;">✔️</p>`;

                    // Remove the number from selection
                    draggedItem.remove();
                    draggedItem = null;

                    // ✅ Check if player has matched all numbers
                    if (matchedCount === totalNumbers) {
                        showWellDoneMessage();
                    }
                } else {
                    this.innerHTML += `<p style="color:red; font-weight:bold;">❌</p>`;
                }
            }
        });
    });

    // ✅ Start Countdown Timer
    function countdown() {
        if (timeLeft > 0) {
            timeLeft--;
            timerElement.textContent = timeLeft;
            setTimeout(countdown, 1000);
        } else {
            alert("⏳ Time's up! Submitting score...");
            redirectToScorePage();
        }
    }

    countdown();

    // ✅ Submit Button Click Event
    submitButton.addEventListener("click", function () {
        if (matchedCount < totalNumbers) {
            alert("⚠️ You haven't matched all numbers yet!");
            return;
        }
        redirectToScorePage();
    });

    // ✅ Redirect to Score Page and Send Score via AJAX
    function redirectToScorePage() {
        finalScoreInput.value = score;

        console.log(`📌 Sending Score: ${score}`); // ✅ Debugging

        fetch("/store-drag-drop-score/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("input[name='csrfmiddlewaretoken']").value,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ score: score }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(`🎉 Game Over! Your Score: ${score}`);
                console.log("✅ Score saved successfully"); // ✅ Debugging
                window.location.href = "/score3/?score=" + score; // ✅ Redirect to score page
            } else {
                console.error("❌ Error saving score:", data);
                alert("⚠️ Error saving score. Please try again.");
            }
        })
        .catch(error => console.error("❌ AJAX Error:", error));
    }

    // ✅ Show "Well Done" Message
    function showWellDoneMessage() {
        const gameContainer = document.querySelector(".game-container");

        // Blur the background
        gameContainer.style.filter = "blur(5px)";
        gameContainer.style.pointerEvents = "none"; // Disable interactions

        // Create "Well Done" message
        const message = document.createElement("div");
        message.innerHTML = `
            <h2 style="color: #4CAF50; font-size: 2.5rem; text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.1);">
                🎉 Well Done! 🎉
            </h2>
            <p style="font-size: 1.5rem; color: #555;">You matched all the numbers correctly!</p>
        `;
        message.style.position = "fixed";
        message.style.top = "50%";
        message.style.left = "50%";
        message.style.transform = "translate(-50%, -50%)";
        message.style.padding = "20px";
        message.style.borderRadius = "10px";
        message.style.background = "white";
        message.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.2)";
        message.style.textAlign = "center";
        message.style.zIndex = "1000";

        document.body.appendChild(message);

        // ✅ Wait 2 seconds and then redirect
        setTimeout(redirectToScorePage, 2000);
    }
});
