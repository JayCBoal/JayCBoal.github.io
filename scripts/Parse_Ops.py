# Set global Debug variable to control logging verbosity
import os, sys, glob, csv, traceback, shutil, datetime

# Get argument(s) with which script was called
# Accepted arguments: <ProcessName> <JobName> <InstanceID> <RunCount> [<Debug>] [<StartAtStep>] [<StopAfterStep>] [<SkipSteps>]
Args = sys.argv

# Get code repository root path
Glb = {}
Glb["CodeRoot"] = os.path.dirname(os.path.dirname(Args[0]))

# Append Common module (includes all custom functions)
sys.path.append(Glb["CodeRoot"] + "/modules")
import Common

# Call Init_Job to populate global dict 'Glb'
Glb = Common.Init_Job(Glb, Args, SkipAutoApp = True)
if not Glb:
    sys.exit(-1)
strGlb = ""
for Key in Glb.keys():
    strGlb += f"\n\t{Key}: {Glb[Key]}"
Common.Log_Msg("Global variables:" + strGlb, "DEBUG")

Common.Log_Msg(f"Check for Csv file(s) in '{Glb['OpsFolder']}'")
try:
    CsvFiles = glob.glob(f"{Glb['OpsFolder']}/*.csv")
except Exception:
    Common.Exit_Job(-1, f"Error getting Csv files in '{Glb['OpsFolder']}': {traceback.format_exc()}", False, "ERROR")

Common.Log_Msg(f"Total Csv file(s) found: {len(CsvFiles)}")
if len(CsvFiles) == 0:
    Common.Exit_Job(0, "", True)
Common.Log_Msg(f"Csv file(s):\n{str(CsvFiles)}", "DEBUG")

ConnectResults = Common.Connect_SQL(Glb["AutomationDBHost"], Glb["AutomationDBName"])
if not ConnectResults[0]:
    Common.Exit_Job(-1)
Connection = ConnectResults[0]

Apps = {}
# Pair format:
# {"<App Abbr>": <App ID>}
SQL = f"SELECT id, Abbr FROM Applications ORDER BY Abbr"
Common.Log_Msg(f"Application lookup SQL: {SQL}", "DEBUG")
Results = Common.Execute_SQL(DBConn = Connection, DBHost = Glb["AutomationDBHost"], DBName = Glb["AutomationDBName"], DBUser = Glb["AutomationDBUser"], SQL = SQL, Silent = True)
if Results["RC"] == 0:
    Table = Results["Output"]["Other"][0]
elif Results["RC"] == -1:
    Common.Exit_Job(-1, f"Error getting Applications from AutoApp: {str(Results['Errors'])}", False, "ERROR")
for Row in Table:
    Apps[Row[1]] = Row[0]
Common.Log_Msg(f"Apps dict: {str(Apps)}", "DEBUG")

Entities = {}
# Pair format:
# {"<Entity Abbr>": <Entity ID>}
SQL = f"SELECT id, Abbr FROM Entities ORDER BY Abbr"
Common.Log_Msg(f"Entities lookup SQL: {SQL}", "DEBUG")
Results = Common.Exec_SQL(SQL, Connection)
Common.Log_Msg(f"Entities lookup results: {str(Results)}", "DEBUG")
Table = Results[1]
for Row in Table:
    Entities[Row[1]] = Row[0]
Common.Log_Msg(f"Entities dict: {str(Entities)}", "DEBUG")

Processes = {}
# Format:
# { "<ProcessName>": {
#         "ProcessID": 0,
#         "Jobs": {
#             "<JobName>": <JobID>
#         }
#     }
# }
SQL = "SELECT p.id AS ProcID, p.Name AS ProcName, j.id AS JobID, j.Name AS JobName FROM Processes p JOIN Jobs j ON j.Process_id = p.id ORDER BY p.Name, j.Name"
Common.Log_Msg(f"Processes/Jobs lookup SQL: {SQL}", "DEBUG")
Results = Common.Exec_SQL(SQL, Connection)
Common.Log_Msg(f"Processes/Jobs lookup results: {str(Results)}", "DEBUG")
Table = Results[1]
for Row in Table:
    try:
        Processes[Row[1]]["Jobs"][Row[3]] = Row[2]
    except:
        Processes[Row[1]] = {
            "ProcessID": Row[0],
            "Jobs": {Row[3]: Row[2]}
        }
Common.Log_Msg(f"Processes/Jobs dict: {str(Processes)}" , "DEBUG")

Sites = {}
# Pair format:
# {"<UID>@<Host>": "<Site ID>"}
SQL = "SELECT id, CONCAT(UserID, '@', Host) AS UID_Host FROM Sites ORDER BY UID_Host"
Common.Log_Msg(f"Sites lookup SQL: {SQL}", "DEBUG")
Results = Common.Exec_SQL(SQL, Connection)
Common.Log_Msg(f"Sites lookup results: {str(Results)}", "DEBUG")
Table = Results[1]
for Row in Table:
    Sites[Row[1]] = Row[0]
Common.Log_Msg(f"Sites dict: {str(Sites)}", "DEBUG")

Sources = {}
# Pair format:
# {"<Site ID>|<Path Template>|<Filename Pattern>": "<Source ID>"}
SQL = "SELECT id, Site_id, PathTemplate, FilenamePattern FROM Sources ORDER BY PathTemplate, FilenamePattern"
Common.Log_Msg(f"Sources lookup SQL: {SQL}", "DEBUG")
Results = Common.Exec_SQL(SQL, Connection)
Common.Log_Msg(f"Sources lookup results: {str(Results)}", "DEBUG")
Table = Results[1]
for Row in Table:
    if Row[1]:
        SiteID = Row[1]
    else: 
        SiteID = ""
    Sources[str(SiteID) + "|" + Row[2] + "|" + Row[3]] = Row[0]
Common.Log_Msg(f"Sources dict: {str(Sources)}", "DEBUG")

Deliveries = {}
# Pair format:
# {"<Site ID>|<Filename Pattern>|<Path Template>|<Rename Mask>": "<Source ID>"}
SQL = "SELECT id, Site_id, FilenamePattern, PathTemplate, RenameMask FROM Deliveries ORDER BY FilenamePattern, PathTemplate, RenameMask"
Common.Log_Msg(f"Deliveries lookup SQL: {SQL}", "DEBUG")
Results = Common.Exec_SQL(SQL, Connection)
Common.Log_Msg(f"Deliveries lookup results: {str(Results)}", "DEBUG")
Table = Results[1]
for Row in Table:
    if Row[1]:
        SiteID = Row[1]
    else: 
        SiteID = ""
    Deliveries[str(SiteID) + "|" + Row[2] + "|" + Row[3] + "|" + Row[4]] = Row[0]
Common.Log_Msg(f"Deliveries dict: {str(Deliveries)}", "DEBUG")

Ops = []
OpsInsertSQL = []
OpsInsertFilename = Glb["InstanceRunID"] + "_Ops_INSERT.sql"
OpsInsertFile = Glb["WorkingFolder"] + "/" + OpsInsertFilename
# SQLFile = open(OpsInsertFile, "a", newline = "\n")
OpsCounter = 0
MasterErrors = {}
SQL = []

# Loop over files
for CsvFile in CsvFiles:
    Common.Log_Msg()
    Common.Log_Msg(f"Import Csv file: {CsvFile}")
    FileErrors = {
        "Errors": [],
        "Ops": {}
    }
    try:
        File = open(CsvFile, "r")
        Reader = csv.DictReader(File)
    except Exception:
        FileErrors["Errors"].append(f"Error reading Csv file '{CsvFile}': {traceback.format_exc()}")
        Common.Log_Msg(FileErrors["Errors"][-1], "ERROR")
        MasterErrors[CsvFile] = FileErrors
        continue

    # Loop over Ops in file
    FileOpsInsertSQL = []
    FileOpsCounter = 0
    OpIndex = 0
    for Op in Reader:
        OpIndex += 1
        Common.Log_Msg("Operation " + str(OpIndex) + ": " + str(Op), "DEBUG")
        OpErrors = {
            "Op": Op,
            "Errors": [],
            "Warnings": []
        }
        if not Op["Type"]:
            OpErrors["Errors"].append("Operation Type not specified")
        else:
            if not Op["Type"].upper() in ["COPY", "MOVE", "DELETE", "CREATE", "FTPUPLOAD", "FTPDOWNLOAD", "ENCRYPT", "DECRYPT", "ZIP", "UNZIP", "SQL", "EXE"]:
                OpErrors["Errors"].append("Unrecognized Type '" + Op["Type"] + "'")
            if Op["Type"].upper() in ["COPY", "MOVE", "DELETE", "CREATE", "FTPUPLOAD", "FTPDOWNLOAD", "ENCRYPT", "DECRYPT", "ZIP", "UNZIP"]:
                if not ((Op["SourcePath"] and Op["SourceFilename"]) or (Op["DestPath"] and Op["DestFilename"])):
                    OpErrors["Errors"].append("For File Ops types, SourcePath/SourceFilename and/or DestPath/DestFilename must be specified at a minimum")
            if Op["Type"].upper() in ["SQL", "EXE"]:
                if not Op.Detail:
                    OpErrors["Errors"].append("For non-File Ops types, Detail must be specified at a minimum")
        if not Op["EndDateTime"]:
            OpErrors["Errors"].append("Operation EndDateTime not specified")
        if OpErrors["Errors"]:
            Common.Log_Msg("Validation error(s) in Operation:\r\n" + str(OpErrors["Errors"]) + "Operation:\r\n" + str(Op), "ERROR")
            FileErrors["Ops"][OpIndex] = OpErrors
            MasterErrors[CsvFile] = FileErrors
            continue

        Keys_Values = {
            "Type": Op["Type"],
            "EndDateTime": Op["EndDateTime"],
            "AutomationApp": Op["AutomationApp"],
            "ProcessName": Op["ProcessName"],
            "JobName": Op["JobName"],
            "InstanceID": Op["InstanceID"],
            "PerformedBy": Op["PerformedBy"]
        }
        if Op["StartDateTime"]:
            Keys_Values["StartDateTime"] = Op["StartDateTime"]
        if Op["Details"]:
            Keys_Values["Details"] = Op["Details"]
        if Op["SourceSite_id"]:
            Keys_Values["SourceSite_id"] = Op["SourceSite_id"]
        if Op["SourceSite_UID_Host"]:
            Keys_Values["SourceSite_UID_Host"] = Op["SourceSite_UID_Host"]
        if Op["SourcePath"]:
            Keys_Values["SourcePath"] = Op["SourcePath"]
        if Op["SourceFilename"]:
            Keys_Values["SourceFilename"] = Op["SourceFilename"]
        if Op["SourceSize"]:
            Keys_Values["SourceSize"] = Op["SourceSize"]
        if Op["DestSite_id"]:
            Keys_Values["DestSite_id"] = Op["DestSite_id"]
        if Op["DestSite_UID_Host"]:
            Keys_Values["DestSite_UID_Host"] = Op["DestSite_UID_Host"]
        if Op["DestPath"]:
            Keys_Values["DestPath"] = Op["DestPath"]
        if Op["DestFilename"]:
            Keys_Values["DestFilename"] = Op["DestFilename"]
        if Op["DestSize"]:
            Keys_Values["DestSize"] = Op["DestSize"]
        if Op["SourcePathTemplate"]:
            Keys_Values["SourcePathTemplate"] = Op["SourcePathTemplate"]
        if Op["SourceFilenamePattern"]:
            Keys_Values["SourceFilenamePattern"] = Op["SourceFilenamePattern"]
        if Op["DestPathTemplate"]:
            Keys_Values["DestPathTemplate"] = Op["DestPathTemplate"]
        if Op["DestRenameMask"]:
            Keys_Values["DestRenameMask"] = Op["DestRenameMask"]
        Keys = ", ".join(Keys_Values.keys())
        Values = "'" + "', '".join(Keys_Values.values()) + "'"
        # OpsInsertSQL.append(f"INSERT INTO Operations ({Keys}) VALUES ({Values})") # Operation INSERTs will be executed after all files have been parsed
        FileOpsInsertSQL.append(f"INSERT INTO Operations ({Keys}) VALUES ({Values})") # Operation INSERTs will be executed after all files have been parsed
        FileOpsCounter += 1
        # Common.Log_Msg("Op insert SQL: " + OpsInsertSQL[-1], "DEBUG")
        Common.Log_Msg("Op insert SQL: " + FileOpsInsertSQL[-1], "DEBUG")

        ChildPath = Op["ProcessName"].replace("-", "/")
        WorkingFolder = f"{Glb['WFRoot']}/{ChildPath}"
        ArchiveFolder = f"{Glb['ArchiveRoot']}/{ChildPath}"
        AppAbbr = Op["ProcessName"].split("-")[1]
        AppLP = f"{Glb['AppLPRoot']}/{AppAbbr}"
        CliAbbr = Op["ProcessName"].split("-")[2]
        FTPLP = f"{Glb['FTPLPRoot']}/{CliAbbr}"
        
        # Check if Application is known:
        try:
            AppID = Apps[AppAbbr]
            Common.Log_Msg(f"Application '" + AppAbbr + "' (ID: " + str(AppID) + ") found in Apps dict", "DEBUG")
        except:
            OpErrors["Warnings"].append("Unknown App abbreviation '" + AppAbbr + "'")
            AppName = "<Abbr_" + AppAbbr + ">" 
            AppInsertSQL = "INSERT INTO Applications (Name, Abbr) VALUES ('" + AppName + "', '" +  AppAbbr + "')"
            Results = Common.Exec_SQL(AppInsertSQL, Connection, Commit = True)
            if Results[0] == 0:
                AppID = Results[1]
                Apps[AppAbbr] = AppID
                OpErrors["Warnings"][-1] += ". Inserted into Applications table with Name '" + AppName + "' (id :" + str(AppID) + ")"
                Common.Log_Msg(OpErrors["Warnings"][-1] + " and added to Apps dict", "WARN")
            else:
                OpErrors["Errors"].append("Error inserting App record:\r\n" + Results[2] + "\r\nSQL: " + AppInsertSQL)
                Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                FileErrors["Ops"][OpIndex] = OpErrors
                MasterErrors[CsvFile] = FileErrors
                continue
        Common.Log_Msg("App ID: " + str(AppID), "DEBUG")

        # Check if Client is known:
        try:
            CliID = Entities[CliAbbr]
            Common.Log_Msg(f"Client '{CliAbbr}' found in Entities dict (ID: {CliID})", "DEBUG")
        except:
            OpErrors["Warnings"].append("Unknown Client abbreviation '" + CliAbbr + "'")
            CliName = "<Abbr_" + CliAbbr + ">"
            CliInsertSQL = "INSERT INTO Entities (LegalName, Abbr) VALUES ('" + CliName + "', '" +  CliAbbr + "')"
            Results = Common.Exec_SQL(CliInsertSQL, Connection, Commit = True)
            if Results[0] == 0:
                CliID = Results[1]
                Entities[CliAbbr] = CliID
                OpErrors["Warnings"][-1] += ". Inserted into Entities table with Name '" + CliName + "' (id : " + str(CliID) + ")"
                Common.Log_Msg(OpErrors["Warnings"][-1] + " and added to Entities dict", "WARN")
            else:
                OpErrors["Errors"].append("Error inserting Entity record:\r\n" + Results[2] + "\r\nSQL: " + CliInsertSQL)
                Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                FileErrors["Ops"][OpIndex] = OpErrors
                MasterErrors[CsvFile] = FileErrors
                continue
        Common.Log_Msg("Client ID: " + str(CliID), "DEBUG")

        # Check if Process is known:
        try:
            ProcessID = Processes[Op["ProcessName"]]["ProcessID"]
            Common.Log_Msg("Process '" + Op["ProcessName"] + "' found in Processes dict (ID: " + str(ProcessID) + ")", "DEBUG")
        except:
            OpErrors["Warnings"].append("Unknown Process Name '" + Op["ProcessName"] + "'")
            ProcInsertSQL = "INSERT INTO Processes (Name, Application_id, Client_id) VALUES ('" + Op["ProcessName"] + "', " +  str(AppID) + ", " + str(CliID) + ")"
            Results = Common.Exec_SQL(ProcInsertSQL, Connection, Commit = True)
            if Results[0] == 0:
                ProcessID = Results[1]
                OpErrors["Warnings"][-1] += ". Inserted into Processes table (id: " + str(ProcessID) + ")"
                JobInsertSQL = "INSERT INTO Jobs (Process_id, Name) VALUES (" + str(ProcessID) + ", '" + Op["JobName"] + "')"
                Results = Common.Exec_SQL(JobInsertSQL, Connection, Commit = True)
                if Results[0] == 0:
                    JobID = Results[1]
                    OpErrors["Warnings"][-1] += ". Inserted Job '" + Op["JobName"] + "' into Jobs table (id: " + str(JobID) + ")"
                    Processes[Op["ProcessName"]] = {
                        "ProcessID": ProcessID,
                        "Jobs": {Op["JobName"]: JobID}
                    }
                    Common.Log_Msg(OpErrors["Warnings"][-1] + ". Added Process & Job to Processes dict", "WARN")
                else:
                    OpErrors["Errors"].append("Error inserting Job record:\r\n" + Results[2] + "\r\nSQL: " + JobInsertSQL)
                    Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                    Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                    FileErrors["Ops"][OpIndex] = OpErrors
                    MasterErrors[CsvFile] = FileErrors
                    continue
            else:
                OpErrors["Errors"].append("Error inserting Process record:\r\n" + Results[2] + "\r\nSQL: " + JobInsertSQL)
                Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                FileErrors["Ops"][OpIndex] = OpErrors
                MasterErrors[CsvFile] = FileErrors
                continue
        Common.Log_Msg("Process ID: " + str(ProcessID), "DEBUG")
        
        # Check if Job is known:
        try:
            JobID = Processes[Op["ProcessName"]]["Jobs"][Op["JobName"]]
            Common.Log_Msg("Job '" + Op["JobName"] + "' found in Processes/Jobs dict (ID: " + str(JobID) + ")", "DEBUG")
        except:
            OpErrors["Warnings"].append("Unknown Job Name '" + Op["JobName"] + "'")
            JobInsertSQL = "INSERT INTO Jobs (Process_id, Name) VALUES (" + str(ProcessID) + ", '" + Op["JobName"] + "')"
            Results = Common.Exec_SQL(JobInsertSQL, Connection, Commit = True)
            if Results[0] == 0:
                JobID = Results[1]
                OpErrors["Warnings"][-1] += ". Inserted into Jobs table (id: " + str(JobID) + ")"
                Processes[Op["ProcessName"]]["Jobs"][Op["JobName"]] = JobID
                Common.Log_Msg(OpErrors["Warnings"][-1] + ". Added Process & Job to Processes dict", "WARN")
            else:
                OpErrors["Errors"].append("Error inserting Job record:\r\n" + Results[2] + "\r\nSQL: " + JobInsertSQL)
                Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                FileErrors["Ops"][OpIndex] = OpErrors
                MasterErrors[CsvFile] = FileErrors
                continue
        
        # Check if Site is known
        if Op["SourceSite_id"] or Op["DestSite_id"]:
            if Op["SourceSite_id"]:
                SiteID = Op["SourceSite_id"]
            else:
                SiteID = Op["DestSite_id"]
        elif Op["SourceSite_UID_Host"] or Op["DestSite_UID_Host"]:
            if Op["SourceSite_UID_Host"]:
                Site_UID_Host = Op["SourceSite_UID_Host"]
            else:
                Site_UID_Host = Op["DestSite_UID_Host"]
            try:
                SiteID = Sites[Site_UID_Host]
                Common.Log_Msg("Site '" +  Site_UID_Host + "' found in Sites table (id: " + SiteID + ")", "DEBUG")
            except:
                OpErrors["Warnings"].append("Unknown Site UID@Host '" + Site_UID_Host + "'")
                UID = Site_UID_Host.split("@")[0]
                Host = Site_UID_Host.split("@")[1]
                SiteName = "<" + UID + "@" + Host + ">"
                SiteInsertSQL = "INSERT INTO Sites (Name, Host, UserID) VALUES ('" + SiteName + "', '" + Host + "', '" + UID + "')"
                Results = Common.Exec_SQL(SiteInsertSQL, Connection, Commit = True)
                if Results[0] == 0:
                    SiteID = Results[1]
                    OpErrors["Warnings"][-1] += ". Inserted into Sites table with Name '" + SiteName + "' (id: " + str(SiteID) + ")"
                    Sites[Site_UID_Host] = SiteID
                    Common.Log_Msg(OpErrors["Warnings"][-1] + " and added to Sites dict", "WARN")
                else:
                    OpErrors["Errors"].append("Error inserting Site record:\r\n" + Results[2] + "\r\nSQL: " + SiteInsertSQL)
                    Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                    Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                    FileErrors["Ops"][OpIndex] = OpErrors
                    MasterErrors[CsvFile] = FileErrors
                    continue
        else:
            SiteID = ""

        # Check if Operation is from a 'Source' and whether it is known
        for i in [1]:
            if not Op["SourcePathTemplate"]:
                Common.Log_Msg("Op SourcePathTemplate is empty - this is not a 'Source'", "DEBUG")
                break
            if WorkingFolder.upper() in Op["SourcePathTemplate"].upper() or "<WORKINGFOLDER>" in Op["SourcePathTemplate"].upper():
                Common.Log_Msg("Op SourcePathTemplate is Working Folder - this is not a 'Source'", "DEBUG")
                break
            if not (WorkingFolder.upper() in Op["DestPathTemplate"].upper() or "<WORKINGFOLDER>" in Op["DestPathTemplate"].upper()):
                Common.Log_Msg("Op DestPathTemplate is not Working Folder - this is not a 'Source'", "DEBUG")
                break
            SourceDescriptor = str(SiteID) + "|" + Op["SourcePathTemplate"] + "|" + Op["SourceFilenamePattern"]
            Common.Log_Msg("'Source' descriptor: " + SourceDescriptor, "DEBUG")
            try:
                SourceID = Sources[SourceDescriptor]
                Common.Log_Msg("Source '" +  SourceDescriptor + "' found in Sources table (id: " + str(SourceID) + ")", "DEBUG")
            except:
                OpErrors["Warnings"].append("Unknown Source '" + SourceDescriptor + "'")
                if SiteID:
                    SourceInsertSQL = "INSERT INTO Sources (Site_id, PathTemplate, FilenamePattern) VALUES (" + str(SiteID) + ", '" + Op["SourcePathTemplate"] + "', '" + Op["SourceFilenamePattern"] + "')"
                else:
                    SourceInsertSQL = "INSERT INTO Sources (PathTemplate, FilenamePattern) VALUES ('" + Op["SourcePathTemplate"] + "', '" + Op["SourceFilenamePattern"] + "')"
                Common.Log_Msg("'Source' insert SQL: " + SourceInsertSQL, "DEBUG")
                Results = Common.Exec_SQL(SourceInsertSQL, Connection, Commit = True)
                if Results[0] == 0:
                    SourceID = Results[1]
                    OpErrors["Warnings"][-1] += ". Inserted into Sources table (id: " + str(SourceID) + ")"
                    Sources[SourceDescriptor] = SourceID
                    Common.Log_Msg(OpErrors["Warnings"][-1] + " and added to Sources dict", "WARN")
                else:
                    OpErrors["Errors"].append("Error inserting Source record:\r\n" + Results[2] + "\r\nSQL: " + SourceInsertSQL)
                    Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                    Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                    FileErrors["Ops"][OpIndex] = OpErrors
                    MasterErrors[CsvFile] = FileErrors
                    continue

        # Check if Operation is to a 'Delivery' and whether it is known
        for i in [1]:
            if not Op["DestPathTemplate"]:
                Common.Log_Msg("Op DestPathTemplate is empty - this is not a 'Delivery'", "DEBUG")
                break
            if not (WorkingFolder.upper() in Op["SourcePathTemplate"].upper() or "<WORKINGFOLDER>" in Op["SourcePathTemplate"].upper()):
                Common.Log_Msg("Op SourcePathTemplate is not Working Folder - this is not a 'Delivery'", "DEBUG")
                break
            if WorkingFolder.upper() in Op["DestPathTemplate"].upper() or "<WORKINGFOLDER>" in Op["DestPathTemplate"].upper():
                Common.Log_Msg("Op DestPathTemplate is Working Folder - this is not a 'Delivery'", "DEBUG")
                break
            if ArchiveFolder.upper() in Op["DestPathTemplate"].upper() or "<ARCHIVEFOLDER>" in Op["DestPathTemplate"].upper():
                Common.Log_Msg("Op DestPathTemplate is Archive Folder - this is not a 'Delivery'", "DEBUG")
                break
            if FTPLP.upper() in Op["DestPathTemplate"].upper() or "<FTPLP>" in Op["DestPathTemplate"].upper():
                Common.Log_Msg("Op DestPathTemplate is FTP Landing Pad - this is not a 'Delivery'", "DEBUG")
                break
            DeliveryDescriptor = str(SiteID) + "|" + Op["SourceFilenamePattern"] + "|" + Op["DestPathTemplate"] + "|" + Op["DestRenameMask"]
            Common.Log_Msg("'Delivery' descriptor: " + DeliveryDescriptor, "DEBUG")
            try:
                DeliveryID = Deliveries[DeliveryDescriptor]
                Common.Log_Msg("Delivery '" +  DeliveryDescriptor + "' found in Deliveries table (id: " + str(DeliveryID) + ")", "DEBUG")
            except:
                OpErrors["Warnings"].append("Unknown Delivery '" + DeliveryDescriptor + "'")
                if SiteID:
                    DeliveryInsertSQL = "INSERT INTO Deliveries (Site_id, FilenamePattern, PathTemplate, RenameMask) VALUES (" + SiteID + ", '" + Op["SourceFilenamePattern"] + "', '" + Op["DestPathTemplate"] + "', '" + Op["DestRenameMask"] + "')"
                else:
                    DeliveryInsertSQL = "INSERT INTO Deliveries (FilenamePattern, PathTemplate, RenameMask) VALUES ('" + Op["SourceFilenamePattern"] + "', '" + Op["DestPathTemplate"] + "', '" + Op["DestRenameMask"] + "')"
                Common.Log_Msg("'Delivery' insert SQL: " + DeliveryInsertSQL, "DEBUG")
                Results = Common.Exec_SQL(DeliveryInsertSQL, Connection, Commit = True)
                if Results[0] == 0:
                    DeliveryID = Results[1]
                    OpErrors["Warnings"][-1] += ". Inserted into Deliveries table (id: " + str(DeliveryID) + ")"
                    Deliveries[DeliveryDescriptor] = DeliveryID
                    Common.Log_Msg(OpErrors["Warnings"][-1] + " and added to Deliveries dict", "WARN")
                else:
                    OpErrors["Errors"].append("Error inserting Delivery record:\r\n" + Results[2] + "\r\nSQL: " + DeliveryInsertSQL)
                    Common.Log_Msg(OpErrors["Warnings"][-1], "WARN")
                    Common.Log_Msg(OpErrors["Errors"][-1], "ERROR")
                    FileErrors["Ops"][OpIndex] = OpErrors
                    MasterErrors[CsvFile] = FileErrors
                    continue
        
        if OpErrors["Errors"] or OpErrors["Warnings"]:
            FileErrors["Ops"][OpIndex] = OpErrors

    Common.Log_Msg(str(FileOpsCounter) + " Operations found in Csv file")

    if FileOpsInsertSQL:
        try:
            SQLFile = open(OpsInsertFile, "a", newline = "\n")
            SQLFile.write(";\r\n".join(FileOpsInsertSQL) + ";\r\n")
            Common.Log_Msg("Ops INSERT statement(s) appended to '" + OpsInsertFile + "'")
            SQLFile.close()
        except Exception:
            FileErrors["Errors"].append(f"Error writing Ops INSERT SQL for file '" + CsvFile + "' to '" + OpsInsertFile + "': " + traceback.format_exc())
            Common.Log_Msg(FileErrors["Errors"][-1], "ERROR")
            MasterErrors[CsvFile] = FileErrors

    FileError = False
    if FileErrors["Ops"]:
        FileError = False
        for OpIndex in FileErrors["Ops"].keys():
            Op = FileErrors["Ops"][OpIndex]
            if Op["Errors"]:
                FileError = True
                break
    if FileError:
        MasterErrors[CsvFile] = FileErrors
        ErrorPath = Glb['OpsFolder'] + "/errors"
        ErrorFilePath = CsvFile.replace(Glb['OpsFolder'], ErrorPath)
        try:
            shutil.move(CsvFile, ErrorFilePath)
            Common.Log_Msg("Csv file '" + CsvFile + "' moved to '" + ErrorFilePath + "'")
        except Exception:
            FileErrors["Errors"].append(f"Error moving Csv file '" + CsvFile + "' to '" + ErrorFilePath + "': " + traceback.format_exc())
            Common.Log_Msg(FileErrors["Errors"][-1], "ERROR")
            MasterErrors[CsvFile] = FileErrors
    else:
        ArchivePath = Glb["ArchiveRoot"] + "/" + Glb["ChildPath"]
        CsvFilename = os.path.basename(CsvFile)
        ArchiveFilename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + CsvFilename
        ArchiveFilePath = ArchivePath + "/" + ArchiveFilename
        try:
            shutil.move(CsvFile, ArchiveFilePath)
            Common.Log_Msg("Csv file '" + CsvFile + "'\r\n\tarchived to '" + ArchiveFilePath + "'")
        except Exception:
            FileErrors["Errors"].append(f"Error archiving Csv file '" + CsvFile + "' to '" + ArchiveFilePath + "': " + traceback.format_exc())
            Common.Log_Msg(FileErrors["Errors"][-1], "ERROR")
            MasterErrors[CsvFile] = FileErrors

if os.path.exists(OpsInsertFile):
    try:
        SQLFile = open(OpsInsertFile, "r")
        OpsInsertSQL = SQLFile.readlines()
        Common.Log_Msg()
        Common.Log_Msg("Total Ops to insert: " + str(len(OpsInsertSQL)))
        InsertCounter = 0
        InsertErrors = []
        for InsertSQL in OpsInsertSQL:
            Common.Log_Msg("Op insert SQL: " + InsertSQL, "DEBUG")
            Results = Common.Exec_SQL(InsertSQL, Connection, Commit = True)
            Common.Log_Msg(f"Operation insert results: {str(Results)}", "DEBUG")
            if Results[0] == 0:
                OpID = Results[1]
                Common.Log_Msg(f"Inserted Operation record (ID: {OpID})", "DEBUG")
                InsertCounter += 1
            else:
                InsertErrors.append("Error inserting Operation record:\r\n" + Results[2])
                Common.Log_Msg(InsertErrors[-1], "ERROR")
        Common.Log_Msg()
        Common.Log_Msg("Inserted " + str(InsertCounter) + " Ops records.")
        SQLFile.close()
        ArchiveFilename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + OpsInsertFilename
        ArchiveFilePath = ArchivePath + "/" + ArchiveFilename
        try:
            shutil.move(OpsInsertFile, ArchiveFilePath)
            Common.Log_Msg("Ops INSERT SQL file '" + OpsInsertFile + "'\r\n\tarchived to '" + ArchiveFilePath + "'")
        except Exception:
            FileErrors["Errors"].append(f"Error archiving Ops INSERT SQL file '" + OpsInsertFile + "' to '" + ArchiveFilePath + "': " + traceback.format_exc())
            Common.Log_Msg(FileErrors["Errors"][-1], "ERROR")
            MasterErrors[CsvFile] = FileErrors
    except Exception:
        FileErrors["Errors"].append(f"Error writing Ops INSERT SQL for file '" + CsvFile + "' to '" + OpsInsertFile + "': " + traceback.format_exc())
        Common.Log_Msg(FileErrors["Errors"][-1], "ERROR")
        MasterErrors[CsvFile] = FileErrors

Errors = False
if MasterErrors:
    Common.Log_Msg("Error(s)/warning(s) encountered parsing Ops:", "ERROR")
    for File in MasterErrors.keys():
        Common.Log_Msg("\tFile:" + File, Level = "", AddDtStamp = False)
        FileErrors = MasterErrors[File]
        if FileErrors["Errors"]:
            Errors = True
            Common.Log_Msg("\t\tFile-level error(s):", Level = "", AddDtStamp = False)
            for Error in FileErrors["Errors"]:
                Common.Log_Msg("\t\t\t" + Error, Level = "", AddDtStamp = False)
        if FileErrors["Ops"]:
            for OpIndex in FileErrors["Ops"].keys():
                OpObj = FileErrors["Ops"][OpIndex]
                if OpObj["Errors"]:
                    Errors = True
                    Common.Log_Msg("\t\tOps-level Errors:", Level = "", AddDtStamp = False)
                    for Error in OpObj["Errors"]:
                        Common.Log_Msg("\t\t\t" + Error, Level = "", AddDtStamp = False)
                if OpObj["Warnings"]:
                    Common.Log_Msg("\t\tOps-level Warnings:", Level = "", AddDtStamp = False)
                    for Warning in OpObj["Warnings"]:
                        Common.Log_Msg("\t\t\t" + Warning, Level = "", AddDtStamp = False)

if Errors:
    Common.Exit_Job(-1, "Error(s) encountered. See summary above.", False)
Common.Exit_Job(0, "", True)