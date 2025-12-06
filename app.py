from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

# --- Flask App Config ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_hackathon_secret_key')

# --- Initialize Firebase Admin ---
try:
    # Check if the JSON file exists
    cred_path = "firebase/service-account.json"
    
    if not os.path.exists(cred_path):
        print(f"❌ Firebase credentials not found at: {cred_path}")
        print("   Please download service account JSON from Firebase Console:")
        print("   https://console.firebase.google.com/project/finsenseai-834cf/settings/serviceaccounts/adminsdk")
        db = None
    else:
        cred = credentials.Certificate(cred_path)
        
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin initialized successfully!")
        
        db = firestore.client()
        
except Exception as e:
    print(f"❌ Firebase initialization error: {e}")
    db = None

# Temporary DEFAULT user ID for demo
USER_ID = "user123"

# In-memory fallback if Firebase fails
user_data = {
    'user123': {
        'username': 'BudgetBoss',
        'level': 5,
        'xp': 780,
        'net_worth': 45000,
        'budget_limit': {'food': 8000, 'entertainment': 3000, 'savings': 5000},
        'spending_log': []
    }
}

# ----------------- FIREBASE FUNCTIONS -----------------

def get_user_data(user_id):
    """Fetch user document from Firestore or use fallback."""
    if db:
        try:
            doc_ref = db.collection('users').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                # Create default user
                default_data = {
                    'username': 'BudgetBoss',
                    'level': 5,
                    'xp': 780,
                    'net_worth': 45000,
                    'budget_limit': {'food': 8000, 'entertainment': 3000, 'savings': 5000},
                    'spending_log': []
                }
                doc_ref.set(default_data)
                return default_data
        except Exception as e:
            print(f"⚠️ Firestore error: {e}")
            return user_data.get(user_id, user_data['user123'])
    
    return user_data.get(user_id, user_data['user123'])

def update_user_data(user_id, data):
    """Update user data in Firestore or memory."""
    if db:
        try:
            db.collection('users').document(user_id).update(data)
            return True
        except Exception as e:
            print(f"⚠️ Firestore update error: {e}")
    
    # Fallback to memory
    if user_id in user_data:
        user_data[user_id].update(data)
    else:
        user_data[user_id] = data
    return True

def calculate_current_spending(user):
    """Calculate total spending for all categories."""
    log = user['spending_log']
    spending = {'food': 0, 'entertainment': 0, 'savings': 0}
    
    for item in log:
        category = item['category']
        if category in spending:
            spending[category] += item['amount']
    
    return spending

def check_for_ai_nudge(user):
    spending = calculate_current_spending(user)
    budget = user['budget_limit']
    
    nudges = []
    
    for category in ['food', 'entertainment']:
        if spending[category] > budget[category] * 0.50:
            nudges.append({
                'message': f"⚠️ You've spent ₹{spending[category]} on {category}, "
                          f"which is over 50% of your ₹{budget[category]} limit!",
                'type': 'warning'
            })
    
    return nudges if nudges else None

def update_xp(user, amount):
    user['xp'] += amount
    level_updated = False
    if user['xp'] >= 1000:
        user['level'] += 1
        user['xp'] = 0
        level_updated = True
    return level_updated

# ----------------- ROUTES -----------------

@app.route('/')
def dashboard():
    user = get_user_data(USER_ID)
    spending = calculate_current_spending(user)
    
    food_progress = (spending['food'] / user['budget_limit']['food']) * 100 if user['budget_limit']['food'] > 0 else 0
    entertainment_progress = (spending['entertainment'] / user['budget_limit']['entertainment']) * 100 if user['budget_limit']['entertainment'] > 0 else 0
    
    nudge = check_for_ai_nudge(user)

    return render_template("dashboard.html",
                           username=user['username'],
                           level=user['level'],
                           xp=user['xp'],
                           net_worth=user['net_worth'],
                           nudge=nudge,
                           food_progress=food_progress,
                           entertainment_progress=entertainment_progress,
                           budget_limit=user['budget_limit'],
                           spending=spending)

@app.route('/log_expense', methods=['GET', 'POST'])
def log_expense():
    if request.method == 'POST':
        category = request.form.get('category')
        amount = int(request.form.get('amount'))
        description = request.form.get('description', '')

        user = get_user_data(USER_ID)

        new_entry = {
            'category': category,
            'amount': amount,
            'description': description,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        updated_log = user['spending_log'] + [new_entry]
        new_networth = user['net_worth'] - amount

        level_updated = update_xp(user, 50)

        update_user_data(USER_ID, {
            'spending_log': updated_log,
            'net_worth': new_networth,
            'xp': user['xp'],
            'level': user['level']
        })

        return redirect(url_for('dashboard'))

    return render_template('log_expense.html')

# ----------------- API ROUTES -----------------

@app.route('/api/config/firebase')
def get_firebase_config():
    """Safely provide Firebase config."""
    return jsonify({
        'apiKey': os.getenv('FIREBASE_API_KEY', ''),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': os.getenv('FIREBASE_PROJECT_ID', ''),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', ''),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': os.getenv('FIREBASE_APP_ID', '')
    })

@app.route('/api/user/data')
def get_user_api():
    """API endpoint for user data."""
    user = get_user_data(USER_ID)
    spending = calculate_current_spending(user)
    
    food_progress = (spending['food'] / user['budget_limit']['food']) * 100 if user['budget_limit']['food'] > 0 else 0
    entertainment_progress = (spending['entertainment'] / user['budget_limit']['entertainment']) * 100 if user['budget_limit']['entertainment'] > 0 else 0
    
    nudge = check_for_ai_nudge(user)
    
    return jsonify({
        'username': user['username'],
        'level': user['level'],
        'xp': user['xp'],
        'net_worth': user['net_worth'],
        'budget_limit': user['budget_limit'],
        'spending_log': user['spending_log'][-5:],
        'food_progress': food_progress,
        'entertainment_progress': entertainment_progress,
        'spending': spending,
        'nudge': nudge
    })

@app.route('/api/log/expense', methods=['POST'])
def log_expense_api():
    """API endpoint to log expenses."""
    try:
        data = request.json
        category = data.get('category')
        amount = float(data.get('amount'))
        description = data.get('description', '')

        user = get_user_data(USER_ID)

        new_entry = {
            'category': category,
            'amount': amount,
            'description': description,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        updated_log = user['spending_log'] + [new_entry]
        new_networth = user['net_worth'] - amount

        level_updated = update_xp(user, 50)

        update_user_data(USER_ID, {
            'spending_log': updated_log,
            'net_worth': new_networth,
            'xp': user['xp'],
            'level': user['level']
        })

        return jsonify({
            'status': 'success',
            'message': 'Expense logged successfully',
            'level_updated': level_updated,
            'new_networth': new_networth,
            'xp_gained': 50
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'firebase': 'connected' if db else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

# Run app
if __name__ == '__main__':
    print("🚀 Starting FinSenseAI Flask Server")
    print("=" * 50)
    print(f"📁 Project: {os.getcwd()}")
    print(f"🔐 Firebase: {'✅ Connected' if db else '❌ Not connected'}")
    print(f"🌐 Server: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, port=5000)





























# from flask import Flask, render_template, request, redirect, url_for, jsonify, session
# from datetime import datetime
# from dotenv import load_dotenv
# import os
# import time
# import google.generativeai as genai
# import json
# import firebase_admin
# from firebase_admin import credentials, firestore, auth as admin_auth

# # Load environment variables
# load_dotenv()

# # --- Flask App Config ---
# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_hackathon_secret_key')
# app.config['SESSION_TYPE'] = 'filesystem'

# # Configure Gemini
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)

# # --- Initialize Firebase Admin ---
# # Use the correct path to your JSON file in the firebase folder
# try:
#     # Path to your service account JSON file
#     cred_path = "firebase/service-account.json"
    
#     # Check if file exists
#     if not os.path.exists(cred_path):
#         raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")
    
#     cred = credentials.Certificate(cred_path)
    
#     # Initialize Firebase Admin if not already initialized
#     if not firebase_admin._apps:
#         firebase_admin.initialize_app(cred)
    
#     print("✅ Firebase Admin initialized successfully!")
    
# except Exception as e:
#     print(f"❌ Firebase Admin initialization failed: {e}")
#     # Fallback to in-memory storage for demo
#     print("⚠️  Using in-memory storage as fallback")
#     firebase_admin = None

# # Get Firestore client if Firebase is initialized
# if firebase_admin and firebase_admin._apps:
#     db = firestore.client()
# else:
#     db = None

# # Firebase Client configuration (for frontend)
# firebase_client_config = {
#     "apiKey": os.getenv('FIREBASE_API_KEY', "AIzaSyCJNlKOrGxt19Ewv_MTH9XLb-JPlEOZMq"),
#     "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN', "finsenseai-834cf.firebaseapp.com"),
#     "projectId": os.getenv('FIREBASE_PROJECT_ID', "finsenseai-834cf"),
#     "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET', "finsenseai-834cf.firebasestorage.app"),
#     "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID', "1089787327198"),
#     "appId": os.getenv('FIREBASE_APP_ID', "1:1089787327198:web:a847d5d61df1444849c84f"),
# }

# # Temporary DEFAULT user ID for demo
# USER_ID = "user123"

# # In-memory fallback storage (used if Firebase fails)
# user_data = {
#     'user123': {
#         'username': 'BudgetBoss',
#         'level': 5,
#         'xp': 780,
#         'net_worth': 45000,
#         'budget_limit': {'food': 8000, 'entertainment': 3000, 'savings': 5000},
#         'spending_log': []
#     }
# }

# # ----------------- FIREBASE FUNCTIONS -----------------

# def get_user_data(user_id):
#     """Fetch user data from Firestore or fallback to memory."""
#     if db:  # If Firebase is working
#         try:
#             doc_ref = db.collection('users').document(user_id)
#             doc = doc_ref.get()
#             if doc.exists:
#                 return doc.to_dict()
#             else:
#                 # Create default user entry if not exists
#                 default_data = {
#                     'username': 'BudgetBoss',
#                     'level': 5,
#                     'xp': 780,
#                     'net_worth': 45000,
#                     'budget_limit': {'food': 8000, 'entertainment': 3000, 'savings': 5000},
#                     'spending_log': []
#                 }
#                 doc_ref.set(default_data)
#                 return default_data
#         except Exception as e:
#             print(f"⚠️  Firestore error, falling back to memory: {e}")
    
#     # Fallback to in-memory storage
#     if user_id in user_data:
#         return user_data[user_id]
#     else:
#         # Create default user entry if not exists
#         default_data = {
#             'username': 'BudgetBoss',
#             'level': 5,
#             'xp': 780,
#             'net_worth': 45000,
#             'budget_limit': {'food': 8000, 'entertainment': 3000, 'savings': 5000},
#             'spending_log': []
#         }
#         user_data[user_id] = default_data
#         return default_data


# def update_user_data(user_id, data):
#     """Update user data in Firestore or memory."""
#     if db:  # If Firebase is working
#         try:
#             db.collection('users').document(user_id).update(data)
#             return True
#         except Exception as e:
#             print(f"⚠️  Firestore update error: {e}")
#             return False
    
#     # Fallback to in-memory storage
#     if user_id in user_data:
#         user_data[user_id].update(data)
#     else:
#         user_data[user_id] = data
#     return True


# def calculate_current_spending(user):
#     """Calculate total spending for all categories."""
#     log = user['spending_log']
    
#     categories = {}
#     for item in log:
#         category = item['category']
#         if category not in categories:
#             categories[category] = 0
#         categories[category] += item['amount']
    
#     return categories


# def check_for_ai_nudge(user):
#     """Check spending against budget limits and provide nudges."""
#     spending = calculate_current_spending(user)
#     budget_limit = user['budget_limit']
    
#     nudges = []
    
#     for category, limit in budget_limit.items():
#         current_spending = spending.get(category, 0)
        
#         if current_spending > limit * 0.80:
#             nudges.append({
#                 'message': f"🚨 High Alert! You've spent ₹{current_spending} on {category}, "
#                           f"which is over 80% of your ₹{limit} limit!",
#                 'type': 'danger'
#             })
#         elif current_spending > limit * 0.50:
#             nudges.append({
#                 'message': f"⚠️  Warning! You've spent ₹{current_spending} on {category}, "
#                           f"which is over 50% of your ₹{limit} limit.",
#                 'type': 'warning'
#             })
    
#     # Check savings specifically
#     savings_ratio = user.get('net_worth', 0) / 45000  # Assuming 45000 is starting net worth
#     if savings_ratio < 0.8:
#         nudges.append({
#             'message': f"💰 Savings Tip: Your net worth is down {100 - (savings_ratio * 100):.0f}%. "
#                       f"Consider reducing discretionary spending this week.",
#             'type': 'info'
#         })
    
#     return nudges if nudges else None


# def update_xp(user, amount):
#     """Update user XP and check for level up."""
#     user['xp'] += amount
#     level_updated = False
#     if user['xp'] >= 1000:
#         user['level'] += 1
#         user['xp'] = 0
#         level_updated = True
#     return level_updated


# def add_reward_for_achievement(user, achievement):
#     """Add rewards for completing achievements."""
#     rewards = {
#         'first_expense': 100,
#         'weekly_budget_met': 200,
#         'savings_milestone': 300
#     }
    
#     if achievement in rewards:
#         user['xp'] += rewards[achievement]
#         return rewards[achievement]
#     return 0

# # ----------------- ROUTES -----------------

# @app.route('/')
# def index():
#     """Serves the main SPA shell."""
#     return render_template('index.html')


# @app.route('/dashboard')
# def dashboard():
#     user = get_user_data(USER_ID)
#     spending = calculate_current_spending(user)
    
#     # Calculate progress percentages
#     progress = {}
#     for category, limit in user['budget_limit'].items():
#         current = spending.get(category, 0)
#         progress[category] = (current / limit) * 100 if limit > 0 else 0
    
#     nudge = check_for_ai_nudge(user)
    
#     # Get recent transactions (last 5)
#     recent_transactions = user['spending_log'][-5:] if user['spending_log'] else []

#     return render_template("dashboard.html",
#                            username=user['username'],
#                            level=user['level'],
#                            xp=user['xp'],
#                            net_worth=user['net_worth'],
#                            nudge=nudge,
#                            progress=progress,
#                            budget_limit=user['budget_limit'],
#                            spending=spending,
#                            recent_transactions=recent_transactions)


# @app.route('/log_expense', methods=['GET', 'POST'])
# def log_expense():
#     if request.method == 'POST':
#         category = request.form.get('category')
#         amount = int(request.form.get('amount'))
#         description = request.form.get('description', '')

#         user = get_user_data(USER_ID)

#         new_entry = {
#             'category': category,
#             'amount': amount,
#             'description': description,
#             'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }

#         updated_log = user['spending_log'] + [new_entry]
#         new_networth = user['net_worth'] - amount

#         level_updated = update_xp(user, 50)
        
#         # Check for achievements
#         if len(user['spending_log']) == 0:
#             add_reward_for_achievement(user, 'first_expense')

#         update_user_data(USER_ID, {
#             'spending_log': updated_log,
#             'net_worth': new_networth,
#             'xp': user['xp'],
#             'level': user['level']
#         })

#         return redirect(url_for('dashboard'))

#     return render_template('log_expense.html')


# # ----------------- API ROUTES -----------------

# @app.route('/api/config/firebase')
# def get_firebase_config():
#     """Returns Firebase Client configuration safely."""
#     return jsonify(firebase_client_config)


# @app.route('/api/coach/chat', methods=['POST'])
# def chat_with_coach():
#     """AI Chat Endpoint with Gemini."""
#     data = request.json
#     user_msg = data.get('message', '')
#     mode = data.get('mode', 'quick')
    
#     if GEMINI_API_KEY:
#         try:
#             model = genai.GenerativeModel('gemini-pro')
            
#             # Get user context for personalized responses
#             user = get_user_data(USER_ID)
#             spending = calculate_current_spending(user)
            
#             prompt = f"""
#             You are FinSenseAI, a helpful financial coach. 
#             User Profile: Level {user['level']}, XP: {user['xp']}, Net Worth: ₹{user['net_worth']}
#             Current Spending: {spending}
#             Budget Limits: {user['budget_limit']}
            
#             Mode: {mode}
#             User Query: {user_msg}
            
#             Provide a concise, actionable response that considers the user's financial situation.
#             """
            
#             response = model.generate_content(prompt).text
#             return jsonify({'response': response})
#         except Exception as e:
#             print(f"Gemini Error: {e}")
#             # Fallback to mock response
    
#     # Mock Responses based on user context
#     time.sleep(0.5)
#     user = get_user_data(USER_ID)
    
#     if "budget" in user_msg.lower():
#         response = f"Based on your current spending, you have ₹{user['net_worth']} left this month. Try the 50/30/20 rule: 50% Needs, 30% Wants, 20% Savings."
#     elif "save" in user_msg.lower() or "investment" in user_msg.lower():
#         response = f"Great question! As a Level {user['level']} user, consider starting with a SIP of ₹{int(user['net_worth'] * 0.1)} per month for compound growth."
#     else:
#         response = f"I see you're asking about '{user_msg}'. As your AI coach at Level {user['level']}, I recommend checking your spending dashboard for insights."
        
#     return jsonify({'response': response})


# @app.route('/api/academy/quiz', methods=['GET'])
# def get_quiz():
#     """Dynamic Quiz Generation using Gemini."""
#     track = request.args.get('track', 'general')
    
#     if GEMINI_API_KEY:
#         try:
#             model = genai.GenerativeModel('gemini-pro')
#             prompt = f"""
#             Generate 5 multiple-choice questions about '{track}' in finance for a beginner.
#             Return ONLY valid JSON in this format:
#             {{
#                 "questions": [
#                     {{
#                         "id": 1,
#                         "question": "Question text",
#                         "options": ["Option A", "Option B", "Option C", "Option D"],
#                         "correct": 0,
#                         "explanation": "Brief explanation of the correct answer"
#                     }}
#                 ]
#             }}
#             The 'correct' field should be the index (0-3) of the correct option.
#             Include an 'explanation' field for each question.
#             """
#             response = model.generate_content(prompt).text
#             # Clean up markdown code blocks if present
#             cleaned_response = response.replace('```json', '').replace('```', '').strip()
#             return jsonify(json.loads(cleaned_response))
#         except Exception as e:
#             print(f"Gemini Quiz Error: {e}")
#             # Fallback to mock
#             pass

#     # Fallback Mock Questions with explanations
#     questions = [
#         {
#             "id": 1,
#             "question": "What is the 50/30/20 rule of budgeting?",
#             "options": ["50% Needs, 30% Wants, 20% Savings", "50% Savings, 30% Needs, 20% Wants", "50% Wants, 30% Savings, 20% Needs", "None of the above"],
#             "correct": 0,
#             "explanation": "The 50/30/20 rule helps allocate income: 50% for needs, 30% for wants, and 20% for savings."
#         },
#         {
#             "id": 2,
#             "question": "Which factor has the highest impact on your credit score?",
#             "options": ["Credit Mix", "New Credit", "Payment History", "Length of Credit History"],
#             "correct": 2,
#             "explanation": "Payment history (35%) has the biggest impact, as it shows if you pay bills on time."
#         }
#     ]
#     return jsonify({'questions': questions})


# @app.route('/api/user/data', methods=['GET'])
# def get_user_api():
#     """API endpoint to get user data for SPA."""
#     user = get_user_data(USER_ID)
#     spending = calculate_current_spending(user)
    
#     # Calculate progress for all categories
#     progress = {}
#     for category, limit in user['budget_limit'].items():
#         current = spending.get(category, 0)
#         progress[category] = (current / limit) * 100 if limit > 0 else 0
    
#     nudge = check_for_ai_nudge(user)
    
#     return jsonify({
#         'username': user['username'],
#         'level': user['level'],
#         'xp': user['xp'],
#         'net_worth': user['net_worth'],
#         'budget_limit': user['budget_limit'],
#         'spending_log': user['spending_log'][-10:],  # Last 10 transactions
#         'progress': progress,
#         'spending': spending,
#         'nudge': nudge,
#         'firebase_connected': db is not None
#     })


# @app.route('/api/log/expense', methods=['POST'])
# def log_expense_api():
#     """API endpoint to log expenses from SPA."""
#     try:
#         data = request.json
#         category = data.get('category')
#         amount = float(data.get('amount'))
#         description = data.get('description', '')

#         user = get_user_data(USER_ID)

#         new_entry = {
#             'category': category,
#             'amount': amount,
#             'description': description,
#             'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }

#         updated_log = user['spending_log'] + [new_entry]
#         new_networth = user['net_worth'] - amount

#         level_updated = update_xp(user, 50)

#         update_user_data(USER_ID, {
#             'spending_log': updated_log,
#             'net_worth': new_networth,
#             'xp': user['xp'],
#             'level': user['level']
#         })

#         return jsonify({
#             'status': 'success',
#             'message': 'Expense logged successfully',
#             'level_updated': level_updated,
#             'new_networth': new_networth,
#             'xp_gained': 50
#         })
#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': f'Failed to log expense: {str(e)}'
#         }), 400


# @app.route('/api/achievements', methods=['GET'])
# def get_achievements():
#     """Get user achievements."""
#     user = get_user_data(USER_ID)
    
#     achievements = []
    
#     # Check for achievements
#     if len(user['spending_log']) > 0:
#         achievements.append({
#             'name': 'First Step',
#             'description': 'Logged your first expense',
#             'icon': '💰',
#             'unlocked': True
#         })
    
#     if user['level'] >= 3:
#         achievements.append({
#             'name': 'Budget Master',
#             'description': 'Reached Level 3',
#             'icon': '🏆',
#             'unlocked': True
#         })
    
#     # More achievements based on spending habits
#     spending = calculate_current_spending(user)
#     if spending.get('savings', 0) > 1000:
#         achievements.append({
#             'name': 'Savings Starter',
#             'description': 'Saved over ₹1000',
#             'icon': '💎',
#             'unlocked': True
#         })
    
#     return jsonify({'achievements': achievements})


# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """Health check endpoint."""
#     return jsonify({
#         'status': 'healthy',
#         'firebase': 'connected' if db else 'disconnected',
#         'gemini': 'configured' if GEMINI_API_KEY else 'not_configured',
#         'timestamp': datetime.now().isoformat()
#     })


# @app.route('/api/mail/welcome', methods=['POST'])
# def send_welcome():
#     """Mock Welcome Email."""
#     return jsonify({'status': 'sent', 'message': 'Welcome email queued.'})


# # Error handlers
# @app.errorhandler(404)
# def not_found(e):
#     return jsonify({'error': 'Not found'}), 404


# @app.errorhandler(500)
# def server_error(e):
#     return jsonify({'error': 'Internal server error'}), 500


# # Run app
# if __name__ == '__main__':
#     print("=" * 50)
#     print("🚀 FinSenseAI Flask Backend")
#     print("=" * 50)
#     print(f"📁 Project root: {os.getcwd()}")
#     print(f"🔑 Firebase Admin: {'✅ Connected' if db else '❌ Disconnected'}")
#     print(f"🤖 Gemini AI: {'✅ Configured' if GEMINI_API_KEY else '⚠️ Not configured'}")
#     print(f"🌐 Server URL: http://localhost:5000")
#     print("=" * 50)
    
#     app.run(debug=True, port=5000, host='0.0.0.0')
















# from flask import Flask, render_template, request, redirect, url_for, jsonify
# from datetime import datetime
# import firebase_admin
# from firebase_admin import credentials, firestore

# # --- Flask App Config ---
# app = Flask(_name_)
# app.config['SECRET_KEY'] = 'your_hackathon_secret_key'

# # --- Initialize Firebase Admin ---
# cred = credentials.Certificate("finsenseai-834cf-firebase-adminsdk-fbsvc-e8ef115421.json")
# firebase_admin.initialize_app(cred)

# db = firestore.client()  # Firestore reference

# # Temporary DEFAULT user ID for demo
# USER_ID = "user123"


# # ----------------- FIREBASE FUNCTIONS -----------------

# def get_user_data(user_id):
#     """Fetch user document from Firestore."""
#     doc_ref = db.collection('users').document(user_id)
#     doc = doc_ref.get()
#     if doc.exists:
#         return doc.to_dict()
#     else:
#         # Create default user entry if not exists
#         default_data = {
#             'username': 'BudgetBoss',
#             'level': 5,
#             'xp': 780,
#             'net_worth': 45000,
#             'budget_limit': {'food': 8000, 'entertainment': 3000, 'savings': 5000},
#             'spending_log': []
#         }
#         doc_ref.set(default_data)
#         return default_data


# def update_user_data(user_id, data):
#     """Update user data in Firestore."""
#     db.collection('users').document(user_id).update(data)


# def calculate_current_spending(user):
#     """Calculate total spending for food category."""
#     log = user['spending_log']
#     current_food_spending = sum(item['amount'] for item in log if item['category'] == 'food')
#     return {'food': current_food_spending}


# def check_for_ai_nudge(user):
#     spending = calculate_current_spending(user)
#     limit = user['budget_limit']['food']

#     if spending['food'] > limit * 0.50:
#         return {
#             'message': f"⚠ Nudge! You've spent ₹{spending['food']} on food, "
#                        f"which is halfway to your ₹{limit} limit! Try the 'Cook at Home' challenge this week.",
#             'type': 'warning'
#         }
#     return None


# def update_xp(user, amount):
#     user['xp'] += amount
#     level_updated = False
#     if user['xp'] >= 1000:
#         user['level'] += 1
#         user['xp'] = 0
#         level_updated = True
#     return level_updated


# # ----------------- ROUTES -----------------

# @app.route('/')
# def dashboard():
#     user = get_user_data(USER_ID)

#     spending = calculate_current_spending(user)
#     food_progress = (spending['food'] / user['budget_limit']['food']) * 100

#     nudge = check_for_ai_nudge(user)

#     return render_template("dashboard.html",
#                            username=user['username'],
#                            level=user['level'],
#                            xp=user['xp'],
#                            net_worth=user['net_worth'],
#                            nudge=nudge,
#                            food_progress=food_progress,
#                            budget_limit=user['budget_limit'])


# @app.route('/log_expense', methods=['GET', 'POST'])
# def log_expense():
#     if request.method == 'POST':
#         category = request.form.get('category')
#         amount = int(request.form.get('amount'))

#         user = get_user_data(USER_ID)

#         new_entry = {
#             'category': category,
#             'amount': amount,
#             'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }

#         updated_log = user['spending_log'] + [new_entry]
#         new_networth = user['net_worth'] - amount

#         update_xp(user, 50)

#         update_user_data(USER_ID, {
#             'spending_log': updated_log,
#             'net_worth': new_networth,
#             'xp': user['xp'],
#             'level': user['level']
#         })

#         return redirect(url_for('dashboard'))

#     return render_template('log_expense.html')


# @app.route('/ai_chat', methods=['POST'])
# def ai_chat():
#     user_query = request.json.get('query')
#     user = get_user_data(USER_ID)

#     ai_response = (f"Great question about '{user_query}'! Since you're Level {user['level']}, "
#                    f"you should focus on Savings and Compound Growth strategies now. (Demo Response)")

#     return jsonify({'response': ai_response})


# # Run app
# if _name_ == '_main_':
#     app.run(debug=True)


