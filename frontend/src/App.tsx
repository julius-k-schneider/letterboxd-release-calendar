import { useState } from "react";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Box from "@mui/material/Box";
import { CalendarGrid } from "./components/CalendarGrid";
import { MovieCard } from "./components/MovieCard";
import { SearchForm } from "./components/SearchForm";
import { Movie, fetchCalendar } from "./api";

export default function App() {
  const [movies, setMovies] = useState<Movie[] | null>(null);
  const [undated, setUndated] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<{ username: string; country: string } | null>(null);

  const handleSearch = async (username: string, country: string) => {
    setLoading(true);
    setError(null);
    setMovies(null);
    setUndated([]);
    setSubmitted({ username, country });
    try {
      const data = await fetchCalendar(username, country);
      setMovies(data.movies);
      setUndated(data.undated_movies ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const hasResults = (movies && movies.length > 0) || undated.length > 0;

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 5, md: 8 } }}>
      <Stack spacing={1} sx={{ mb: 5 }}>
        <Typography variant="h3" component="h1">
          Letterboxd Release Calendar
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 560, pt: 1 }}>
          Upcoming theatrical releases from your Letterboxd watchlist, filtered by country and
          ordered by date.
        </Typography>
      </Stack>

      <SearchForm loading={loading} onSubmit={handleSearch} />

      <Box sx={{ mt: 5 }}>
        {error && (
          <Alert severity="error" variant="outlined" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {loading && (
          <Stack direction="row" alignItems="center" spacing={2} sx={{ py: 2 }}>
            <CircularProgress size={18} thickness={4} />
            <Typography variant="body2" color="text.secondary">
              Loading watchlist and matching against TMDB…
            </Typography>
          </Stack>
        )}

        {movies && !loading && !hasResults && (
          <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
            No upcoming theatrical releases for {submitted?.username} in {submitted?.country}.
          </Typography>
        )}

        {movies && movies.length > 0 && <CalendarGrid movies={movies} />}

        {undated.length > 0 && (
          <Box component="section" sx={{ mt: movies && movies.length > 0 ? 8 : 0 }}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="baseline"
              sx={{ mb: 2 }}
            >
              <Typography variant="h5" component="h2">
                Release date TBA
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {undated.length} {undated.length === 1 ? "film" : "films"}
              </Typography>
            </Stack>
            <Divider sx={{ mb: 3 }} />
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: {
                  xs: "repeat(2, 1fr)",
                  sm: "repeat(3, 1fr)",
                  md: "repeat(4, 1fr)",
                  lg: "repeat(5, 1fr)",
                },
                gap: 2.5,
              }}
            >
              {undated.map((movie) => (
                <MovieCard key={movie.tmdb_id} movie={movie} />
              ))}
            </Box>
          </Box>
        )}
      </Box>
    </Container>
  );
}
