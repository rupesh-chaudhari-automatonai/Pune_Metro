import kafka
from pymongo import MongoClient
import json
from video_info import video_list
from model_info import model_list
from threading import Thread
import os

class DbInsertion(Thread):
    """
    This is a Database insertion thread class used to create different database insertion threads based on source inputs and model.
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
        The job of this method is to read serialized meta-data information from specified topic and insert that meta-data information in different collection of DB. 
        """

        video_source = self.args[0]
        model = self.args[1]client

        topic_model_suffix='_{}_metadata'.format(model) 
        topic = os.path.split(video_source)[-1].split('.')[0] # To get base topic name
        topic_meta_data = f'{topic}{topic_model_suffix}' # To get meta-data topic name
        topic_suffix_db ='_db'  
        topic_db = f'{topic_meta_data}{topic_suffix_db}' # To create a overlay topic name
        print(topic_db)


        consumer = kafka.KafkaConsumer(topic_meta_data, bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest')


        # To get the instance of available database
        db_instance = .get_database("mydb")

        # To get the instance of available collection
        collection_instance = db_instance.get_collection(topic_db)

        # To read the data from consumer and insert into DB
        for data in consumer:
            final = json.loads(data.value)
            collection_instance.insert_one(final)


# collection_instance.insert_one(document)
if __name__ == "__main__": 

    # To get the video list from txt file
    vid_lst = video_list()

    # To get the model list from txt file
    model_lst = model_list()

    # connection_string for mongoDB database
    connection_string = "mongodb://localhost:27017/mydb"

    # creating connection
    client = MongoClient(connection_string)

    threads = []

    for i in range(len(vid_lst)):
        for j in range(len(model_lst)):
                
            # creating thread 
            thread = DbInsertion(args=(vid_lst[i],model_lst[j])) 
            thread.start()
            threads.append(thread)

    # To make main thread wait until producer threads finishes their jobs    
    for thread in threads:
        thread.join()
        
    # threads completely executed 
    print("Done!") 
