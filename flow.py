from credentials import credentials
from cardConfig import *
import json
import requests
from base64Decode import base64Decode
import logging
from restApi import *

webexUrl = credentials["webexUrl"]
bearer = credentials["botAccessToken"]
botWebexHeaders = headersInRequest(bearer, "json")
webexReq = api(webexUrl)

def cardPost(roomId, mobile, mobileText1, mobileText2, mobileText3):

    configCard = simplifiedCard(mobile, mobileText1, mobileText2, mobileText3)
    text = f"Use your laptop to answer to the questions"
    payload = {
        "roomId": roomId,
        "text": text,
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": configCard
            }
        ]
    }
    webexReq.post("messages", botWebexHeaders.full, payload )
    print("response for the posted card is: ", webexReq.response)

def flow(roomId, mobile):
    if mobile == "":
        mobileText1 = "Optional"
        mobileText2 = ""
        mobileText3 = "<Configure a mobile>"
    else:
        mobileText1 = "Send important messages to my mobile"
        mobileText2 = "Or use the following mobile No"
        mobileText3 = "<Alternate mobile No>"
    cardPost (roomId, mobile, mobileText1, mobileText2, mobileText3)

def roomCreate(personId, title):
    messagesRoomId = "failure"
    payload = {
        "isLocked": False,
        "isAnnouncementOnly": False,
        "title": f"___{title}"
    }
    webexReq.post("rooms", botWebexHeaders.full, payload)
    response = webexReq.response
    status = webexReq.status
    if "id" in response.keys():
        messagesRoomId = response["id"]
    #add the person
    payload = {
        "isModerator": False,
        "roomId": messagesRoomId,
        "personId": personId
    }
    webexReq.post("memberships", botWebexHeaders.full, payload)
    print("post response for roomCreate is: ", webexReq.response)

    return messagesRoomId, webexReq.response

def postMessage(personEmail, displayName, messageBody, roomId, link):
    payload = {
            "roomId": roomId,
            "markdown": f"Space: {link}\nfrom: {displayName} {personEmail}\n\n{messageBody}\n"
            }
    webexReq.post("messages", botWebexHeaders.full, payload)
    print(webexReq.response)

def textOnly (rooms, roomId):
    print("sending recap")
    for key in rooms:
        keywords = rooms[key]
        roomLink = base64Decode(rooms[key][-1])
        text = f"\n**{roomLink}**"
        for i in range(len(keywords)-1):
            text = f"{text}\n{keywords[i]}"
        text = f"{text}\n"
        payload = {
            "roomId": roomId,
            "markdown": text
        }
        webexReq.post("messages", botWebexHeaders.full, payload)
        print(webexReq.response)


def plainMessage (roomId, message):
    payload = {
            "roomId": roomId,
             "text": message
            }
    webexReq.post("messages", botWebexHeaders.full, payload)
    print(webexReq.response)

