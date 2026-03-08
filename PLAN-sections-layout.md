# Plan: Sections as TSX files + unified LayoutBlock

## Goal

- Each landing section = separate TSX file.
- One reusable **LayoutBlock** (or `SectionBlock`) that wraps section content with:
  - **Color scheme** chosen from a predefined array `[{ bg, fg, text }, ...]` (e.g. dark bg + light text vs light bg + dark text).
  - **Margins** (consistent vertical/optional horizontal).
  - **Layout**: `display: 'flex'`, `flexDirection: 'column'`, `alignItems: 'center'` (content centered in a column).

---

## 1. Color scheme type and array

- **Type** (e.g. in `src/types/layout.ts` or next to the component):

```ts
export interface BlockColorScheme {
  bg: string      // background
  fg?: string     // optional, default same as text
  text: string    // primary text (and fg if omitted)
}
```

- **Array of schemes** (e.g. in theme or a small constants file) so blocks can pick by index or id:

```ts
// Example: dark block (current default), light block, accent block
export const BLOCK_SCHEMES: BlockColorScheme[] = [
  { bg: '#121214', text: '#e5e5e5' },           // dark bg, light text
  { bg: '#e5e5e5', text: '#121214' },           // light bg, dark text
  { bg: '#1b1b20', text: '#8b5cf6' },           // card + primary accent text
]
```

- Prefer using theme palette values (e.g. `theme.palette.background.default`, `theme.palette.text.primary`) when building this array so it stays consistent with Techno-Arcane.

---

## 2. LayoutBlock component

- **File**: `src/components/LayoutBlock.tsx` (or `src/layout/LayoutBlock.tsx`).

- **Props**:
  - `scheme`: `BlockColorScheme` or index into `BLOCK_SCHEMES` (e.g. `scheme={0}` or `scheme={BLOCK_SCHEMES[0]}`).
  - `children`: section content.
  - Optional: `sx` for overrides, `component` (default `'section'`), margin overrides (e.g. `marginY`, `paddingY`).

- **Styles** (MUI `Box` or `section`):
  - `backgroundColor`: `scheme.bg`
  - `color`: `scheme.fg ?? scheme.text`
  - `display: 'flex'`
  - `flexDirection: 'column'`
  - `alignItems: 'center'`
  - Margins (e.g. `my: 2`, `px: 2`, or via theme spacing).
  - Optional: `width: '100%'`, `boxSizing: 'border-box'`, and max-width for content if needed.

- **Behavior**: Renders a single wrapper; all section content (headings, body, buttons) goes inside as children and inherits the block’s text color unless overridden.

---

## 3. Sections as separate TSX files

- **Location**: `src/sections/` (e.g. `HeroSection.tsx`, `FooterSection.tsx`; add more as the page grows).

- **Each section**:
  - Imports and uses `LayoutBlock` with a chosen scheme (e.g. `scheme={BLOCK_SCHEMES[0]}`).
  - Imports content from `src/content/text.json` (or a section-specific slice) and renders its part (e.g. hero title/subtitle).
  - Exports a single component (e.g. `HeroSection`).

- **Example** (conceptual):

```tsx
// src/sections/HeroSection.tsx
import { LayoutBlock } from '../components/LayoutBlock'
import { BLOCK_SCHEMES } from '../constants/block-schemes'
import content from '../content/text.json'

export function HeroSection() {
  return (
    <LayoutBlock scheme={BLOCK_SCHEMES[0]}>
      <Typography component="h1" variant="h1">{content.hero.title}</Typography>
      {content.hero.subtitle && <Typography variant="body1">{content.hero.subtitle}</Typography>}
    </LayoutBlock>
  )
}
```

- **App.tsx** then just stacks sections:

```tsx
<Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
  <HeroSection />
  <FooterSection />
</Box>
```

---

## 4. File structure (summary)

```
src/
  components/
    LayoutBlock.tsx      # unified block: scheme + flex column + align center + margins
  constants/
    block-schemes.ts     # BLOCK_SCHEMES array (and optionally BlockColorScheme type)
  sections/
    HeroSection.tsx
    FooterSection.tsx
  types/
    layout.ts            # BlockColorScheme (if not in constants)
  App.tsx                # composes sections only
```

- **Constants**: Either keep `BlockColorScheme` and `BLOCK_SCHEMES` in one file (e.g. `block-schemes.ts`) or put the type in `types/layout.ts` and the array in constants. Use theme palette values in `BLOCK_SCHEMES` where possible (e.g. pass `theme` or import theme and read `theme.palette.*`).

---

## 5. Suggested order

1. Add `BlockColorScheme` type and `BLOCK_SCHEMES` array (theme-based values).
2. Implement `LayoutBlock` with `scheme`, margins, and flex column + align center.
3. Add `src/sections/HeroSection.tsx` and `FooterSection.tsx`, each using `LayoutBlock` and JSON content.
4. Refactor `App.tsx` to render only the list of section components.

After this, new sections are new TSX files in `sections/` and a new entry in `App.tsx`; color changes per block are done by choosing a different `scheme` from `BLOCK_SCHEMES`.
