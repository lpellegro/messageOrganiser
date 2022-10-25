
import requests
import json
import logging
from restApi import *

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

  print("SENDING SMS TO: ", to)
  imiRequest = api(baseUrl)
  imiRequest.post ("messaging", imiHeaders.apiKey, payload)
  response = imiRequest.response
  print("Response for the SMS is: ", response)


