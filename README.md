🤖 AI Course Recommender (Cyber-Advisor)
A machine learning-powered course recommendation system built with Flask, Scikit-Learn, and Google Gemini 2.5 Flash. This project uses RAG (Retrieval-Augmented Generation) to suggest courses based on user queries and provide AI-generated advice.

🛠 Setup Instructions for Collaborators
1. Prerequisites
Python 3.9 or higher

A Google Gemini API Key from Google AI Studio.

2. Clone & Environment Setup
Bash

# Clone the project
git clone <your-repository-url>
cd ML_Project

# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
3. Install Modern Dependencies
We have migrated to the latest google-genai SDK to avoid deprecation errors and 404 model issues.

Bash

pip install flask pandas scikit-learn numpy google-genai python-dotenv
4. Configuration (.env)
Create a .env file in the root directory. This file is ignored by Git for security.

Code snippet

GEMINI_API_KEY=your_actual_api_key_here
5. Initialize the Model
The recommender depends on a pre-calculated similarity matrix. You must run this script once to generate model.pkl:

Bash

python train_model.py
6. Launch the App
Bash

python app.py
Visit http://127.0.0.1:5000 in your browser.

🏗 Project Architecture
app.py: The Flask server handling routing and the Gemini 2.5 API connection.

train_model.py: Processes the dataset using TF-IDF and saves the model to a pickle file.

frontend/: Contains the static/ (CSS/JS) and templates/ (HTML) files.

⚠️ Critical Notes
AI Model: We use gemini-2.5-flash. Do not switch back to 1.5-flash in the code, as the older API endpoints may return 404 NOT_FOUND.

API Library: We use from google import genai. Do not use import google.generativeai as it is now deprecated.

Styling: The UI uses WebKit-specific CSS for scrollbars and text effects; ensure you test in Chrome, Edge, or Safari.