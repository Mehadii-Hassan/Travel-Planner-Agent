let currentThreadId = null;

async function planTrip() {
    const userInputElement = document.getElementById('userInput');
    const planBtn = document.getElementById('planBtn');
    const errorMsg = document.getElementById('errorMsg');
    
    const loadingState = document.getElementById('loadingState');
    const resultsState = document.getElementById('resultsState');
    
    const message = userInputElement.value.trim();

    if (!message) {
        errorMsg.textContent = "Please enter your travel preferences first.";
        errorMsg.classList.remove('hidden');
        return;
    }

    // Reset UI
    errorMsg.classList.add('hidden');
    resultsState.classList.add('hidden');
    loadingState.classList.remove('hidden');
    
    // Disable button
    planBtn.disabled = true;
    planBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Planning...';

    const payload = {
        message: message,
        thread_id: currentThreadId
    };

    try {
        const response = await fetch('/api/travel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Save thread_id for continuous conversation
            currentThreadId = data.thread_id;

            // Populate DOM
            document.getElementById('finalAnswer').innerHTML = marked.parse(data.answer);
            document.getElementById('flights').textContent = data.flight_results || "No flight data available.";
            document.getElementById('hotels').textContent = data.hotel_results || "No hotel data available.";
            document.getElementById('rawItinerary').textContent = data.itinerary || "No raw itinerary available.";
            document.getElementById('llmCalls').textContent = data.llm_calls;

            // Show results
            loadingState.classList.add('hidden');
            resultsState.classList.remove('hidden');
            
            // Reset to first tab
            document.querySelector('.tab-btn').click();
        } else {
            throw new Error(data.error || "An unknown error occurred.");
        }
    } catch (error) {
        console.error("Error:", error);
        loadingState.classList.add('hidden');
        errorMsg.textContent = "Error: " + error.message;
        errorMsg.classList.remove('hidden');
    } finally {
        // Re-enable button
        planBtn.disabled = false;
        planBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Plan My Trip';
    }
}

// Tab Switching Logic
function switchTab(evt, tabId) {
    // Hide all tab contents
    const contents = document.getElementsByClassName("tab-content");
    for (let i = 0; i < contents.length; i++) {
        contents[i].classList.remove("active");
    }

    // Remove active class from all buttons
    const buttons = document.getElementsByClassName("tab-btn");
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove("active");
    }

    // Show current tab and add active class to clicked button
    document.getElementById(tabId).classList.add("active");
    evt.currentTarget.classList.add("active");
}

// Allow "Enter" key to submit, but Shift+Enter for new line
document.getElementById('userInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        planTrip();
    }
});