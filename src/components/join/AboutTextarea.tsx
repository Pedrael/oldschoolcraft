import { TextField } from "@mui/material";

export interface AboutTextareaProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
}

export function AboutTextarea({
  value,
  onChange,
  label = "About you",
}: AboutTextareaProps) {
  return (
    <TextField
      fullWidth
      label={label}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      variant="outlined"
      multiline
      rows={4}
      sx={{
        "& .MuiOutlinedInput-root": {
          borderRadius: 0,

          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: (theme) => theme.palette.primary.light,
          },

          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: (theme) => theme.palette.primary.main,
          },
        },
      }}
    />
  );
}
