import sys, random, datetime, os
    

CharSet = "0123456789abcdefghijklmnopqrstuvwxyz"
ProcessName = "DEV-ABC-MASSMARKET-FEED_CLNT"
JobName = "SEND_DATA"
InstanceID = "".join(random.choices(CharSet, k=5))
OrderDate = datetime.datetime.now().strftime("%Y%m%d")
RunCount = 1


Args = sys.argv
try:
    Debug = Args[1]
except: 
    Debug = ""
try:
    StartAtStep = Args[2]
except: 
    StartAtStep = ""
try:
    StopAfterStep = Args[3]
except: 
    StopAfterStep = ""
try:
    SkipSteps = Args[4]
except: 
    SkipSteps = ""

# print(f"{InstanceID}_{OrderDate}")

# TestScript.py ProcessName JobName f"{InstanceID}_{OrderDate}" RunCount StartAtStep StopAfterStep SkipSteps

Command = f"python \"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/JobScript.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{str(Debug)}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
print(f"{Command}")

os.system(Command)