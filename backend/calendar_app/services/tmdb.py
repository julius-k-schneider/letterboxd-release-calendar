from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import requests
from django.conf import settings
from django.utils import timezone

from ..models import TMDBMovieCache
from . import TMDB_TTL

BASE_URL = "https://api.themoviedb.org/3"
# TMDB release types
TYPE_PREMIERE = 1
TYPE_THEATRICAL_LIMITED = 2
TYPE_THEATRICAL = 3
TYPE_DIGITAL = 4
TYPE_PHYSICAL = 5
TYPE_TV = 6
HOME_TYPES = {TYPE_DIGITAL, TYPE_PHYSICAL, TYPE_TV}
THEATRICAL_TYPES = {TYPE_THEATRICAL_LIMITED, TYPE_THEATRICAL}
# Films released in cinemas anywhere more than this many months ago are treated
# as "the distribution train has left" — they won't be picked up for a fresh
# theatrical run in a new country. Recent foreign releases still count as TBA.
STALE_THEATRICAL_MONTHS = 18
SESSION = requests.Session()
TIMEOUT = 10


def _params(extra: dict | None = None) -> dict:
    params = {"api_key": settings.TMDB_API_KEY}
    if extra:
        params.update(extra)
    return params


def _http_search_movie(title: str, year: int | None) -> int | None:
    params = {"query": title, "include_adult": "false"}
    if year:
        params["year"] = str(year)
    r = SESSION.get(f"{BASE_URL}/search/movie", params=_params(params), timeout=TIMEOUT)
    if r.status_code != 200:
        return None
    results = r.json().get("results") or []
    return results[0]["id"] if results else None


def _http_fetch_movie(tmdb_id: int) -> dict | None:
    r = SESSION.get(
        f"{BASE_URL}/movie/{tmdb_id}",
        params=_params({"append_to_response": "release_dates"}),
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        "tmdb_id": data["id"],
        "title": data.get("title") or data.get("original_title") or "",
        "poster_path": data.get("poster_path"),
        "overview": data.get("overview") or "",
        "release_dates": data.get("release_dates") or {"results": []},
    }


def _http_resolve(item: dict) -> dict | None:
    """Pure-HTTP worker: resolves a Letterboxd item to a fresh TMDB movie dict.

    Runs in worker threads. Must NOT touch the Django DB."""
    tmdb_id = item.get("tmdb_id")
    if not tmdb_id:
        tmdb_id = _http_search_movie(item["title"], item.get("year"))
    if not tmdb_id:
        return None
    movie = _http_fetch_movie(int(tmdb_id))
    if not movie:
        return None
    movie["slug"] = item.get("slug")
    return movie


def resolve_and_fetch_many(items: list[dict]) -> list[dict]:
    """Resolve a watchlist to TMDB movies, using cache where possible.

    1. Main thread: split items into cache hits vs misses.
    2. Worker threads: HTTP-fetch the misses (no DB access).
    3. Main thread: persist fresh fetches to the cache (serial).
    """
    cutoff = timezone.now() - TMDB_TTL

    hits: list[dict] = []
    misses: list[dict] = []
    for item in items:
        tmdb_id = item.get("tmdb_id")
        cached = None
        if tmdb_id:
            cached = TMDBMovieCache.objects.filter(
                tmdb_id=int(tmdb_id), fetched_at__gt=cutoff
            ).first()
        if cached:
            hits.append(
                {
                    "tmdb_id": cached.tmdb_id,
                    "title": cached.title,
                    "poster_path": cached.poster_path,
                    "overview": cached.overview,
                    "release_dates": cached.release_dates,
                    "slug": item.get("slug"),
                }
            )
        else:
            misses.append(item)

    fresh: list[dict] = []
    if misses:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for movie in pool.map(_http_resolve, misses):
                if movie:
                    fresh.append(movie)

    for movie in fresh:
        TMDBMovieCache.objects.update_or_create(
            tmdb_id=movie["tmdb_id"],
            defaults={
                "title": movie["title"],
                "poster_path": movie["poster_path"],
                "overview": movie["overview"],
                "release_dates": movie["release_dates"],
            },
        )

    return hits + fresh


def has_country_theatrical(movie: dict, country: str) -> bool:
    """True if movie has ANY theatrical release date in country (past or future)."""
    country = country.upper()
    for entry in (movie.get("release_dates") or {}).get("results", []):
        if entry.get("iso_3166_1", "").upper() != country:
            continue
        for rd in entry.get("release_dates", []):
            if rd.get("type") == TYPE_THEATRICAL and rd.get("release_date"):
                return True
    return False


def has_stale_theatrical_anywhere(movie: dict) -> bool:
    """True if the movie had a theatrical release anywhere more than
    STALE_THEATRICAL_MONTHS ago. Used to drop films from 'TBA' that have
    long been out in cinemas elsewhere — they won't get a fresh release
    in a new country at this point.
    """
    today = timezone.now().date()
    cutoff = today - timedelta(days=STALE_THEATRICAL_MONTHS * 30)
    for entry in (movie.get("release_dates") or {}).get("results", []):
        for rd in entry.get("release_dates", []):
            if rd.get("type") not in THEATRICAL_TYPES:
                continue
            raw = rd.get("release_date")
            if not raw:
                continue
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
            except ValueError:
                continue
            if parsed < cutoff:
                return True
    return False


def is_available_at_home(movie: dict) -> bool:
    """True if the movie has a past digital, physical, or TV release anywhere.

    Used to filter out films that already exist for home viewing (Netflix,
    Apple TV, Blu-ray, …) from the 'TBA' bucket. A past theatrical run in
    another country does NOT count — the user might still be waiting for the
    local cinema release.
    """
    today = timezone.now().date()
    for entry in (movie.get("release_dates") or {}).get("results", []):
        for rd in entry.get("release_dates", []):
            if rd.get("type") not in HOME_TYPES:
                continue
            raw = rd.get("release_date")
            if not raw:
                continue
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
            except ValueError:
                continue
            if parsed <= today:
                return True
    return False


def filter_upcoming_theatrical(movie: dict, country: str) -> date | None:
    today = timezone.now().date()
    country = country.upper()
    for entry in (movie.get("release_dates") or {}).get("results", []):
        if entry.get("iso_3166_1", "").upper() != country:
            continue
        candidate: date | None = None
        for rd in entry.get("release_dates", []):
            if rd.get("type") != TYPE_THEATRICAL:
                continue
            raw = rd.get("release_date")
            if not raw:
                continue
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
            except ValueError:
                continue
            if parsed <= today:
                continue
            if candidate is None or parsed < candidate:
                candidate = parsed
        return candidate
    return None
