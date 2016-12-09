import urllib
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Store URL
storeURL = "http://store.steampowered.com/search/?tags=21978&vrsupport=401"

# File handle
fileCSV = open('SteamVR-Data.csv', 'w')

# Get current time stamp
timestamp = time.time()
currentTime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Get the current VR game steam page
with urllib.request.urlopen(storeURL) as url:
    steampage = BeautifulSoup(url.read(), "lxml")

# Find total number of games
gameNumStr = steampage("div",{"class" : "search_pagination_left"})[0].text
num = [int(s) for s in gameNumStr.split() if s.isdigit()]
totalGames = num[2]

# Find total number of pages
pageNumStr = steampage("div",{"class" : "search_pagination_right"})[0].text
num = [int(s) for s in pageNumStr.split() if s.isdigit()]
totalPages = num[-1]

# Record the overall data
fileCSV.write('{0},{1},{2}\n'.format('Time Recorded', 'Total Apps', 'Store Entry Used'))
fileCSV.write('{0},{1},{2}\n\n'.format(currentTime, totalGames, storeURL))
 
# Record the headings of data section     
fileCSV.write('{0},{1},{2},{3},{4},{5}\n'.format('Steam App ID', 'Game Name', 'Price', 'Release Date', 'Review Percentage', 'Review Count'))

''' 
This section scrapes data from Steam Store webpage
'''
# Assemble a complete list of URLs to scrape
steamUrlList = []
for i in range(totalPages):
    steamUrlList.append(storeURL+"&page={0}".format(i+1))

for idx, url in enumerate(steamUrlList):
    print('Scraping page {0} / {1}'.format(idx+1, totalPages))
    print('URL: {0}'.format(url))
    
    with urllib.request.urlopen(url) as urlObj:
        steampage = BeautifulSoup(urlObj.read(), "lxml")
        
        appStr = steampage('a', {'class': 'search_result_row'})
        gameNameStr = steampage('span', {'class': 'title'})
        releaseDateStr = steampage('div', {'class': "col search_released responsive_secondrow"})
        gamePriceStr = steampage('div', {'class': 'search_price'})
        gameReviewStr = steampage('span', {'class': 'search_review_summary'})

        print('Number of games found: {0}\n'.format(len(appStr)))
        
        for i in range(len(appStr)):
            appID = appStr[i].get('data-ds-appid')
            
            gameName = appStr[i].findAll('span', {'class': 'title'})[-1].get_text().replace('\u2122','').replace('\xae','').replace('\xf1','')
            
            # priceStr = re.findall(r"[-+]?\d*\.\d+|\d+", gamePriceStr[i].get_text())
            priceStr = re.findall(r"[-+]?\d*\.\d+|\d+", appStr[i].findAll('div',{'class': 'search_price'})[-1].get_text())
            if len(priceStr) == 0: priceStr = ['0.0']
            gamePrice = float(priceStr[-1])
            
            releaseDate = appStr[i].findAll('div', {'class': "col search_released responsive_secondrow"})[-1].get_text()
            
            gameReviewStr = appStr[i].findAll('span',{'class': 'search_review_summary'})
            if len(gameReviewStr) == 0:
                gameReview = 0
                gameReviewNum = 0
            else:
                reviewStr = re.findall(r"[-+]?\d*\.\d+|\d+", str(appStr[i].findAll('span',{'class': 'search_review_summary'})[-1]))
                gameReview = int(reviewStr[0])
                gameReviewNum = int(reviewStr[1])
            
            fileCSV.write('{0},"{1}",{2},"{3}",{4}%,{5}\n'.format(appID,gameName,gamePrice,releaseDate,gameReview,gameReviewNum))            
    
fileCSV.close()