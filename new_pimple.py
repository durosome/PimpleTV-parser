import requests
from bs4 import BeautifulSoup as bs


def load_site(url=str):
    for i in range(1, 10):
        try:
            site = requests.get(url).text
            break
        except:
            site = '404'
    return site

class Pimple:
    def open_history(self) -> list:
        self.matches_history = open('sent_matches.txt', 'r')
        self.sent_matches = self.matches_history.read().split('\n')
        self.matches_history.close()
        return self.sent_matches

    def __init__(self, url=str):
        self.sent_matches = self.open_history()
        self.html = load_site(url)



    def check_matches(self) -> list:
        self.parser = bs(self.html, "html.parser")
        self.content = self.parser.find(class_='sport')
        self.days = self.content.find_all(class_='streams-day')
        self.matches = self.content.find_all(class_='match-item _rates')  # список матчей, элементы
        self.matches_list = []
        for match in self.matches:
            if match in self.sent_matches:
                pass
            else:
                self.matches_list.append(f'https://pimpletv.ru{match["href"]}')
        return self.matches_list

    def send_matches(self, matches):
        for url in matches:
            match = Match(url)



class Match:
    def format_message(self):
        self.message = f'-\n**{self.home_team} — {self.away_team}**\n{self.datetime}\n{self.ace_url}'
        return self.message

    def parse_match(self, url) -> dict:
        self.html = load_site(url)
        if self.html == '404':
            return
        else:
            self.parser = bs(self.html, "html.parser")
            if self.parser.find(class_='btn-watch') is None:
                self.match_dict = {
                    'Дата и время': self.parser.find('p', attrs={'itemprop': 'startDate'}).text.split('\n')[0],
                    'Домашняя команда': self.parser.find_all(class_='team')[0].text,
                    'Гостевая команда': self.parser.find_all(class_='team')[1].text,
                    'Ссылка на страницу с матчем': url,
                    'Ссылка на трансляцию': 'нету'
                }
            else:
                self.match_dict = {
                    'Дата и время': self.parser.find('p', attrs={'itemprop': 'startDate'}).text.split('\n')[0],
                    'Домашняя команда': self.parser.find_all(class_='team')[0].text,
                    'Гостевая команда': self.parser.find_all(class_='team')[1].text,
                    'Ссылка на страницу с матчем': url,
                    'Ссылка на трансляцию': self.parser.find(class_='btn-watch')['href']
                }
        return self.match_dict

    def send_match(self):
        if self.ace_url == 'нету':
            pass
        else:
            self.format_message(self)


    def __init__(self, url=str):
        self.dict = self.parse_match(url)
        self.url = url
        self.datetime = self.dict.get('Дата и время')
        self.home_team = self.dict.get('Домашняя команда')
        self.away_team = self.dict.get('Гостевая команда')
        self.ace_url = self.dict.get('Ссылка на трансляцию')
        self.send_match(self)



'''
    site = load_site('http://pimpletv.ru/')
    check_matches(site)
    for match in matches:
        parse_match(match)
'''

pimple = Pimple('http://pimpletv.ru/')
matches = pimple.check_matches()
pimple.send_matches(matches)
