import streamlit as st
import pandas as pd
# import rekognition
# from dotenv import load_dotenv
import os
# load_dotenv()

user_types = ['Customer', 'Bank Employee', 'Bank Admin']
banks_list = ['HDFC', 'ICICI']

if 'page' not in st.session_state :
 st.session_state['page'] = 'Sign In'

if st.sidebar.button("Sign In") :
    st.session_state['page'] = 'Sign In'
    st.session_state['user_type'] = ''
    if 'signed_in' not in st.session_state :
        st.session_state['signed_in'] = False

if st.sidebar.button("Sign Up") :
    st.session_state['page'] = 'Sign Up'
    st.session_state['otp_sent'] = False

if st.sidebar.button("Home") :
    st.session_state['page'] = 'Home'
    if 'sub_page' not in st.session_state :
        st.session_state['sub_page'] = 'Upload Docs'

if st.session_state['page'] == 'Sign Up' :

    user_type = st.selectbox('User Type', user_types)

    if user_type == 'Customer' :
        st.title("KYC Customer Sign Up")

        if 'otp_sent' not in st.session_state :
            st.session_state['otp_sent'] = False
        mobile_num = st.text_input("Mobile Number")

        if st.button("Send OTP") :
            st.session_state['otp_sent'] = True
        
        if st.session_state['otp_sent'] :
            otp = st.text_input("OTP")
            password = st.text_input("Password", type='password')
            retype_password = st.text_input("Confirm Password", type='password')

            if st.button("Sign Up", key='1') :
                private_key = 'xxx'
                st.info('Your private key is ' + private_key + '. Note down and use while logging in.')


    if user_type == 'Bank Employee' :
        st.title("KYC Bank Employee Sign Up")

        if 'otp_sent' not in st.session_state :
            st.session_state['otp_sent'] = False
        employee_name = st.text_input('Name')
        bank_name = st.selectbox('Bank', banks_list)
        emp_email_id = st.text_input("Email ID")

        if st.button("Send OTP") :
            st.session_state['otp_sent'] = True
        
        if st.session_state['otp_sent'] :
            otp = st.text_input("OTP")
            password = st.text_input("Password", type='password')
            retype_password = st.text_input("Confirm Password", type='password')

            if st.button("Sign Up", key='2') :
                private_key = 'xxx'
                st.info('Your private key is ' + private_key + '. Note down and use while logging in.')


if st.session_state['page'] == 'Sign In' :

    user_type = st.selectbox('User Type', user_types)
    st.session_state['user_type'] = user_type

    if user_type == 'Customer' :
        st.title("KYC Customer Sign In")

        mobile_num = st.text_input("Mobile Number")
        password = st.text_input("Password", type='password')
        password = st.text_input("Private Key")

        if st.button("Sign In", key='1') :
            st.success("Signed In successfully")
            st.session_state['signed_in'] = True

    if user_type == 'Bank Employee' :
        st.title("KYC Employee Sign In")

        email_id = st.text_input("Email ID")
        password = st.text_input("Password", type='password')
        password = st.text_input("Private Key")

        if st.button("Sign In", key='2') :
            st.success("Signed In successfully")
            st.session_state['signed_in'] = True

if st.session_state['page'] == 'Home' :

    if st.session_state['signed_in'] :
        if st.session_state['user_type'] == 'Customer' :
            if st.session_state['sub_page'] == 'Upload Docs' :
                PAN_file = st.file_uploader("Upload PAN as PDF", type=['pdf'], key='PAN')
                if PAN_file is not None:
                    #  # To read file as bytes:
                    #  bytes_data = uploaded_file.getvalue()
                    #  st.write(bytes_data)

                    #  # To convert to a string based IO:
                    #  stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                    #  st.write(stringio)

                    #  # To read file as string:
                    #  string_data = stringio.read()
                    #  st.write(string_data)

                    #  # Can be used wherever a "file-like" object is accepted:
                    #  dataframe = pd.read_csv(uploaded_file)
                    #  st.write(dataframe)

                    print("PAN uploaded")

                Aadhar_file = st.file_uploader("Upload Aadhar as PDF", type=['pdf'], key='Aadhar')
                if Aadhar_file is not None:
                    print("Aadhar uploaded")

                if st.button('Next', key='1') :
                    st.session_state['sub_page'] = 'Take Selfie'

            if st.session_state['sub_page'] == 'Take Selfie' :
                selfie = st.camera_input('Take a Selfie')
                video = st.camera_input('Take a Video')

                if st.button('Next', key='2') :
                    st.session_state['sub_page'] = 'Confirmation'

            if st.session_state['sub_page'] == 'Confirmation' :
                st.title('Confirm your Documents, Selfie and Video')

                if st.button('Confirm and Submit KYC', key='2') :
                    st.session_state['sub_page'] = 'KYC Status'

            if st.session_state['sub_page'] == 'KYC Status' :
                st.title('KYC sumbitted and pending for approval')

    else :
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