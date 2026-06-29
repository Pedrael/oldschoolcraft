import { Box, Typography } from "@mui/material";

type CarouselSlideProps = {
  title: string;
  paragraphs: string[];
  image?: string;
};

const CarouselSlide: React.FC<CarouselSlideProps> = ({
  title,
  paragraphs,
  image,
}) => {
  return (
    <Box display="flex" flexDirection="column" alignItems="center">
      <Typography variant="h2">{title}</Typography>
      <Box
        display="flex"
        flexDirection="column"
        gap={4}
        alignItems="start"
        mt={4}
        minHeight={"100vh"}
      >
        <Box
          display="flex"
          flexDirection="column"
          alignItems="start"
          gap={2}
          minHeight={"360px"}
        >
          {paragraphs.map((paragraph, i) => (
            <Typography key={i} variant="body1">
              {paragraph}
            </Typography>
          ))}
        </Box>

        {image && (
          <Box display="flex" justifyContent="center">
            <Box
              component="img"
              src={image}
              alt={title}
              sx={{
                width: "100%",
                height: "auto",
              }}
            />
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default CarouselSlide;
