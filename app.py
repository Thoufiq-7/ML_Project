from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

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
    course_title = request.form.get('user_id') # We'll use the input for Course Name now
    
    if course_title not in df['Course Name'].values:
        return jsonify({"error": "Course not found"}), 404

    # Get index of the course
    idx = df[df['Course Name'] == course_title].index[0]
    
    # Get similarity scores for all courses
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort by highest score, skip the first one (itself)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    
    # Get titles
    course_indices = [i[0] for i in sim_scores]
    recs = df['Course Name'].iloc[course_indices].tolist()
    
    return jsonify({"recs": recs})

if __name__ == '__main__':
    app.run(debug=True)