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
allergies = ["44729-4274-34"]

# Utility function to save data back to the JSON file
def save_to_json(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

# Route to retrieve drug details using its ID
@app.route('/drugs/<id>')
def get_drug(id):
    drug = data["Drugs"].get(id)
    
    if not drug:
        return jsonify({"error": "Drug not found"}), 404

    # Check for allergies and interactions
    if id in allergies or any(drug_id in data["drug-interactions"].get(id, []) for drug_id in data.get("drugs-administered", {})):
        drug["confirmation"] = False
    else:
        drug["confirmation"] = True

    return jsonify(drug), 200

# Route to administer a drug and record its administration time
@app.route('/administer/<id>')
def take_drug(id):
    drug_info = data["Drugs"].get(id)
    
    if not drug_info:
        return "Error: Drug not found", 404

    # Ensure drug is intended for the right patient
    if drug_info["patient"] != "Vye Russ":
        return f"Error: Drug not intended for Vye Russ, got {drug_info['patient']}", 400

    # Calculate time constraints based on drug frequency
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d-%H:%M:%S')
    dateJson = data["drugs-administered"].get(id, {}).get("time", [""])[-1] 
    last_admin_time = None
    if dateJson:
        last_admin_time = datetime.strptime(dateJson, '%Y-%m-%d-%H:%M:%S')
    
    # Ensure drug is not administered too frequently
    if last_admin_time and now - last_admin_time < timedelta(hours=24/int(drug_info["freq1"])):
        return f"Error: Previously taken {drug_info['rxName']} within {24/int(drug_info['freq1'])} hours at {last_admin_time}", 400
    
    # Record the drug administration time
    data["drugs-administered"].setdefault(id, {"name": drug_info["rxName"], "time": []})["time"].append(formatted_time)
    save_to_json(data)

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

    # Note: Ensure to implement the call to the Eleven Labs API and handle its response

# Route to check allergies
@app.route('/allergies')
def get_allergies():
    allName = [data["Drugs"][x]["rxName"] for x in allergies if data["Drugs"].get(x)]
    return jsonify(allName)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
