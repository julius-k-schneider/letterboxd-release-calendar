from __future__ import annotations

from typing import Any

from django.utils import timezone

from ..models import WatchlistCache
from . import WATCHLIST_TTL, LetterboxdNotFound


def _normalize(raw: Any) -> tuple[list[dict], int]:
    """Return (items, count) tuple from a letterboxdpy watchlist payload.

    Known shapes:
      * {"count": int, "data": {slug: {"name": ..., ...}, ...}}
      * {"count": int, "data": [{"slug": ..., "name": ...}, ...]}
      * [{"slug": ..., "name": ..., "year": ...}, ...]
    """
    count = 0
    if isinstance(raw, dict):
        count = int(raw.get("count") or 0)
        data = raw.get("data", {})
    else:
        data = raw

    items: list[dict] = []
    if isinstance(data, dict):
        for slug, info in data.items():
            info = info or {}
            items.append(
                {
                    "slug": info.get("slug") or slug,
                    "title": info.get("name") or info.get("title") or slug,
                    "year": info.get("year"),
                }
            )
    elif isinstance(data, list):
        for info in data:
            info = info or {}
            items.append(
                {
                    "slug": info.get("slug"),
                    "title": info.get("name") or info.get("title"),
                    "year": info.get("year"),
                }
            )
    items = [i for i in items if i.get("slug") and i.get("title")]
    if not count:
        count = len(items)
    return items, count


def _make_user(username: str):
    try:
        from letterboxdpy.user import User
    except ImportError as exc:
        raise RuntimeError("letterboxdpy ist nicht installiert") from exc
    try:
        return User(username)
    except Exception as exc:
        raise LetterboxdNotFound(f"User '{username}' nicht gefunden") from exc


def _remote_count(user) -> int | None:
    """Cheap call: only fetch the watchlist count, not the entries."""
    if hasattr(user, "get_watchlist_count"):
        try:
            value = user.get_watchlist_count()
            return int(value) if value is not None else None
        except Exception:
            return None
    return None


def _scrape(user) -> tuple[list[dict], int]:
    if hasattr(user, "get_watchlist"):
        raw = user.get_watchlist()
    elif hasattr(user, "watchlist"):
        attr = user.watchlist
        raw = attr() if callable(attr) else attr
    else:
        raise RuntimeError("letterboxdpy User-Klasse hat keine Watchlist-Methode")
    return _normalize(raw)


def fetch_watchlist(username: str, force_refresh: bool = False) -> list[dict]:
    username = username.strip().lower()
    cached = WatchlistCache.objects.filter(username=username).first()
    user = _make_user(username)

    if cached and not force_refresh:
        remote = _remote_count(user)
        cutoff = timezone.now() - WATCHLIST_TTL
        # Cache-Hit, wenn Count gleich ODER (Count-Check fehlgeschlagen UND TTL noch gültig)
        if remote is not None:
            if remote == cached.count:
                return cached.items
        elif cached.fetched_at > cutoff:
            return cached.items

    items, count = _scrape(user)
    WatchlistCache.objects.update_or_create(
        username=username,
        defaults={"items": items, "count": count},
    )
    return items
