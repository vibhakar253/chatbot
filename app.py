import os
from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

uri = "mongodb+srv://aksvibhakar:vibhakaraks@chatbotcluster.v1hibdg.mongodb.net/?retryWrites=true&w=majority&appName=chatbotcluster"

# Connecting to MongoDb
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['chatbotdatabase']
collection = db['chatbotcollection']

# storing in MongoDb
session_data = {}

def store_temp_data(session_id, key, value):
    if session_id not in session_data:
        session_data[session_id] = {}
    session_data[session_id][key] = value

def retrieve_temp_data(session_id, key):
    return session_data.get(session_id, {}).get(key, None)

#connecting to Dialogflow webhook

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

#Pushing email and password into MongoDb

def store_user_details(email, password):
    collection.insert_one({'email': email, 'password': password})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
