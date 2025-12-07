// renderer.js
document.addEventListener('DOMContentLoaded', () => {
    const chatDisplay = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Initial greeting from Finny (simulated)
    // NOTE: The backend system prompt controls the actual AI's first message.
    chatDisplay.value = "Finny: Hello! I'm Finny, your financial education assistant. Ask me anything about Indian finance!\n\n";

    sendButton.addEventListener('click', () => {
        sendMessage();
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // renderer.js

// ... (existing DOMContentLoaded setup)

async function sendMessage() {
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    const chatDisplay = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const API_URL = 'http://127.0.0.1:5000/chat';

    // 1. Display user message (as a new HTML element)
    chatDisplay.innerHTML += `<div class="user-message">You: ${userMessage}</div>`;
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
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP Status: ${response.status}`);
        }

        const data = await response.json();

        // --------------------------------------------------------------------------
        // CRITICAL FIX: MANUALLY CONVERT MARKDOWN TO RICH HTML

        let finnyResponse = data.response;

        // Step A: Replace common Markdown elements with HTML tags

        // Replace Heading (##) with <h3> tags
        finnyResponse = finnyResponse.replace(/^#+\s*(.*)$/gm, '<h3>$1</h3>');

        // Replace Bold (**) with <strong> tags
        finnyResponse = finnyResponse.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Step B: Handle Lists
        // Replace bullet points (*, -, +) with <li> tags, but we'll deal with the <ul> wrapper in Step C
        finnyResponse = finnyResponse.replace(/^\s*[\-\*\+]\s*(.*)$/gm, '<li>$1</li>');

        // Step C: Handle Paragraphs (This is the most crucial part for breaking the text)
        // Convert all remaining double newlines into closing/opening paragraph tags.
        // This ensures the AI's \n\n breaks are rendered as distinct paragraphs.
        finnyResponse = finnyResponse.replace(/\n\n/g, '</p><p>');

        // Step D: Clean up and wrap the entire response in a final container
        // This regex ensures list items are wrapped in <ul>, and the whole thing is in a final <div>.

        // Wrap any adjacent <li> items in <ul> tags
        finnyResponse = finnyResponse.replace(/(<li>.*?<\/li>)/g, '<ul>$1</ul>');

        // Wrap the entire output in paragraph tags if it doesn't already start with a block element
        if (!finnyResponse.startsWith('<h') && !finnyResponse.startsWith('<p') && !finnyResponse.startsWith('<ul')) {
             finnyResponse = '<p>' + finnyResponse + '</p>';
        }

        // Remove extraneous <p> tags around block elements (like <h3> or <ul>)
        finnyResponse = finnyResponse.replace(/<p>(<h3>)/g, '$1').replace(/(<\/h3>)<\/p>/g, '$1');
        finnyResponse = finnyResponse.replace(/<p>(<ul>)/g, '$1').replace(/(<\/ul>)<\/p>/g, '$1');

        // 3. Display Finny's final HTML response
        const aiMessageHTML = `<div class="ai-message">Finny: ${finnyResponse}</div>`;
        chatDisplay.innerHTML += aiMessageHTML;

        // --------------------------------------------------------------------------

    } catch (error) {
        console.error(error);
        const errorMessageHTML = `<div class="error-message">[Connection Error] Could not reach the backend server or API failed. (${error.message})</div>`;
        chatDisplay.innerHTML += errorMessageHTML;
    }
    // Always scroll to the bottom
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}
});