import requests
from datetime import datetime, timedelta, timezone
import csv
from dateutil import parser

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
    return round(vol * 75.42 - 873.4, 0)
