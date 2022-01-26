import rekognition
import os
from dotenv import load_dotenv
load_dotenv()
from mtcnn.mtcnn import MTCNN

default_initial_vars = {
    "page": "Home", 
    "signed_in": True, 
    "user_type": 'Customer', 
    "otp_sent": False, 
    'sub_page': 'Verify Aadhar and PAN', 
    'mtcnn': MTCNN(),
    "rekog_object": rekognition.Rekognition(
            access_key=os.environ.get('access_key_id'), 
            secret_key=os.environ.get('secret_key_id'), 
            region=os.environ.get('region'))
    }
