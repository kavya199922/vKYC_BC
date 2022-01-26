import rekognition
import os
from dotenv import load_dotenv
load_dotenv()
from mtcnn.mtcnn import MTCNN

default_initial_vars = {
#     "page": "Sign In", 
    "signed_in": False, 
    "user_type": 'Customer', 
    "otp_sent": False, 
#     'sub_page': 'Choose Bank', 
    'mtcnn': MTCNN(),
    "rekog_object": rekognition.Rekognition(
            access_key=os.environ.get('access_key_id'), 
            secret_key=os.environ.get('secret_key_id'), 
            region=os.environ.get('region'))
    }
