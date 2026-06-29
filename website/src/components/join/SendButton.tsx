import { Button } from "@mui/material";

export interface SendButtonProps {
  disabled?: boolean;
  label?: string;
}

export function SendButton({
  disabled = false,
  label = "Send",
}: SendButtonProps) {
  return (
    <Button
      type="submit"
      variant="contained"
      disabled={disabled}
      sx={{
        width: 300,
        maxWidth: "100%",
        borderRadius: 0,
        "&:hover": {
          background: (theme) => theme.palette.primary.light,
        },
      }}
    >
      {label}
    </Button>
  );
}
