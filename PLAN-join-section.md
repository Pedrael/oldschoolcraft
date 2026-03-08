# JoinSection and form components plan

## 1. Content in JSON

**File:** [src/content/text.json](oldschoolcraft/src/content/text.json)

Add a `join` (or `joinSection`) key:

- `heading`: "Think you can survive here?"
- `body`: "We keep the whitelist small so the world doesn't turn into chaos. Drop your nickname and a few words about yourself."
- `serverIp`: the server IP string (e.g. "play.example.com" or "192.168.1.1:25565") so it's editable and reusable for the clickable block.
- Optional: `nicknameLabel`, `aboutLabel`, `sendButtonLabel` (e.g. "Nickname", "About you", "Send") so labels are content-driven; otherwise hardcode in components.

---

## 2. Separate components (field, textarea, button)

**Location:** `src/components/join/` (or `src/components/`)

**NicknameField** (`NicknameField.tsx`)

- MUI `TextField` (or `OutlinedInput` + `InputLabel`), single line.
- Props: `value`, `onChange`, `error`, `required` (default true). Optional: `label` from content.
- Used for the mandatory nickname; parent form will validate and set `error` when empty on submit.

**AboutTextarea** (`AboutTextarea.tsx`)

- MUI `TextField` with `multiline` and `rows` (e.g. 4), or `TextField` + `minRows`/`maxRows`. Optional label.
- Props: `value`, `onChange`, optional `label`. No required validation.

**SendButton** (`SendButton.tsx`)

- MUI `Button`, type `submit`, label "Send" (or from content).
- Props: `disabled` (optional, e.g. while submitting or when nickname is empty if you want to disable until valid). No logic inside the component; parent form handles submit.

All three receive props from the parent; no form state inside these components so they stay presentational and reusable.

---

## 3. Form state and validation

The **parent** (JoinSection or a small **JoinForm** component) holds:

- `nickname: string`, `about: string` (state).
- `errors` or a single `nicknameError` (e.g. empty string on submit).
- `handleSubmit`: `preventDefault`, validate nickname (required), then either call an optional `onSubmit(nickname, about)` prop or for now just `console.log` / show a snackbar so a real backend can be wired later.

Pass `value`, `onChange`, `error` into NicknameField; `value`, `onChange` into AboutTextarea; and use SendButton inside a `<form onSubmit={handleSubmit}>`.

---

## 4. JoinSection layout

**File:** `src/sections/JoinSection.tsx`

- Wrap in [LayoutBlock](oldschoolcraft/src/components/LayoutBlock.tsx) with a chosen scheme (e.g. `BLOCK_SCHEMES[1]` or `0`).
- Order:
  1. `<Typography component="h1">` with `join.heading`.
  2. `<Typography variant="body1">` with `join.body`.
  3. **Server IP (clickable):** Display `join.serverIp` as a clickable element that copies the IP to the clipboard on click (e.g. `navigator.clipboard.writeText(serverIp)`), with optional visual feedback (e.g. "Copied!" tooltip or Snackbar). Use MUI `Button` or `Link`-like styling so it’s clearly clickable.
  4. **Form:** `<form onSubmit={...}>` containing:
     - `<NicknameField value={nickname} onChange={...} error={nicknameError} />`
     - `<AboutTextarea value={about} onChange={...} />`
     - `<SendButton />` (or `<SendButton disabled={!nickname.trim()} />` if you want)
- Use a consistent max-width and spacing (e.g. same as other sections). Form layout: stack fields vertically with `sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 400 }}` or similar.

---

## 5. Wiring

- **App:** Add `<JoinSection />` after `<FeaturesSection />` in [App.tsx](oldschoolcraft/src/App.tsx).

---

## 6. Implementation order

1. Add `join` content to `text.json` (heading, body, serverIp, optional labels).
2. Create `NicknameField`, `AboutTextarea`, and `SendButton` in `src/components/join/` (or `src/components/`).
3. Implement JoinSection: LayoutBlock, h1, p, clickable server IP (copy), form with state and validation that uses the three components, handleSubmit (client-side only for now).
4. Add JoinSection to App.

No backend in scope; submit handler can be a placeholder until you add an API or form service.
