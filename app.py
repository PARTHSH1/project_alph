from flask import Flask, render_template, request
import pickle
import requests
import gzip
import pickle


app = Flask(__name__)

# Load your data and similarity matrix
with gzip.open("movie_list.pkl.gz", "rb") as f_in:
    movies = pickle.load(f_in)

with gzip.open("movie_list.pkl.gz", "rb") as f_in:
    similarity = pickle.load(f_in)


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
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
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        recommendations = zip(recommended_movie_names, recommended_movie_posters)
    return render_template('index.html', movie_list=movie_list, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)

