import { TextField } from "@mui/material";

export interface NicknameFieldProps {
  value: string;
  onChange: (value: string) => void;
  error?: boolean;
  required?: boolean;
  label?: string;
}

export function NicknameField({
  value,
  onChange,
  error = false,
  required = true,
  label = "Nickname",
}: NicknameFieldProps) {
  return (
    <TextField
      fullWidth
      label={label}
      variant="outlined"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      error={error}
      required={required}
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
