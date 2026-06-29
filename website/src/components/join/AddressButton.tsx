import { Button } from "@mui/material";

export interface AddressButtonProps {
  onClick: () => void;
  label?: string;
}

export function AddressButton({
  onClick,
  label = "Address",
}: AddressButtonProps) {
  return (
    <Button
      onClick={onClick}
      variant="text"
      sx={{
        mb: 3,
        letterSpacing: 2,
        borderRadius: 0,
        "&:hover": {
          background: "transparent",
          color: (theme) => theme.palette.primary.light,
        },
      }}
    >
      {label}
    </Button>
  );
}
