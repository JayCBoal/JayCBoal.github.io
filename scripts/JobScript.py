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
Glb = Common.Init_Job(Glb, Args) # get steps/step parameters from AutomationDB
if not Glb:
    print("Init_Job function did not return global parameters dictionary!")
    sys.exit(-1)
strGlb = ""
for Key in Glb.keys():
    strGlb += f"\n\t{Key}: {Glb[Key]}"
Common.Log_Msg("Global variables:" + strGlb, "DEBUG")

for StepNo in Glb["JobSteps"].keys():
    Step = Glb["JobSteps"][StepNo]
    Common.Log_Msg(str(Step), "DEBUG")
    StepResults = Common.Execute_Step(Step)

Common.Exit_Job(0, "")