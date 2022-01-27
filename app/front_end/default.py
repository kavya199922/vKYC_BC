import rekognition
import os
from dotenv import load_dotenv, dotenv_values
load_dotenv()
from mtcnn.mtcnn import MTCNN
default_initial_vars = {
    # "page": "Home",
    "signed_in": False, 
    "user_type": 'Customer', 
    "otp_sent": False, 
    # 'sub_page': 'Choose Bank', 
    'artifacts': {
        'pan_pdf': None,
        'aadhar_pdf': None,
        "basic_info": {
        },
        'AI_Detection':{
            'aadhar': {},
            'pan': {},
            'similarity_score_face': ""
        }
    },
    'mtcnn': MTCNN(),
    "rekog_object": rekognition.Rekognition(
            access_key=os.environ.get('access_key_id'), 
            secret_key=os.environ.get('secret_key_id'), 
            region=os.environ.get('region')),
    "s3_object": rekognition.S3( access_key=os.environ.get('access_key_id'), 
            secret_key=os.environ.get('secret_key_id'), 
            region=os.environ.get('region'))
    }