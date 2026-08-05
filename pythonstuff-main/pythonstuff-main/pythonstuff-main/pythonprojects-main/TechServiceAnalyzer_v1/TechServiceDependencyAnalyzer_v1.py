from turtledemo.penrose import start


def analyze_services(services, start_service_input):
    #Data Type Validations
    if not isinstance(services, dict):
        raise TypeError("Services is not a dictionary")
    if not isinstance(start_service_input, str):
        raise TypeError("Start service is not a string")
    if start_service_input not in services:
        raise ValueError("start_service is not a key in services")
    for service in services:
        if "depends_on" not in services[service] or "incidents" not in services[service]:
            raise ValueError("a service is missing \"depends_on\" or \"incidents\"")
        elif not isinstance(services[service]["depends_on"], list) or not isinstance(services[service]["incidents"], list):
            raise ValueError("\"depends_on\" or \"incidents\" is not a list")
        for dependency in services[service]["depends_on"]:
            if dependency not in services:
                raise ValueError("dependency references a service that does not exist")
        for number in services[service]["incidents"]:
            if not isinstance(number, int) or isinstance(number, bool) or number < 0:
                raise ValueError("an incident time is not a non-negative integer")
    #Depth First Search Algo
    def depth_first_searcher(services, start_service):
        visited = []
        def explore(dependency):
            if dependency  in visited:
                return
            else:
                visited.append(dependency)
            for depends in services[dependency]['depends_on']:
                explore(depends)
        explore(start_service)
        return visited

    dfs_order = depth_first_searcher(services, start_service_input)
    print()
    print(f'Starting from {start_service_input}, the Depth First Search Order is:\n{dfs_order}')

    def breadth_first_search(services, start_service):
        queue = [start_service]
        result = []

        while queue:
            current = queue.pop(0)
            if current not in result:
                result.append(current)
                for x in services[current]['depends_on']:
                    queue.append(x)
        return result

    bfs_order = breadth_first_search(services, start_service_input)
    print()
    print(f'Starting from {start_service_input}, the Breadth First Search Order is:\n{bfs_order}')

    def reachable_services(bfs_order, dfs_order):
        return int((len(bfs_order) + len(dfs_order))/2)
    number_reachable_services = reachable_services(bfs_order, dfs_order)
    print()
    print(f'Number of reachable services from {start_service_input} is {number_reachable_services}')

    def dependency_levels(services, start_service_input):
        dependency_dict = {start_service_input: 0}
        queue = [start_service_input]
        while queue:
            current = queue.pop(0)
            for x in services[current]['depends_on']:
                if x not in dependency_dict:
                    queue.append(x)
                    dependency_dict[x] = dependency_dict[current] + 1
        return dependency_dict

    depends_level = dependency_levels(services, start_service_input)
    print()
    print(f'Dictionary showing the minimum number of dependency steps required to reach each service\n{depends_level}')

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

    short_path = shortest_path(services, start_service_input)
    print()
    print(f'Dictionary containing the shortest dependency path from start_service to every reachable service.\n{short_path}')

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
    incident_avgs = avg_incident_times(services, start_service_input)
    print()
    print(f'The average incident-resolution time for every reachable service\n{incident_avgs}')

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

    total_time = total_incident_time(services, start_service_input)
    print()
    print(f'The combined incident time for all reachable services from starting service\n{total_time}')

    def high_risk_services(service_list):
        depends_map = {name: 0 for name in service_list}
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
                highest_risk['risk_score'] = (depends_map[service] - 1) * avg_times[service]
                highest_risk["service"] = service
        return highest_risk

    highest_risk_service = high_risk_services(services)
    print(f'\nHighest Risk Service Formula = blast radius (dependencies) * downtime (incident times)\nThe highest risk service is:{highest_risk_service}')


services = {
    "Customer Portal": {
        "depends_on": ["Authentication API", "Claims API"],
        "incidents": [30, 45]
    },
    "Authentication API": {
        "depends_on": ["User Database"],
        "incidents": [20]
    },
    "Claims API": {
        "depends_on": ["Claims Database", "Document Service"],
        "incidents": [60, 90, 30]
    },
    "User Database": {
        "depends_on": [],
        "incidents": [15, 25]
    },
    "Claims Database": {
        "depends_on": ["Storage Service"],
        "incidents": [40]
    },
    "Document Service": {
        "depends_on": ["Storage Service"],
        "incidents": []
    },
    "Storage Service": {
        "depends_on": [],
        "incidents": [50, 70]
    },
    "Unused Reporting Tool": {
        "depends_on": [],
        "incidents": [120]
    }
}



print(f'What service would you like to start with?')
for number, service in enumerate(services, start=1):
    print(f'{number}. {service}')
start_service_input = input('\n')
if start_service_input.isdigit():
    if int(start_service_input) <= len(services) and int(start_service_input) > 0:
        for number, service in enumerate(services, start=1):
            if number == int(start_service_input):
                start_service_input = service
                analyze_services(services, start_service_input)
                break
    elif int(start_service_input) > len(services) or int(start_service_input) <= 0:
        print('please input a number or service from the list')
else:
    analyze_services(services, start_service_input)

