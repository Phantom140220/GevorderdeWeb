def check_lampid(lampid):
    if lampid in ["1a","1b","1c","2a","2b","2c","3a","3b","3c","4a","4b","4c","5a","5b","5c"]:
        return True
    else:
        return False
    
def check_POST_data(data):
    if data == "1":
        return True