from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.list import ThreeLineAvatarListItem, ImageLeftWidget
from kivymd.app import MDApp
import certifi

import os
import urllib3
import chardet
import warnings

import json
import requests
import tmdbsimple as tmdb



tmdb.API_KEY = 'a94278cb91874a2154e9ca93b46260b4'


style = Builder.load_file('popfilms.kv')

class MainScreen(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class CatalogScreen(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
	
        if pop.data:
            self.update_page()

    def update_page(self):
        for i in range(len(pop.data)):
            TLALI = ThreeLineAvatarListItem(
		  text=pop.data[i]["title"],
		  secondary_text=f"Дата выхода: {pop.data[i]['date']} | Рейтинг: {pop.data[i]['vote']}",
		  tertiary_text=pop.data[i]['view'],on_press=lambda x: self.change_film(x))
            TLALI.add_widget(ImageLeftWidget(source=pop.data[i]['path']))
            self.ids.scroll.add_widget(TLALI)

    def change_film(self, name):
        pop.card_page.get_film(name.text)
        pop.sm.current = 'card'




class CardScreen(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name_film = ''
        if self.name_film:
            self.update_film_info()


    def update_film_info(self):

        self.filtered_db = [d for d in pop.data if d['title'] == self.name_film]
        self.id = self.filtered_db[0]['id']
        movie = tmdb.Movies(self.id)
        self.info = movie.info(language='ru')
        self.ids.genre.text = 'Жанр: ' + self.get_genre()
        self.ids.budget.text = 'Бюджет: ' +str(self.info['budget']) + "$"
        self.actor, self.director, self.writer = self.get_info(self.id)
        self.ids.poster.source = self.filtered_db[0]["path"]
        self.ids.title.text = self.filtered_db[0]['title']
        self.ids.date.text =  f"Дата: {self.filtered_db[0]['date']}"
        self.ids.vote.text = str(self.filtered_db[0]['vote'])
        self.ids.describe.text = f"Описание\n{self.filtered_db[0]['view']}"
        self.ids.director.text = "Режиссёр: " + self.director[0]['name']
        self.ids.writer.text = "Сценарий: " + self.writer[0]['name']
        self.change_actors()


    def get_genre(self):
        genre = []
        for i in range(2):
            genre.append(self.info['genres'][i]['name'])
        return ', '.join(genre)

    def get_info(self, id):
        r = requests.get(
            f'https://api.themoviedb.org/3/movie/{id}/credits?api_key=a94278cb91874a2154e9ca93b46260b4&language=ru-Ru')
        actor = [d for d in r.json()['cast'] if d['known_for_department'] == 'Acting']
        director = [d for d in r.json()['crew'] if d["job"] == 'Director']
        writer = [d for d in r.json()['crew'] if d['job'] == "Editor"]
        return actor, director, writer

    def change_actors(self):
        self.clean()
        for i in range(5):
            self.ids.actors.add_widget(SmartTileWithLabel(
                source=f"https://image.tmdb.org/t/p/w92///{self.actor[i]['profile_path']}",
                text=f'[size=12]{self.actor[i]["name"]}[/size]', height='100dp'))

    def get_film(self, name):
        self.name_film = name
        self.update_film_info()

    def clean(self):
        rows = [i for i in self.ids.actors.children]
        for row1 in rows:
                self.ids.actors.remove_widget(row1)




class PopfilmsApp(MDApp):
    def build(self):
        self.data = []
        self.theme_cls.theme_style = "Dark"
        self.sm = ScreenManager()

        self.main  = MainScreen()
        screen = Screen(name='main')
        screen.add_widget(self.main)
        self.sm.add_widget(screen)

        self.catalog = CatalogScreen()
        screen = Screen(name='catalog')
        screen.add_widget(self.catalog)
        self.sm.add_widget(screen)

        self.card_page = CardScreen()
        screen = Screen(name='card')
        screen.add_widget(self.card_page)
        self.sm.add_widget(screen)

        return self.sm
    
    def on_start(self):
        self.req = requests.get(
            'https://api.themoviedb.org/3/movie/popular?api_key=a94278cb91874a2154e9ca93b46260b4&language=ru-US&page=1')
        with open('db.json', 'w', encoding='utf-8') as data:
            data.write(self.req.text)
        self.read_json()
    
    def read_json(self):
        with open('db.json', 'r', encoding='utf-8') as data:
            db = json.loads(data.read())
        for i in db['results']:
            id = i['id']
            url = i['poster_path']
            title = i['title']
            describe = i['overview']
            vote = i["vote_average"] if bool(i["vote_average"]) else '-'
            date = i["release_date"] if i.get("release_date") else '-'
            self.data.append(
        {'id': id, 'path': f"https://image.tmdb.org/t/p/w92///{url}", "title": title, "view": describe, 'vote': vote, 'date': date})
        pop.catalog.update_page()
    def to_catalog(self):
        pop.sm.current = 'catalog'
    
        

if __name__ == '__main__':
    pop = PopfilmsApp()
    pop.run()