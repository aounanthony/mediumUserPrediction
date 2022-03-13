"""
this script contains the constants that will be used in all the other scripts
"""

#base url of the medium website
MEDIUM_URL = "https://medium.com/@"

#directory of the prediction model
MODEL_NAME = "../models/logisticRegressionPredictionModel.pkl"

#directory of the text data vectorizer
VECTORIZER_NAME = "../models/countVectorizer.pkl"

#directory of the new stored accounts
USER_DATA_JSON = "../data/accounts_data.json"

#directory of the labeled training dataset
TRAINING_DATA_JSON = "../data/accounts_training_data.json"

#directory of the labeled testing dataset
TESTING_DATA_JSON = "../data/accounts_testing_data.json"

#directory of the log file
LOGFILE_DIR = "../logs/LogFile.log"

#Mongo connection uri
MONGO_URI = "mongodb://localhost:27017/"

#Mongo database name
DATABASE_NAME = "medium_database"

#Mongo accounts collection name
COLLECTION_NAME = "medium_accounts_collection"