#!/usr/bin/env python
# coding: utf-8

from video_info import video_list
from ultralytics import YOLO
import math

# importing the threading module 
from threading import Thread

import cv2
from PIL import Image
import numpy as np
import os

import sys
import time

import itertools
import glob


from datetime import datetime
import base64
import pickle
from collections import defaultdict

from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

import cv2.dnn
import numpy as np

from ultralytics.utils import ASSETS, yaml_load
from ultralytics.utils.checks import check_yaml

import json

CLASSES = yaml_load(check_yaml("coco8.yaml"))["names"]
colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))

def json_serializer(data):
    """
    This is a utility function used to serialize data.
    """
    return json.dumps(data, indent=4, sort_keys=True, default=str).encode("utf-8")

def decode_base64_str_to_cv2(frame_str):
    """
    This is a utility function used to convert base64 image into numpy array.
    """

    img64 = frame_str.encode()  
    img64 = base64.b64decode(img64)
    cv2_encoded_img = np.frombuffer(img64, dtype=np.uint8)
    img = cv2.imdecode(cv2_encoded_img, cv2.IMREAD_COLOR)

    return img

def unpickle_from_kafka(data, img_key='img'):
    """
    This is a utility function used to deserialize data.
    """

    deserialized_data = pickle.loads(data.value)

    if img_key in deserialized_data:
        base64_img = deserialized_data[img_key]
        img = decode_base64_str_to_cv2(base64_img)
        deserialized_data[img_key] = img

    if 'img_data' in deserialized_data:
        if img_key in deserialized_data['img_data']:
            base64_img = deserialized_data['img_data'][img_key]
            img = decode_base64_str_to_cv2(base64_img)
            deserialized_data['img_data'][img_key] = img

    return deserialized_data


def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    """
    Draws bounding boxes on the input image based on the provided arguments.

    Args:
        img (numpy.ndarray): The input image to draw the bounding box on.
        class_id (int): Class ID of the detected object.
        confidence (float): Confidence score of the detected object.
        x (int): X-coordinate of the top-left corner of the bounding box.
        y (int): Y-coordinate of the top-left corner of the bounding box.
        x_plus_w (int): X-coordinate of the bottom-right corner of the bounding box.
        y_plus_h (int): Y-coordinate of the bottom-right corner of the bounding box.
    """
    label = f"{CLASSES[class_id]} ({confidence:.2f})"
    color = colors[class_id]
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

class ConsumerThread(Thread):
    """
    This is a consumer thread class used to create different consumer threads based on source inputs and model.
    """

    def __init__(self, video_source, model):
        """ 
        Initializer for consumer thread class.
        """
        super().__init__()
        self.video_source = video_source
        self.model = model

    def run(self):
        """ 
        This is a run static method, which gets executed when we create a thread extending thread class.
        The job of this method is to read serialized data from specified topic frame by frame and perform model inference on each frame. 
        The output meta-data is send to specified topic for further post processing.
        """

        print("video_source :",self.video_source)

        data_dir = './frames'

        topic_suffix='_face_metadata'  
        topic = os.path.split(self.video_source)[-1].split('.')[0] # To get base topic name
        topic_meta_data = f'{topic}{topic_suffix}' # To create a meta-data topic name
        print("topic_meta_data :",topic_meta_data)

        if not os.path.exists(os.path.join(data_dir, topic)):
            os.makedirs(os.path.join(data_dir, topic))

        # Fire up the Kafka Consumer
        consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest')
        
        # Fire up the Kafka Producer
        producer = KafkaProducer(bootstrap_servers='localhost:9092')

        # Reading data from Kafka Consumer on specified topic
        for data in consumer:
            try:
                deserialized_data = unpickle_from_kafka(data)
                img = deserialized_data['img']
                frame_id = deserialized_data['frame_id']
                vid_id = deserialized_data['vid_id']
                print("frame_id ", frame_id)
                meta_data = self.process(img)

                frame_path = os.path.join(data_dir, topic, f'{frame_id}.jpg')
                cv2.imwrite(frame_path, img)

                deserialized_data["meta_data"] = meta_data
                deserialized_data["model"] = 'face'
                deserialized_data["frame_path"] = frame_path
                deserialized_data.pop('img', None)

                serialized_data = json_serializer(deserialized_data)
                producer.send(topic_meta_data, serialized_data)

            except Exception as e:
                print(e)

    def process(self, img):

        """
        This is a process method used to do inference on frames, it returns meta-data.
        """

        count = 0
        meta_data = {}
        img1 = img

        ## Actual Yolo Prediction
        start_time = time.time()
        results = model.predict(source=img1, conf=0.40, device=0, imgsz=[720,1080])
        elapsed_time = time.time() - start_time

        for result in results:

            for image_info, infer_info in zip(result,result.boxes):
                # print(image_info,"==??",infer_info)
                lst = []
                # CLass labels value in INT {eg. like 0 or 1 or 2}
                class_index = int(infer_info.cls[0])
                print(class_index)

                # # Class Label
                class_label = image_info.names[class_index]
                print(class_label)

                # Get the Confidence Score
                score = math.ceil(infer_info.conf[0].item() * 100)
                print(score)
                # print(infer_info.xyxy[0][1].item())

                #Bbox Co-ordinate 
                x1 = infer_info.xyxy[0][0].item()
                y1 = infer_info.xyxy[0][1].item()
                x2 = infer_info.xyxy[0][2].item()
                y2 = infer_info.xyxy[0][3].item()
                bbox = [x1, y1, x2, y2]
                # print(x1,y1,x2,y2)

                count = count + 1

                lst.append(class_label)
                lst.append(bbox)
                meta_data[count] = lst

        return meta_data



if __name__ == "__main__": 

    # To get the video list from txt file
    vid_lst = video_list()

    # # Path to the trained model
    Model_Path = "./Models/Left_Bag_Detection/best.engine"

    #Load the Yolo Model
    model = YOLO(Model_Path)

    # # # Path to the label_map of model ( Labels on which model is trained )
    # Label_Map_path = "./yolo_weights/classes.txt"

    threads = []

    for video in vid_lst:            

        thread = ConsumerThread(video, model)
        thread.start()
        threads.append(thread)

    # To make main thread wait until producer threads finishes their jobs    
    for thread in threads:
        thread.join()
        
    # threads completely executed 
    print("Done!") 
