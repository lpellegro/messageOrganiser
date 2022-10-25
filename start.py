from credentials import credentials
import glob
from get_tokens import get_my_access_token, get_tokens
from sms import *
from flask import *
from base64Decode import base64Decode
from flow import flow, roomCreate, postMessage, textOnly
import os.path
import logging
from logging.handlers import RotatingFileHandler
from flow import plainMessage
from restApi import *

reqst = api(credentials["webexUrl"])

def setup_logger(logger_name, logfile):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    fh = RotatingFileHandler(logfile, maxBytes=5000000, backupCount=10)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

databasePath = credentials["database"]

def emailNormalization(email):
    normalization1 = email.replace(".", "_")
    normalizedEmail = normalization1.replace("@", "_")
    return normalizedEmail

def tokenFinder(normalizedEmail):
    tokenOwner = False
    tokenOwnerHead = False

    for file in glob.glob(f"{databasePath}*_token.txt"):
        if normalizedEmail in file:
            data = {}
            print(f"found email {normalizedEmail} in file {file}")
            mylogger.info(f"found email {normalizedEmail} in file {file}")
            filename = file
            with open(filename, 'r', encoding='utf-8') as local_file:
                values = local_file.read()
                print(values)
                mylogger.info(f"{local_file} has these values: {values}")
                data = json.loads(values)
                print("filename data is: ", data)
                print("filename is :", filename)
                tokenOwner = data['access_token']
                webexOwnerHeaders = headersInRequest(tokenOwner, "json")
                tokenOwnerHead = webexOwnerHeaders.full
                return tokenOwner, tokenOwnerHead
        else:
            print("ERROR: no access token for this user!")
            mylogger.info(f"no access token for {normalizedEmail}!")
            return tokenOwner, tokenOwnerHead

def dictionaryKey (dictionary, string):
    print(f"dictionary to be checked is {dictionary} against string {string}")
    mylogger.info(f"dictionary to be checked is {dictionary} against string {string}")
    key = ""
    keyExists = False
    if dictionary != {}:
        keys = list(dictionary.keys())
        values = list(dictionary.values())
        a = [sub_list for sub_list in values if string in sub_list]
        print ("a is: ", a)
        if a == []:
           keyExists = False
        else:
            item = a[0]
            index = values.index(item)
            key = keys[index]
            keyExists = True
    return key, keyExists

def mergeDictionary(dict_1, dict_2):
   dict_3 = {**dict_1, **dict_2}
   for key, value in dict_3.items():
       if key in dict_1 and key in dict_2:
               dict_3[key] = value + dict_1[key]
   return dict_3

#when a user adds the bot, then a card is sent with authentication request. When the code is posted to the script by Webex,then the script must go on with a card containing the keywords. In order to keep track of the room space, in the membership phase a file is created with the email address and the room ID. This file is checked just before sending the configuration card to the user.

mylogger=setup_logger("main","log.log")
mylogger.info("LOGGING STARTED")

urgentMessage = credentials["urgentMessage"]

webexUrl = credentials["webexUrl"]
webhookUrl = f"{webexUrl}webhooks"
webhookExists = False
botPersonId = credentials["botId"]
PAWebhook = credentials["PAWebhook"]
PAWebhookName = PAWebhook.split("//")[-1]
PAWebhookCardName = f"{PAWebhookName}/card"

#simpleHead = simpleHeaders ()
#headers = simpleHead.headers

tunnelCounter = 0
localPort = 6000

botHeaders = headersInRequest(credentials["botAccessToken"], "json")
reqst.get("webhooks", botHeaders.simple, "")
resp = reqst.response

print("webhook list in Webex subscribed by the bot", resp)
items = resp["items"]
webhookNo = len(items)
webhookEsists = False
cardTunnelExists = False
cardTunnelUrl = f"{PAWebhook}/card"

for i in range(webhookNo):
    if items[i]["targetUrl"] == PAWebhook and items[i]["createdBy"] == credentials["botPersonId"]:
        # webhook already exists
        print(f"webhook {items[i]['targetUrl']} already exists")
        mylogger.info(f"{items[i]['targetUrl']} already exists")
        webhookExists = True
    else:
        if items[i]["targetUrl"] == cardTunnelUrl and items[i]["createdBy"] == credentials["botPersonId"]:
            print(f"webhook {items[i]['targetUrl']} already exists")
            mylogger.info(f"{items[i]['targetUrl']} already exists")
            cardTunnelExists = True
        else:
            # delete this unused webhook
            webhookId = items[i]["id"]
            reqst.delete(f"webhooks/{webhookId}", botHeaders.simple, "")
            print (f"webhook {items[i]['targetUrl']} is not necessary and will be deleted")
            mylogger.info(f"webhook {items[i]['targetUrl']} is not necessary and will be deleted")

bodyjson = {"name": PAWebhookName,
            "targetUrl": PAWebhook,
            "resource": "all",
            "event": "all"
            }

if webhookExists == False:
    reqst.post("webhooks", botHeaders.full, bodyjson)
    resp = reqst.response
    print("webex tunnel creation response for the bot", resp)
    mylogger.info(f"Webex tunnel creation response for the bot: {resp}")

if cardTunnelExists == False:
    cardjson = {"name": PAWebhookCardName,
                "targetUrl": cardTunnelUrl,
                "resource": "attachmentActions",
                "event": "created"
                }
    reqst.post("webhooks", botHeaders.full, cardjson)
    resp = reqst.response
    print("bot webex webhook creation response for the card", resp)

tokenMap = {}

for file in glob.glob(f"{databasePath}*_token.txt"):
    with open(file, 'r', encoding='utf-8') as local_file:
        print("file is: ", file)
        values = local_file.read()
        print(values)
        if values != "":

            data = json.loads(values)
            print("data is:", data)
            accessToken = data["access_token"]
            tokenOwnerEmail = data ["tokenOwner"]
            tokenOwnerNormalizedEmail = emailNormalization(tokenOwnerEmail)
            userHeaders = headersInRequest(accessToken, "json")
            reqst.get("webhooks", userHeaders.simple, "")
            error = reqst.status
            print("error is: ", error)
            print(error)
            if error == 401 or error == 407:
                #expired token
                messagesRoomId = data["messagesRoomId"]
                newToken = get_my_access_token(tokenOwnerNormalizedEmail, messagesRoomId, True)
                userHeaders = headersInRequest(newToken, "json")
            else:
                resp = reqst.response
                print(f"webhook list in Webex for the user {tokenOwnerEmail}: {resp}")
                mylogger.info(f"webhook list in Webex for the user {tokenOwnerEmail}: {resp}")
                items = resp["items"]
                webhookNo = len(items)
                print("number of webhooks", webhookNo)
                webhookExists = False
                for i in range(webhookNo):

                    if str(PAWebhookName) in str(items[i]["targetUrl"]) and "allow" in str(items[i]["targetUrl"]):
                        tunnelAddress = items[i]["targetUrl"]
                        # webhook already exists
                        print(f"webhook {items[i]['targetUrl']} already exists")
                        mylogger.info(f"webhook {items[i]['targetUrl']} already exists")
                        webhookExists = True
                    else:
                        #delete this unused webhook
                        webhookId = items[i]["id"]
                        reqst.delete(f"webhooks/{webhookId}", userHeaders.simple, "")
                if webhookExists == False:
                    # create a new webhook
                    webhookNewName = f"{PAWebhookName}-{tokenOwnerNormalizedEmail}"
                    tunnelAddress = f"{PAWebhook}/allow/{tokenOwnerNormalizedEmail}"
                    bodyjson["targetUrl"] = tunnelAddress
                    bodyjson["name"] = webhookNewName
                    reqst.post("webhooks", userHeaders.full, bodyjson)
                    print (f"response for the tunnel creation for {tokenOwnerEmail} is: {reqst.response}")
                    mylogger.info(f"tunnel creation for {tokenOwnerEmail} response is: {reqst.response}")
                print("TUNNEL ADDRESS IS:", tunnelAddress)

                tokenMap[tunnelAddress] = [tokenOwnerEmail, accessToken]

print("tokenMap is:", tokenMap)
mylogger.info(f"tunnel map is: {tokenMap}")


app = Flask(__name__)

@app.route('/allow/<name>', methods=['GET', 'POST'])
#webhook created by the user
def user(name):
    #name is the owner normalized email
    print("Receive message:", request.data)
    req = request.json
    if req["data"]["personId"] != credentials["botPersonId"]:
        targetUrl = req["targetUrl"]
        filename = f"{databasePath}{name}_token.txt"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as local_file:
                values = local_file.read()
                print(values)
                data = json.loads(values)
                tokenOwnerEmail = name
                token = data["access_token"]
                print(f"message received from {tokenOwnerEmail} on hook {targetUrl}")
                mylogger.info(f"message received from {tokenOwnerEmail} on hook {targetUrl}")
                userHeaders = headersInRequest(token, "json")
                if "resource" in req:
                    resource = req["resource"]
                    if resource == "messages":
                        if req["event"] == "created":
                            personEmail = req["data"]["personEmail"]
                            normalizedPersonEmail = emailNormalization(personEmail)
                            if normalizedPersonEmail != tokenOwnerEmail: #discarded messages sent by the user himself
                                messageId = req["data"]["id"]
                                reqst.get(f"messages/{messageId}", userHeaders.simple, "")
                                message = reqst.response
                                status = reqst.status
                                if status == 401 or status == 407: #expired token
                                    get_my_access_token(name, data["messagesRoomId"], True)
                                else:
                                    print("received message is: ", message)
                                    if "text" in message.keys():
                                        messageBody = message["text"]
                                        roomId = req["data"]["roomId"]
                                        personId = req["data"]["personId"]
                                        tokenOwnerNormalizedEmail = emailNormalization(tokenOwnerEmail)
                                        print(f"You received one message from {personEmail}. It says: {messageBody}")
                                        mylogger.info(f"{name} received one message from {personEmail}")
                                        file = f"{databasePath}{tokenOwnerNormalizedEmail}_token.txt"
                                        found = False
                                        listFlag = False
                                        with open(file, 'r', encoding='utf-8') as local_file:
                                            values = local_file.read()
                                            print(values)
                                            userdata = json.loads(values)

                                            mobile = userdata["mobile"]
                                            if "rooms" in userdata.keys():
                                                if userdata["rooms"] != {}:
                                                    dictionary = userdata ["rooms"]
                                                    for item in dictionary.items():
                                                        keywordList = item[1][:-1] #as it is a tuple
                                                        for index in range(len(keywordList)):
                                                            print(f"analyzing if word {keywordList[index]} is in message '{messageBody.lower()}'")
                                                            mylogger.info(f"analyzing if word {keywordList[index]} is in received message")
                                                            stringToCheck = keywordList[index]
                                                            if isinstance(stringToCheck, list): #if it is a list
                                                               result = [w for w in stringToCheck if w in messageBody.lower()]
                                                               if result == stringToCheck:
                                                                  print(f"found {keywordList[index]}!")
                                                                  mylogger.info(f"found {keywordList[index]}!")
                                                                  found = True
                                                                  for i in range(len(stringToCheck)): #make the words in bold and preserve the original lower/uppercase
                                                                      lowerCaseWord = stringToCheck[i]
                                                                      size = len(lowerCaseWord)
                                                                      initial = messageBody.lower().find(lowerCaseWord)
                                                                      end = initial + size
                                                                      originalWord = messageBody[initial:end]
                                                                      newMessage = messageBody.replace(originalWord, f" **_{originalWord}_** ", 1)
                                                                      messageBody = newMessage
                                                            else:
                                                               if stringToCheck in messageBody.lower():
                                                                  print(f"found {keywordList[index]}!")
                                                                  size = len(stringToCheck)
                                                                  initial = messageBody.lower().find(stringToCheck)
                                                                  end = initial + size
                                                                  originalWord = messageBody[initial:end]
                                                                  newMessage = messageBody.replace(originalWord,f" **_{originalWord}_** ",1)
                                                                  messageBody = newMessage
                                                                  mylogger.info(f"found {keywordList[index]}!")
                                                                  found = True
                                                            if found == True:
                                                                roomIdPosted = item[1][-1]
                                                                link = base64Decode(roomId)
                                                                reqst.get(f"people/{personId}", userHeaders.simple, "")
                                                                if "displayName" in reqst.response.keys():
                                                                    displayName = reqst.response["displayName"]
                                                                postMessage(personEmail, displayName, newMessage, roomIdPosted, link)
                                                                if any(importantWord in messageBody.lower() for importantWord in urgentMessage):
                                                                    if "mobile" in userdata.keys() and userdata["mobile"] != "":
                                                                            smsLegacy(personEmail, messageBody, link, mobile)
                                                                break

                                                        if found == True:
                                                           break




    return Response(status=200)

@app.route('/card', methods=['GET', 'POST'])
def card():
    print("Receive CARD:", request.data)
    req = request.json
    data = req["data"]["id"]
    print("CARD DATA IS:", data)
    getUrl = f"https://webexapis.com/v1/attachment/actions/{data}"
    print(getUrl)
    reqst.get(f"attachment/actions/{data}", botHeaders.simple, "")
    response = reqst.response
    print(response)
    mylogger.info(f"card received: {response}")
    roomId = response ["roomId"]
    rooms = {}
    kw = []
    words = []
    personId = response["personId"]
    reqst.get(f"people/{personId}", botHeaders.simple, "")
    personIdResponse = reqst.response
    print(personIdResponse)
    email = personIdResponse["emails"][0]
    emailNorm = emailNormalization(email)
    messagesRoomId = "failure"
    #create room for selected messages
    token =""
    filename = f"{databasePath}{emailNorm}_token.txt"
    existingWords = []
    roomsOld = {}
    roomCreation = True
    if os.path.exists(filename):
        with open (filename, 'r', encoding='utf-8') as file:
            userdatatext = file.read()
            print(userdatatext)
            userdata = json.loads(userdatatext)
            if "words" in userdata:
                existingWords = userdata["words"]
            else:
                userdata ["words"] = []
            if "rooms" in userdata:
                roomsOld = userdata["rooms"]
            else:
                userdata["rooms"] = {}
            if "access_token" in userdata.keys():
                token = userdata["access_token"]

    keylist = [key for key in response["inputs"].keys() if key.startswith ("k") and len(key) < 4]
    oldTitle = ""
    oldTitleLower = ""
    title = ""
    titleLower = ""
    keylist.append("loopEndMarker")
    for key in keylist:
            if key == "loopEndMarker":
                if titleLower != "":
                    if roomCreation == True:
                        print(f"{oldTitle} has to be added")
                        mylogger.info(f"{oldTitle} has to be added")
                        messagesRoomId, creationResult = roomCreate(personId, oldTitle)
                        kw.append(messagesRoomId)
                    print(f"keywords to be added to {title} are: {kw}")
                    mylogger.info(f"keywords to be added to {title} are: {kw}")
                    rooms[oldTitleLower] = kw #include added keywords but room is there
                    kw = []
                    print(rooms)
            else:
                if response["inputs"][key] != "":
                    if key [-1] == "0":  #if the last part of the item is 0 or the item is the last in the list
                        title = response["inputs"][key].strip()
                        titleLower = title.lower()
                        if titleLower != oldTitleLower and oldTitleLower != "": #when the title changes or there are no more titles
                            print(f"{oldTitle} is new")
                            if roomCreation == True:
                                print(f"{oldTitle} has to be added")
                                mylogger.info(f"{oldTitle} has to be added")
                                messagesRoomId, creationResult = roomCreate(personId, oldTitle)
                                kw.append(messagesRoomId)
                                print(f"keywords to be added to {oldTitle} are: {kw}")
                                mylogger.info(f"keywords to be added to {oldTitle} are: {kw}")
                                rooms[oldTitleLower] = kw
                                oldTitleLower = titleLower
                                oldTitle = title
                                kw = []
                                messagesRoomId = "failure"
                                print(rooms)
                            else:
                                rooms[oldTitleLower] = kw
                                kw = []
                                roomCreation = True

                        if titleLower != oldTitleLower:
                            oldTitleLower = titleLower
                            oldTitle = title


                        print(title)
                        if title == "":
                           roomCreation == False
                           break
                        else:
                           if roomsOld != {} and titleLower in roomsOld.keys():
                                 roomCreation = False

                    else:  # this is a keyword
                        #check if the keyword is already used.
                        item = response["inputs"][key].strip()  # "strip" removes the leading and ending spaces
                        item = item.lower()
                        eKey = f"e{key[1:]}"
                        print(eKey)
                        listConvert = False
                        if eKey not in response["inputs"].keys():
                            #convert into a list
                            listConvert  = True

                        else:
                            if response["inputs"][eKey] == False or response["inputs"][eKey] == "false":  # Check if the sentence has to be splitted to perform teh search for non-consecutive words
                                listConvert = True
                                print(f"WE MUST CONVERT THE STRING {item} INTO A LIST")
                                mylogger.info (f"we must convert the string {item} to a list")

                        if listConvert == True:
                            if item != "":
                                wordList = item.lower().split(" ")
                                wordList.sort()
                                if len(wordList) > 1: #is a list
                                    item = wordList
                        if item != "":
                            existingSpace, keyExists = dictionaryKey(roomsOld, item)
                            if item in existingWords or item in words:
                                   print(f"item {item} exists in both '{existingSpace}' and '{title}'. '{title}' won't be created")
                                   mylogger.info(f"item {item} exists in both '{existingSpace}' and '{title}'. '{title}' won't be created")
                                   roomCreation = False
                                   oldTitleLower = existingSpace
                            else:
                                   kw.append(item)
                                   words.append(item)

    words = existingWords + words
    if "mobile" in userdata.keys():
        mobile = userdata["mobile"]
    if "mobileNo" in response["inputs"].keys():
        if response["inputs"]["mobileNo"] != "":
           mobile = response["inputs"]["mobileNo"]

    newRooms = mergeDictionary(roomsOld, rooms)
    print("new rooms are: ", newRooms)
    mylogger.info(f"new rooms to be added are: {newRooms}")
    userdata ["rooms"] = newRooms
    userdata["mobile"] = mobile
    #if messagesRoomId != "failure":
    userdata["messagesRoomId"] = roomId
    if words != []:
       userdata["words"] = words
       print("userdata is:", userdata)
    with open(filename, 'w+', encoding='utf-8') as file:
        file.write(json.dumps(userdata))
    textOnly(newRooms, roomId) #recap the filters created by the user

    if token != "":
       tunnelAddress = f"{PAWebhook}/allow/{emailNorm}"
       webhookNewName = f"{PAWebhookName}-{emailNorm}"
       if tunnelAddress not in tokenMap.keys():
           userHeaders = headersInRequest(token, "json")
           bodyjson = {"name": webhookNewName, "targetUrl": tunnelAddress, "resource": "all", "event": "all"}
           reqst.post("webhooks", userHeaders.full, bodyjson)
           response = reqst.response
           print("user webhook creation response", response)
    else:
           roomTracker = f"{databasePath}{emailNorm}_-_-_-_{roomId}.txt"
           if not os.path.exists(roomTracker):
                with open(roomTracker, 'w+', encoding='utf-8') as local_file:
                    local_file.write
           token = get_my_access_token(emailNorm, roomId, False)
    flow(roomId, mobile)  # send a card for more config
    return Response(status=200)



@app.route('/', methods=['GET', 'POST'])
def hook():
    print("Receive message:", request.data)
    mylogger.info(f"message received: {request.data}")
    #this is the get message for the OAuth flow
    if request.method == 'GET':
        if "code" in request.args:
            code = request.args.get("code")  # Captures value of the code.
            print("OAUTH CODE POSTED:", code)
            mylogger.info(f"OAuth Code Posted: {code}")
            filename, access_token = get_tokens('authorization_code', code, "roomIdNotNeeded")
            print(f"filename is {filename} and access token is {access_token}")
            with open(filename, 'r', encoding='utf-8') as local_file:
                values = local_file.read()
                print(values)
                data = json.loads(values)
                mobile = ""
                if "mobile" in data.keys():
                    if data["mobile"] != "":
                       mobile = data["mobile"]
                owner = data["tokenOwner"]

            userHeaders = headersInRequest(access_token, "json")
            tunnelAddress = f"{PAWebhook}/allow/{owner}"
            webhookNewName = f"{PAWebhookName}-{owner}"
            bodyjson = {"name": webhookNewName, "targetUrl": tunnelAddress, "resource": "all", "event": "all"}
            print("new webhook json details:", bodyjson)
            reqst.post("webhooks", userHeaders.full, bodyjson)
            tokenMap[tunnelAddress] = [owner, access_token]
            print(reqst.response)
            for file in glob.glob(f"{databasePath}{owner}_-_-_-_*.txt"):
                print(file)
                roomIdTxt = file.split("_-_-_-_")[1]
                roomId = roomIdTxt.split(".txt")[0]
            flow(roomId, mobile)
            return "Access granted, you can close this window"
    else:
        req = request.json
        print ("NON-OAUTH MESSAGE:", req)

        if "resource" in req:
            resource = req["resource"]
            if resource == "memberships":
                if req["event"] == "created" and req["createdBy"] == credentials["botPersonId"] and req["data"]["personId"] != credentials["botPersonId"]:
                    roomId = req["data"]["roomId"]
                    personEmail = req["data"]["personEmail"]
                    normalizedEmail = emailNormalization(personEmail)
                    exists = False
                    for file in glob.glob(f"{databasePath}{normalizedEmail}_-_-_-_*"):
                        if file:
                            exists = True
                    if exists == False:
                        print("New user has added the Organizer bot")
                        mylogger.info(f"new user {personEmail} has added Maggiordomo to the room list")
                        roomTracker = f"{databasePath}{normalizedEmail}_-_-_-_{roomId}.txt"
                        with open(roomTracker, 'w+', encoding='utf-8') as local_file:
                            local_file.write
                    get_my_access_token(normalizedEmail, roomId, False)
                    #note: this goes on after the OAuth code has been posted (see "if "code" in request.arg)

            else:
                    if "personId" in req["data"]:
                        personId = req["data"]["personId"]
                        if req["data"]["personId"] != credentials["botPersonId"] and "roomId" in req["data"]:
                            roomId = req["data"]["roomId"]
                            personId = req["data"]["personId"]
                            personEmail = req["data"]["personEmail"]

                            messageId = req["data"]["id"]
                            print("message ID is:", messageId)
                            print("person ID is:", personId)
                            print("person email is: ", personEmail)
                            tokenOwner = req["createdBy"]
                            reqst.get(f"messages/{messageId}", botHeaders.simple, "")
                            message = reqst.response
                            messageBody = message["text"]
                            hook = req["targetUrl"]
                            print(f"You received one message from {personEmail} on hook {hook}. It says: {messageBody}")
                            mylogger.info (f"Maggiordomo received one message from {personEmail} on hook {hook}. It says: {messageBody}")
                            normalizedEmail = emailNormalization(personEmail)
                            if "authenticate" == messageBody.lower():
                                roomTracker = f"{databasePath}{normalizedEmail}_-_-_-_{roomId}.txt"
                                if not os.path.exists(roomTracker):
                                    with open(roomTracker, 'w+', encoding='utf-8') as local_file:
                                        local_file.write
                                token = get_my_access_token(normalizedEmail, roomId, False)

                            if "configure" == messageBody.lower():
                                roomTracker = f"{databasePath}{normalizedEmail}_-_-_-_{roomId}.txt"
                                if not os.path.exists(roomTracker):
                                    with open(roomTracker, 'w+', encoding='utf-8') as local_file:
                                        local_file.write
                                filename = f"{databasePath}{normalizedEmail}_token.txt"
                                if not os.path.exists(filename):
                                   get_my_access_token(normalizedEmail, roomId, False)
                                else:
                                    with open(filename, 'r', encoding='utf-8') as local_file:
                                        values = local_file.read()
                                        print(values)
                                        data = json.loads(values)
                                        mobile = ""
                                        if "mobile" in data.keys():
                                            if data["mobile"] != "":
                                                mobile = data["mobile"]
                                    flow(roomId, mobile)

                            if "stop" == messageBody.lower():
                                roomTracker = f"{databasePath}{normalizedEmail}_-_-_-_{roomId}.txt"
                                filename = f"{databasePath}{normalizedEmail}_token.txt"
                                plainMessage(roomId, "Stopping the service...")
                                plainMessage(roomId, "Removing your data...")
                                if os.path.exists (filename):
                                    with open(filename, 'r', encoding='utf-8') as local_file:
                                        values = local_file.read()
                                        print(values)
                                        data = json.loads(values)
                                        access_token = data["access_token"]
                                        userHeaders = headersInRequest(access_token, "json")
                                        reqst.get("webhooks", userHeaders.simple, "")
                                        resp = reqst.response
                                        print(f"webhook list in Webex for the user {personEmail}: {resp}")
                                        items = resp["items"]
                                        webhookNo = len(items)
                                        print("number of webhooks", webhookNo)
                                        for i in range(webhookNo):
                                            webhookId = items[i]["id"]
                                            reqst.delete(f"webhooks/{webhookId}", userHeaders.simple, "")
                                            print(reqst.response)
                                        os.remove (filename)
                                if os.path.exists(roomTracker):
                                   os.remove(roomTracker)

                                plainMessage(roomId, "Done. \n'configure' if you want to start the service again.")

    return Response(status=200)

if __name__ == '__main__':
    app.run('0.0.0.0', port = localPort, debug=True)


