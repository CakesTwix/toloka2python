import logging

from bs4 import BeautifulSoup

from toloka2python.models.account import Account
from toloka2python.models.torrent import TorrentAccount


def get_account_info(html_text: str) -> Account:
    """Отримати інформацію про користувача з HTML-сторінки"""
    soup = BeautifulSoup(html_text, "html.parser")
    account_soup = soup.find_all("td", class_="bodyline")[1]

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
                    upload_torrent.find("span", class_="gen").text,      # Forum name
                    upload_torrent.find("a", class_="gen")["href"],      # Forum url
                    upload_torrent.find("a", class_="genmed").text,      # Torrent Name
                    upload_torrent.find("span", class_="seedmed").text,  # Seeders
                    upload_torrent.find("span", class_="leechmed").text, # Leechers
                    upload_torrent.find("a", class_="genmed")["href"],   # Url
                )
            )

    # logging.debug(torrent_profile_soup)

    # /u123456
    account_url = soup.find("a", string="Профіль")["href"]
    # images/avatars/19977720906228cba9378bf.png
    avatar = soup.find("span", class_="postdetails").find("img")["src"]
    online = True if account_soup.find("font", string="(в мережі)") else False
    email = communicate_soup[0].find_all("span", class_="gen")[1].text
    skype = communicate_soup[0].find_all("span", class_="gen")[1].text
    first_login = info_soup[0].find_all("span", class_="gen")[1].text
    last_login = info_soup[1].find_all("span", class_="gen")[1].text
    messages = info_soup[2].find_all("span", class_="gen")[1].text
    uploaded = torrent_profile_soup[1].find("span", class_="seed").find("b").text.replace("\xa0", " ")
    downloaded = torrent_profile_soup[2].find("span", class_="leech").find("b").text.replace("\xa0", " ")
    uploaded_now = torrent_profile_soup[1].find_all("span", class_="seed")[1].find("b").text.replace("\xa0", " ")
    downloaded_now = torrent_profile_soup[2].find_all("span", class_="leech")[1].find("b").text.replace("\xa0", " ")
    uploaded_yesterday = torrent_profile_soup[1].find_all("span", class_="seed")[2].find("b").text.replace("\xa0", " ")
    downloaded_yesterday = torrent_profile_soup[2].find_all("span", class_="leech")[2].find("b").text.replace("\xa0", " ")
    bonus_seeding = torrent_profile_soup[3].find_all("span", class_="gen")[1].text.replace("\xa0", " ")
    bonus_seeding_now = torrent_profile_soup[3].find_all("span", class_="gen")[3].text.replace("\xa0", " ")
    bonus_seeding_yesterday = torrent_profile_soup[3].find_all("span", class_="gen")[4].text.replace("\xa0", " ")
    ul_dl_rating = torrent_profile_soup[4].find_all("span", class_="gen")[1].text.replace("\xa0", " ")
    ul_dl_rating_without_bonus = torrent_profile_soup[4].find_all("span", class_="gen")[1].text.replace("\xa0", " ")
    releases = torrent_profile_soup[6].find("span", class_="seed").text 
    thanks = torrent_profile_soup[7].find_all("span", class_="gen")[1].text if 1 < len(torrent_profile_soup[7].find_all("span", class_="gen")) else None
    logging.debug(thanks)
    if thanks != None:
        max_download = torrent_profile_soup[8].find("span", class_="leech").find("b").text.replace("\xa0", " ")
        max_upload = torrent_profile_soup[8].find("span", class_="seed").find("b").text.replace("\xa0", " ")
        passkey = torrent_profile_soup[9].find_all("span", class_="gen")[1].text
    else:
        max_download = torrent_profile_soup[7].find("span", class_="leech").find("b").text.replace("\xa0", " ")
        max_upload = torrent_profile_soup[7].find("span", class_="seed").find("b").text.replace("\xa0", " ")
        passkey = None

    return Account(
        account_url,
        avatar,
        online,
        email,
        skype,
        first_login,
        last_login,
        int(messages),
        uploaded,
        downloaded,
        uploaded_now,
        downloaded_now,
        uploaded_yesterday,
        downloaded_yesterday,
        bonus_seeding,
        bonus_seeding_now,
        bonus_seeding_yesterday,
        ul_dl_rating,                # TODO: Fix ul_dl_rating
        ul_dl_rating_without_bonus,  # TODO: Fix ul_dl_rating
        int(releases),
        int(0 if thanks is None else thanks),
        max_download,
        max_upload,
        passkey,
        upload_torrent_list,
        download_torrent_list,
    )