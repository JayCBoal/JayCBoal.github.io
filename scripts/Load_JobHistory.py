# Set global Debug variable to control logging verbosity
import os, sys, glob, csv, traceback, shutil, datetime

# Get argument(s) with which script was called
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

Common.Log_Msg(f"Check for SQL file(s) in '{Glb['JobHistoryFolder']}'")
try:
    SQLFiles = glob.glob(f"{Glb['JobHistoryFolder']}/*.sql")
    SQLFiles.sort(key=lambda x: os.path.getmtime(x))
except Exception:
    Common.Exit_Job(-1, f"Error getting SQL files in '{Glb['JobHistoryFolder']}': {traceback.format_exc()}", False, "ERROR")

Common.Log_Msg(f"Total SQL file(s) found: {len(SQLFiles)}")
if len(SQLFiles) == 0:
    Common.Exit_Job(0, "", True)
Common.Log_Msg(f"SQL file(s):\n{str(SQLFiles)}", "DEBUG")

ConnectResults = Common.Connect_SQL(Glb["AutomationDBHost"], Glb["AutomationDBName"])
if not ConnectResults[0]:
    Common.Exit_Job(-1)
Connection = ConnectResults[0]

# Loop over files
ErrorList = []
for SQLFile in SQLFiles:
    Common.Log_Msg()
    Common.Log_Msg(f"Import SQL file: {SQLFile}")
    Errors = []
    try:
        File = open(SQLFile, "r")
        arrLines = File.readlines()
    except Exception:
        ErrorList.append({
            "File": SQLFile,
            "Errors": [f"Error reading SQL file '{SQLFile}': {traceback.format_exc()}"]
        })
        Common.Log_Msg(ErrorList[-1]["Errors"][-1], "ERROR")
        continue

    FileErrors = []
    for Line in arrLines:
        SQLResults = Common.Execute_SQL(DBConn = Connection, DBHost = Glb["AutomationDBHost"], DBName = Glb["AutomationDBName"], DBUser = Glb["AutomationDBUser"], SQL = Line, Silent = True, Commit = True)
        if SQLResults["RC"] == 0:
            Common.Log_Msg("Executed SQL successfully")
        else:
            FileErrors.append("SQL execution failed: " + str(SQLResults["Errors"]))
            Common.Log_Msg(FileErrors[-1], "ERROR")
    SQLFilename = os.path.basename(SQLFile)
    if not FileErrors:
        ArchiveFilename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + SQLFilename
        ArchiveFilePath = Glb["ArchiveFolder"] + "/" + ArchiveFilename
        try:
            shutil.move(SQLFile, ArchiveFilePath)
            Common.Log_Msg("SQL file '" + SQLFile + "'\r\n\tarchived to '" + ArchiveFilePath + "'")
        except Exception:
            FileErrors.append(f"Error archiving SQL file '" + SQLFile + "' to '" + ArchiveFilePath + "': " + traceback.format_exc())
            Common.Log_Msg(FileErrors[-1], "ERROR")
    if FileErrors:
        ErrorFilePath = Glb['JobHistoryFolder'] + "/errors/" + SQLFilename
        try:
            shutil.move(SQLFile, ErrorFilePath)
            Common.Log_Msg("SQL file '" + SQLFile + "' moved to '" + ErrorFilePath + "'")
        except Exception:
            FileErrors.append("Error moving SQL file '" + SQLFile + "' to error folder '" + ErrorFilePath + "': " + traceback.format_exc())
            Common.Log_Msg(FileErrors[-1], "ERROR")
        ErrorList.append({
            "File": SQLFile,
            "Errors": FileErrors
        })
        
if ErrorList:
    Common.Log_Msg("Error(s) occurred executing Job History loader SQL statements:", "ERROR")
    for File in ErrorList:
        Common.Log_Msg("\tFile: " + File["File"], Level = "", AddDtStamp = False)
        for FileError in File["Errors"]:
            Common.Log_Msg("\t\t" + FileError, Level = "", AddDtStamp = False)
    Common.Exit_Job(-1, "", Success = False)

Common.Exit_Job(0, "", Success = True)