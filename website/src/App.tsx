import { Box } from "@mui/material";
import { HeroSection } from "./sections/HeroSection";
import { ProblemSection } from "./sections/ProblemSection";
import { SolutionSection } from "./sections/SolutionSection";
import { FeaturesSection } from "./sections/FeaturesSection";
import { JoinSection } from "./sections/JoinSection";
import { useRef } from "react";

function App() {
  const joinRef = useRef<HTMLDivElement>(null);

  const handleScrollToJoin = () => {
    joinRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };
  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <HeroSection onCTAClick={handleScrollToJoin} />
      <ProblemSection />
      <SolutionSection />
      <FeaturesSection />
      <JoinSection ref={joinRef} />
    </Box>
  );
}

export default App;
