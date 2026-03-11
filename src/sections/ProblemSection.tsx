import { Box, Typography } from "@mui/material";
import { LayoutBlock } from "../components/LayoutBlock";
import content from "../content/text.json";
import { theme } from "../theme";
import { BadgeBlock } from "../components/BadgeBlock";

export function ProblemSection() {
  const { heading, intro, redHeading, outro } = content.problem;

  const BEDROCK_TILES = [{ src: "/assets/blocks/bedrock.png", weight: 10 }];

  return (
    <>
      <LayoutBlock tiles={BEDROCK_TILES} tileDim={0.8} tileSize={64}>
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
      <BadgeBlock background={theme.palette.background.contrast}>
        <Typography
          variant="h3"
          component="h3"
          color={theme.palette.error.main}
          textAlign="center"
        >
          {outro}
        </Typography>
      </BadgeBlock>
    </>
  );
}
