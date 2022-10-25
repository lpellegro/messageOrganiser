
import requests
import json
import logging
from restApi import *

#hostlogger = logging.getLogger('main.whatsapp')

def sms(messageFrom, messageBody, messageTo, link, bearer, fromField):
  print(messageBody)
  print("SIAMO IN SMS-SSETE")
  url = "https://api-sandbox.imiconnect.io/v1/sms/messages"
  payload = json.dumps({
    "contentType": "text",
    "content": f"from: {messageFrom}\n{messageBody}\ncheck this link: {link}",
    "from": fromField,
    "to": messageTo,
  })

  headers = {
    'Authorization': bearer, 
    'Content-Type': 'application/json',

  }

  response = requests.request("POST", url, headers=headers, data=payload)
  print(messageTo)
  print(type(messageTo))
  print(response.text)
  #hostlogger.info(f"sms response is {response.text}")

def whatsappete(messageFrom, messageBody, to, link, bearer, fromField):
  print(messageBody)
  print("SIAMO IN WHATSAPPETE")
  url = "https://api-sandbox.imiconnect.io/v1/whatsapp/messages"
  payload = json.dumps({
    "contentType": "text",
    "content": f"from: {messageFrom}\n{messageBody}\ncheck this link: {link}",
    "from": fromField, 
    "to": to,
  })
  headers = {
    'Authorization': bearer,
    'Content-Type': 'application/json',

  }

  response = requests.request("POST", url, headers=headers, data=payload)
  #hostlogger.info(f"whatsapp response is {response.text}")
  print(to)
  print(type(to))
  print(response.text)


def smsLegacy(messageFrom, messageBody, link, to):
  baseUrl = "https://api.us.webexconnect.io/resources/v1/"
  imiHeaders = headersInRequest("notUsed", "json")
  payload = {
    "deliverychannel": "sms",
    "channels": {
      "sms": {
        "text": f"from: {messageFrom}\n{messageBody}\ncheck this link: {link}",
        "senderid": "CONNCT"
      }
    },
    "destination": [
      {
        "msisdn": [
          to
        ]
      }
    ]
  }
  #headers = {
    #'Content-type': 'application/json',
    #'key': '6d41c47e-3f10-11ed-9e4c-02b6c62f50eb' #'6d41c47e-3f10-11ed-9e4c-02b6c62f50eb'
 # }

  print("SENDING SMS TO: ", to)
  imiRequest = api(baseUrl)
  imiRequest.post ("messaging", imiHeaders.apiKey, payload)
  response = imiRequest.response
  print("Response for the SMS is: ", response)

  #response = requests.request("POST", baseUrl, headers=headers, data=payload)

  #print(response.text)

#smstest("Luca Pellegrini", "Need to test SMS with an US mobile, ciao!", "+19016322594")

#sms("test", "test", "+393357561685", "link", "ae2b87ba-a6c1-11ec-b58d-063d0d6fdfb5", "+393399950808")
#whatsappete("test", "test", "+393357561685", "link", "ae2b87ba-a6c1-11ec-b58d-063d0d6fdfb5","a_163115952236765903")

