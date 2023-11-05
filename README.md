Drug Interaction and Administration API
This API is designed to provide detailed information about drugs, verify drug interactions, administer drugs based on the frequency, and speak drug administration instructions. The data is based on a JSON file named data.json.

Features
Drug Retrieval: Get detailed information about a specific drug.
Drug Administration: Record the administration of a drug, ensuring it is not given too frequently.
Administration History: View a history of all drugs that have been administered.
Allergy Check: Check if a drug is on the allergy list.
Getting Started
Clone the repository:

bash
Copy code
git clone <repository_url>
cd <repository_folder_name>
Install the required packages:

You need to have Flask, json, and requests installed. If you don't have them, you can install via pip:

bash
Copy code
pip install Flask requests
Run the application:

bash
Copy code
python <filename>.py
Endpoints
/drugs/<id>: Retrieve information about a specific drug by its ID.

/administer/<id>: Administer a drug by its ID and store the administration time.

/history: Retrieve a list of drugs that have been administered, along with their times.

/allergies: Check if a drug is on the allergy list.
