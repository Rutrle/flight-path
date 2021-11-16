import csv
import datetime
import json
import copy


def read_flight_data(dst):

    with open(dst, 'r') as flight_data_file:
        flights = {}
        reader = csv.DictReader(flight_data_file, delimiter=',')

        for row in reader:
            flight = {}
            flight['flight_no'] = row['flight_no']
            flight['origin'] = row['origin']
            flight['destination'] = row['destination']
            flight['departure'] = datetime.datetime.fromisoformat(
                row['departure'])
            flight['arrival'] = datetime.datetime.fromisoformat(row['arrival'])
            flight['base_price'] = float(row['base_price'])
            flight['bag_price'] = float(row['bag_price'])
            flight['bags_allowed'] = int(row['bags_allowed'])

            flights.setdefault(flight['origin'], [])

            flights[flight['origin']].append(flight)

        return (flights)


def construct_graph(flights):
    flight_graph = {}

    for origin in flights:
        if origin not in flight_graph:
            flight_graph[origin] = set()
        for flight in flights[origin]:
            if flight['destination'] not in flight_graph:
                flight_graph[flight['destination']] = set()

            flight_graph[origin].add(flight['destination'])

    '''
    variant with list, probably not to be used
    for flight in flights:
        if flight['origin'] not in flight_graph:
            flight_graph[flight['origin']] = set()
        if flight['destination'] not in flight_graph:
            flight_graph[flight['destination']] = set()

        flight_graph[flight['origin']].add(flight['destination'])
    '''
    return flight_graph


def find_all_paths(src, dst, flight_data, graph):

    def _inner_find_all_paths(graph, inbound_flight, dst, current_path, flight_data, current_visited, index):

        current_path.append((inbound_flight))
        current_visited.append(inbound_flight['destination'])
        airport_path.append([inbound_flight['destination'], index])

        if inbound_flight['destination'] == dst:
            finished_paths.append(tuple(current_path))
            airport_fin.append(tuple(airport_path))
            # print(current_path)

        else:
            # for airport in graph[inbound_flight['destination']]:
            for i, new_flightpath in enumerate(flight_data[inbound_flight['destination']]):

                layover_time = (
                    new_flightpath['departure'] - inbound_flight['arrival'])
                layover_OK = datetime.timedelta(
                    hours=1) < layover_time < datetime.timedelta(hours=6)

                if new_flightpath['destination'] not in current_visited and layover_OK:
                    _inner_find_all_paths(
                        graph, new_flightpath, dst, current_path, flight_data, current_visited, i)

        current_path.pop()
        current_visited.pop()
        airport_path.pop()

    current_path = []
    current_visited = [src]
    finished_paths = []
    airport_path = []  # to be deleted
    airport_fin = []

    for i, new_flightpath in enumerate(flight_data[src]):
        _inner_find_all_paths(graph, new_flightpath, dst,
                              current_path, flight_data, current_visited, i)

    print(finished_paths)
    print(airport_fin)
    return finished_paths


def convert_to_JSON(flight_paths):
    json_export = []

    for flight_path in flight_paths:
        bags_allowed = float('inf')
        current_flight = {}
        flights = []
        total_price = 0

        travel_time = (flight_path[-1]['arrival'] -
                       flight_path[0]['departure'])

        for flight in flight_path:
            current_flight = copy.deepcopy(flight)
            current_flight['departure'] = current_flight['departure'].isoformat()
            current_flight['arrival'] = current_flight['arrival'].isoformat()

            flights.append(current_flight)
            total_price = total_price + current_flight["base_price"]

            bags_allowed = min(bags_allowed, current_flight["bags_allowed"])

        current_flight = {
            "flights": flights,
            "bags_allowed": bags_allowed,
            "destination": flight_path[-1]['destination'],
            'origin': flight_path[0]['origin'],
            'total_price': total_price,
            'travel_time': str(travel_time)
        }

        json_export.append(current_flight)
    print(json.dumps(json_export, indent=4))

    with open(f"{json_export[0]['origin']}-{json_export[0]['destination']}_flight_paths.json", mode='w') as write_file:
        json.dump(json_export, write_file, indent=4)


if __name__ == '__main__':
    flight_data = read_flight_data('example/example1.csv')

    flight_graph = construct_graph(flight_data)

    possible_paths = find_all_paths('SML', 'NIZ', flight_data, flight_graph)

    convert_to_JSON(possible_paths)
