import { createTheme } from "@mui/material/styles";

const BG = "#15181d";
const SURFACE = "#1c2026";
const SURFACE_HOVER = "#222831";
const BORDER = "#2a2f37";
const TEXT_PRIMARY = "#e8eaed";
const TEXT_SECONDARY = "#9aa0a6";
const ACCENT = "#7aa2f7";

export const theme = createTheme({
  palette: {
    mode: "dark",
    background: {
      default: BG,
      paper: SURFACE,
    },
    primary: {
      main: ACCENT,
    },
    text: {
      primary: TEXT_PRIMARY,
      secondary: TEXT_SECONDARY,
    },
    divider: BORDER,
  },
  typography: {
    fontFamily:
      '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: { fontWeight: 600, letterSpacing: "-0.02em" },
    h2: { fontWeight: 600, letterSpacing: "-0.01em" },
    h3: { fontWeight: 500, letterSpacing: "-0.005em" },
    h4: { fontWeight: 500 },
    h5: { fontWeight: 500 },
    h6: { fontWeight: 500 },
    button: { textTransform: "none", fontWeight: 500 },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: BG,
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          borderRadius: 8,
          paddingInline: 20,
          paddingBlock: 10,
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: SURFACE,
          "& fieldset": { borderColor: BORDER },
          "&:hover fieldset": { borderColor: "#3a414b !important" },
          "&.Mui-focused fieldset": { borderColor: `${ACCENT} !important` },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: SURFACE,
          border: `1px solid ${BORDER}`,
          transition: "background-color 0.2s ease, border-color 0.2s ease",
          "&:hover": {
            backgroundColor: SURFACE_HOVER,
            borderColor: "#363c45",
          },
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: BORDER,
        },
      },
    },
  },
});
