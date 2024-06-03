import sys, random, datetime, os

Args = sys.argv
CharSet = "0123456789abcdefghijklmnopqrstuvwxyz"
InstanceID = "".join(random.choices(CharSet, k=5))
OrderDate = datetime.datetime.now().strftime("%Y%m%d")
RunCount = 1
try:
    ProcessName = Args[1]
except: 
    ProcessName = ""
try:
    JobName = Args[2]
except: 
    JobName = ""
try:
    Debug = Args[3]
except: 
    Debug = ""
try:
    StartAtStep = Args[4]
except: 
    StartAtStep = ""
try:
    StopAfterStep = Args[5]
except: 
    StopAfterStep = ""
try:
    SkipSteps = Args[6]
except: 
    SkipSteps = ""

Command = f"python \"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/JobScript.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{str(Debug)}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
print(f"{Command}")
os.system(Command)