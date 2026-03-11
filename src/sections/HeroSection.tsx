import { Box, Button, Typography } from "@mui/material";
import content from "../content/text.json";
import { palette as p } from "../theme";
import parse from "html-react-parser";

type HeroSectionProps = {
  onCTAClick: () => void;
};

export const HeroSection: React.FC<HeroSectionProps> = ({ onCTAClick }) => {
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
          gap: 16,
          color: textColor,
        }}
      >
        <Box display="flex" flexDirection="column" alignItems="center">
          <Typography component="h1" variant="h1">
            {content.hero.title}
          </Typography>
          {content.hero.subtitle ? (
            <Typography component="h3" variant="h3">
              {parse(content.hero.subtitle)}
            </Typography>
          ) : null}
        </Box>
        <Button
          type="submit"
          variant="contained"
          sx={{
            width: 300,
            maxWidth: "100%",
            backgroundColor: p.retro.main,
            borderRadius: 0,
            "&:hover": {
              background: p.retro.light,
            },
          }}
          onClick={onCTAClick}
        >
          Join Now
        </Button>
      </Box>
    </Box>
  );
};
