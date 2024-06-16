from NetworkSettings import ConnectNetwork
from BinanceTest import TestConnectivity as Ping
from env import SSID, PASSWORD

ConnectNetwork(SSID, PASSWORD)
Ping()
