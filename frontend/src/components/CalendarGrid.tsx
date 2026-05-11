import { useMemo } from "react";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Box from "@mui/material/Box";
import { Movie } from "../api";
import { MovieCard } from "./MovieCard";

const monthFormatter = new Intl.DateTimeFormat("en-US", {
  month: "long",
  year: "numeric",
});

interface Group {
  key: string;
  label: string;
  movies: Movie[];
}

interface Props {
  movies: Movie[];
}

export function CalendarGrid({ movies }: Props) {
  const groups = useMemo<Group[]>(() => {
    const map = new Map<string, Group>();
    for (const movie of movies) {
      if (!movie.release_date) continue;
      const date = new Date(movie.release_date);
      const key = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}`;
      if (!map.has(key)) {
        map.set(key, { key, label: monthFormatter.format(date), movies: [] });
      }
      map.get(key)!.movies.push(movie);
    }
    return Array.from(map.values()).sort((a, b) => a.key.localeCompare(b.key));
  }, [movies]);

  return (
    <Stack spacing={6}>
      {groups.map((group) => (
        <Box key={group.key} component="section">
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="baseline"
            sx={{ mb: 2 }}
          >
            <Typography variant="h5" component="h2">
              {group.label}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {group.movies.length} {group.movies.length === 1 ? "film" : "films"}
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
            {group.movies.map((movie) => (
              <MovieCard key={movie.tmdb_id} movie={movie} />
            ))}
          </Box>
        </Box>
      ))}
    </Stack>
  );
}
