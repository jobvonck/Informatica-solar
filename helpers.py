import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser
import json

# terug leveren https://www.frankenergie.nl/saldering-bij-dynamische-contracten
def FrankEnergy():
    now = datetime.now()

    startdate = now.strftime("%Y-%m-%d")
    enddate = datetime.now() + timedelta(days=+1)
    enddate = enddate.strftime("%Y-%m-%d")
 
    if int(now.strftime("%H")) > 15:
        tomorrow = datetime.now() + timedelta(days=2)
        startdate = now.strftime("%Y-%m-%d")
        enddate = tomorrow.strftime("%Y-%m-%d")
    headers = {"content-type": "application/json"}

    query = {
        "query": """
                    query MarketPrices($startDate: Date!, $endDate: Date!) {
                        marketPricesElectricity(startDate: $startDate, endDate: $endDate) {
                            from till marketPrice marketPriceTax sourcingMarkupPrice energyTaxPrice
                        }
                        marketPricesGas(startDate: $startDate, endDate: $endDate) {
                            from till marketPrice marketPriceTax sourcingMarkupPrice energyTaxPrice
                        }
                    }
                """,
        "variables": {"startDate": str(startdate), "endDate": str(enddate)},
        "operationName": "MarketPrices",
    }

    response = requests.post("https://frank-graphql-prod.graphcdn.app/", json=query)
    data = response.json()

    response = requests.post('https://frank-graphql-prod.graphcdn.app', json=query)
    data = response.json()
 
    for electra in data['data']['marketPricesElectricity']:
        #print(round(electra["marketPrice"] + electra["marketPriceTax"] + electra["sourcingMarkupPrice"] + electra["energyTaxPrice"],4))
        #print(electra["marketPrice"])
        #print(electra)
        if parser.parse(electra["from"]) <= datetime.now(timezone.utc) <= parser.parse(electra["till"]):
            totalPrice = round(electra["marketPrice"] + electra["marketPriceTax"] + electra["sourcingMarkupPrice"] + electra["energyTaxPrice"],4)
            marketPrice = electra["marketPrice"]
            return [totalPrice,marketPrice]


def CalcBat(vol):
    battery = round(vol * 75.42 - 873.4, 0)
    if battery >100:
        battery = 100
    elif battery < 0:
        battery = 0
    return battery

def GetWeather(stad):
    api_key = "4d8fb5b93d4af21d66a2948710284366"
    url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s&units=metric" % (stad, api_key)
    response = requests.get(url)
    data = json.loads(response.text)
    return data
