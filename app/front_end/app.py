import streamlit as st
import pandas as pd
import rekognition
import default
from default import default_initial_vars
import os
from dotenv import load_dotenv
load_dotenv()
import cv2
os.environ["CUDA_VISIBLE_DEVICES"]="-1"


user_types = ['Customer', 'Bank Employee', 'Bank Admin']
banks_list = ['HDFC', 'ICICI']


print(default_initial_vars)
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
                verifier_bank = st.selectbox('Bank', banks_list)
                if st.button('Next', key='uploadscreenbtn'):
                    st.session_state['sub_page'] = 'Upload Docs'
            if st.session_state['sub_page'] == 'Upload Docs':
                st.subheader("Step 2: Upload Documents")
                PAN_file = st.file_uploader(
                    "Upload PAN as PDF", type=['pdf'], key='PAN')
                if PAN_file is not None:
                    print("PAN uploaded")

                Aadhar_file = st.file_uploader(
                    "Upload Aadhar as PDF", type=['pdf'], key='Aadhar')
                if Aadhar_file is not None:
                    print("Aadhar uploaded")

                if st.button('Next', key='1'):
                    st.session_state['sub_page'] = 'Take Selfie'

            if st.session_state['sub_page'] == 'Take Selfie':
                st.subheader("Step 3: Take Selfie")
                selfie_buffer = st.camera_input('Take a Selfie')
                if selfie_buffer is not None:
                    selfie = selfie_buffer.getvalue()
                    st.write(type(selfie))

                if st.button('Next', key='2'):
                    st.session_state['sub_page'] = 'Verify Aadhar and PAN'

            if st.session_state['sub_page'] == 'Verify Aadhar and PAN':
                st.subheader("Step 4: Verify Aadhar and PAN")
                st.markdown(
                    "Hold your Aadhar and PAN in front of the camera. Make sure your face, and the document is clearly visible.")
                st.markdown("**1. Aadhar**")
                frame_aadhar = st.empty()
                vid_obj = cv2.VideoCapture(0) 
                success = True
                while success:
                    success, image = vid_obj.read()
                    frame_aadhar.image(image, channels="BGR")
                    faces = st.session_state["mtcnn"].detect_faces(image)
                    print(len(faces))
                    resp = st.session_state["rekog_object"].client.detect_faces(Image={'Bytes': cv2.imencode('.jpg', image)[1].tobytes()})
                    print(resp)
                    
                    
                st.markdown("**2. PAN**")
                frame_pan = st.empty()

                if st.button('Next', key='confirmation'):
                    st.session_state['sub_page'] = 'Confirmation'

            if st.session_state['sub_page'] == 'Confirmation':
                st.title('Confirm your Documents, Selfie and Video')

                if st.button('Confirm and Submit KYC', key='2'):
                    st.session_state['sub_page'] = 'KYC Status'

            if st.session_state['sub_page'] == 'KYC Status':
                st.title('KYC submitted and pending for approval')

    else:
        st.error("Please Sign in")





# Rekognition object
# client = rekognition.Rekognition(access_key = os.environ.get('access_key_id'),secret_key=os.environ.get('secret_key_id'),region=os.environ.get('region'))
# print(client.access_key,client.secret_key)
# source_image = '/path/to/src/image'
# target_image = '/path/to/target/image'
# image_path = '/path/to/image'
# client.compare_faces(src_image,target_image)
# client.detect_faces(image_path)
# client.detect_text(image_path)
