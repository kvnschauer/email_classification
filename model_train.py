from sklearn.feature_extraction.text import TfidfVectorizer

class Model_Train:

    __vectorizer: TfidfVectorizer

    def __init__(self):
        self.__vectorizer = TfidfVectorizer(stop_words='english')


    def train_model(self, train_data):
        """
             Handles training the model
        """

        vectorized_data = self.__vectorizer.fit_transform(train_data.loc[:, 'subject'])

        print(vectorized_data.toarray()[0])
        print( self.__vectorizer.get_feature_names_out())