# Youtube news downloader

This program aims to be executed daily in order to download recent videos from news Youtube channels of your choosing.

## Description

From a txt file containing channel urls (one by line) this program downloads their recent videos (of the current day and eventually the day before) and stores them in a folder named on the current date.
To perform the scraping, Selenium is used to collect the videos url (can not use BeautifulSoup because the website is JavaScript rendered).
To select the videos to download, the current strategy is to look at the frequency of the words used in all titles (translating them in english with GoogleTranslater and excluding stopwords and stemming with nltk) and choosing videos containing the most and least common words on average (in order to get the most spread news, but not only). This method is pretty basic and could be improved.
After that, the videos are downloaded using yt_dlp (better performance than youtube_dl) and played with VLC.

## Getting Started

### Dependencies

*OS: Windows 10 or higher
*glob
*nltk
*deep_translator
*selenium and webdriver_manager
*yt_dlp



### Installing

Clone this project or place the 3 files (main.py, news_downloader.py and urls_list.txt) in the same folder.
Write in urls_list.txt the urls of the News Youtube channels you are interested in (one per line, no separator)
Make sure that you have installed all of the dependencies stated above and that the path given in vlc_path correspond to the executable of VLC on your computer (correct it if needed).


### Executing program

The program can be used merely by executing main.py
