import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardMedia from "@mui/material/CardMedia";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { Movie } from "../api";

const dateFormatter = new Intl.DateTimeFormat("en-US", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

interface Props {
  movie: Movie;
}

export function MovieCard({ movie }: Props) {
  const formatted = movie.release_date
    ? dateFormatter.format(new Date(movie.release_date))
    : "Release date TBA";

  const content = (
    <>
      {movie.poster_url ? (
        <CardMedia
          component="img"
          image={movie.poster_url}
          alt={movie.title}
          loading="lazy"
          sx={{ aspectRatio: "2 / 3", objectFit: "cover" }}
        />
      ) : (
        <Box
          sx={{
            aspectRatio: "2 / 3",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "text.secondary",
            backgroundColor: "background.default",
          }}
        >
          —
        </Box>
      )}
      <CardContent sx={{ pb: "16px !important" }}>
        <Typography
          variant="subtitle2"
          component="h3"
          sx={{ lineHeight: 1.3, mb: 0.5 }}
          title={movie.title}
        >
          {movie.title}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {formatted}
        </Typography>
      </CardContent>
    </>
  );

  return (
    <Card variant="outlined" sx={{ display: "flex", flexDirection: "column" }}>
      {movie.letterboxd_url ? (
        <CardActionArea
          href={movie.letterboxd_url}
          target="_blank"
          rel="noreferrer"
          sx={{ display: "flex", flexDirection: "column", alignItems: "stretch", height: "100%" }}
        >
          {content}
        </CardActionArea>
      ) : (
        content
      )}
    </Card>
  );
}
