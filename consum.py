#!/usr/bin/env python
# coding: utf-8

from video_info import video_list

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

import json

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

class ConsumerThread(Thread):
    """
    This is a consumer thread class used to create different consumer threads based on source inputs and model.
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        """ 
        Initializer for consumer thread class.
        """
        super().__init__()
        self.args = args
        self.kwargs = kwargs


    def run(self):
        """ 
        This is a run static method, which gets executed when we create a thread extending thread class.
        The job of this method is to read serialized data from specified topic frame by frame and perform model inference on each frame. 
        The output meta-data is send to specified topic for further post processing.
        """

        video_source = self.args[0]

        print("video_source :",video_source)

        data_dir = './frames'

        topic_suffix='_face_metadata'  
        topic = os.path.split(video_source)[-1].split('.')[0] # To get base topic name
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
            deserialized_data = unpickle_from_kafka(data) # De-serializing data
            img = deserialized_data['img'] # Getting img numpy array
            frame_id = deserialized_data['frame_id'] # Getting frame_id
            vid_id = deserialized_data['vid_id'] # Getting video_id / video_name

            try:
                
                # getting meta-data
                meta_data = ConsumerThread.process(img)

                print(topic, meta_data)

            except Exception as e:
                print(e)

            frame_path = os.path.join(data_dir, topic) + '/' + f'{frame_id}.jpg' 

            print(frame_path)

            cv2.imwrite(frame_path,img )



if __name__ == "__main__": 

    # To get the video list from txt file
    vid_lst = video_list()

    threads = []

    for i in range(len(vid_lst)):
            
        # creating thread 
        thread = ConsumerThread(args=(vid_lst[i],)) 
        thread.start()
        threads.append(thread)

    # To make main thread wait until producer threads finishes their jobs    
    for thread in threads:
        thread.join()
        
    # threads completely executed 
    print("Done!") 
