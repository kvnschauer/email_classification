from Data_Load.data_load import load_data_all
from data_analyzer import Data_analyzer

analyzer = Data_analyzer()
function_to_execute = 0
user_input = ''
available_functions = { 1: load_data_all, 2: analyzer.analyze_data_all}

while function_to_execute not in available_functions:
    user_input = input('Choose an option: \n'
                                '1. load all email data\n'
                                '2. analyze data\n\n')

    try:
        function_to_execute = int(user_input)
    except ValueError:
        print('Please enter a numeric input\n\n')
        continue

    if function_to_execute not in available_functions:
        print("Please choose a valid option.")

available_functions[function_to_execute]()
