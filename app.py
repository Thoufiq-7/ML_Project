from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

# Load the pre-calculated data
try:
    with open('model.pkl', 'rb') as f:
        data = pickle.load(f)
        df = data['df']
        cosine_sim = data['cosine_sim']
except FileNotFoundError:
    print("Error: model.pkl not found. Run train_model.py first!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.form.get('user_id', '').lower().strip()
        if not user_input:
            return jsonify({"recs": []})

        # --- LOGIC SELECTION ---
        all_courses = df['Course Name Lower'].tolist()
        closest_match = difflib.get_close_matches(user_input, all_courses, n=1, cutoff=0.7)

        if closest_match:
            # Recommender Mode: Finding similar to a specific course
            idx = df[df['Course Name Lower'] == closest_match[0]].index[0]
            sim_scores = list(enumerate(cosine_sim[idx]))
            target_name = closest_match[0]
        else:
            # Search Mode: Finding courses matching a topic
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['content'])
            query_vector = tfidf.transform([user_input])
            query_sim = cosine_similarity(query_vector, tfidf_matrix).flatten()
            sim_scores = list(enumerate(query_sim))
            target_name = user_input

        # Sort top 10 (exclude the first one if it's an exact course match)
        start_idx = 1 if closest_match else 0
        sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[start_idx:11]
        
        # --- FEATURE 1: EVALUATION METRICS (Precision@K) ---
        # We define "Relevant" as a similarity score > 0.4
        k = len(sorted_scores)
        relevant_items = [s for _, s in sorted_scores if s > 0.4]
        precision = len(relevant_items) / k if k > 0 else 0
        recall = len(relevant_items) / 50 # Assuming a target set of 50 relevant items in dataset

        recs_list = []
        pattern_data = []

        for i, score in sorted_scores:
            row = df.iloc[i]
            
            # --- FEATURE 2: EXPLAINABILITY ---
            # Dynamic reasoning based on the similarity score
            reason = f"Highly relevant to your interest in '{target_name}'" if score > 0.6 else f"Broadly matches skills related to '{target_name}'"
            
            recs_list.append({
                "name": str(row['Course Name']),
                "univ": str(row['University']),
                "diff": str(row['Difficulty Level']),
                "rate": str(row['Course Rating']),
                "url": str(row['Course URL']),
                "reason": reason
            })
            
            # --- FEATURE 3: VISUALIZATION DATA ---
            # Sending raw scores to plot the 'Learning Pattern' curve
            pattern_data.append(round(float(score), 2))
        
        return jsonify({
            "recs": recs_list,
            "metrics": {
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "k": k
            },
            "pattern_data": pattern_data
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)