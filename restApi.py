import time
import requests
import json
from card_near import card_near
from credentials import credentials

class headersInRequest:
    def __init__(self, token, content):
        authorization = {}
        apiKey = {}
        contentType = {}
        if content == "json":
           contentType["Content-type"] = "application/json"
           self.contentType = contentType
        if content == "urlencoded":
           contentType["Content-type"] = "application/x-www-form-urlencoded"
           self.contentType = contentType
        authorization["Authorization"] = f"Bearer {token}"
        apiKey["key"] = credentials["imiKey"]
        self.full = {**authorization,**contentType}
        self.simple = authorization
        self.apiKey = {**apiKey,**contentType}


class api:
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
    def get(self, url, headers, body):
        self.response, self.status = keepOnTrying(self.baseUrl + url, "get", headers, body)
    def post(self, url, headers, body):
        self.response, self.status = keepOnTrying(self.baseUrl + url, "post", headers, body)
    def delete(self, url, headers, body):
        self.response, self.status = keepOnTrying(self.baseUrl + url, "delete", headers, body)
    def put(self, url, headers, body):
        self.response, self.status = keepOnTrying(self.baseUrl + url, "put", headers, body)



def keepOnTrying(url, method, header, body):
    if body != "":
       print(f"{header} in keepOnTrying")
       if "Content-type" in header.keys():
           if header["Content-type"] == "application/json":
               command = f"requests.{method}('{url}', headers={header}, data=json.dumps({body}))"
           if header["Content-type"] == "application/x-www-form-urlencoded":
               command = f"requests.{method}('{url}', headers={header}, data={body})"
    else:
       command = f"requests.{method}('{url}', headers={header})"
    print("body type is:", type(body))
    print(body)
    try:
        print("Full request is: ", command)
        response = eval(command)
        print(f"response for {command} is {response.text}")
        status = str(response.status_code)
        print("status is: ", status)
        tries = 1
        if status != "401" and status != "407" and status != "409" and status != "400":
            while not status.startswith("2"):
                response.close()
                newResponse = eval(command)
                status = str(newResponse.status_code)
                response = newResponse
                newResponse = ""
                time.sleep(4)
                print(f"{tries} tries for {command}")
                tries += 1
                if tries > 10:
                    exit()

        #else:
            #put your logic here in case of errors

    except requests.exceptions.RequestException as connectionError:
        print("Connection Error: ", connectionError)
        exit()
    status_code = response.status_code
    if response.text != "":
        response = response.json()
    else:
        response = {}
    #response["status_code"] = status_code
    return response, status_code