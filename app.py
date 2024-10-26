from flask import Flask, render_template, request
import pickle
import requests
import gzip
import numpy as np

# Load your movie data and similarity matrix
with gzip.open("movie_list.pkl.gz", "rb") as f_in:
    movies = pickle.load(f_in)

with gzip.open("similarity.pkl.gz", "rb") as f_in:
    similarity = pickle.load(f_in)

app = Flask(__name__)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)

    if response.status_code == 200:  # Check if the request was successful
        data = response.json()
        poster_path = data.get('poster_path', '')
        full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""
        return full_path
    else:
        return ""  # Return empty if the poster could not be fetched

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Get top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    movie_list = movies['title'].values
    recommendations = []

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        if selected_movie in movie_list:  # Check if the selected movie is valid
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
            recommendations = zip(recommended_movie_names, recommended_movie_posters)

    return render_template('index.html', movie_list=movie_list, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
