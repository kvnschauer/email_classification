import os
import json
import datetime
import pandas
import matplotlib.pyplot as plt

from pandas import DataFrame
from postgres_db_client import PostgresDbConnector

class Data_analyzer:
    __db_connector: PostgresDbConnector
    __config_file_path = 'C:\\repos\\email_classification\\config.json'
    __analysis_backup_path = 'C:\\repos\\email_classification\\Data_Analysis'

    def __init__(self):
        config = json.load(open(self.__config_file_path))
        self.__db_connector = PostgresDbConnector(config)

    def analyze_data_all(self):
        # read in data and create directory
        data: DataFrame = self.__db_connector.read_emails_bulk(1)
        data_next: DataFrame = data
        while len(data_next) > 0:
            data_next = self.__db_connector.read_emails_bulk(int(data_next.id.max()))
            if len(data_next) > 0:
                data = pandas.concat([data, data_next])

        date_time_now = datetime.datetime.now()
        folder_name = '{}_{}_{}_{}_{}_{}'.format(date_time_now.month,
                                    date_time_now.day,
                                    date_time_now.year,
                                    date_time_now.hour,
                                    date_time_now.minute,
                                    date_time_now.second)
        new_folder_path = self.__analysis_backup_path + '\\' + folder_name
        #os.mkdir(new_folder_path)

        stats = (f'Dataset total: {len(data)}\n\n'
                 f'Columns: {data.columns}\n\n'
                 f'Percent non spam: {round(len(data.loc[data.is_spam == False]) / len(data), 3) * 100}\n\n'
                 f'Email source info:\n {data.source.value_counts()}\n\n'
                 f'Email size stats non spam (kilobyte):\n {(data.loc[data.is_spam == False].size_bytes / 1000).describe()}\n\n'
                 f'Email size stats spam (kilobyte):\n {(data.loc[data.is_spam == True].size_bytes / 1000).describe()}\n\n')

        print(stats)
        # with open(new_folder_path + '\\stats.txt', 'a') as f:
        #     f.write(stats)