# Setup:
To run this locally, please install all necessary requirements found in the
"requirements.txt" file. 

1. it is recommended that you first create a virtual environment.
2. Inside of your virtualenv enter `pip install -r requirements.txt`

# Enable API Functions from make_siteID/lib/apiFunctions.py
To establish a connection with the Index Exchange API you need to provide
authorization credentials. Create a `auth_credential.json` file inside of the
`config` folder and provide the following key-value pairs:

1. `API_KEY` - The Index user API key
2. `UI_LOGIN` - The Index user email login

# Starting Server
Enter in your commmand line or terminal:
Local hosting:
`python manage.py runserver --settings=globalID_creator.settings.local`
Bartender hosting:
`python manage.py runserver 6606 --settings=globalID_creator.settings.production`

# Stop Server
`CTRL-C`

# What does the application do
1. The application will navigate the user to a front page with a `userID` submission form.
The 6 digit ID corresponds to the Index app-account ID.

2. If the account exists they will be navigated to the primary page with
fields propageted with details from the associated app-account

3. If the user would like a general description for a list of websites, they can submit a list
of domains on an excel sheet under a `Domain` column. The application will go to each respective
website to read and return the <meta> tag `description` of the site to the user.
 
4. With a list of domains and categories known (through the assistance of the site crawl) the user
can submit these domains with categories for creation as data points in the publishers app-account.

# NOTE
-The application will read only excel files
