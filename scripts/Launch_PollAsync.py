import random
import datetime
import os

CharSet = "0123456789abcdefghijklmnopqrstuvwxyz"
ProcessName = "DEV-AUTOAPP-JAYCO-POLL_ASYNC"
JobName = "RUN_SCRIPT"
InstanceID = "".join(random.choices(CharSet, k=5))
OrderDate = datetime.datetime.now().strftime("%Y%m%d")
RunCount = 1
StartAtStep = ""
StopAfterStep = ""
SkipSteps = ""

Command = f"python \"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/PollAsync.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
print(f"{Command}")

os.system(Command)