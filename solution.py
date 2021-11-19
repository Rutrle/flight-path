import csv
import datetime
import json
import copy
import argparse
import sys
import tkinter


class FlightConnections:
    '''
    Takes in 
    '''

    def __init__(self, user_input):
        flight_data = self.read_flight_data(user_input['source'])

        possible_paths = self.find_all_paths(
            user_input['origin'], user_input['destination'], flight_data, user_input['bag_number'])
        print(possible_paths)
        if len(possible_paths) > 0:
            self.flight_paths_output = self.convert_to_JSON(
                possible_paths, user_input['bag_number'])
        else:
            self.flight_paths_output = None

    def read_flight_data(self, source):
        '''
        Reads csv file with flights data on 'source' path and returns
        them as dictionary where key to the list of flights is their origin
        :param source: str path
        '''

        with open(source, 'r') as flight_data_file:
            flights = {}
            reader = csv.DictReader(flight_data_file, delimiter=',')

            for row in reader:
                flight = {
                    'flight_no': row['flight_no'],
                    'origin': row['origin'],
                    'destination': row['destination'],
                    'departure': datetime.datetime.fromisoformat(row['departure']),
                    'arrival': datetime.datetime.fromisoformat(row['arrival']),
                    'base_price': float(row['base_price']),
                    'bag_price': float(row['bag_price']),
                    'bags_allowed': int(row['bags_allowed'])
                }

                flights.setdefault(flight['origin'], [])
                flights[flight['origin']].append(flight)

            return flights

    def find_all_paths(self, src, dst, flight_data, bags_num=0, return_ticket=True):

        def _inner_find_all_paths(inbound_flight, dst, current_path, flight_data, current_visited, bags_num, return_flight):

            current_path.append((inbound_flight))
            current_visited.append(inbound_flight['destination'])

            if inbound_flight['destination'] == dst:

                if return_flight == False:
                    finished_paths.append(tuple(current_path))
                else:
                    current_visited = [dst]
                    print(dst, former_src)
                    for new_flightpath in flight_data[dst]:
                        layover_time = (
                            new_flightpath['departure'] - inbound_flight['arrival'])
                        layover_ok = datetime.timedelta(
                            hours=1) <= layover_time <= datetime.timedelta(hours=120)

                        if new_flightpath['destination'] not in current_visited and layover_ok and new_flightpath['bags_allowed'] >= bags_num:
                            _inner_find_all_paths(
                                new_flightpath, former_src, current_path, flight_data, current_visited, bags_num, False)

            else:
                for new_flightpath in flight_data[inbound_flight['destination']]:

                    layover_time = (
                        new_flightpath['departure'] - inbound_flight['arrival'])
                    layover_ok = datetime.timedelta(
                        hours=1) <= layover_time <= datetime.timedelta(hours=6)

                    if new_flightpath['destination'] not in current_visited and layover_ok and new_flightpath['bags_allowed'] >= bags_num:
                        _inner_find_all_paths(
                            new_flightpath, dst, current_path, flight_data, current_visited, bags_num, return_flight)

            current_path.pop()
            current_visited.pop()

        current_visited = [src]
        finished_paths = []
        former_src = src

        for new_flightpath in flight_data[src]:
            if new_flightpath['bags_allowed'] >= bags_num:
                _inner_find_all_paths(new_flightpath, dst, [],
                                      flight_data, current_visited, bags_num, return_ticket)

        return finished_paths

    def convert_to_JSON(self, flight_paths, bag_num):
        '''
        Converts 'flight_paths' to correct output format
        and then prints and saves the ouput in json format
        :param flight_paths: list
        :param bag_num: int

        '''
        json_export = []

        for flight_path in flight_paths:
            current_path = self.prepare_flight_path(flight_path, bag_num)
            json_export.append(current_path)

        with open(f"{json_export[0]['origin']}-{json_export[0]['destination']}_flight_paths.json", mode='w') as write_file:
            json.dump(json_export, write_file, indent=4)

        return json.dumps(json_export, indent=4)

    def prepare_flight_path(self, flight_path, bag_num):
        '''
        gives data from single valid flight path correct structure for json export
        :param flight_path: dict
        :param bag_num: int
        :returns: dict
        '''
        bags_allowed = float('inf')
        flights = []
        total_price = 0
        travel_time = (flight_path[-1]['arrival'] -
                       flight_path[0]['departure'])

        for flight in flight_path:

            current_flight = copy.deepcopy(flight)
            current_flight['departure'] = current_flight['departure'].isoformat()
            current_flight['arrival'] = current_flight['arrival'].isoformat()

            flights.append(current_flight)
            total_price += current_flight["base_price"] + \
                current_flight["bag_price"]*bag_num

            bags_allowed = min(bags_allowed, current_flight["bags_allowed"])

        prepared_path = {
            "flights": flights,
            "bags_allowed": bags_allowed,
            "bags_count": bag_num,
            "destination": flight_path[-1]['destination'],
            'origin': flight_path[0]['origin'],
            'total_price': total_price,
            'travel_time': str(travel_time)
        }

        return prepared_path


def input_control():
    arguments = {}

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('source', type=str,
                            help='location of file with flight data')
        parser.add_argument('-o', '--origin', type=str,
                            required=True, help='origin of the flight')
        parser.add_argument('-d', '--destination', type=str,
                            required=True, help='destination of the flight')
        parser.add_argument('--bags', type=str, required=False)

        args = parser.parse_args()
        print(args.bags)

        arguments = {
            'source': args.source,
            'origin': args.origin,
            'destination': args.destination,
            'bag_number': 0
        }
        if args.bags != None:
            arguments['bag_number'] = int(args.bags)
    else:
        print('here goes tkinter')
        arguments = {
            'source': 'example\\example0.csv',
            'origin': 'WIW',
            'destination': 'ECV',
            'bag_number': 0
        }

    return arguments


if __name__ == '__main__':
    user_input = input_control()

    flight_conections = FlightConnections(user_input)

    print(flight_conections.json_output)
