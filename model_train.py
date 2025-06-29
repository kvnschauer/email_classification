import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import re

# two models to test out
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression

class Model_Train:

    __vectorizer: TfidfVectorizer
    __hot_encoder: OneHotEncoder

    def __init__(self):
        self.__vectorizer = TfidfVectorizer(stop_words='english')
        self.__hot_encoder = OneHotEncoder(sparse_output=True)

    @staticmethod
    def train_model(train_data: DataFrame):
        """
             Handles training the model
        """
        # clean and transform data for training
        # select rows where subject and sender are present
        train_data = train_data.loc[(~pd.isnull(train_data.subject)) & (~pd.isnull(train_data.sender_address))]

        # break up sender local and domain into different features
        train_data['sender_local'] = train_data.sender_address.map(lambda x: re.search('.*(?=@)', x).group(0))
        train_data['sender_domain'] = train_data.sender_address.map(lambda x: re.search('(?<=@).*', x).group(0))

        # break up data into trn, test and validation sets
        train_set, test_set = train_test_split(train_data, test_size=.2, stratify=train_data['is_spam'], random_state=22)

        percent_non_spam = round(len(train_data.loc[train_data.is_spam == False]) / len(train_data), 3) * 100
        train_percent_non_spam = round(len(train_set.loc[train_set.is_spam == False]) / len(train_set), 3) * 100

        # verify that train set is stratified by is_spam feature
        print(f'Full set non spam: {percent_non_spam} train set non spam: {train_percent_non_spam}')

        #encoded_sender = hot_encoder.fit_transform(train_data[['sender_address']])
        #encoded_subject = self.__vectorizer.fit_transform(train_data.subject)

        #svc = LinearSVC()
        #svc.fit([encoded_sender, encoded_subject], train_data.is_spam)


