import { Box } from "@mui/material";
import { HeroSection } from "./sections/HeroSection";
import { ProblemSection } from "./sections/ProblemSection";
import { SolutionSection } from "./sections/SolutionSection";
import { FeaturesSection } from "./sections/FeaturesSection";
import { JoinSection } from "./sections/JoinSection";

function App() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <HeroSection />
      <ProblemSection />
      <SolutionSection />
      <FeaturesSection />
      <JoinSection />
    </Box>
  );
}

export default App;
