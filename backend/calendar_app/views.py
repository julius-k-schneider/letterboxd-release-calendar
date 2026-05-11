from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import LetterboxdNotFound, letterboxd, tmdb


class CalendarView(APIView):
    def post(self, request):
        username = (request.data.get("username") or "").strip()
        country = (request.data.get("country") or "").strip().upper()

        if not username or len(country) != 2:
            return Response(
                {"detail": "username und country (ISO-3166-1 alpha-2) erforderlich"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            items = letterboxd.fetch_watchlist(username)
        except LetterboxdNotFound as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response(
                {"detail": f"Watchlist konnte nicht geladen werden: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        movies = tmdb.resolve_and_fetch_many(items)

        def _serialize(movie, release):
            poster = movie.get("poster_path")
            return {
                "tmdb_id": movie["tmdb_id"],
                "title": movie["title"],
                "overview": movie.get("overview", ""),
                "poster_url": f"https://image.tmdb.org/t/p/w342{poster}" if poster else None,
                "release_date": release.isoformat() if release else None,
                "letterboxd_url": (
                    f"https://letterboxd.com/film/{movie['slug']}/"
                    if movie.get("slug")
                    else None
                ),
            }

        dated: list[dict] = []
        undated: list[dict] = []
        for movie in movies:
            release = tmdb.filter_upcoming_theatrical(movie, country)
            if release:
                dated.append(_serialize(movie, release))
                continue
            if tmdb.has_country_theatrical(movie, country):
                continue  # already released in this country
            if tmdb.is_available_at_home(movie):
                continue  # already on streaming / disc / TV somewhere
            undated.append(_serialize(movie, None))

        dated.sort(key=lambda x: x["release_date"])
        undated.sort(key=lambda x: x["title"].lower())

        return Response(
            {
                "count": len(dated),
                "movies": dated,
                "undated_count": len(undated),
                "undated_movies": undated,
            }
        )
