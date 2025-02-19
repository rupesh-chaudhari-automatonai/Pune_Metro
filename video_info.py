def video_list():
        
    video_list = None

    with open("video_list.txt", "r") as fd:
        video_list = fd.read().splitlines()

    return video_list
