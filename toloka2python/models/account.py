from dataclasses import dataclass
from toloka2python.models.torrent import TorrentAccount


@dataclass
class Account:
    id: str
    avatar: str
    online: bool
    email: str
    skype: str
    first_login: str
    last_login: str
    messages: int
    uploaded: str
    downloaded: str
    uploaded_now: str
    downloaded_now: str
    uploaded_yesterday: str
    downloaded_yesterday: str
    bonus_seeding: str
    bonus_seeding_now: str
    bonus_seeding_yesterday: str
    ul_dl_rating: float
    ul_dl_rating_without_bonus: float
    releases: int
    thanks: int
    max_download: str
    max_upload: str
    passkey: str
    upload_torrent: TorrentAccount
    download_torrent: TorrentAccount
