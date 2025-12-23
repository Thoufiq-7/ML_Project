import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load
df = pd.read_csv("data.csv")

# 2. Clean & Combine
df['content'] = (df['Course Name'] + " " + df['Difficulty Level'] + 
                 " " + df['Course Description'] + " " + df['Skills']).fillna('')

# 3. Train (Vectorize)
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['content'])

# 4. Save the Brain
# We save the matrix and the dataframe to use in the backend
model_data = {
    'matrix': tfidf_matrix,
    'df': df
}

with open('model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("Model trained and saved as model.pkl")