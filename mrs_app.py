from flask import Flask, render_template, request, redirect, jsonify, make_response
from flask_cors import CORS, cross_origin
import pickle
import pandas as pd
import numpy as np
import requests
import json

app = Flask(__name__)
cors = CORS(app)

movies_dict = pickle.load(open('backend/movies_dict.pkl', 'rb'))

def fetch_poster(movie_id):
    response = requests.get("https://api.themoviedb.org/3/movie/"+format(movie_id)+"?api_key=36918a0c2a061e7fd76bddeda063bcf8&language=en-US")
    data_dumps = json.dumps(response.json(), indent=4)
    #print("""jj""")
    #data = response.json()
    data = json.loads(data_dumps)
    #print(data)
    #print(data['poster_path'])
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


@app.route('/', methods=['GET', 'POST'])
def index():
    movies = pd.DataFrame(movies_dict)
    movies = selected_movie_name = movies['title'].values
    return render_template('index.html', movies=movies)

@app.route('/generate_magic', methods=['POST'])
@cross_origin()
def recommend():
    request_movie = request.form['movie']
    request_movie = request.args.get(request_movie)
    #print("request_movie", request_movie)
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('backend/similarity.pkl', 'rb'))
    selected_movie = request.form.get('movie')  # movie variable for selected movie
    #print("selected_movie",selected_movie)
    movie_index = movies[movies['title'] == selected_movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)),
                         reverse=True, key=lambda x: x[1])[1:13]

    #print(movies)
    recommended_movies = []
    recommended_movies_poster = []
    rm_homepage = []
    rm_vote_average = []
    rm_tagline = []

    for i in movies_list:
        #print(movies)
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
        # rm_homepage.append(movies.iloc[i[0]].homepage)
        # rm_vote_average.append(movies.iloc[i[0]].vote_average)
        rm_tagline.append(movies.iloc[i[0]].tags)

    responseBody = {"recommended_movies": recommended_movies,
                    "recommended_movies_poster": recommended_movies_poster,
                    # "rm_homepage": rm_homepage,
                    # "rm_vote_average": rm_vote_average,
                    "rm_desc": rm_tagline,
                    }
    print(responseBody)
    return make_response(jsonify(responseBody), 200)

if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
