from datetime import datetime, timedelta
from pytz import timezone
import pytz

def e():
    now = datetime.now(tz=pytz.utc)
    #print(f"UTC TIME: {now}")
    now = now.astimezone(timezone('US/Eastern'))

    output = ""

    hour = now.strftime("%I")

    if hour[0] == "0":
        output += hour[1]
    else:
        output += hour
    
    output += "e"

    minute = now.strftime("%M")
    if minute[0] == "0" and minute[1] != "0":
        output += minute[1]
    elif minute[0] == "0" and minute[1] == "0":
        output += ""
    else:
        output += minute

    am = now.strftime("%p")
    if am == "AM":
        output += "a"

    print(output)

e()