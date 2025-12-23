import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("data.csv")

# Ensure lowercase for matching
df['Course Name Lower'] = df['Course Name'].str.lower().str.strip()

# Combine text for the model
df['content'] = (df['Course Name'] + " " + df['Difficulty Level'] + 
                 " " + df['Course Description'] + " " + df['Skills']).fillna('').str.lower()

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['content'])

# PRE-CALCULATE SIMILARITY HERE
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Save the DF and the SIMILARITY MATRIX
model_data = {
    'df': df,
    'cosine_sim': cosine_sim
}

with open('model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("Training Complete. model.pkl created.")