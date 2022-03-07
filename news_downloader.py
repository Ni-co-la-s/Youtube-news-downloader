# -*- coding: utf-8 -*-



import glob, os
import subprocess
import sys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import youtube_dl
import re
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
from collections import Counter
import numpy as np
import yt_dlp
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
   

s=Service(ChromeDriverManager().install())

options = webdriver.ChromeOptions()
options.add_argument("--headless");
options.add_argument("--log-level=3");
options.add_argument("--output=NUL");


class Video:
    def __init__(self,link, name, translated_name, date, source,duration,downloaded=False):
      self.link = link
      self.name = name
      self.translated_name=translated_name
      self.date=date
      self.downloaded=downloaded
      self.source=source
      self.duration=duration
      
    def download(self):
        
        os.system("cls")
        
        ydl = youtube_dl.YoutubeDL()
        ydl_opts = {
            'quiet': True,
            'outtmpl': os.path.join(self.date, self.name+".%(ext)s"),

        }        
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.link])
        self.downloaded=True
        


# In: List of Videos
# Out: List of stemmed words 
#      List of stemmed titles (list of lists of stemmed words)
def get_english_titles(List_videos):
    
    List_videos=[video.translated_name for video in List_videos]
    list_stemmed_words=[]
    List_stemmed_titles=[]
    
    for title in List_videos:

        new_title = re.sub('[^a-zA-Z]', ' ', title)
        new_title = new_title.lower()
        new_title = new_title.split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        new_title = [ps.stem(word) for word in new_title if not word in set(all_stopwords)]
        list_stemmed_words=list_stemmed_words+new_title
        List_stemmed_titles.append(new_title)
        
    return(list_stemmed_words,List_stemmed_titles)


#In: List of videos
#Out: Counter of all stemmed words in the headlines
#     List of stemmed_titles (list of list of stemmed_words)
def get_most_common_word(List_videos):
    list_stemmed_words,List_stemmed_titles=get_english_titles(List_videos)
    counts = Counter(list_stemmed_words)
    return(counts,List_stemmed_titles)


#In: List of videos
#    Sum of the durations of the videos to download (default: 1200) 
#    Maximum duration of a video in s (default: 300)
#Out: List of the videos_downloaded
def pick_video(List_videos,duration,max_duration):
    count,List_stemmed_titles=get_most_common_word(List_videos)
    liste_score=[]
    
    for i in range(len(List_stemmed_titles)):
        score=0
        for mot in List_stemmed_titles[i]:
            score=score+count[mot]
        score=score/len(List_stemmed_titles[i])-List_videos[i].duration/30
        liste_score.append(score)
    array_score=np.array(liste_score)  
    sorted_array=np.argsort(array_score)
 
    i=0
    list_downloaded=[]
    t0_5=duration*0.6
    while(duration>t0_5):
        List_videos[i].download()
        duration-List_videos[i].duration
        list_downloaded.append(List_videos[i])

        i=i+1

    i=len(sorted_array)-1
    while(duration>0):
        List_videos[i].download()
        duration=duration-List_videos[i].duration
        list_downloaded.append(List_videos[i])

        i=i-1
    return(list_downloaded)
           
  

#In: Url of a channel
#Out: The Url of the page containing its videos if possible, otherwise empty string 
def clean(url):
    channel=re.findall("https://www.youtube.com/(c|channel)/(.*)/(.*)", url)
    if(len(channel)==0):
        channel=re.findall("https://www.youtube.com/(c|channel)/(.*)", url)

    if len(channel)==0:
        return ""
    else:
        return "https://www.youtube.com/"+channel[0][0]+'/'+channel[0][1]+"/videos"



#In: Url of a channel
#    Boolean indicating whether the videos of the previous day must be downloaded as well (default: True)
#    Maximum duration of a video in s (default: 300)
#Out: List of Videos found on the channel
def get_headlines_youtube_channel(url,video_previous_day,max_duration):
    List_video=[]
    
    driver = webdriver.Chrome(service=s, options=options)

    today = datetime.now()
    d1 = today.strftime("%Y%m%d")
    yesterday= today - timedelta(1)
    d2 =yesterday.strftime("%Y%m%d")

    driver.get(url)
    cookie=driver.find_elements(By.XPATH,'//div/button')
    if len(cookie)!=0:
        cookie[1].click()
    headlines=driver.find_elements(By.XPATH,'//*[@id="video-title"]')
    if len(headlines)==0:
        return []
    url=[headlines[k].get_attribute('href') for k in range(len(headlines))]

    for source_url in url:
        with youtube_dl.YoutubeDL() as ydl:                  
            info = ydl.extract_info(source_url, download=False)
            date = info.get('upload_date')
            title = info.get('title')
            duration=info.get('duration')
            if(video_previous_day==False):
                d2=d1 
    
            if (date==d1 or date==d2) and duration<max_duration and title not in [a.name for a in List_video]:
                translated = GoogleTranslator(source='auto', target='en').translate(title)
                List_video.append(Video(source_url,title,translated,d1,"ytb",duration))
            else:
                break
    driver.quit()
    return(List_video)



        
    
#In: Sum of the durations of the videos to download (default: 1200)
#    Maximum duration of a video in s (default: 300)
#    Boolean indicating whether the meta-infos on the videos must be saved (default False): not implemented yet
#    Path of a txt file containing the urls of the channel (default: 'urls_list.txt')
#    Boolean indicating whether the videos of the previous day must be downloaded as well (default: True)
#    Boolean indicating whether the videos must be played after downloading (default:True)
def get_news_of_the_day(max_duration=300,duration=1200,save=False, url_file_name='urls_list.txt',video_previous_day=True,play_video=True):
    
    try:
        f = open(url_file_name)
    except (OSError,IOError):
        print ("Could not open/read file:", url_file_name)
        sys.exit()
    Lf=[]

    with f:
        lines = f.readlines()
        for url in lines:
            url_cleaned=clean(url)
            if(url_cleaned==""):
                print("URL not valid: "+url)
            else:
                List_videos=get_headlines_youtube_channel(url,video_previous_day,max_duration)
                if List_videos==[]:
                    print("Channel does not exist or does not have videos in the period wanted: "+url)
                else:
                    Lf=Lf+List_videos
                    print(Lf)

    pick_video(Lf,duration)
    
    if (play_video==True):
        play()


#In: Path of the VLC exe (default: "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe)
def play(vlc_path=os.path.join("C:\\", "Program Files (x86)", "VideoLAN", "VLC", "vlc.exe")):
    if not(os.path.exists(vlc_path)):
        print ("Could not find path: ", vlc_path)
        sys.exit()
        
    today = datetime.now()
    d1_format = today.strftime("%Y%m%d")
    
    os.chdir(os.path.abspath(d1_format))
    video_list = glob.glob("*.webm")
    
    cmd = [vlc_path, '--play-and-exit']
    cmd.extend ( video_list)
    subprocess.run(cmd)
              
                    
