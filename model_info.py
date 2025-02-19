def model_list():
        
    model_list = None

    with open("model_list.txt", "r") as fd:
        model_list = fd.read().splitlines()

    return model_list
