import csv
import datetime
import json
import copy
import argparse
import sys
import os
import tkinter
from tkinter import ttk, messagebox


class FlightConnections:
    '''
    Takes in 'user_input'
    :param user_input: dictionary
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

        check_validity_src_dst(src, dst, flight_data)

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


class GUIInput:
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
            root, text='Adress of flights dataset*', font=('calibre', 10, 'bold'))
        source_entry = tkinter.Entry(root, font=(
            'calibre', 10, 'normal'), borderwidth=3, width=30)

        origin_label = tkinter.Label(
            root, text='Origin*', font=('calibre', 10, 'bold'))
        origin_entry = tkinter.Entry(root, font=(
            'calibre', 10, 'normal'), borderwidth=3)

        destination_label = tkinter.Label(
            root, text='Destination*', font=('calibre', 10, 'bold'))
        destination_entry = tkinter.Entry(
            root, font=('calibre', 10, 'normal'), borderwidth=3)

        sep = ttk.Separator(root, orient='horizontal')

        bag_number_label = tkinter.Label(
            root, text='Number of bags', font=('calibre', 10, 'bold'))
        bag_number_entry = tkinter.Entry(
            root, font=('calibre', 10, 'normal'), borderwidth=3, width=10)

        return_flag = tkinter.IntVar()
        return_ticket_label = tkinter.Label(
            root, text='Return possible?', font=('calibre', 10, 'bold'))
        return_ticket_check = tkinter.Checkbutton(root, variable=return_flag)

        info_label = tkinter.Label(
            root, text='* required parameters', font=('calibre', 7))
        sub_btn = tkinter.Button(
            root, text='Find flights!', command=lambda: self.pass_input(source_entry.get(), origin_entry.get(), destination_entry.get(), bag_number_entry.get(), return_flag.get()))

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

        info_label.grid(row=6, column=0, pady=10)

        sub_btn.grid(row=99, column=0, columnspan=2, padx=10, pady=10)

    def pass_input(self, source, origin, destination, bags_num, return_flag):
        '''
        passes data from tkinter window ('source', 'origin', 'destination', 'bags_num' and 'return_flag')
        into 'arguments' attribute and closes tkinter window afterwards
        :param source: str
        :param origin: str
        :param destination: str
        :param bags_num: str(int)
        :param return_flag: 0 or 1
        '''

        if bags_num == '':
            bags_num = 0
        self.arguments = {
            'source': source,
            'origin': origin,
            'destination': destination,
            'bag_number': int(bags_num),
            'return_flag': bool(return_flag)
        }
        self.root.destroy()


def command_line_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str,
                        help='location of file with flights dataset')
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
        'bag_number': 0,
        'return_flag': False
    }

    if args.bags != None:
        arguments['bag_number'] = int(args.bags)

    return arguments


def check_validity_src_dst(src, dst, flight_data):

    valid_airports = ', '.join(flight_data.keys())

    if src not in flight_data:
        raise_error(
            f"Wrong input, no airport named '{src}' in provided flights data \nValid airport codes in provided flights data:  {valid_airports}")

    if dst not in flight_data:
        raise_error(
            f"Wrong input, no airport named '{dst}' in provided flights data\nValid airport codes in provided flights data:  {valid_airports}")


def check_validity(user_input):
    '''
    checks validity of 'user_input'
    :param user_input:  dict
    '''

    if user_input['source'] == user_input['origin'] == user_input['destination'] == '':
        # need for messagebox with raise_error when no input  was provided
        raise Exception('No input')

    if user_input['source'] == '':
        raise_error("Adress of flight dataset is a required value")
    if user_input['origin'] == '':
        raise_error("Origin of flight is a required value")
    if user_input['destination'] == '':
        raise_error("Destination  of flight is a required value")

    if not os.path.exists(user_input['source']):
        raise_error(f"file address '{user_input['source']}' is not valid!")


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
    how many arguments the script was started and returns it afterwards
    :returns: dict
    '''

    if len(sys.argv) > 1:
        user_input = command_line_input()

    else:
        gui_input = GUIInput()
        user_input = gui_input.arguments

    return user_input


if __name__ == '__main__':
    user_input = input_control()
    check_validity(user_input)

    flight_conections = FlightConnections(user_input)

    if flight_conections.flight_paths_output != None:
        print(flight_conections.flight_paths_output)
    else:
        print('Sorry, no flights satisfying your request were found.')

    input('Press ENTER to exit')
