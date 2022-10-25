Using Webex app or other similar applications allow the user to receive messages on a specific space, but does not allow
the user to create key sentences to be notified when messages with those key sentences are received. Most email systems
allow to do this.

For users running Webex app, this script does the following:
1. Uses an Integration to get the access and refresh token for a user. When the user adds the bot to the buddy list, the bot responds with a card. Clicking on that card will start the OAuth flow.
   /Users/lpellegr/Downloads/authenticate.png
  
2. After authentication, another card is received by the user:
   /Users/lpellegr/Downloads/Picture_1.png
3. The user populates the card by configuring space names, and key sentences. If a message matches the corresponding key sentence, it is linked on the relative space.
4. This card can be used multiple times to configure multiple spaces with multiple key sentences
5. If a message matching key sentences also includes words such as "important", "urgent", "critical" (or other words configured in credentials.py), the system sends a SMS to the user via Imi Mobile SMS APIs.

This script requires:
1. A Webex Integration for OAuth flow
2. A Webex bot for the card management
3. An Imi Mobile account for the use of SMS APIs
4. A public reachable server, on-premises or hosted, for webhooks from Webex
