# ocr,label detection,face matching
import boto3
class Rekognition:
    def __init__(self,access_key,secret_key,region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
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