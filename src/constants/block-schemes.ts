import type { BlockColorScheme } from "../types/layout";
import { palette as p } from "../theme";

export const BLOCK_SCHEMES: Record<string, BlockColorScheme> = {
  "neutral-1": {
    bg: p.background.default,
    h: p.text.primary,
    p: p.text.secondary,
  }, // neutral 1
  "neutral-2": {
    bg: p.background.paper,
    h: p.text.primary,
    p: p.text.secondary,
  }, // neutral 2
  success: { bg: p.success.dark, h: p.success.light, p: p.success.main }, // success
  warning: { bg: p.warning.dark, h: p.warning.light, p: p.warning.main }, // warning
  error: { bg: p.error.dark, h: p.error.light, p: p.error.main }, // error
  techno: {
    bg: p.techno.dark,
    h: p.techno.light,
    p: p.techno.main,
  }, // techno
  retro: { bg: p.retro.dark, h: p.retro.light, p: p.retro.main }, // retro
};
