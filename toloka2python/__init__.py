"""Початок моєї бібліотеки"""
import json
import os
import logging

import requests
from bs4 import BeautifulSoup
from toloka2python.models.torrent import TorrentElement, TorrentAccount, Torrent
from toloka2python.models.account import Account
from toloka2python.account import get_account_info

# Set Logging
logging.basicConfig(level=logging.DEBUG)


class Toloka:
    """Клас для взаємодії з торрент-трекером Toloka"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }

    toloka_url = "https://toloka.to"

    def __init__(self, username: str, password: str, ssl="on", file: str = None):
        self.session = requests.Session()
        self.session.headers = self.headers

        # If not have cookie - do login
        if not os.path.exists("cookie.txt"):
            logging.info("No cookie file.")

            self.session.post(
                f"{self.toloka_url}/login.php",
                {
                    "username": username,
                    "password": password,
                    "autologin": "on",
                    "ssl": ssl,
                    "login": "Вхід",
                },
            )

            if file:
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

        # We have cookie, no need do request
        else:
            logging.info("Open cookie file.")
            with open("cookie.txt", "r", encoding="utf-8") as f:
                cookies = requests.utils.cookiejar_from_dict(json.load(f))
                self.session.cookies.update(cookies)

    def search(self, nm):
        """Пошук торрентів за запитом"""
        result = self.session.get(
            f"{self.toloka_url}/tracker.php?nm={nm}&pn=&send=Пошук"
        )
        torrent_list = []
        soup = BeautifulSoup(result.text, "html.parser")
        for torrent in soup.find_all("tr", class_=["prow1", "prow2"]):
            torrent = torrent.find_all("td")

            torrent_list.append(
                TorrentElement(
                    torrent[1].text,  # Форум
                    torrent[1].find("a", class_="gen")["href"],  # Посил на форум
                    torrent[2].find("a")["href"],  # Посил на торрент
                    torrent[2].text,  # Назва
                    torrent[3].text,  # Автор
                    True if torrent[4].text == "+" else False,  # Пер
                    torrent[5].find("a")["href"],  # Посил
                    torrent[6].text,  # Розмір
                    torrent[7]["title"],  # Статус
                    torrent[9].text,  # S
                    torrent[10].text,  # L
                    torrent[11].text,  # R
                    torrent[12].text,  # Додано
                )
            )
        return torrent_list

    @property
    def html(self):
        """Отримати HTML головної сторінки"""
        return self.session.get(self.toloka_url)

    @property
    def me(self):
        """Отримати інформацію про себе"""
        # Get main page for get account url
        soup = BeautifulSoup(self.html.text, "html.parser")

        # Get request to account url
        me_html = self.session.get(
            f"{self.toloka_url}/{soup.find('a', string='Профіль')['href']}"
        ).text
        return get_account_info(me_html)

    def get_account(self, url: str):
        """Отримати інформацію про користувача за посиланням"""
        # Get request to account url
        return get_account_info(self.session.get(url).text)

    def get_torrent(self, url):
        """Отримати інформацію про торрент за посиланням"""
        soup = BeautifulSoup(self.session.get(url + "?spmode=full&dl=names#torrent").text, "html.parser")

        name = soup.find("a", class_="maintitle").text
        url = soup.find("a", class_="maintitle")["href"]
        img = soup.find("img", attrs={"alt": name})
        if img:
            img = img.get("src", None)

        torrent_name = soup.find("tr", class_="row6_to").text
        registered_date = soup.find("td", string=" Зареєстрований: ").find_next("td").contents[0][3:]
        size = soup.find("td", string=" Розмір: ").find_next("span").contents[0].replace("\xa0", "")
        thanks = soup.find("td", string=" Подякували: ").find_next("span").contents[0]
        rating = soup.find("span", attrs={"itemprop": "ratingValue"}).text
        torrent_url = soup.find("a", string="Завантажити")["href"]

        return Torrent(
            name,
            url,
            img,
            torrent_name.replace("\xa0", " ").replace("\n", "")[1:-1],
            registered_date,
            size,
            int(thanks),
            rating,
            torrent_url,
        )

    def download_torrent(self, torrent_url: str):
        return self.session.get(torrent_url).content
