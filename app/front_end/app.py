import streamlit as st
import pandas as pd
import rekognition
import default
from default import default_initial_vars
import os
from dotenv import load_dotenv
load_dotenv()
import cv2
import base64
os.environ["CUDA_VISIBLE_DEVICES"]="-1"


def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


user_types = ['Customer', 'Bank Employee']
banks_list = ['HDFC', 'ICICI', 'Kotak']
user_table = pd.DataFrame({
                'Name' : ['Kavya', 'Skanda', 'Vishnu'],
                'Mobile Number' : ['927484982', '973729393', '937378484'],
                'Status' : ['Approved', 'Pending', 'Pending']
            })
session_params = [
    'page', 'user_type', 'sub_page', 'otp_sent', 'signed_in', 'current_customer',
    'mtcnn', 'rekog_object'
]


print(default_initial_vars)
for key in default_initial_vars:
    if key not in st.session_state:
        st.session_state[key] = default_initial_vars[key]


# Default Page
if 'page' not in st.session_state :
    if st.session_state['signed_in'] :
        st.session_state['page'] = 'Home'
    else :
        st.session_state['page'] = 'Sign In'

# Sidebar
if st.sidebar.button("Sign In"):
    st.session_state['page'] = 'Sign In'

if st.sidebar.button("Sign Up"):
    st.session_state['page'] = 'Sign Up'   

if st.sidebar.button("Home"):
    st.session_state['page'] = 'Home'
    if 'sub_page' not in st.session_state :
        if st.session_state['user_type'] == 'Customer' :
            st.session_state['sub_page'] = 'Choose Bank'
        if st.session_state['user_type'] == 'Bank Employee' :
            st.session_state['sub_page'] = 'List View'

if st.sidebar.button("KYC Access Requests"):
    st.session_state['page'] = 'Requests'

if st.sidebar.button("Logout"):
    st.session_state['page'] = 'Logout'
    if st.session_state['signed_in'] :
        st.session_state = default_initial_vars.copy()
        st.session_state['page'] = 'Logout'
        st.title("You have successfully logged out")
    else :
        st.error("Please Sign in")


# Sign Up
if st.session_state['page'] == 'Sign Up':
    user_type = st.selectbox('User Type', user_types)

    # Customer
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

    # Employee
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

# Sign In
if st.session_state['page'] == 'Sign In':

    user_type = st.selectbox('User Type', user_types)
    st.session_state['user_type'] = user_type

    # Customer
    if user_type == 'Customer':
        st.title("KYC Customer Sign In")

        mobile_num = st.text_input("Mobile Number")
        password = st.text_input("Password", type='password')
        private_key = st.text_input("Private Key")

        if st.button("Sign In", key='1'):
            st.success("Signed in successfully. Go to \"Home\"")
            st.session_state['signed_in'] = True

    # Employee
    if user_type == 'Bank Employee':
        st.title("KYC Bank Employee Sign In")

        email_id = st.text_input("Email ID")
        password = st.text_input("Password", type='password')
        private_key = st.text_input("Private Key")

        if st.button("Sign In", key='2'):
            st.success("Signed in successfully. Go to \"Home\"")
            st.session_state['signed_in'] = True


# Home
if st.session_state['page'] == 'Home':

    if st.session_state['signed_in']:
        # Customer
        if st.session_state['user_type'] == 'Customer':
            st.title("KYC Customer Home")

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
                # while success:
                #     success, image = vid_obj.read()
                #     frame_aadhar.image(image, channels="BGR")
                #     faces = st.session_state["mtcnn"].detect_faces(image)
                #     print(len(faces))
                #     resp = st.session_state["rekog_object"].client.detect_faces(Image={'Bytes': cv2.imencode('.jpg', image)[1].tobytes()})
                #     print(resp)
                    
                    
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

        # Employee
        if st.session_state['user_type'] == 'Bank Employee':
            st.title("KYC List")
            # if st.session_state['sub_page'] == 'List View' :
            if True :

                colms = st.columns((1, 2, 2, 1, 1))
                fields = ['##### S.No', '##### Name', '##### Mobile Number', '##### Verified', '##### Action']

                for col, field_name in zip(colms, fields):
                    # header
                    col.write(field_name)
                st.write("\n")

                for x, mobile_num in enumerate(user_table['Name']):
                    col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
                    col1.write(x)
                    col2.write(user_table['Name'][x])
                    col3.write(user_table['Mobile Number'][x])
                    status = user_table['Status'][x]
                    col4.write(status) # flexible type of button
                    # button_type = "Unblock" if verified else "Block"
                    button_phold = col5.empty()  # create a placeholder
                    if status == 'Pending' :
                        do_action = button_phold.button("View", key=x)
                        if do_action :
                            st.session_state['sub_page'] = 'Detailed View'
                            st.session_state['current_customer'] = {
                                "ID" : x,
                                "Mobile Number" : user_table['Mobile Number'][x],
                                "Name" : user_table['Name'][x]
                            }

            st.components.v1.html("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """)
            
            if st.session_state['sub_page'] == 'Detailed View' :
                # if st.button('Back') :
                #     st.session_state['sub_page'] = 'List View'
                if 'current_customer' in st.session_state :
                    st.subheader("Details")
                    st.write(st.session_state['current_customer'])
                    st.subheader("Aadhar card PDF")
                    displayPDF('/home/vishnupriyaa/Desktop/Installations and Steps/HiveInstallation.pdf')
                    st.subheader("PAN card PDF")
                    displayPDF('/home/vishnupriyaa/Desktop/Installations and Steps/HiveInstallation.pdf')
                    st.subheader("Selfie")
                    st.image("/home/vishnupriyaa/Desktop/Laptop/Pictures/Screenshots 1/Screenshot (178).png")
                    st.subheader("Video")
                    st.video("/home/vishnupriyaa/Desktop/AWS Cloud Synapt Demo Videos/Login.mp4")
                    st.subheader("Findings")
                    st.write({
                        "Face match" : "80%",
                        "Address match" : True,
                        "Phone number match" : True
                    })
                    st.write("\n")

                    c1, c2 = st.columns((3,3))
                    if c1.button("Approve KYC") :
                        user_table["Status"][st.session_state['current_customer']['ID']] = 'Approved'
                        st.session_state['sub_page'] = 'List View'
                    if c2.button("Reject KYC") :
                        user_table["Status"][st.session_state['current_customer']['ID']] = 'Rejected'
                        st.session_state['sub_page'] = 'List View'

    else:
        st.error("Please Sign in")

# Requests
if st.session_state['page'] == 'Requests':

    if st.session_state['signed_in']:
        # Customer
        if st.session_state['user_type'] == 'Customer':
            st.title("KYC Access Requests")

            requests_table = pd.DataFrame({
                "Bank" : ["ICICI", "Kotak"],
                "Status" : ["Approved", "Pending"]
            })
            colms = st.columns((1, 2, 2, 1, 1))
            fields = ['##### S.No', '##### Bank', '##### Request Status', '##### Action']

            for col, field_name in zip(colms, fields):
                # header
                col.write(field_name)
            st.write("\n")

            for x, bank in enumerate(requests_table['Bank']):
                col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
                col1.write(x)
                col2.write(requests_table['Bank'][x])
                status = requests_table['Status'][x]
                col3.write(status) # flexible type of button
                # button_type = "Unblock" if verified else "Block"
                button_phold1 = col4.empty()  # create a placeholder
                button_phold2 = col5.empty()  # create a placeholder
                if status == 'Pending' :
                    do_action1 = button_phold1.button("Approve", key=x)
                    do_action2 = button_phold2.button("Reject", key=x)
                    if do_action1 :
                        st.write(x,"Approved")
                    if do_action2 :
                        st.write(x,"Rejected")

        # Employee
        if st.session_state['user_type'] == 'Bank Employee':
            st.title("KYC Access Requests")

            request_mobile_num = st.text_input("Mobile Number")
            if st.button("Send Request") :
                st.success("Request has been sent")

            st.write("\n\n")
            st.subheader("Request List")
            requests_table = pd.DataFrame({
                "Name" : ["Skanda", "Kavya", "Vishnu"],
                "Mobile Number" : ["937282399", "9747378822", "977647387"],
                "Status" : ["Approved", "Rejected", "Pending"]
            })
            colms = st.columns((1, 2, 2, 2))
            fields = ['##### S.No', '##### Name', '##### Mobile Number', '##### Request Status']

            for col, field_name in zip(colms, fields):
                # header
                col.write(field_name)
            st.write("\n")

            for x, bank in enumerate(requests_table['Name']):
                col1, col2, col3, col4 = st.columns((1, 2, 2, 2))
                col1.write(x)
                col2.write(requests_table['Name'][x])
                col3.write(requests_table['Mobile Number'][x])
                col4.write(requests_table['Status'][x])

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
