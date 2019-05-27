import pickle
import config


START = "0"
LIST_OF_FACES = "1"
SEND_NAME = "2"
SEND_PHOTO = "3"
FACE_MNG = "4"
ACTION_WITH_FACE = "5"
DELETE_FACE = "6"
UNAUTHORIZED = "-1"

CURRENT_STATE = "current"
PAST_STATE = "past"

def get_current_state(id):

    if id == config.ADMIN_ID:
        try:
            states = pickle.loads(open(config.STATES_PATH, "rb").read())     
            state = states[str(id) + "current"]
            return state
        except:

            data = {str(id) + CURRENT_STATE: START,
                    str(id) + PAST_STATE: START}

            update_db(data)
            return START
    else:
        return UNAUTHORIZED

def set_current_state(id, value):

    if id == config.ADMIN_ID:
        try:
            states = pickle.loads(open(config.STATES_PATH, "rb").read()) 
            past_state = states[str(id) + "current"]
            current_state = value

            data = {str(id) + CURRENT_STATE: current_state,
                    str(id) + PAST_STATE: past_state}

            update_db(data)
            return True
        except:
            return False
    else:
        return False

def update_db(data):
    db = open(config.STATES_PATH, "wb")
    db.write(pickle.dumps(data))
    db.close()