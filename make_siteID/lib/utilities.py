from .apiFunctions import (getAllSiteIDs, 
                           api_token_generator,
                           apiAuthReader,
                           siteCategorieReader)
import pandas as pd

def loadSheet_validator(excel_template, userID, headings):
    if type(userID) != int:
        raise TypeError("loadSheet_Validator(): The userID argument must be type int")
    if type(headings) != tuple:
        raise TypeError("loadSheet_validator(): The headings argument must be type tuple")

    domain_head = headings[0]
    category_head = headings[1]

    credentials = apiAuthReader()
    token = api_token_generator(credentials["API_KEY"], credentials["UI_LOGIN"])
    # initialising the template dataframe
    template = pd.read_excel(excel_template)

    # Checking the excel template headers to ensure the proper columns exist
    try:
        for header in headings:
            template[header]
    except:
        raise KeyError("The template is missing a '{}' column. Enter this column manually or download a fresh template.".format(header))

    # initialising all category entrees
    categories = template[category_head]
    # Initialising domain submissions
    domains = template[domain_head]
    if len(domains) > 100:
        raise RuntimeError("Domain list is OVER 100. Please break the list down into groups of 100")

    # Ensuring each domain has an accompanying category
    for index, domain in enumerate(domains.dropna()):
        if type(categories[index]) == float:
            raise RuntimeError("The domain '{}' on line {} is missing a category. Please enter a category and try again".format(domain, index + 2))


    # reinitialising template with Nan values stripped from domain and category columns
    template = template.dropna(subset=[domain_head, category_head])
    # reinitialising domains and categories after stripping Nan entrees
    domains = template[domain_head]
    categories = template[category_head]


    # Checking for duplicate values on the sheet
    for index, duplicate_check in enumerate(domains.duplicated()):
        if duplicate_check == True:
            raise RuntimeError('Domain Name: "{}" on line {} is a duplicate entry'.format(domains[index], index + 2))


    # storing all siteID names into a set for duplicate checks in the system
    siteIDs = getAllSiteIDs(userID,token)
    siteID_mainDomains = set([siteID['mainDomain'].lower() for siteID in siteIDs])
    

    # Checking domains for duplicates
    for index, domain in enumerate(domains):
        if "http://" + domain.lower() in siteID_mainDomains:
            domains.update({index: "NOTICE: [{}] already Exists".format(domain)})


    # Validating the category entrees to ensure they exist in the UI
    ui_categories = siteCategorieReader()
    for index, cat in enumerate(categories):
        try:
            categories.update({index: ui_categories[cat]})

            # cat = ui_categories[cat]
        except Exception as error:
            raise KeyError("The Category '{}' on line {} does NOT exist in the UI".format(cat, index + 2))


    # Returning the dataframe upon succesful validation
    return template


# This is a custom loadhsheet validator designed for the domain crawling service
def validate_crawl_sheet(excel_template):
    domain_heading = "Domain"
    template = pd.read_excel(excel_template)
    # Ensuring the "Domain" column exists in the dataframe
    try:
        template[domain_heading]
    except:
        raise KeyError("The excel file is missing a '{}' column. Please insert this manually or download a new template".format(domain_heading))

    template = template.dropna(subset=[domain_heading])

    domains = template[domain_heading]

    # Checking for duplicate values in Domain column
    for index, duplicate_check in enumerate(domains.duplicated()):
        if duplicate_check == True:
            raise RuntimeError('Domain Name: "{}" on line {} is a duplicate entry'.format(domains[index], index + 2))
    
    return template

def standard_ix_api_header(token):
    """
    This is the standard header used in the majority of Index API Requests
    """

    headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer {}".format(token)
        }

    return headers
