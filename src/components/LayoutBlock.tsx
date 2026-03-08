import { Box, type BoxProps } from "@mui/material";
import type { TileOption } from "../util/bg-generator";
import { TileBackground } from "../util/bg-generator";
import { theme } from "../theme";

export interface LayoutBlockProps extends Omit<BoxProps, "component"> {
  component?: BoxProps["component"];
  /** If provided, renders a TileBackground instead of a solid bg color */
  tiles?: TileOption[];
  /** Darkness overlay for the tile background (0–1). Default 0. */
  tileDim?: number;
  /** Tile size in px. Default 32. */
  tileSize?: number;
  background?: string;
}

export function LayoutBlock({
  children,
  sx,
  component = "section",
  tiles,
  background = theme.palette.background.default,
  tileDim = 0,
  tileSize = 32,
  ...rest
}: LayoutBlockProps) {
  return (
    <Box
      component={component}
      sx={{
        position: "relative",
        width: "100%",
        boxSizing: "border-box",
        backgroundColor: tiles ? "transparent" : background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        pt: "5rem",
        px: "10rem",
        ...sx,
      }}
      {...rest}
    >
      {tiles ? (
        <TileBackground tiles={tiles} tileSize={tileSize} dim={tileDim} />
      ) : null}
      <Box
        sx={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "100%",
          maxWidth: "1024px",
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
