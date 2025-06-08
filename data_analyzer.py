import os
import json
import datetime
import matplotlib.pyplot as plt


from pandas import DataFrame
from postgres_db_client import PostgresDbConnector

class Data_analyzer:
    """
        Class to handle analyzing data
    """
    __db_connector: PostgresDbConnector
    __config_file_path = 'C:\\repos\\email_classification\\config.json'
    __analysis_backup_path = 'C:\\repos\\email_classification\\Data_Analysis'

    def __init__(self):
        config = json.load(open(self.__config_file_path))
        self.__db_connector = PostgresDbConnector(config)

    def analyze_data_all(self, data: DataFrame):
        """
            Function to analyze data and print result to a file in new folder

            Parameters:
                data: dataframe of email data to be analyzed
        """
        # generate stats as txt and save if applicable
        save_data: bool = None
        new_folder_path: str = ''
        while save_data == None:
            user_input = input('Do you want to save the data from analysis (y/n)?')

            if  user_input.lower() in ['y', 'n']:
                save_data = user_input.lower() == 'y'


        percent_non_spam = round(len(data.loc[data.is_spam == False]) / len(data), 3) * 100
        stats = (f'Dataset total: {len(data)}\n\n'
                 f'Columns: {data.columns}\n\n'
                 f'Percent non spam: {percent_non_spam}\n\n'
                 f'Email source info:\n {data.source.value_counts()}\n\n'
                 f'Email size stats non spam (kilobyte):\n {(data.loc[data.is_spam == False].size_bytes / 1000).describe()}\n\n'
                 f'Email size stats spam (kilobyte):\n {(data.loc[data.is_spam == True].size_bytes / 1000).describe()}\n\n')

        print(stats)

        if save_data:
            date_time_now = datetime.datetime.now()
            folder_name = '{}_{}_{}_{}_{}_{}'.format(date_time_now.month,
                                                     date_time_now.day,
                                                     date_time_now.year,
                                                     date_time_now.hour,
                                                     date_time_now.minute,
                                                     date_time_now.second)
            new_folder_path = self.__analysis_backup_path + '\\' + folder_name
            os.mkdir(new_folder_path)
            with open(new_folder_path + '\\stats.txt', 'a') as f:
                f.write(stats)

        # create graphs and save if applicable
        print(data.loc[:, 'is_spam'])
        plt.pie([percent_non_spam, 100 - percent_non_spam], labels=['Non Spam', 'Spam'], autopct='%1.1f%%')

        if save_data:
            plt.savefig(new_folder_path + '\\percent_spam_graph.png', dpi=300, bbox_inches='tight', format='png')
            plt.close()
        else:
            plt.show()




