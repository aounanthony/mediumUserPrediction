import json, typing
from fastapi import FastAPI
from mediumScraper import predict_medium_account
from mediumScraper import collect_medium_accounts
from mediumScraper import get_medium_page_data
from mediumScraper import account_is_in_trainingdataset
from starlette.responses import Response

app = FastAPI()

class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=8,
            separators=(", ", ": "),
        ).encode("utf-8")


@app.get("/")
def home():
    """

    Returns
    -------
    PrettyJSONResponse
        returns a json containing the message of the api's default route.

    """
    return PrettyJSONResponse({"message":"Welcome to the medium prediction api go to /routes to check the available options"})


@app.get("/routes")
def get_routes():
    """

    Returns
    -------
    PrettyJSONResponse
        returns a Json containing the available routes of the api.

    """
    return PrettyJSONResponse({"/predictMediumUser/quartz?with_data=True": "predict 1 user using user id like BessemerVP and an optional parameter with_data set by default to True to display data or False for the prediction only",
                               "/predictUsersStartingWith/{user_id}/{number_of_users}": "predict multiple users that are not part of the training dataset starting with user_id like BessemerVP and a number_of_users like 5",
                               "/checkTrainingData/{user_id}": "check if account with user_id is in the model training dataset"})


@app.get("/checkTrainingData/{user_id}")
def account_is_in_training_set(user_id: str):
    """
    function that takes in the user id and returns whether the account was used in the training dataset or not

    Parameters
    ----------
    user_id : str
        user id of the account.

    Returns
    -------
    PrettyJSONResponse
        Json containing the medium id and a boolean true or false that defines if the user is part of the tranining dataset.

    """
    return PrettyJSONResponse({"medium": user_id, "is_in_training_dataset": account_is_in_trainingdataset(user_id)})


@app.get("/predictMediumUser/{user_id}")
def predict_user(user_id: str, with_data: bool = True):
    """
    function that predicts if the user is a person or a company and can return all the scraped account data of the given medium user

    Parameters
    ----------
    user_id : str
        medium user id to scrape and predict.
    with_data : bool, optional
        true to return all the scraped data of the medium user, false to return the prediction only. The default is True.

    Returns
    -------
    PrettyJSONResponse
        Json of the prediction the medium user id and optionally the scraped data.

    """
    if(with_data):
        print(get_medium_page_data(user_id))
        user_data_dict = json.loads(get_medium_page_data(user_id))
        user_data_dict["type"] = predict_medium_account("None", user_data_dict["description"])
        return PrettyJSONResponse(user_data_dict)
    else:
        return PrettyJSONResponse({"medium": user_id, "type": predict_medium_account(user_id)})

@app.get("/predictUsersStartingWith/{user_id}/{number_of_users}")
def predict_multiple_users(user_id: str, number_of_users: int):
    """
    function that returns the prediction and scraped data of multiple medium users 
    starting with a provided medium user id and searching for a number of users provided in the parameters

    Parameters
    ----------
    user_id : str
        medium user id to start scraping data and predict with.
    number_of_users : int
        number of user to be returned.

    Returns
    -------
    PrettyJSONResponse
        Json containing the scraped medium accounts and the predictions.

    """
    return PrettyJSONResponse(json.loads(collect_medium_accounts(user_id, number_of_users, True)))