SELECT A.id, A.name, C.StartServiceId, D.AnalysisType, D.Result
FROM services A INNER JOIN
--ServiceDependencies B on A.id = B.ServiceID INNER JOIN
ServiceAnalyzerRuns C on C.StartServiceId = A.id INNER JOIN
ServiceAnalyzerResults D on D.AnalysisRunId = C.id

Select A.ServiceID, A.DependsOnServiceID, B.id, B.Name as ServiceName, C.name as DependsName
from ServiceDependencies A 
join Services B on A.ServiceID = B.id
join Services C on A.DependsOnServiceID = C.id


