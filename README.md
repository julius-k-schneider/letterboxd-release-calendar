# Letterboxd Release Calendar

Webseite, die die Watchlist eines Letterboxd-Users scraped und daraus einen Release-Kalender der zukünftigen Kinostarts im gewählten Land erzeugt — via [TMDB](https://www.themoviedb.org/) API.

## Stack

- **Backend**: Django + Django REST Framework, SQLite, `letterboxdpy` zum Scrapen, `requests` für TMDB.
- **Frontend**: Vite + React + TypeScript, ohne Router, mit Proxy auf das Backend.
- **Caching**: Watchlist 6 h, TMDB-Filmdaten 24 h (in DB).

## Setup

### 1. Backend

```bash
# Im Repo-Root
python -m venv .venv
source .venv/bin/activate
pip install -e .

cp backend/.env.example backend/.env
# In backend/.env einen TMDB v3 API-Key eintragen (https://www.themoviedb.org/settings/api)

cd backend
python manage.py migrate
python manage.py runserver
# Läuft auf http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# Läuft auf http://localhost:5173 mit Proxy auf das Backend
```

### 3. Benutzung

Im Browser `http://localhost:5173` öffnen → Letterboxd-Username eingeben, Land wählen, „Kalender laden“.

## API

`POST /api/calendar/`

```json
{ "username": "deinusername", "country": "DE" }
```

Antwort:

```json
{
  "count": 12,
  "movies": [
    {
      "tmdb_id": 12345,
      "title": "Beispielfilm",
      "overview": "...",
      "poster_url": "https://image.tmdb.org/t/p/w342/abc.jpg",
      "release_date": "2026-06-12",
      "letterboxd_url": "https://letterboxd.com/film/beispielfilm/"
    }
  ]
}
```

Gefiltert wird auf Releases mit `type == 3` (Theatrical) im angefragten Land mit `release_date > heute`.
