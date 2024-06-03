print()

# Import modules used by all scripts
import os, sys

# Get argument(s) with which script was called
# Accepted arguments: <JobName> <InstanceID> [<Debug>] [<StartAtStep>] [<StopAfterStep>] [<SkipSteps>]
Args = sys.argv

# Get code repository root path
Glb = {}
Glb["CodeRoot"] = os.path.dirname(os.path.dirname(Args[0]))

# Append Common module (includes all custom functions)
sys.path.append(Glb["CodeRoot"] + "/modules")
import Common

# Call Init_Job to populate global dict 'Glb'
# Glb = Common.Init_Job(Glb, Args) # get steps/step parameters from AutomationDB
Glb = Common.Init_Job(Glb, Args, SkipAutoApp = True) # define Glb["JobSteps"] manually below
if not Glb:
    sys.exit(-1)
strGlb = ""
for Key in Glb.keys():
    strGlb += f"\n\t{Key}: {Glb[Key]}"
Common.Log_Msg("Global variables:" + strGlb, "DEBUG")

Glb["JobSteps"] = { # Define JobSteps here if InitJob/SkipAutoApp parameter is True
    1: {
        "Title": "Poll for Async processes eligible for downstream processing",
        "FuncName": "Poll_AsyncElig",
        "Disabled": "",
        "FuncParams": {
        }
    }
}

for StepNo in Glb["JobSteps"].keys():
    Step = Glb["JobSteps"][StepNo]
    Common.Log_Msg(str(Step), "DEBUG")
    StepResults = Common.Execute_Step(Step)

Common.Exit_Job(0, "")