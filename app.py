from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import difflib

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

        all_courses = df['Course Name Lower'].tolist()
        closest_match = difflib.get_close_matches(user_input, all_courses, n=1, cutoff=0.3)

        if not closest_match:
            return jsonify({"recs": []})

        idx = df[df['Course Name Lower'] == closest_match[0]].index[0]
        
        # Use the pre-calculated similarity scores
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
        
        recs_list = []
        for i, score in sim_scores:
            row = df.iloc[i]
            recs_list.append({
                "name": str(row['Course Name']),
                "univ": str(row['University']),
                "diff": str(row['Difficulty Level']),
                "rate": str(row['Course Rating']),
                "url": str(row['Course URL'])
            })
        
        return jsonify({"recs": recs_list})
    except Exception as e:
        print(f"Backend Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)