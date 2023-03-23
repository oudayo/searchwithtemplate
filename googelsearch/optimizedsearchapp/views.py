import pickle
import random
from urllib.parse import quote_plus

import requests
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.dateparse import parse_duration


# from googleapiclient.discovery import build
# from apiclient.discovery import build
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# import numpy as np


def search(request):
    videos = []
    if request.method == "POST":

        query = request.POST.get("query")
        page_number = request.POST.get('page', 0)
        button1 = request.POST.get("button1")
        button2 = request.POST.get("button2")
        button3 = request.POST.get("button3")
        button4 = request.POST.get("button4")
        button5 = request.POST.get("button5")
        if button1 != None:
            level=1
        elif button2 != None:
            level=2
        elif button3 != None:
            level=3
        elif button4 != None:
            level=4
        elif button5 != None:
            level=5
        else:
            level=1
        api_key = "AIzaSyAt-w_yZPQwfYfhzgb6qyzSgzc1JBIcG-k"
        cx = "55643214e2b7c4c4e"
        # num = 100
        quote_plus(query)
        items = []
        page_number = int(page_number) * 10 + 1
        try:
            # for i in range(1, 100, 10):
            response = requests.get(f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}&start={page_number}&num=10&gl=us")
            data = response.json()
            items = data["items"]

            # get video
            search_url = 'https://www.googleapis.com/youtube/v3/search'
            video_url = 'https://www.googleapis.com/youtube/v3/videos'

            search_params = {
                'part': 'snippet',
                'q': query,
                'key': api_key,
                'maxResults': 10,
                'type': 'video'
            }

            r = requests.get(search_url, params=search_params)

            results = r.json()['items']
            video_ids = []
            for result in results:
                video_ids.append(result['id']['videoId'])

            video_params = {
                'key': api_key,
                'part': 'snippet,contentDetails',
                'id': ','.join(video_ids),
                'maxResults': 10
            }

            r = requests.get(video_url, params=video_params)

            results = r.json()['items']

            for result in results:
                video_data = {
                    'title': result['snippet']['title'],
                    'id': result['id'],
                    'url': f'https://www.youtube.com/watch?v={result["id"]}',
                    'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                    'thumbnail': result['snippet']['thumbnails']['high']['url']
                }

                videos.append(video_data)

        except:
            return render(request, "search.html",
                          {"runout": "runout", 'query': query, 'level': level, 'page_number': page_number})

        if items:
            if level == 1:
                items = [item for item in items if 'pagemap' in item and 'cse_image' in item['pagemap']]
            elif level == 2:
                items = [item for item in items if 'pagemap' in item and len(item['snippet']) <= 200]
            elif level == 3:
                items = [item for item in items if len(item['snippet']) <= 150]
            elif level == 4:
                items = [item for item in items if 'pagemap' in item and len(item['snippet']) >= 100]
            elif level == 5:
                items = [item for item in items]

            random.shuffle(items)
            random.shuffle(videos)
            return render(request, "search.html",
                          {"page_obj": items, 'query': query, 'level': level, 'page_number': int(page_number / 10) + 1,'videos': videos})
        else:
            items = []
            return render(request, "search.html", {"page_obj": items})

    else:
        return render(request, "search.html", {"empty": "empty"})