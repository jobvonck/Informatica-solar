import requests
from datetime import datetime, timedelta
import csv
from dateutil import parser

# terug leveren https://www.frankenergie.nl/saldering-bij-dynamische-contracten
def FrankEnergy():
    now = datetime.now()

    yesterday = datetime.now() + timedelta(days=-1)
    startdate = yesterday.strftime("%Y-%m-%d")
    enddate = now.strftime("%Y-%m-%d")

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

    response = []

    for item in data["data"]["marketPricesElectricity"]:
        item["from"] = parser.parse(item["from"])
        item.pop("till")
        response.append(item)

    return response


def calc_bat(vol):
    return round(vol * 75.42 - 873.4, 0)
