from credentials import credentials

oauthUrl = credentials["oauth_authorization_url"]

def card_near ():


        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.2",
            "body": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "300px",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Please Authenticate",
                                    "wrap": True,
                                    "size": "ExtraLarge",
                                    "fontType": "Monospace"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": "",
                                    "wrap": True,
                                    "size": "ExtraLarge",
                                    "fontType": "Monospace"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "ImageSet",
                                    "images": [
                                        {
                                            "type": "Image",
                                            "size": "Large",
                                            "url": "https://www.cisco.com/c/en/us/products/conferencing/webex/jcr:content/Grid/category_atl_6b9a/layout-category-atl/blade/bladeContents3/tile/image.img.png/1590697890585.png"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "",
                    "wrap": True,
                    "separator": True,
                    "size": "Small",
                    "fontType": "Monospace"
                },
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "ActionSet",
                                    "horizontalAlignment": "Center",
                                    "actions": [
                                        {
                                            "type": "Action.OpenUrl",
                                            "title": "Authenticate",
                                            "url": oauthUrl
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        return card
