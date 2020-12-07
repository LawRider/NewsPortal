from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from itertools import groupby
import json

NEWS_JSON_PATH = settings.NEWS_JSON_PATH


class MainView(View):
    def get(self, request, *args, **kwargs):
        html = """
        <h1>Coming soon</h1>
        <a href="/news/">News</a>
        """
        return HttpResponse(html)


class ArticleListView(View):
    def get(self, request, *args, **kwargs):
        with open(NEWS_JSON_PATH) as json_db:
            json_data = json.load(json_db)
        query_string = request.GET.get('q', None)
        if query_string is not None:
            src_results = []
            for article in json_data:
                if query_string.strip().lower() in article['title'].lower():
                    src_results.append(article)
            grouped_by_day = self.group_articles(src_results)
        else:
            grouped_by_day = self.group_articles(json_data)
        return render(request, 'news/main.html', {'grouped_by_day': grouped_by_day})

    @staticmethod
    def group_articles(json_data):
        # Sort list by value of the key 'created' in dicts in reverse order
        json_data_sorted = sorted(json_data, key=lambda i: i['created'], reverse=True)
        grouped_by_day = {}
        # Strip time value of the key 'created' in dicts
        # This value will be a key for dicts grouped in lists
        for k, g in groupby(json_data_sorted, key=lambda i: i['created'][:10]):
            grouped_by_day[k] = list(g)
        return grouped_by_day


class ArticleView(View):
    def get(self, request, article_id, *args, **kwargs):
        with open(NEWS_JSON_PATH) as json_db:
            json_data = json.load(json_db)
            for article in json_data:
                if article['link'] == article_id:
                    article_data = article
                    break
        return render(request, 'news/article.html', {'article': article_data})


class AddArticleView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'news/add_article.html')

    def post(self, request, *args, **kwargs):
        title = request.POST['title']
        text = request.POST['text']
        created = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open(NEWS_JSON_PATH) as f:
            json_data = json.load(f)
        link_id = max(i['link'] for i in json_data) + 1
        new_record = {"created": created, "text": text, "title": title, "link": link_id}
        json_data.append(new_record)
        with open(NEWS_JSON_PATH, 'w') as f:
            json.dump(json_data, f)
        return redirect('/news/')
