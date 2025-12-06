from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import random
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')

# --- API Endpoints ---

@app.route('/api/config/firebase')
def get_firebase_config():
    """Returns Firebase configuration safely."""
    return jsonify({
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID')
    })

@app.route('/api/coach/chat', methods=['POST'])
def chat_with_coach():
    """Mock LLM Chat Endpoint."""
    data = request.json
    user_msg = data.get('message', '')
    mode = data.get('mode', 'quick')
    
    # Simulate network delay
    time.sleep(1)
    
    # Mock Responses based on mode/input
    if mode == 'explain':
        response = "I see you're asking about a specific concept. Let me break it down: [Explanation Placeholder]"
    elif "budget" in user_msg.lower():
        response = "Budgeting is key! Try the 50/30/20 rule: 50% Needs, 30% Wants, 20% Savings."
    else:
        response = f"That's interesting! You said: '{user_msg}'. As your AI coach, I recommend checking your spending snapshot."
        
    return jsonify({'response': response})

@app.route('/api/academy/quiz', methods=['GET'])
def get_quiz():
    """Mock Quiz Generation."""
    track = request.args.get('track', 'general')
    questions = [
        {
            "id": 1,
            "question": "What is the primary goal of budgeting?",
            "options": ["Restrict fun", "Track income vs expenses", "Pay more taxes", "None of the above"],
            "correct": 1
        },
        {
            "id": 2,
            "question": "Which of these improves your credit score?",
            "options": ["Missing payments", "High credit utilization", "Paying on time", "Closing old accounts"],
            "correct": 2
        }
    ]
    return jsonify({'questions': questions})

@app.route('/api/mail/welcome', methods=['POST'])
def send_welcome():
    """Mock Welcome Email."""
    return jsonify({'status': 'sent', 'message': 'Welcome email queued.'})

# --- Main Route ---

@app.route('/')
def index():
    """Serves the main SPA shell."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)