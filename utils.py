import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
import response_storage
import os
from imutils import paths
import subprocess
from subprocess import check_output, CalledProcessError
import pgrep

def check_camera_status():
    pids = pgrep.pgrep("-f recognition")
    if len(pids) == 1:
        return False 
    else:
        return True 

def make_keyboard(type):

    if type == "remove":
        keyboard = ReplyKeyboardRemove()

    if type == "main":
        keyboard = ReplyKeyboardMarkup()
        keyboard.add(response_storage.face_mng, response_storage.status)
        if check_camera_status() == True:
            keyboard.add(response_storage.camera_toggle_off)
        else:
            keyboard.add(response_storage.camera_toggle_on)
        keyboard.resize_keyboard = True

    return keyboard


def make_inline_keyboard(type):

    keyboard = InlineKeyboardMarkup()

    if type == "face_managment":
        keyboard.row(InlineKeyboardButton(response_storage.add_face, 
        	                              callback_data="add_face"))

        keyboard.row(InlineKeyboardButton(response_storage.list_of_faces, 
        	                              callback_data="list_of_faces"))
        
    if type == "list_of_faces":
        try:
            faces = list(paths.list_images("dataset"))
            for (i, face) in enumerate(faces):
                name = face.split(os.path.sep)[-2]
                keyboard.row(InlineKeyboardButton(name, callback_data=name))
        except:
            pass
        keyboard.row(InlineKeyboardButton(response_storage.back,
        	                              callback_data="back"))

    if type == "action_with_face":
        keyboard.row(InlineKeyboardButton(response_storage.delete_face,
        	                              callback_data="delete_face"))

        keyboard.row(InlineKeyboardButton(response_storage.get_photo,
        	                              callback_data="get_photo"))

        keyboard.row(InlineKeyboardButton(response_storage.back,
        	                              callback_data="back"))

    if type == "confirm_cancel":
        keyboard.row(InlineKeyboardButton(response_storage.confirm, 
        	                              callback_data="confirm"),
        	         InlineKeyboardButton(response_storage.cancel,
        	         	                  callback_data="cancel"))

    if type == "cancel":
        keyboard.add(InlineKeyboardButton(response_storage.cancel,
                                          callback_data="cancel"))

    return keyboard


def change_text_markdown(text, markdown):
    if markdown == "bold":
        return "*" + text + "*"
    if markdown == "italic":
        return "_" + text + "_"
