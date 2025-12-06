from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import time
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    """Mock LLM Chat Endpoint (or Real if Key exists)."""
    data = request.json
    user_msg = data.get('message', '')
    mode = data.get('mode', 'quick')
    
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"You are a helpful financial coach named FinSense. Mode: {mode}. User says: {user_msg}. Keep it short and helpful."
            response = model.generate_content(prompt).text
            return jsonify({'response': response})
        except Exception as e:
            print(f"Gemini Error: {e}")
            # Fallback to mock
            pass

    # Mock Responses
    time.sleep(1)
    if mode == 'explain':
        response = "I see you're asking about a specific concept. Let me break it down: [Explanation Placeholder]"
    elif "budget" in user_msg.lower():
        response = "Budgeting is key! Try the 50/30/20 rule: 50% Needs, 30% Wants, 20% Savings."
    else:
        response = f"That's interesting! You said: '{user_msg}'. As your AI coach, I recommend checking your spending snapshot."
        
    return jsonify({'response': response})

@app.route('/api/academy/quiz', methods=['GET'])
def get_quiz():
    """Dynamic Quiz Generation using Gemini."""
    track = request.args.get('track', 'general')
    
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Generate 5 multiple-choice questions about '{track}' in finance.
            Return ONLY valid JSON in this format:
            {{
                "questions": [
                    {{
                        "id": 1,
                        "question": "Question text",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct": 0
                    }}
                ]
            }}
            The 'correct' field should be the index (0-3) of the correct option.
            """
            response = model.generate_content(prompt).text
            # Clean up markdown code blocks if present
            cleaned_response = response.replace('```json', '').replace('```', '').strip()
            return jsonify(json.loads(cleaned_response))
        except Exception as e:
            print(f"Gemini Quiz Error: {e}")
            # Fallback to mock
            pass

    # Fallback Mock Questions
    questions = [
        {
            "id": 1,
            "question": "What is the 50/30/20 rule of budgeting?",
            "options": ["50% Needs, 30% Wants, 20% Savings", "50% Savings, 30% Needs, 20% Wants", "50% Wants, 30% Savings, 20% Needs", "None of the above"],
            "correct": 0
        },
        {
            "id": 2,
            "question": "Which factor has the highest impact on your credit score?",
            "options": ["Credit Mix", "New Credit", "Payment History", "Length of Credit History"],
            "correct": 2
        },
        {
            "id": 3,
            "question": "What is a 'Bear Market'?",
            "options": ["A market where prices are rising", "A market where prices are falling", "A market for trading animals", "A stable market"],
            "correct": 1
        },
        {
            "id": 4,
            "question": "What does ROI stand for?",
            "options": ["Rate of Inflation", "Return on Investment", "Risk of Investment", "Real Owner Interest"],
            "correct": 1
        },
        {
            "id": 5,
            "question": "Which account typically offers the highest interest rate?",
            "options": ["Checking Account", "Savings Account", "Certificate of Deposit (CD)", "Under the mattress"],
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
