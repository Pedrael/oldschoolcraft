import { Box, Typography } from "@mui/material";
import { LayoutBlock } from "../components/LayoutBlock";
import { Carousel } from "../components/Carousel";
import content from "../content/text.json";
import { palette as p } from "../theme";
import { useState } from "react";
import CarouselSlide from "../components/CarouselSlide";

export function FeaturesSection() {
  const { main, slides } = content.features;
  const [colorSchemeIndex, setColorSchemendex] = useState<number>(0);

  const colorSchemeHash = [
    {
      bg: p.magic.dark,
    },
    {
      bg: p.retro.dark,
    },
    {
      bg: p.background.default,
    },
  ];

  const slidesElements = [
    <CarouselSlide
      key={1}
      title={slides[0].title}
      paragraphs={slides[0].paragraphs}
      image={slides[0].image}
    />,
    <CarouselSlide
      key={2}
      title={slides[1].title}
      paragraphs={slides[1].paragraphs}
      image={slides[1].image}
    />,
    <CarouselSlide
      key={3}
      title={slides[2].title}
      paragraphs={slides[2].paragraphs}
      image={slides[2].image}
    />,
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
