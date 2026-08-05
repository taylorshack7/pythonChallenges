from db import DatabaseInitializer, ServicesToSQL, AnalyzerToSQL
from DependencyDictionary import services

def analyze_services(service_list, start_service_input):
    #Data Type Validations
    if not isinstance(service_list, dict):
        raise TypeError("Services is not a dictionary")
    if not isinstance(start_service_input, str):
        raise TypeError("Start service is not a string")
    if start_service_input not in service_list:
        raise ValueError("start_service is not a key in services")
    for service in service_list:
        if "depends_on" not in service_list[service] or "incidents" not in service_list[service]:
            raise ValueError("a service is missing \"depends_on\" or \"incidents\"")
        elif not isinstance(service_list[service]["depends_on"], list) or not isinstance(service_list[service]["incidents"], list):
            raise ValueError("\"depends_on\" or \"incidents\" is not a list")
        for dependency in service_list[service]["depends_on"]:
            if dependency not in service_list:
                raise ValueError("dependency references a service that does not exist")
        for number in service_list[service]["incidents"]:
            if not isinstance(number, int) or isinstance(number, bool) or number < 0:
                raise ValueError("an incident time is not a non-negative integer")
    #Depth First Search Algo
    def depth_first_searcher(service_list, start_service):
        visited = []
        def explore(dependency):
            if dependency  in visited:
                return
            else:
                visited.append(dependency)
            for depends in service_list[dependency]['depends_on']:
                explore(depends)
        explore(start_service)
        return visited
    dfs_order = depth_first_searcher(service_list, start_service_input)

    def breadth_first_search(service_list, start_service):
        queue = [start_service]
        result = []
        while queue:
            current = queue.pop(0)
            if current not in result:
                result.append(current)
                for x in service_list[current]['depends_on']:
                    queue.append(x)
        return result
    bfs_order = breadth_first_search(service_list, start_service_input)

    #Silly calc as DFS & BFS are same length. Gives same result regardless. Just did it this way for fun.
    def reachable_services(bfs_order, dfs_order):
        return int((len(bfs_order) + len(dfs_order))/2)
    number_reachable_services = reachable_services(bfs_order, dfs_order)

    def dependency_levels(service_list, start_service_input):
        dependency_dict = {start_service_input: 0}
        queue = [start_service_input]
        while queue:
            current = queue.pop(0)
            for x in service_list[current]['depends_on']:
                if x not in dependency_dict:
                    queue.append(x)
                    dependency_dict[x] = dependency_dict[current] + 1
        return dependency_dict
    depends_level = dependency_levels(service_list, start_service_input)

    def shortest_path(services_list, start_service):
        dependency_path = {start_service: [start_service]}
        queue = [start_service]
        while queue:
            current = queue.pop(0)
            for x in services_list[current]['depends_on']:
                if x not in dependency_path:
                    queue.append(x)
                    dependency_path[x] = dependency_path[current] + [x]
        return dependency_path
    short_path = shortest_path(service_list, start_service_input)

    def avg_incident_times(service_list, start_service):
        incident_times = {}
        queue = [start_service]
        current_sum = 0
        while queue:
            current = queue.pop(0)
            for x in service_list[current]['depends_on']:
                if x not in incident_times:
                    queue.append(x)
            for times in service_list[current]["incidents"]:
                current_sum += times
            if len(service_list[current]["incidents"]) > 0:
                incident_times[current] = current_sum / len(service_list[current]["incidents"])
            else:
                incident_times[current] = 0
            current_sum = 0
        return incident_times
    incident_avgs = avg_incident_times(service_list, start_service_input)

    def total_incident_time(service_list, start_service):
        incident_times = []
        queue = [start_service]
        current_sum = 0
        while queue:
            current = queue.pop(0)
            for x in service_list[current]['depends_on']:
                if x not in incident_times:
                    queue.append(x)
                    incident_times.append(x)
            for times in service_list[current]["incidents"]:
                current_sum += times
        return current_sum
    total_time = total_incident_time(service_list, start_service_input)

    def high_risk_services(service_list):
        depends_map = {name:0 for name in service_list}
        highest_risk: dict = {"service": 'service_name',
                        'risk_score': 0}
        for x in service_list:
            depth_dict = depth_first_searcher(service_list, x)
            for item in depth_dict:
                depends_map[item] += 1
        for service in depends_map:
            depth_dict = depth_first_searcher(service_list, service)
            avg_times = avg_incident_times(service_list, service)
            if (depends_map[service] - 1) * avg_times[service] > highest_risk['risk_score'] and service in depth_dict:
                highest_risk['risk_score'] = (depends_map[service] -1) * avg_times[service]
                highest_risk["service"] = service
        return highest_risk
    highest_risk_service = high_risk_services(service_list)

    return {'Depth First Search Order': dfs_order,
            'Breadth First Search Order': bfs_order,
            'Number of Reachable Services': number_reachable_services,
            'Dependency Levels': depends_level,
            'Shortest Path': short_path,
            'Average Incident Times': incident_avgs,
            'Total Incident Times': total_time,
            'Highest Risk Service': highest_risk_service
            }

print(f'What service would you like to start with?')
for number_bullet, system in enumerate(services, start=1):
    print(f'{number_bullet}. {system}')
user_input = input('\n')
if user_input.isdigit():
    if len(services) >= int(user_input) > 0:
        for number_bullet, system in enumerate(services, start=1):
            if number_bullet == int(user_input):
                user_input = system
                break
    else:
        print('please input a number or service from the list')
        raise SystemExit
elif user_input not in services:
    print('not a valid service')
    raise SystemExit

results = analyze_services(services, user_input)

#Objects initialized
db = DatabaseInitializer()
services_sql = ServicesToSQL(services)
analyzer_sql = AnalyzerToSQL()

#Create tables: services, service dependencies, incident times, service analyzer runs, service analyzer results
db.create_services_table()
db.create_servicedependencies_table()
db.create_incidenttimes_table()
db.create_serviceanalyzerruns_table()
db.create_serviceanalyzerresults_table()
db.conn.commit()

#Populate tables: services, service dependencies, and incident times
services_sql.add_service_sql()
services_sql.add_servicedependency_sql()
services_sql.add_serviceincident_sql()
services_sql.commit_to_DB()

#Populate tables: service analyzer runs and service analyzer results
analyzer_sql.add_analyzerrun_sql(user_input, services_sql.get_service_idmap())
analyzer_sql.add_analyzerresults_sql(results)
analyzer_sql.commit_to_DB()

#Close object SQLite connections
db.conn.close()
services_sql.close_DB_connection()
analyzer_sql.close_DB_connection()

print(f'\nResults:\n{results}\n\nResults saved to DB successfully')