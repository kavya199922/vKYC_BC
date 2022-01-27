import rekognition
import os
from dotenv import load_dotenv, dotenv_values
load_dotenv()
from mtcnn.mtcnn import MTCNN
default_initial_vars = {
    "page": "Home", 
    "signed_in": True, 
    "user_type": 'Customer', 
    "otp_sent": False, 
    'sub_page': 'Choose Bank', 
    'artifacts': {
        'pan_pdf': None,
        'aadhar_pdf': None,
        'AI_Detection':{
            'aadhar': {},
            'pan': {},
            'similarity_score_face': ""
        }
    },
    'mtcnn': MTCNN(),
    "rekog_object": rekognition.Rekognition(
            access_key=dotenv_values(".env").get('access_key_id'), 
            secret_key=dotenv_values(".env").get('secret_key_id'), 
            region=dotenv_values(".env").get('region'))
    }
