import requests
import datetime
from datetime import datetime, timedelta
import json
from os.path import exists
import glob
from credentials import credentials
from card_near import card_near
import os.path
import logging
from restApi import *

oauth_authorization_url = credentials["oauth_authorization_url"]
databasePath = credentials ["database"]

class Storage():
    access_token = None
    at_expires_in = None
    refresh_token = None
    rt_expires_in = None
    release_date = None
    tokenOwner = None
    mobile = None
class Org():
      filename = None

baseUrl = credentials["webexUrl"]

Store = Storage()
org = Org()

def get_tokens(token_type, token, roomId):
    request = api(baseUrl)
    client_id = credentials["client_id"]
    client_secret = credentials["client_secret"]
    redirect_uri = credentials["redirect_uri"]
    payload = {
        "grant_type": token_type,
        "client_id": client_id,
        "client_secret": client_secret
    }

    if token_type == "authorization_code":
        payload["code"] = token
        payload["redirect_uri"] = redirect_uri

    if token_type == "refresh_token":
        payload["refresh_token"] = token
    print('from get_tokens this is the payload: ', payload)
    headers = headersInRequest("notUsed", "urlencoded")
    headersContentOnly = headers.contentType
    request.post("access_token", headersContentOnly, payload)
    print("response is: ", request.response)
    while request.status == 401:
        print("We got 401")
        new_request = api(baseUrl)
        new_request.post("access_token", headers, payload)
        print('from get_tokens this is the response: ', new_request.response)
        request = new_request
        #add a break condition in case of infinite loop

    if request.status == 400 and token_type == "refresh_token":
        # This is the error received if the refresh token is expired
        start(roomId)
    else:
        response = request.response
        print('from get_tokens this is the response: ', response)
        now = datetime.now()
        access_token = response['access_token']
        at_exp = response['expires_in']
        #calculate the date and time of expiration based on the delta time expressed in seconds
        at_expiration = now + timedelta(0, at_exp)
        refresh_token = response['refresh_token']
        rt_exp = response['refresh_token_expires_in']
        #calculate the date and time of expiration based on the delta time expressed in seconds
        rt_expiration = now + timedelta(0, rt_exp)
        Store.access_token = access_token
        Store.refresh_token = refresh_token
        Store.at_expires_in = str(at_expiration) #expiration in time and date
        Store.rt_expires_in = str(rt_expiration)
        Store.at_exp = at_exp #expiration in seconds
        Store.rt_exp = rt_exp
        Store.at_release_date = str(datetime.now())
        userHeaders = headersInRequest(access_token, "")
        request.get("people/me", userHeaders.simple, "")
        response = request.response
        print("people/me response is: ", response)
        emailAddress = response ["emails"][0]
        normalization1 = emailAddress.replace(".", "_")
        tokenOwner = normalization1.replace("@", "_") #tokenOwner matches the email address without . and @
        Store.tokenOwner = tokenOwner
        Store.mobile = ""
        if token_type == "authorization_code":
            if "phoneNumbers" in response.keys():
                phoneNumbers = response["phoneNumbers"]
                l = len(phoneNumbers)
                for i in range(l):
                    if phoneNumbers[i]["type"] == "mobile":
                        mobile = phoneNumbers[i]["value"]
                        mobileNospaces = mobile.replace(" ", "")
                        Store.mobile = mobileNospaces
        print("MOBILE NUMBER IS:", Store.mobile)
        token_details = vars(Store)
        print(f"token details are {token_details} and type is {type(token_details)}")
        expiry_date = token_details['at_expires_in']
        print(f"expiry date for access token is {expiry_date} and variable type is {type(expiry_date)}")
        filename = write_file(token_details) #, friendly_name)
        return filename, access_token

def get_my_access_token(normalizedEmail, roomId, expired):
    data = read_file(normalizedEmail)
    if data != {}:
       at_expires_in = data['at_expires_in']
       rt_expires_in = data['rt_expires_in']
       print(at_expires_in, type(at_expires_in))
       at_expiry_time = datetime.fromisoformat(at_expires_in)
       rt_expiry_time = datetime.fromisoformat(rt_expires_in)
       now = datetime.now()
       access_token = data['access_token']
       if at_expiry_time > now and expired == False:
          bearer = access_token
          print(bearer)
       else:
          print('outdated access token is: ', access_token)
          if rt_expiry_time > now:
             refresh_token = data['refresh_token']
             get_tokens("refresh_token", refresh_token, roomId)
          else:
             start(roomId)
       new_data = read_file(org.filename)
       access_token = new_data['access_token']
       return access_token
    else:
        start(roomId)

def read_file (normalizedEmail):
    print ("normalizedEmail is:", normalizedEmail)
    filename = ""
    for file in glob.glob(f"{databasePath}*_token.txt"):
        if normalizedEmail in file:
           print(f"found email {normalizedEmail} in file {file}")
           filename = file
    data = {}
    if filename != None and filename != "" and exists(filename) == True:
          with open (filename, 'r', encoding='utf-8') as local_file:
              values = local_file.read()
              print(values)
              data = json.loads(values)
              org.filename = filename
    print("filename data is: ", data)
    print("filename is :", filename)
    return data

def write_file (token_details):

    tokenOwner = Store.tokenOwner
    filename = f"{databasePath}{tokenOwner}_token.txt"

    org.filename = filename
    data = token_details
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as local_file:
            values = local_file.read()
            print(values)
            if values != "":
                data = json.loads(values)
                if "mobile" in data.keys(): #if the mobile number in the file is different from the mobile number retrieved after receiving the access token, then it means that the mobile number has been changed by the user. We want to keep this.
                   if data ["mobile"] != token_details["mobile"]:
                      token_details["mobile"] = data["mobile"]

                data.update(token_details)

    with open (filename, 'w+', encoding='utf-8') as local_file:
        local_file.write(json.dumps(data))
    return filename

def start(roomId):
    request = api(credentials["webexUrl"])
    bearer = credentials["botAccessToken"]
    headers = headersInRequest(bearer, "json")
    authCard = card_near()
    print(authCard)
    text = f"Please authenticate\n{oauth_authorization_url}"
    payload = {
        "roomId": str(roomId),
        "text": text,
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": authCard
            }
        ]
    }
    request.post("messages", headers.full, payload)
    print("CARD POST RESPONSE: ", request.response)

if __name__ == '__main__':
    get_my_access_token()



