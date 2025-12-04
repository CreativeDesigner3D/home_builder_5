def inch(value):
    """ Converts inch to meter
    """
    return value * 0.0254

def feet(value):
    """ Converts feet to meter
    """
    return value * 0.3048

def millimeter(value):
    """ Converts millimeter to meter
    """
    return value * .001

def centimeter(value):
    """ Converts centimeter to meter
    """
    return value * .01

def meter_to_inch(value):
    """ Converts meter to inch
    """
    return round(value * 39.3701,6)

def meter_to_millimeter(meter):
    """ Converts meter to millimeter
    """
    return meter * 1000

def meter_to_feet(meter):
    """ Converts meter to feet
    """
    return round(meter * 3.28084,6)

def unit_to_string(unit_settings,value):
    if unit_settings.system == 'METRIC':
        if unit_settings.length_unit == 'METERS':
            return str(round(value,3)) + "m"
        else:
            return str(round(meter_to_millimeter(value),2)) + "mm"
    elif unit_settings.system == 'IMPERIAL':
        if unit_settings.length_unit == 'FEET':
            return str(round(meter_to_feet(value),2)) + "'"
        else:
            return str(round(meter_to_inch(value),4)) + '"'
    else:
        return str(round(value,4))    