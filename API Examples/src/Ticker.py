import urequests as requests
from env import URL_BASE

def TickerBTC():
    response = requests.get(URL_BASE)
    data = response.json()
    response.close()
    
    return {
        'last_price': data['ticker']['last_price'][0],
        'price_variation_24h': data['ticker']['price_variation_24h'],
        'price_variation_7d': data['ticker']['price_variation_7d'],
    }

def PriceBTC():
    print('Consultando precio del BTC en CLP')
    data = TickerBTC()
    print(f"El último precio del BTC en CLP es: {data['last_price']}\n")

def Variation24Hrs():
    print('Consultando variación en las ultimas 24Hrs del BTC en CLP')
    data = TickerBTC()
    print(f"La variación en las últimas 24 horas del BTC en CLP es: {data['price_variation_24h']}\n")

def Variation7Day():
    print('Consultando variación en los ultimos 7 días del BTC en CLP')
    data = TickerBTC()
    print(f"La variación en los últimos 7 días del BTC en CLP es: {data['price_variation_7d']}\n")