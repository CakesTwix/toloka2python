"""Початок моєї бібліотеки"""
import json
import os
import logging

import requests
from bs4 import BeautifulSoup
from toloka2python.models.torrent import TorrentElement, TorrentAccount
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
                    torrent[1].find("a", class_="gen")["href"],  # Посил на форум
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
        account_soup = BeautifulSoup(me_html, "html.parser").find_all(
            "td", class_="bodyline"
        )[1]

        # Доступна інформація про ...
        info_soup = account_soup.find_all("td", class_="row1")[1].find_all("tr")

        # Зв'язок з ...
        communicate_soup = account_soup.find_all("td", class_="row1")[2].find_all("tr")

        # Torrent-профіль користувача ...
        torrent_profile_soup = account_soup.find("td", class_="row2").find_all("tr")

        upload_torrent_list = []
        # TODO: Implement
        download_torrent_list = []

        # Активні торренти
        for upload_torrent in account_soup.find_all("table", class_="forumline")[
            1
        ].find_all("tr")[6:]:
            if len(upload_torrent) == 9:
                # logging.debug(upload_torrent)
                upload_torrent_list.append(
                    TorrentAccount(
                        upload_torrent.find("span", class_="gen").text,
                        upload_torrent.find("a", class_="gen")["href"],
                        upload_torrent.find("a", class_="genmed").text,
                        upload_torrent.find("span", class_="seedmed").text,
                        upload_torrent.find("span", class_="leechmed").text,
                        upload_torrent.find("a", class_="genmed")["href"],
                    )
                )

        # logging.debug(torrent_profile_soup)

        return Account(
            soup.find("a", string="Профіль")["href"],
            account_soup.find("img")["src"],
            True if account_soup.find("font", string="(в мережі)") else False,
            communicate_soup[0].find_all("span", class_="gen")[1].text,
            communicate_soup[2].find_all("span", class_="gen")[1].text,
            info_soup[0].find_all("span", class_="gen")[1].text,
            info_soup[1].find_all("span", class_="gen")[1].text,
            int(info_soup[2].find_all("span", class_="gen")[1].text),
            torrent_profile_soup[1]
            .find("span", class_="seed")
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[2]
            .find("span", class_="leech")
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[1]
            .find_all("span", class_="seed")[1]
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[2]
            .find_all("span", class_="leech")[1]
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[1]
            .find_all("span", class_="seed")[2]
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[2]
            .find_all("span", class_="leech")[2]
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[3]
            .find_all("span", class_="gen")[1]
            .text.replace("\xa0", " "),
            torrent_profile_soup[3]
            .find_all("span", class_="gen")[3]
            .text.replace("\xa0", " "),
            torrent_profile_soup[3]
            .find_all("span", class_="gen")[4]
            .text.replace("\xa0", " "),
            torrent_profile_soup[4]
            .find_all("span", class_="gen")[1]
            .text.replace("\xa0", " "),  # TODO: Fix ul_dl_rating
            torrent_profile_soup[4]
            .find_all("span", class_="gen")[1]
            .text.replace("\xa0", " "),  # TODO: Fix ul_dl_rating
            torrent_profile_soup[6].find("span", class_="seed").text,
            torrent_profile_soup[7].find_all("span", class_="gen")[1].text,
            torrent_profile_soup[8]
            .find("span", class_="leech")
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[8]
            .find("span", class_="seed")
            .find("b")
            .text.replace("\xa0", " "),
            torrent_profile_soup[9].find_all("span", class_="gen")[1].text,
            upload_torrent_list,
            download_torrent_list,
        )
