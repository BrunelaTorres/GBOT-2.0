# sentiment_analysis.py (con paso de usuario)
import os
from groq import Groq
from dotenv import load_dotenv
import telebot

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)


# --- ANALISIS DE SENTIMIENTOS ---

def analizar_sentimiento(texto: str) -> str:
    """
    Analiza si una opinión es positiva, negativa o neutral usando Groq.
    Devuelve: "positivo", "negativo" o "neutral".
    """

    mensajes = [
        {"role": "system", "content": "Clasifica el sentimiento del texto como positivo, negativo o neutral. Solo responde con una palabra."},
        {"role": "user", "content": texto}
    ]

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes,
            temperature=0.0
        )

        # CORRECCIÓN IMPORTANTE:
        resultado = response.choices[0].message.content.strip().lower()

        if "positivo" in resultado:
            return "positivo"
        elif "negativo" in resultado:
            return "negativo"
        else:
            return "neutral"

    except Exception as e:
        print("Error al analizar sentimiento:", e)
        return "neutral"


# --- FLUJO DE OPINIÓN EN TELEGRAM ---

def pedir_opinion(bot, message):
    """
    Mensaje inicial para pedir opinión al usuario.
    """
    user_id = message.chat.id

    bot.send_message(
        user_id,
        "📝 *Dejanos tu opinión:* escribí cómo fue tu experiencia con GIRSU.",
        parse_mode="Markdown"
    )

    # Espera la opinión del usuario
    bot.register_next_step_handler(message, lambda m: procesar_opinion(bot, m))


def procesar_opinion(bot, message):
    """
    Recibe la opinión del usuario, analiza el sentimiento y responde.
    """

    user_id = message.chat.id

    if not message.text:
        bot.send_message(user_id, "❗ Por favor escribí un texto con tu opinión.")
        return

    opinion = message.text.strip()

    # Mostrar "escribiendo…"
    bot.send_chat_action(user_id, "typing")

    sentimiento = analizar_sentimiento(opinion)

    if sentimiento == "positivo":
        respuesta = "😊 ¡Gracias por tu comentario positivo! Nos alegra mucho."
    elif sentimiento == "negativo":
        respuesta = "😟 Lamentamos que tu experiencia no haya sido buena. Vamos a tenerlo en cuenta."
    else:
        respuesta = "🙂 ¡Gracias por tu opinión! La tendremos en cuenta."

    bot.send_message(user_id, respuesta)
