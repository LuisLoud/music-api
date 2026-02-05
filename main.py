from fastapi import FastAPI, UploadFile, File
from supabase import create_client, Client

from dotenv import load_dotenv

import os, uuid, shutil, time, json, math
import numpy as np

#from essentia.standard import (
#    MonoLoader,
#    TensorflowPredictMAEST,
#    TensorflowPredictEffnetDiscogs,
#    TensorflowPredictVGGish,
#    TensorflowPredict2D,
#    TensorflowPredict,
#    TempoCNN
#)
#from essentia import Pool

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("URL:", SUPABASE_URL)
print("KEY:", SUPABASE_KEY)

app = FastAPI()

# embedding_model_1_2 = TensorflowPredictMAEST(
#     graphFilename="./models/discogs-maest-5s-pw-2.pb",
#     output="PartitionedCall/Identity_12"
# )

# embedding_model_2 = TensorflowPredictMAEST(
#     graphFilename="./models/discogs-maest-30s-pw-519l-2.pb",
#     output="PartitionedCall/Identity_12"
# )

# embedding_discogs_model = TensorflowPredictEffnetDiscogs(
#     graphFilename="./models/discogs-effnet-bs64-1.pb",
#     output="PartitionedCall:1"
# )

# embedding_vggish_model = TensorflowPredictVGGish(
#     graphFilename="./models/audioset-vggish-3.pb",
#     output="model/vggish/embeddings"
# )

# model_1_2 = TensorflowPredict(
#     graphFilename="./models/genre_discogs400-discogs-maest-5s-pw-1.pb",
#     inputs=["embeddings"],
#     outputs=["PartitionedCall/Identity_1"]
# )

# model_2 = TensorflowPredict(
#     graphFilename="./models/genre_discogs519-discogs-maest-30s-pw-519l-1.pb",
#     inputs=["embeddings"],
#     outputs=["PartitionedCall/Identity_1"]
# )

# model_3  = TensorflowPredict2D("./models/mtg_jamendo_genre-discogs-effnet-1.pb")
# model_11 = TensorflowPredict2D("./models/mtg_jamendo_moodtheme-discogs-effnet-1.pb")
# model_24 = TensorflowPredict2D("./models/mtg_jamendo_top50tags-discogs-effnet-1.pb")
# model_25 = TensorflowPredict2D("./models/mtt-discogs-effnet-1.pb")
# model_12 = TensorflowPredict2D("./models/mtg_jamendo_instrument-discogs-effnet-1.pb")

# model_10_2 = TensorflowPredict2D(
#     graphFilename="./models/moods_mirex-audioset-vggish-1.pb",
#     input="serving_default_model_Placeholder",
#     output="PartitionedCall"
# )

# model_4_1  = TensorflowPredict2D("./models/danceability-audioset-vggish-1.pb", output="model/Softmax")
# model_5_1  = TensorflowPredict2D("./models/mood_aggressive-audioset-vggish-1.pb", output="model/Softmax")
# model_6_1  = TensorflowPredict2D("./models/mood_happy-audioset-vggish-1.pb", output="model/Softmax")
# model_7_1  = TensorflowPredict2D("./models/mood_party-audioset-vggish-1.pb", output="model/Softmax")
# model_8_1  = TensorflowPredict2D("./models/mood_relaxed-audioset-vggish-1.pb", output="model/Softmax")
# model_9_1  = TensorflowPredict2D("./models/mood_sad-audioset-vggish-1.pb", output="model/Softmax")
# model_14_1 = TensorflowPredict2D("./models/mood_acoustic-audioset-vggish-1.pb", output="model/Softmax")
# model_15_1 = TensorflowPredict2D("./models/mood_electronic-audioset-vggish-1.pb", output="model/Softmax")
# model_16_1 = TensorflowPredict2D("./models/voice_instrumental-audioset-vggish-1.pb", output="model/Softmax")
# model_17_1 = TensorflowPredict2D("./models/gender-audioset-vggish-1.pb", output="model/Softmax")
# model_23_1 = TensorflowPredict2D("./models/tonal_atonal-audioset-vggish-1.pb", output="model/Softmax")

# model_30_1 = TempoCNN(
#     graphFilename="./models/deepsquare-k16-3.pb"
# )

# model_31_3 = TensorflowPredict2D(
#     "./models/deam-audioset-vggish-2.pb",
#     output="model/Identity"
# )

# model_31_4 = TensorflowPredict2D(
#     "./models/emomusic-audioset-vggish-2.pb",
#     output="model/Identity"
# )


def classificar_audio(caminho):
    # depois você colocará seu código real aqui
    return {
        "tempo": 120,
        "moods_mirex": "rock",
        "happy": 0.5
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    nome_unico = f"{uuid.uuid4()}_{file.filename}"
    caminho_local = f"temp_{nome_unico}"

    with open(caminho_local, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resultado = classificar_audio(caminho_local)

    with open(caminho_local, "rb") as f:
        supabase.storage.from_("audios").upload(
            f"uploads/{nome_unico}", f
        )

    supabase.table("TESTE_ROCK").insert({
        "arquivo": file.filename,
        "caminho": f"uploads/{nome_unico}",
        "tempo": resultado["tempo"]
    }).execute()

    os.remove(caminho_local)

    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/buscar")
def buscar_musica(arquivo: str):
    resposta = supabase.table("TESTE_ROCK") \
        .select("*") \
        .ilike("arquivo", f"%{arquivo}%") \
        .execute()

    return resposta.data


@app.get("/buscar_genero")
def buscar_genero(genero: str):

    filtro = (
        f"genre_discogs400_maest5s_1.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_2.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_3.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_4.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_5.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_6.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_7.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_8.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_9.ilike.%{genero}%,"
        f"genre_discogs400_maest5s_10.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_1.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_2.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_3.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_4.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_5.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_6.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_7.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_8.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_9.ilike.%{genero}%,"
        f"genre_discogs519_maest30s_10.ilike.%{genero}%,"
        f"jamendo_genre_1.ilike.%{genero}%,"
        f"jamendo_genre_2.ilike.%{genero}%,"
        f"jamendo_genre_3.ilike.%{genero}%,"
        f"jamendo_genre_4.ilike.%{genero}%,"
        f"jamendo_genre_5.ilike.%{genero}%,"
        f"jamendo_genre_6.ilike.%{genero}%,"
        f"jamendo_genre_7.ilike.%{genero}%,"
        f"jamendo_genre_8.ilike.%{genero}%,"
        f"jamendo_genre_9.ilike.%{genero}%,"
        f"jamendo_genre_10.ilike.%{genero}%"
    )

    resposta = supabase.table("TESTE_ROCK") \
        .select("arquivo") \
        .or_(filtro) \
        .execute()

    return resposta.data

@app.get("/buscar_mood_theme")
def buscar_mood_theme(mood_theme: str):

    filtro = (
        f"jamendo_mood_theme_1.ilike.%{mood_theme}%,"
        f"jamendo_mood_theme_2.ilike.%{mood_theme}%,"
        f"jamendo_mood_theme_3.ilike.%{mood_theme}%,"
        f"jamendo_mood_theme_4.ilike.%{mood_theme}%,"
        f"jamendo_mood_theme_5.ilike.%{mood_theme}%"
    )

    resposta = supabase.table("TESTE_ROCK") \
        .select("arquivo") \
        .or_(filtro) \
        .execute()

    return resposta.data

@app.get("/buscar_topmagna")
def buscar_topmagna(topmagna: str):

    filtro = (
        f"jamendo_top50_tags_1.ilike.%{topmagna}%,"
        f"jamendo_top50_tags_2.ilike.%{topmagna}%,"
        f"jamendo_top50_tags_3.ilike.%{topmagna}%,"
        f"jamendo_top50_tags_4.ilike.%{topmagna}%,"
        f"jamendo_top50_tags_5.ilike.%{topmagna}%,"
        f"magnatagatune_1.ilike.%{topmagna}%,"
        f"magnatagatune_2.ilike.%{topmagna}%,"
        f"magnatagatune_3.ilike.%{topmagna}%,"
        f"magnatagatune_4.ilike.%{topmagna}%,"
        f"magnatagatune_5.ilike.%{topmagna}%"
    )

    resposta = supabase.table("TESTE_ROCK") \
        .select("arquivo") \
        .or_(filtro) \
        .execute()

    return resposta.data

@app.get("/buscar_instrument")
def buscar_instrument(instrument: str):

    filtro = (
        f"jamendo_instrument_2.ilike.%{instrument}%,"
        f"jamendo_instrument_2.ilike.%{instrument}%,"
        f"jamendo_instrument_2.ilike.%{instrument}%,"
        f"jamendo_instrument_2.ilike.%{instrument}%,"
        f"jamendo_instrument_2.ilike.%{instrument}%"
    )

    resposta = supabase.table("TESTE_ROCK") \
        .select("arquivo") \
        .or_(filtro) \
        .execute()

    return resposta.data

@app.get("/buscar_moods_mirex")
def buscar_moods_mirex(moods_mirex: str):
    resposta = supabase.table("TESTE_ROCK") \
        .select("arquivo") \
        .ilike("moods_mirex", f"%{moods_mirex}%") \
        .execute()

    return resposta.data

@app.get("/buscar_mood")
def buscar_mood(mood: str):

    filtro = (
        f"deam_mood_principal.ilike.%{mood}%,"
        f"deam_moods_vizinhos.ilike.%{mood}%,"
        f"emo_mood_principal.ilike.%{mood}%,"
        f"emo_mood_principal.ilike.%{mood}%"
    )

    resposta = supabase.table("TESTE_ROCK") \
        .select("arquivo") \
        .or_(filtro) \
        .execute()

    return resposta.data