"""Початок моєї бібліотеки"""
import json
import os
import logging

import requests
from bs4 import BeautifulSoup
from toloka2python.models.torrent import TorrentElement
from toloka2python.models.account import Account

# Set Logging
logging.basicConfig(level=logging.DEBUG)


class Toloka:
    """Клас для взаємодії з торрент-трекером Toloka"""

    toloka_url = "https://toloka.to"

    def __init__(self, username: str, password: str, ssl="on"):
        self.session = requests.Session()

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
            with open("cookie.txt", "w", encoding="utf-8") as f:
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
        return self.session.get(self.toloka_url)

    @property
    def me(self):
        # Get main page for get account url
        soup = BeautifulSoup(self.html.text, "html.parser")

        # Get request to account url
        me_html = self.session.get(
            f"{self.toloka_url}/{soup.find('a', string='Профіль')['href']}"
        ).text
        account_soup = BeautifulSoup(me_html, "html.parser").find_all("td", class_="bodyline")[1]

        #  	Доступна інформація про ...
        info_soup = account_soup.find_all("td", class_="row1")[1].find_all("tr")

        # Зв'язок з ...
        communicate_soup = account_soup.find_all("td", class_="row1")[2].find_all("tr")
        # logging.debug(info_soup)

        # logging.debug(account_soup)
        # TODO: Account
        return Account(
            soup.find("a", string="Профіль")["href"],
            account_soup.find("img")["src"],
            True if account_soup.find("font", string="(в мережі)") else False,
            communicate_soup[0].find_all("span", class_="gen")[1].text,
            communicate_soup[2].find_all("span", class_="gen")[1].text,
            info_soup[0].find_all("span", class_="gen")[1].text,
            info_soup[1].find_all("span", class_="gen")[1].text,
            int(info_soup[2].find_all("span", class_="gen")[1].text),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        )
