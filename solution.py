import csv
import datetime
import json
import argparse
import sys
import os
import tkinter
from tkinter import ttk, messagebox
from copy import deepcopy


class FlightConnections:
    '''
    Takes in 'user_input', reads flight data from address provided in 'user_input' and finds
    all possible flight paths according to it and stores them into 'flight_paths_output' attribute,
    either in .json format, if some paths are found ot as a None if no paths are found
    :param user_input: dictionary
    '''

    def __init__(self, user_input):
        flight_data = self.read_flight_data(user_input['source'])

        possible_paths = self.find_all_paths(
            user_input['origin'], user_input['destination'], flight_data, user_input['bag_number'], user_input['return_flag'])

        if len(possible_paths) > 0:
            self.flight_paths_output = self.convert_to_JSON(
                possible_paths, user_input)
        else:
            self.flight_paths_output = None

    def read_flight_data(self, source):
        '''
        Reads csv file with flights data on 'source' path and returns
        them as dictionary where key to the list of flights is their origin
        :param source: str path
        :returns: dict
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

    def find_all_paths(self, src, dst, flight_data, bags_num=0, return_ticket=False):
        '''
        Uses backtracking to find all avaiable paths in 'flight_data' between starting airport 'src'
        and destination 'dst', in conformity with number of bags 'bags_num'
        :param src: string
        :param dst: string
        :param flight_data: dict
        :param bags_num: int
        :param return_ticket: boolean
        :returns: list of tuples
        '''

        def _inner_find_all_paths(inbound_flight, dst, current_path, flight_data, current_visited, bags_num, return_flight):
            '''
            Uses backtracking to find all avaiable paths in 'flight_data' between 'inbound_flight' destination and
            whole journey destination 'dst', in conformity with number of bags 'bags_num',
            not visiting any of the already visited 'current_visited' airports
            In case 'return_flight' is true, then after finding journey destination goes back to journey origin
            :param inbound_flight: dict
            :param dst: string
            :param current_path: list
            :param flight_data: dict
            :param current_visited: list
            :param bags_num: int
            :param return_flight: boolean
            '''

            current_path.append((inbound_flight))
            current_visited.append(inbound_flight['destination'])

            if inbound_flight['destination'] == dst:

                if return_flight == False:
                    finished_paths.append(tuple(current_path))
                else:
                    new_visited = [dst]

                    for new_flightpath in flight_data[dst]:
                        flightpath_ok = self.flightpath_valid(
                            new_flightpath, new_visited, inbound_flight['arrival'], bags_num, 1, 672)

                        if flightpath_ok:
                            _inner_find_all_paths(
                                new_flightpath, former_src, current_path, flight_data, new_visited, bags_num, False)

            else:
                for new_flightpath in flight_data[inbound_flight['destination']]:
                    flightpath_ok = self.flightpath_valid(
                        new_flightpath, current_visited, inbound_flight['arrival'], bags_num)

                    if flightpath_ok:
                        _inner_find_all_paths(
                            new_flightpath, dst, current_path, flight_data, current_visited, bags_num, return_flight)

            current_path.pop()
            current_visited.pop()

        self.check_validity_src_dst(src, dst, flight_data)

        current_visited = [src]
        finished_paths = []
        former_src = src

        for new_flightpath in flight_data[src]:
            if new_flightpath['bags_allowed'] >= bags_num:
                _inner_find_all_paths(new_flightpath, dst, [],
                                      flight_data, current_visited, bags_num, return_ticket)

        return finished_paths

    def flightpath_valid(self, flight, visited, previous_arrival, bags_num, layover_min=1, layover_max=6):
        '''
        checks validity of given 'flight' 
        :param flight: dictionary
        :param visited: list
        :param previous_arrival: datetime obj
        :param bags_num: int
        :param layover_min: int
        :param layover_max: int
        :returns: bool
        '''
        layover_time = (flight['departure'] - previous_arrival)
        layover_ok = datetime.timedelta(
            hours=layover_min) <= layover_time <= datetime.timedelta(hours=layover_max)

        bags_ok = flight['bags_allowed'] >= bags_num
        airport_ok = flight['destination'] not in visited

        flight_valid = layover_ok and airport_ok and bags_ok

        return flight_valid

    def check_validity_src_dst(self, origin, destination, flight_data):
        '''
        checks that airport codes 'origin' and 'destination' are
        valid keys in flight_data, if not calls 'raise_error'
        :param origin: str
        :param destination: str
        :param flight_data: dictionary
        '''

        valid_airports = ', '.join(flight_data.keys())

        if origin not in flight_data:
            raise_error(
                f"Wrong input, no airport named '{origin}' in provided flights data \nValid airport codes in provided flights data:  {valid_airports}")

        if destination not in flight_data:
            raise_error(
                f"Wrong input, no airport named '{destination}' in provided flights data\nValid airport codes in provided flights data:  {valid_airports}")

    def convert_to_JSON(self, flight_paths, user_input):
        '''
        Converts 'flight_paths' to correct output format
        and then returns and saves the ouput in json format
        :param flight_paths: list
        :param user_input: dictionary
        :returns: json list
        '''
        json_export = []

        for flight_path in flight_paths:
            current_path = self.prepare_flight_path(
                flight_path, user_input['bag_number'])
            json_export.append(current_path)

        json_export = sorted(json_export, key=lambda x: x['total_price'])

        if not os.path.exists('results'):
            os.mkdir('results')

        if user_input['return_flag']:
            file_name = f"{user_input['origin']}-{user_input['destination']}-{user_input['origin']}_flight_paths.json"

        else:
            file_name = f"{user_input['origin']}-{user_input['destination']}_flight_paths.json"

        result_address = os.path.join('results', file_name)

        if user_input['save_flag']:
            with open(result_address, mode='w') as write_file:
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

            current_flight = deepcopy(flight)
            current_flight['departure'] = current_flight['departure'].isoformat()
            current_flight['arrival'] = current_flight['arrival'].isoformat()

            flights.append(current_flight)
            total_price += current_flight['base_price'] + \
                current_flight['bag_price']*bag_num

            bags_allowed = min(bags_allowed, current_flight['bags_allowed'])

        prepared_path = {
            'flights': flights,
            'bags_allowed': bags_allowed,
            'bags_count': bag_num,
            'destination': flight_path[-1]['destination'],
            'origin': flight_path[0]['origin'],
            'total_price': total_price,
            'travel_time': str(travel_time)
        }

        return prepared_path


class GUIInput:
    '''
    Creates tkinter window for filling user inputs for finding
    flight paths, saves them as 'arguments' attribute
    '''

    def __init__(self):
        self.arguments = {}
        self.root = tkinter.Tk()
        self.root.title('Find flight connections')
        self.populate(self.root)

        self.root.mainloop()

    def populate(self, root):
        '''
        fills in the 'root' with widgets
        :param root: tkinter Tk object
        '''
        source_label = tkinter.Label(
            root, text='Address of flights dataset*', font=('calibre', 10, 'bold'))
        source_entry = tkinter.Entry(root, font=(
            'calibre', 10, 'normal'), borderwidth=3, width=30)

        origin_label = tkinter.Label(
            root, text='Origin airport code*', font=('calibre', 10, 'bold'))
        origin_entry = tkinter.Entry(root, font=(
            'calibre', 10, 'normal'), borderwidth=3)

        destination_label = tkinter.Label(
            root, text='Destination airport code*', font=('calibre', 10, 'bold'))
        destination_entry = tkinter.Entry(
            root, font=('calibre', 10, 'normal'), borderwidth=3)

        sep = ttk.Separator(root, orient='horizontal')

        bag_number_label = tkinter.Label(
            root, text='Number of bags', font=('calibre', 10, 'bold'))
        bag_number_entry = tkinter.Entry(
            root, font=('calibre', 10, 'normal'), borderwidth=3, width=10)

        return_flag = tkinter.IntVar()
        return_ticket_label = tkinter.Label(
            root, text='Return ticket', font=('calibre', 10, 'bold'))
        return_ticket_check = tkinter.Checkbutton(root, variable=return_flag)

        save_flag = tkinter.IntVar()
        save_flag_label = tkinter.Label(
            root, text='Save results', font=('calibre', 10, 'bold'))
        save_flag_check = tkinter.Checkbutton(root, variable=save_flag)

        info_label = tkinter.Label(
            root, text='* required parameters', font=('calibre', 7))
        sub_btn = tkinter.Button(
            root, text='Find flights!', command=lambda: self.pass_input(source_entry.get(), origin_entry.get(), destination_entry.get(), bag_number_entry.get(), return_flag.get(), save_flag.get()))

        source_label.grid(row=0, column=0, padx=10, pady=5)
        source_entry.grid(row=0, column=1, padx=10, pady=5)
        origin_label.grid(row=1, column=0, padx=10, pady=5)
        origin_entry.grid(row=1, column=1, padx=10, pady=5)
        destination_label.grid(row=2, column=0, padx=10, pady=5)
        destination_entry.grid(row=2, column=1, padx=10, pady=5)
        sep.grid(row=3, column=0, columnspan=3, padx=10, pady=10, ipadx=100)
        bag_number_label.grid(row=4, column=0, padx=10, pady=5)
        bag_number_entry.grid(row=4, column=1, padx=10, pady=5)
        return_ticket_label.grid(row=5, column=0, padx=10, pady=5)
        return_ticket_check.grid(row=5, column=1, padx=10, pady=5)
        save_flag_label.grid(row=6, column=0, padx=10, pady=5)
        save_flag_check.grid(row=6, column=1, padx=10, pady=5)
        info_label.grid(row=7, column=0, pady=10)

        sub_btn.grid(row=99, column=0, columnspan=2, padx=10, pady=10)

    def pass_input(self, source, origin, destination, bags_num, return_flag, save_flag):
        '''
        passes data from tkinter window ('source', 'origin', 'destination', 'bags_num' and 'return_flag')
        into 'arguments' attribute and closes tkinter window afterwards
        :param source: str
        :param origin: str
        :param destination: str
        :param bags_num: str(int)
        :param return_flag: 0 or 1
        :param save_flag: 0 or 1
        '''

        if bags_num == '':
            bags_num = 0

        self.arguments = {
            'source': source,
            'origin': origin,
            'destination': destination,
            'bag_number': bags_num,
            'return_flag': bool(return_flag),
            'save_flag': bool(save_flag)
        }

        self.root.destroy()


def command_line_input():
    '''
    Takes in user input from command line,
     and returns is as a dictionary
    :returns: dictionary
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str,
                        help='Location of file with flights dataset')
    parser.add_argument('-o', '--origin', type=str,
                        required=True, help='Airport code of origin of the flight, must be followed by the three letter airport code')
    parser.add_argument('-d', '--destination', type=str,
                        required=True, help='Airport code of destination of the flight, must be followed by the three letter airport code')
    parser.add_argument('-b', '--bags', type=int, required=False,
                        help='Number of bags you are travelling with')
    parser.add_argument('-r', '--return_ticket',
                        action='store_true', required=False, help='Searches also for return path')

    parser.add_argument('-s', '--save',
                        action='store_true', required=False, help='Saves results in json file')
    args = parser.parse_args()

    arguments = {
        'source': args.source,
        'origin': args.origin,
        'destination': args.destination,
        'bag_number': 0,
        'return_flag': args.return_ticket,
        'save_flag': args.save
    }

    if args.bags is not None:
        arguments['bag_number'] = args.bags

    return arguments


def check_validity(user_input):
    '''
    checks validity of 'user_input', if not valid
    calls raise_error (or raise Exception by itself)
    :param user_input:  dict
    '''
    if user_input['source'] == user_input['origin'] == user_input['destination'] == '':
        # No need for messagebox with raise_error when no input  was provided
        raise Exception('No input')

    if user_input['source'] == '':
        raise_error('Adress of flight dataset is a required value')
    if user_input['origin'] == '':
        raise_error('Origin of flight is a required value')
    if user_input['destination'] == '':
        raise_error('Destination  of flight is a required value')

    if not os.path.exists(user_input['source']):
        raise_error(f"File address '{user_input['source']}' is not valid!")


def raise_error(error_message):
    '''
    displays 'error_message' in message box, then raises exception
    :param error_message: str
    '''
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showerror('error', error_message)

    raise Exception(error_message)


def input_control():
    '''
    switches between command line and GUI user input depending on with
    how many arguments the script was started and returns the input after a bit of cleanup
    :returns: dict
    '''

    if len(sys.argv) > 1:
        user_input = command_line_input()

    else:
        gui_input = GUIInput()
        user_input = gui_input.arguments

    try:
        user_input['bag_number'] = int(user_input['bag_number'])

    except ValueError:
        raise_error('Please enter only numbers for number of bags')

    return user_input


if __name__ == '__main__':
    user_input = input_control()
    check_validity(user_input)

    flight_conections = FlightConnections(user_input)

    if flight_conections.flight_paths_output is not None:
        print(flight_conections.flight_paths_output)
    else:
        print('Sorry, no flights satisfying your request were found.')

    input('Press ENTER to exit')
