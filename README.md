# mediumUserPrediction

## Description
this project was created in order to download the user data of medium.com users by starting with a single Medium user id like "BessemerVP".
After downloading the required user data the scripts can also predict whether a user is a company or a person. The main technologies used during this project are a text classification algorithm using sklearn in python3, the requests and beautifulsoup libraries to scrape the needed web pages and finally FastAPI to serve the JSON data.
## Project structure
this project is divided into 3 main parts: 
  * Web scraping and data collection
  * Prediction model
  * Serving the data
  * Exception handling and logging

The implementation of the first 2 parts can be found in mediumScraper.py, the API part is in predictionAPI.py and exception handling part in logHandling.py

### Web scraping and data collection
the first step was the creation of a data scraper that can find the data of one or multiple medium accounts by starting with a single medium id. 
This was achieved with requests and beautifulsoup in order to extract all the data from a given medium.com link. the extracted data is formatted to JSON and returned as follows:
* medium : medium id
* name : account name
* num_followers : number of followers
* following_top_5 :
  * following 1
  * following 2
  * following 3
  * following 4
  * following 5
*  all_following_link : See All following link
*  description : account description
*  links_of_description : link in description
*  type : ""

### Prediction model
The second step is opening the created prediction model and data vectorizer and applying them on the data. A function is therefore provided 
which can take a medium user id, scrape the user's page for the required data, apply the fitted text vectorizer on the scraped description,
use the vectorized description data to predict the type of the account through the model.

### Serving the data
The data can be accessed directly through the usage of the provided scraping and prediction functions. It can also be stored in Json files or a 
mongodb database. However, this part of the project facilitates these steps by providing an API which can be called to predict the label of 
one or many medium accounts at a time and display the full data in a Json response.

### Exception handling and logging
the exception handling and logging is implemented and performed a by a decorator which wraps around all the other functions in the project's structure.
the logs are saved in the LogFile in the logs folder.

## Building the prediction model
### Building the dataset
In order to create the model we downloaded 500 medium user data and manually labeled these entries by inputing a type of "person" or "company".
After this first labeling step the resulting dataset was not appropriate for the model because the amount of "person" accounts vastly outnumbered the 
"company" accounts which heavily skewed the predictor in the favor of person accounts. The final dataset used was created by combining 172 company
accounts and 338 person accounts randomly, therefore obtaining a more balanced 500 account dataset. this dataset was subdivided into a training part of
400 accounts and a testing part of 100 accounts.

### Preparing the text data
This step is a crucial one for the creation of a text classifier because the algorithms must have numerical inputs instead of textual data. The created vectorizer 
was fitted on the training dataset for future use on other data. The same vectorizer used in this step is stored in reused throughout the project whenever a prediciton is preformed.
This step transforms the textual data by removing stop words, escaping the ASCII characters and vectorizing the words into a list of numbers.
We did not use TF-IDF methods during this process because a frequency and occurence analysis resulted in a lower f1-score in the prediction model because the textual paragraphs 
provided are quite small.

### Choosing and tuning the classifier
The prediction of a binary outcome like in this case amounts to a classification problem, because we are trying to predict a label that can only take 2 values "person" and "company".
The classification algorithms that we tested are Multinomial Naive Bayes, Random Forest, SVM and finally Logistic Regression. We decided to stick with the Logistic Regression
because it provided the highest f1-score, precision and recall. This fact is due to the amount of data provided to the classifier. A logistic regression requires the least amount 
of data to obtain an accurate model compared to the other classification algorithms.

### Testing the classifier
The trained classifier was created with the use of 400 accounts in a training dataset and then tested with a subset of 100 labeled accounts. These steps include the creation of 
a classification report and confusion matrix containing the f1-score of the model which is the most pertinent metric because it is a classification problem.
the final weighted average f1-score we obtained was 92% which can be accessed by launching the calculate_model_scores function of the mediumScraper.py file.

## Scraping and Prediction
the following functions can all be called separately to perform different scraping and prediction steps
### get_medium_page_data
This function can be used in order to scrape the data from one account without performing any predictions.
Parameters:
* user_id - string: the medium id of the account to scrape

Returns:
String containing the scraped account data in a JSON format

### collect_medium_accounts
this function takes the user id to start with and the number of accounts to scrape and predict and returns and stores the data in JSON format.
Parameters:
* user_id - string: the medium id of the account to start scraping from
* number_to_collect - integer - optional: the number of accounts to return. default is 500.
* predict_account - boolean - optional: variable that defines whether to perform the prediction step or not. default is False.
* store_accounts - boolean - optional: variable that defines whether to store the accounts or not. default is False.
* use_mongodb - boolean - optional: variable that defines whether to store the accounts in mongodb or a JSON file in the data folder. default is False.

Returns:
String containing the scraped accounts data in a JSON format

### predict_medium_account
this function opens the prediction model and performs a prediction on the provided data by scraping using a provided medium id or directly with a provided description.
* user_id - string: the medium id of the account to predict
* description - str - optional: description to use for a prediction

Returns:
String prediction that can be "person" or "company"

## Using the API
Accessing the functions is made easier through the api which can be accessed with these steps:
1. open the console / powershell / cmd
2. navigate to the directory of predictionAPI.py
3. run the following commande: uvicorn predictionApi:app --reload
4. open the browser and navigate to http://127.0.0.1:8000/

a list of all available routes can be returned by accessing http://127.0.0.1:8000/routes after performing the previous steps
these routes are:
* /routes
* /checkTrainingData/{user_id}
* /predictMediumUser/{user_id}
* /predictUsersStartingWith/{user_id}/{number_of_users}

## requirements
this project uses the following libraries:
* sklearn
* bs4
* fastapi
* pymongo

## Configuration
All the configuration steps can be made by accessing the constants.py file in the scripts folder.
* USER_DATA_JSON: define the directory of the JSON file to store the new accounts scraped and predicted by collect_medium_accounts
* MONGO_URI: the connection string of the mongo client
* LOGFILE_DIR: the URL of the log file


