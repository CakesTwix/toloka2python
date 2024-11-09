import requests
import os
import json
import logging
import re

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from datetime import datetime
from toloka2python.models.torrent import TorrentElement, Torrent, TorrentFile
from toloka2python.account import get_account_info

# Set Logging
logging.basicConfig(level=logging.DEBUG)


class Toloka:
    """Class for interacting with the torrent tracker Toloka"""

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    toloka_url = "https://toloka.to"
    cookie_file = "cookie.txt"
    max_login_attempts = 2  # Limit to prevent infinite login attempts

    def __init__(self, username: str, password: str, ssl="on", file: str = None):
        self.username = username
        self.password = password
        self.ssl = ssl
        self.file = file or self.cookie_file
        self.session = requests.Session()
        self.session.headers = self.headers
        self.login_attempts = 0

        self.login()

    def login(self):
        """Handle login and session management."""
        if not os.path.exists(self.file):
            logging.info("No cookie file found. Logging in.")
            self.perform_login()
        else:
            logging.info("Loading cookies from file.")
            if not self.load_cookies():
                logging.info("Cookie loading failed or expired, re-logging in.")
                self.perform_login()

    def perform_login(self):
        """Perform login to the site and save cookies."""
        self.login_attempts += 1
        try:
            response = self.session.post(
                f"{self.toloka_url}/login.php",
                {
                    "username": self.username,
                    "password": self.password,
                    "autologin": "on",
                    "ssl": self.ssl,
                    "login": "Вхід",
                },
            )
            response.raise_for_status()  # Check if the request was successful
            if self.validate_cookies():
                self.save_cookies()
                self.login_attempts = 0  # Reset login attempts after successful login
            else:
                if self.login_attempts < self.max_login_attempts:
                    logging.info("Initial cookie validation failed, trying again.")
                    os.remove(self.file)
                    self.session.cookies.clear()  # Clear session cookies before retry
                    self.perform_login()  # Retry login
                else:
                    logging.error("Maximum login attempts reached, raising exception.")
                    raise Exception("Failed to validate cookies after maximum retries.")
        except RequestException as e:
            logging.error(f"Failed to login: {e}")
            raise

    def load_cookies(self):
        """Load cookies from a local file and check if they are still valid."""
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                self.session.cookies.update(requests.utils.cookiejar_from_dict(cookies))
            return self.validate_cookies()
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error loading cookies: {e}")
            return False

    def validate_cookies(self):
        """Validate the cookies by checking if a protected page can be accessed."""
        check_url = f"{self.toloka_url}/f50"
        response = self.session.get(check_url)
        if "login.php?redirect=viewforum.php" in response.url:
            logging.info("Cookies are invalid or expired.")
            return False
        logging.info("Cookies are valid.")
        return True

    def save_cookies(self):
        """Save cookies to a local file."""
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)
        except IOError as e:
            logging.error(f"Failed to save cookies: {e}")

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
                    date=output_date,
                )
            )
        return torrent_list

    def searchv2(self, nm):
        """Пошук торрентів за запитом в API"""
        result = self.session.get(f"{self.toloka_url}/api.php?search={nm}")
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
                date="",
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
        cleaned_content = re.sub(r"[\n\t]+", "", content)
        soup = BeautifulSoup(cleaned_content, "html.parser")

        description = ""
        try:
            # TBD baseline for description of quality and content
            # format somehow?
            start_text = "Відео:"
            end_text = "MediaInfo"

            # Extract entire text from HTML
            text = soup.get_text()

            # Find start and end index
            start_idx = text.find(start_text)
            end_idx = text.find(end_text, start_idx)

            # Extract the relevant part
            data = text[start_idx:end_idx].strip()

            # Replace multiple whitespaces with a single space
            description = " ".join(data.split())
        except Exception as e:
            description = e

        name = soup.find("a", class_="maintitle").text
        url = soup.find("a", class_="maintitle")["href"].replace("/", "")
        forum = soup.select_one("td[class='nav'] h2:nth-of-type(2) a").text
        forum_url = soup.select_one("td[class='nav'] h2:nth-of-type(2) a")[
            "href"
        ].replace("f", "tracker.php?f=")

        author = ""
        try:
            author = soup.select_one("td.row1 span.name b a").text
        except Exception as e:
            author = "Anonymous"
        thumb = soup.select_one("[rel=image_src]")["href"]
        img = soup.find("img", attrs={"alt": name})
        img_alt = soup.select_one(".postbody > [align=center] img")
        img = (
            img.get("src")
            if img
            else f"https:{img_alt.get('src')}" if img_alt else None
        )

        torrent_name = soup.find("tr", class_="row6_to").text
        registered_date = (
            soup.find("td", string=" Зареєстрований: ").find_next("td").contents[0][3:]
        )
        size = (
            soup.find("td", string=" Розмір: ")
            .find_next("span")
            .contents[0]
            .replace("\xa0", "")
        )
        thanks = soup.find("td", string=" Подякували: ").find_next("span").contents[0]
        rating = soup.find("span", attrs={"itemprop": "ratingValue"}).text
        torrent_url = soup.find("a", string="Завантажити")["href"]

        torrent_files = []
        torrent_files_table = soup.select(".files-wrap tr")

        # Extract folder name
        folder_name = (
            torrent_files_table[0].select_one("td[align=left]").text.strip()
            if torrent_files_table[0].select_one("td[align=left]")
            else None
        )

        # Iterate over the rows, skip the first row with folder name
        for row in torrent_files_table[1:]:
            td_elements = row.find_all("td")
            if len(td_elements) >= 3:  # Ensure there are enough columns in this row
                row_file_name = (
                    td_elements[1].text.strip()
                    if td_elements[1].get("align") == "left"
                    else ""
                )
                row_size = (
                    td_elements[2].text.strip().replace("\xa0", " ")
                    if td_elements[2].get("align") == "right"
                    else ""
                )
                if (
                    row_file_name and row_size
                ):  # Make sure file_name and size are not empty
                    torrent_file = TorrentFile(folder_name, row_file_name, row_size)
                    torrent_files.append(torrent_file)

        return Torrent(
            forum=forum,
            forum_url=forum_url,
            author=author,
            name=name,
            url=url,
            img=img,
            thumbnail=thumb,
            torrent_name=torrent_name.replace("\xa0", " ").replace("\n", "")[1:-1],
            date=registered_date,
            size=size,
            thanks=int(thanks),
            rating=rating,
            torrent_url=torrent_url,
            files=torrent_files,
            description=description,
        )

    def download_torrent(self, torrent_url: str):
        return self.session.get(torrent_url).content
