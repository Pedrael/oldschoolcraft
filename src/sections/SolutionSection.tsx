import { Box, Typography } from "@mui/material";
import { LayoutBlock } from "../components/LayoutBlock";
import content from "../content/text.json";
import { theme, palette as p } from "../theme";
import { BadgeBlock } from "../components/BadgeBlock";

export function SolutionSection() {
  const { heading, intro, redHeading, motto, outro } = content.solution;

  const COBBLESTONE_TILES = [
    { src: "/assets/blocks/cobblestone.png", weight: 6.5 },
    { src: "/assets/blocks/cobblestone_mossy.png", weight: 3.5 },
  ];

  return (
    <>
      <LayoutBlock tiles={COBBLESTONE_TILES} tileDim={0.6} tileSize={64}>
        <Typography component="h2" variant="h2" sx={{ mb: 2 }}>
          {heading}
        </Typography>
        <Typography variant="body1">{intro}</Typography>
        <Box width="100%">
          <Box component="ul">
            {redHeading.map((line, i) => (
              <Typography key={i} component="li" variant="body1">
                {line}
              </Typography>
            ))}
          </Box>
        </Box>
      </LayoutBlock>
      <BadgeBlock background={p.green[1]}>
        <Typography
          variant="h3"
          component="h3"
          color={theme.palette.success.light}
          textAlign="center"
        >
          {motto[0]}
        </Typography>
        <Typography
          variant="h3"
          component="h3"
          color={theme.palette.success.light}
        >
          {motto[1]}
        </Typography>
        <Typography
          variant="h3"
          component="h3"
          color={theme.palette.success.light}
        >
          {outro}
        </Typography>
      </BadgeBlock>
    </>
  );
}
