# -*- coding: utf-8 -*-


from news_downloader import get_news_of_the_day


get_news_of_the_day(max_duration=300,duration=1200,save=False, url_file_name='urls_list.txt',video_previous_day=True,play_video=True)