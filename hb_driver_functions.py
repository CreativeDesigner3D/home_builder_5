def IF(statement,true,false):
    """ Returns true if statement is true Returns false if statement is false:
        statement - conditional statement
        true - value to return if statement is True
        false - value to return if statement is False
    """
    if statement == True:
        return true
    else:
        return false

def OR(*vars):
    """ Returns True if ONE parameter is true
    """
    for var in vars:
        if var:
            return True
    return False

def AND(*vars):
    """ Returns True if ALL parameters are true
    """
    for var in vars:
        if not var:
            return False
    return True        