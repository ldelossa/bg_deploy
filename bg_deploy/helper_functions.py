
def _input_loop(msg):
    usr_input = input(msg)

    if usr_input.upper() in ['YES', 'Y']:
        return True
    elif usr_input.upper() in ['NO', 'N']:
        return False
    else:
        _input_loop(msg)