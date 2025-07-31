import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os



load_dotenv('key.env')
csv_path = os.getenv('CSV_PATH')
if csv_path:
    try:
        df = pd.read_csv(csv_path)
        print("CSV loaded successfully!")
    except Exception as e:
        print("Failed to load CSV:", e)
else:
    print("CSV path not found in environment variables.")



# Data Preprocessing
df['short_composition1'] = df['short_composition1'].fillna('')
df['short_composition2'] = df['short_composition2'].fillna('')
for col in ['Is_discontinued', 'type', 'pack_size_label']:
    if col in df.columns:
        df.drop(col, axis=1, inplace=True)
df['combined_composition'] = df['short_composition1'] + ' ' + df['short_composition2']
df = df.sort_values(by='id', ascending=True)

tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_composition'])
svd = TruncatedSVD(n_components=7, n_iter=7, random_state=42)
reduced_matrix = svd.fit_transform(tfidf_matrix)




def calculate_similarity_in_batches(query_index, reduced_matrix, batch_size=1000):
    similarity_scores = []
    for i in range(0, reduced_matrix.shape[0], batch_size):
        batch_end = min(i + batch_size, reduced_matrix.shape[0])
        batch_similarity = cosine_similarity(reduced_matrix[query_index:query_index+1], reduced_matrix[i:batch_end])
        for j in range(batch_similarity.shape[1]):
            similarity_scores.append((i + j, batch_similarity[0, j]))
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores




def find_similar_medicines(index, reduced_matrix, top_n):
    similarity_scores = calculate_similarity_in_batches(index, reduced_matrix)
    top_similar_indices = [score[0] for score in similarity_scores[1:top_n + 1]]
    return top_similar_indices




def alternatives(target_index, top_n=5):
    """
    Finds similar medicines and returns them as a clean list of dictionaries.
    This is more robust than relying on column order.
    """
    similar_medicines_indices = find_similar_medicines(target_index, reduced_matrix, top_n)
    
    results = []
    for index in similar_medicines_indices:
        # Get the row of data for the alternative medicine
        row = df.iloc[index]
        
        # Build a dictionary with clear keys for each piece of data
        results.append({
            "name": row['name'],
            "manufacturer": row['manufacturer_name'],
            "composition": row['combined_composition'],
            "price": row['price']
        })
    return results




import pandas as pd



def search_medicine(medicine_found):

    """
    Searches for a medicine by checking both its brand name and its composition.
    This is a much more robust way to find matches.
    """

    if not medicine_found:
        return (None, None, None, None, None)

    # Prepare the search term
    search_term = medicine_found.lower()

    # Search in both 'name' and 'combined_composition' columns
    name_matches = df[df['name'].str.lower().str.contains(search_term, na=False)]
    composition_matches = df[df['combined_composition'].str.lower().str.contains(search_term, na=False)]

    # Combine the results, prioritize brand name matches, and remove duplicates
    combined_results = pd.concat([name_matches, composition_matches]).drop_duplicates().reset_index()

    if not combined_results.empty:
        # Get the first matched row from our combined search
        first_match_row = combined_results.iloc[0]
        
        # Extract the details from this row
        med_searched_name = first_match_row['name']
        comp = first_match_row['combined_composition']
        manu = first_match_row['manufacturer_name']
        price = first_match_row['price']
        
        # Get the original index to find alternatives for the *correct* medicine
        original_df_index = first_match_row['index']
        similar_meds = alternatives(original_df_index)
        
        return (med_searched_name, comp, similar_meds, manu, price)
    else:
        # Return None if no match is found in either column
        return (None, None, None, None, None)
