# ocr,label detection,face matching
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"

import boto3
from mtcnn.mtcnn import MTCNN
from numpy import asarray
import cv2

class Rekognition:
    def __init__(self,access_key,secret_key,region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        if self.access_key is None or self.secret_key is None or self.region is None:
            raise Exception("Please provide access_key, secret_key and region")
        self.client = boto3.client('rekognition', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)

    def compare_faces(self,source_image,target_image,similarity_threshold):
        source_image_bytes = open(source_image, 'rb').read()
        target_image_bytes = open(target_image, 'rb').read()
        resp = self.client.compare_faces(SimilarityThreshold=similarity_threshold,SourceImage={'Bytes': source_image_bytes},TargetImage={'Bytes': target_image_bytes})
        return resp['FaceMatches']
    
    def detect_text(self,image):
        image_bytes = open(image, 'rb').read()
        resp = self.client.detect_text(Image={'Bytes': image_bytes})
        return resp
    
    def detect_faces(self,image):
        image_bytes = open(image, 'rb').read()
        resp = self.client.detect_faces(Image={'Bytes': image_bytes})
        return resp
    
    def extract_face_frame(self, video_file_or_stream):
        vid = cv2.VideoCapture(video_file_or_stream)
        while(vid.isOpened()):
            ret, frame = vid.read()
            detector = MTCNN()
            f = detector.detect_faces(frame)
            if len(f) > 0:
                return frame
        return None

class S3:
    def __init__(self,access_key,secret_key,region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        if self.access_key is None or self.secret_key is None or self.region is None:
            raise Exception("Please provide access_key, secret_key and region")
        self.session = boto3.Session(region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        self.client = boto3.client("s3", region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)