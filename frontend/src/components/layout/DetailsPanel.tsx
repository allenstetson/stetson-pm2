import { Paper, Typography } from '@mui/material'

export function DetailsPanel() {
  return (
    <Paper
      sx={{
        width: 300,
        flexShrink: 0,
        p: 2,
        marginTop: '64px',
        borderLeft: '1px solid #ddd',
      }}
    >
      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
        Project Details
      </Typography>
      <Typography variant="body2" color="textSecondary">
        Select a project to view details
      </Typography>
    </Paper>
  )
}
