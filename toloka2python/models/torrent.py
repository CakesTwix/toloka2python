from dataclasses import dataclass

@dataclass
class Torrent:
    """Датаклас, який містить інформацію про торрент"""
    name: str
    url: str
    img: str
    torrent_name: str
    registered_date: str
    size: str
    thanks: int
    rating: int
    torrent_url: str

@dataclass
class TorrentElement:
    """Датаклас, що містить інформацію про торрент зі списку торрентів під час пошуку"""
    forum: str
    forum_url: str
    url: str
    name: str
    author: str
    verify: bool
    download_link: str
    size: str
    status: str
    seeders: int
    leechers: int
    answers: int
    date: str


@dataclass
class TorrentAccount:
    """Датаклас, що містить інформацію про торрент зі списку торрентів з акаунта користувача"""
    forum: str
    forum_url: str
    name: str
    seeders: int
    leechers: int
    url: str
