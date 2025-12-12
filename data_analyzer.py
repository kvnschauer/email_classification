import os
import json
import datetime
import matplotlib.pyplot as plt
import pandas as pd

from model import Model
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from typing import List
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

    @staticmethod
    def __remove_stop_words(words: List[str]):
        english_stop_copy = ENGLISH_STOP_WORDS.copy().union(['-'])
        return [word for word in words if word not in english_stop_copy]

    @staticmethod
    def __lower_case_list(words: List[str]):
        return [word.lower() for word in words]

    @staticmethod
    def __group_list(lst):
        return list(zip(Counter(lst).keys(), Counter(lst).values()))

    @staticmethod
    def __sort_grouped_list(item):
        return item[1]

    def __build_percent_spam_pie(self, save_data, percent_spam, folder_path):
        plt.pie([100 - percent_spam, percent_spam], labels=['Non Spam', 'Spam'], autopct='%1.1f%%')
        if save_data:
            plt.savefig(folder_path + '\\percent_spam_graph.png', dpi=300, bbox_inches='tight', format='png')
            plt.close()
        else:
            plt.show()

    def __build_subject_words_table(self, save_data, email_data, folder_path, is_spam):
        subject_words: List[str] = []
        subject_data = email_data.loc[(~pd.isnull(email_data.subject)) & email_data.is_spam == is_spam]
        for index, email in subject_data.iterrows():
            if email.subject is not None:
                subject_words = subject_words + email.subject.split()


        subject_words = Model.remove_stop_words(subject_words)
        subject_words = self.__lower_case_list(subject_words)

        grouped_subject_words = self.__group_list(subject_words)
        grouped_subject_words.sort(key=self.__sort_grouped_list, reverse=True)

        fig, ax = plt.subplots()
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')
        plt.table([
            [grouped_word[0], grouped_word[1]] for grouped_word in grouped_subject_words[:10]],
            colLabels=['Word', 'Count'], loc='center')
        fig.tight_layout()
        spam_non_spam_title = 'Spam' if is_spam else 'Non-Spam'
        ax.set_title(f'Common {spam_non_spam_title} Subject Words', y=0.8)

        if save_data:
            plt.savefig(folder_path + f'\\common_subject_words_{spam_non_spam_title}.png', format='png')
            plt.close()
        else:
            plt.show()

    def __setup_folder(self, save_data):
        new_folder_path = None

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

        return new_folder_path

    def analyze_data_all(self, data: DataFrame):
        """
            Function to analyze data and print result to a file in new folder

            Parameters:
                data: dataframe of email data to be analyzed
        """
        # generate stats as txt and save if applicable
        save_data: bool = None
        while save_data == None:
            user_input = input('Do you want to save the data from analysis (y/n)?')

            if  user_input.lower() in ['y', 'n']:
                save_data = user_input.lower() == 'y'

        new_folder_path = self.__setup_folder(save_data)
        percent_non_spam = round(len(data.loc[data.is_spam == False]) / len(data), 3) * 100
        stats = (f'Dataset total: {len(data)}\n\n'
                 f'Columns: {data.columns}\n\n'
                 f'Percent non spam: {percent_non_spam}\n\n'
                 f'Email source info:\n {data.source.value_counts()}\n\n')

        print(stats)
        if save_data:
            with open(new_folder_path + '\\stats.txt', 'a') as f:
                f.write(stats)

        #take a look at most common words for spam and non spam emails
        self.__build_subject_words_table(save_data, data, new_folder_path, True)
        self.__build_subject_words_table(save_data, data, new_folder_path, False)
        self.__build_percent_spam_pie(save_data, 100 - percent_non_spam, new_folder_path)