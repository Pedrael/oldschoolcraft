# Carousel + FeaturesSection plan

## 1. Carousel component (reusable)

**File:** `src/components/Carousel.tsx`

**Slide shape (type in same file or `src/types/carousel.ts`):**

- `title: string` (h2)
- `paragraphs: string[]` (one or more `<p>`)
- `image?: string` (URL or path, e.g. `/assets/slide-1.jpg`) — optional; if missing, slide is text-only
- `scheme?: number | BlockColorScheme` — which BLOCK_SCHEMES to use for this slide’s background and text. Default e.g. `0` if omitted.

**Props:**

- `slides: Slide[]` (required)
- Optional: `initialIndex?: number`, `showDots?: boolean`, `showArrows?: boolean`

**Behavior:**

- One slide visible at a time. Track current index in `useState`.
- Each slide is a panel with:
  - **Scheme:** Apply the slide’s `scheme` (resolve via BLOCK_SCHEMES) to the slide container: `backgroundColor: resolved.bg`, `color: resolved.text`, same flex column + align center as LayoutBlock.
  - **Layout:** Flex row on large screens (image on one side, text on the other) or column on small; image and text block (title + paragraphs) inside.
  - **Content:** `<Typography component="h2">`, then map `paragraphs` to `<Typography variant="body1">`; optional img or Box with backgroundImage for the picture.
- **Navigation:** Dots (one per slide, click to go to index) and/or Prev/Next arrows. No extra dependency: React state + MUI IconButton and simple dot elements.

**Implementation:** No carousel library in package.json. Use a minimal custom carousel: `currentIndex` state, render only `slides[currentIndex]` (or render all and hide with overflow + translateX for optional animation). Prefer single-slide render first; add CSS transition later if desired.

---

## 2. Content: features in JSON

**File:** `src/content/text.json`

Add a `features` key:

- **`features.main`:** `heading`: "Three layers of chaos. One world.", `body`: "Magic, machinery and survival all collide in a world that actually fights back."
- **`features.slides`:** Array of 3 items:
  - **Slide 1:** title "Magic that feels dangerous", paragraphs: [Thaumcraft/Botania/EvilCraft paragraph, Research forbidden…, This is not decorative…]
  - **Slide 2:** title "Technology with actual consequences", paragraphs: [Thermal Expansion…, Build production lines…]
  - **Slide 3:** title "A world that pushes back", paragraphs: [EnviroMine…, Temperature matters…, You are not just building…, This is old-school modded tech…]

Each slide can later get an `image` path when assets exist; for now omit or use `""`. Optional: add `scheme` per slide (e.g. 0, 1, 2) so each slide has a different look.

---

## 3. FeaturesSection

**File:** `src/sections/FeaturesSection.tsx`

**Layout:**

- Wrap in LayoutBlock with a chosen section scheme, or a full-width block so the carousel controls its own slide backgrounds.
- **Main block (top):** One h1 with `features.main.heading`, one p with `features.main.body`. Centered, max-width, spacing below.
- **Carousel (below):** `<Carousel slides={content.features.slides} />`. Pass slides from JSON; each slide has title, paragraphs, optional image, optional scheme.

**Content source:** Import content from `../content/text.json`, use `content.features.main` and `content.features.slides`.

---

## 4. Wiring and images

- **App:** Add `<FeaturesSection />` after existing sections in `App.tsx`.
- **Images:** Slides accept `image: string`. Start without images or with placeholders. When you have art, add paths to `features.slides[].image` (e.g. `/assets/features-magic.jpg`) and put files in `public/assets/`.

---

## 5. Suggested implementation order

1. **Types and content** — Define `Slide` type. Update `text.json` with `features.main` and `features.slides` (all three slides with the exact copy).
2. **Carousel** — Implement `Carousel.tsx`: resolve scheme per slide, render one slide (title + paragraphs + optional image), apply scheme to slide container, add dots and optional arrows, useState for index.
3. **FeaturesSection** — Implement section with main h1 + p and `<Carousel slides={...} />`.
4. **App** — Render FeaturesSection in the page.

Optional later: slide transition (fade or translateX), autoplay, or different layout (e.g. image above text on mobile).
