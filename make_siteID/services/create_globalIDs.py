import json
import time
import requests
import aiohttp
import asyncio
from ..lib.utilities import loadSheet_validator, standard_ix_api_header
from ..lib.apiFunctions import (siteCategorieReader,
                                apiAuthReader,
                                api_token_generator)
                                       

def create_globalIDs(userID, excel_template):
    # Initialising login credentials to generate an api token
    credentials = apiAuthReader()
    token = api_token_generator(credentials["API_KEY"], credentials["UI_LOGIN"])


    # Initialising dataframe headings
    headings = ("Domain", "Category")

    # Validating the excel_template
    template = loadSheet_validator(excel_template, userID, headings)

    # Initialising domain names and categories to create
    siteName = template[headings[0]]
    siteTagCategoryID = template[headings[1]]

    globalID_list = batch_create_globalIDs(userID, siteName, siteTagCategoryID, token)
    siteID_list = [int(siteID['siteID']) for siteID in globalID_list if len(siteID['siteID']) == 6]

    # Submitting all globalIDs created for approval
    if siteID_list:
        try:
            approve_globalIDs(siteID_list)
        except Exception as error:
            raise error

    return globalID_list


def API_create_globalIDs(post_data):
    # Initialising login credentials to generate an api token
    userID = post_data['userID']
    credentials = apiAuthReader()
    token = api_token_generator(credentials["API_KEY"], credentials["UI_LOGIN"])

    # categories = siteCategorieReader()

    # verifying category existence in the Database

    try:
        siteTagCategoryIDs = [list(category.items())[0][1] for category in post_data['globalIDs']]

    except Exception as error:
        raise error

    siteName = [list(category.items())[0][0] for category in post_data['globalIDs']]

    globalID_list = batch_create_globalIDs(userID, siteName, siteTagCategoryIDs, token)
    siteID_list = [int(siteID['siteID']) for siteID in globalID_list if len(siteID['siteID']) == 6]

    # Submitting all globalIDs created for approval
    if siteID_list:
        try:
            approve_globalIDs(siteID_list)
        except Exception as error:
            raise error

    return globalID_list

    



# This functions takes in a list of siteIDs for approval in the Index Exchange
# UI
def approve_globalIDs(siteID_list):
    if type(siteID_list) != list:
        raise TypeError("approve_globalIDs() The siteID_list argument must by type list")

    attempts = 0
    while attempts < 10:
        response = requests.get(url="http://bartender.indexexchange.com/domain/api/sites?siteids={}".format((', '.join([str(siteID) for siteID in siteID_list]))))

        if len(response.json()) == len(siteID_list):
            print('siteIDs registered in Viper2')
            payload = {
                "siteids": siteID_list
            }

            response = requests.post(url="http://bartender.indexexchange.com/domain/api/sites/approve",
                                    json=payload)
            if response.status_code != 200:
                print("Approval API responded with status code: {}".format(response.status_code))
                raise RuntimeError("An error has occured during the approval process. The following globalIDs have been made {}".format(siteID_list))
            else:
                print(response.text)
                print("submitted the following siteIDs for approval: {}".format(siteID_list))
                break
        
        else:
            print('{} Attempt {} Failed...retrying...'.format(siteID_list, attempts))
            time.sleep(15)
            attempts += 1

    if attempts == 10:
        raise RuntimeError("Maximum registration checks reached... Please approve the following siteIDs manually {}".format(siteID_list))


def batch_create_globalIDs(userID, siteNames, siteTagCategoryIDs, token):
    """
    This function submits asynchronous batch requests the Index Exchange API
    to create global siteIDs
    """

    async def create_put_data(userID, siteNames, siteTagCategoryIDs):
        for tagName, categoryID in zip(siteNames, siteTagCategoryIDs):
            yield {
                "userID": userID,
                "name": tagName,
                "mainDomain": "http://" + tagName,
                "description": tagName,
                "siteTagCategory": categoryID,
                "autoApproval": 1,
                "rtbTransparent": 0,
                "rollupDomain": "http://" + tagName
            }

    async def put_requests():
        async with aiohttp.ClientSession(headers=standard_ix_api_header(token)) as session:
            put_tasks = []

            async for put_data in create_put_data(userID, siteNames, siteTagCategoryIDs):
                put_tasks.append(create_global_siteID(session, "https://api01.indexexchange.com/api/publishers/sites", put_data))
            
            results = await asyncio.gather(*put_tasks)
            return results



    async def create_global_siteID(session, url, put_data):
        async with session.put(url, json=put_data) as response:
            if response.status == 200:
                data = await response.json()
                print('Created GlobalID {}'.format(put_data['name']))
                return {
                    'domain': put_data['name'],
                    'siteID': str(data['data']['siteID'][0])
                }
            else:
                data = await response.json()
                print(data)
                return {
                    'domain': put_data['name'],
                    'siteID': 'Failed to Create'
                }

    
    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(put_requests())
    finally:
        loop.close()

    return results