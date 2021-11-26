# Find flight paths

## What it does
This script (solution.py) finds all possible paths between chosen origin and destination airport, according to supplied .csv flights data and user input and prints the results in JSON format. Optionally, user can choose number of bags he wants to travel with, if he want also all possible return flights to be found as well (with) and also if the results should be saved in .JSON file. There are two possibilities how to run it, either through GUI or through supplying arguments directly through command line.

## Install
no installation is needed, script is run directly and project uses only standard library of Python 3.7

## How to use it
There are two ways how to run this script:
    1) run it in command line without any arguments or start the python
     file directly => GUI will open for you to fill in arguments
    2) run it in command line with arguments 

Regardless of the way of launching the script, the results are printed in json format into the console.
If option to save the result was used, results are save also in JSON file in results folder.

### GUI usage
When script is started either directly, or from command line with no arguments, GUI is started(as can be seen in GUI_example.png)
following arguments can be entered into the GUI:
![GUI example](/GUI_example.PNG)

required argument:
 - Address of flight dataset - enter address of csv file with flights data
 - Origin airport code - enter three letter code of origin airport (from where your journey should start)
 - Destination airport code - enter three letter code of destination airport (from where your journey should end)

optional arguments:
 - Number of bags - enter number of bags you want to take on your journey (default is 0)
 - Return ticket - if checked, all possible paths are found from origin aitport to destination airport and back
 - Save results - if checked, results of search are saved as .JSON file in 'results' folder

### Command line usage
input schema:
''' 
python solution.py <source required> -o  <origin required> -d <destination required> -b <bag_number optional> -r -s
'''
example input : python solution.py data.csv -o  DHE -d EZO -b 2 -r -s

takes in flight data from 'data.csv' file and find all paths from origin 'DHE' to destination 'EZO' and then back to the origin
'DHE' (because of the '-r'), taking in account that you want to travel with 2 bags. Results are then printed in json format
into the console and also saved  in  results\DHE-EZO-DHE_flight_paths.json

arguments:
source - positional argument - address of csv file with flights data
origin - [-o, --origin], followed by three letter code of origin airport - required argument
destiantion - [-d, --destination], followed by three letter code of destination airport - required argument
bag_number - [-b, --bags] - number of bags you want to travel with (used for calculation of both price and feasibility of journey)- optional parameter
return - [-r, --return_ticket] - if used, script looks for connections to the given destination and from there back to given origin, optional argument
save - [-s, --save] - if used, results are saved as a .JSON file, optional argument