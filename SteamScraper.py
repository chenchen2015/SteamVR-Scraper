'''
Steam App Data Scraper
Version: 2.0

License Agreement: MIT License

Author: Chen Chen  (chenchen.bme@gmail.com)
12/11/2016
'''

import urllib
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re
from sys import stdout

# Store URL Base to Scrape
storeURL = "http://store.steampowered.com/search/?tags=21978&vrsupport=401"
steamAppURL = "http://store.steampowered.com/app/{0}/"
steamSpyURL = "http://steamspy.com/app/{0}"

# Get current time stamp
timestamp = time.time()
currentTime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# File handle
fileCSV = open('SteamVR-Data-{0}.csv'.format(datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')), 'w')

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
fileCSV.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}\n'.format(
              'Steam App ID', 
              'Game Name', 
              'Price', 
              'Release Date', 
              'Positive Review Percentage', 
              'Reviews Count',
              'Developer',
              'Publisher',
              'Genre',
              'Category',
              'Tags',
              'Peak User Yesterday',
              'Number of Owners',
              'Number of Players',
              'Percentage of Actual Players in the Owners'
              ))

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
            print("Scraping app data {0}/{1} ({2}%)".format(i,len(appStr),100*i/len(appStr)), flush=True)
            # Get App ID
            appID = appStr[i].get('data-ds-appid')
            
            # Game Name
            gameName = appStr[i].findAll('span', {'class': 'title'})[-1].get_text().replace('\u2122','').replace('\xae','').replace('\xf1','').replace('\u2122','(TM)')
            
            # Game Price
            priceStr = re.findall(r"[-+]?\d*\.\d+|\d+", appStr[i].findAll('div',{'class': 'search_price'})[-1].get_text())
            if len(priceStr) == 0: priceStr = ['0.0']
            gamePrice = float(priceStr[-1])
            
            # Release Date
            releaseDate = appStr[i].findAll('div', {'class': "col search_released responsive_secondrow"})[-1].get_text()
            
            # Positive Review Percentage and Number of User Reviews
            gameReviewStr = appStr[i].findAll('span',{'class': 'search_review_summary'})
            if len(gameReviewStr) == 0:
                gameReview = 0
                gameReviewNum = 0
            else:
                reviewStr = re.findall(r"[-+]?\d*\.\d+|\d+", str(appStr[i].findAll('span',{'class': 'search_review_summary'})[-1]))
                gameReview = int(reviewStr[0])
                gameReviewNum = int(reviewStr[1])
            
            # v2.0 Update
            # Let's push this further by get to the app page and scrape deeper
            # data including tags, reviews and many more...
            if str(appID) == 'None':
                # Could not find any App ID
                # This senario has been found with:
                #    1) This is a game boundle sales link
                #
                # I will just dump this data and continue...
                continue
                '''
                tagsStr = ''
                developerStr = ''     
                publisherStr = ''   
                genreStr = ''
                categoryStr = ''
                peakUserYesterday = ''
                ownersMean = -1
                ownersSEM = ''
                playersMean = -1
                playersSEM = ''
                playersPercentage = ''
                '''
            else:
                appPageURL = steamSpyURL.format(appID)
                appPage = BeautifulSoup(requests.get(appPageURL).text, "lxml")
                
                appDataStr = appPage('div', {'class' : 'p-r-30'})[0].get_text().replace('\xeb','e').replace('\xc5','A').replace('\u0161','s').replace('\u2122','(TM)')
                
                try:
                    tagsStr = re.search('Tags: (.*)Category:', appDataStr).group(1)
                except:
                    tagsStr = ''
                    
                try:
                    developerStr = re.search('Developer: (.*) Publisher:', appDataStr).group(1)
                except:
                    developerStr = ''        
               
                try:
                    publisherStr = re.search('Publisher: (.*) Genre:', appDataStr).group(1)
                except:
                    publisherStr = ''        
                
                try:
                    genreStr = re.search('Genre: (.*)Languages:', appDataStr).group(1)
                except:
                    genreStr = ''       
                
                try:
                    categoryStr = re.search('Category: (.*)Release date:', appDataStr).group(1)
                except:
                    categoryStr = ''        
                
                try:
                    peakUserYesterday = int(re.search('players yesterday: (\d*)', appDataStr).group(1))
                except:
                    peakUserYesterday = ''
                    
                regex = re.compile('Owners: (\d*.\d*) \xB1 (\d*.\d*)',re.UNICODE)
                regexResult = re.search(regex, appDataStr)
                try:
                    ownersMean = int(re.sub("[^0-9]", "", regexResult.group(1)))
                    ownersSEM  = int(re.sub("[^0-9]", "", regexResult.group(2)))
                except:
                    ownersMean = -1
                    ownersSEM = ''
                
                regex = re.compile('Players total: (\d*.\d*) \xB1 (\d*.\d*)',re.UNICODE)
                regexResult = re.search(regex, appDataStr)
                try:
                    playersMean = int(re.sub("[^0-9]", "", regexResult.group(1)))
                    playersSEM  = int(re.sub("[^0-9]", "", regexResult.group(2)))
                except:
                    playersMean = -1
                    playersSEM = ''
                    
                # Percentage of Players who played the game for at least once
                if ownersMean > 0 and playersMean >= 0:
                    playersPercentage = 100.0 * playersMean / ownersMean
                else:
                    playersPercentage = ''.encode(stdout.encoding, errors='replace')
            
            fileCSV.write('{0},"{1}",{2},"{3}",{4},{5},"{6}","{7}","{8}","{9}","{10}",{11},{12} +/- {13},{14} +/- {15},{16}\n'.format(
                          appID.encode(stdout.encoding, errors='replace'),             # 0  - Steam Store App ID
                          gameName.encode(stdout.encoding, errors='replace'),          # 1  - App Name
                          gamePrice,                                                   # 2  - App Price
                          releaseDate.encode(stdout.encoding, errors='replace'),       # 3  - Date Released
                          gameReview,                                                  # 4  - Percentage of Positive Reviews
                          gameReviewNum,                                               # 5  - Total Number of Reviews Recorded
                          developerStr.encode(stdout.encoding, errors='replace'),      # 6  - Developer
                          publisherStr.encode(stdout.encoding, errors='replace'),      # 7  - Publisher
                          genreStr.encode(stdout.encoding, errors='replace'),          # 8  - Genre
                          categoryStr.encode(stdout.encoding, errors='replace'),       # 9  - Category
                          tagsStr.encode(stdout.encoding, errors='replace'),           # 10 - Game Tags
                          peakUserYesterday,                                           # 11 - Peak User Yesterday
                          ownersMean,                                                  # 12 - Estimated Number of Owners (mean)
                          ownersSEM,                                                   # 13 - Estimated Number of Owners (SEM)
                          playersMean,                                                 # 14 - Estimated Number of Players (mean)
                          playersSEM,                                                  # 15 - Estimated Number of Players (SEM)
                          playersPercentage,                                           # 16 - Estimated Percentage of Active Players
                          ))          
    
fileCSV.close()
