from dataclasses import dataclass


@dataclass
class TorrentElement:
    forum: str
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
    forum: str
    forum_url: str
    name: str
    seeders: int
    leechers: int
    url: str
