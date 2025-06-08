from pandas import DataFrame
from Data_Load.data_load import load_data_all
from data_analyzer import Data_analyzer
from postgres_db_client import PostgresDbConnector
import json

# initialize variables
db_connector: PostgresDbConnector
config_file_path = 'C:\\repos\\email_classification\\config.json'
analysis_backup_path = 'C:\\repos\\email_classification\\Data_Analysis'

config = json.load(open(config_file_path))
db_connector = PostgresDbConnector(config)
analyzer = Data_analyzer()
function_to_execute = 0
user_input = ''
data: DataFrame = db_connector.read_emails_bulk()
available_functions = { 1: load_data_all, 2: lambda: analyzer.analyze_data_all(data)}

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
