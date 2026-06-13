import telebot
from telebot import types
import os
import bot_voz                # Responde por voz y texto (dataset1)
import basurero               # Responde basurero voz + texto (dataset2)
import imagen                 # Clasificar imágenes
import opinion                # Analizar opinión usuario
from opinion import pedir_opinion
import salir

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)


# MENÚ PRINCIPAL
@bot.message_handler(commands=['start'])
def menu_principal(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(types.InlineKeyboardButton("🤖 Interactuar con G-BOT", callback_data="interactuar"))
    markup.add(types.InlineKeyboardButton("🚛 Saber cuándo pasa el camión basurero", callback_data="basurero"))
    markup.add(types.InlineKeyboardButton("♻️ ¿Esto es reciclable?", callback_data="reciclable"))
    markup.add(types.InlineKeyboardButton("💬 Dejanos tu opinión", callback_data="opinion"))
    markup.add(types.InlineKeyboardButton("🚪 Salir", callback_data="salir"))

    mensaje = (
        "🌱 *¡Bienvenido a G-BOT!*\n\n"
        "Este bot es para residentes de la localidad de Almafuerte!\n"
        "Mis funcionalidades son:\n"
        "• Separacion de residuos\n"
        "• Saber cuándo pasa el basurero por tu barrio🚛\n"
        "• Identificar si un objeto es reciclable ♻️\n"
        "• Dejar tu opiniòn para que podamos mejorar! 💬\n"
        "Elegí una opción 👇"
    )

    bot.send_message(message.chat.id, mensaje, parse_mode="Markdown", reply_markup=markup)



# MENSAJES

@bot.callback_query_handler(func=lambda call: True)
def menu_callback(call):
    chat_id = call.message.chat.id

    # ------------------ G-BOT ------------------
    if call.data == "interactuar":
        bot_voz.send_welcome(bot, call.message)
        bot.register_next_step_handler(call.message, manejar_gbot)

    # ------------------ BASURERO ------------------
    elif call.data == "basurero":
        bot.send_message(chat_id, "🏘️ Decime tu *barrio* por texto o audio:", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, manejar_basurero)

    # ------------------ RECICLABLE (IMAGEN) ------------------
    elif call.data == "reciclable":
        bot.send_message(chat_id, "📸 Enviá una *foto* del objeto que querés analizar.")
        bot.register_next_step_handler(call.message, manejar_imagen)

    # ------------------ OPINIÓN ------------------
    elif call.data == "opinion":
        pedir_opinion(bot, call.message)

    # ------------------ SALIR ------------------
    elif call.data == "salir":
        salir.salir(bot, call.message)


# MANEJAR G-BOT (dataset1)
def manejar_gbot(message):
    # AUDIO
    if message.content_type == "voice":
        file_info = bot.get_file(message.voice.file_id)
        data = bot.download_file(file_info.file_path)

        with open("voz.ogg", "wb") as f:
            f.write(data)

        respuesta = bot_voz.procesar_audio("voz.ogg")
        bot.send_message(message.chat.id, respuesta)
        return

    # TEXTO
    if message.content_type == "text":
        respuesta = bot_voz.procesar_texto(message.text)
        bot.send_message(message.chat.id, respuesta)
        return


# MANEJAR BASURERO (dataset2)
def manejar_basurero(message):

    # AUDIO
    if message.content_type == "voice":
        file_info = bot.get_file(message.voice.file_id)
        data = bot.download_file(file_info.file_path)

        with open("basurero.ogg", "wb") as f:
            f.write(data)

        respuesta = basurero.procesar_audio("basurero.ogg")
        bot.send_message(message.chat.id, respuesta)
        return

    # TEXTO
    if message.content_type == "text":
        respuesta = basurero.procesar_texto(message.text)
        bot.send_message(message.chat.id, respuesta, parse_mode="Markdown")
        return



# MANEJAR IMÁGENES (Reciclable o no)
def manejar_imagen(message):
    if message.content_type != "photo":
        bot.send_message(message.chat.id, "⚠️ Debés enviar una *foto*.")
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    data = bot.download_file(file_info.file_path)

    ruta = "objeto.jpg"
    with open(ruta, "wb") as f:
        f.write(data)

    resultado = imagen.clasificar(ruta)
    bot.send_message(message.chat.id, f"🔎 *Resultado:* {resultado}", parse_mode="Markdown")



# INICIO DEL BOT

if __name__ == "__main__":
    print("🚀 G-BOT iniciado correctamente.")
    bot.infinity_polling()
