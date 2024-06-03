import random
import datetime
import os

CharSet = "0123456789abcdefghijklmnopqrstuvwxyz"
ProcessName = "DEV-AUTOAPP-JAYCO-PARSE_OPS"
JobName = "RUN_SCRIPT"
InstanceID = "".join(random.choices(CharSet, k=5))
OrderDate = datetime.datetime.now().strftime("%Y%m%d")
RunCount = 1
StartAtStep = ""
StopAfterStep = ""
SkipSteps = ""

Command = f"python \"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/Parse_Ops.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
print(f"{Command}")

os.system(Command)