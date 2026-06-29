import { useCallback, useEffect, useState } from "react";
import { Box, IconButton } from "@mui/material";
import ChevronLeft from "@mui/icons-material/ChevronLeft";
import ChevronRight from "@mui/icons-material/ChevronRight";
import { theme } from "../theme";

export interface CarouselProps {
  slides: React.ReactNode[];
  slideTimeout?: number;
  initialIndex?: number;
  showDots?: boolean;
  showArrows?: boolean;
  fadeDuration?: number;
  callback: (index: number) => void;
}

export function Carousel({
  slides,
  initialIndex = 0,
  slideTimeout = 5000,
  showDots = true,
  showArrows = true,
  fadeDuration = 300,
  callback,
}: CarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [isFading, setIsFading] = useState(false);

  const slide = slides[currentIndex];
  const color = theme.palette.text.primary;

  const changeSlide = useCallback(
    (nextIndex: number) => {
      if (!slides.length || isFading) return;

      setIsFading(true);

      window.setTimeout(() => {
        callback(nextIndex);
        setCurrentIndex(nextIndex);
        setIsFading(false);
      }, fadeDuration);
    },
    [slides.length, isFading, fadeDuration, callback],
  );

  const goPrev = useCallback(() => {
    const nextIndex = currentIndex <= 0 ? slides.length - 1 : currentIndex - 1;
    changeSlide(nextIndex);
  }, [currentIndex, slides.length, changeSlide]);

  const goNext = useCallback(() => {
    const nextIndex = currentIndex >= slides.length - 1 ? 0 : currentIndex + 1;
    changeSlide(nextIndex);
  }, [currentIndex, slides.length, changeSlide]);

  useEffect(() => {
    if (!slideTimeout || slideTimeout <= 0 || slides.length <= 1) return;

    const intervalId = window.setInterval(() => {
      goNext();
    }, slideTimeout);

    return () => window.clearInterval(intervalId);
  }, [slideTimeout, slides.length, goNext]);

  // return the current index to the parent component on mount
  useEffect(() => {
    callback(currentIndex);
  }, [currentIndex, callback]);

  if (!slide) return null;

  return (
    <Box width="100%">
      <Box
        width="100%"
        boxSizing="border-box"
        color={color}
        display="flex"
        flexDirection="column"
        alignItems="center"
        py={4}
        px={2}
      >
        {slide}

        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            mt: 3,
          }}
        >
          {showArrows ? (
            <>
              <IconButton
                onClick={goPrev}
                aria-label="Previous slide"
                sx={{ color: "inherit" }}
              >
                <ChevronLeft />
              </IconButton>
              <Box sx={{ width: 24 }} />
            </>
          ) : null}

          {showDots
            ? slides.map((_, i) => (
                <Box
                  key={i}
                  onClick={() => changeSlide(i)}
                  sx={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    bgcolor: i === currentIndex ? color : "transparent",
                    border: `2px solid ${color}`,
                    cursor: "pointer",
                    opacity: i === currentIndex ? 1 : 0.5,
                  }}
                  aria-label={`Go to slide ${i + 1}`}
                />
              ))
            : null}

          {showArrows ? (
            <>
              <Box sx={{ width: 24 }} />
              <IconButton
                onClick={goNext}
                aria-label="Next slide"
                sx={{ color: "inherit" }}
              >
                <ChevronRight />
              </IconButton>
            </>
          ) : null}
        </Box>
      </Box>
    </Box>
  );
}
