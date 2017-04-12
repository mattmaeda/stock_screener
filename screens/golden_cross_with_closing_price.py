SCREEN = {
    "name": "Golden Cross Plus",
    "description": "50 Day Moving Average Cross Over 100 Day Moving Average and Closing Price above 50 Day Moving Average",
    "conditions": [
        "MA50 XOVER MA100",
        "MA50 LT MA200",
        "MA100 LT MA200",
        "MA50 LT CP",
        "MA100 LT CP"
    ],
    "criteria": [
        "50 Day Moving Average Crosses Over 100 Day Moving Average",
        "50 Day Moving Average Below 200 Day Moving Average",
        "100 Day Moving Average Below 200 Day Moving Average",
        "50 Day Moving Average Below Closing Price",
        "100 Day Moving Average Below Closing Price"
    ]
}
