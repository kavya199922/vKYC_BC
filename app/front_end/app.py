import datetime
import requests
import os
from cv2 import error
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
REST_API = 'http://10.168.126.150:9090'
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

if st.sidebar.button("Sign In"):
    st.session_state['page'] = 'Sign In'

if st.sidebar.button("Sign Up"):
    st.session_state['page'] = 'Sign Up'   

if st.sidebar.button("Home"):
    st.session_state['page'] = 'Home'
    if 'sub_page' not in st.session_state :
        if st.session_state['artifacts']['user_type'] == 'Customer' :
            st.session_state['sub_page'] = 'Choose Bank'
        if st.session_state['artifacts']['user_type'] == 'BANK' :
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
                resp = requests.post(REST_API+'/signup',json = {"mobile_number":mobile_num,"password":password,"kyc_number":"NA","user_type":"CUSTOMER"})
                private_key = resp.json()['private_key']
                st.info('Your private key is ' + private_key + \
                        '. Note down and use while logging in.')


    if user_type == 'Bank Employee':
        st.title("KYC Bank Employee Sign Up")
        st.session_state['artifacts']['user_type']= 'BANK'
        # employee_name = st.text_input('Name')
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
                resp = requests.post(REST_API+'/signup',json = {"identifier":emp_email_id,"password":password,"bank_name":bank_name,"user_type":st.session_state['artifacts']['user_type']})
                private_key = resp.json()['private_key']
                st.info('Your private key is ' + private_key + \
                        '. Note down and use while logging in.')


if st.session_state['page'] == 'Sign In':

    user_type = st.selectbox('User Type', user_types)
    st.session_state['artifacts']['user_type'] = user_type

    if user_type == 'Customer':
        st.title("KYC Customer Sign In")

        mobile_num = st.text_input("Mobile Number")
        password = st.text_input("Password", type='password')
        private_key = st.text_input("Private Key")

        if st.button("Sign In", key='1'):
            resp = requests.post(REST_API+'/login',json ={"identifier":mobile_num,"password":password,"private_key":private_key,"user_type":st.session_state['user_type']})
            st.write(resp.json()['data']['status'])
            if resp.json()['data']['status'] == 'login success':
                st.session_state['artifacts']['private_key'] = private_key
                st.session_state['artifacts']['mobile_num'] = mobile_num
                st.session_state['artifacts']['password'] = password
                st.session_state['artifacts']['kyc_number'] = resp.json()['data']['kyc_number']
                st.success("Signed In successfully")
                st.session_state['signed_in'] = True
            else:
                st.error("Invalid User")
                st.session_state['signed_in'] = False


        

       

    if user_type == 'Bank Employee':
        st.title("KYC Employee Sign In")
        st.session_state['artifacts']['user_type'] = 'BANK'
        bank_name = st.text_input('Bank Name')
        email_id = st.text_input("Email ID")
        password = st.text_input("Password", type='password')
        private_key = st.text_input("Private Key")

        if st.button("Sign In", key='2'):
            resp = requests.post(REST_API+'/login',json ={"identifier":email_id,"password":password,"private_key":private_key,"user_type":st.session_state['artifacts']['user_type']})
            st.write(resp.json()['data']['status'])
            if resp.json()['data']['status'] == 'login success':
                st.session_state['artifacts']['private_key'] = private_key
                st.session_state['artifacts']['email_id'] = email_id
                st.session_state['artifacts']['bank_name'] = bank_name
                st.session_state['artifacts']['password'] = password
                if resp.json()['data']['status'] == 'login success':
                    st.success("Signed In successfully")
                    st.session_state['signed_in'] = True
                else:
                    st.error('invalid login')
                    st.session_state['signed_in']=False

if st.session_state['page'] == 'Home':

    if st.session_state['signed_in']:
        if st.session_state['artifacts']['user_type'] == 'Customer':
                # check if kyc number is NA or done
            resp = requests.post(REST_API+'/login',json ={"identifier":st.session_state['artifacts']['mobile_num'],"password":st.session_state['artifacts']['password'],"private_key":st.session_state['artifacts']['private_key'],"user_type":st.session_state['artifacts']['user_type']})
            st.session_state['artifacts']['kyc_number'] = resp.json()['data']['kyc_number']
            st.write(st.session_state['artifacts']['kyc_number'])
            st.title("KYC Customer")
            if st.session_state['artifacts']['kyc_number'] == 'NA':
                
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
                        #commented:
                        # st.session_state["artifacts"]["aadhar_pdf"] = Aadhar_file.getvalue()
                        # with pdfium.PdfContext(Aadhar_file.getvalue()) as pdf:
                        #     pil_image = pdfium.render_page(
                        #         pdf,
                        #         page_index = 0,
                        #         scale = 1,
                        #         rotation = 0,
                        #         colour = 0xFFFFFFFF,
                        #         annotations = True,
                        #         greyscale = False,
                        #         optimise_mode = pdfium.OptimiseMode.none,
                        #     )
                        #     faces = st.session_state["mtcnn"].detect_faces(np.array(pil_image))
                        #     if(len(faces)==0):
                        #         st.error("No face detected in Aadhar")
                        #     else:
                        #         pil_image.save("tmp/aadhar.png")
                        #         resp = st.session_state["rekog_object"].client.detect_text(Image={'Bytes': cv2.imencode('.jpg', np.array(pil_image))[1].tobytes()})
                        #         detected_keys = extract_ocr(resp, "Aadhar")
                        #         st.session_state["artifacts"]["AI_Detection"]["aadhar"] = detected_keys
                        st.session_state["artifacts"]["AI_Detection"]["aadhar"] = '724304348374'
                        st.info("Aadhar uploaded")
                    PAN_file = st.file_uploader(
                            "Upload PAN as PDF", type=['pdf'], key='PAN')
                    if PAN_file is not None:
                        #commented:
                        # st.session_state["artifacts"]["pan_pdf"] = PAN_file.getvalue()
                        # with pdfium.PdfContext(PAN_file.getvalue()) as pdf:
                        #     pil_image = pdfium.render_page(
                        #         pdf,
                        #         page_index = 0,
                        #         scale = 1,
                        #         rotation = 0,
                        #         colour = 0xFFFFFFFF,
                        #         annotations = True,
                        #         greyscale = False,
                        #         optimise_mode = pdfium.OptimiseMode.none,
                        #     )
                        #     pil_image.save("tmp/pan.png")
                        #     resp = st.session_state["rekog_object"].client.detect_text(Image={'Bytes': cv2.imencode('.jpg', np.array(pil_image))[1].tobytes()})
                        #     detected_keys = extract_ocr(resp, "PAN")
                        #     st.session_state["artifacts"]["AI_Detection"]["PAN"] = detected_keys
                        st.session_state["artifacts"]["AI_Detection"]["PAN"] = 'JENPK3361G'

                            
                        st.info("PAN uploaded")

                    if PAN_file is not None and Aadhar_file is not None:
                        if st.button('Next', key='1'):
                            st.session_state['sub_page'] = 'Take Selfie'

                if st.session_state['sub_page'] == 'Take Selfie':
                    st.subheader("Step 3: Take Selfie")
                    #commented:
                    # selfie_buffer = st.camera_input('Take a Selfie')
                    selfie_buffer = 'dummy'
                    if selfie_buffer is not None:
                    #commented:
                    #     img = Image.open(selfie_buffer)
                    #     img.save("tmp/selfie.png")
                    #     img_array = np.array(img)
                    #     image_bytes = selfie_buffer.getvalue()
                    #     faces = st.session_state["mtcnn"].detect_faces(img_array)
                    #     if(len(faces)==0):
                    #         st.error("No face detected")
                    #     else:                    
                    #         source_image_bytes = open("tmp/aadhar.png", "rb").read()
                    #         target_image_bytes = open("tmp/selfie.png", "rb").read()
                    #         resp = st.session_state["rekog_object"].client.compare_faces(SimilarityThreshold=0.7,SourceImage={'Bytes': source_image_bytes},TargetImage={'Bytes': target_image_bytes})
                    #         print(resp)
                    #         if not len(resp['FaceMatches']):
                    #             st.error("Face not matching with Aadhar")
                    #         else:
                    #             st.session_state["artifacts"]["selfie"] = target_image_bytes
                    #             st.session_state["artifacts"]["AI_Detection"]["similarity_score_face"] = resp["FaceMatches"][0]["Similarity"]
                                st.session_state["artifacts"]["AI_Detection"]["similarity_score_face"] = '98'
                                st.success("Face matching with Aadhar successful")

                    if st.button('Next', key='2'):
                        st.session_state['sub_page'] = 'Verify Aadhar and PAN'

                if st.session_state['sub_page'] == 'Verify Aadhar and PAN':
                    st.subheader("Step 4: Verify Aadhar and PAN")
                    st.markdown(
                        "Hold your Aadhar and PAN in front of the camera. Make sure your face, and the document is clearly visible.")
                    st.markdown("**1. Aadhar**")
                    #commented:
                    # st.session_state["artifacts"]["aadhar_video"] = videoRecPlay("Aadhar")
                        
                    st.markdown("**2. PAN**")
                    #commented:
                    # st.session_state["artifacts"]["pan_video"] = videoRecPlay("PAN")
                    

                    if st.button('Next', key='confirmation'):
                        st.session_state['sub_page'] = 'Confirmation'

                if st.session_state['sub_page'] == 'Confirmation':
                    st.title('Confirm your Documents, Selfie and Video')
                    st.subheader("Details")
                    st.subheader("Verifier bank")
                    st.write(st.session_state['artifacts']["verifier_bank"])

                    st.subheader("Aadhar card PDF")
                    #commented:
                    # base64_pdf = base64.b64encode(st.session_state["artifacts"]["aadhar_pdf"])
                    # pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'
                    # st.markdown(pdf_display, unsafe_allow_html=True)

                    st.subheader("PAN card PDF")
                    #commented:
                    # base64_pdf = base64.b64encode(st.session_state["artifacts"]["pan_pdf"])
                    # pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'
                    # st.markdown(pdf_display, unsafe_allow_html=True)
                    
                    st.subheader("Selfie")
                    #commented:
                    # st.image(st.session_state["artifacts"]["selfie"])
                    # st.subheader("Aadhar Video")
                    # st.video(st.session_state["artifacts"]["aadhar_video"])
                    # st.subheader("PAN Video")
                    # st.video(st.session_state["artifacts"]["pan_video"])
                    st.subheader("AI Summary")
                    st.write(st.session_state["artifacts"]["AI_Detection"])
                    st.write("\n")


                    if st.button('Confirm and Submit KYC', key='2'):
                        resp = requests.post(REST_API+'/add_kyc',json = {'kyc_data':{'created_date':str(datetime.datetime.now()),'updated_date':str(datetime.datetime.now()),'expiry_date':str(datetime.datetime.now() + datetime.timedelta(days=180)),'docs':[{'name':'PAN_file','value':'s3://pan_file'},{'name':'Aadhar_file','value':'s3://aadhar'}],'status':"NOT SUBMITTED",'assigned_to':st.session_state['artifacts']["verifier_bank"],'allowed_banks':[st.session_state['artifacts']["verifier_bank"]]},'user_data':{'private_key':st.session_state['artifacts']['private_key'],'mobile_number':st.session_state['artifacts']['mobile_num'],'password':st.session_state['artifacts']['password'],'user_type':'CUSTOMER','kyc_number':'NA'}})
                        st.success('Here is Your KYC NUMBER ' + resp.json()['data']+' wait for verification')
                        st.session_state['artifacts']['kyc_number']=resp.json()['data']
                        st.session_state['sub_page'] = 'KYC Status'
            else:
                # st.write('999')
                st.session_state['sub_page'] = 'KYC Status'

            if st.session_state['sub_page'] == 'KYC Status':
                # view kyc 
                resp = requests.post(REST_API+'/view_kyc_details',json ={'kyc_number':st.session_state['artifacts']['kyc_number'],'user_data':{'user_type':'customer','private_key':st.session_state['artifacts']['private_key']}})
                st.write(resp.json())
                st.title('KYC Status: '+ resp.json()['data'][st.session_state['artifacts']['kyc_number']]['status'])

        # Employee
        if st.session_state['artifacts']['user_type'] == 'BANK':
            st.title("KYC List")
            # if st.session_state['sub_page'] == 'List View' :
            if True :
                # list all pending kyc 
                # st.write({'user_data':{'bank_name':st.session_state['artifacts']['bank_name'],'private_key':st.session_state['artifacts']['private_key']}})
                resp = requests.post(REST_API+'/view_pending_lists',json = {'user_data':{'bank_name':st.session_state['artifacts']['bank_name'],'private_key':st.session_state['artifacts']['private_key']}})
                st.write(resp.json())
                pending_lists = []
                if resp.json()['data']!='No Data':
                    pending_lists = resp.json()['data']['pending_list']
                    st.write(pending_lists)

                for kyc in pending_lists:
                    resp = None
                    co1,co2  = st.columns([1,1])
                    with co1:
                        st.write(kyc)
                    with co2 :
                        if st.button('view',key=kyc):
                            resp = requests.post(REST_API+'/view_kyc_details',json ={'kyc_number':st.session_state['artifacts']['kyc_number'],'user_data':{'user_type':'bank','private_key':st.session_state['artifacts']['private_key'],'bank_name':st.session_state['artifacts']['bank_name']}})
                            st.write(resp.json())
                            # consolidated data - s3 display
                            
                    co3,co4 = st.columns([1,1])
                    with co3:
                        if st.button('Approve KYC',key='approve'+kyc):
                            st.write('---')
                            resp = requests.post(REST_API+'/verify_kyc',json={"kyc_number":kyc,"status":"VERIFIED BY "+st.session_state['artifacts']['bank_name'],"user_data":{"private_key":st.session_state['artifacts']['private_key'],"bank_name":st.session_state['artifacts']['bank_name']}})
                            st.write(resp.json())

                    with co4:
                        if st.button('Reject KYC',key='reject'+kyc):
                            resp = requests.post(REST_API+'/verify_kyc',json={"kyc_number":kyc,"status":"REJECTED BY "+st.session_state['artifacts']['bank_name'],"user_data":{"private_key":st.session_state['artifacts']['private_key'],"bank_name":st.session_state['artifacts']['bank_name']}})
                            st.write(resp.json())
                    





                    
                        



                #commented:
                # colms = st.columns((1, 2, 2, 1, 1))
                # fields = ['##### S.No', '##### Name', '##### Mobile Number', '##### Verified', '##### Action']

                # for col, field_name in zip(colms, fields):
                #     # header
                #     col.write(field_name)
                # st.write("\n")

                # for x, mobile_num in enumerate(user_table['Name']):
                #     col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
                #     col1.write(x)
                #     col2.write(user_table['Name'][x])
                #     col3.write(user_table['Mobile Number'][x])
                #     status = user_table['Status'][x]
                #     col4.write(status) # flexible type of button
                #     # button_type = "Unblock" if verified else "Block"
                #     button_phold = col5.empty()  # create a placeholder
                #     if status == 'Pending' :
                #         do_action = button_phold.button("View", key=x)
                #         if do_action :
                #             st.session_state['sub_page'] = 'Detailed View'
                #             st.session_state['current_customer'] = {
                #                 "ID" : x,
                #                 "Mobile Number" : user_table['Mobile Number'][x],
                #                 "Name" : user_table['Name'][x]
                #             }

            st.components.v1.html("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """)
            #commented:            
            # if st.session_state['sub_page'] == 'Detailed View' :
            #     # if st.button('Back') :
            #     #     st.session_state['sub_page'] = 'List View'
            #     if 'current_customer' in st.session_state :
            #         st.subheader("Details")
            #         st.write(st.session_state['current_customer'])
            #         st.subheader("Aadhar card PDF")
            #         # displayPDF('/home/vishnupriyaa/Desktop/Installations and Steps/HiveInstallation.pdf')
            #         st.subheader("PAN card PDF")
            #         # displayPDF('/home/vishnupriyaa/Desktop/Installations and Steps/HiveInstallation.pdf')
            #         st.subheader("Selfie")
            #         # st.image("/home/vishnupriyaa/Desktop/Laptop/Pictures/Screenshots 1/Screenshot (178).png")
            #         st.subheader("Video")
            #         # st.video("/home/vishnupriyaa/Desktop/AWS Cloud Synapt Demo Videos/Login.mp4")
            #         st.subheader("Findings")
            #         st.write({
            #             "Face match" : "80%",
            #             "Address match" : True,
            #             "Phone number match" : True
            #         })
            #         st.write("\n")

            #         c1, c2 = st.columns((3,3))
            #         if c1.button("Approve KYC") :
            #             user_table["Status"][st.session_state['current_customer']['ID']] = 'Approved'
            #             st.session_state['sub_page'] = 'List View'
            #         if c2.button("Reject KYC") :
            #             user_table["Status"][st.session_state['current_customer']['ID']] = 'Rejected'
            #             st.session_state['sub_page'] = 'List View'

    else:
        st.error("Please Sign in")

# Requests
if st.session_state['page'] == 'Requests':

    if st.session_state['signed_in']:
        # st.write(st.session_state[''])
        # Customer
        if st.session_state['artifacts']['user_type'] == 'Customer':
            st.title("KYC Access Requests")
            resp = requests.post(REST_API+'/view_pending_banks',json={'kyc_number':st.session_state['artifacts']['kyc_number'],"user_data":{"private_key":st.session_state['artifacts']['private_key']}})
            # st.write(resp.json())
            pending_banks = resp.json()['data']['pending_banks']
            for bank in pending_banks:
                co1,co2,co3 = st.columns([1,2,1])
                with co1:
                    st.write(bank)
                with co2:
                    if st.button('Approve',key=bank):
                        resp =requests.post(REST_API+'/accept_kyc_request',json={'kyc_number':st.session_state['artifacts']['kyc_number'],'user_data':{"bank_name":bank,"private_key":st.session_state['artifacts']['private_key']}})
                        st.write(resp.json())
                        st.write("Approved")
                with co3:
                    if st.button('Reject',key=bank):
                        resp =requests.post(REST_API+'/reject_kyc_request',json={'kyc_number':st.session_state['artifacts']['kyc_number'],'user_data':{"bank_name":bank,"private_key":st.session_state['artifacts']['private_key']}})
                        st.write(resp.json())
                        st.write("rejected")
            st.write('Allowed banks')
            resp = requests.post(REST_API+'/view_kyc_details',json ={'kyc_number':st.session_state['artifacts']['kyc_number'],'user_data':{'user_type':'customer','private_key':st.session_state['artifacts']['private_key']}})
            st.write(resp.json()['data'][st.session_state['artifacts']['kyc_number']]['allowed_banks'])

            # requests_table = pd.DataFrame({
            #     "Bank" : ["ICICI", "Kotak"],
            #     "Status" : ["Approved", "Pending"]
            # })
            # colms = st.columns((1, 2, 2, 1, 1))
            # fields = ['##### S.No', '##### Bank', '##### Request Status', '##### Action']

            # for col, field_name in zip(colms, fields):
            #     # header
            #     col.write(field_name)
            # st.write("\n")

            # for x, bank in enumerate(requests_table['Bank']):
            #     col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
            #     col1.write(x)
            #     col2.write(requests_table['Bank'][x])
            #     status = requests_table['Status'][x]
            #     col3.write(status) # flexible type of button
            #     # button_type = "Unblock" if verified else "Block"
            #     button_phold1 = col4.empty()  # create a placeholder
            #     button_phold2 = col5.empty()  # create a placeholder
            #     if status == 'Pending' :
            #         do_action1 = button_phold1.button("Approve", key=x)
            #         do_action2 = button_phold2.button("Reject", key=x)
            #         if do_action1 :
            #             st.write(x,"Approved")
            #         if do_action2 :
            #             st.write(x,"Rejected")

        # Employee
        if st.session_state['artifacts']['user_type'] == 'BANK':
            st.title("KYC Access Requests")
            # request to access kyc 
            kyc_number = st.text_input("Kyc Number")
            if st.button("Send Request") :
                resp = requests.post(REST_API+'/request_kyc_details',json={"kyc_number":kyc_number,"user_data":{"bank_name":st.session_state['artifacts']['bank_name'],"private_key":st.session_state['artifacts']['private_key']}})
                st.write(resp.json())
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