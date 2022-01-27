import os
from cv2 import error
os.environ["CUDA_VISIBLE_DEVICES"]="-1"

import streamlit as st
import pandas as pd
import rekognition
import default
from default import default_initial_vars

import base64
import cv2
from PIL import Image
import numpy as np

from videocomponent import videocomponent
import pypdfium2 as pdfium
import re

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

def extract_ocr(resp, key):
    filtered_detection = [detection["DetectedText"] for detection in resp["TextDetections"] if detection["Confidence"] > 90 and detection["Type"] == "LINE"]
    detected_keys = {}
    if key=="Aadhar":
        
        for word in filtered_detection:
            # match aadhar number regex
            if re.match(r'[0-9]{4} [0-9]{4} [0-9]{4}', word):
                detected_keys["aadhar_number"] = word
            if re.match(r'^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$', word):
                if "Issue" not in word or "DOB" in word:
                    detected_keys["dob_aadhar"] = word
    
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
    error_videoholder= st.empty()
    videoholder_video_stream = st.empty()
    videoholder_video_stream = videocomponent(my_input_value="", key=key)

    if videoholder_video_stream is not None:
        vid_obj = cv2.VideoCapture(videoholder_video_stream) 
        success = True
        face_detected_videoholder = False
        error_videoholder.info("Processing video...")
        while success:
            success, image = vid_obj.read()
            if success:
                faces = st.session_state["mtcnn"].detect_faces(image)
                if(len(faces)>0):
                    face_detected_videoholder = True
                    break
            else: 
                break
        if not face_detected_videoholder:
            error_videoholder.error("No face detected / Video invalid")
        else:
            
            error_videoholder.success("Video valid!")
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
                if st.button('Next', key='uploadscreenbtn'):
                    st.session_state['sub_page'] = 'Upload Docs'
            if st.session_state['sub_page'] == 'Upload Docs':
                st.subheader("Step 2: Upload Documents")

                Aadhar_file = st.file_uploader(
                    "Upload Aadhar as PDF", type=['pdf'], key='Aadhar')
                if Aadhar_file is not None:
                    st.session_state["artifacts"]["aadhar_pdf"] = Aadhar_file.getvalue()
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
                            st.session_state["artifacts"]["AI_Detection"]["aadhar"] = detected_keys
                    st.info("Aadhar uploaded")
                    
                PAN_file = st.file_uploader(
                        "Upload PAN as PDF", type=['pdf'], key='PAN')
                if PAN_file is not None:
                    st.session_state["artifacts"]["pan_pdf"] = PAN_file.getvalue()
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
                

                if st.button('Next', key='confirmation'):
                    st.session_state['sub_page'] = 'Confirmation'

            if st.session_state['sub_page'] == 'Confirmation':
                st.title('Confirm your Documents, Selfie and Video')
                st.subheader("Details")

                st.subheader("Verifier bank")
                st.write(st.session_state['artifacts']["verifier_bank"])

                st.subheader("Aadhar card PDF")
                base64_pdf = base64.b64encode(st.session_state["artifacts"]["aadhar_pdf"])
                pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

                st.subheader("PAN card PDF")
                base64_pdf = base64.b64encode(st.session_state["artifacts"]["pan_pdf"])
                pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                st.subheader("Selfie")
                st.image(st.session_state["artifacts"]["selfie"])
                st.subheader("Aadhar Video")
                st.video(st.session_state["artifacts"]["aadhar_video"])
                st.subheader("PAN Video")
                st.video(st.session_state["artifacts"]["pan_video"])
                st.subheader("AI Summary")
                st.write(st.session_state["artifacts"]["AI_Detection"])
                st.write("\n")


                if st.button('Confirm and Submit KYC', key='2'):    
                    st.session_state['sub_page'] = 'KYC Status'

            if st.session_state['sub_page'] == 'KYC Status':
                st.title('KYC submitted and pending for approval')

    else:
        st.error("Please Sign in")
