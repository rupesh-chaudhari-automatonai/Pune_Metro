from video_info import video_list

from threading import Thread

import time
from datetime import datetime
import base64
import pickle
from collections import defaultdict
import cv2
import numpy as np

from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

import os

def encode_cv2_to_base64_str(img):
    """
    This is a utility function used to convert numpy image array into base64 string.
    """
    
    cv2_encoded_img = cv2.imencode('.jpg', img)[1]  
    img64 = base64.b64encode(cv2_encoded_img)  
    frame_str = img64.decode()  

    return frame_str

def pickle_to_kafka(img_data, img_keys=['img']):
    """
    This is a utility function used to serialize data.
    """
    for img_key in img_keys:
        if img_key in img_data:
            img = img_data[img_key]
            base64_img = encode_cv2_to_base64_str(img)
            img_data[img_key] = base64_img

        if 'img_data' in img_data:
            if img_key in img_data['img_data']:
                img = img_data['img_data'][img_key]
                base64_img = encode_cv2_to_base64_str(img)
                img_data['img_data'][img_key] = base64_img

    serialized_data = pickle.dumps(img_data)

    return serialized_data

class ProducerThread(Thread):
    """
    This is a producer thread class used to create different producer threads based on different source inputs.
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        """ 
        Initializer for producer thread class 
        """
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """ 
        This is a run static method, which gets executed when we create a thread extending thread class. 
        The job of this method is to read different video_source from list and transmit the data frame by frame to specified topic in serialized form.
        """

        video_source = self.args[0]

        print("video_source :",video_source)

        try:
            
            cap = cv2.VideoCapture(video_source)   # In case of RTSP stream, change video_source with RTSP url. 

            if  video_source == 0 :   # 0 for webcam
                video_source = str(video_source)

        except Exception as e:
            print(e) # If video source is not given it will give exception
            
        # Start up producer
        producer = KafkaProducer(bootstrap_servers='localhost:9092')   # IP Addr and Port on which Kafka Server is active to creates topics on it. # 192.168.0.212:9092
        
        frame_id = 0
        stream_start_datetime = None

        topic = os.path.split(video_source)[-1].split('.')[0]
        # print(topic)

        # To get the topics from Kafka
        consumer = KafkaConsumer(bootstrap_servers=['localhost:9092'])  # IP Addr and Port on which Consumer is active.
        topic_list = consumer.topics()

        print("topic_list ", topic_list)

        if topic not in topic_list:

            # To create a Topic automatically (on the fly)
            admin_client = KafkaAdminClient(
                bootstrap_servers="localhost:9092", 
            )

            topic_list = []
            topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))
            admin_client.create_topics(new_topics=topic_list, validate_only=False)

        try :

            while(cap.isOpened()):
                ret, img = cap.read() # Read the video file

                ts = datetime.now()

                if not ret:
                    print(f'Could not read for {topic}')
                    break

                if frame_id == 0:
                    stream_start_datetime = ts
                
                # Creating dictionary to for each frame to real-time streaming
                img_data = {
                'vid_id': topic,
                'frame_id': frame_id,
                'img': img,
                'ts': ts,
                'stream_start_datetime': stream_start_datetime
                }

                # print(img_data)

                # import time
                # time.sleep(2)

                # serializing img_data dictionary 
                # ( data needs to be serialized for fast transfer of data, minimize the data’s size which then reduces disk space or bandwidth requirements )
                serialized_data = pickle_to_kafka(img_data)

                #print(f'{topic}: sending frame {frame_id}')

                # Send the serialized_data to respective topics
                producer.send(topic, serialized_data)

                frame_id += 1
                
                print(frame_id)
                print()
            cap.release()
            print('Video sending complete')

        except Exception as e:
            print(e)

if __name__ == "__main__": 

    # To get the video list from txt file
    vid_lst = video_list()

    threads = []

    for i in range(len(vid_lst)):
            
        # creating thread 
        thread = ProducerThread(args=(vid_lst[i],)) 
        thread.start()
        threads.append(thread)

    # To make main thread wait until producer threads finishes their jobs    
    for thread in threads:
        thread.join()
        
    # threads completely executed 
    print("Done!") 
