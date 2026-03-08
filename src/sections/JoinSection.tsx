import { useState } from "react";
import { Box, Snackbar, Typography } from "@mui/material";
import { LayoutBlock } from "../components/LayoutBlock";
import { NicknameField } from "../components/join/NicknameField";
import { AboutTextarea } from "../components/join/AboutTextarea";
import { SendButton } from "../components/join/SendButton";
import content from "../content/text.json";
import { AddressButton } from "../components/join/AddressButton";

const STONEBRICK_TILES = [
  { src: "/assets/blocks/stonebrick.png", weight: 6 },
  { src: "/assets/blocks/stonebrick_mossy.png", weight: 3 },
  { src: "/assets/blocks/stonebrick_cracked.png", weight: 1 },
];

export function JoinSection() {
  const join = content.join;
  const [nickname, setNickname] = useState("");
  const [about, setAbout] = useState("");
  const [nicknameError, setNicknameError] = useState(false);
  const [copiedOpen, setCopiedOpen] = useState(false);

  const handleCopyIp = async () => {
    try {
      await navigator.clipboard.writeText(join.serverIp);
      setCopiedOpen(true);
    } catch {
      // ignore
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = nickname.trim();
    if (!trimmed) {
      setNicknameError(true);
      return;
    }
    setNicknameError(false);
    console.log({ nickname: trimmed, about: about.trim() });
  };

  return (
    <LayoutBlock
      tiles={STONEBRICK_TILES}
      tileDim={0.8}
      tileSize={64}
      sx={{ pb: "5rem" }}
    >
      <Typography
        component="h1"
        variant="h1"
        sx={{ mb: 2, textAlign: "center" }}
      >
        {join.heading}
      </Typography>
      <Typography variant="body1" sx={{ textAlign: "center", mb: 2 }}>
        {join.body}
      </Typography>
      <AddressButton onClick={handleCopyIp} label={join.serverIp} />
      <Box
        component="form"
        onSubmit={handleSubmit}
        display="flex"
        flexDirection="column"
        alignItems="center"
        gap={2}
        width="100%"
      >
        <NicknameField
          value={nickname}
          onChange={(v) => {
            setNickname(v);
            setNicknameError(false);
          }}
          error={nicknameError}
          label={join.nicknameLabel}
        />
        <AboutTextarea
          value={about}
          onChange={setAbout}
          label={join.aboutLabel}
        />
        <SendButton label={join.sendButtonLabel} />
      </Box>
      <Snackbar
        open={copiedOpen}
        autoHideDuration={2000}
        onClose={() => setCopiedOpen(false)}
        message="Copied!"
        sx={{
          "& .MuiSnackbarContent-root": {
            borderRadius: 0,
          },
        }}
      />
    </LayoutBlock>
  );
}
