import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser
import json
import csv
from scipy import integrate

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

    response = requests.post("https://frank-graphql-prod.graphcdn.app", json=query)
    data = response.json()

    for electra in data["data"]["marketPricesElectricity"]:
        if (
            parser.parse(electra["from"])
            <= datetime.now(timezone.utc)
            <= parser.parse(electra["till"])
        ):
            totalPrice = round(
                electra["marketPrice"]
                + electra["marketPriceTax"]
                + electra["sourcingMarkupPrice"]
                + electra["energyTaxPrice"],
                4,
            )
            marketPrice = electra["marketPrice"]

    prices = []
    for i in data["data"]["marketPricesElectricity"]:
        time = parser.parse(i["from"]).replace(tzinfo=None) + timedelta(hours=2)
        time = str(time).split()[1]
        totalPrice = round(
            i["marketPrice"]
            + i["marketPriceTax"]
            + i["sourcingMarkupPrice"]
            + i["energyTaxPrice"],
            4,
        )
        marketPrice = i["marketPrice"]
        prices.append(([time, totalPrice, marketPrice]))

    return [totalPrice, marketPrice, prices]


def GetHighestPrice():
    prices = FrankEnergy()[2]
    return max(prices, key=lambda x: x[1])


def CalcBat(vol):
    battery = round(vol * 75.42 - 873.4, 0)
    if battery > 100:
        battery = 100
    elif battery < 0:
        battery = 0
    return battery


def GetWeather(stad):
    api_key = "4d8fb5b93d4af21d66a2948710284366"
    url = (
        "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s&units=metric"
        % (stad, api_key)
    )
    response = requests.get(url)
    data = json.loads(response.text)
    return data


def CheckPrice():
    response = GetHighestPrice()

    now = datetime.now()
    now = now.strftime("%H:%M:%S")
    time = datetime.strptime(response[0], "%H:%M:%S")
    now = datetime.strptime(now, "%H:%M:%S")
    if now > time and now < time + timedelta(hours=1):
        return True
    else:
        return False


def TimeToInt(dateobj):
    total = int(dateobj.strftime("%S"))
    total += int(dateobj.strftime("%M")) * 60
    total += int(dateobj.strftime("%H")) * 60 * 60
    total += (int(dateobj.strftime("%j")) - 1) * 60 * 60 * 24
    total += (int(dateobj.strftime("%Y")) - 1970) * 60 * 60 * 24 * 365
    return total


def DeleteFilecontent():
    f = open("data.csv", "w")
    f.truncate()
    f.close()


def SaveData(solar, battery):
    time = TimeToInt(datetime.now())

    with open("data.csv", mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow([time, solar, battery])


def CalculateWh():
    with open("data.csv", mode="r") as file:
        reader = csv.reader(file, delimiter=",")
        xdata = []
        ysdata = []
        ybdata = []
        for row in reader:
            xdata.append(float(row[0]))
            ysdata.append(float(row[1]))
            ybdata.append(float(row[2]))

        Solar = integrate.trapz(ysdata, xdata)
        Battery = integrate.trapz(ybdata, xdata)
    return [round(Solar / 1000, 1), round(Battery / 1000, 1)]
