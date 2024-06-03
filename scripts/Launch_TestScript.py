import sys, random, datetime, os

Args = sys.argv
CharSet = "0123456789abcdefghijklmnopqrstuvwxyz"
ProcessName = "DEV-TESTAPP-JAYCO-TEST_PROCESS"
JobName = "TEST_JOB"
InstanceID = "".join(random.choices(CharSet, k=5))
OrderDate = datetime.datetime.now().strftime("%Y%m%d")
RunCount = 1
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

Command = f"python \"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/TestScript.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{Debug}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
print(f"{Command}")

os.system(Command)