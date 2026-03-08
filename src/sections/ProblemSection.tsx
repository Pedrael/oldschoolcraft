import { Box, Typography } from "@mui/material";
import { LayoutBlock } from "../components/LayoutBlock";
import content from "../content/text.json";
import { theme } from "../theme";

export function ProblemSection() {
  const { heading, intro, redHeading, outro } = content.problem;

  return (
    <>
      <LayoutBlock>
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
      <Box width="100%" bgcolor={theme.palette.background.default} py="1rem">
        <Typography
          variant="h3"
          component="h3"
          color={theme.palette.error.main}
          textAlign="center"
        >
          {outro}
        </Typography>
      </Box>
    </>
  );
}
