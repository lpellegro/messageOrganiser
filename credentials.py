
credentials = {
               "botAccessToken": "<your Bot Access Token>",
               "PAWebhook": "https://example.com:5062",
               "botUsername": "<yourbot>@webex.bot",
               "botId": "<your Bot ID>",
               "botPersonId": "<bot Person Id>", #if it doesn't appear, check it through an API request (i.e. people/me)
               "webexUrl": "https://webexapis.com/v1/",
               "client_id": "<your client ID",
               "client_secret": "<your client secret>",
               "oauth_authorization_url": "<your Auth URL taken from the Integration creation web page>",
               "redirect_uri": "<matches the PAWebhook>",
               "integration_id": "<your Integration ID",
               "urgentMessage": ["urgent", "important", "critical"],
               "database": "database/", #path to the folder used to store data
               "imiKey": "<Your Imi Mobile Service Key to send SMS via Imi Mobile APIs>"
      }
