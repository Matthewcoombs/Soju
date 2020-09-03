import requests
from ..lib.utilities import validate_crawl_sheet
from bs4 import BeautifulSoup

def crawl_domains(excel_template):
    template = validate_crawl_sheet(excel_template)
    siteName = template['Domain']
    meta_data_list = []

    print(siteName)

    # This block will go to each domain submitted and read the websites DOM to extract 
    # the <meta> data description tag of the site
    for domain in siteName:
        try:
            crawl_domain = 'http://www.' + domain
            response = requests.get(crawl_domain)
            text = response.text
            soup = BeautifulSoup(text, features= 'lxml')

            metas = soup.find_all('meta')
            meta_data = [ meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
            
            # This block will record and display the typical error encountered when a domain submitted
            # DOES NOT follow the "domain.com" naming convention
        except:
            data = {
                'domain': domain,
                'description': 'Cannot Reach Site'
                }
            meta_data_list.append(data)
            continue

        # If no description can be pulled from the site
        if len(meta_data) < 1:
            data = {
                'domain': domain,
                'description': 'No Description'
                }
            meta_data_list.append(data)
        # Appending the website description into the meta_data_list list
        else:
            data = {
                'domain': domain,
                'description': meta_data[0]
                }
            meta_data_list.append(data)

    return meta_data_list
