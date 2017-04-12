SCREEN = {
    "name": "Death Cross Plus",
    "description": "50 Day Moving Average Cross Under 100 Day Moving Average and Closing Price above 50 Day Moving Average",
    "conditions": [
        "MA50 XUNDER MA100",
        "MA50 GT MA200",
        "MA100 GT MA200",
        "MA50 GT CP",
        "MA100 GT CP"
    ],
    "criteria": [
        "50 Day Moving Average Crosses Under 100 Day Moving Average",
        "50 Day Moving Average Above 200 Day Moving Average",
        "100 Day Moving Average Above 200 Day Moving Average",
        "50 Day Moving Average Above Closing Price",
        "100 Day Moving Average Above Closing Price"
    ]
}
