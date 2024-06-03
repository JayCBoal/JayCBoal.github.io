SELECT
    P.id AS ProcessID,
    P.Name AS ProcessName,
    J.JobOrder,
    J.Name AS JobName,
    JS.StepOrder,
    JS.Title AS StepTitle,
    JSP.ParamName,
    JSP.ParamValue
FROM
    Processes P
    JOIN Jobs J ON J.Process_id = P.id
    JOIN JobSteps JS ON JS.Job_id = J.id
    JOIN JobStepParameters JSP ON JSP.JobStep_id = JS.id
WHERE P.Name LIKE '%'
ORDER BY
    ProcessName,
    JobOrder,
    StepOrder,
    JSP.id