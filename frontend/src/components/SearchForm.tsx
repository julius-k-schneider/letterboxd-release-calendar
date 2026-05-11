import { FormEvent, useState } from "react";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import { COUNTRIES } from "../countries";

function detectCountry(): string {
  const candidates: string[] = [];
  if (typeof navigator !== "undefined") {
    if (navigator.languages) candidates.push(...navigator.languages);
    if (navigator.language) candidates.push(navigator.language);
  }
  const supported = new Set(COUNTRIES.map((c) => c.code));
  for (const tag of candidates) {
    const region = tag.split("-")[1]?.toUpperCase();
    if (region && supported.has(region)) return region;
  }
  return "DE";
}

interface Props {
  loading: boolean;
  onSubmit: (username: string, country: string) => void;
}

export function SearchForm({ loading, onSubmit }: Props) {
  const [username, setUsername] = useState("");
  const [country, setCountry] = useState(detectCountry);

  const handle = (event: FormEvent) => {
    event.preventDefault();
    if (!username.trim()) return;
    onSubmit(username.trim(), country);
  };

  return (
    <form onSubmit={handle}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={2}
        alignItems={{ xs: "stretch", sm: "flex-start" }}
      >
        <TextField
          label="Letterboxd username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="off"
          spellCheck={false}
          fullWidth
          sx={{ flex: 2 }}
        />
        <TextField
          select
          label="Region"
          value={country}
          onChange={(event) => setCountry(event.target.value)}
          sx={{ flex: 1, minWidth: 180 }}
          SelectProps={{
            MenuProps: { PaperProps: { sx: { maxHeight: 360 } } },
          }}
        >
          {COUNTRIES.map((c) => (
            <MenuItem key={c.code} value={c.code}>
              {c.name}
            </MenuItem>
          ))}
        </TextField>
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={loading || !username.trim()}
          sx={{ height: 56, minWidth: 140 }}
        >
          {loading ? "Loading…" : "Load calendar"}
        </Button>
      </Stack>
    </form>
  );
}
