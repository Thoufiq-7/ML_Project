from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import difflib 

app = Flask(__name__, 
            template_folder='frontend/templates', 
            static_folder='frontend/static')

with open('model.pkl', 'rb') as f:
    data = pickle.load(f)
    tfidf_matrix = data['matrix']
    df = data['df']
# 1. LOAD & CLEAN
df = pd.read_csv("data.csv")
df.head(5)
# Combine text columns into one "soup" for the model to read
df['content'] = df['Course Description'] + " " + df['Skills'] + " " + df['Difficulty Level']
df['content'] = df['content'].fillna('')

# 2. VECTORIZE (The Math)
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['content'])

# 3. CALCULATE SIMILARITY
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.form.get('user_id').lower().strip()
    all_courses = df['Course Name Lower'].tolist()
    closest_match = difflib.get_close_matches(user_input, all_courses, n=1, cutoff=0.3)

    if not closest_match:
        return jsonify({"recs": []})

    idx = df[df['Course Name Lower'] == closest_match[0]].index[0]
    sim_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    related_indices = sim_scores.argsort()[-11:-1][::-1]
    
    recs_list = []
    for i in related_indices:
        row = df.iloc[i]
        # We use the EXACT column names you provided
        recs_list.append({
            "name": str(row['Course Name']),
            "univ": str(row['University']),
            "diff": str(row['Difficulty Level']),
            "rate": str(row['Course Rating']),
            "url": str(row['Course URL'])
        })
    
    return jsonify({"recs": recs_list})

if __name__ == '__main__':
    app.run(debug=True)