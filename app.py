from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from google import genai  # Modern library
import os
from dotenv import load_dotenv

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

load_dotenv()

# --- NEW AI CONFIGURATION ---
# Initialize the client (This replaces genai.configure)
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1'} 
)
MODEL_ID = "gemini-2.5-flash"

# Load the pre-calculated data
try:
    with open('model.pkl', 'rb') as f:
        data = pickle.load(f)
        df = data['df']
        cosine_sim = data['cosine_sim']
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['content'].fillna(''))
    print("System Online: Model and TF-IDF Matrix loaded.")
except FileNotFoundError:
    print("Error: model.pkl not found. Run train_model.py first!")

def get_ai_advice(user_query, retrieved_courses):
    try:
        if not retrieved_courses:
            return "No data paths found to analyze."

        context = ""
        for c in retrieved_courses:
            context += f"Course: {c['name']} by {c['univ']}. Level: {c['diff']}.\n"

        prompt = f"""
        You are a Cyber-Advisor. User query: "{user_query}"
        Analyze these options:
        {context}
        Pick the best one and explain why in 2 short, punchy sentences. 
        Use a futuristic, helpful tone.
        """
        
        # NEW SYNTAX: Use client.models.generate_content
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"AI error log: {e}")
        return retrieved_courses[0]['reason'] if retrieved_courses else "Neural link unstable."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.form.get('user_id', '').lower().strip()
        if not user_input:
            return jsonify({"recs": []})

        all_courses = df['Course Name Lower'].tolist()
        closest_match = difflib.get_close_matches(user_input, all_courses, n=1, cutoff=0.7)

        if closest_match:
            idx = df[df['Course Name Lower'] == closest_match[0]].index[0]
            sim_scores = list(enumerate(cosine_sim[idx]))
            target_name = closest_match[0]
        else:
            query_vector = tfidf.transform([user_input])
            query_sim = cosine_similarity(query_vector, tfidf_matrix).flatten()
            sim_scores = list(enumerate(query_sim))
            target_name = user_input

        start_idx = 1 if closest_match else 0
        sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[start_idx:11]
        
        k = len(sorted_scores)
        relevant_items = [s for _, s in sorted_scores if s > 0.4]
        precision = len(relevant_items) / k if k > 0 else 0
        recall = len(relevant_items) / 50 

        recs_list = []
        pattern_data = []

        for i, score in sorted_scores:
            row = df.iloc[i]
            reason = f"High match for '{target_name}'" if score > 0.6 else f"Related to '{target_name}'"
            
            recs_list.append({
                "name": str(row['Course Name']),
                "univ": str(row['University']),
                "diff": str(row['Difficulty Level']),
                "rate": str(row['Course Rating']),
                "url": str(row['Course URL']),
                "reason": reason
            })
            pattern_data.append(round(float(score), 2))

        ai_commentary = get_ai_advice(user_input, recs_list[:3])

        return jsonify({
            "recs": recs_list,
            "metrics": {
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "k": k
            },
            "pattern_data": pattern_data,
            "ai_advice": ai_commentary
        })

    except Exception as e:
        print(f"Backend Error: {e}")
        return jsonify({"error": str(e)}), 500

# --- UPDATED DEBUG SECTION ---
try:
    # Adding a small timeout to ensure it doesn't hang
    debug_response = client.models.generate_content(
        model=MODEL_ID, 
        contents="Hi im Walter White"
    )
    print(f"AI Debug Check: {debug_response.text}")
except Exception as e:
    print(f"AI Debug Connection Failed: {e}")


if __name__ == '__main__':
    app.run(debug=True)