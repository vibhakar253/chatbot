import os
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Initialize MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['chatbotdatabase']  # This will be created if it doesn't exist
collection = db['chatbotcollection']  # This will be created if it doesn't exist

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
    session_id = req.get('session')

    if intent == 'Login_intent':
        return jsonify({"fulfillmentText": "Enter your email"})

    elif intent == 'Login_intent - email':
        email = parameters.get('email')
        if email:
            store_temp_data(session_id, 'email', email)
            return jsonify({"fulfillmentText": "Enter your password"})
        else:
            return jsonify({"fulfillmentText": "Please provide a valid email."})

    elif intent == 'Login_intent - email - password':
        password = parameters.get('password')
        email = retrieve_temp_data(session_id, 'email')
        if email and password:
            store_user_details(email, password)
            return jsonify({"fulfillmentText": "Your account has been registered."})
        else:
            return jsonify({"fulfillmentText": "Something went wrong. Please start over."})
    else:
        return jsonify({"fulfillmentText": "I don't understand. Please try again."})

def store_user_details(email, password):
    collection.insert_one({'email': email, 'password': password})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
