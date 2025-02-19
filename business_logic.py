
#############################################################################
# Logic For Ticket Line Exceeds
#############################################################################


# %% [markdown]
# ## Logic For Ticket Line Exceeds

import torch
import os
HOME = os.getcwd()
print(HOME)

import cv2
# from sort import *
import math
import numpy as np
from ultralytics import YOLO
import cvzone

# !pip install ultralytics
import ultralytics
ultralytics.checks()

from IPython import display
display.clear_output()

import detectron2
print("detectron2:", detectron2.__version__)

# !pip install supervision==0.18.0
display.clear_output()
import supervision as sv
print("supervision", sv.__version__)

# %%
Input_Video_Path = "/workspace/Metro_Video_Analytics/Ticketing_Line_2_trimmed.avi"
model = YOLO('yolov8m.pt')

# initiate polygon zone
polygon = np.array([
    [130, 750],
    [1350, 410],
    [1040, 270],
    [130, 400],
    [130, 750]
])

# create BYTETracker instance
byte_tracker = sv.ByteTrack(track_thresh=0.25, track_buffer=30, match_thresh=0.8, frame_rate=30)
video_info = sv.VideoInfo.from_video_path(Input_Video_Path)

# %%
import numpy as np
import supervision as sv

video_info = sv.VideoInfo.from_video_path(Input_Video_Path)
# Put_Text font 
font = cv2.FONT_HERSHEY_SIMPLEX 
# initiate annotators
box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.4)

# extract video frame
generator = sv.get_video_frames_generator(Input_Video_Path)
iterator = iter(generator)
frame = next(iterator)

# detect

results = model(frame, imgsz=1280,classes=0,save_txt=True)[0]
detections = sv.Detections.from_ultralytics(results)
detections = detections[detections.class_id == 0]
# detections = byte_tracker.update_with_detections(detections)
print(detections)

# if model.names == "person":
# annotate Bounding Box on Frame
labels = [f"# {traking_id} {model.names[class_id]} {confidence:0.2f}" for traking_id,confidence, class_id in zip(detections.tracker_id,detections.confidence, detections.class_id)]
frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

# Draw the polygon
cv2.polylines(frame,[polygon], isClosed=False, color=(0, 0, 255), thickness=4)
# Display the current count of boxes inside the polygon on the frame
cv2.putText(frame, "People count exceed the Given Threshold", (20, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
# Display the current count of boxes inside the polygon on the frame
cv2.putText(frame, "People count exceed the Given Threshold", (20, 85), font, 1, (255, 0, 0), 2, cv2.LINE_AA)


list_of_xyxy = detections[0].xyxy
x,y,x1,y1 = list_of_xyxy[0]
print(x,y,x1,y1)

%matplotlib inline  
sv.plot_image(frame, (16, 16))


import numpy as np
import cv2
import cvzone
import supervision as sv

# Put_Text font 
font = cv2.FONT_HERSHEY_SIMPLEX 

# initiate_Bbox annotators
box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.4)
def process_frame(frame: np.ndarray, _) -> np.ndarray:

    zoneAcounter = []
    results = model(frame, imgsz=1280, classes=0)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = detections[detections.class_id == 0]
    
    # Draw the polygon
    cv2.polylines(frame, [polygon], isClosed=False, color=(0, 255, 0), thickness=4)
    
    # track_result = tracker.update(detections)
    # detections = byte_tracker.update_with_detections(detections1)    
    # print(detections)
    #, tracker_id in , detections.tracker_id
    for xyxy, confidence, class_id in zip(detections.xyxy, detections.confidence, detections.class_id):
        
        x1, y1, x2, y2 = xyxy
        # id = tracker_id
        # id = int(tracker_id)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w // 2, y2
    
        # Calculate the center point of the bottom line of the bbox
        center = (cx, cy)
        # Check if the center point intersects or passes through the polygon
        if cv2.pointPolygonTest(polygon, center, False) >= 0:
            cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (240, 32, 160), 3)
            cvzone.putTextRect(frame, "Person", [x1 + 8, y1 - 12], thickness=2, scale=1.5)
            zoneAcounter.append(1)  # Store a value of 1 for each bbox inside the polygon
    
    if 0 < len(zoneAcounter) < 12: 
        # Display the current count of boxes inside the polygon on the frame
        cv2.putText(frame, f"Total People in Queue = {len(zoneAcounter)}", (20, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
    else:
        # Display the current count of boxes inside the polygon on the frame
        cv2.putText(frame, f"Total People in Queue = {len(zoneAcounter)}", (20, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
        # Display the current count of boxes inside the polygon on the frame
        cv2.putText(frame, "People count exceed the Given Threshold", (20, 85), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

    return frame  
   
    

sv.process_video(source_path=Input_Video_Path, target_path=f"{HOME}/Ticketing_Line_2_trimmed_infered.mp4", callback=process_frame)



#############################################################################
# Logic For Intrution Detection
#############################################################################

import torch
import os
HOME = os.getcwd()
print(HOME)

import cv2
# from sort import *
import math
import numpy as np
from ultralytics import YOLO
import cvzone

# !pip install ultralytics
import ultralytics
ultralytics.checks()

from IPython import display
display.clear_output()

import detectron2
print("detectron2:", detectron2.__version__)

# !pip install supervision==0.18.0
display.clear_output()
import supervision as sv
print("supervision", sv.__version__)

# %%
Input_Video_Path = "/workspace/Metro_Video_Analytics/Loitering_4_trimmed.avi"
model = YOLO('yolov8m.pt')

# create BYTETracker instance
byte_tracker = sv.ByteTrack(track_thresh=0.25, track_buffer=30, match_thresh=0.8, frame_rate=30)
video_info = sv.VideoInfo.from_video_path(Input_Video_Path)

road_zoneA = np.array([[425, 705], [565, 710], [640, 600], [520, 600], [425, 705]], np.int32)
# road_zoneB = np.array([[727, 797], [1123, 812], [1001, 516], [741, 525], [730, 795]], np.int32)
# road_zoneC = np.array([[1116, 701], [1533, 581], [1236, 367], [1009, 442], [1122, 698]], np.int32)

# %%
import numpy as np
import supervision as sv

video_info = sv.VideoInfo.from_video_path(Input_Video_Path)

# initiate annotators
box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.4)

# extract video frame
generator = sv.get_video_frames_generator(Input_Video_Path)
iterator = iter(generator)
frame = next(iterator)

# detect

results = model(frame, imgsz=1280,classes=0,save_txt=True)[0]
detections = sv.Detections.from_ultralytics(results)
detections = detections[detections.class_id == 0]
detections = byte_tracker.update_with_detections(detections)
print(detections)

# if model.names == "person":
# annotate Bounding Box on Frame
labels = [f"# {traking_id} {model.names[class_id]} {confidence:0.2f}" for traking_id,confidence, class_id in zip(detections.tracker_id,detections.confidence, detections.class_id)]
frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

# Draw the polygon
cv2.polylines(frame,[road_zoneA], isClosed=False, color=(0, 0, 255), thickness=4)


list_of_xyxy = detections[0].xyxy
x,y,x1,y1 = list_of_xyxy[0]
print(x,y,x1,y1)

%matplotlib inline  
sv.plot_image(frame, (16, 16))

# %%
import numpy as np
import cv2
import cvzone
import supervision as sv

# Put_Text font 
font = cv2.FONT_HERSHEY_SIMPLEX 

# initiate_Bbox annotators
box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.4)
def process_frame(frame: np.ndarray, _) -> np.ndarray:

    zoneAcounter = []
    results = model(frame, imgsz=1280, classes=0)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections1 = detections[detections.class_id == 0]
    
    # Check if any bounding boxes intersect or are inside the polygon
    polygon_color = (0, 255, 0)  # Default color is green
    for bbox in detections1.xyxy:
        center = ((bbox[0] + bbox[2]) // 2, bbox[3])
        if cv2.pointPolygonTest(road_zoneA, center, False) >= 0:
            polygon_color = (0, 0, 255)  # Change color to blue if any box intersects or is inside

    # Draw the polygon
    cv2.polylines(frame,[road_zoneA], isClosed=False, color=(0, 255, 0), thickness=4)
    
    for xyxy, confidence, class_id in zip(detections.xyxy, detections.confidence, detections.class_id):
        
        x1, y1, x2, y2 = xyxy
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w // 2 , y2
    
        # Calculate the center point of the bottom line of the bbox
        center = (cx, cy)
        # Check if the center point intersects or passes through the polygon
        if cv2.pointPolygonTest(road_zoneA, center, False) >= 0:
            cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (240, 32, 160), 3)
            cvzone.putTextRect(frame, "Person", [x1 + 8, y1 - 12], thickness=2, scale=1.5)
            zoneAcounter.append(1)  # Store a value of 1 for each bbox inside the polygon

    # Display the current count of boxes inside the polygon on the frame
    cv2.putText(frame, f"{len(zoneAcounter)} Intruders Detected !!!", (20, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

    return frame
    

sv.process_video(source_path=Input_Video_Path, target_path=f"{HOME}/Loitering_4_trimmed_infered.mp4", callback=process_frame)

# %%



#############################################################################
# Logic For Edge_Crossing and Jumping
#############################################################################


# %% [markdown]
# ## Logic For Edge_Crossing and Jumping

# %%
import torch
import os
HOME = os.getcwd()
print(HOME)

import cv2
# from sort import *
import math
import numpy as np
from ultralytics import YOLO
import cvzone

# !pip install ultralytics
import ultralytics
ultralytics.checks()

from IPython import display
display.clear_output()

import detectron2
print("detectron2:", detectron2.__version__)

# !pip install supervision==0.18.0
display.clear_output()
import supervision as sv
print("supervision", sv.__version__)

# %%
Input_Video_Path = "PF_EdgeCrossing_2.avi"
model = YOLO('yolov8l.pt')


# %%
# create BYTETracker instance
byte_tracker = sv.ByteTrack(track_thresh=0.25, track_buffer=30, match_thresh=0.8, frame_rate=30)
video_info = sv.VideoInfo.from_video_path(Input_Video_Path)
line1 = [690, 1010,1040,200]
line2 = [410,1050, 1007, 210]
yellow_line_counter = []
Edge_line_counter = []

# %%
import numpy as np
import supervision as sv

video_info = sv.VideoInfo.from_video_path(Input_Video_Path)

# initiate annotators
box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.4)

# extract video frame
generator = sv.get_video_frames_generator(Input_Video_Path)
iterator = iter(generator)
frame = next(iterator)

# detect

results = model(frame, imgsz=1280,classes=0,save_txt=True)[0]
detections = sv.Detections.from_ultralytics(results)
detections = detections[detections.class_id == 0]
detections = byte_tracker.update_with_detections(detections)
print(detections)

# if model.names == "person":
# annotate Bounding Box on Frame
labels = [f"# {traking_id} {model.names[class_id]} {confidence:0.2f}" for traking_id,confidence, class_id in zip(detections.tracker_id,detections.confidence, detections.class_id)]
frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

#Drawing Line on frame
cv2.line(frame,(line1[0],line1[1]),(line1[2],line1[3]),(0,255,255),3)

#Draw The 2nd Line For Jump
cv2.line(frame,(line2[0],line2[1]),(line2[2],line2[3]),(0,0,255),2)

list_of_xyxy = detections[0].xyxy
x,y,x1,y1 = list_of_xyxy[0]
print(x,y,x1,y1)

%matplotlib inline  
sv.plot_image(frame, (16, 16))

# %%
import numpy as np
import supervision as sv

yellow_line_counter = []
Edge_line_counter = []

# Put_Text font 
font = cv2.FONT_HERSHEY_SIMPLEX 

# initiate_Bbox annotators
box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.4)
def process_frame(frame: np.ndarray, _) -> np.ndarray:
    
    results = model(frame, imgsz=1280,classes=0)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections1 = detections[detections.class_id == 0]
    
    #Drawing Line on frame
    cv2.line(frame,(line1[0],line1[1]),(line1[2],line1[3]),(0,255,255),3)

    #Draw The 2nd Line For Jump
    cv2.line(frame,(line2[0],line2[1]),(line2[2],line2[3]),(0,0,255),3)
    
    # track_result = tracker.update(detections)
    detections = byte_tracker.update_with_detections(detections1)    
    print(detections)
    for xyxy, confidence, class_id, tracker_id in zip(detections.xyxy,detections.confidence,detections.class_id,detections.tracker_id):
        
        x1,y1,x2,y2 = xyxy
        id = tracker_id
        x1, y1, x2, y2, id = int(x1), int(y1), int(x2), int(y2),int(tracker_id)
    
        w,h = x2-x1,y2-y1
        cx,cy = x1+w//2 , y2
    
        cv2.circle(frame,(cx,cy),6,(0,0,255),-1)
        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),3)
        cvzone.putTextRect(frame,f'{id}',
                           [x1+8,y1-12],thickness=2,scale=1.5)
        
        # Assuming line is represented as (x1, y1, x2, y2)
        m1 = (line1[3] - line1[1]) / (line1[2] - line1[0])  # Slope
        b1 = line1[1] - m1 * line1[0]  # Intercept

        cy1expected = m1 * cx + b1  # Expected cy for a given cx on the line

        # Check if cy is within a certain range of cy1expected
        if (cy1expected - 10) < cy < (cy1expected + 10):
            # Increment count or perform desired action
            cv2.line(frame, (line1[0], line1[1]), (line1[2], line1[3]), (255, 0, 0), 3)
            cv2.putText(frame,f'ALLERT !!!! - Defined Yellow Line Crosses',[200,100],font,fontScale=2.3,color=(0,255,255),thickness=3)
            if yellow_line_counter.count(id) == 0:
                yellow_line_counter.append(id)

                # Assuming line is represented as (x1, y1, x2, y2)
        m2 = (line2[3] - line2[1]) / (line2[2] - line2[0])  # Slope
        b2 = line2[1] - m2 * line2[0]  # Intercept

        cy2expected = m2 * cx + b2  # Expected cy for a given cx on the line

        # Check if cy is within a certain range of cy1expected
        if (cy2expected - 10) < cy < (cy2expected + 10):
            # Increment count or perform desired action
            cv2.line(frame, (line2[0], line2[1]), (line2[2], line2[3]), (255, 0,0), 3)
            cv2.putText(frame,f'ALLERT !!!! - Edge Line is crossed',[200,300],font,fontScale=2.3,color=(0,0,255),thickness=3)
            if Edge_line_counter.count(id) == 0:
                Edge_line_counter.append(id)
    
    
    # cv2.putTextRect(frame,f'ALLERT !!!! - Defined Yellow Line Crosses',[200,100],thickness=3,scale=2.3,border=2)
    return frame

sv.process_video(source_path=Input_Video_Path, target_path=f"{HOME}/PF_EdgeCrossing_2_1.mp4", callback=process_frame)


    # cv2.imshow('frame',frame)
    # cv2.waitKey(1)

# %%
import numpy as np
import supervision as sv

# initiate annotators
box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.4)
# extract video frame
generator = sv.get_video_frames_generator("PF_EdgeCrossing_2.avi")
iterator = iter(generator)
frame = next(iterator)
detections = np.empty((0,5))
result = model(frame,stream=1)
for info in result:
    boxes = info.boxes
    print(boxes)
    for box in boxes:
        x1,y1,x2,y2 = box.xyxy[0]
        conf = box.conf[0]
        classindex = box.cls[0]
        conf = math.ceil(conf * 100)
        classindex = int(classindex)
        objectdetect = classnames[classindex] 

        if objectdetect == 'person':
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            new_detections = np.array([x1,y1,x2,y2,conf])
            detections = np.vstack((detections,new_detections))
            # print("##################################################")
            print(detections)
            # print("################################################")
track_result = byte_tracker.update_with_detections(x1,y1,x2,y2)
cv2.line(frame,(line[0],line[1]),(line[2],line[3]),(0,255,255),7)


# %%



