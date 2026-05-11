from datetime import timedelta

WATCHLIST_TTL = timedelta(hours=6)
TMDB_TTL = timedelta(hours=24)


class LetterboxdNotFound(Exception):
    pass
