from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import re

app = FastAPI(
    title="Sistema de Recomendação Musical",
    description="API de recomendações musicais usando conteúdo, gênero, colaborativo e híbrido",
    version="1.0.0",
)

# Carregar os dados e ajustar os nomes das colunas
songs = pd.read_csv("app/musicas.csv")
songs = songs.rename(columns={"the genre of the track": "genre"})

def clean(col_name):
    if col_name in ["genre", "title", "artist", "year"]:
        return col_name
    if "-" in col_name:
        col_name = col_name.split("-")[0]
    if "_" in col_name:
        col_name = col_name.split("_")[0]
    # Remover qualquer caracter especial (deixar só letras e números)
    col_name = re.sub(r"[^A-Za-z0-9]", "", col_name)
    return col_name.lower()


songs.columns = [clean(col) for col in songs.columns]


def recomendacaoBaseadaEmConteudo(song_title, limit=5, weights=None):
    feature_cols = [
        "beatsperminute",
        "energy",
        "danceability",
        "loudnessdb",
        "liveness",
        "valence",
        "length",
        "acousticness",
        "speechiness",
        "popularity",
    ]

    # Aplicar pesos
    features = songs[feature_cols]
    if weights:
        for feat, w in weights.items():
            if feat in features.columns:
                features[feat] = features[feat] * w

    sim_matrix = cosine_similarity(features)
    song_idx = songs[songs["title"].str.lower() == song_title.lower()].index
    if len(song_idx) == 0:
        return []

    song_idx = song_idx[0]
    sim_scores = list(enumerate(sim_matrix[song_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1 : limit + 1]

    recommended = [songs.iloc[i].to_dict() for i, _ in sim_scores]
    return recommended


def recomendacaoGenreArtist(genre=None, artist=None, limit=5):
    filtered = songs
    if genre:
        filtered = filtered[filtered["genre"].str.lower() == genre.lower()]
    if artist:
        filtered = filtered[filtered["artist"].str.lower() == artist.lower()]

    if filtered.empty:
        return []
    return (
        filtered.sort_values(by="popularity", ascending=False)
        .head(limit)
        .to_dict(orient="records")
    )


# Simulação de dados fictícios de usuário
user_preferences = {
    1: ["Shape of You", "Blinding Lights", "Rockstar"],
    2: ["Rockstar", "Closer", "One Dance"],
    3: ["Blinding Lights", "Senorita", "Girls Like You"],
}


def filtragemColaborativa(user_id, limit=5):
    if user_id not in user_preferences:
        return []

    liked_songs = user_preferences[user_id]
    co_occur = {}

    for user, songs_liked in user_preferences.items():
        if user == user_id:
            continue
        for song in songs_liked:
            if song not in liked_songs:
                co_occur[song] = co_occur.get(song, 0) + 1

    recommended = sorted(co_occur.items(), key=lambda x: x[1], reverse=True)[:limit]
    results = []
    for song_name, _ in recommended:
        song_info = songs[songs["title"].str.lower() == song_name.lower()]
        if not song_info.empty:
            results.append(song_info.iloc[0].to_dict())
    return results


# Função híbrida
def recomendacaoHibrida(
    song_title, user_id, content_weight=0.7, collab_weight=0.3, limit=5
):
    content_recs = recomendacaoBaseadaEmConteudo(song_title, limit=20)
    collab_recs = filtragemColaborativa(user_id, limit=20)

    content_titles = {rec["title"]: (i + 1) for i, rec in enumerate(content_recs)}
    collab_titles = {rec["title"]: (i + 1) for i, rec in enumerate(collab_recs)}

    combined_scores = {}
    for title in set(content_titles.keys()).union(collab_titles.keys()):
        content_score = content_weight * (1 / content_titles.get(title, 100))
        collab_score = collab_weight * (1 / collab_titles.get(title, 100))
        combined_scores[title] = content_score + collab_score

    final_titles = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[
        :limit
    ]
    results = []
    for title, _ in final_titles:
        song_info = songs[songs["title"].str.lower() == title.lower()]
        if not song_info.empty:
            results.append(song_info.iloc[0].to_dict())
    return results


# Popularidade filtrada por ano ou gênero
def popularidade(year=None, genre=None, limit=5):
    filtered = songs
    if year:
        filtered = filtered[filtered["year"] == year]
    if genre:
        filtered = filtered[filtered["genre"].str.lower() == genre.lower()]

    if filtered.empty:
        return []
    return (
        filtered.sort_values(by="popularity", ascending=False)
        .head(limit)
        .to_dict(orient="records")
    )


#MODELOS


class GenreArtistRequest(BaseModel):
    genre: str = None
    artist: str = None
    limit: int = 5


class HybridoRequest(BaseModel):
    song_title: str
    user_id: int
    content_weight: float = 0.7
    collab_weight: float = 0.3
    limit: int = 5


#ENDPOINTS


@app.get("/recommendations/content-based/{song_title}")
async def recomenda_conteudo(song_title: str, limit: int = 5, weights: dict = None):
    return recomendacaoBaseadaEmConteudo(song_title, limit, weights)


@app.post("/recommendations/genre-artist")
async def recomenda_genero_artista(request: GenreArtistRequest):
    return recomendacaoGenreArtist(request.genre, request.artist, request.limit)


@app.get("/recommendations/collaborative/{user_id}")
async def recomendacao_colaborativa(user_id: int, limit: int = 5):
    return filtragemColaborativa(user_id, limit)


@app.post("/recommendations/hybrid")
async def recomendacao_hybrida(request: HybridoRequest):
    return recomendacaoHibrida(
        request.song_title,
        request.user_id,
        request.content_weight,
        request.collab_weight,
        request.limit,
    )

@app.get("/recommendations/popular")
async def recomenda_popularidade(year: int = None, genre: str = None, limit: int = 5):
    return popularidade(year, genre, limit)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return RedirectResponse(url="/docs")
    else:
        raise exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
