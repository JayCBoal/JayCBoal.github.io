-- jayboal@penguin:~$ mysqldump -d -u testuser -p -h localhost AutomationDB
-- Enter password: 

-- MariaDB dump 10.19  Distrib 10.11.6-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: AutomationDB
-- ------------------------------------------------------
-- Server version       10.11.6-MariaDB-0+deb12u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Drop tables in specific order due to foreign key constraints
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `Applications`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Applications` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(64) NOT NULL COMMENT 'Full name of Application',
  `Abbr` varchar(10) NOT NULL COMMENT 'Standard abbreviation of Application',
  `Description` varchar(256) DEFAULT NULL COMMENT 'Description of Application''s purpose/function',
  `SupportDL` varchar(64) DEFAULT NULL COMMENT 'Application Support team''s email distribution list',
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  UNIQUE KEY `Name` (`Name`),
  UNIQUE KEY `Abbr` (`Abbr`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Applications with which AutoApp jobs interacts';
/*!40101 SET character_set_client = @saved_cs_client */;

-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `Credentials`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Credentials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Credentials` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `UID` varchar(64) NOT NULL COMMENT 'User ID of automation account',
  `Pwd` varchar(128) NOT NULL COMMENT 'Password of automation account',
  `Description` varchar(256) DEFAULT NULL COMMENT 'Description of automation account''s purpose/function',
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UID` (`UID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Automation accounts used by AutoApp jobs';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `Entities`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Entities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Entities` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `LegalName` varchar(64) NOT NULL COMMENT 'Full legal name of Entity',
  `Abbr` varchar(10) NOT NULL COMMENT 'Common abbreviation of Entity name',
  `AKAs` varchar(256) DEFAULT NULL COMMENT 'Common "AKA"s of Entity - former names, names of other Entities which it has acquired or with which it has merged, alternative spellings, etc.',
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Entities with which AutoApp jobs interact';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `Sites`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Sites` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(64) NOT NULL COMMENT 'Name of Site',
  `Entity_id` int(11) unsigned DEFAULT NULL COMMENT 'ID of associated Entity record, if applicable (in some cases the Site is not Entity-specific but has access to various Entities'' Sites [where we host the Site])',
  `Host` varchar(64) NOT NULL COMMENT 'Hostname or IP address of the Site host',
  `UserID` varchar(128) NOT NULL COMMENT 'Login ID for the Site',
  `Protocol` varchar(20) NOT NULL COMMENT '"SFTP", "FTP", "FTPS (implicit SSL)", "FTPS (explicit SSL)", "AWS_S3", "Azure_Blob"',
  `AuthType` varchar(20) NOT NULL COMMENT '"UID & Pwd" "UID & SSH Key", "UID & Pwd & SSH Key"',
  `Pwd` varchar(64) DEFAULT NULL COMMENT 'Login password for the Site',
  `KeyFile` varchar(64) DEFAULT NULL COMMENT 'Full path of SSH Key for login to the Site',
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  KEY `Entities_Sites_Entity_id` (`Entity_id`),
  CONSTRAINT `Entities_Sites_Entity_id` FOREIGN KEY (`Entity_id`) REFERENCES `Entities` (`id`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='FTP (and other) site definitions';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `Processes`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Processes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Processes` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(64) NOT NULL COMMENT 'Process name',
  `Application_id` int(11) unsigned DEFAULT NULL COMMENT 'Application ID with which the Process is associated',
  `Client_id` int(11) unsigned DEFAULT NULL COMMENT 'Entity ID for the Client with which the Process is associated',
  `Severity` int(1) DEFAULT NULL COMMENT 'Process severity (1 = 1 hour SLA; 2 = 4 hours; 3 = 24 hours)',
  `ShortDescription` varchar(100) DEFAULT NULL COMMENT 'Short (<=100 character) description of process'' function. To be used for auto-generation of process name.',
  `TechDescription` varchar(1024) DEFAULT NULL COMMENT 'Detailed technical description of process',
  `BusDescription` varchar(1024) DEFAULT NULL COMMENT 'Detailed description of business process',
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  KEY `Application_id` (`Application_id`),
  KEY `Entities_Processes_Entity_id` (`Client_id`),
  CONSTRAINT `Applications_Processes_Application_id` FOREIGN KEY (`Application_id`) REFERENCES `Applications` (`id`) ON DELETE SET NULL ON UPDATE SET NULL,
  CONSTRAINT `Entities_Processes_Entity_id` FOREIGN KEY (`Client_id`) REFERENCES `Entities` (`id`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Process definitions';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `Jobs`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Jobs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Process_id` int(11) unsigned NOT NULL COMMENT 'id of associated record in Processes',
  `JobOrder` int(3) unsigned NOT NULL COMMENT 'Ordinal position of Job within Process execution (e.g. 1 = 1st Job, 2 = 2nd Job, etc.)',
  `Name` varchar(64) NOT NULL COMMENT 'Job name',
  `Description` varchar(100) DEFAULT NULL,
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  KEY `Processes_Jobs_Process_id` (`Process_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Job definitions';
/*!40101 SET character_set_client = @saved_cs_client */;
  -- ,  CONSTRAINT `Processes_Jobs_Process_id` FOREIGN KEY (`Process_id`) REFERENCES `Processes` (`id`) ON DELETE SET NULL ON UPDATE SET NULL


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `JobHistory`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `JobHistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `JobHistory` (
  `InstanceID` varchar(20) NOT NULL COMMENT 'ID of unique instance of automation Job',
  `ProcessName` varchar(64) NOT NULL COMMENT 'Name of automation Process to which Job belongs',
  `JobName` varchar(64) NOT NULL COMMENT 'Name of automation Job',
  `BeginExecutionDateTime` datetime NOT NULL COMMENT 'Date/time the Job began executing',
  `EndExecutionDateTime` datetime DEFAULT NULL COMMENT 'Date/time the Job completed',
  `ReturnCode` INT(3) DEFAULT NULL COMMENT 'Return code of Job script',
  `CompletionStatus` VARCHAR(20) DEFAULT NULL COMMENT 'Completion status of Job (Success/Failure)',
  `LogFile` VARCHAR(256) NOT NULL COMMENT 'Full path of Job output log',
  `AutomationApp` VARCHAR(20) NOT NULL COMMENT 'Automation application which executed the Job',
  `Host` VARCHAR(64) NOT NULL COMMENT 'Host on which the Job was executed',
  `User` varchar(64) NOT NULL COMMENT 'User that executed the Job',
  `InsertedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was inserted',
  PRIMARY KEY (`InstanceID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lists execution history of automation jobs';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `JobSteps`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `JobSteps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `JobSteps` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique ID of record',
  `Job_id` int(11) unsigned NOT NULL COMMENT 'id of associated Job record',
  `StepOrder` int(3) NOT NULL COMMENT 'Ordinal position of step within Job execution (e.g. 1 = 1st Step, 2 = 2nd Step, etc.)',
  `Title` varchar(64) NOT NULL COMMENT 'Brief description of Step''s function',
  `Enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Whether step is Enabled (meaning it would be executed when Job executes) or not (meaning it would be skipped)',
  `FunctionName` varchar(64) NOT NULL COMMENT 'Name of function executed by Step',
  `SuccessRCs` varchar(32) DEFAULT NULL COMMENT 'Step return code(s) that should be considered successful',
  `FailureRCs` varchar(32) DEFAULT NULL COMMENT 'Step return code(s) that should be considered failure',
  `WarningRCs` varchar(32) DEFAULT NULL COMMENT 'Step return code(s) that should be considered warning',
  `CreatedDateTime` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(50) NOT NULL DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL COMMENT 'Date/time the record was last modified',
  `ModifiedBy` int(11) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  KEY `Jobs_JobSteps_Job_id` (`Job_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Steps performed by Jobs';
/*!40101 SET character_set_client = @saved_cs_client */;
  -- CONSTRAINT `Jobs_JobSteps_Job_id` FOREIGN KEY (`Job_id`) REFERENCES `Jobs` (`id`)


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `JobStepParameters`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `JobStepParameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `JobStepParameters` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique ID of record',
  `JobStep_id` int(11) unsigned NOT NULL COMMENT 'JobStep ID with which the Step Parameter is associated',
  `ParamName` varchar(32) NOT NULL COMMENT 'Name of Step Parameter',
  `ParamValue` varchar(2048) NOT NULL COMMENT 'Value of Step Parameter',
  `CreatedDateTime` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(50) NOT NULL DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL COMMENT 'Date/time the record was last modified',
  `ModifiedBy` int(11) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  KEY `JobSteps_JobStepParameters_JobStep_id` (`JobStep_id`),
  CONSTRAINT `JobSteps_JobStepParameters_JobStep_id` FOREIGN KEY (`JobStep_id`) REFERENCES `JobSteps` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Parameters of Steps performed by Jobs';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `StepTypes`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `StepTypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `StepTypes` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique ID of record',
  `Name` varchar(32) NOT NULL COMMENT 'Name of Step Type',
  `FunctionName` varchar(64) NOT NULL COMMENT 'Name of function executed by Step Type',
  `CreatedDateTime` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(50) NOT NULL DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL COMMENT 'Date/time the record was last modified',
  `ModifiedBy` int(11) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Supported Job Step types';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `StepDefinitions`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `StepDefinitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `StepDefinitions` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique ID of record',
  `StepType_id` int(11) unsigned NOT NULL COMMENT 'StepType ID with which the Step Parameter is associated',
  `ParamOrder` int(2) NOT NULL COMMENT 'Order in which parameter should be displayed in web UI',
  `ParamName` varchar(32) NOT NULL COMMENT 'Name of Step Parameter',
  `ParamDefaultValue` varchar(64) DEFAULT NULL COMMENT 'Default value of Step Parameter',
  `Required` tinyint(1) DEFAULT NULL COMMENT 'Whether Parameter is required for Step',
  `CreatedDateTime` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(50) NOT NULL DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL COMMENT 'Date/time the record was last modified',
  `ModifiedBy` int(11) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`id`),
  KEY `StepTypes_StepDefinitions_StepType_id` (`StepType_id`),
  CONSTRAINT `StepTypes_StepDefinitions_StepType_id` FOREIGN KEY (`StepType_id`) REFERENCES `StepTypes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Parameters accepted for each Step Type';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `Audits`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Audits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Audits` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Table` varchar(64) NOT NULL COMMENT 'Name of table upon which Audited action was performed',
  `Table_Record_id` int(11) NOT NULL COMMENT 'id of record upon which Audited action was performed ',
  `Action` varchar(16) NOT NULL COMMENT 'Type of Audited action: "INSERT", "UPDATE", "DELETE"',
  `Details` varchar(2048) NOT NULL COMMENT 'Details of Audited action: column names & values inserted, updated or deleted',
  `DateTime` datetime NOT NULL COMMENT 'Date/time the Audited action was performed',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Changes to other tables (excluding Operations)';
/*!40101 SET character_set_client = @saved_cs_client */;


-- Drop/recreate 'Operations' table is commented out as no changes to structure are anticipated and I don't want to lose the data in it
-- -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- -- Table structure for table `Operations`
-- -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- DROP TABLE IF EXISTS `Operations`;
-- /*!40101 SET @saved_cs_client     = @@character_set_client */;
-- /*!40101 SET character_set_client = utf8 */;
-- CREATE TABLE `Operations` (
--   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
--   `Type` varchar(20) NOT NULL COMMENT 'Type of operation, e.g. "COPY", "FTPUPLOAD", "SQL", etc.',
--   `StartDateTime` datetime DEFAULT NULL COMMENT 'Operation start date/time',
--   `EndDateTime` datetime NOT NULL COMMENT 'Operation end date/time',
--   `Details` varchar(2048) DEFAULT NULL COMMENT 'Details of Operation (only applicable for non-File Ops)',
--   `SourceSite_id` int(11) DEFAULT NULL COMMENT 'ID of record in Sites table from which Source site parameters were pulled',
--   `SourceSiteUID_Host` varchar(128) DEFAULT NULL COMMENT '"UserID"@"Hostname/IP address" of Source FTP Site',
--   `SourcePath` varchar(256) DEFAULT NULL COMMENT 'Source Path (for File Op)',
--   `SourceFilename` varchar(256) DEFAULT NULL COMMENT 'Source Filename (for File Op)',
--   `SourceSize` int(11) DEFAULT NULL COMMENT 'Source File Size (for File Op)',
--   `DestSite_id` int(11) DEFAULT NULL COMMENT 'ID of record in Sites table from which Destination site parameters were pulled',
--   `DestSiteUID_Host` varchar(128) DEFAULT NULL COMMENT '"UserID"@"Hostname/IP address" of Destination FTP Site',
--   `DestPath` varchar(256) DEFAULT NULL COMMENT 'Destination Path (for File Ops)',
--   `DestFilename` varchar(256) DEFAULT NULL COMMENT 'Destination Filename (for File Ops)',
--   `DestSize` int(11) DEFAULT NULL COMMENT 'Destination File Size (for File Ops)',
--   `SourcePathTemplate` varchar(256) DEFAULT NULL COMMENT 'Source Path Template [including substitution placeholders if applicable] (for File Ops)',
--   `SourceFilenamePattern` varchar(256) DEFAULT NULL COMMENT 'Source Filename Pattern [including substitution placeholders if applicable] (for File Ops)',
--   `DestPathTemplate` varchar(256) DEFAULT NULL COMMENT 'Dest Path Template [including substitution placeholders if applicable] (for File Ops)',
--   `DestRenameMask` varchar(256) DEFAULT NULL COMMENT 'Destination Rename Mask [including substitution placeholders if applicable] (for File Ops)',
--   `AutomationApp` varchar(20) NOT NULL COMMENT 'Automation application which executed the process/job that performed the Operation',
--   `ProcessName` varchar(64) NOT NULL COMMENT 'Name of automation process containing job that performed the Operation',
--   `JobName` varchar(64) NOT NULL COMMENT 'Name of automation job that performed the Operation',
--   `InstanceID` varchar(20) NOT NULL COMMENT 'ID of unique instance of automation job that performed the Operation',
--   `PerformedBy` varchar(50) NOT NULL COMMENT 'Username that performed the Operation',
--   `InsertedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the Operation record was inserted',
--   PRIMARY KEY (`id`)
-- ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Operations performed by AutoApp jobs';
-- /*!40101 SET character_set_client = @saved_cs_client */;


-- Drop/recreate 'Sources' table is commented out as no changes to structure are anticipated and I don't want to lose the data in it
-- -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- -- Table structure for table `Sources`
-- -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- DROP TABLE IF EXISTS `Sources`;
-- /*!40101 SET @saved_cs_client     = @@character_set_client */;
-- /*!40101 SET character_set_client = utf8 */;
-- CREATE TABLE `Sources` (
--   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
--   `Description` varchar(255) DEFAULT NULL COMMENT 'Description of file(s) retrieved from Source',
--   `Application_id` int(11) unsigned DEFAULT NULL COMMENT 'Application ID with which the Source is associated, if applicable',
--   `Site_id` int(11) unsigned DEFAULT NULL COMMENT 'Site ID with which the Source is associated, if applicable',
--   `Entity_id` int(11) unsigned DEFAULT NULL COMMENT 'Entity ID with which the Source is associated, if applicable (only applicable if Source is associated with an Entity but is *not* associated with an Entity-specific Site)',
--   `PathTemplate` varchar(255) NOT NULL COMMENT 'Template for Destination path, including date/time placeholders if applicable (e.g. "\\xyz01AppFolderDrop<yyyyMMdd>")',
--   `FilenamePattern` varchar(255) NOT NULL COMMENT 'Pattern for matching Source file(s), including wildcards and date placeholders if applicable (e.g. "File_<yyyyMMdd>*.txt")',
--   `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
--   `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
--   `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
--   `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
--   PRIMARY KEY (`id`),
--   KEY `Applications_Sources_Application_id` (`Application_id`),
--   KEY `Entities_Sources_Entity_id` (`Entity_id`),
--   KEY `Sites_Sources_Site_id` (`Site_id`),
--   CONSTRAINT `Applications_Sources_Application_id` FOREIGN KEY (`Application_id`) REFERENCES `Applications` (`id`),
--   CONSTRAINT `Entities_Sources_Entity_id` FOREIGN KEY (`Entity_id`) REFERENCES `Entities` (`id`),
--   CONSTRAINT `Sites_Sources_Site_id` FOREIGN KEY (`Site_id`) REFERENCES `Sites` (`id`)
-- ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='File retrieval templates';
-- /*!40101 SET character_set_client = @saved_cs_client */;


-- Drop/recreate 'Deliveries' table is commented out as no changes to structure are anticipated and I don't want to lose the data in it
-- -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- -- Table structure for table `Deliveries`
-- -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- DROP TABLE IF EXISTS `Deliveries`;
-- /*!40101 SET @saved_cs_client     = @@character_set_client */;
-- /*!40101 SET character_set_client = utf8 */;
-- CREATE TABLE `Deliveries` (
--   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
--   `Description` varchar(255) DEFAULT NULL COMMENT 'Description of file(s) delivered',
--   `Application_id` int(11) unsigned DEFAULT NULL COMMENT 'Application ID with which the Delivery is associated, if applicable',
--   `Site_id` int(11) unsigned DEFAULT NULL COMMENT 'Site ID with which the Delivery is associated, if applicable',
--   `Entity_id` int(11) unsigned DEFAULT NULL COMMENT 'Entity ID with which the Delivery is associated, if applicable (only applicable if Delivery is associated with an Entity but is *not* associated with an Entity-specific Site)',
--   `FilenamePattern` varchar(255) NOT NULL DEFAULT '*' COMMENT 'Pattern for matching file(s) to deliver, including wildcards and date placeholders if applicable (e.g. "File_<yyyyMMdd>*.txt")',
--   `PathTemplate` varchar(255) NOT NULL COMMENT 'Template for Delivery path, including date/time placeholders if applicable (e.g. "\\xyz01AppFolderDrop<yyyyMMdd>")',
--   `RenameMask` varchar(255) DEFAULT NULL COMMENT 'Template for renaming Delivery file with respect to original file, including source filename and date/time placeholders if applicable (e.g. "<SourceFilename>_<yyyyMMdd_HHmmss>.<SourceExt>")',
--   `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
--   `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
--   `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
--   `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
--   PRIMARY KEY (`id`),
--   KEY `Entities_Deliveries_Entity_id` (`Entity_id`),
--   KEY `Sites_Deliveries_Site_id` (`Site_id`),
--   KEY `Applications_Deliveries_Application_id` (`Application_id`) USING BTREE,
--   CONSTRAINT `Applications_Deliveries_Application_id` FOREIGN KEY (`Application_id`) REFERENCES `Applications` (`id`) ON DELETE SET NULL ON UPDATE SET NULL,
--   CONSTRAINT `Entities_Deliveries_Entity_id` FOREIGN KEY (`Entity_id`) REFERENCES `Entities` (`id`) ON DELETE SET NULL ON UPDATE SET NULL,
--   CONSTRAINT `Sites_Deliveries_Site_id` FOREIGN KEY (`Site_id`) REFERENCES `Sites` (`id`) ON DELETE SET NULL ON UPDATE SET NULL
-- ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='File delivery templates';
-- /*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `AsyncParentInstances`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `AsyncParentInstances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `AsyncParentInstances` (
  `InstanceID` VARCHAR(20) NOT NULL COMMENT 'Unique instance id of AutoApp Job that initiated the Async process',
  `Status` VARCHAR(1) NOT NULL COMMENT 'I: Parent Process initiated; E: Error(s) initiating Async instance(s); P: Processing (all Async instance(s) have been initiated); S: Downstream Process/Job(s) triggered successfully; F: Error triggering downstream Process/Job(s)',
  `DownstreamProcessName` varchar(64) NOT NULL COMMENT 'Name of Downstream AutoApp Process to trigger when all Async instance(s) complete successfully',
  `DownstreamJobName` varchar(64) NOT NULL COMMENT 'Name of job (or wildcard pattern matching jobs) in downstream AutoApp Process to trigger when all Async instance(s) complete successfully (If blank, all contents of Process folder will be triggered)',
  `TriggerAttempt` INT(1) NOT NULL DEFAULT 0 COMMENT 'Number of time(s) downstream Process/Job(s) have been attempted to be triggered',
  `SupportDL` varchar(128) NOT NULL COMMENT 'Application Support team''s email distribution list',
  `SendOverrunNotification` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether email notification (to SupportDL) for overrun of ExpectedDuration should be sent',
  `SendFailureNotification` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether email notification (to SupportDL) for failure should be sent',
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`InstanceID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Asynchronous process Parent instances (instances of AutoApp jobs which initiated Async processes)';
/*!40101 SET character_set_client = @saved_cs_client */;


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Table structure for table `AsyncInstances`
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `AsyncInstances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `AsyncInstances` (
  `ParentInstanceID` VARCHAR(20) NOT NULL COMMENT 'Unique instance id of parent AutoApp Job that triggered Async instance',
  `AsyncID` INT(3) NOT NULL COMMENT 'Counter of Async instance initiated by parent AutoApp job',
  `InitiatingCall` VARCHAR(2048) NOT NULL COMMENT 'Details of call made to initiate Async Instance',
  `InitiatingCallOutput` VARCHAR(2048) DEFAULT NULL COMMENT 'Output returned by initiating call (e.g. expected duration, etc.)',
  `Status` VARCHAR(1) NOT NULL COMMENT 'Status of Async Instance (I: Initiated; S: Succeeded; F: Failed)',
  `ExpectedDuration` INT(4) DEFAULT NULL COMMENT 'Expected duration (in minutes) of Async Instance',
  `OverrunNotificationSent` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether email notification (to SupportDL) for overrun of ExpectedDuration has been sent',
  `CallbackContent` varchar(2048) DEFAULT NULL COMMENT 'Content of callback upon completion of Async instance (separate from success/failure [e.g. output filename])',
  `FailureNotificationSent` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether email notification (to SupportDL) for failure has been sent',
  `CreatedDateTime` datetime DEFAULT current_timestamp() COMMENT 'Date/time the record was created',
  `CreatedBy` varchar(64) DEFAULT user() COMMENT 'User who created the record',
  `ModifiedDateTime` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Date/time the record was last modified',
  `ModifiedBy` varchar(64) DEFAULT NULL COMMENT 'User who last modified the record',
  PRIMARY KEY (`ParentInstanceID`, `AsyncID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Asynchronous instances (instances initiated by but not directly tracked by AutoApp jobs)';
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-15 10:25:25


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate Applications table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO Applications (Name, Abbr, Description, SupportDL) VALUES ('Test Application', 'TESTAPP', 'Does nothing', 'testapp_support@jayco.com');
INSERT INTO Applications (Name, Abbr, Description, SupportDL) VALUES ('Finance', 'FINANCE', 'Accounting & Finance', 'finance_support@jayco.com');
INSERT INTO Applications (Name, Abbr, Description, SupportDL) VALUES ('ABC Application', 'ABC', 'Does the thing', 'ABC_support@jayco.com');
INSERT INTO Applications (Name, Abbr, Description, SupportDL) VALUES ('Legal Eagle', 'LEGAL', 'Legal stuff', 'legal_eagle_support@jayco.com');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate Credentials table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO Credentials (UID, Pwd, Description) VALUES ('AutoAppUser', 'autopwd', 'Primary account used for execution of AutoApp jobs');
INSERT INTO Credentials (UID, Pwd) VALUES ('testuser', 'testpwd');
INSERT INTO Credentials (UID, Pwd) VALUES ('DummyUsr', 'a&5,xc*N');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate Entities table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO Entities (LegalName, Abbr) VALUES ('The Jay Company', 'JAYCO');
INSERT INTO Entities (LegalName, Abbr) VALUES ('ABC Company, Inc.', 'ABC');
INSERT INTO Entities (LegalName, Abbr, AKAs) VALUES ('DEFCo, Llc.', 'DEFCO', 'Dillinger, Edgar and Franklin, Dillinger, Edgar & Franklin');
INSERT INTO Entities (LegalName, Abbr, AKAs) VALUES ('The Mass Market Insurance Company, Inc.', 'MASSMARKET', 'MassMark');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate Sites table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO Sites (Name, Entity_id, Host, UserID, Protocol, AuthType, Pwd) VALUES ('ABC', 2, 'sftp.abcco.com', 'jayco', 'SFTP', 'Pwd', 'jayco_sftp_x27nb');
INSERT INTO Sites (Name, Entity_id, Host, UserID, Protocol, AuthType, Pwd) VALUES ('DEFCO', 3, 'ftp.dillingeredgarfranklin.com', 'jayco2', 'SFTP', 'Pwd', 'SD%^x03?');
INSERT INTO Sites (Name, Entity_id, Host, UserID, Protocol, AuthType, Pwd) VALUES ('MASSMARKET', 4, 'sftp.jayco.com', 'massmark', 'SFTP', 'Pwd', 'C^%YUB0X');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate Processes table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO Processes (Name, Application_id, Client_id, Severity, ShortDescription) VALUES ('DEV-TESTAPP-ABC-TEST_PROCESS', 1, 2, 3, 'Test Process');
INSERT INTO Processes (Name, Application_id, Client_id, Severity, ShortDescription) VALUES ('DEV-FINANCE-DEFCO-FEED_APP', 2, 3, 3, 'DEF Feed to Finance Application');
INSERT INTO Processes (Name, Application_id, Client_id, Severity, ShortDescription) VALUES ('DEV-ABC-MASSMARKET-FEED_CLNT', 3, 4, 3, 'ABC feed to Mass Market');
INSERT INTO Processes (Name, Application_id, Client_id, Severity, ShortDescription) VALUES ('DEV-LEGAL-JAYCO-ALL_CLNT_EXTRACT', 4, 1, 1, 'Extract from Legal for all clients');
INSERT INTO Processes (Name, Application_id, Client_id, Severity, ShortDescription) VALUES ('DEV-TESTAPP-ABC-ASYNC_TEST', 1, 2, 3, 'Async Test Process');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate Jobs table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO Jobs (Process_id, JobOrder, Name, Description) VALUES (1, 1, 'TEST_JOB', 'Test Job');
INSERT INTO Jobs (Process_id, JobOrder, Name, Description) VALUES (2, 1, 'GET_DATA', 'Get input from inbound FTP LP, archive, deliver to app LP');
INSERT INTO Jobs (Process_id, JobOrder, Name, Description) VALUES (3, 1, 'SEND_DATA', 'Get input from app LP, archive, deliver to outbound FTP LP');
INSERT INTO Jobs (Process_id, JobOrder, Name, Description) VALUES (4, 1, 'EXTRACT_DATA', 'Execute SQL to extract data, archive');
INSERT INTO Jobs (Process_id, JobOrder, Name, Description) VALUES (5, 1, 'INIT_ASYNC', 'Initiate Async instance(s)');
INSERT INTO Jobs (Process_id, JobOrder, Name, Description) VALUES (5, 2, 'DELIVER', 'Deliver output of Async instance(s)');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate StepTypes table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO StepTypes (Name, FunctionName) VALUES ('Copy File(s)', 'Copy_Files');
INSERT INTO StepTypes (Name, FunctionName) VALUES ('Delete File(s)', 'Delete_Files');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate StepDefinitions table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO StepDefinitions (StepType_id, ParamOrder, ParamName, Required) VALUES (1, 1, 'Source', 1);
INSERT INTO StepDefinitions (StepType_id, ParamOrder, ParamName, Required) VALUES (1, 2, 'Dest', 1);
INSERT INTO StepDefinitions (StepType_id, ParamOrder, ParamName, Required) VALUES (1, 3, 'DelSrc', 0);
INSERT INTO StepDefinitions (StepType_id, ParamOrder, ParamName, Required) VALUES (1, 4, 'Move', 0);
INSERT INTO StepDefinitions (StepType_id, ParamOrder, ParamName, Required) VALUES (1, 5, 'CreateFolder', 0);
INSERT INTO StepDefinitions (StepType_id, ParamOrder, ParamName, Required) VALUES (2, 1, 'Source', 1);
INSERT INTO StepDefinitions (StepType_id, ParamOrder, ParamName, Required) VALUES (2, 2, 'Cleanup', 0);


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate JobSteps table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (1, 1, 'Get source file(s)', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (1, 2, 'Deliver file(s) to first location', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (1, 3, 'Clean up working folder', 'Delete_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (2, 1, 'Get source file(s) from FTP LP', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (2, 2, 'Archive file(s)', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (2, 3, 'Deliver file(s) to app LP', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (2, 4, 'Clean up working folder', 'Delete_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (3, 1, 'Get source file(s) from app LP', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (3, 2, 'Archive file(s)', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (3, 3, 'Deliver file(s) to FTP LP', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (3, 4, 'Clean up working folder', 'Delete_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (4, 1, 'Execute SQL to extract data', 'Execute_SQL');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (4, 2, 'Archive file(s)', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (4, 3, 'Deliver file(s) to first location', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (4, 4, 'Deliver file(s) to DEFCO FTP LP', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (4, 5, 'Clean up working folder', 'Delete_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (5, 1, 'Initiate Async instance(s)', 'Initiate_Async');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (6, 1, 'Get source file(s) from app LP', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (6, 2, 'Archive file(s)', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (6, 3, 'Deliver file(s) to first location', 'Copy_Files');
INSERT INTO JobSteps (Job_id, StepOrder, Title, FunctionName) VALUES (6, 4, 'Clean up working folder', 'Delete_Files');


-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Populate JobStepParameters table
-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (1, 'Source', '/home/jayboal/Testing/source/<yyyyMMdd>/file*.txt');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (1, 'Dest', '<WorkingFolder>/');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (1, 'CreateFolder', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (2, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (2, 'Dest', '/home/jayboal/Testing/dest/<yyyyMMdd>_<SourceFilename>_<yyyyMMdd_HHmmss><SourceExt>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (3, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (3, 'Cleanup', 'y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (4, 'Source', '<FTPLP>/from_client/file*.txt');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (4, 'Dest', '<WorkingFolder>/');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (4, 'CreateFolder', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (4, 'DelSrc', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (5, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (5, 'Dest', '<ArchiveFolder>/<yyyyMMdd_HHmmss>_<SourceFilenameFull>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (5, 'CreateFolder', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (6, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (6, 'Dest', '<AppLP>/to_app/<yyyyMMdd>_<SourceFilenameFull>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (7, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (7, 'Cleanup', 'y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (8, 'Source', '<AppLP>/from_app/<yyyyMMdd>_file*.txt');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (8, 'Dest', '<WorkingFolder>/');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (8, 'CreateFolder', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (8, 'DelSrc', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (9, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (9, 'Dest', '<ArchiveFolder>/<yyyyMMdd_HHmmss>_<SourceFilenameFull>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (9, 'CreateFolder', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (10, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (10, 'Dest', '<FTPLP>/to_client/<SourceFilename>_<yyyyMMdd_HHmmss><SourceExt>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (11, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (11, 'Cleanup', 'y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'DBHost', 'localhost');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'DBUser', 'testuser');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'DBName', 'AutomationDB');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'SQL', 'SELECT * FROM JobStepParameters LIMIT 10');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'IncludeHeader', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'OutputFile', '<WorkingFolder>/Extract_<yyyyMMdd>.csv');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'LogOutput', '');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (12, 'Silent', '');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (13, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (13, 'Dest', '<ArchiveFolder>/<yyyyMMdd_HHmmss>_<SourceFilenameFull>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (13, 'CreateFolder', 'Y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (14, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (14, 'Dest', '/home/jayboal/Testing/delivery/Legal_Extract/<yyyyMMdd>_<SourceFilenameFull>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (15, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (15, 'Dest', '<FTPLP>/to_client/');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (16, 'Source', '<WorkingFolder>/*');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (16, 'Cleanup', 'y');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (17, 'ExternalCalls', 'remoteexec.bat xyz01 testuser test_job.exe file1;remoteexec.bat xyz01 testuser test_job.exe file2');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (17, 'SupportDL', 'testapp_support@jayco.com');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (17, 'DownstreamProcessName', '<ProcessName>');
INSERT INTO JobStepParameters (JobStep_id, ParamName, ParamValue) VALUES (17, 'DownstreamJobName', 'DELIVER');
