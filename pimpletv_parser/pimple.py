"""
pip install discord, bs4, requests
"""

import discord
from discord.ext import tasks

from config import *
import requests
from bs4 import BeautifulSoup as bs

import time
from datetime import datetime

text_file = open('sent_matches.txt', 'r')
sent_matches = text_file.read().split('\n')
text_file.close()

match = {
    'url': 'none'
}


def get_match_list():
    site = requests.get('https://www.pimpletv.ru/')
    soup = bs(site.text, "html.parser")
    content = soup.find(class_='sport')  # not string!
    days = content.find_all(class_='streams-day')
    matches_list = []
    matches = content.find_all(class_='match-item _rates')  # список матчей, элементы
    for match in matches:
        matches_list.append(f'https://pimpletv.ru{match["href"]}')
    return matches_list


def match_is_sent(url=str):
    if url in sent_matches:
        return True
    else:
        return False


def get_match(url=str):  # 'str'
    match_page = requests.get(url)
    parser_match_page = bs(match_page.text, "html.parser")
    if parser_match_page.find(class_='btn-watch') is None:
        match_dict = {
            'Дата и время': parser_match_page.find('p', attrs={'itemprop': 'startDate'}).text.split('\n')[0],
            'Домашняя команда': parser_match_page.find_all(class_='team')[0].text,
            'Гостевая команда': parser_match_page.find_all(class_='team')[1].text,
            'Ссылка на страницу с матчем': url,
            'Ссылка на трансляцию': 'нету'
        }
    else:
        match_dict = {
            'Дата и время': parser_match_page.find('p', attrs={'itemprop': 'startDate'}).text.split('\n')[0],
            'Домашняя команда': parser_match_page.find_all(class_='team')[0].text,
            'Гостевая команда': parser_match_page.find_all(class_='team')[1].text,
            'Ссылка на страницу с матчем': url,
            'Ссылка на трансляцию': parser_match_page.find(class_='btn-watch')['href']
        }
    return (match_dict)


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0

        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print('Опять работа?')
        print(self.user.name)
        print(self.user.id)
        print('------')

    @tasks.loop(seconds=10 * 60)
    async def my_background_task(self):
        channel = self.get_channel(976125197302243338)  # channel ID goes here
        for match_url in get_match_list():
            if match_is_sent(match_url):
                pass
            else:
                match = get_match(match_url)
                if match.get('Ссылка на трансляцию') == 'нету':
                    pass
                else:
                    message = f'-\n**{match.get("Домашняя команда")} — {match.get("Гостевая команда")}**\n{match.get("Дата и время")}\n{match.get("Ссылка на трансляцию")}'
                    sent_matches.append(match_url)
                    text_file = open('sent_matches.txt', 'a')
                    text_file.write(match_url + '\n')
                    text_file.close()
                    #await channel.send(message)
                    print(message)

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = MyClient()
client.run(discord_token)
