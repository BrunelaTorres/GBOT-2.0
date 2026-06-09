from telebot import types

def salir(bot, message):
    bot.send_message(
        message.chat.id,
        "👋 ¡Gracias por usar G-BOT!, esperamos que vuelvas a consultarnos"
          "🌱Seguimos cuidando el planeta juntos 💚"
          "💚Infinitas gracias💚",
        reply_markup=types.ReplyKeyboardRemove()
    )
