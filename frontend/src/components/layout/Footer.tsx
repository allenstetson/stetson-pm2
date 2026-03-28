import { Box, Typography } from '@mui/material'

export function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        py: 2,
        px: 3,
        backgroundColor: '#f5f5f5',
        borderTop: '1px solid #ddd',
      }}
    >
      <Typography variant="caption" color="textSecondary">
        Stetson Home Projects Manager v0.1.0
      </Typography>
    </Box>
  )
}
