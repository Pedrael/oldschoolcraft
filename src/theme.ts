import {
  createTheme,
  responsiveFontSizes,
  type ThemeOptions,
} from "@mui/material/styles";

const paletteWithCustom = {
  mode: "dark" as const,
  background: {
    default: "#121214",
    paper: "#1b1b20",
    contrast: "#000000",
  },
  primary: {
    main: "#00AA00",
    dark: "#3e883e",
    light: "#55FF55",
    contrastText: "#000000",
  },
  secondary: {
    main: "#00aaff",
    contrastText: "#121214",
  },
  text: {
    primary: "#e5e5e5",
    secondary: "#a0a0b0",
  },
  success: {
    main: "#55ff55",
    light: "#88ff88",
    dark: "#3e883e",
  },
  warning: {
    main: "#e0b84f",
    light: "#ffd088",
    dark: "#b78a3e",
  },
  error: {
    main: "#ff5555",
    light: "#ff8888",
    dark: "#b73e3e",
  },
  techno: {
    main: "#00aaff",
    dark: "#00aaff",
    light: "#00ffd0",
  },
  retro: {
    main: "#e0b84f",
    dark: "#c97a1c",
    light: "#ffd088",
  },
  magic: {
    main: "#8b5cf6",
    dark: "#5c2a8a",
    light: "#b388ff",
  },
  green: {
    1: "#1e401e",
    2: "#2f5f2f",
    3: "#3e883e",
    4: "#4faa4f",
    5: "#55ff55",
    6: "#72ff72",
    7: "#88ff88",
    8: "#a0ffa0",
    9: "#c8ffc8",
  },
};

export const palette = paletteWithCustom;

const baseTheme = createTheme({
  palette: paletteWithCustom as ThemeOptions["palette"],
  typography: {
    fontFamily: '"PixelOperator", system-ui, sans-serif',
    body1: { fontSize: "1.5rem", textIndent: "1.5rem" },
    body2: { fontSize: "1rem", textIndent: "1.5rem" },
    h1: {
      fontFamily: '"Minecraft", sans-serif',
      fontSize: "4rem",
      textAlign: "center",
    },
    h2: {
      fontFamily: '"Minecraft", sans-serif',
      fontSize: "3rem",
      textAlign: "center",
    },
    h3: {
      fontFamily: '"Minecraft", sans-serif',
      fontSize: "2.5rem",
      textAlign: "center",
    },
    h4: {
      fontFamily: '"Minecraft", sans-serif',
      fontSize: "2rem",
      textAlign: "center",
    },
    h5: { fontFamily: '"Minecraft", sans-serif' },
    h6: { fontFamily: '"Minecraft", sans-serif' },
    button: { fontFamily: '"Minecraft", sans-serif' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          fontFamily: '"Minecraft", sans-serif',
        },
      },
    },
  },
});

export const theme = responsiveFontSizes(baseTheme);
