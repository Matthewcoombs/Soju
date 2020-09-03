import requests
import json
import pandas as pd
import time
import datetime


#GENERATING THE API TOKEN as a token variable for general use.
def api_token_generator(key, userName):
    headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-cache" 
    }

    payload = {
        "username": userName,
        "key": key
    }

    resp = requests.post(url = "https://auth.indexexchange.com/auth/oauth/token", data = json.dumps(payload), headers = headers)
    json_data = json.loads(resp.text)

    if json_data['responseCode'] != 200:
        print('\nTHE API KEY ENTERED IS INCORRECT')
        print('PLEASE CHECK THE API KEY CURRENTLY SET FOR ACCOUNT.OPERATIONS...\n')
    
    else:
        token = json_data['data']['accessToken']
        return token


#Gathering general siteID information
def siteId_info(token, siteId, pubId):

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer " + token
    }

    payload = {
        "userID": pubId,
        "siteID": [siteId]
    }

    response = requests.post(url="https://api01.indexexchange.com/api/publishers/sites", data=json.dumps(payload), headers=headers)
    json_data = json.loads(response.text)
    return json_data['data']


#This functions reads the auth credentials from the credentials json file
def apiAuthReader():
    with open('config/auth_credential.json', 'r') as files:
        credentials = json.load(files)
    
    return credentials


#This functions returns a list of all siteID objects for a given userID
def getAllSiteIDs(userID, token):
    headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Bearer " + token
    }

    payload = {
    "userID": userID
    }

    response = requests.post(url = "https://api01.indexexchange.com/api/publishers/sites", data = json.dumps(payload), headers = headers)
    data = response.json()
    return data['data']


#This functions reads the siteCategories json file
def siteCategorieReader():
    with open('config/siteCategories.json', 'r') as files:
        categories = json.load(files)
    
    return categories
