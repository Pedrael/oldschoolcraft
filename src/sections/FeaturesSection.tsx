import { Box, Typography } from "@mui/material";
import { LayoutBlock } from "../components/LayoutBlock";
import { Carousel } from "../components/Carousel";
import content from "../content/text.json";
import { palette as p } from "../theme";
import { useState } from "react";

export function FeaturesSection() {
  const { main, slides } = content.features;
  const [colorSchemeIndex, setColorSchemendex] = useState<number>(0);

  const colorSchemeHash = [
    {
      bg: p.magic.dark,
      h: p.magic.light,
      p: p.magic.main,
    },
    {
      bg: p.techno.dark,
      h: p.techno.light,
      p: p.techno.main,
    },
    {
      bg: p.retro.dark,
      h: p.retro.light,
      p: p.retro.main,
    },
  ];

  const slidesElements = [
    <Box key="1">
      <Typography component="h2" variant="h2">
        {slides[0].title}
      </Typography>
    </Box>,
    <Box key="2">
      <Typography component="h2" variant="h2">
        {slides[1].title}
      </Typography>
    </Box>,
    <Box key="3">
      <Typography component="h2" variant="h2">
        {slides[2].title}
      </Typography>
    </Box>,
  ];

  const handleSlideChange = (index: number) => {
    setColorSchemendex(index);
  };

  return (
    <LayoutBlock
      background={colorSchemeHash[colorSchemeIndex].bg}
      sx={{
        transition: "background-color 500ms ease",
      }}
    >
      <Typography
        component="h1"
        variant="h1"
        sx={{ mb: 2, textAlign: "center" }}
      >
        {main.heading}
      </Typography>
      <Typography
        variant="body1"
        sx={{ maxWidth: 560, textAlign: "center", mb: 4 }}
      >
        {main.body}
      </Typography>
      <Box sx={{ width: "100%" }}>
        <Carousel
          slides={slidesElements}
          showDots
          showArrows
          callback={handleSlideChange}
        />
      </Box>
    </LayoutBlock>
  );
}
