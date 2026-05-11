export interface Movie {
  tmdb_id: number;
  title: string;
  overview: string;
  poster_url: string | null;
  release_date: string | null;
  letterboxd_url: string | null;
}

export interface CalendarResponse {
  count: number;
  movies: Movie[];
  undated_count: number;
  undated_movies: Movie[];
}

export async function fetchCalendar(
  username: string,
  country: string,
): Promise<CalendarResponse> {
  const response = await fetch("/api/calendar/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, country }),
  });
  if (!response.ok) {
    let detail = `Fehler ${response.status}`;
    try {
      const body = await response.json();
      if (body.detail) detail = body.detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return response.json();
}
