from NetworkSettings import ConnectNetwork
from env import SSID, PASSWORD
from Ticker import PriceBTC, Variation24Hrs, Variation7Day

ConnectNetwork(SSID, PASSWORD)
PriceBTC()
Variation24Hrs()
Variation7Day()
