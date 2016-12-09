import urllib
import time
from datetime import datetime
from bs4 import BeautifulSoup


with urllib.request.urlopen("http://store.steampowered.com/search/?tags=21978&vrsupport=401") as url:
    steampage = BeautifulSoup(url.read(), "lxml")

html = steampage.prettify("utf-8")
with open("AllVRApps.html", "wb") as file:
    file.write(html)
      
timestamp = time.time()
currentTime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

fileCSV = open('SteamTop100byTime.csv', 'w')

fileCSV.write('{0},{1},{2}\n'.format('Time Recorded', 'Steam App ID', 'Game Name'))

for row in steampage('a', {'class': 'search_result_row'}):
    steamAppID = row.get('data-ds-appid')
    steamGameName = row.find_all('span')[0].get_text().replace('\u2122','')
    print('{0},{1},"{2}"\n'.format(currentTime, steamAppID, steamGameName))
    #price = row.find_all('span')[1].get_text()
    fileCSV.write('{0},{1},{2}\n'.format(currentTime, steamAppID, steamGameName))

fileCSV.close()