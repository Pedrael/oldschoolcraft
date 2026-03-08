import { Box } from '@mui/material'

const LINE_COUNT = 32

export function BlockMessageBlock() {
  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: 560,
        height: 160,
        overflow: 'hidden',
        backgroundColor: '#000',
        borderRadius: 1,
        px: 2,
        py: 1.5,
        fontFamily: '"Minecraft", sans-serif',
        fontSize: '0.9rem',
        lineHeight: 1.3,
      }}
    >
      {Array.from({ length: LINE_COUNT }, (_, i) => (
        <Box key={i} component="span" sx={{ display: 'block' }}>
          <Box component="span" sx={{ color: '#ff5555' }}>
            Hey!
          </Box>
          <Box component="span" sx={{ color: '#c0c0c0' }}>
            {' '}
            Sorry, but you can't break that block here.
          </Box>
        </Box>
      ))}
    </Box>
  )
}
