import csv
import datetime


def read_flight_data(dst):

    with open(dst,'r') as flight_data_file:
        flights = {}
        reader = csv.DictReader(flight_data_file, delimiter = ',')

        for row in reader:
            flight={}
            flight['number'] = row['flight_no']
            flight['origin'] = row['origin']
            flight['destination'] = row['destination']
            flight['departure'] = datetime.datetime.fromisoformat(row['departure'])
            flight['arrival'] = datetime.datetime.fromisoformat(row['arrival'])
            flight['base_price'] = row['base_price']
            flight['bag_price'] = row['bag_price']
            flight['bags_allowed'] = row['bags_allowed']

            flights.setdefault(flight['origin'],[])

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

def find_all_paths(graph, src, dst,flight_data):


    def _inner_find_all_paths(graph, src, dst,arrival, current_path,flight_data):
    
        current_path.append(src)
        if src == dst:
            finished_paths.append(tuple(current_path))
        
        else:
            for airport in graph[src]:
                for i, flightpath in enumerate(flight_data[src]):
                    print(i,':',flightpath)
                    layover_time = (flightpath['departure'] - arrival)

                    layover_OK = datetime.timedelta(hours=1) < layover_time < datetime.timedelta(hours=6)

                if airport not in current_path and layover_OK:
                    _inner_find_all_paths(graph, airport, dst,flightpath['arrival'], current_path,flight_data)
        
        current_path.pop()

    current_path=[src]
    finished_paths = []

    for airport in graph[src]:
        for i, flightpath in enumerate(flight_data[src]):
            _inner_find_all_paths(graph, flightpath['destination'], dst, flightpath['arrival'] , current_path,flight_data)
    print(finished_paths)

if __name__ == '__main__':
    flight_data = read_flight_data('example/example0.csv')
    print(flight_data)
    flight_graph = construct_graph(flight_data)
    print(flight_graph)
    find_all_paths(flight_graph, 'WIW','RFZ',flight_data)


