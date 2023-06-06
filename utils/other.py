

def is_number(string: str):
    try:
        float(string)
        return True
    except:
        return False