from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

# --- Configuration and Initialization ---
app = Flask(__name__)
# In a real project, this would be a secure, secret key
app.config['SECRET_KEY'] = 'your_hackathon_secret_key'

# --- Placeholder for User State/Database ---
# In a hackathon, you might start with a simple Python dictionary
# instead of a full database for rapid prototyping.
# Key: User ID (or session ID), Value: User Data
user_data = {
    'user123': {
        'username': 'BudgetBoss',
        'level': 5,
        'xp': 780,
        'net_worth': 45000,  # Virtual currency
        'budget_limit': {'food': 8000, 'entertainment': 3000, 'savings': 5000},
        'spending_log': [
            {'category': 'food', 'amount': 1200, 'date': datetime(2025, 12, 1)},
            {'category': 'entertainment', 'amount': 500, 'date': datetime(2025, 12, 3)},
        ]
    }
}


# --- AI and Game Logic Functions (PLACEHOLDERS) ---

def calculate_current_spending(user_id):
    """Calculates total spending in the current virtual month."""
    log = user_data[user_id]['spending_log']
    # Simplified calculation for the hackathon MVP
    current_food_spending = sum(item['amount'] for item in log if item['category'] == 'food')
    return {'food': current_food_spending}


def check_for_ai_nudge(user_id):
    """Determines if the AI needs to intervene based on spending patterns."""
    spending = calculate_current_spending(user_id)
    limit = user_data[user_id]['budget_limit']['food']

    # Example Logic: If food spending exceeds 50% of the limit early in the month
    # For demo purposes, let's relax the condition or ensure it triggers if we want to see it.
    # But sticking to user logic:
    if spending['food'] > limit * 0.50: # Removed date check for easier demo
        # --- PLACEHOLDER for LLM API CALL (e.g., Gemini API) ---
        # In the final version, this is where you'd call the Gemini API
        # with a prompt like: "The user is 50% over their food budget early. Give a friendly tip."

        return {
            'message': f"⚠ *Nudge!* You've spent ₹{spending['food']} on food, which is halfway to your ₹{limit} limit! Try the 'Cook at Home' virtual challenge this week.",
            'type': 'warning'
        }
    return None


def update_xp(user_id, amount):
    """Updates user XP and checks for level up (placeholder)."""
    user_data[user_id]['xp'] += amount
    # Simplified Level Up Check
    if user_data[user_id]['xp'] >= 1000:
        user_data[user_id]['level'] += 1
        user_data[user_id]['xp'] = 0  # Reset XP
        return True
    return False


# --- Flask Routes ---

@app.route('/')
def dashboard():
    """Renders the main game dashboard."""
    user_id = 'user123'  # Placeholder for session management
    user = user_data[user_id]

    # Run the AI logic to check for a nudge
    nudge = check_for_ai_nudge(user_id)

    # Calculate current budget progress for display
    current_spending = calculate_current_spending(user_id)
    food_progress = (current_spending['food'] / user['budget_limit']['food']) * 100

    return render_template('dashboard.html',
                           username=user['username'],
                           level=user['level'],
                           xp=user['xp'],
                           net_worth=user['net_worth'],
                           nudge=nudge,
                           food_progress=food_progress,
                           budget_limit=user['budget_limit'])


@app.route('/log_expense', methods=['GET', 'POST'])
def log_expense():
    """Allows user to log a new virtual expense."""
    if request.method == 'POST':
        user_id = 'user123'
        category = request.form.get('category')
        amount = int(request.form.get('amount'))

        # 1. Update User State
        user_data[user_id]['spending_log'].append({
            'category': category,
            'amount': amount,
            'date': datetime.now()
        })
        user_data[user_id]['net_worth'] -= amount

        # 2. Award XP (Gamification)
        update_xp(user_id, 50)  # Award 50 XP for logging an expense

        # 3. Redirect back to dashboard to see results
        return redirect(url_for('dashboard'))

    # GET request shows the log expense form
    return render_template('log_expense.html')


@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    """Placeholder for the direct chat interaction with the AI Mentor."""
    # Handle JSON or Form data
    if request.is_json:
        user_query = request.json.get('query')
    else:
        user_query = request.form.get('query')
        
    user_id = 'user123'

    # --- PLACEHOLDER for LLM API CALL ---
    # In a real implementation, you would:
    # 1. Inject user_data[user_id] into the prompt.
    # 2. Send the full prompt and user_query to the Gemini API.
    # 3. Get the structured response.

    ai_response = f"Thank you for asking about '{user_query}'! Based on your *Level {user_data[user_id]['level']}*, focus on **Compounding Interest** lessons now. (Placeholder response)"

    # Return JSON for JS fetch calls
    return jsonify({'response': ai_response})


# --- Run the Application ---
if __name__ == '__main__':
    # Set debug=True for development to auto-reload
    app.run(debug=True)