import telebot
import config
from telebot import apihelper
from proxy import Proxy
import response_storage  

def run(path, name):

    bot = telebot.TeleBot(config.TOKEN)
    apihelper.proxy = {"https": config.PROXY}
    photo = open(path, "rb")
    bot.send_message(config.ADMIN_ID, response_storage.face_detected + name)
    bot.send_photo(config.ADMIN_ID, photo)
