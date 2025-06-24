import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.preprocessing import OneHotEncoder

class Model_Train:

    __vectorizer: TfidfVectorizer

    def __init__(self):
        self.__vectorizer = TfidfVectorizer(stop_words='english')

    def train_model(self, train_data: DataFrame):
        """
             Handles training the model
        """
        # clean and transform data for training
        # select rows where subject and sender are present
        train_data = train_data.loc[(~pd.isnull(train_data.subject)) & (~pd.isnull(train_data.sender_address))]
        hot_encoder = OneHotEncoder(sparse_output=True)
        print(train_data[['sender_address']].head())

        # TODO
        # break up sender local and domain into different features
        # break up data into trn, test and validation sets

        encoded_sender = hot_encoder.fit_transform(train_data[['sender_address']])
        encoded_subject = self.__vectorizer.fit_transform(train_data.subject)

        #svc = LinearSVC()
        #svc.fit([encoded_sender, encoded_subject], train_data.is_spam)


