import requests
import itertools
import json
from .forms import UserIDForm
from django.http import JsonResponse
from make_siteID.lib.apiFunctions import (api_token_generator,
                                          apiAuthReader,
                                          siteCategorieReader)
from .services import create_globalIDs, crawl_domains
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def home_page(request):
    if "GET" == request.method:
        form = UserIDForm
        return render(request, 'make_siteID/home.html', {'form': form})
        # return render(request, userID, 'make_siteID/make_siteID.html')

    if "POST" == request.method:
        data_dict = request.POST
        userID = data_dict['userID']

        #If the userID submitted does not exist OR account.operations DOES NOT 
        #have access, the user will be redirected back to the homepage
        credentials = apiAuthReader()
        token = api_token_generator(credentials['API_KEY'], credentials['UI_LOGIN'])
        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + token}
        response = requests.get(url = 'https://api01.indexexchange.com/api/users/profile?userID=' + str(userID), headers = headers).json()
        if response['responseCode'] != 200:
            form = UserIDForm
            error = {'description': 'The publisher Account (' + userID + ') does not Exist, OR account.operations does not have access to the account'}
            # context = {"error": error}
            return render(request, 'make_siteID/home.html', {'form': form, 'error':error})
        else:
            return HttpResponseRedirect(reverse('create-global',args=[userID]))


def globalID_template(request):
    with open('config/domainSubmissionList.xlsx', 'rb') as files:
        response = HttpResponse(files.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename=globalIDTemplate.xlsx'
        return response


def create_global_siteID(request,userID):
    credentials = apiAuthReader()
    token = api_token_generator(credentials['API_KEY'], credentials['UI_LOGIN'])
    headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + token}
    response = requests.get(url = 'https://api01.indexexchange.com/api/users/profile?userID=' + str(userID), headers = headers).json()
    if response['responseCode'] == 200:
        publisher_data = {'publisherEmail': response['data']['emailAddress'], 'companyName': response['data']['companyName']}
    

    if "GET" == request.method:
        #If the userID submitted does not exist OR account.operations DOES NOT 
        #have access, the user will be redirected back to the homepage
        if response['responseCode'] != 200:
            return HttpResponseRedirect(reverse('home'))
        else:
            publisher_data = {'publisherEmail': response['data']['emailAddress'], 'companyName': response['data']['companyName'], 'userID': userID}
            return render(request, 'make_siteID/make_siteID.html', {'publisher_data': publisher_data})

    elif "POST" == request.method:

        data_dict = request.FILES
        if 'excel_crawl_data' in data_dict:
            excel_data = data_dict['excel_crawl_data']

            try:
                meta_data_list = crawl_domains.crawl_domains(excel_data)
                return JsonResponse({"meta_data_list": meta_data_list})

            except Exception as err:
                return JsonResponse({"error": str(err)})
        
        #This block will execute if the request was to create Global IDs
        elif 'excel_create_data' in data_dict:
            excel_data = data_dict['excel_create_data']

            try:
                globalID_list = create_globalIDs.create_globalIDs(int(userID), excel_data)
                return JsonResponse({"creation_list": globalID_list})

            except Exception as err:
                return JsonResponse({'error': str(err)})
        else:
            return JsonResponse({'publisher_data': publisher_data})


@csrf_exempt
def API_create_globalIDs(request):
    
    if "POST" != request.method:
        return HttpResponse(status=405)
    
    try:
        body = json.loads(request.body)
        keys_to_check = {'userID': int, 'globalIDs': list}

        for key in keys_to_check:
            if key not in body:
                return JsonResponse({'ERROR': 'The request is missing the paramater "{}"'.format(key)}, safe=False)
            if not isinstance(body[key], keys_to_check[key]):
                return JsonResponse({'ERROR': 'The request paramater "{}" is an INVALID TYPE'.format(key)}, safe=False)


        globalID_list = create_globalIDs.API_create_globalIDs(body)
        return JsonResponse({'success': globalID_list}, safe=False)

    except Exception as error:
        return JsonResponse({'ERROR': str(error)})


@csrf_exempt
def API_get_categoryIDs(request):
    
    if "GET" != request.method:
        return HttpResponse(status=405)
    
    try:
        categories_json = siteCategorieReader()
        return JsonResponse({'success': categories_json}, safe=False)

    except Exception as error:
        return JsonResponse({'ERROR': str(error)})
