import urllib
import time
from datetime import datetime
from bs4 import BeautifulSoup


with urllib.request.urlopen("http://store.steampowered.com/stats/?l=english") as url:
    steampage = BeautifulSoup(url.read(), "lxml")

timestamp = time.time()
currentTime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

top100CSV = open('SteamTop100byTime.csv', 'a')

for row in steampage('tr', {'class': 'player_count_row'}):
    steamAppID = row.a.get('href').split("/")[4]
    steamGameName = row.a.get_text().encode('utf-8')
    currentConcurrent = row.find_all('span')[0].get_text()
    maxConcurrent = row.find_all('span')[1].get_text()
    
    top100CSV.write('{0},{1},"{2}","{3}","{4}"\n'.format(currentTime, steamAppID, steamGameName, currentConcurrent, maxConcurrent))

top100CSV.close()

steamOverallCSV = open('SteamOverallbyTime.csv', 'a')

for row in steampage('div', {'class': 'statsTop'}):
    steamOverallCurrentConcurrent = row.find_all('span')[0].get_text()
    steamOverallMaxConcurrent = row.find_all('span')[1].get_text()
    
    steamOverallCSV.write('{0},"{1}","{2}"\n'.format(currentTime, steamOverallCurrentConcurrent, steamOverallMaxConcurrent))
    
steamOverallCSV.close()