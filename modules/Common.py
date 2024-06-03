# ##############################################################################################################################
# ##############################################################################################################################
# Common functions - functions that are or may be used by all jobs and/or from within other functions.
# ##############################################################################################################################
# ##############################################################################################################################

def Get_Ctrl():
    
    # ##########################################################################
    # Check for an existing control file for the specific instance of the job
    # If it exists, get flow control parameters from it;
    # If not, initialize flow control parameters.
    # ##########################################################################
    
    CtrlFile = f"{Glb['CtrlFolder']}/{Glb['CtrlFilename']}"
    # Log_Msg(f"Check for existing control file: {CtrlFile}")
    if os.path.exists(CtrlFile):
        try:
            JobControl = json.loads(open(CtrlFile, "r").read())
            Log_Msg(f"Imported 'CtrlFile' successfully.\nJob Control:\n{str(Glb['JobControl'])}")
        except Exception:
            Exit_Job(-1, f"Error importing '{CtrlFile}' in 'Get_Ctrl':\n{traceback.format_exc()}", False)
    else:
        Log_Msg(f"No existing control file 'CtrlFile'. Initialize Job Control...", "DEBUG")
        JobControl = {
            "StepNo": 0,
            "StepResults": []
        }
    return JobControl

# ###############################################################################################################################

def Exit_Job(RC, Msg = "", Success = True):
    
    # ##########################################################################
    # Function to exit the job with various options
    # NOTE: should be called *only* by the Execute_Step function (if step failed)
    # or at end of job script.
    # ##########################################################################
    
    Log_Msg("*" * 120 + "\r\n" + "*" * 120, Level = "", AddDtStamp = False)
    Log_Ops(FinalizeFile = True)
    Status = "Success"
    if not Success:
        Status = "FAILURE"
    Log_Msg("Job complete.\r\n\tRC: " + str(RC) + "\r\n\tStatus: " + Status)
    if (Msg):
        Log_Msg("\tFinal message: " + Msg, Level = "", AddDtStamp = False)
    Log_Msg(FinalizeFile = True)
    Log_JobHistory(CompletionStatus = Status, ReturnCode = RC)
        
    sys.exit(RC)

# ###############################################################################################################################

def Log_JobHistory(CompletionStatus = None, ReturnCode = None):
    
    # ##########################################################################
    # Import modules and define variables that will be used globally in the job
    # ##########################################################################

    try:
        if CompletionStatus:
            # Log_Msg("End of job. Write job history record update statement.")
            JobHistoryFile = Glb["JobHistoryUpdateFile"]
            SQL = f"UPDATE JobHistory SET EndExecutionDateTime = '{datetime.datetime.now()}', ReturnCode = '{ReturnCode}', CompletionStatus = '{CompletionStatus}', LogFile = '{Glb['LogFile']}' WHERE InstanceID = '{Glb['InstanceRunID']}'"
        else:
            # Log_Msg("Start of job. Write job history record insert statement.")
            JobHistoryFile = Glb["JobHistoryInsertFile"]
            SQL = f"INSERT INTO JobHistory (InstanceID, ProcessName, JobName, BeginExecutionDateTime, LogFile, AutomationApp, Host, User) VALUES ('{Glb['InstanceRunID']}', '{Glb['ProcName']}', '{Glb['JobName']}', '{Glb['StartDateTime']}', '{Glb['LogFile']}.tmp', 'AutoApp', '{Glb['Host']}', '{Glb['User']}')"
        Log_Msg("Write SQL to file '" + JobHistoryFile + "':\r\n" + SQL, "DEBUG")
        try:
            FileWriter = open(JobHistoryFile, "a")
            FileWriter.write(SQL)
            Log_Msg("Wrote JobHistory SQL to '" + JobHistoryFile + "'", "DEBUG")
        except Exception:
            Log_Msg(f"Error writing SQL to '{JobHistoryFile}': {traceback.format_exc()}", "ERROR")
            return False
    except Exception:
        Log_Msg(f"Error in master try block in 'Log_JobHistory': {traceback.format_exc()}", "ERROR")
        return False

# ###############################################################################################################################

def Init_Job(tmpGlb, Args, SkipAutoApp = False):
    
    # ##########################################################################
    # Import modules and define variables that will be used globally in the job
    # ##########################################################################
    
    # Import stdlib modules that will be used in various other functions
    global datetime, glob, json, os, shutil, sys, traceback
    import datetime, glob, json, os, shutil, sys, traceback

    # Define global 'Glb' dictionary object - contains various global job-level parameters
    global Glb
    Glb = tmpGlb

    # Get *required* arguments from arguments passed to script
    try:
        Glb["Script"] = Args[0]
        Glb["ProcName"] = Args[1]
        Glb["JobName"] = Args[2]
        Glb["InstanceID"] = Args[3]
        Glb["RunCount"] = Args[4]
    except Exception:
        print(f"Error parsing 'Script', 'ProcName', 'JobName', 'InstanceID',  and/or 'RunCount' from arguments passed to script in 'Init_Job': {traceback.format_exc()}")
        return False

    # Get optional arguments from arguments passed to script
    try:
        Glb["Debug"] = Args[5]
        if str(Glb["Debug"]).upper() == 'Y':
            Glb["Debug"] = True
        else:
            Glb["Debug"] = False
    except:
        Glb["Debug"] = False
    try:
        Glb["StartAtStep"] = int(Args[6])
    except:
        Glb["StartAtStep"] = 0
    try:
        Glb["StopAfterStep"] = int(Args[7])
    except:
        Glb["StopAfterStep"] = 0
    try:
        Glb["SkipSteps"] = [int(x) for x in Args[8].split(",")]
    except:
        Glb["SkipSteps"] = []
    
    # Import environment config file and add values to Glb
    try:
        Env = json.loads(open(f"{Glb['CodeRoot']}/env/config.json", "r").read())
        for Key in Env.keys():
            Glb[Key] = Env[Key]
    except Exception:
        print(f"Error parsing 'Script', 'ProcName', 'JobName' and/or 'InstanceID' from arguments passed to script in 'Init_Job': {traceback.print_exc()}")
        return False
    
    # Validate form of Process Name
    try:
        arrProcName = Glb["ProcName"].split("-")
        if not len(arrProcName) == 4:
            print("Process name '" + Glb["ProcName"] + "' is not formatted correctly (must be '<Env>-<App>-<Client>-<Process>')")
            return False
        Glb["AppName"] = arrProcName[1]
        Glb["ClientName"] = arrProcName[2]
    except Exception:
        print(f"Error defining 'WorkingFolder', 'ArchiveFolder', 'LogFolder' and/or 'CtrlFolder': {traceback.print_exc()}")
        return False

    # Define other global variables
    Glb["InstanceRunID"] = Glb["InstanceID"] + "_" + Glb["RunCount"]
    Glb["StartDateTime"] = datetime.datetime.now()
    Glb["JobFullPath"] = f"{Glb['ProcName']}--{Glb['JobName']}"
    Glb["ChildPath"] = Glb["ProcName"].replace("-", "/")
    Glb["LogFilename"] = f"{Glb['JobName']}_{Glb['InstanceRunID']}.log"
    Glb["JobHistoryInsertFilename"] = f"I_{Glb['JobName']}_{Glb['InstanceRunID']}.sql"
    Glb["JobHistoryUpdateFilename"] = f"U_{Glb['JobName']}_{Glb['InstanceRunID']}.sql"
    Glb["OpsFilename"] = f"{Glb['JobName']}_{Glb['InstanceRunID']}.csv"
    Glb["CtrlFilename"] = f"{Glb['JobName']}_{Glb['InstanceID']}.json"
    Glb["JobLog"] = []
    Glb["User"] = os.getlogin()
    Glb["Host"] = os.uname()[1]
    
    # Validate *required* parameters from environment config file
    try:
        Glb["WorkingFolder"] = f"{Glb['WFRoot']}/{Glb['ChildPath']}"
        Glb["ArchiveFolder"] = f"{Glb['ArchiveRoot']}/{Glb['ChildPath']}"
        Glb["CtrlFolder"] = f"{Glb['CtrlRoot']}/{Glb['ChildPath']}"
        Glb["LogFile"] = f"{Glb['LogFolder']}/{Glb['LogFilename']}"
        Glb["CtrlFile"] = f"{Glb['CtrlFolder']}/{Glb['CtrlFilename']}"
        Glb["JobHistoryInsertFile"] = f"{Glb['JobHistoryFolder']}/{Glb['JobHistoryInsertFilename']}"
        Glb["JobHistoryUpdateFile"] = f"{Glb['JobHistoryFolder']}/{Glb['JobHistoryUpdateFilename']}"
        Glb["OpsFile"] = f"{Glb['OpsFolder']}/{Glb['OpsFilename']}"
        Glb["AppLP"] = f"{Glb['AppLPRoot']}/{Glb['AppName']}"
        Glb["FTPLP"] = f"{Glb['FTPLPRoot']}/{Glb['ClientName']}"
    except Exception:
        print(f"Error defining 'WorkingFolder', 'ArchiveFolder', 'LogFolder' and/or 'CtrlFolder': {traceback.print_exc()}")
        return False
    
    Glb["JobControl"] = Get_Ctrl()
    
    ProcID = 0
    ProcDesc = ""
    JobID = 0
    JobDesc = ""
    if not SkipAutoApp: # Get job parameters from AutoApp DB
        ConnectSQLResults = Connect_SQL();
        if not ConnectSQLResults[0]:
            return False
        SQL = f"SELECT id, ShortDescription FROM Processes WHERE Name = '{Glb['ProcName']}'"
        SQLResults = Exec_SQL(SQL, ConnectSQLResults[0])
        if not SQLResults[0] == 0:
            Log_Msg(f"Could not get Process ID: {SQLResults[1]}", "ERROR")
            return False
        ProcID = SQLResults[1][0][0]
        ProcDesc = SQLResults[1][0][1]
        SQL = f"SELECT id, Description FROM Jobs WHERE Process_id = {ProcID} AND Name = '{Glb['JobName']}'"
        SQLResults = Exec_SQL(SQL, ConnectSQLResults[0])
        if not SQLResults[0] == 0:
            Log_Msg(f"Could not get Job ID: {SQLResults[1]}", "ERROR")
            return False
        JobID = SQLResults[1][0][0]
        JobDesc = SQLResults[1][0][1]
        SQL = f"SELECT id, StepOrder, Title, Enabled, FunctionName, SuccessRCs, FailureRCs, WarningRCs FROM JobSteps WHERE Job_id = {JobID} ORDER BY StepOrder"
        SQLResults = Exec_SQL(SQL, ConnectSQLResults[0])
        if not SQLResults[0] == 0:
            Log_Msg(f"Could not get Job Steps: {SQLResults[1]}", "ERROR")
            return False
        JobSteps = {}
        StepIDs = []
        for Row in SQLResults[1]:
            StepIDs.append(str(Row[0]))
            JobSteps[Row[0]] = {
                "StepOrder": Row[1],
                "Title": Row[2],
                "Enabled": Row[3],
                "FuncName": Row[4],
                "SuccessRCs": Row[5],
                "FailureRCs": Row[6],
                "WarningRCs": Row[7],
                "FuncParams": {},
            }
        strStepIDs = ", ".join(StepIDs)
        SQL = f"SELECT JobStep_id, ParamName, ParamValue FROM JobStepParameters WHERE JobStep_id in ({strStepIDs}) ORDER BY JobStep_id"
        SQLResults = Exec_SQL(SQL, ConnectSQLResults[0])
        if not SQLResults[0] == 0:
            Log_Msg(f"Could not get Job Step Parameters: {SQLResults[1]}", "ERROR")
            return False
        for Row in SQLResults[1]:
            JobSteps[Row[0]]["FuncParams"][Row[1]] = Row[2]
        Glb["JobSteps"] = {}
        for Step in JobSteps.values():
            Glb["JobSteps"][Step["StepOrder"]] = {
                "Title": Step["Title"],
                "Enabled": Step["Enabled"],
                "FuncName": Step["FuncName"],
                "SuccessRCs": Step["SuccessRCs"],
                "FailureRCs": Step["FailureRCs"],
                "WarningRCs": Step["WarningRCs"],
                "FuncParams": Step["FuncParams"],
            }

    # Log start of job
    Log_JobHistory()
    Log_Msg("*" * 120 + "\r\n" + "*" * 120, Level = "", AddDtStamp = False)
    Log_Msg(f"Start of job\r\n\tProcess '{Glb['ProcName']}' (ID: {ProcID}): {ProcDesc}\r\n\tJob '{Glb['JobName']}' (ID: {JobID}): {JobDesc}\r\n\tInstance ID: {Glb['InstanceID']}\r\n\tRun count: {Glb['RunCount']}")
    if not SkipAutoApp:
        Log_Msg(f"\tStep summary:", Level = "", AddDtStamp = False)
        for Step in JobSteps.values():
            Log_Msg(f"\t\t{Step['StepOrder']}: {Step['Title']}", Level = "", AddDtStamp = False)
    Log_Msg(f"Global variables: {str(Glb)}", "DEBUG")
    
    return Glb

# ###############################################################################################################################

def Log_Msg(Msg = "" , Level = "INFO", AddDtStamp = True, WriteFile = False, FinalizeFile = False):
    
    # ##########################################################################
    # Function to write a specified message to the console in a structured format:
    # [<Date/time stamp>] [<Log level>] <Message>
    # Write to external log file as well.
    # ##########################################################################
    
    Level = Level.upper()
    DateStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if Level == "DEBUG":
        if not(Glb["Debug"]):
            return
    MsgPrefix = []
    if AddDtStamp:
        MsgPrefix.append(DateStamp)
    if Level:
        MsgPrefix.append(f"[{Level}]")
    if not Msg:
        MsgPrefix = ""
    if MsgPrefix:
        Msg = " ".join(MsgPrefix) + " " + Msg
    print(Msg)
    Glb["JobLog"].append(Msg)
    if FinalizeFile:
        WriteFile = True

    TempFile = f"{Glb['LogFile']}.tmp"
    if WriteFile:
        try:
            LogFile = open(TempFile, "a")
            LogFile.write("\r\n".join(Glb["JobLog"]) + "\r\n")
            if Level == "DEBUG":
                print(f"{DateStamp} [DEBUG] Job temp log file '{TempFile}' updated.")
            Glb["JobLog"] = []
        except Exception:
            print(f"{DateStamp} [ERROR] Error writing to temp log file '{TempFile}': {traceback.format_exc()}")
    if FinalizeFile:
        if os.path.exists(TempFile):
            try:
                shutil.move(TempFile, Glb["LogFile"])
                if Level == "DEBUG":
                    print(f"{DateStamp} [DEBUG] Job log file finalized as {Glb['LogFile']}")
            except Exception:
                print(f"{DateStamp} [ERROR] Error finalizing Ops temp datafile '{TempFile}' as '{Glb['LogFilename']}': {traceback.format_exc()}")
        else:
            print(f"{DateStamp} [ERROR] No temp log file '{TempFile}' to finalize")

# ###############################################################################################################################

def Log_Ops(Ops = [], WriteFile = True, FinalizeFile = False):
    
    # ##########################################################################
    # Function to write step Operations to structured data file(s) for later
    # insertion into log table(s)
    # ##########################################################################
    
    try:
        arrReturn = [0, None, None]
        arrOps = []
        ValidationErrors = []
        for Op in Ops:
            Log_Msg("Operation: " + str(Op), "DEBUG")
            
            objOp = {}
            
            try:
                objOp["Type"] = Op["OpType"]
            except:
                ValidationErrors.append("Missing 'OpType' property")
            try:
                objOp["StartDateTime"] = Op["StartDateTime"]
            except:
                objOp["StartDateTime"] = None
            try:
                objOp["EndDateTime"] = Op["EndDateTime"]
            except:
                ValidationErrors.append("Missing 'EndDateTime' property")
            try:
                objOp["Details"] = Op["OpDetails"]
            except:
                objOp["Details"] = None
            try:
                objOp["SourceSite_id"] = Op["SourceSiteID"]
            except:
                objOp["SourceSite_id"] = None
            try:
                objOp["SourceSite_UID_Host"] = Op["SourceSiteUIDHost"]
            except:
                objOp["SourceSite_UID_Host"] = None
            try:
                objOp["SourcePath"] = Op["SourcePath"]
            except:
                objOp["SourcePath"] = None
            try:
                objOp["SourceFilename"] = Op["SourceFilename"]
            except:
                objOp["SourceFilename"] = None
            try:
                objOp["SourceSize"] = Op["SourceSize"]
            except:
                objOp["SourceSize"] = None
            try:
                objOp["DestSite_id"] = Op["DestSiteID"]
            except:
                objOp["DestSite_id"] = None
            try:
                objOp["DestSite_UID_Host"] = Op["DestSiteUIDHost"]
            except:
                objOp["DestSite_UID_Host"] = None
            try:
                objOp["DestPath"] = Op["DestPath"]
            except:
                objOp["DestPath"] = None
            try:
                objOp["DestFilename"] = Op["DestFilename"]
            except:
                objOp["DestFilename"] = None
            try:
                objOp["DestSize"] = Op["DestSize"]
            except:
                objOp["DestSize"] = None
            try:
                objOp["SourcePathTemplate"] = Resolve_SpecialPlaceholders(Op["SourcePathTemplate"])
            except:
                objOp["SourcePathTemplate"] = None
            try:
                objOp["SourceFilenamePattern"] = Op["SourceFilenamePattern"]
            except:
                objOp["SourceFilenamePattern"] = None
            try:
                objOp["DestPathTemplate"] = Resolve_SpecialPlaceholders(Op["DestPathTemplate"])
            except:
                objOp["DestPathTemplate"] = None
            try:
                objOp["DestRenameMask"] = Op["DestRenameMask"]
            except:
                objOp["DestRenameMask"] = None
            objOp["AutomationApp"] = "JAY_AUTO"
            objOp["ProcessName"] = Glb["ProcName"]
            objOp["JobName"] = Glb["JobName"]
            objOp["InstanceID"] = f"{Glb['InstanceID']}_{str(Glb['RunCount'])}"
            objOp["PerformedBy"] = os.environ["USER"]
            
            if Glb["Debug"]:
                Log_Msg("Operation details:", "DEBUG")
                for Key in objOp.keys():
                    Log_Msg(f"\t{Key}: {objOp[Key]}", "", False)
            
            if not ValidationErrors:
                arrOps.append(objOp)
            else:
                Log_Msg(f"Operation could not be parsed successfully. Validation error(s):\n\t{str(ValidationErrors)}\nOp:\n\t{str(Op)}", "ERROR")
        
        TempFile = f"{Glb['OpsFile']}.tmp"
        TempFileExists = os.path.exists(TempFile)
        
        if arrOps and WriteFile:
            try:
                import csv
                with open(TempFile, "a", encoding="utf8", newline="") as CsvFile:
                    Csv = csv.DictWriter(CsvFile, fieldnames=arrOps[0].keys())
                    if not TempFileExists:
                        Csv.writeheader()
                    Csv.writerows(arrOps)
                Log_Msg(f"Ops data written to temp file '{TempFile}'", "DEBUG")
            except Exception:
                arrReturn[0] = -1
                arrReturn[2] = f"Error outputting Ops data to file '{TempFile}': {traceback.format_exc()}"
        
        if FinalizeFile:
            
            if TempFileExists:
                try:
                    shutil.move(TempFile, Glb["OpsFile"])
                    Log_Msg(f"Ops data file finalized as '{Glb['OpsFile']}'", "DEBUG")
                    Log_Msg()
                except Exception:
                    arrReturn[0] = -1
                    arrReturn[2] = f"Error finalizing Ops temp datafile '{TempFile}' as '{Glb['OpsFilename']}': {traceback.format_exc()}"
                    Log_Msg(arrReturn[2], "ERROR")
            else:
                Log_Msg(f"No Ops data temp file '{TempFile}' to finalize", "DEBUG")
        
    except Exception:
        arrReturn[0] = -1
        arrReturn[2] = f"Error in master try/except block in 'Log_Ops': {traceback.format_exc()}"
        Log_Msg(arrReturn[2], "ERROR")
    return arrReturn

# ###############################################################################################################################

def Execute_Step(StepParams):
    
    # ##########################################################################
    # Function to dynamically execute a specified function in a specified module
    # with parameters specified via a dict
    # ##########################################################################

    Log_Msg(f"Global variables: {str(Glb)}", "DEBUG")

    Glb["JobControl"]["StepNo"] += 1
    Title = ""
    StepFunc = ""
    ValidationErrors = []
    arrArgs = []
    StepResults = {
        "RC": 0, # standard success return code is 0; standard failure is -1; warning is 1
        "Output": {
            "Summary": [], # Human-readable list of action(s) performed by step
            "Ops": [], # list of structured 'Operation' object(s)
            "Other": [] # list of other objects
        },
        "Errors": [] # list of error(s)
    }

    try:
        Title = StepParams["Title"]
    except:
        ValidationErrors.append("'Title' parameter missing from step parameters")
    try:
        Disabled = not bool(StepParams["Enabled"])
    except:
        Disabled = False
    try:
        StepFunc = StepParams["FuncName"]
    except:
        ValidationErrors.append("'FuncName' parameter missing from step parameters")
    try:
        SuccessRCs = StepParams["SuccessRCs"]
    except:
        SuccessRCs = []
    try:
        FailureRCs = StepParams["FailureRCs"]
    except:
        FailureRCs = []
    try:
        WarningRCs = StepParams["WarningRCs"]
    except:
        WarningRCs = []
    for FuncParamName in StepParams["FuncParams"].keys():
        FuncParamValue = StepParams["FuncParams"][FuncParamName]
        arrArgs.append(f"{FuncParamName} = \"{FuncParamValue}\"")

    FuncArgs = ", ".join(str(Element) for Element in arrArgs)
    Log_Msg("Step function: " + StepFunc +"\r\n\tParameters: " + FuncArgs, "DEBUG")
    
    # Validate step parameters
    if StepFunc == "":
        ValidationErrors.append("Function name parameter ('FuncName') missing from step parameters")
    # if FuncArgs == "":
    #     ValidationErrors.append("No arguments specified for function")
    if SuccessRCs:
        try:
            SuccessRCs = [int(x) for x in SuccessRCs.split(",")]
        except:
            ValidationErrors.append("Success return codes parameter ('{SuccessRCs}') incorrectly formatted. Must be a comma-separated list of integers (e.g. '1,2,3').")
    if FailureRCs:
        try:
            FailureRCs = [int(x) for x in FailureRCs.split(",")]
        except:
            ValidationErrors.append("Failure return codes parameter ('{FailureRCs}') incorrectly formatted. Must be a comma-separated list of integers (e.g. '1,2,3').")
    if WarningRCs:
        try:
            WarningRCs = [int(x) for x in WarningRCs.split(",")]
        except:
            ValidationErrors.append("Warning return codes parameter ('{WarningRCs}') incorrectly formatted. Must be a comma-separated list of integers (e.g. '1,2,3').")
    if not SuccessRCs and not FailureRCs:
        SuccessRCs = [0]
    if ValidationErrors != []:
        ErrMsg = "Validation error(s) in Execute_Step:"
        for ValidationError in ValidationErrors:
            ErrMsg += "\n\t" + ValidationError
        Log_Msg(ErrMsg, "ERROR")
        Exit_Job(-1, "", False)
    
    # Log start of step
    Log_Msg()
    Log_Msg("*" * 120 + f"\n* Step {Glb['JobControl']['StepNo']}: {Title}", "", False)
    SkipMsg = []
    if Glb["JobControl"]["StepNo"] < Glb["StartAtStep"]:
        SkipMsg.append(f"StartAtStep {Glb['StartAtStep']} was specified")
    if Glb["StopAfterStep"] and Glb["StepNo"] > Glb["StopAfterStep"]:
        SkipMsg.append(f"StopAfterStep {Glb['StopAfterStep']} was specified")
    if Glb["JobControl"]["StepNo"] in Glb["SkipSteps"]:
        SkipMsg.append(f"SkipSteps {Glb['SkipSteps']} was specified")
    if Disabled:
        SkipMsg.append("it is disabled")
    Log_Msg("*" * 120, "", False)
    if SkipMsg:
        Log_Msg("***** SKIP step because " + ", ".join(SkipMsg) + " *****", Level = "", AddDtStamp = False)
        StepResults["RC"] = 1
        StepResults["Output"]["Summary"].append("<Skipped>")
        Glb["JobControl"]["StepResults"].append(StepResults)
        return StepResults

    # Execute step function
    try:
        Command = f"{StepFunc}({FuncArgs})"
        Log_Msg("Step function call: " + Command, "DEBUG")
        StepResults = eval(Command)
    except Exception:
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error calling step function '{StepFunc}': {traceback.format_exc()}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    if Glb["Debug"]:
        Log_Msg("Step results: \r\n\tReturn Code: " + str(StepResults["RC"]), "DEBUG")
        if StepResults["Output"]["Summary"]:
            Log_Msg("\tOutput summary: " + str(StepResults["Output"]["Summary"]), Level = "", AddDtStamp = False)
        if StepResults["Output"]["Ops"]:
            Log_Msg("\tOperation(s): " + str(StepResults["Output"]["Ops"]), Level = "", AddDtStamp = False)
        if StepResults["Output"]["Other"]:
            Log_Msg("\tOther output: " + str(StepResults["Output"]["Other"]), Level = "", AddDtStamp = False)
        if StepResults["Errors"]:
            Log_Msg("\tError(s): " + str(StepResults["Errors"]), Level = "", AddDtStamp = False)

    Log_Msg("\r\n" + "*" * 120, Level = "", AddDtStamp = False)
    LogOpsResults = Log_Ops(StepResults["Output"]["Ops"])
    Log_Msg("Log_Ops results: " + str(LogOpsResults), "DEBUG")
    
    # Determine step success/failure
    StepStatus = "Success"
    if SuccessRCs:
        if not StepResults["RC"] in SuccessRCs:
            if WarningRCs and StepResults["RC"] in WarningRCs:
                StepStatus = "WARNING"
            else: 
                StepStatus = "FAILURE"
    else:
        Log_Msg("SuccessRCs is empty.")
        if WarningRCs and StepResults["RC"] in WarningRCs:
            StepStatus = "WARNING"
        else: 
            StepStatus = "FAILURE"
    
    # Log end of step
    Log_Msg("Step " + str(Glb["JobControl"]["StepNo"]) + " complete.\r\n\tRC: " + str(StepResults["RC"]) + "\r\n\tStatus: " + StepStatus + "\r\n", WriteFile = True)

    if StepStatus == "FAILURE":
        Exit_Job(-1, "", False)

    return StepResults

# ###############################################################################################################################

def Eval_UseDate(UseDate = None):

    # ##########################################################################
    # Evaluate a passed 'UseDate' parameter and return an object in 'datetime'
    # format (or get current date/time if no value passed)
    # ##########################################################################

    if not UseDate:
        UseDate = Glb["StartDateTime"].date()
    else:
        if isinstance(UseDate, datetime.datetime):
            UseDate = UseDate.date()
        elif isinstance(UseDate, datetime.date):
            UseDate = UseDate
        else:
            try:
                YYYY = UseDate[0:4]
                MM = UseDate[4:6]
                DD = UseDate[6:8]
                UseDate = datetime.date(int(YYYY), int(MM), int(DD))
            except:
                Log_Msg(f"Cannot parse UseDate ({UseDate}). Must be a date or datetime object, or a string in 'yyyymmdd' format.", "ERROR")
                UseDate = False
        
    return UseDate

# ###############################################################################################################################

def Eval_DateTimeMask(DateTimeMask, UseDate = None):

    # ##########################################################################
    # Evaluate a date/time mask (e.g. '<yyyyMMdd_HHmmss>') and return a string
    # in the specified format based on the passed 'UseDate' value
    # ##########################################################################

    try:
        Log_Msg(f"Evaluate DateTimeMask '{DateTimeMask}' with date {UseDate}", "DEBUG")
        UseDate = Eval_UseDate(UseDate)
        if not UseDate:
            Log_Msg("'UseDate' parameter not specified correctly", "ERROR")
            return False
        Now = datetime.datetime.now()
        strDateTime = f"{UseDate.year}, {UseDate.month}, {UseDate.day}, {Now.hour}, {Now.minute}, {Now.second}"
        UseDateTime = datetime.datetime(int(UseDate.year), int(UseDate.month), int(UseDate.day), int(Now.hour), int(Now.minute), int(Now.second))
        DateTimeStamp = DateTimeMask
        DateTimeStamp = DateTimeStamp.replace("yyyy", str(UseDateTime.year))
        DateTimeStamp = DateTimeStamp.replace("yy", str(UseDateTime.year)[3])
        DateTimeStamp = DateTimeStamp.replace("MMMM", str(UseDateTime.strftime("%B")))
        DateTimeStamp = DateTimeStamp.replace("MMM", str(UseDateTime.strftime("%b")))
        DateTimeStamp = DateTimeStamp.replace("MM", str(UseDateTime.strftime("%m")))
        DateTimeStamp = DateTimeStamp.replace("M", str(int(str(UseDateTime.strftime("%m")))))
        DateTimeStamp = DateTimeStamp.replace("dddd", str(UseDateTime.strftime("%A")))
        DateTimeStamp = DateTimeStamp.replace("ddd", str(UseDateTime.strftime("%a")))
        DateTimeStamp = DateTimeStamp.replace("dd", str(UseDateTime.strftime("%d")))
        DateTimeStamp = DateTimeStamp.replace("dd", str(int(str(UseDateTime.strftime("%d")))))
        DateTimeStamp = DateTimeStamp.replace("HH", str(UseDateTime.strftime("%H")))
        DateTimeStamp = DateTimeStamp.replace("H", str(int(str(UseDateTime.strftime("%H")))))
        DateTimeStamp = DateTimeStamp.replace("hh", str(UseDateTime.strftime("%I")))
        DateTimeStamp = DateTimeStamp.replace("h", str(int(str(UseDateTime.strftime("%I")))))
        DateTimeStamp = DateTimeStamp.replace("mm", str(UseDateTime.strftime("%M")))
        DateTimeStamp = DateTimeStamp.replace("m", str(int(str(UseDateTime.strftime("%M")))))
        DateTimeStamp = DateTimeStamp.replace("ss", str(UseDateTime.strftime("%S")))
        DateTimeStamp = DateTimeStamp.replace("s", str(int(str(UseDateTime.strftime("%S")))))
        Log_Msg(f"DateTimeStamp: {DateTimeStamp}", "DEBUG")
        return DateTimeStamp
    except Exception as e:
        ErrDetail = traceback.format_exc()
        Log_Msg(f"Error in master try/except block in 'Eval_DateTimeMask': {ErrDetail}", "ERROR")
        return False

# ###############################################################################################################################

def Resolve_SpecialPlaceholders(String = ""):

    # ##########################################################################
    # Find placeholders for special paths and replace with with correct values 
    # NOTE: does not perform date/time stamp substitution
    #   (Use Sub_DateTime function for this)
    # ##########################################################################

    if String == "":
        Log_Msg("String is empty. No substitution is applicable.", "DEBUG")
        return ""

    # Perform substitution(s)
    import re
    ReturnString = String
    ReturnString = re.sub("<WorkingFolder>", Glb["WorkingFolder"], ReturnString, flags=re.IGNORECASE)
    ReturnString = re.sub("<ArchiveFolder>", Glb["ArchiveFolder"], ReturnString, flags=re.IGNORECASE)
    ReturnString = re.sub("<AppLP>", Glb["AppLP"], ReturnString, flags=re.IGNORECASE)
    ReturnString = re.sub("<FTPLP>", Glb["FTPLP"], ReturnString, flags=re.IGNORECASE)
    ReturnString = re.sub("<ProcessName>", Glb["ProcName"], ReturnString, flags=re.IGNORECASE)
    ReturnString = re.sub("<JobName>", Glb["JobName"], ReturnString, flags=re.IGNORECASE)

    Log_Msg(f"New string after substitutions: " + ReturnString, "DEBUG")

    return ReturnString

def Resolve_RenameMask(Filename = "", RenameMask = ""):

    # ##########################################################################
    # Determine destination filename based on source filename and rename mask
    # NOTE: does not perform date/time stamp substitution
    #   (Use Sub_DateTime function for this)
    # ##########################################################################

    if Filename == "":
        Log_Msg("String is empty. No substitution is applicable.", "DEBUG")
        return ""
    if RenameMask == "":
        Log_Msg("Rename Mask is empty. Dest filename is same as source filename.", "DEBUG")
        return Filename

    # Perform substitution(s)
    import re
    ReturnString = RenameMask
    SourceFilenameNoExt = os.path.splitext(Filename)[0]
    SourceExt = os.path.splitext(Filename)[1]
    ReturnString = re.sub("<SourceFilenameFull>", Filename, ReturnString, flags=re.IGNORECASE)
    ReturnString = re.sub("<SourceFilename>", SourceFilenameNoExt, ReturnString, flags=re.IGNORECASE)
    ReturnString = re.sub("<SourceExt>", SourceExt, ReturnString, flags=re.IGNORECASE)

    Log_Msg(f"Dest filename: " + ReturnString, "DEBUG")

    return ReturnString

# ###############################################################################################################################

def Sub_DateTime(String, UseDate = None):

    # ##########################################################################
    # Find date/time placeholders and replace with strings in the specified 
    # format based on the passed UseDate value
    # ##########################################################################

    UseDate = Eval_UseDate(UseDate)
    Log_Msg(f"Perform date substitution(s) on string '{String}' using date '{UseDate}'", "DEBUG")
    NewString = String
    StartIndex = NewString.find("<")
    EndIndex = NewString.find(">", StartIndex)
    if StartIndex >= 0 and EndIndex > StartIndex:
        DateTimeMask = NewString[StartIndex + 1:EndIndex]
    else:
        DateTimeMask = None
    while DateTimeMask != None:
        DateTimeStamp = Eval_DateTimeMask(DateTimeMask, UseDate)
        NewString = NewString.replace(f"<{DateTimeMask}>", DateTimeStamp)
        StartIndex = NewString.find("<")
        EndIndex = NewString.find(">", StartIndex)
        if StartIndex >= 0 and EndIndex > StartIndex:
            DateTimeMask = NewString[StartIndex + 1:EndIndex]
        else:
            DateTimeMask = None

    Log_Msg(f"New string (after) date substitution(s)): {NewString}", "DEBUG")
    return NewString

# ###############################################################################################################################

def Resolve_String(String = "", RenameMask = "", UseDate = None):

    # ##########################################################################
    # Find placeholders and replace with with correct values 
    # ##########################################################################

    if String == "":
        Log_Msg("String is empty. No substitution is applicable.", "DEBUG")
        return ""

    UseDate = Eval_UseDate(UseDate)
    
    ReturnString = String
    ReturnString = Resolve_SpecialPlaceholders(ReturnString)
    ReturnString = Resolve_RenameMask(ReturnString, RenameMask)
    ReturnString = Sub_DateTime(ReturnString, UseDate)

    Log_Msg(f"Fully-resolved string: " + ReturnString, "DEBUG")

    return ReturnString

# ###############################################################################################################################

def ConvertTo_Regex(Pattern):

    # ##########################################################################
    # Convert a wildcard pattern to a regex pattern
    # ##########################################################################

    Regex = f"^{Pattern}$"
    Regex = Regex.replace(".", "\.")
    Regex = Regex.replace("*", ".*")
    return Regex

# ###############################################################################################################################

def Get_Files(Source, UseDate = None, FilesOrFolders = "Files", Recurse = False):
    
    # ##########################################################################
    # Get file(s) matching Source specification
    # Return list of objects in "Operation" format
    # ##########################################################################

    arrReturn = [0, []]

    try:
        
        # Validate arguments
        ValidationErrors = []
        if Source.endswith("/"):
            ValidationErrors.append(f"'Source' argument ({Source}) must end with a filename or filename pattern")
        SourcePathOrig = os.path.dirname(Source)
        if SourcePathOrig == "":
            ValidationErrors.append(f"'Source' argument ({Source}) incorrectly formatted. Must contain a path and filename or filename pattern")
        FilenamePatternOrig = os.path.split(Source)[1]
        FilesOrFolders = FilesOrFolders.upper()
        if FilesOrFolders not in ['FILES', 'FOLDERS', 'BOTH']:
            ValidationErrors.append(f"'FilesOrFolders' argument ({FilesOrFolders}) invalid. Must be one of 'Files', 'Folders', or 'Both'")
        if not isinstance(Recurse, bool):
            ValidationErrors.append(f"'Recurse' argument ({Recurse}) invalid. Must be Boolean (True/False)")
        if UseDate == None or UseDate == "":
            UseDate = Glb["StartDateTime"].date()
        else:
            tmpUseDate = Eval_UseDate(UseDate)
            if not tmpUseDate:
                ValidationErrors.append(f"Cannot parse 'UseDate' parameter ({UseDate})")
            else:
                UseDate = tmpUseDate
        if ValidationErrors:
            arrReturn[1] = "Argument validation error(s) in Get_Files:\n\t" + "\n\t".join(ValidationErrors)
            Log_Msg(arrReturn[1][-1], "ERROR")
            return arrReturn
        
        # SourcePathPattern = Resolve_PathPlaceholders(SourcePathOrig)
        SourcePath = Resolve_String(SourcePathOrig, UseDate = UseDate)
        SourceFilenamePattern = Sub_DateTime(FilenamePatternOrig, UseDate = UseDate)

        if not os.path.exists(SourcePath):
            arrReturn = [1, [f"Source path '{SourcePath}' does not exist!"]]
            Log_Msg(arrReturn[1], "WARN")
            return arrReturn

        SourceDesc = f"{SourcePath}/{SourceFilenamePattern}"
        try:
            Items = glob.glob(SourceDesc)
        except Exception:
            ErrDetail = traceback.format_exc()
            arrReturn[1] = f"Error getting file(s) matching '{SourceDesc}':\n{ErrDetail}"
            Log_Msg(arrReturn[1], "ERROR")
            return arrReturn
        if not Items:
            arrReturn = [1,"No file(s) matching '{SourceDesc}'"]
            return arrReturn
        for Item in Items:
            if os.path.isfile(Item):
                SourceFilename = os.path.split(Item)[1]
                SourceSize = os.stat(Item).st_size
                arrReturn[1].append({
                    "SourcePath": SourcePath,
                    "SourceFilename": SourceFilename,
                    "SourceSize": SourceSize,
                    # "SourcePathTemplate": SourcePathPattern,
                    "SourcePathTemplate": SourcePathOrig,
                    "SourceFilenamePattern": FilenamePatternOrig
                })

        
    except Exception:
        ErrDetail = traceback.format_exc()
        Log_Msg(f"Error in master try block in 'Get_Files':\n{ErrDetail}", "ERROR")

    return arrReturn

# ###############################################################################################################################

def Connect_SQL(Host = None, DB = None, User = None, Password = None):
    
    # ##########################################################################
    # Establish a connection to a MySQL database host with a specified user.
    # (Optionally) connect to a specific database.
    # ##########################################################################

    Results = [None, []]
    try:
        if not Host:
            # Host = "localhost"
            Host = Glb["AutomationDBHost"]
        if DB == None:
            DB = Glb["AutomationDBName"]
        if not User:
            User = Glb["AutomationDBUser"]
            Password = Glb["AutomationDBPwd"]
        if not Password:
            GetCredResults = Get_Pwd(User)
            if GetCredResults[0]:
                Password = GetCredResults[0]
            else:
                Results[1].append("Error retrieving password for user ID '" + User + "':\r\n" + GetCredResults[1])
                Log_Msg(Results[1][-1], "ERROR")
                return Results
        import mysql.connector
        try:
            if DB:
                Connection = mysql.connector.connect(host = Host, user = User, password = Password, database = DB)
            else:
                Connection = mysql.connector.connect(host = Host, user = User, password = Password)
        except Exception:
            ErrMsg = f"Error connecting in 'Connect_SQL':\n{traceback.format_exc()}\n\tDB Host: {Host}\n\tDB Name: {DB}\n\tDB User: {User}\n\tDB Pwd: {Password}" 
            Log_Msg(ErrMsg, "ERROR")
            Results[1] = ErrMsg
        Log_Msg(f"Connected: {str(Connection)}", "DEBUG")
        Results[0] = Connection
    except Exception:
        ErrMsg = f"Error in master try block in 'Connect_SQL':\n{traceback.format_exc()}" 
        Log_Msg(ErrMsg, "ERROR")
        Results[1] = ErrMsg
    return Results

# ##############################################################################################################################

# Results = Common.Exec_SQL(InsertSQL, Connection, Commit = True)
def Exec_SQL(Statement, Conn = None, Host = None, DB = None, User = None, Commit = False):

    # ##########################################################################
    # Execute SQL statement against specified database host/database name
    # with specified user.
    # (Optional) - issue COMMIT statement after executing statement;
    # ##########################################################################
    
    Results = [0, None, ""]

    try:
        
        ValidationErrors = []
        if not Statement:
            ValidationErrors.append("No active Connection and no Host specified")
        if not Conn:
            if not Host:
                ValidationErrors.append("No active Connection and no Host specified")
        if ValidationErrors:
            Results[0] = -1
            Results[2] = "Validation error(s) in 'Execute_SQL':\r\n" + {str(ValidationErrors)}
            return Results
        
        if not Conn:
            ConnectSQLResults = Connect_SQL(Host, DB, User)
            if not ConnectSQLResults[0]:
                Results[0] = -1
                Results[2] = ConnectSQLResults[1]
                return Results
            # Conn = Connect_SQL(Host, DB, User, Password)
            Conn = ConnectSQLResults[0]
        
        Cursor = Conn.cursor()
        try:
            Cursor.execute(Statement)
        except Exception:
            Results[0] = -1
            Results[2] = f"Error executing SQL statement in 'Exec_SQL':\r\n{traceback.format_exc()}\r\nSQL: {Statement}"
            Log_Msg(Results[2], "ERROR")
            return Results

        if "INSERT INTO" in Statement.upper():
            Results[1] = Cursor.lastrowid
            Log_Msg("Inserted record ID: " + str(Results[1]), "DEBUG")
        if Commit:
            try:
                Conn.commit()
            except Exception:
                Results[0] = -1
                Results[2] = f"Error in commit in 'Exec_SQL':\n{traceback.format_exc()}"
                Log_Msg(Results[2], "ERROR")
                return Results
        else:
            Results[1] = Cursor.fetchall()
            Log_Msg(f"SQL results:\n{str(Results)}", "DEBUG")
            if not Results[1]:
                Results[0] = 1
    
        Cursor.close()

    except Exception:
        Results[0] = -1
        Results[2] = f"Error in master try block in 'Exec_SQL':\n{traceback.format_exc()}"
        Log_Msg(Results[2], "ERROR")
    
    return Results

# ##############################################################################################################################

def Test_Path(Path, Create = False):

    # ##########################################################################
    # Check if path exists; if not, check iteratively to see if each node exists
    # Optionally, create folder(s) iteratively
    # ##########################################################################

    Results = [True, "", ""]
    try:
        if os.path.exists(Path):
            return Results
        arrPath = Path.split("/")
        PartialPath = ""
        for Node in arrPath:
            if (Node):
                PartialPath += "/" + Node
                if not os.path.exists(PartialPath):
                    Results[0] = False
                    Results[1] = PartialPath
                    if Create:
                        try:
                            os.mkdir(PartialPath)
                            Log_Msg("Created folder '" + PartialPath + "'")
                        except Exception:
                            Results[2] = f"Error creating folder:\n{traceback.format_exc()}"
                            Log_Msg(Results[1], "ERROR")
                            return Results
                    else:
                        return Results
        Results[0] = True
        Results[1] = ""
    except Exception:
        Results[0] = False
        Results[2] = f"Error in master try block in 'Create_Path':\n{traceback.format_exc()}"
        Log_Msg(Results[2], "ERROR")
    
    return Results

def Get_Pwd(User = None):

    # ##########################################################################
    # Get password for specified User ID from Users table in AutomationDB
    # ##########################################################################

    Results = [None, ""]

    if not User:
        Results[1] = "Missing 'User' parameter!"
        Log_Msg(Results[1], "ERROR")
        return Results

    ConnectResults = Connect_SQL(Host = Glb["AutomationDBHost"], DB = Glb["AutomationDBName"], User = Glb["AutomationDBUser"], Password = Glb["AutomationDBPwd"])
    if ConnectResults[0]:
        DBConn = ConnectResults[0]
    else:
        Results[1] = ConnectResults[1]
        Log_Msg(Results[1], "ERROR")
        return Results
    
    Cursor = DBConn.cursor()
    
    try:
        Cursor.execute("SELECT Pwd FROM Credentials WHERE UID = '" + User + "'")
    except Exception:
        Results[0] = False
        Results[1] = f"Error getting password for user '" + User + "':\r\n" + traceback.format_exc()
        Log_Msg(Results[1], "ERROR")
        return Results

    Results[0] = Cursor.fetchall()[0][0]
    if not Results[0]:
        Results[0] = None
        Results[1] = "No user ID matching '" + User + "' found."

    Cursor.close()

    return Results

# ##############################################################################################################################
# ##############################################################################################################################
# Step functions
#
# NOTE: a Step function template is at the bottom of this file
# ##############################################################################################################################
# ##############################################################################################################################

def Copy_Files(Source = None, Dest = None, UseDate = None, DelSrc = False, Move = False, CreateFolder= False):
    
    # ##########################################################################
    # Step function for copying/moving files
    # ##########################################################################
    
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }
    try:
        SourcePathOrig = os.path.dirname(Source)
        FilenamePatternOrig = os.path.split(Source)[1]

        # Validate remaining parameters
        ValidationErrors = []
        if not Source:
            ValidationErrors.append("'Source' parameter missing")
        else:
            if FilenamePatternOrig == "":
                ValidationErrors.append("'Source' parameter missing filename pattern (e.g. 'file*.txt')")
        if not Dest:
            ValidationErrors.append("'Dest' parameter missing")
        if not UseDate:
            UseDate = Glb["StartDateTime"].date()
        else:
            tmpUseDate = Eval_UseDate(UseDate)
            if not tmpUseDate:
                ValidationErrors.append(f"Cannot parse 'UseDate' parameter ({UseDate})")
            else:
                UseDate = tmpUseDate
        if ValidationErrors != []:
            StepResults["RC"] = -1
            ErrMsg = "Validation error(s) in Copy_Files:\n\t" + "\n\t".join(ValidationErrors)
            StepResults["Errors"].append(ErrMsg)
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults
        if isinstance(DelSrc, str):
            if str(DelSrc).upper() == "Y":
                DelSrc = True
            else:
                DelSrc = False
        else:
            DelSrc = False
        if isinstance(Move, str):
            if str(Move).upper() == "Y":
                Move = True
            else:
                Move = False
        else:
            Move = False
        if Move:
            DelSrc = False
        if isinstance(CreateFolder, str):
            if str(CreateFolder).upper() == "Y":
                CreateFolder = True
            else:
                CreateFolder = False
        else:
            CreateFolder = False
        
        ParamList = f"\tSource: {Source}\n\tDest: {Dest}\n\tDelSrc: {DelSrc}\n\tMove: {Move}"
        Log_Msg(f"Executing 'Copy_Files' function with parameters:\n{ParamList}", "DEBUG")
        DestPathOrig = os.path.dirname(Dest)
        RenameMask = os.path.split(Dest)[1]
        
        Action = "Copy"
        if Move:
            Action = "Move"
        strSourcePath = SourcePathOrig
        SourcePath = Resolve_String(SourcePathOrig, UseDate = UseDate)
        if SourcePath != SourcePathOrig:
            strSourcePath += f" (resolved: {SourcePath})"
        strFilenamePattern = f"'{FilenamePatternOrig}'"
        FilenamePattern = Resolve_String(FilenamePatternOrig, UseDate = UseDate)
        if FilenamePattern != FilenamePatternOrig:
            strFilenamePattern += f" (resolved: {FilenamePattern})"
        ResolvedSource = SourcePath + "/" + FilenamePattern
        strDestPath = DestPathOrig
        # DestPathPattern = Resolve_PathPlaceholders(DestPathOrig)
        DestPath = Resolve_String(DestPathOrig, UseDate = UseDate)
        if DestPath != DestPathOrig:
            strDestPath += f" (resolved: {DestPath})"
        strDesc = f"{Action} file(s) matching {strFilenamePattern}\n\tFrom: {strSourcePath}\n\tTo: {strDestPath}"
        if RenameMask:
            strDesc += f"\n\tusing rename mask '{RenameMask}' with date '{UseDate}'"
        if DelSrc:
            strDesc += "\n\tand delete file(s) from source"
        Log_Msg(strDesc)
        Log_Msg()

        # Get file(s) to copy
        GetFilesResults = Get_Files(Source) # Call 'Get_Files' function to get list in "Operation" format
        if GetFilesResults[0] != 0:
            StepResults["RC"] = GetFilesResults[0]
            if GetFilesResults[0] == 1:
                Log_Msg(f"No file(s) found matching '{ResolvedSource}'", "WARN")
            return StepResults
        FilesToCopy = GetFilesResults[1]
        Log_Msg(f"File(s) to copy: {str(FilesToCopy)}", "DEBUG")
        
        # Check whether destination path exists; if not, (optionally) create it
        TestPathResults = Test_Path(DestPath, CreateFolder)
        Log_Msg("Test path results: " + str(TestPathResults), "DEBUG")
        if (not TestPathResults[0]):
            StepResults["RC"] = -1
            if TestPathResults[2]:
                StepResults["Errors"].append(TestPathResults[2])
            return StepResults

        # Copy file(s)
        for FileToCopy in FilesToCopy:
            Log_Msg(f"File to copy: {str(FileToCopy)}", "DEBUG")
            SourceFullPath = f"{FileToCopy['SourcePath']}/{FileToCopy['SourceFilename']}"
            DestFilename = Resolve_String(FileToCopy["SourceFilename"], RenameMask, UseDate)
            DestFullPath = f"{DestPath}/{DestFilename}"
            objDest = {
                "DestPath": DestPath,
                "DestFilename": DestFilename,
                "DestSize": FileToCopy["SourceSize"],
                # "DestPathTemplate": DestPathPattern,
                "DestPathTemplate": DestPathOrig,
                "DestRenameMask": RenameMask
            }
            Op = FileToCopy.copy() | objDest
            Op["StartDateTime"] = datetime.datetime.now()
            Op["OpType"] = Action.upper()
            Summary = ""
            try:
                if not Move:
                    Log_Msg(f"Copy file '{SourceFullPath}' to '{DestFullPath}'", "DEBUG")
                    shutil.copy(SourceFullPath, DestFullPath)
                    Summary = f"Copied file '{SourceFullPath}'\n\tto '{DestFullPath}'"
                    
                else:
                    Log_Msg(f"Move file '{SourceFullPath}' to '{DestFullPath}'", "DEBUG")
                    shutil.move(SourceFullPath, DestFullPath)
                    Summary = f"Moved file '{SourceFullPath}'\n\tto '{DestFullPath}'"
                Log_Msg(Summary)
                Op["EndDateTime"] = datetime.datetime.now()
                StepResults["Output"]["Ops"].append(Op)
            except Exception:
                    ErrDetail = traceback.format_exc()
                    StepResults["Errors"].append(f"Error copying/moving '{SourceFullPath}' to '{DestFullPath}':\n{ErrDetail}")
                    Log_Msg(StepResults["Errors"][-1], "ERROR")
            if DelSrc:
                Op = FileToCopy.copy()
                Op["StartDateTime"] = datetime.datetime.now()
                Op["OpType"] = "DELETE"
                Log_Msg(f"Delete file '{SourceFullPath}'", "DEBUG")
                try:
                    os.remove(SourceFullPath)
                    Summary += f" and deleted '{SourceFullPath}'"
                    Log_Msg(f"\tDeleted '{SourceFullPath}'", "", False)
                    Op["EndDateTime"] = datetime.datetime.now()
                    StepResults["Output"]["Ops"].append(Op)
                except Exception:
                    ErrDetail = traceback.format_exc()
                    StepResults["Errors"].append(f"Error deleting '{SourceFullPath}':\n{ErrDetail}")
                    Log_Msg(StepResults["Errors"][-1], "ERROR")
                    try:
                        os.remove(DestFullPath)
                        Log_Msg(f"***** cleaned up dest file '{DestFullPath}'")
                        StepResults["Output"]["Ops"].pop()
                    except Exception:
                        ErrDetail = traceback.format_exc()
                        StepResults["Errors"].append(f"Error cleaning up '{DestFullPath}':\n{ErrDetail}")
                        Log_Msg(StepResults["Errors"][-1], "ERROR")
                    return StepResults
            if Summary != "":
                StepResults["Output"]["Summary"].append(Summary)
    except Exception:
        ErrDetail = traceback.print_exc()
        Log_Msg(f"Error in master try block in 'Copy_Files':\n{ErrDetail}", "ERROR")
    if StepResults["Errors"]:
        StepResults["RC"] = -1
    return StepResults

# ##############################################################################################################################

def Delete_Files(Source, Cleanup = False):
    
    # ##########################################################################
    # Delete specified file(s)
    # (Optional) - Move to a 'Processed' subfolder with a filename prefix
    #   reflecting the job instance ID/run count 
    # ##########################################################################
    
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Validate parameters
        ValidationErrors = []
        if isinstance(Cleanup, str):
            if Cleanup.upper() == "Y":
                Cleanup = True
            else:
                Cleanup = False
        elif not isinstance(Cleanup, bool):
            ValidationErrors.append(f"Error parsing Cleanup parameter '{Source}':\r\nMust be either Boolean or 'Y/N'")
        if ValidationErrors:
            StepResults["RC"] = -1
            StepResults["Errors"].append("Validation error(s) in 'Step_Function'\r\n\t" + "\r\n\t".join(ValidationErrors))
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults
        
        # Get file(s) to delete
        GetFilesResults = Get_Files(Source) # Call 'Get_Files' function to get list in "Operation" format
        if GetFilesResults[0] != 0:
            StepResults["RC"] = GetFilesResults[0]
            if GetFilesResults[0] == 1:
                Log_Msg(f"No file(s) found matching '{Source}'", "WARN")
            return StepResults
        FilesToDelete = GetFilesResults[1]
        Log_Msg(f"File(s) to delete: {str(FilesToDelete)}", "DEBUG")
        
        # Check for Processed subfolder
        if Cleanup:
            ProcessedFolderPath = FilesToDelete[0]["SourcePath"] + "/Processed"
            if not os.path.exists(ProcessedFolderPath):
                try:
                    os.mkdir(ProcessedFolderPath)
                    Log_Msg("Created 'Processed' subfolder")
                except Exception:
                    StepResults["RC"] = -1
                    StepResults["Errors"].append(f"Error creating Processed folder '{ProcessedFolderPath}':\n{traceback.format_exc()}")
                    Log_Msg(StepResults["Errors"][-1], "ERROR")

        # Delete file(s)
        for FileToDelete in FilesToDelete:
            Log_Msg(f"File to copy: {str(FileToDelete)}", "DEBUG")
            SourceFullPath = f"{FileToDelete['SourcePath']}/{FileToDelete['SourceFilename']}"
            Op = FileToDelete.copy()
            Op["StartDateTime"] = datetime.datetime.now()
            Op["OpType"] = "DELETE"
            DeleteSummary = ""
            DeleteError = ""
            if not Cleanup:
                try:
                    os.remove(SourceFullPath)
                    DeleteSummary = f"Deleted '{SourceFullPath}'"
                except Exception:
                    DeleteError = f"Error deleting '{SourceFullPath}':\n{traceback.format_exc()}"
            else:
                ProcessedFilename = Glb["InstanceRunID"] + "_" + FileToDelete["SourceFilename"]
                ProcessedFullPath = ProcessedFolderPath + "/" + ProcessedFilename
                try:
                    shutil.move(SourceFullPath, ProcessedFullPath)
                    DeleteSummary = f"Moved '{SourceFullPath}' to 'Processed' subfolder"
                except Exception:
                    DeleteError = f"Error moving '{SourceFullPath}' to 'Processed' subfolder':\n{traceback.format_exc()}"
            if DeleteSummary:
                Log_Msg(DeleteSummary)
                StepResults["Output"]["Summary"].append(DeleteSummary)
                Op["EndDateTime"] = datetime.datetime.now()
                StepResults["Output"]["Ops"].append(Op)
            else:
                Log_Msg(DeleteError, "ERROR")
                StepResults["Errors"].append(DeleteError)

        if StepResults["Errors"]:
            StepResults["RC"] = -1

    except Exception:
        ErrDetail = traceback.format_exc()
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error in master try block in 'Delete_Files':\n{ErrDetail}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    return StepResults

# ###############################################################################################################################

def Execute_SQL(DBHost = None, DBName = None, DBUser = None, DBPwd = None, DBConn = None, SQL = None, Commit = False, OutputFile = None, IncludeHeader = False, LogOutput = True, Silent = False):

    # Call: ExecSQLResults = Execute_SQL(DBHost = "<DB host>", DBName = "<DB name>", DBUser = "DB User", SQL = "<SQL statement>")
    #       if ExecSQLResults["RC"] == 0:
    #           Tables = ExecSQLResults["Output"]["Other"]
    
    # ##########################################################################
    # Execute SQL statement against specified database host/database name
    # with specified user.
    # (Optional) - issue COMMIT statement after executing statement;
    # (Optional) - save SQL output to specified Csv file.
    # ##########################################################################
    
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Validate parameters
        # Log_Msg("Silent: " + str(Silent) + "; LogOutput: " + str(LogOutput))
        ValidationErrors = []
        if not DBHost:
            ValidationErrors.append("No Database Host specified")
        if not DBUser:
            ValidationErrors.append("No Database User specified")
        if not SQL:
            ValidationErrors.append("No SQL statement specified")
        if not type(IncludeHeader) is bool:
            if str(IncludeHeader).upper() == "Y":
                IncludeHeader = True
            else:
                IncludeHeader = False
        if not type(LogOutput) is bool:
            if str(LogOutput).upper() == "N":
                LogOutput = False
            else:
                LogOutput = True
        if not type(Silent) is bool:
            if str(Silent).upper() == "Y":
                Silent = True
            else:
                Silent = False
        if Silent:
            LogOutput = False
        if ValidationErrors:
            StepResults["RC"] = -1
            StepResults["Errors"].append("Validation error(s) in 'Execute_SQL':\r\n" + {str(ValidationErrors)})
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults
        # Log_Msg("Silent: " + str(Silent) + "; LogOutput: " + str(LogOutput))
        
        if not Silent:
            Log_Msg("Execute SQL statement:\r\n\t\"" + SQL + "\"")
            if DBConn:
                Log_Msg("\tUsing existing DB connection (Host: " + DBHost + "; Name: " + DBName + "; User: " + DBUser + ")", Level = "", AddDtStamp = False)
            else:
                Log_Msg("\tAgainst DB: " + DBName, Level = "", AddDtStamp = False)
                Log_Msg("\tOn Host: " + DBHost, Level = "", AddDtStamp = False)
                Log_Msg("\tWith User: " + DBUser, Level = "", AddDtStamp = False)
            if Commit:
                Log_Msg("Then issue COMMIT.")

        if not DBConn:
            if not DBPwd:
                GetCredResults = Get_Pwd(DBUser)
                if GetCredResults[0]:
                    DBPwd = GetCredResults[0]
                else:
                    StepResults["RC"] = -1
                    StepResults["Errors"].append("Error retrieving password for user ID '" + DBUser + "':\r\n" + GetCredResults[1])
                    Log_Msg(StepResults["Errors"][-1], "ERROR")
                    return StepResults
            ConnectSQLResults = Connect_SQL(DBHost, DBName, DBUser, DBPwd)
            if not ConnectSQLResults[0]:
                StepResults["RC"] = -1
                StepResults["Errors"].append(ConnectSQLResults[1])
                Log_Msg(StepResults["Errors"][-1], "ERROR")
                return StepResults
            DBConn = ConnectSQLResults[0]
        
        if OutputFile:
            OutputPathOrig = os.path.dirname(OutputFile)
            OutputFilenamePattern = os.path.split(OutputFile)[1]
            OutputPath = Resolve_String(OutputPathOrig)
            OutputFilename = Resolve_String(OutputFilenamePattern)
            OutputFullPath = OutputPath + "/" + OutputFilename
            if os.path.exists(OutputFullPath):
                StepResults["RC"] = -1
                StepResults["Errors"].append("Output file '" + OutputFullPath + "' already exists!")
                Log_Msg(StepResults["Errors"][-1], "ERROR")
                return StepResults
            import csv

        Cursor = DBConn.cursor()
        try:
            Cursor.execute(SQL)
        except Exception:
            StepResults["RC"] = -1
            StepResults["Errors"].append(f"Error executing SQL statement in 'Execute_SQL':\r\n{traceback.format_exc()}\r\nSQL: {SQL}")
            StepResults[2] = f"Error executing SQL statement in 'Exec_SQL':\r\n{traceback.format_exc()}\r\nSQL: {SQL}"
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults

        # Loop over SQL resultset(s)
        StartDateTime = datetime.datetime.now()
        if "INSERT INTO" in SQL.upper():
            InsertedRecordID = Cursor.lastrowid
            Log_Msg("Inserted record ID: " + str(InsertedRecordID), "DEBUG")
        else:
            InsertedRecordID = 0
        if Commit:
            RowCount = Cursor.rowcount
            Log_Msg(str(RowCount) + " row(s) affected", "DEBUG")
            if RowCount > 0:
                try:
                    DBConn.commit()
                    StepResults["Output"]["Other"].append(InsertedRecordID)
                except Exception:
                    StepResults["RC"] = -1
                    StepResults["Errors"].append(f"Error in commit in 'Execute_SQL':\n{traceback.format_exc()}")
                    Log_Msg(StepResults["Errors"][-1], "ERROR")
            else:
                Log_Msg("No row(s) affected. COMMIT not issued.", "WARN")
        else:
            NextSet = True
            while NextSet:
                SQLHeaders = [tuple([i[0] for i in Cursor.description])]
                Log_Msg("SQL result headers:\n" + str(SQLHeaders) + " (type: " + str(type(SQLHeaders)) + ")", "DEBUG")
                SQLResult = Cursor.fetchall()
                Log_Msg("SQL results:\n" + str(SQLResult) + " (type: " + str(type(SQLResult)) + ")", "DEBUG")
                for Row in SQLResult:
                    Log_Msg("Row: " + str(Row) + " (type: " + str(type(Row)) + ")", "DEBUG")
                if IncludeHeader: 
                    SQLResult = SQLHeaders + SQLResult
                StepResults["Output"]["Other"].append(SQLResult)
                if LogOutput:
                    Log_Msg()
                    Log_Msg("Result set:")
                    for Row in SQLResult:
                        arrRow = []
                        for Item in Row:
                            arrRow.append(str(Item))
                        Log_Msg("\t".join(arrRow), Level = "", AddDtStamp = False)

                if OutputFile:
                    try:
                        FileObj = open(OutputFullPath, "a", newline = "\n")
                        CsvFile = csv.writer(FileObj)
                        CsvFile.writerows(SQLResult)
                        if not Silent:
                            if LogOutput:
                                Log_Msg()
                            Log_Msg("SQL resultset written to '" + OutputFullPath + "'")
                    except Exception:
                        StepResults["RC"] = -1
                        StepResults["Errors"].append("Error writing SQL results to '" + OutputFullPath + "' in 'Execute_SQL':\n" + traceback.format_exc())
                        Log_Msg(StepResults["Errors"][-1], "ERROR")

                # Check if SQL statement returned additional resultset
                NextSet = Cursor.nextset()
        EndDateTime = datetime.datetime.now()
        Cursor.close()

        if OutputFile:
            if os.path.exists(OutputFullPath):
                StepResults["Output"]["Ops"].append({
                    "OpType": "CREATE",
                    "DestPath": OutputPath,
                    "DestFilename": OutputFilename,
                    "DestSize": os.stat(OutputFullPath).st_size,
                    "StartDateTime": StartDateTime,
                    "EndDateTime": EndDateTime,
                    "DestPathTemplate": OutputPathOrig,
                    "DestRenameMask": OutputFilenamePattern
                })

    except Exception:
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error in master try block in 'Execute_SQL':\n{traceback.format_exc()}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    # Log_Msg("Step results: " + str(StepResults))
    if not StepResults["Output"]["Other"]:
        StepResults["RC"] = 1
    return StepResults

# ##############################################################################################################################

def Send_Email(Server = None, Port = None, From = None, To = None, Cc = None, Bcc = None, Subject = None, Body = None, Attachments = None):

    # ##########################################################################
    # Step function for sending SMTP email
    # ##########################################################################
    
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Validate parameters
        ValidationErrors = []
        if not From:
            From = Glb["EmailFrom"]
        if not Server:
            Server = Glb["SMTPServer"]
        if not Port:
            Port = 25
        if not To:
            ValidationErrors.append("'To' parameter missing")
        if not Subject:
            ValidationErrors.append("'Subject' parameter missing")
        if not Body:
            ValidationErrors.append("'Body' parameter missing")
        if ValidationErrors:
            Log_Msg("Validation error(s) in Send_Email:\r\n\t" + str(ValidationErrors), "ERROR")
            StepResults["Errors"] = ValidationErrors
            return StepResults

        # ########################################################################
        # At present do not have actual code to send email
        # import smtplib
        # SMTPServer = smtplib.SMTP(Server, Port)
        # ########################################################################

        StepResults["Output"]["Summary"].append("Sent email as follows:")
        StepResults["Output"]["Summary"][-1] += "\r\n\tFrom: " + From
        StepResults["Output"]["Summary"][-1] += "\r\n\tTo: " + To
        if Cc:
            StepResults["Output"]["Summary"][-1] += "\r\n\tCc: " + Cc
        if Bcc:
            StepResults["Output"]["Summary"][-1] += "\r\n\tBcc: " + Bcc
        StepResults["Output"]["Summary"][-1] += "\r\n\tSubject: " + Subject
        StepResults["Output"]["Summary"][-1] += "\r\n\tBody:" + "\r\n\t\t" + Body.replace("\r\n", "\r\n\t\t")
        if Attachments:
            StepResults["Output"]["Summary"][-1] += "\r\n\tAttachments: " + Attachments
        Log_Msg(StepResults["Output"]["Summary"][-1])

    except Exception:
        ErrMsg = f"Error in master try block in 'Send_Email':\n{traceback.format_exc()}" 
        Log_Msg(ErrMsg, "ERROR")
        StepResults[2].append(ErrMsg)
    
    return StepResults

###############################################################################################################################

def AddUpdate_AsyncParentInstance(InstanceID = None, Status = None, DownstreamProcessName = "", DownstreamJobName = "", MaxTriggerAttempts = 0, SupportDL = ""):
    
    # ##########################################################################
    # Add or update record to AsyncParentInstances table in AutoApp DB
    # These records represent initiating instances of Async processes, used for
    # tracking whether the overall process is complete.
    # ##########################################################################
    
    # All step functions return a results object defined as follows:
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Validate parameters
        ValidationErrors = []
        if not InstanceID:
            InstanceID = Glb["InstanceID"] + "_" + Glb["RunCount"]
            Status = "I"
        if not Status:
            Status = "I"
        else:
            Status = Status.upper()
        if not Status in ["I", "E", "T", "S", "F"]:
            ValidationErrors.append("Status must be one of the following: 'I' (Parent Process initiated), 'T' (Async instance(s) initiated successfully), 'S' (Downstream Process/Job(s) triggered successfully), 'F' (Error triggering downstream Process/Job(s)))")
        if not DownstreamJobName:
            DownstreamJobName = "*"
        if not SupportDL:
            ValidationErrors.append("SupportDL must be specified")
        if not MaxTriggerAttempts:
            MaxTriggerAttempts = 3
        else:
            try:
                MaxTriggerAttempts = int(MaxTriggerAttempts)
            except:
                ValidationErrors.append("Invalid value of MaxTriggerAttempts (" + str(MaxTriggerAttempts) + "). Must be an integer.")
        if ValidationErrors:
            StepResults["RC"] = -1
            StepResults["Errors"].append("Validation error(s) in 'AddUpdate_AsyncParentInstance'\n\t" + "\n\t".join(ValidationErrors))
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults
        
        DownstreamProcessName = Resolve_SpecialPlaceholders(DownstreamProcessName)

        SQLResults = Connect_SQL(Host = Glb["AutomationDBHost"], DB = Glb["AutomationDBName"], User = Glb["AutomationDBUser"])
        if not SQLResults[0]:
            StepResults["RC"] = -1
            StepResults["Errors"] = SQLResults[1]
            return StepResults
        DBConn = SQLResults[0]

        if Status in ["I", "E"]:
            SQLStatement = f"INSERT INTO AsyncParentInstances (InstanceID, Status, DownstreamProcessName, DownstreamJobName, SupportDL) VALUES ('{InstanceID}', '{Status}', '{DownstreamProcessName}', '{DownstreamJobName}', '{SupportDL}')"
            Summary = "Inserted Async parent instance record '" + InstanceID + "' with status '" + Status + "'."
        else:
            if Status == "F":
                SQLStatement = "SELECT TriggerAttempt from AsyncParentInstances WHERE InstanceID = '" + InstanceID + "'"
                SQLResults = Execute_SQL(DBConn = DBConn, DBHost = Glb["AutomationDBHost"], DBName = Glb["AutomationDBName"], DBUser = Glb["AutomationDBUser"], SQL = SQLStatement, Silent = True)
                if not SQLResults["RC"] == 0:
                    StepResults["RC"] = -1
                    if SQLResults["RC"] == 1:
                        StepResults["Errors"].append("No existing record for Instance ID '" + InstanceID + "' found")
                    else:
                        StepResults["Errors"].append(SQLResults["Errors"][-1])
                    Log_Msg("Error updating record '" + InstanceID + " to status 'F': " + StepResults["Errors"][-1], "ERROR")
                    return StepResults
                TriggerAttempts = SQLResults["Output"]["Other"][0][0][0]
                if TriggerAttempts < MaxTriggerAttempts:
                    NewTriggerAttempt = 1 + TriggerAttempts
                    SQLStatement = f"UPDATE AsyncParentInstances SET Status = '{Status}', TriggerAttempt = {NewTriggerAttempt}, ModifiedBy = '{os.getlogin()}' WHERE InstanceID = '{InstanceID}'"
                    Summary = "Updated Async parent instance record '" + InstanceID + "' with status 'F' and TriggerAttempt " + str(NewTriggerAttempt) + "."
                else:
                    StepResults["RC"] = 1
                    StepResults["Output"]["Summary"].append("Reached max trigger attempts")
                    Log_Msg(StepResults["Output"]["Summary"][-1])
                    return StepResults
            else:
                SQLStatement = f"UPDATE AsyncParentInstances SET Status = '{Status}', ModifiedBy = '{os.getlogin()}' WHERE InstanceID = '{InstanceID}'"
                Summary = "Updated Async parent instance record '" + InstanceID + "' with status '" + Status + "."
        SQLResults = Execute_SQL(DBConn = DBConn, DBHost = Glb["AutomationDBHost"], DBName = Glb["AutomationDBName"], DBUser = Glb["AutomationDBUser"], SQL = SQLStatement, Commit = True, Silent = True)
        if not SQLResults["RC"] == 0:
            StepResults["RC"] = -1
            StepResults["Errors"] = SQLResults["Errors"]
            return StepResults
        StepResults["Output"]["Summary"].append(Summary)
    except Exception:
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error in master try block in 'AddUpdate_AsyncParentInstance':\n{traceback.format_exc()}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    Log_Msg(StepResults["Output"]["Summary"][-1])
    return StepResults

###############################################################################################################################

def AddUpdate_AsyncInstance(ParentInstanceID = None, AsyncID = None, Status = None, InitiatingCall = "", InitiatingCallResults = "", CallbackContent = ""):
    
    # ##########################################################################
    # Add or update record to AsyncInstances table in AutoApp DB
    # These records represent instances of external (i.e. Async) processes 
    # initiated by a parent AutoApp job. Used for tracking whether Async 
    # instance has completed successfully.
    # ##########################################################################
    
    # All step functions return a results object defined as follows:
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Validate parameters
        ValidationErrors = []
        if not ParentInstanceID:
            ValidationErrors.append("ParentInstanceID must be specified")
        if not AsyncID:
            AsyncID = 1
        else:
            try: 
                AsyncID = int(AsyncID)
            except: 
                ValidationErrors.append("Invalid AsyncID (" + str(AsyncID) + ") specified. Must be an integer.")
        if not Status:
            Status = "I"
        else:
            Status = Status.upper()
        if not Status in ["I", "S", "F"]:
            ValidationErrors.append("Status must be one of the following: 'I' (initiated), 'S' (completed successfully), 'F' (failed).")
        if not InitiatingCall:
            ValidationErrors.append("InitiatingCall must be specified.")
        if ValidationErrors:
            StepResults["RC"] = -1
            StepResults["Errors"].append("Validation error(s) in 'AddUpdate_AsyncInstance'\n\t" + "\n\t".join(ValidationErrors))
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults
        
        SQLResults = Connect_SQL(Host = Glb["AutomationDBHost"], DB = Glb["AutomationDBName"], User = Glb["AutomationDBUser"])
        if not SQLResults[0]:
            StepResults["RC"] = -1
            StepResults["Errors"] = SQLResults[1]
            return StepResults
        DBConn = SQLResults[0]

        if Status == "I":
            if InitiatingCallResults:
                SQLStatement = f"INSERT INTO AsyncInstances (ParentInstanceID, AsyncID, Status, InitiatingCall, InitiatingCallOutput) VALUES ('{ParentInstanceID}', {AsyncID}, 'I', '{InitiatingCall}', '{InitiatingCallResults}')"
            else:
                SQLStatement = f"INSERT INTO AsyncInstances (ParentInstanceID, AsyncID, Status, InitiatingCall) VALUES ('{ParentInstanceID}', {AsyncID}, 'I', '{InitiatingCall}')"
            Summary = "Inserted Async instance record '" + ParentInstanceID + " " + str(AsyncID) + "' with status 'I'."
        else:
            SQLStatement = "UPDATE AsyncInstances SET Status = '" + Status + "'"
            if CallbackContent:
                SQLStatement += ", CallbackContent = '" + CallbackContent + "'"
            SQLStatement += " WHERE ParentInstanceID = '" + ParentInstanceID + "' AND AsyncID = '" + str(AsyncID) + "'"
        # Log_Msg("SQL statement: " + SQLStatement)
        SQLResults = Execute_SQL(DBConn = DBConn, DBHost = Glb["AutomationDBHost"], DBName = Glb["AutomationDBName"], DBUser = Glb["AutomationDBUser"], SQL = SQLStatement, Commit = True, Silent = True)
        if not SQLResults["RC"] == 0:
            StepResults["RC"] = -1
            StepResults["Errors"] = SQLResults["Errors"]
            return StepResults
        StepResults["Output"]["Summary"].append(Summary)
    except Exception:
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error in master try block in 'AddUpdate_AsyncInstance':\n{traceback.format_exc()}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    Log_Msg(StepResults["Output"]["Summary"][-1])
    return StepResults

# ###############################################################################################################################

def Initiate_Async(ExternalCalls = None, Delimiter = ";", DownstreamProcessName = "", DownstreamJobName = "", SupportDL = ""):
    
    # ##########################################################################
    # Initiate an Asynchronous process (i.e. a process that executes some 
    # external code asynchronously, which makes a callback to indicate when it 
    # is complete, upon which downstream processing is triggered).
    # This comprises two steps:
    #  1) Initiate Async instance(s). For each:
    #    a) Make some call (e.g. API) to initiate external code;
    #    b) Insert record into AsyncInstances table for tracking.
    #  2) Insert record into AsyncParentInstances table for tracking.
    # ##########################################################################
    
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Validate parameters
        ValidationErrors = []
        if not ExternalCalls:
            ValidationErrors.append("ExternalCalls must be specified")
        # if not DownstreamProcessName:
        #     ValidationErrors.append("DownstreamProcessName must be specified")
        # if not DownstreamJobName:
        #     ValidationErrors.append("DownstreamJobName must be specified")
        if not SupportDL:
            ValidationErrors.append("SupportDL must be specified")
        if not Delimiter:
            Delimiter = ";"
        if ValidationErrors:
            StepResults["RC"] = -1
            StepResults["Errors"].append("Validation error(s) in 'Step_Function'\n\t" + "\n\t".join(ValidationErrors))
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults

        DownstreamProcessNameOrig = DownstreamProcessName
        DownstreamProcessName = Resolve_SpecialPlaceholders(DownstreamProcessName)
        InstanceID = Glb["InstanceID"] + "_" + Glb["RunCount"]

        OverallResults = {
            "ParentInstanceID": InstanceID,
            "AsyncInstances": [],
            "InsertAsyncParentInstanceResults": {}
        }
        
        # Initiate external call(s)
        arrExternalCalls = ExternalCalls.split(Delimiter)
        ExternalErrors = []
        InternalErrors = []
        AsyncID = 0
        for ExternalCall in arrExternalCalls:
            AsyncID += 1
            AsyncInstance = {
                "AsyncID": AsyncID,
                "ExternalCall": ExternalCall,
                "InitiatingCallResults": [],
                "InsertAsyncInstanceResults": {}
            }

            # ##########################################################################
            # Perform actual external call to initiate async process
            # e.g. AsyncInstance["InitiatingCallResults"] = DO_THE_THING(ExternalCall)
            # There is presently no actual code for this
            # ##########################################################################

            # ##########################################################################
            # Dummy code to test error handling for external call initiation
            #
            # All calls succeed:
            AsyncInstance["InitiatingCallResults"] = [True, f"{ExternalCall} succeeded"]
            #
            # Every other call fails:
            # if AsyncID % 2 == 0:
            #     AsyncInstance["InitiatingCallResults"] = [True, f"{ExternalCall} succeeded"]
            # else:
            #     AsyncInstance["InitiatingCallResults"] = [False, f"{ExternalCall} failed"]
            #
            # /Dummy code to test error handling for external call initiation
            # ##########################################################################

            if AsyncInstance["InitiatingCallResults"][0]: 
                Log_Msg("Async instance " + str(AsyncID) + " initiating call '" + ExternalCall + "' succeeded. Results: " + AsyncInstance["InitiatingCallResults"][1])
                
                # Insert Async Instance record
                AsyncInstance["InsertAsyncInstanceResults"] = AddUpdate_AsyncInstance(ParentInstanceID = InstanceID, AsyncID = AsyncID, Status = "I", InitiatingCall = ExternalCall, InitiatingCallResults = AsyncInstance["InitiatingCallResults"][1])
                if not AsyncInstance["InsertAsyncInstanceResults"]["RC"] == 0:
                    StepResults["Errors"].append("Error inserting Async Instance record for Async instance ID " + str(AsyncID) + ": " + str(AsyncInstance["InsertAsyncInstanceResults"]["Errors"]))
                    InternalErrors.append("Error inserting Async Instance record for Async instance ID " + str(AsyncID) + ": " + str(AsyncInstance["InsertAsyncInstanceResults"]["Errors"]))
            else:
                Log_Msg("Async instance " + str(AsyncID) + " initiating call '" + ExternalCall + "' failed. Error: " + AsyncInstance["InitiatingCallResults"][1], "ERROR")
                StepResults["Errors"].append("Error calling '" + ExternalCall + "' for Async instance ID " + str(AsyncID) + ": " + AsyncInstance["InitiatingCallResults"][1])
                ExternalErrors.append("Error calling '" + ExternalCall + "' for Async instance ID " + str(AsyncID) + ": " + AsyncInstance["InitiatingCallResults"][1])
                
            OverallResults["AsyncInstances"].append(AsyncInstance)
        
        Log_Msg()
        if StepResults["Errors"]:
            Log_Msg("Error(s) occurred initiating asynchronous process!", "ERROR")
            Status = "E"
        else:
            Status = "I"

        # Add Async Parent Instance record
        OverallResults["InsertAsyncParentInstanceResults"] = AddUpdate_AsyncParentInstance(InstanceID = InstanceID, Status = Status, DownstreamProcessName = DownstreamProcessName, DownstreamJobName = DownstreamJobName, SupportDL = SupportDL)
        if OverallResults["InsertAsyncParentInstanceResults"]["RC"] != 0:
            StepResults["Errors"].append("Error inserting Async Parent Instance record: " + str(OverallResults["InsertAsyncParentInstanceResults"]["Errors"]))
            InternalErrors.append("Error inserting Async Parent Instance record: " + str(OverallResults["InsertAsyncParentInstanceResults"]["Errors"]))

        # if ErrorList:
        if StepResults["Errors"]:
            try:
                JsonFilename = Glb["ProcName"] + "__" + Glb["JobName"] + "_" + Glb["InstanceRunID"] + ".json"
                JsonFile = Glb["WorkingFolder"] + "/" + JsonFilename
                Json = json.dumps(OverallResults, indent = 4)
                with open(JsonFile, "w") as OutFile:
                    OutFile.write(Json)
                    Log_Msg("Overall results written to '" + JsonFile + "'")
                OutFile.close()
            except Exception:
                StepResults["Errors"].append(f"Error writing overall results in 'Initiate_Async':\n{traceback.format_exc()}")
                Log_Msg(StepResults["Errors"][-1], "ERROR")
                return StepResults
            if InternalErrors:
                StepResults["RC"] = -1
            elif ExternalErrors: 
                StepResults["RC"] = 1
                SendEmailResults = Send_Email(To = SupportDL, Subject = "Error(s) initiating '" + Glb["ProcName"] + "'", Body = "\r\n".join(ExternalErrors))
                if SendEmailResults["RC"] != 0:
                    StepResults["RC"] = -1

    except Exception:
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error in master try block in 'Initiate_Async':\n{traceback.format_exc()}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    return StepResults

# ###############################################################################################################################

def Launch_Process(Application = "AutoApp", ProcessName = "", JobName = "*"):
    
    # ##########################################################################
    # Attempt to launch a specified automation process
    # (Optionally) only job(s) whose names match specified pattern
    # ##########################################################################
    
    # All step functions return a results object defined as follows:
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Validate parameters
        ValidationErrors = []
        if not Application:
            ValidationErrors.append("Application may not be blank")
        if not ProcessName:
            ValidationErrors.append("ProcessName must be specified")
        if not JobName:
            ValidationErrors.append("JobName may not be blank")
        if "*" in JobName and Application.upper() == "AUTOAPP":
            ValidationErrors.append("Only a specific job may be launched for application 'AutoApp'")
        if ValidationErrors:
            StepResults["RC"] = -1
            StepResults["Errors"].append("Validation error(s) in 'Launch_Process'\n\t" + "\n\t".join(ValidationErrors))
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults
        
        if Application.upper() == "AUTOAPP":
            import random
            import subprocess
            CharSet = "0123456789abcdefghijklmnopqrstuvwxyz"
            # ProcessName = "DEV-AUTOAPP-JAYCO-POLL_ASYNC"
            # JobName = "RUN_SCRIPT"
            InstanceID = "".join(random.choices(CharSet, k=5))
            OrderDate = datetime.datetime.now().strftime("%Y%m%d")
            RunCount = 1
            StartAtStep = ""
            StopAfterStep = ""
            SkipSteps = ""

            Command = f"python \"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/JobScript.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
            Args = f"\"/mnt/chromeos/GoogleDrive/MyDrive/AutomationApp/CodeRepo/scripts/JobScript.py\" \"{ProcessName}\" \"{JobName}\" \"{InstanceID}_{OrderDate}\" \"{str(RunCount)}\" \"{str(StartAtStep)}\" \"{str(StopAfterStep)}\" \"{SkipSteps}\""
            # print(f"{Command}")

            Log_Msg("Launch process '" + ProcessName + "', job '" + JobName + "' with command:\r\n" + Command)
            # os.system(Command)
            # subprocess.Popen(executable = "python", args = Args, shell = True)
            # Args = f"'python', '{Glb['CodeRoot']}/scripts/JobScript.py', '{ProcessName}', '{JobName}', '{InstanceID}_{OrderDate}', '{str(RunCount)}' '{str(StartAtStep)}', '{str(StopAfterStep)}', '{SkipSteps}'"
            Args = ["python", Glb["CodeRoot"] + "/scripts/JobScript.py", ProcessName, JobName, InstanceID + "_" + OrderDate, str(RunCount), str(StartAtStep), str(StopAfterStep), str(SkipSteps)]
            subprocess.Popen(Args, shell = True)

        else:
            StepResults["RC"] = -1
            StepResults["Errors"].append("Launch_Process currently only supports 'AutoApp' application")
            Log_Msg(StepResults["Errors"][-1], "ERROR")
            return StepResults
        
        # # DO THE THING
        # ThingFailed = False
        # ThingWarning = False
        # # Actual code here
        # # Define 'ThingFailed'/'ThingWarning' based on whether the action was successful, failed, or ended with warning(s)
        # if ThingFailed:
        #     StepResults["RC"] = -1
        #     StepResults["Errors"].append("<Error(s)>")
        # else:
        #     StepResults["Output"]["Summary"].append("<Human-readable summary of what the step function did>")
        #     StepResults["Output"]["Ops"].append("<'Operation' format structured object(s), if applicable>")
        #     StepResults["Output"]["Other"].append("<Other structured object(s), if applicable>")
        #     if ThingWarning:
        #         StepResults["RC"] = 1
        #         StepResults["Output"]["Summary"] = "<Human-readable summary of what the step function did (if anything)>"
        # # /DO THE THING

    except Exception:
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error in master try block in 'Launch_Process':\n{traceback.format_exc()}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    return StepResults

# ###############################################################################################################################

def Poll_AsyncElig(MaxTriggerAttempt = 3):
    
    # ##########################################################################
    # Function to poll Async DB tables for processes eligible for downstream
    # processing. For each, attempt to launch the specified downstream process &
    # job(s).
    # ##########################################################################
    
    # All step functions return a results object defined as follows:
    StepResults = {
        "RC": 0,
        "Output": {
            "Summary": [],
            "Ops": [],
            "Other": []
        },
        "Errors": []
    }

    try:
        # Connect to AutomationDB
        SQLResults = Connect_SQL(Host = Glb["AutomationDBHost"], DB = Glb["AutomationDBName"], User = Glb["AutomationDBUser"])
        if not SQLResults[0]:
            StepResults["RC"] = -1
            StepResults["Errors"] = SQLResults[1]
            return StepResults
        DBConn = SQLResults[0]

        # SQLStatement = f"SELECT P.InstanceID, P.DownstreamProcessName, P.DownstreamJobName, P.TriggerAttempt, P.SupportDL, P.SendOverrunNotification, P.SendFailureNotification FROM AsyncParentInstances P RIGHT JOIN AsyncInstances A ON A.ParentInstanceID = P.InstanceID WHERE P.Status = 'I' AND A.Status = 'S' AND P.TriggerAttempt < {MaxTriggerAttempt} AND P.DownstreamProcessName <> ''"
        SQLStatement = f"SELECT P.InstanceID, P.DownstreamProcessName, P.DownstreamJobName, P.TriggerAttempt FROM AsyncParentInstances P RIGHT JOIN AsyncInstances A ON A.ParentInstanceID = P.InstanceID WHERE P.Status = 'I' AND A.Status = 'S' AND P.TriggerAttempt < {MaxTriggerAttempt} AND P.DownstreamProcessName <> ''"
        SQLResults = Execute_SQL(DBConn = DBConn, DBHost = Glb["AutomationDBHost"], DBName = Glb["AutomationDBName"], DBUser = Glb["AutomationDBUser"], SQL = SQLStatement, Silent = True)
        if not SQLResults["RC"] == 0:
            StepResults["RC"] = -1
            StepResults["Errors"] = SQLResults["Errors"]
            return StepResults
        LastInstanceID = 0
        if not SQLResults["Output"]["Other"][0]:
            Log_Msg("No Async processes eligible for downstream processing found.")
            return StepResults
        for Row in SQLResults["Output"]["Other"][0]:
            # Log_Msg("Row: " + str(Row) + "; (" + str(type(Row)) + ")")
            InstanceID = Row[0]
            DownstreamProcessName = Row[1]
            DownstreamJobName = Row[2]
            TriggerAttempt = Row[3]
            # SupportDL = Row[4]
            # SendOverrunNotification = Row[5]
            # SendFailureNotification = Row[6]
            if InstanceID != LastInstanceID:
                LastInstanceID = InstanceID
                Log_Msg("Instance ID: " + InstanceID + "; Downstream process: " + DownstreamProcessName + "; Downstream job(s): " + DownstreamJobName + "; Trigger attempt: " + str(TriggerAttempt))
                LaunchProcessResults = Launch_Process(Application = "AutoApp", ProcessName = DownstreamProcessName, JobName = DownstreamJobName)
            else:
                Log_Msg("Instance ID '" + InstanceID + "' is the same as the previous record. Skipping...")

        # ThingFailed = False
        # ThingWarning = False
        # # Actual code here
        # # Define 'ThingFailed'/'ThingWarning' based on whether the action was successful, failed, or ended with warning(s)
        # if ThingFailed:
        #     StepResults["RC"] = -1
        #     StepResults["Errors"].append("<Error(s)>")
        # else:
        #     StepResults["Output"]["Summary"].append("<Human-readable summary of what the step function did>")
        #     StepResults["Output"]["Ops"].append("<'Operation' format structured object(s), if applicable>")
        #     StepResults["Output"]["Other"].append("<Other structured object(s), if applicable>")
        #     if ThingWarning:
        #         StepResults["RC"] = 1
        #         StepResults["Output"]["Summary"] = "<Human-readable summary of what the step function did (if anything)>"

    except Exception:
        StepResults["RC"] = -1
        StepResults["Errors"].append(f"Error in master try block in 'Poll_AsyncElig':\n{traceback.format_exc()}")
        Log_Msg(StepResults["Errors"][-1], "ERROR")
    
    return StepResults

# ###############################################################################################################################
# ###############################################################################################################################

# def Step_Function(Param1[ = <Default value>], Param2[ = <Default value>], ...):
    
#     # ##########################################################################
#     # TEMPLATE for step function
#     # ##########################################################################
    
#     # All step functions return a results object defined as follows:
#     StepResults = {
#         "RC": 0,
#         "Output": {
#             "Summary": [],
#             "Ops": [],
#             "Other": []
#         },
#         "Errors": []
#     }
#     # First element is numeric return code (standard '0' = success; '1' = warning; '-1' = failure)
#     # Second element is output, formatted as a dict as follows:
#         # Summary: Text-based, human-readable summary of what the step function did
#         # Ops: list of 'Operation' structured objects
#         # Other: list of other objects
#     # Third element is a list of error(s)

#     try:
#         # Validate parameters
#         ValidationErrors = []
#         if not <Test Param1>:
#             ValidationErrors.append("Param1 is invalid")
#         if not <Test Param2>:
#             ValidationErrors.append("Param2 is invalid")
#         if ValidationErrors:
#             StepResults["RC"] = -1
#             StepResults["Errors"].append("Validation error(s) in 'Step_Function'\n\t" + "\n\t".join(ValidationErrors))
#             Log_Msg(StepResults["Errors"][-1], "ERROR")
#             return StepResults
        
#         # DO THE THING
#         ThingFailed = False
#         ThingWarning = False
#         # Actual code here
#         # Define 'ThingFailed'/'ThingWarning' based on whether the action was successful, failed, or ended with warning(s)
#         if ThingFailed:
#             StepResults["RC"] = -1
#             StepResults["Errors"].append("<Error(s)>")
#         else:
#             StepResults["Output"]["Summary"].append("<Human-readable summary of what the step function did>")
#             StepResults["Output"]["Ops"].append("<'Operation' format structured object(s), if applicable>")
#             StepResults["Output"]["Other"].append("<Other structured object(s), if applicable>")
#             if ThingWarning:
#                 StepResults["RC"] = 1
#                 StepResults["Output"]["Summary"] = "<Human-readable summary of what the step function did (if anything)>"
#         # /DO THE THING

#     except Exception:
#         StepResults["RC"] = -1
#         StepResults["Errors"].append(f"Error in master try block in 'Step_Function':\n{traceback.format_exc()}")
#         Log_Msg(StepResults["Errors"][-1], "ERROR")
    
#     return StepResults

