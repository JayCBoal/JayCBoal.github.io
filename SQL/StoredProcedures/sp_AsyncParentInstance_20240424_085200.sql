DROP PROCEDURE IF EXISTS sp_AsyncParentInstance;
DELIMITER //
CREATE PROCEDURE sp_AsyncParentInstance(IN InstanceID VARCHAR(20), IN Status VARCHAR(1), IN DownstreamProcessName VARCHAR(64), IN DownstreamJobName VARCHAR(64))
BEGIN
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
	BEGIN
		GET DIAGNOSTICS CONDITION 1 @SQLState = RETURNED_SQLSTATE, @ErrNo = MYSQL_ERRNO, @ErrText = MESSAGE_TEXT;
		-- SET @FullError = CONCAT("ERROR ", @ErrNo, " (", @SQLState, "): ", @ErrText);
		-- SELECT @FullError AS Result;
		SELECT @ErrNo AS ReturnValue, CONCAT('SQL State ', @SQLState, ': ', @ErrText) AS Message
	END;
    SET @ReturnValue = 0, @Message = '';
	IF Status = 'I' THEN
		INSERT INTO AsyncParentInstances SET `InstanceID` = InstanceID, `Status` = Status, `DownstreamProcessName` = DownstreamProcessName, `DownstreamJobName` = DownstreamJobName;
        SET @ReturnValue = 1, @Message = CONCAT('Inserted record ', InstanceID);
	ELSE
		UPDATE AsyncParentInstances SET `Status` = Status, `ModifiedBy` = CURRENT_USER() WHERE `InstanceID` = InstanceID;
        SET @ReturnValue = 1, @Message = CONCAT('Updated record ', InstanceID, ' to status "', Status, '"');
	END IF;
	SELECT @ReturnValue AS ReturnValue, @Message AS Message;
END //
DELIMITER ;


BEGIN
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
	BEGIN
		GET DIAGNOSTICS CONDITION 1 @SQLState = RETURNED_SQLSTATE, @ErrNo = MYSQL_ERRNO, @ErrText = MESSAGE_TEXT;
		SET @FullError = CONCAT("ERROR ", @ErrNo, " (", @SQLState, "): ", @ErrText);
		SET @ReturnMessage = CONCAT("SQL State ", @SQLState, ": ", @ErrText);
		-- SELECT @FullError AS Result;
		SELECT @ErrNo AS ReturnValue, @ReturnMessage AS ReturnMessage;
		-- SELECT @ErrNo AS Result, CONCAT("SQL State ", @SQLState, ": ", @ErrText) AS Message
	END;
    SET @ReturnValue = 0;
	SET @ReturnMessage = '';
	IF Status = 'I' THEN
		INSERT INTO AsyncParentInstances SET `InstanceID` = InstanceID, `Status` = Status, `DownstreamProcessName` = DownstreamProcessName, `DownstreamJobName` = DownstreamJobName;
        SET @ReturnValue = 1;
		SET @ReturnMessage = CONCAT("Inserted record '", InstanceID, "'");
	ELSE
		UPDATE AsyncParentInstances SET `Status` = Status, `ModifiedBy` = CURRENT_USER() WHERE `InstanceID` = InstanceID;
        SET @ReturnValue = 1;
		SET @ReturnMessage = CONCAT("Updated record '", InstanceID, "' to Status '", Status, "'");
	END IF;
	SELECT @ReturnValue AS ReturnValue, @ReturnMessage AS ReturnMessage;
END


CALL sp_AsyncParentInstance('a1b2c_20240423_1', 'I', 'DOWNSTREAM_PROCESS', 'DOWNSTREAM_JOB') -- INSERT
CALL sp_AsyncParentInstance('a1b2c_20240423_1', 'S', 'DOWNSTREAM_PROCESS', 'DOWNSTREAM_JOB') -- UPDATE

UPDATE AsyncParentInstances SET `Status` = 'I', `ModifiedBy` = CURRENT_USER() WHERE `InstanceID` = 'a1b2c_20240423_1';