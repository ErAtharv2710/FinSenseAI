from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --- Flask App Config ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_hackathon_secret_key'

# --- Initialize Firebase Admin ---
cred = credentials.Certificate("finsenseai-834cf-firebase-adminsdk-fbsvc-e8ef115421.json")
firebase_admin.initialize_app(cred)

db = firestore.client()  # Firestore reference

# Temporary DEFAULT user ID for demo
USER_ID = "user123"


# ----------------- FIREBASE FUNCTIONS -----------------

def get_user_data(user_id):
    """Fetch user document from Firestore."""
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        # Create default user entry if not exists
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


def update_user_data(user_id, data):
    """Update user data in Firestore."""
    db.collection('users').document(user_id).update(data)


def calculate_current_spending(user):
    """Calculate total spending for food category."""
    log = user['spending_log']
    current_food_spending = sum(item['amount'] for item in log if item['category'] == 'food')
    return {'food': current_food_spending}


def check_for_ai_nudge(user):
    spending = calculate_current_spending(user)
    limit = user['budget_limit']['food']

    if spending['food'] > limit * 0.50:
        return {
            'message': f"⚠ *Nudge!* You've spent ₹{spending['food']} on food, "
                       f"which is halfway to your ₹{limit} limit! Try the 'Cook at Home' challenge this week.",
            'type': 'warning'
        }
    return None


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
    food_progress = (spending['food'] / user['budget_limit']['food']) * 100

    nudge = check_for_ai_nudge(user)

    return render_template("dashboard.html",
                           username=user['username'],
                           level=user['level'],
                           xp=user['xp'],
                           net_worth=user['net_worth'],
                           nudge=nudge,
                           food_progress=food_progress,
                           budget_limit=user['budget_limit'])


@app.route('/log_expense', methods=['GET', 'POST'])
def log_expense():
    if request.method == 'POST':
        category = request.form.get('category')
        amount = int(request.form.get('amount'))

        user = get_user_data(USER_ID)

        new_entry = {
            'category': category,
            'amount': amount,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        updated_log = user['spending_log'] + [new_entry]
        new_networth = user['net_worth'] - amount

        update_xp(user, 50)

        update_user_data(USER_ID, {
            'spending_log': updated_log,
            'net_worth': new_networth,
            'xp': user['xp'],
            'level': user['level']
        })

        return redirect(url_for('dashboard'))

    return render_template('log_expense.html')


@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    user_query = request.json.get('query')
    user = get_user_data(USER_ID)

    ai_response = (f"Great question about '{user_query}'! Since you're Level {user['level']}, "
                   f"you should focus on Savings and Compound Growth strategies now. (Demo Response)")

    return jsonify({'response': ai_response})


# Run app
if __name__ == '__main__':
    app.run(debug=True)
