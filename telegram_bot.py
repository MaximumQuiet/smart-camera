#!/usr/bin/python
# -*- coding: utf-8 -*-
import telebot
import config
from imutils import paths
import detect_face
import encode_faces
from telebot import apihelper
from telebot import types
import os
import shutil
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import states_worker as sw
from proxy import Proxy
import pickle
import time
import utils
import response_storage
import subprocess
import pgrep
import signal
from subprocess import check_output, CalledProcessError

apihelper.proxy = {"https": config.PROXY}

bot = telebot.TeleBot(config.TOKEN)

photos_count = 0
name = ""


@bot.message_handler(commands=["start", "help"])
def cmd_start(msg):
    state = sw.get_current_state(msg.chat.id)
    if (state != sw.UNAUTHORIZED):
        bot.send_message(msg.chat.id, response_storage.system_ready, 
        	             reply_markup=utils.make_keyboard("main"))
    else:
        bot.send_message(msg.chat.id, response_storage.you_not_auth)

@bot.message_handler(func=lambda message: message.text == response_storage.status)
def cmd_status(msg):
    bot.reply_to(msg, utils.change_text_markdown(response_storage.online, "italic"), 
    	         parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == response_storage.face_mng)
def cmd_face_mng(msg):
    bot.send_message(msg.chat.id, response_storage.face_mng, 
    	             reply_markup=utils.make_inline_keyboard("face_managment"))

@bot.message_handler(func=lambda message: message.text == response_storage.camera_toggle_on)
def cmd_camera_toggle_on(msg): 
    os.system("python3 /home/pi/smart-camera/recognition.py &") 
    bot.send_message(msg.chat.id,
            utils.change_text_markdown(response_storage.camera_turned_on, "italic"), 
    	         parse_mode="Markdown", reply_markup=utils.make_keyboard("main"))

@bot.message_handler(func=lambda message: message.text == response_storage.camera_toggle_off) 
def cmd_camera_toggle_off(msg):
    pids = pgrep.pgrep("-f recognition")
    for pid in pids:
        os.kill(int(pid), signal.SIGKILL)

    bot.send_message(msg.chat.id,
            utils.change_text_markdown(response_storage.camera_turned_off, "italic"), 
    	         parse_mode="Markdown", reply_markup=utils.make_keyboard("main"))

@bot.callback_query_handler(func=lambda message: message.data == "add_face")
def cmd_inline_add_face(msg):
    m = bot.edit_message_text(chat_id=msg.message.chat.id,
    	                      message_id=msg.message.message_id, 
    	                      text=response_storage.send_name, 
                              reply_markup=utils.make_inline_keyboard("cancel"))

    sw.set_current_state(msg.message.chat.id, sw.SEND_NAME)
    

@bot.callback_query_handler(func=lambda message: message.data == "list_of_faces")
def cmd_inline_list_of_faces(msg):
    m = bot.edit_message_text(chat_id=msg.message.chat.id, 
    	                      message_id=msg.message.message_id, 
    	                      text=response_storage.list_of_faces, 
                              reply_markup=utils.make_inline_keyboard("list_of_faces"))

    sw.set_current_state(msg.message.chat.id, sw.LIST_OF_FACES)


@bot.callback_query_handler(func=lambda message: message.data == "delete_face")
def cmd_inline_delete_face(msg):
    m = bot.edit_message_text(chat_id=msg.message.chat.id, 
    	                      message_id=msg.message.message_id, 
    	                      text=response_storage.confirm_delete_face, 
    	                      reply_markup=utils.make_inline_keyboard("confirm_cancel"))

    sw.set_current_state(msg.message.chat.id, sw.DELETE_FACE)


@bot.callback_query_handler(func=lambda message: message.data == "get_photo")
def cmd_inline_get_photo(msg):

    imagePaths = list(paths.list_images("dataset" + "/" + name))
    for imagePath in imagePaths:
        photo = open(imagePath, "rb")
        bot.delete_message(config.ADMIN_ID, msg.message.message_id)
        bot.send_photo(config.ADMIN_ID, photo)
        continue


@bot.callback_query_handler(func=lambda message: message.data == "back")
def cmd_inline_back(msg):
    
    state = sw.get_current_state(msg.message.chat.id)
    if state == sw.LIST_OF_FACES:
        sw.set_current_state(msg.message.chat.id, sw.FACE_MNG)
        m = bot.edit_message_text(chat_id=msg.message.chat.id, 
                                  message_id=msg.message.message_id, 
                                  text=response_storage.face_mng, 
                                  reply_markup=utils.make_inline_keyboard("face_managment"))

    if state == sw.ACTION_WITH_FACE:
        sw.set_current_state(msg.message.chat.id, sw.LIST_OF_FACES)
        m = bot.edit_message_text(chat_id=msg.message.chat.id, 
                                  message_id=msg.message.message_id, 
                                  text=response_storage.list_of_faces, 
                                  reply_markup=utils.make_inline_keyboard("list_of_faces"))    


@bot.callback_query_handler(func=lambda message: message.data == "cancel")
def cmd_cancel(msg):
    state = sw.get_current_state(msg.message.chat.id)
    print("CANCELLLL " + state)
    if state == sw.SEND_NAME:
        m = bot.edit_message_text(chat_id=msg.message.chat.id, 
        	                      message_id=msg.message.message_id, 
        	                      text=utils.change_text_markdown(response_storage.canceled,
        	                      	                              "italic"), 
        	                      parse_mode="Markdown")

        sw.set_current_state(msg.message.chat.id, sw.START)

    if state == sw.SEND_PHOTO:
        if name != "":
            try:
                shutil.rmtree(DATASET_PATH + "/" + name)
            except:
                pass
            m = bot.edit_message_text(chat_id=msg.message.chat.id, 
                                      message_id=msg.message.message_id, 
                                      text=utils.change_text_markdown(response_storage.canceled, 
            	                      	                             "italic"), 
            	                      parse_mode="Markdown")
        photos_count = 0
        sw.set_current_state(msg.message.chat.id, sw.START)
    if state == sw.DELETE_FACE:
        m = bot.edit_message_text(chat_id=msg.message.chat.id,
        	                      message_id=msg.message.message_id,
        	                      text=utils.change_text_markdown(response_storage.canceled,
        	                      	                              "italic"),
        	                      parse_mode="Markdown")

        sw.set_current_state(msg.message.chat.id, sw.START)


@bot.callback_query_handler(func=lambda message:message.data == "confirm")
def cmd_confirm(msg):
    state = sw.get_current_state(msg.message.chat.id)
    if state == sw.SEND_PHOTO:
        encode_faces.add(name)
        m = bot.edit_message_text(chat_id=msg.message.chat.id,
        	                      message_id=msg.message.message_id,
        	                      text=utils.change_text_markdown(response_storage.face_added,
        	                      	                              "italic"),
        	                      parse_mode="Markdown")

        sw.set_current_state(msg.message.chat.id, sw.START)
        photos_count = 0

    if state == sw.DELETE_FACE:
        if name != "":
            shutil.rmtree(config.DATASET_PATH + name)
            encode_faces.delete(name)
            m = bot.edit_message_text(chat_id=msg.message.chat.id,
            	                      message_id=msg.message.message_id,
            	                      text=utils.change_text_markdown(response_storage.deleted,
            	                      	                              "italic"),
            	                      parse_mode="Markdown")

            sw.set_current_state(msg.message.chat.id, sw.START)


@bot.callback_query_handler(func=lambda message: True)
def inline_text(msg):
    global name

    state = sw.get_current_state(msg.message.chat.id)
    if state == sw.LIST_OF_FACES:
         m = bot.edit_message_text(chat_id=msg.message.chat.id,
         	                       message_id=msg.message.message_id,
         	                       text=response_storage.action_with_face + msg.data,
         	                       reply_markup=utils.make_inline_keyboard("action_with_face"))

         sw.set_current_state(msg.message.chat.id, sw.ACTION_WITH_FACE)
         name = msg.data


@bot.message_handler(func=lambda message: message.content_type == "text")
def text_msg(msg):
    global name
    state = sw.get_current_state(msg.chat.id)
    if state == sw.SEND_NAME:
        name = msg.text
        m = bot.send_message(msg.chat.id, response_storage.send_photo, 
        	                 reply_markup=utils.make_inline_keyboard("cancel"))

        sw.set_current_state(msg.chat.id, sw.SEND_PHOTO)

    if state == sw.SEND_PHOTO:
        if photos_count == 0:
            m = bot.send_message(msg.chat.id, response_storage.send_only_photo,
            	                 reply_markup=utils.make_inline_keyboard("cancel"))
        else:
            m = bot.send_message(msg.chat.id, response_storage.send_only_photo,
                                 reply_markup=confirm_board_inline("confirm_cancel"))


@bot.message_handler(content_types=["photo"])
def photo_msg(msg):
    global photos_count
    state = sw.get_current_state(msg.chat.id)

    if state == sw.SEND_PHOTO:
        file_info = bot.get_file(msg.photo[-1].file_id)
        download_file = bot.download_file(file_info.file_path)
        save_path = config.DATASET_PATH + name + "/" + str(photos_count)+ ".png"
        try:
            os.makedirs(config.DATASET_PATH + name)
        except OSError:
            pass
        with open(save_path, "wb") as photo:
            photo.write(download_file)

        if detect_face.run(save_path) is True:
            m = bot.send_message(msg.chat.id, 
            	                 response_storage.photo_accepted,
                                 reply_markup=utils.make_inline_keyboard("confirm_cancel"))
            photos_count += 1
        else:
            m = bot.send_message(msg.chat.id,
            	                 response_storage.face_not_detected,
            	                 reply_markup=utils.make_inline_keyboard("cancel"))

    
while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(15)
