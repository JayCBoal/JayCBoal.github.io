import random
import datetime
import os

CharSet = "0123456789abcdefghijklmnopqrstuvwxyz"
ProcessName = "DEV-FINANCE-DEFCO-FEED_APP"
JobName = "GET_DATA"
InstanceID = "".join(random.choices(CharSet, k=5))
OrderDate = datetime.datetime.now().strftime("%Y%m%d")
RunCount = 1
StartAtStep = ""
StopAfterStep = ""
SkipSteps = ""

# print(f"{InstanceID}_{OrderDate}")

# TestScript.py ProcessName JobName f"{InstanceID}_{OrderDate}" RunCount StartAtStep StopAfterStep SkipSteps

Command = f"python \"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/JobScript.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
print(f"{Command}")

os.system(Command)