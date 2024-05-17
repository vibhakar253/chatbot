from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize SQLite Database
def init_sqlite_db():
    conn = sqlite3.connect('users.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS users (email TEXT, password TEXT)')
    print("Table created successfully")
    conn.close()

init_sqlite_db()

# Temporary storage for session data (use a more robust solution for production)
session_data = {}

def store_temp_data(session_id, key, value):
    if session_id not in session_data:
        session_data[session_id] = {}
    session_data[session_id][key] = value

def retrieve_temp_data(session_id, key):
    return session_data.get(session_id, {}).get(key, None)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    intent = req.get('queryResult').get('intent').get('displayName')
    parameters = req.get('queryResult').get('parameters')
    session_id = req.get('session')  # Use session ID to keep track of conversations

    print(intent)
    if intent == 'Login_intent':
        return jsonify({"fulfillmentText": "Enter your email"})
    if intent == 'Login_intent - email':
        email = parameters.get('email')
        store_temp_data(session_id, 'email', email)
        return jsonify({"fulfillmentText": "Enter your password"})
    if intent == 'Login_intent - email - password':
        password = parameters.get('password')
        email = retrieve_temp_data(session_id, 'email')
        store_user_details(email, password)
        return jsonify({"fulfillmentText": "Your account has been registered."})
    else:
        return jsonify({"fulfillmentText": "I don't understand. Please try again."})

def store_user_details(email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
