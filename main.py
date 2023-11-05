import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify

ELEVEN_API_URL = "https://api.elevenlabs.com/synthesize"
ELEVEN_API_KEY = "2c41c659b07dc4a1de4db7f4679798a6"

app = Flask(__name__)

with open('data.json') as file:
    data = json.load(file)

allergies = ["44729-4274-34"]

def save_to_json(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

@app.route('/drugs/<id>')
def get_drug(id):
    drug = data["Drugs"].get(id)
    
    if not drug:
        return jsonify({"error": "Drug not found"}), 404

    if id in allergies or any(drug_id in data["drug-interactions"].get(id, []) for drug_id in data.get("drugs-administered", {})):
        drug["confirmation"] = False
    else:
        drug["confirmation"] = True

    return jsonify(drug), 200

@app.route('/administer/<id>')
def take_drug(id):
    drug_info = data["Drugs"].get(id)
    
    if not drug_info:
        return "Error: Drug not found", 404

    if drug_info["patient"] != "Vye Russ":
        return f"Error: Drug not intended for Vye Russ, got {drug_info['patient']}", 400

    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d-%H:%M:%S')
    dateJson = data["drugs-administered"].get(id, {}).get("time", [""])[-1] 
    last_admin_time = None
    if dateJson != None and dateJson != "":
        last_admin_time = datetime.strptime(dateJson,'%Y-%m-%d-%H:%M:%S')
    if last_admin_time and now - last_admin_time < timedelta(hours=24/int(drug_info["freq1"])):
        return f"Error: Previously taken {drug_info['rxName']} within {24/int(drug_info['freq1'])} hours at {last_admin_time}", 400
    
    data["drugs-administered"].setdefault(id, {"name": drug_info["rxName"], "time": []})["time"].append(formatted_time)
    save_to_json(data)

    return jsonify(data["drugs-administered"]), 200

@app.route('/history')
def get_administered():
    return jsonify(data["drugs-administered"]), 200

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
        "voice": "en-US",  # Choose a suitable voice for your application
        "format": "mp3"
    }

@app.route('/allergies')
def get_allergies():
    allName = []
    for x in allergies: 
        if data["Drugs"][x]: 
            allName.append(data["Drugs"][x]["rxName"])
    return allName



if __name__ == '__main__':
    app.run(debug=True)
