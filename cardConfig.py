def simplifiedCard (mobile, mobileText1, mobileText2, mobileText3):

    simplifiedCard = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2",
    "body": [
        {
            "type": "TextBlock",
            "text": "Spaces and key sentences",
            "wrap": True,
            "size": "Large",
            "weight": "Bolder"
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "307px",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Space Name",
                            "id": "k10"
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Key Sentence",
                            "id": "k11"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "90px",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Exact",
                            "value": "true",
                            "id": "e11"
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Key Sentence",
                            "id": "k12"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "90px",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Exact",
                            "value": "true",
                            "id": "e12"
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "307px",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Space Name",
                            "id": "k20"
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Key Sentence",
                            "id": "k21"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "90px",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Exact",
                            "value": "true",
                            "id": "e21"
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Key Sentence",
                            "id": "k22"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "90px",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Exact",
                            "value": "true",
                            "id": "e22"
                        }
                    ]
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": f"Send important messages to my mobile: {mobile} ",
            "wrap": True
        },
        {
            "type": "TextBlock",
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": "Or use the following mobile:",
            "wrap": True
        },
        {
            "type": "Input.Text",
            "placeholder": "<Alternate mobile No>",
            "id": "mobileNo"
        },
        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Submit"
                }
            ]
        }
    ]
}
    return simplifiedCard
