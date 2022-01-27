import os
from cv2 import error
from uuid import uuid1
from validators import uuid
os.environ["CUDA_VISIBLE_DEVICES"]="-1"

import streamlit as st
import pandas as pd
import rekognition
import default
from default import default_initial_vars
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
import requests

import base64
import cv2
from PIL import Image
import numpy as np

from videocomponent import videocomponent
import pypdfium2 as pdfium
import re
from io import StringIO, BytesIO

user_types = ['Customer', 'Bank Employee']
banks_list = ['HDFC', 'ICICI']

def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

def extract_ocr(resp, key, name_match=True):
    if len(resp["TextDetections"])==0:
        st.error("Invalid pdf/image")
        return {}
    
    filtered_detection = [detection["DetectedText"] for detection in resp["TextDetections"] if detection["Confidence"] > 90 and detection["Type"] == "LINE"]
    filtered_detection_word = [detection["DetectedText"] for detection in resp["TextDetections"] if detection["Confidence"] > 90 and detection["Type"] == "WORD"]
    detected_keys = {}
    if key=="Aadhar":
                
        for word in filtered_detection:
            # match aadhar number regex
            if re.match(r'[0-9]{4} [0-9]{4} [0-9]{4}', word):
                detected_keys["aadhar_number"] = word
            if re.match(r'^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$', word):
                if "Issue" not in word or "DOB" in word:
                    detected_keys["dob_aadhar"] = word

        # Name match validation
        if name_match:
            given_name_words = [word.lower() for word in st.session_state["artifacts"]["basic_info"]["full_name"].split()]
            filtered_detection_word = [word.lower() for word in filtered_detection_word]
            if len(list(set(filtered_detection_word) & set(given_name_words))) == len(given_name_words):
                detected_keys["aadhar_name_match"] = True
            else:
                detected_keys["aadhar_name_match"] = False

    
    if key=="PAN":
        for word in filtered_detection:
            # match pan number regex
            if re.match(r'[0-9A-Z]{10}', word):
                detected_keys["pan_number"] = word
            if re.match(r'^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$', word):
                if "Issue" not in word or "DOB" in word:
                    detected_keys["dob_pan"] = word

    return detected_keys

def videoRecPlay(key):
    response = st.empty()
    response = videocomponent(my_input_value="", key=key)
    error_videoholder= st.empty()

    if response is not None:
        videoholder_video_stream = response[0]
        screenshot = response[1]

        face_detected_videoholder = False
        error_videoholder.info("Processing video...")
        base64_decoded = base64.b64decode(screenshot.replace("data:image/png;base64", ""))
        image = Image.open(BytesIO(base64_decoded))
        # faces = st.session_state["mtcnn"].detect_faces(np.array(image))
        faces = []
        if(len(faces)>0) or True:
            face_detected_videoholder = True
        if not face_detected_videoholder:
            error_videoholder.error("No face detected / Video invalid")
        else:
            resp = st.session_state["rekog_object"].client.detect_text(Image={'Bytes': cv2.imencode('.jpg', np.array(image))[1].tobytes()})
            print(resp)
            detected_keys = extract_ocr(resp, key, False)
            print(detected_keys)
            if key =="PAN":
                if "pan_number" in detected_keys.keys():
                    error_videoholder.success("Video valid!")
                else:
                    error_videoholder.error("Captured Image not clear enough / invalid")
            if key =="Aadhar":
                if "aadhar_number" in detected_keys.keys():
                    error_videoholder.success("Video valid!")
                else:
                    error_videoholder.error("Captured Image not clear enough / invalid")
            
            return videoholder_video_stream
    return None

for key in default_initial_vars:
    if key not in st.session_state:
        st.session_state[key] = default_initial_vars[key]


if st.sidebar.button("Sign In"):
    st.session_state['page'] = 'Sign In'

if st.sidebar.button("Sign Up"):
    st.session_state['page'] = 'Sign Up'

if st.sidebar.button("Home"):
    st.session_state['page'] = 'Home'

if st.session_state['page'] == 'Sign Up':
    user_type = st.selectbox('User Type', user_types)
    if user_type == 'Customer':
        st.title("KYC Customer Sign Up")
        mobile_num = st.text_input("Mobile Number")

        if st.button("Send OTP"):
            st.session_state['otp_sent'] = True

        if st.session_state['otp_sent']:
            otp = st.text_input("OTP")
            password = st.text_input("Password", type='password')
            retype_password = st.text_input(
                "Confirm Password", type='password')

            if st.button("Sign Up", key='1'):
                private_key = 'xxx'
                st.info('Your private key is ' + private_key + \
                        '. Note down and use while logging in.')


    if user_type == 'Bank Employee':
        st.title("KYC Bank Employee Sign Up")

        employee_name = st.text_input('Name')
        bank_name = st.selectbox('Bank', banks_list)
        emp_email_id = st.text_input("Email ID")

        if st.button("Send OTP"):
            st.session_state['otp_sent'] = True

        if st.session_state['otp_sent']:
            otp = st.text_input("OTP")
            password = st.text_input("Password", type='password')
            retype_password = st.text_input(
                "Confirm Password", type='password')

            if st.button("Sign Up", key='2'):
                private_key = 'xxx'
                st.info('Your private key is ' + private_key + \
                        '. Note down and use while logging in.')


if st.session_state['page'] == 'Sign In':

    user_type = st.selectbox('User Type', user_types)
    st.session_state['user_type'] = user_type

    if user_type == 'Customer':
        st.title("KYC Customer Sign In")

        mobile_num = st.text_input("Mobile Number")
        password = st.text_input("Password", type='password')
        password = st.text_input("Private Key")

        if st.button("Sign In", key='1'):
            st.success("Signed In successfully")
            st.session_state['signed_in'] = True

    if user_type == 'Bank Employee':
        st.title("KYC Employee Sign In")

        email_id = st.text_input("Email ID")
        password = st.text_input("Password", type='password')
        password = st.text_input("Private Key")

        if st.button("Sign In", key='2'):
            st.success("Signed In successfully")
            st.session_state['signed_in'] = True

if st.session_state['page'] == 'Home':

    if st.session_state['signed_in']:
        if st.session_state['user_type'] == 'Customer':
            st.title("KYC Customer Upload Docs")
            if st.session_state['sub_page'] == 'Choose Bank':
                st.subheader("Step 1: Choose verifier bank")
                st.session_state["artifacts"]["verifier_bank"] = st.selectbox('Bank', banks_list)
                st.session_state["artifacts"]["basic_info"]["full_name"] = st.text_input("Full Name (As per Aadhar)")
                if st.button('Next', key='uploadscreenbtn'):
                    st.session_state['sub_page'] = 'Upload Docs'
            if st.session_state['sub_page'] == 'Upload Docs':
                st.subheader("Step 2: Upload Documents")

                Aadhar_file = st.file_uploader(
                    "Upload Aadhar as PDF", type=['pdf'], key='Aadhar')
                if Aadhar_file is not None:
                    st.session_state["artifacts"]["aadhar_pdf"] = Aadhar_file
                    with pdfium.PdfContext(Aadhar_file.getvalue()) as pdf:
                        pil_image = pdfium.render_page(
                            pdf,
                            page_index = 0,
                            scale = 1,
                            rotation = 0,
                            colour = 0xFFFFFFFF,
                            annotations = True,
                            greyscale = False,
                            optimise_mode = pdfium.OptimiseMode.none,
                        )
                        faces = st.session_state["mtcnn"].detect_faces(np.array(pil_image))
                        if(len(faces)==0):
                            st.error("No face detected in Aadhar")
                        else:
                            pil_image.save("tmp/aadhar.png")
                            resp = st.session_state["rekog_object"].client.detect_text(Image={'Bytes': cv2.imencode('.jpg', np.array(pil_image))[1].tobytes()})
                            detected_keys = extract_ocr(resp, "Aadhar")
                            if not detected_keys["aadhar_name_match"]:
                                st.error("Name not matched with Aadhar")
                            st.session_state["artifacts"]["AI_Detection"]["aadhar"] = detected_keys
                    st.info("Aadhar uploaded")
                    
                PAN_file = st.file_uploader(
                        "Upload PAN as PDF", type=['pdf'], key='PAN')
                if PAN_file is not None:
                    st.session_state["artifacts"]["pan_pdf"] = PAN_file
                    with pdfium.PdfContext(PAN_file.getvalue()) as pdf:
                        pil_image = pdfium.render_page(
                            pdf,
                            page_index = 0,
                            scale = 1,
                            rotation = 0,
                            colour = 0xFFFFFFFF,
                            annotations = True,
                            greyscale = False,
                            optimise_mode = pdfium.OptimiseMode.none,
                        )
                        pil_image.save("tmp/pan.png")
                        resp = st.session_state["rekog_object"].client.detect_text(Image={'Bytes': cv2.imencode('.jpg', np.array(pil_image))[1].tobytes()})
                        detected_keys = extract_ocr(resp, "PAN")
                        st.session_state["artifacts"]["AI_Detection"]["PAN"] = detected_keys
                        
                    st.info("PAN uploaded")

                if PAN_file is not None and Aadhar_file is not None:
                    if st.button('Next', key='1'):
                        st.session_state['sub_page'] = 'Take Selfie'

            if st.session_state['sub_page'] == 'Take Selfie':
                st.subheader("Step 3: Take Selfie")
                selfie_buffer = st.camera_input('Take a Selfie')
                if selfie_buffer is not None:
                    img = Image.open(selfie_buffer)
                    img.save("tmp/selfie.png")
                    img_array = np.array(img)
                    image_bytes = selfie_buffer.getvalue()
                    faces = st.session_state["mtcnn"].detect_faces(img_array)
                    if(len(faces)==0):
                        st.error("No face detected")
                    else:                    
                        source_image_bytes = open("tmp/aadhar.png", "rb").read()
                        target_image_bytes = open("tmp/selfie.png", "rb").read()
                        resp = st.session_state["rekog_object"].client.compare_faces(SimilarityThreshold=0.7,SourceImage={'Bytes': source_image_bytes},TargetImage={'Bytes': target_image_bytes})
                        print(resp)
                        if not len(resp['FaceMatches']):
                            st.error("Face not matching with Aadhar")
                        else:
                            st.session_state["artifacts"]["selfie"] = target_image_bytes
                            st.session_state["artifacts"]["AI_Detection"]["similarity_score_face"] = resp["FaceMatches"][0]["Similarity"]
                            st.success("Face matching with Aadhar successful")
                        
                            if st.button('Next', key='2'):
                                st.session_state['sub_page'] = 'Verify Aadhar and PAN'

            if st.session_state['sub_page'] == 'Verify Aadhar and PAN':
                st.subheader("Step 4: Verify Aadhar and PAN")
                st.markdown(
                    "Hold your Aadhar and PAN in front of the camera. Make sure your face, and the document is clearly visible.")
                st.markdown("**1. Aadhar**")
                st.session_state["artifacts"]["aadhar_video"] = videoRecPlay("Aadhar")
                    
                st.markdown("**2. PAN**")
                st.session_state["artifacts"]["pan_video"] = videoRecPlay("PAN")
                

                if st.button('Next', key='location'):
                    st.session_state['sub_page'] = 'Location'

            if st.session_state['sub_page'] == 'Location':
                st.title('Location')
                st.markdown("We need your location to verify your identity")
                loc_button = Button(label="Get Location")
                loc_button.js_on_event("button_click", CustomJS(code="""
                    navigator.geolocation.getCurrentPosition(
                        (loc) => {
                            document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
                        }
                    )
                    """))
                result = streamlit_bokeh_events(
                    loc_button,
                    events="GET_LOCATION",
                    key="get_location",
                    refresh_on_update=False,
                    override_height=75,
                    debounce_time=0)
                
                if result is not None:
                    latlng = result["GET_LOCATION"]
                    print(latlng)
                    x = requests.get("https://nominatim.openstreetmap.org/reverse", {"lat": latlng["lat"], "lon": latlng["lon"], "format": "json"})
                    st.write("Currently we find you nearby: ")
                    st.session_state["artifacts"]["location"] = x.json()["display_name"]
                    st.markdown("**"+st.session_state["artifacts"]["location"]+"**")
                    st.write("\n")
                    if st.button('Confirm', key='confirmation'):
                        st.session_state['sub_page'] = 'Confirmation'

            if st.session_state['sub_page'] == 'Confirmation':
                st.title('Confirm your Documents, Selfie and Video')
                st.subheader("Details")
                
                st.subheader("Full name")
                st.write(st.session_state["artifacts"]["basic_info"]["full_name"] + " \u2705") 
            
                st.subheader("Verifier bank")
                st.write(st.session_state['artifacts']["verifier_bank"])

                st.subheader("Aadhar card PDF")
                base64_pdf =  base64.b64encode(st.session_state["artifacts"]["aadhar_pdf"].read()).decode('utf-8')
                pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

                st.subheader("PAN card PDF")
                base64_pdf = base64.b64encode(st.session_state["artifacts"]["pan_pdf"].read()).decode('utf-8')
                pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                st.subheader("Selfie")
                st.image(st.session_state["artifacts"]["selfie"])

                st.subheader("Aadhar Video")
                st.video(base64.b64decode(st.session_state["artifacts"]["aadhar_video"].replace("data:video/webm;base64","")))

                st.subheader("PAN Video")
                st.video(base64.b64decode(st.session_state["artifacts"]["pan_video"].replace("data:video/webm;base64","")))

                st.subheader("Location")
                st.write(st.session_state["artifacts"]["location"])

                st.subheader("AI Summary")
                st.write(st.session_state["artifacts"]["AI_Detection"])
                st.write("\n")

            


                if st.button('Confirm and Submit KYC', key='2'):    
                    data_on_bc = {

                    }

                    st.info("Uploading data")
                    BUCKET_NAME = "uploads.blockchain-geeks-askv"
                    upload_id = str("test")
                    s3 = st.session_state["s3_object"].session.resource("s3")
                    s3_client = st.session_state["s3_object"].client
                    allowed_banks = [
                        {
                        "bank_name": st.session_state['artifacts']["verifier_bank"],
                        "presigned_url":{
                            "aadhar_pdf": "",
                            "pan_pdf": "",
                            "selfie": "",
                            "aadhar_video": "",
                            "pan_video": "",
                            }
                        }
                    ]

                    def upload_data(keyfile, body):
                        global data_on_bc, allowed_banks, upload_id
                        filename = upload_id + "/" + keyfile
                        object = s3.Object(BUCKET_NAME, filename)
                        result = object.put(Body=body)
                        url = s3_client.generate_presigned_url(ClientMethod='get_object', 
                                Params={'Bucket': BUCKET_NAME, 'Key': filename},
                                ExpiresIn=36000)
                        data_on_bc[keyfile] = url.split("?")[0]
                        allowed_banks[0]["presigned_url"][keyfile] = {}
                        for qp in url.split("?")[1].split("&"):
                            allowed_banks[0]["presigned_url"][keyfile][qp.split("=")[0]] = qp.split("=")[1]
                    
                    upload_data("aadhar_pdf", st.session_state["artifacts"]["aadhar_pdf"].getvalue())
                    upload_data("pan_pdf", st.session_state["artifacts"]["pan_pdf"].getvalue())
                    upload_data("aadhar_video", base64.b64decode(st.session_state["artifacts"]["aadhar_video"].replace("data:video/webm;base64","")))
                    upload_data("pan_video", base64.b64decode(st.session_state["artifacts"]["pan_video"].replace("data:video/webm;base64","")))
                    upload_data("selfie", st.session_state["artifacts"]["selfie"])

                    data_on_bc["location"] = st.session_state["artifacts"]["location"]
                    data_on_bc["verifier_bank"] = st.session_state["artifacts"]["verifier_bank"]
                    data_on_bc["AI_Detection"] = st.session_state["artifacts"]["AI_Detection"]
                    data_on_bc["fullname"] = st.session_state["artifacts"]["basic_info"]["full_name"]

                    st.write(data_on_bc)
                    st.write(allowed_banks)

                    # st.session_state['sub_page'] = 'KYC Status'

            if st.session_state['sub_page'] == 'KYC Status':
                st.title('KYC submitted and pending for approval')

    else:
        st.error("Please Sign in")
