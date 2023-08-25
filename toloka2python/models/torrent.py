from dataclasses import dataclass


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
