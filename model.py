
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

from typing import List
from pandas.core.interchange.dataframe_protocol import DataFrame
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_predict, cross_val_score, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
import re

# two models to test out
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression

class Model:
    __analysis_backup_path = 'C:\\repos\\email_classification\\Training_Analysis'

    @staticmethod
    def remove_stop_words(words: List[str]):
        english_stop_copy = ENGLISH_STOP_WORDS.copy().union(['-'])
        return [word for word in words if word not in english_stop_copy]

    @staticmethod
    def __get_pre_process_transformer():
        """
           Builds the pre-processing transformer

           Parameters:
               all_data - DataFrame containing all the data collected

           Returns:
               A ColumnTransformer used to pre-process data prior to training
        """
        # Converts DataFrame column to Series
        def get_text_data(X):
            return X.squeeze()

        def to_lower(df: DataFrame, col_name):
            df_copy = df.copy()
            df_copy[col_name] = df_copy[col_name].str.lower()
            return df_copy

        def subject_remove_stop_words(df: DataFrame, col_name):
            df_copy = df.copy()
            return np.array([ ' '.join(word for word in Model.remove_stop_words(x.split()))
                     for x in df_copy[col_name] ]).reshape(-1, 1)

        return ColumnTransformer(transformers=[
            ('sender_local', Pipeline([
                ('lower_case', FunctionTransformer(func=to_lower, kw_args={'col_name': 'sender_local'})),
                ('hot_encoder', OneHotEncoder(sparse_output=True, handle_unknown='ignore'))
        ]), ['sender_local']),
            ('sender_domain', Pipeline([
                ('lower_case', FunctionTransformer(func=to_lower, kw_args={'col_name': 'sender_domain'})),
                ('hot_encoder', OneHotEncoder(sparse_output=True, handle_unknown='ignore'))
        ]), ['sender_domain']),
            ('subject', Pipeline([
                    ('lower_case', FunctionTransformer(func=to_lower, kw_args={'col_name': 'subject'})),
                    ('stop_words', FunctionTransformer(func=subject_remove_stop_words, kw_args={'col_name': 'subject'})),
                    ('to_series', FunctionTransformer(get_text_data)),
                    ('tfidf', TfidfVectorizer(max_features=5000))
                ]), ['subject'])
        ])

    def __build_learning_curve_graph(self, save_data, folder_path, train_sizes, train_mean, test_mean):
        plt.plot(train_sizes, train_mean, label='Training score')
        plt.plot(train_sizes, test_mean, label='Cross-validation score')
        plt.xlabel('Training Size')
        plt.ylabel('Accuracy')
        plt.legend()

        if save_data:
            plt.savefig(folder_path + '\\learning_curve.png', dpi=300, bbox_inches='tight', format='png')
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

    def train(self, all_data: DataFrame):
        """
             Handles training the model
        """
        # clean and transform data for training
        # select rows where subject and sender are present
        def __reg_replace(regex_str, initial_str):
            reg_search_result = re.search(regex_str, initial_str)
            return '' if not reg_search_result else reg_search_result.group(0)

        save_data = None
        while save_data == None:
            user_input = input('Do you want to save the data from analysis (y/n)?')

            if user_input.lower() in ['y', 'n']:
                save_data = user_input.lower() == 'y'

        new_folder_path = self.__setup_folder(save_data)

        all_data = all_data.loc[(~pd.isnull(all_data.subject)) & (~pd.isnull(all_data.sender_address))]
        # break up sender local and domain into different features
        all_data['sender_local'] = all_data.sender_address.map(lambda x: __reg_replace('.*(?=@)', x))
        all_data['sender_domain'] = all_data.sender_address.map(lambda x: __reg_replace('(?<=@).*', x))

        # break up data into trn, test and validation sets
        train_set, test_set = train_test_split(all_data, test_size=.2, stratify=all_data['is_spam'], random_state=22)
        percent_non_spam = round(len(all_data.loc[all_data.is_spam == False]) / len(all_data), 3) * 100
        train_percent_non_spam = round(len(train_set.loc[train_set.is_spam == False]) / len(train_set), 3) * 100

        # verify that train set is stratified by is_spam feature
        print(f'Full set non spam: {percent_non_spam} train set non spam: {train_percent_non_spam}')

        svc_pipeline = Pipeline([
            ('preprocessing', self.__get_pre_process_transformer()),
            ('classifier', LinearSVC())
        ])

        # Input features and target
        X = train_set[['sender_local', 'sender_domain', 'subject']]
        y = train_set['is_spam']

        train_sizes, train_scores, test_scores = learning_curve(
            svc_pipeline, X, y, cv=5, scoring='accuracy', train_sizes=np.linspace(0.1, 1.0, 20)
        )

        # Compute mean scores
        train_mean = np.mean(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)

        # Plot learning curves
        self.__build_learning_curve_graph(save_data, new_folder_path, train_sizes, train_mean, test_mean)

        # svc_scores = cross_val_score(svc_pipeline, X, y, cv=3, scoring='accuracy', verbose=2)
        # print(svc_scores)

        #y_predict = cross_val_predict(svc_pipeline, X, y, cv=3)
        #cf = confusion_matrix(y, y_predict, labels=[0, 1])
        #print(cf)
        #svc_pipeline.fit(X, y)