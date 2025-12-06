// renderer.js
document.addEventListener('DOMContentLoaded', () => {
    const chatDisplay = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Initial greeting from Finny (simulated)
    chatDisplay.value = "Finny: Hello! I'm Finny, your financial education assistant. Ask me anything about Indian finance!\n\n";

    sendButton.addEventListener('click', () => {
        sendMessage();
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    async function sendMessage() {
        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        const API_URL = 'http://127.0.0.1:5000/chat';

        // 1. Display user message
        chatDisplay.value += `You: ${userMessage}\n`;
        userInput.value = ''; // Clear input

        // 2. Call the Flask endpoint
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                // If Flask returns 4xx or 5xx
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP Status: ${response.status}`);
            }

            const data = await response.json();

            // 3. Display Finny's response
            chatDisplay.value += `Finny: ${data.response}\n\n`;

        } catch (error) {
            console.error(error);
            chatDisplay.value += `[Connection Error] Could not reach the backend server or API failed. (${error.message})\n\n`;
        }
        // Always scroll to the bottom
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }
});