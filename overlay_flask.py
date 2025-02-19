import cv2
import numpy as np
import kafka
from pymongo import MongoClient
import json

from video_info import video_list
from model_info import model_list

import threading
import os
from datetime import datetime
import base64
import pickle
from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer
from kafka import TopicPartition
import copy
from kafka.admin import KafkaAdminClient, NewTopic

from multiprocessing import Pool
import multiprocessing
import sys

import matplotlib.pyplot as plt

import math
import queue
import time
from flask import Flask, render_template, Response

app = Flask(__name__)

def decode_base64_str_to_cv2(frame_str):

    img64 = frame_str.encode()  
    img64 = base64.b64decode(img64)
    cv2_encoded_img = np.frombuffer(img64, dtype=np.uint8)
    img = cv2.imdecode(cv2_encoded_img, cv2.IMREAD_COLOR)

    return img

def unpickle_from_kafka(data, img_key='img'):
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

# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# To calculate the distance
def distance_chk(X, Y):

    x1, y1 = X[0], X[1]
    x2, y2 = Y[0], Y[1]

    # print(x1, x2, y1, y2)

    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    return distance

def metadata_process(video_source):

    print("video_source",video_source)

    a, b = video_source[1]

    q = video_source[2]

    topic = os.path.split(video_source[0])[-1].split('.')[0] # kafka main topic


    topic_model_suffix = []

    for model in video_source[1]:
        topic_model_suffix.append('_{}_metadata'.format(model))

    topic_meta_data = []
    
    for model in topic_model_suffix:
        topic_meta_data.append(f'{topic}{model}')   #Kafaka metadata Topic

    topic_suffix_db ='_db'  

    topic_db = {}
    
    for model in topic_meta_data:
        topic_db[model] = (f'{model}{topic_suffix_db}') #Kafaka database Topic


    print(">>>>>>>>>>>  ",topic, topic_model_suffix, topic_meta_data, topic_db)

    # To get the instance of available database
    db_instance = client.get_database("mydb")

    for obj1, obj2 in zip(*[iter(topic_db.values())]*2):
        print("ENterred in 1st for loop")
        print (obj1, obj2)

        # To get the instance of available collection
        collection_instance_obj1 = db_instance.get_collection(obj1)
        collection_instance_obj2 = db_instance.get_collection(obj2)

        filter = {"vid_id" : topic }

        highest_previous_frame_id = -1 # 5

        while True:

            # cursor_obj1 = list(collection_instance_obj1.find(filter))
            # cursor_obj2 = list(collection_instance_obj2.find(filter))

            cursor_obj1 = collection_instance_obj1.find(filter)
            cursor_obj2 = collection_instance_obj2.find(filter)

            for doc1, doc2 in zip(cursor_obj1,cursor_obj2):
                print(doc1['model'], doc2['model'])
                print("Entered in while loop ...........")

                # get the current primary key, and if it's greater than the previous one
                # we print the results and increment the variable to that value
                current_frame_id_doc1 = doc1['frame_id']
                current_frame_id_doc2 = doc2['frame_id']

                if current_frame_id_doc1 > highest_previous_frame_id:
                    # print(topic)
                    # print(current_frame_id_doc1, current_frame_id_doc2)

                    boxes_lst = []
                    mid_pt_lst = []
                    distance_lst = []
                    mid_pt_dict = {}
                    distance_dict = {}
    
                    frame_path = doc1['frame_path']
                    img =  cv2.imread(frame_path)
                    meta_data_doc1 = doc1['meta_data']
                    meta_data_doc2 = doc2['meta_data']
                    for value in meta_data_doc2.values():
                        caption = value[0]
                        # print(type(value[1]))
                        bbox = value[1]
                        
                        # Converting String into List
                        bbox = bbox.strip('[]')  # Remove square brackets
                        bbox = bbox.split()  # Split the string by spaces
                        bbox = [int(coord) for coord in bbox]  # Convert each substring to an integer
                        print(bbox)

                        cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0) , 2) 
                        cv2.putText(img, caption, (int(bbox[0]), int(bbox[1])), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)   

                    for value in meta_data_doc1.values():
                        caption = value[0]
                        bbox = value[1]
                        print(bbox)

                        cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0) , 2) 
                        cv2.putText(img, caption, (int(value[1][0]), int(value[1][1])), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)   

                        bbox = list(map(int, bbox))

                        boxes_lst.append(bbox)   


                    if len(boxes_lst) > 0:
                        for box in boxes_lst:
                            color = [0, 255, 0]
                            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 2)

                    for i in range(len(mid_pt_lst)):
                        for j in range(i, len(mid_pt_lst)):
                            if i == j:
                                pass
                            else:
                                distance = distance_chk(mid_pt_lst[i], mid_pt_lst[j])
                                distance_dict[distance] = (mid_pt_lst[i], mid_pt_lst[j])
                                distance_lst.append(distance)
                                # print(distance)

                    if len(distance_dict) > 0:

                        red_box = []
                        mid_lin = []

                        for distance in list(distance_dict.keys()):

                            if distance < 180:
                                # print(distance)
                                mid_lin.append(distance_dict[distance])
                                temp = []
                                for i in distance_dict[distance]:
                                    bbox = mid_pt_dict[i]
                                    temp.append(bbox)
                                red_box.append(temp)

                        # print("red_box :", red_box)
                        # print("mid_lin :", mid_lin)

                        if len(red_box) > 0:
                            for boxes in red_box:
                                # print(box)
                                for box in boxes:
                                    color = [0, 0, 255]
                                    cv2.rectangle(img, (box[0], box[1]),
                                                (box[2], box[3]), color, 2)

                            #for pt in mid_lin:
                                #p0 = pt[0]
                                #p1 = pt[1]
                                #color = [0, 0, 255]
                                #cv2.line(img, p0, p1, color, 3)
                    
                    q.put(img)

                    highest_previous_frame_id = current_frame_id_doc1


# collection_instance.insert_one(document)
if __name__ == "__main__": 

    vid_lst = video_list()

    model_lst = model_list()
    # print(model_lst)

    connection_string = "mongodb://localhost:27017/mydb"
    client = MongoClient(connection_string)

    memory = {}

    lock = threading.Lock()

    q_lst = []

    for i in range(len(vid_lst)):

        q = queue.Queue()
        q_lst.append(q)

    
    for i in range(len(vid_lst)):
        param = [vid_lst[i], model_lst, q_lst[i]]
        thread = threading.Thread(target=metadata_process, args=(param, )) 
        thread.daemon = True
        thread.start()

    def find_camera(list_id):
        return q_lst[int(list_id)]

    def gen_frames(camera_id):
        # print(camera_id)
        cam = find_camera(camera_id)  # return the camera access link with credentials. Assume 0?
        # cam = cameras[int(id)]

        while not cam.empty():

            z = cam.get()
            typ_z = z.__class__.__name__

            if typ_z == "ndarray" :
                ret, buffer = cv2.imencode('.jpg', z)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
                
    def find_camera(list_id):
        return q_lst[int(list_id)]

    @app.route('/video_feed/<string:list_id>/', methods=["GET"])
    def video_feed(list_id):
        return Response(gen_frames(list_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/video_feed/', methods=["GET"])
    def default_video_feed(list_id):
        # Define behavior for the default video feed route, if needed
        pass  # Placeholder, replace with actual implementation if necessary



    @app.route('/', methods=["GET"])
    def index():
        return render_template('index.html', camera_list=len(vid_lst), camera=q_lst)

    app.run(debug=True, threaded=True)
