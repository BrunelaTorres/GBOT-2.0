import json
import os
from groq import Groq
from dotenv import load_dotenv
import subprocess

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

def cargar_dataset1():
    try:
        with open("dataset1.json", "r", encoding="utf-8") as f:
            return json.load(f)["categorias"]
    except Exception as e:
        print("Error cargando dataset1:", e)
        return []

dataset = cargar_dataset1()

def buscar_respuesta(pregunta):
    pregunta = pregunta.strip().lower()

    for categoria in dataset:
        for item in categoria.get("preguntas", []):
            variantes = item.get("variantes_pregunta", [])
            
            for variante in variantes:
                if variante.strip().lower() == pregunta:
                    return item.get("respuesta")
    return None

def respuesta_groq(texto):
    prompt = (
        "Eres un asistente del sistema GIRSU. Si la información "
        "no está en el dataset, responde: "
        "'No cuento con esa información ahora mismo. "
        "Podés comunicarte con municipalidad@almafuerte.gov.ar 😊'." 
    )

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": texto}
        ]
    )

    return response.choices[0].message.content.strip()


def ogg_a_wav(ruta_ogg):
    ruta_wav = ruta_ogg.replace(".ogg", ".wav")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", ruta_ogg, ruta_wav
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ruta_wav
    except Exception as e:
        print("Error convirtiendo audio:", e)
        return None


def audio_a_texto(ruta_ogg):
    try:
        response = groq_client.audio.transcriptions.create(
            file=ruta_ogg,
            model="whisper-large-v3"
        )
        return response.text
    except Exception as e:
        print("Error en transcripción:", e)
        return None


def procesar_audio(ruta_audio):
    # Convertimos .ogg a .wav compatible
    ruta_wav = ogg_a_wav(ruta_audio)
    if not ruta_wav:
        return "❌ No pude procesar tu audio."

    # Procesamos audio con Groq/Whisper
    texto = audio_a_texto(ruta_wav)
    if not texto:
        return "❌ No pude procesar tu audio."

    # Limpiamos archivo temporal
    os.remove(ruta_wav)

    return procesar_texto(texto)


def procesar_texto(texto):
    respuesta = buscar_respuesta(texto)
    if respuesta:
        return respuesta

    return respuesta_groq(texto)


def send_welcome(bot, message):
    bot.send_message(
        message.chat.id,
        "👋 Hola, soy G-BOT.\nPodés preguntarme lo que quieras sobre GIRSU."
    )

