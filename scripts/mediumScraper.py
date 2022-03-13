import requests
import re
import json
import constants
import pickle
import pandas as pd

from sklearn.metrics import classification_report, confusion_matrix
from logHandling import exception_handler
from bs4 import BeautifulSoup
from copy import deepcopy
from pymongo import MongoClient



@exception_handler
def get_medium_page_data(user_id: str) -> str:
    """
    this function takes the user id of a medium user and scrapes the related data to return it in a json format

    Parameters
    ----------
    user_id : str
        the user id of the medium account to scrape.

    Returns
    -------
    str
        string containing the json data of the medium user.

    """
    #set the medium link and get the page data using the requests module
    medium_link = constants.MEDIUM_URL + str(user_id)
    medium_html_page = requests.get(medium_link)
    
    #parse the page content with beautifulsoup
    soup = BeautifulSoup(medium_html_page.content, 'html.parser')
    #navigate to the right hand section of the medium page containing the user data
    user_soup= soup.find('div', class_="ag dq ck cj")
    #find the tags containing the user following information to be extracted
    top_following_soup = user_soup.findAll('a', class_="au av aw ax ay az ba bb bc bd be bf bg bh bi")
    #find the tag containing the nb of followers to be formated
    nb_followers_soup = user_soup.find('span', class_="pw-follower-count").text.split(" ")[0]
    
    #create the user_data dictionnary containing the scraped data
    user_data = dict()
    user_data["medium"] = user_id
    user_data["name"] = user_soup.find('h2', class_="pw-author-name").text
    
    #format the number of followers by transforming numbers like 14k and 1.2M to an integer like 14000 and 12000000
    if "M" in nb_followers_soup: 
        user_data["num_followers"] = int(float(nb_followers_soup.replace("M",""))*1000000)
    elif "K" in nb_followers_soup:
        user_data["num_followers"] = int(float(nb_followers_soup.replace("K",""))*1000)
    else:
        user_data["num_followers"] = int(nb_followers_soup)
        
    #list comprehension that finds links that contain @user_id? to extract the user_id of all the top 5 following
    #this comprehension also accounts for cases where the link is formated as https://user_id.medium.com
    user_data["following_top_5"] = [re.search('@(.*)?\?', following['href']).group(1) if ("/@" in following['href']) else re.search('https://(.*).medium', following['href']).group(1) if (".medium.com" in following['href']) else '' for following in top_following_soup if (following.find('h4'))]
    
    #check if the user displays following data and if it is found form the standard all following link that follows this format https://medium.com/@user_id/following
    user_data["all_following_link"] = ""
    if user_soup.find('a', text=re.compile('see all', re.I)) is not None: 
        user_data["all_following_link"] = medium_link + "/following"
        
    #check if the user has a description to save
    user_data["description"] = ""
    if "See all (" not in user_soup.findAll('p')[1].text and user_soup.findAll('p')[1].text != "Help":
        user_data["description"] = u"" + user_soup.findAll('p')[1].text
        
    #check for links inside the description to create a list using the following comprehension
    user_data["links_of_description"] = [description_link['href'] for description_link in user_soup.findAll('p')[1].findAll('a')]
    #set the type tag to an empty string to fill it with a prediction or to manually label it later
    user_data["type"] = ""
    
    #return the user data dict in a json format
    return json.dumps(user_data)
    

@exception_handler
def collect_medium_accounts(first_user_id: str, number_to_collect: int = 500, predict_account: bool = False, store_accounts: bool = False, use_mongodb: bool = False) -> str:
    """
    this function takes the user id to start with and scrapes the data using the get_medium_page_data function.
    collect a number of accounts that are not in the training dataset starting from the initial account by adding all the unique top 5 following accounts from subsequent scraped users until the 
    required number of accounts is reached.
    this function can also prerdict the user type and store the outcome if desired

    Parameters
    ----------
    first_user_id : str
        the used id to start scraping data from to get other users.
    number_to_collect : int, optional
        the number of total users to collect. The default is 500.
    predict_account : bool, optional
        variable that defines whether the user type should be predicted or not. The default is False.
    store_accounts : bool, optional
        variable to decide whether to store the accounts of not. The default is False.
    use_mongodb : bool, optional
        variable to decide to store the accounts in a json in directory defined in the constants or in mongodb. The default is False.

    Returns
    -------
    str
        string containing an array of user data formatted in json.

    """
    #if the number to collect is lower than 1 stop the function
    if number_to_collect<1:
        return "provide a number greater than 0"
    #Scrape the data from the first account
    account_data_list = []
    first_account_data_dict = json.loads(get_medium_page_data(first_user_id))
    #predict the type if the parameter predict_amount is true
    if(predict_account):
        #call the prediction function with the description of the scraped account
        first_account_data_dict["type"] = predict_medium_account("None",first_account_data_dict["description"])
        first_account_data_dict["verified"] = "False"
    #add the list of top 5 following accounts to the list of accounts to scrape
    account_data_list.append(first_account_data_dict)
    accounts_to_scrape_list = deepcopy(first_account_data_dict["following_top_5"])
    
    #add all the medium ids of the accounts in the training dataset to a set of strings called account_id_set
    account_id_set = set()
    with open(constants.TRAINING_DATA_JSON, "r") as file:
        training_data_json = json.loads(file.read())
    for training_account in training_data_json:
        account_id_set.add(training_account["medium"])
     
    #while the amount of account data collected is still lower than the required number of accounts continue scraping
    while(len(account_data_list) < int(number_to_collect)):
        
        #if the medium id provided found in the list of accounts to scrape is a string and has not already been scraped call the scraping function
        if(accounts_to_scrape_list[-1] and  accounts_to_scrape_list[-1] not in account_id_set):
            medium_account_json = get_medium_page_data(accounts_to_scrape_list[-1])
            
            #if the scraped data is a string, the scraping has succeeded and we store the json data in a python dict 
            if(isinstance(medium_account_json,str)):
                scraped_account_data_dict = json.loads(medium_account_json)
                
                #if the scraped account does not have a description
                if(scraped_account_data_dict["description"] != ""):
                    
                    #predict the account type using the prediction function is the parameter predict_account is set to true
                    if(predict_account):
                        #call the prediction function with the description of the scraped account
                        scraped_account_data_dict["type"] = predict_medium_account("None",scraped_account_data_dict["description"])
                        scraped_account_data_dict["verified"] = "False"
                    
                    #add account data to the list of scrapped data
                    account_data_list.append(scraped_account_data_dict)
                    #add the top 5 following accounts of the scrapped account to the list of accounts to scrape
                    accounts_to_scrape_list[:0] = scraped_account_data_dict["following_top_5"]
                    #add the account id to the set of scrapped account ids
                    account_id_set.add(scraped_account_data_dict["medium"])
        
        #remove the last element of the accounts to scrape list because it has been treated
        accounts_to_scrape_list.pop() 
    
    #if the parameter store_accounts is true call the store accounts function which stores the scraped accounts either in mongo
    #or in a json file in the directory provided in the contants folder
    if(store_accounts):
        store_accounts_data(account_data_list, use_mongodb)
    
    #returns a string containing the json formatted accounts
    return json.dumps(account_data_list)


@exception_handler
def predict_medium_account(user_id: str, description: str = None) -> str:
    """
    this function opens the fitted prediction model and text count vectorizer to prepare the data of an account and return the predicted type. 
    the predicted type can either be "person" or "company".
    the function can take the user_id and scrape the user to predict or directly make a prediction based on a given description.
    if a description is provided the user id is ignored and the description is used for the prediction instead.

    Parameters
    ----------
    user_id : str
        user id of the medium account to scrape and predict.
    description : str, optional
        description of the medium account to predict.

    Returns
    -------
    str
        label of the account type. can either be "person" or "company".

    """
    #open the saved prediction model
    with open(constants.MODEL_NAME, 'rb') as file:
        prediction_model = pickle.load(file)
    #open the count vectorizer that prepares the text data
    with open(constants.VECTORIZER_NAME, 'rb') as file:
        count_vectorizer = pickle.load(file)
        
    #if no description is provided the account data will be scraped using the get_medium_page_data and the provided user_id
    if(description == None):
        json_data = get_medium_page_data(user_id)
        description_string = json.loads(json_data)["description"]
    #if a description is provided, it is directly taken for the prediction
    else:
        description_string = description
        
    #vectorize and prepare the text data contained in the description using the opened vectorizer
    vectorized_description = count_vectorizer.transform([u""+description_string])
    
    #return the predicted type of the account
    return str(prediction_model.predict(vectorized_description)[0])
    

@exception_handler
def calculate_model_scores():
    """
    this function is used to return the classification report and confusion matrix of the model we have built.

    Returns
    -------
    class_report : TYPE
        the classification report which is a string that can be printed.
    conf_matrix : TYPE
        an array that shows the confusion matrix of the model.

    """
    with open(constants.TESTING_DATA_JSON, 'r') as file:
        testing_accounts_data = json.loads(file.read())
    testing_dataframe = pd.DataFrame(testing_accounts_data)
    testing_dataframe["prediction"] = testing_dataframe["description"].map(lambda description: predict_medium_account("None",description))
    class_report = classification_report(testing_dataframe.type, testing_dataframe.prediction)
    conf_matrix = confusion_matrix(testing_dataframe.type, testing_dataframe.prediction)
    
    return class_report, conf_matrix

    
@exception_handler  
def store_accounts_data(account_data_list: list, use_mongodb: bool = False):
    """
    this function is used to store the accounts data either in mongodb or in a file and directory specified in constants.py

    Parameters
    ----------
    account_data_list : list
        the list of the accounts to store.
    use_mongodb : bool, optional
        True to use mongodb and false to store in a json file in the directory provided in constants.py. The default is False.

    Returns
    -------
    None.

    """
    if(use_mongodb):
        #connect to the mongo client, database and collection and insert or update the accounts found
        client = MongoClient(constants.MONGO_URI)
        database = client[constants.DATABASE_NAME]
        collection = database[constants.COLLECTION_NAME]
        for account in account_data_list:
            collection.update({"medium": account["medium"]}, account, upsert= True)
    else:
        #store the account list in a json file in the directory provided in constants.USER_DATA_JSON
        account_data_json = json.dumps(account_data_list, indent = 7)
        with open(constants.USER_DATA_JSON, 'a') as file:
            file.write(account_data_json)
            
            
@exception_handler  
def account_is_in_trainingdataset(user_id: str) ->bool:
    """
    function that takes the user id and returns true if the user was used in the training dataset of the model and false otherwise

    Parameters
    ----------
    user_id : str
        the user id of the account we want to check.

    Returns
    -------
    bool
        true if the user is in the training database. false in the other case.

    """
    with open(constants.TRAINING_DATA_JSON, "r") as file:
        training_data_json = json.loads(file.read())
    for account_data in training_data_json:
        if user_id == account_data["medium"]:
            return True
    return False