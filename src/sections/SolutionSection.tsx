import { Box, Typography } from "@mui/material";
import { LayoutBlock } from "../components/LayoutBlock";
import content from "../content/text.json";
import { theme } from "../theme";

export function SolutionSection() {
  const { heading, intro, redHeading, motto, outro } = content.solution;

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
      <Box
        width="100%"
        display="flex"
        flexDirection="column"
        alignItems="center"
        bgcolor={theme.palette.success.dark}
        py="1rem"
      >
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
      </Box>
    </>
  );
}
