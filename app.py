import pickle
import streamlit as st
import requests
import pandas as pd

# Load saved data (includes movie_id for poster fetching)
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to fetch poster from TMDB
def fetch_poster(movie_id):
    try:
        api_key = "c3169241c160a57cf82102739dc80633"  # ideally from env vars
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception as e:
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=Error"

# Recommender logic
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# Streamlit UI
st.title('🎬 Movie Recommendation System')

selected_movie = st.selectbox('Search any movie you like:', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i], use_container_width=True)
    else:
        st.warning("Sorry, movie not found or error occurred.")

