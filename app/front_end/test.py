import streamlit as st
import pandas as pd
import rekognition
from dotenv import load_dotenv
import os
load_dotenv()

#### KYC Customer Login ####
# st.title("KYC Customer Login")

# mobile_num = st.text_input("Mobile Number")
# password = st.text_input("Password", type='password')

# if st.button("Login") :
#     print(mobile_num, password)

#### Bank Employee Login ####
# st.title("Bank Employee Login")

# banks = ["HDFC", "ICICI"]
# bank = st.selectbox("Bank", banks)

# username = st.text_input("Username")
# password = st.text_input("Password", type='password')

# if st.button("Login") :
#     print(bank, username, password)

#### Upload PAN and Aadhar ####
# PAN_file = st.file_uploader("Upload PAN as PDF", type=['pdf'], key='PAN')
# if PAN_file is not None:
#     #  # To read file as bytes:
#     #  bytes_data = uploaded_file.getvalue()
#     #  st.write(bytes_data)

#     #  # To convert to a string based IO:
#     #  stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
#     #  st.write(stringio)

#     #  # To read file as string:
#     #  string_data = stringio.read()
#     #  st.write(string_data)

#     #  # Can be used wherever a "file-like" object is accepted:
#     #  dataframe = pd.read_csv(uploaded_file)
#     #  st.write(dataframe)

#     print("PAN uploaded")

# Aadhar_file = st.file_uploader("Upload Aadhar as PDF", type=['pdf'], key='Aadhar')
# if Aadhar_file is not None:
#     print("Aadhar uploaded")

# Rekognition object
client = rekognition.Rekognition(access_key = os.environ.get('access_key_id'),secret_key=os.environ.get('secret_key_id'),region=os.environ.get('region'))
print(client.access_key,client.secret_key)
source_image = '/path/to/src/image'
target_image = '/path/to/target/image'
image_path = '/path/to/image'
client.compare_faces(src_image,target_image)
client.detect_faces(image_path)
client.detect_text(image_path)