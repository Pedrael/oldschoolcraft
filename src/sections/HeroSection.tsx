import { Box, Typography } from "@mui/material";
import content from "../content/text.json";
import { palette as p } from "../theme";

export function HeroSection() {
  const textColor = p.retro.main;

  return (
    <Box
      component="section"
      sx={{
        position: "relative",
        width: "100%",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundImage: "url(/assets/hero-bg.png)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        py: 3,
        px: 2,
      }}
    >
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          backgroundColor: "black",
          opacity: 0.66,
          zIndex: 0,
        }}
      />
      <Box
        sx={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          color: textColor,
        }}
      >
        <Typography component="h1" variant="h1">
          {content.hero.title}
        </Typography>
        {content.hero.subtitle ? (
          <Typography component="h3" variant="h3">
            {content.hero.subtitle}
          </Typography>
        ) : null}
      </Box>
    </Box>
  );
}
