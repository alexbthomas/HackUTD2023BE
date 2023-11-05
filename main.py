import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify

# API endpoint and key for Eleven Labs' text-to-speech service
ELEVEN_API_URL = "https://api.elevenlabs.com/synthesize"
ELEVEN_API_KEY = ""

app = Flask(__name__)

# Load initial drug data from the JSON file
with open('data.json') as file:
    data = json.load(file)

# List of known allergies (represented by drug IDs)
allergies = ["3", "4", "5"]

# Route to retrieve drug details using its ID
@app.route('/drugs/<id>')
def get_drug(id):    
    drug_info = data["Drugs"].get(id)
    
    if not drug_info:
        return "Error: Drug not found", 404

    # Ensure drug is intended for the right patient
    # if drug_info["patient"] != "Vye Russ":
    #     drug_info["message"] = "This drug is not intended for you, it's for {drug_info['patient']}"
    #     drug_info["confirmation"] = False

    #     return jsonify(drug_info), 400

    # Calculate time constraints based on drug frequency
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d-%H:%M:%S')
    dateJson = data["drugs-administered"].get(id, {}).get("time", [""])[-1] 
    last_admin_time = None

    if id in allergies: 
        drug_info["message"] = f"Allergy detected, do not administer"
        drug_info["confirmation"] = False
        return jsonify(drug_info), 400

    if dateJson:
        last_admin_time = datetime.strptime(dateJson, '%Y-%m-%d-%H:%M:%S')
    
    # Ensure drug is not administered too frequently
    if last_admin_time and now - last_admin_time < timedelta(hours=24/int(drug_info["freq1"])):
        drug_info["message"] = f"Previously taken {drug_info['rxName']} within {24/int(drug_info['freq1'])} hours at {last_admin_time}"
        drug_info["confirmation"] = False
        return jsonify(drug_info), 400

    # check if complication with previously taken drug
    if data["drugs-administered"] != None: 
        for x in data["drugs-administered"]:
            if data["drug-interactions"][x] and id in data["drug-interactions"][x]:
                drug_info["message"] = f"Dangerous Drug Interaction detected for {drug_info['rxName']}"
                drug_info["confirmation"] = False
                return jsonify(drug_info), 400


    drug_info["message"] = "No allergies or dangerous interactions detected. Safe to consume."
    return jsonify(drug_info), 200


# Route to administer a drug and record its administration time
@app.route('/administer/<id>')
def take_drug(id):
    drug_info = data["Drugs"].get(id)
    
    if not drug_info:
        return "Error: Drug not found", 404
    
    if id in allergies: 
        drug_info["message"] = f"Allergy detected, do not administer"
        drug_info["confirmation"] = False
        return jsonify(drug_info), 400

    # Ensure drug is intended for the right patient
    # if drug_info["patient"] != "Vye Russ":
    #     drug_info["message"] = f"This drug is not intended for you, it's for {drug_info['patient']}"
    #     drug_info["confirmation"] = False

    #     return jsonify(drug_info), 400

    drug_check_response, status_code = get_drug(id)
    if status_code != 200:
        return drug_check_response
    # Calculate time constraints based on drug frequency
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d-%H:%M:%S')
    dateJson = data["drugs-administered"].get(id, {}).get("time", [""])[-1] 
    last_admin_time = None
    if dateJson:
        last_admin_time = datetime.strptime(dateJson, '%Y-%m-%d-%H:%M:%S')
    
    # Ensure drug is not administered too frequently
    if last_admin_time and now - last_admin_time < timedelta(hours=24/int(drug_info["freq1"])):
        drug_info["message"] = f"Previously taken {drug_info['rxName']} within {24/int(drug_info['freq1'])} hours at {last_admin_time}"
        drug_info["confirmation"] = False
        return jsonify(drug_info), 400
    
    # check if complication with previously taken drug
    if data["drugs-administered"] != None: 
        for x in data["drugs-administered"]:
            if data["drug-interactions"][x] and id in data["drug-interactions"][x]:
                drug_info["message"] = f"Dangerous Drug Interaction detected for {drug_info['rxName']}"
                drug_info["confirmation"] = False
                return jsonify(drug_info), 400
    # Record the drug administration time
    data["drugs-administered"].setdefault(id, {"name": drug_info["rxName"], "time": []})["time"].append(formatted_time)
    return jsonify(data["drugs-administered"]), 200

# Route to retrieve a list of administered drugs
@app.route('/history')
def get_administered():
    return jsonify(data["drugs-administered"]), 200

# Route to provide spoken instructions for administering a drug
@app.route('/speak_instructions/<id>')
def speak_instructions(id):
    drug = data["Drugs"].get(id)
    if not drug:
        return jsonify({"error": "Drug not found"}), 404

    headers = {
        "Authorization": f"Bearer {ELEVEN_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": drug['administerInstructions'],
        "voice": "en-US",
        "format": "mp3"
    }

# Route to check allergies
@app.route('/allergies')
def get_allergies():
    allName = [data["Drugs"][x]["rxName"] for x in allergies if data["Drugs"].get(x)]
    return jsonify(allName)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)