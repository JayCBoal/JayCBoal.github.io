# Set global Debug variable to control logging verbosity
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
# Glb = Common.Init_Job(Glb, Args) # Get job parameters from AutoApp DB
Glb = Common.Init_Job(Glb, Args, SkipAutoApp = True) # Do *not* get job parameters from AutoApp DB (define steps via Glb["JobSteps"] below)
if not Glb:
    sys.exit(-1)
strGlb = ""
for Key in Glb.keys():
    strGlb += f"\n\t{Key}: {Glb[Key]}"
Common.Log_Msg("Global variables:" + strGlb, "DEBUG")
# Glb["InstanceID"] = "2ei6a_20240424" # Hard-code InstanceID for test purposes

# Manually define job steps (comment out this section unless 'SkipAutoApp = True' is specified in Init_Job call)
Glb["JobSteps"] = {
    1: {
        "Title": "Initiate Async process",
        "FuncName": "Initiate_Async",
        "Enabled": 1,
        "WarningRCs": "1",
        "FuncParams": {
            "ExternalCalls": "qwer;asdf;zxcv",
            "DownstreamProcessName": "<ProcessName>",
            "DownstreamJobName": "DELIVER",
            "SupportDL": "testapp_support@jayco.com"
        }
    },
    # 2: {
    #     "Title": "Insert Async instance record in AsyncInstances table in AutoApp DB",
    #     "FuncName": "AddUpdate_AsyncInstance",
    #     "FuncParams": {
    #         "ParentInstanceID": Glb["InstanceID"] + "_" + Glb["RunCount"],
    #         "AsyncID": 1,
    #         "InitiatingCall": "Geneva API/job ID 1234"
    #     }
    # },
    # 3: {
    #     "Title": "Insert Async instance record in AsyncInstances table in AutoApp DB",
    #     "FuncName": "AddUpdate_AsyncInstance",
    #     "FuncParams": {
    #         "ParentInstanceID": Glb["InstanceID"] + "_" + Glb["RunCount"],
    #         "AsyncID": 1,
    #         "InitiatingCall": "Geneva API/job ID 1234"
    #     }
    # },
    # 4: {
    #     "Title": "Update record in AsyncParentInstances table to Status 'T' (Triggered)",
    #     "FuncName": "AddUpdate_AsyncParentInstance",
    #     "FuncParams": {
    #         "InstanceID": Glb["InstanceID"] + "_" + Glb["RunCount"],
    #         "Status": "F"
    #     }
    # }
}

for StepNo in Glb["JobSteps"].keys():
    Step = Glb["JobSteps"][StepNo]
    # Common.Log_Msg(str(Step), "DEBUG")
    StepResults = Common.Execute_Step(Step)

Common.Exit_Job(0, "")