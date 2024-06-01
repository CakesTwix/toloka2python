"""Початок моєї бібліотеки"""
import json
import os
import logging
import re

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from toloka2python.models.torrent import TorrentElement, TorrentAccount, Torrent, TorrentFile
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
            
            input_date = torrent[12].text
            parsed_date = datetime.strptime(input_date, "%Y-%m-%d")
            output_date = parsed_date.strftime("%y-%m-%d %H:%M")
            
            torrent_list.append(
                TorrentElement(
                forum=torrent[1].text,
                forum_url=torrent[1].find("a", class_="gen")["href"],
                url=torrent[2].find("a")["href"],
                name=torrent[2].text,
                author=torrent[3].text,
                verify=True if torrent[4].text == "+" else False,
                torrent_url=torrent[5].find("a")["href"],
                size=torrent[6].text,
                status=torrent[7]["title"],
                seeders=torrent[9].text,
                leechers=torrent[10].text,
                answers=torrent[11].text,
                date=output_date
                )
            )
        return torrent_list

    def searchv2(self, nm):
        """Пошук торрентів за запитом в API"""
        result = self.session.get(
            f"{self.toloka_url}/api.php?search={nm}"
        )
        torrent_list = []
        
        data = result.json()

        torrent_list = []
        for item in data:
            torrent_element = TorrentElement(
                forum=item["forum_name"],
                forum_url=item["forum_parent"],
                url=item["link"],
                name=item["title"],
                author="",
                verify=False,
                torrent_url="",
                size=item["size"],
                status="",
                seeders=int(item["seeders"]),
                leechers=int(item["leechers"]),
                answers=int(item["comments"]),
                date=""
            )
            torrent_list.append(torrent_element)

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
        content = self.session.get(url + "?spmode=full&dl=names#torrent").text
        # Remove extra whitespace, newline, and tab characters using regular expressions
        cleaned_content = re.sub(r'[\n\t]+', '', content)
        soup = BeautifulSoup(cleaned_content, "html.parser")

        name = soup.find("a", class_="maintitle").text
        url = soup.find("a", class_="maintitle")["href"].replace("/","")
        forum = soup.select_one("td[class='nav'] h2:nth-of-type(2) a").text
        forum_url = soup.select_one("td[class='nav'] h2:nth-of-type(2) a")["href"].replace("f","tracker.php?f=")        
        author = soup.select_one("td.row1 span.name b a").text
        
        thumb = soup.select_one("[rel=image_src]")['href']
        img = soup.find("img", attrs={"alt": name})
        img_alt = soup.select_one(".postbody > [align=center] img")
        img = img.get("src") if img else f"https:{img_alt.get("src")}" if img_alt else None

        torrent_name = soup.find("tr", class_="row6_to").text
        registered_date = soup.find("td", string=" Зареєстрований: ").find_next("td").contents[0][3:]
        size = soup.find("td", string=" Розмір: ").find_next("span").contents[0].replace("\xa0", "")
        thanks = soup.find("td", string=" Подякували: ").find_next("span").contents[0]
        rating = soup.find("span", attrs={"itemprop": "ratingValue"}).text
        torrent_url = soup.find("a", string="Завантажити")["href"]

        torrent_files = []
        torrent_files_table = soup.select(".files-wrap tr")

        # Extract folder name
        folder_name = torrent_files_table[0].select_one("td[align=left]").text.strip() if torrent_files_table[0].select_one("td[align=left]") else None

        # Iterate over the rows, skip the first row with folder name
        for row in torrent_files_table[1:]:
            td_elements = row.find_all('td')
            if len(td_elements) >= 3:  # Ensure there are enough columns in this row
                row_file_name = td_elements[1].text.strip() if td_elements[1].get('align') == 'left' else ""
                row_size = td_elements[2].text.strip().replace('\xa0', ' ') if td_elements[2].get('align') == 'right' else ""
                if row_file_name and row_size:  # Make sure file_name and size are not empty
                    torrent_file = TorrentFile(folder_name, row_file_name, row_size)
                    torrent_files.append(torrent_file)
        
        return Torrent(
            forum=forum,
            forum_url=forum_url,
            author=author,
            name = name,
            url = url,
            img = img,
            thumbnail=thumb,
            torrent_name = torrent_name.replace("\xa0", " ").replace("\n", "")[1:-1],
            date = registered_date,
            size = size,
            thanks = int(thanks),
            rating = rating,
            torrent_url = torrent_url,
            files = torrent_files
        )

    def download_torrent(self, torrent_url: str):
        return self.session.get(torrent_url).content
