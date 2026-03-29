import { useEffect, useState } from 'react'
import {
  Box,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Skeleton,
  Stack,
  Tooltip,
  Typography,
} from '@mui/material'
import { fetchProject } from '../../api/projects'
import { ProjectDetail, ProjectSummary } from '../../types/project'

interface DetailsPanelProps {
  selectedProject: ProjectSummary | null
}

const PANEL_WIDTH = 300

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
}

function formatDatetime(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

interface RowProps {
  label: string
  value: React.ReactNode
}

function Row({ label, value }: RowProps) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500, textTransform: 'uppercase', letterSpacing: 0.5 }}>
        {label}
      </Typography>
      <Typography variant="body2" sx={{ mt: 0.25, wordBreak: 'break-all' }}>
        {value ?? '—'}
      </Typography>
    </Box>
  )
}

export function DetailsPanel({ selectedProject }: DetailsPanelProps) {
  const [detail, setDetail] = useState<ProjectDetail | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selectedProject) {
      setDetail(null)
      return
    }

    let cancelled = false
    setLoading(true)
    setDetail(null)

    fetchProject(selectedProject.id)
      .then((d) => { if (!cancelled) setDetail(d) })
      .catch(() => { /* non-fatal — summary data already visible */ })
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [selectedProject?.id])

  return (
    <Paper
      elevation={0}
      sx={{
        width: PANEL_WIDTH,
        flexShrink: 0,
        borderLeft: '1px solid',
        borderColor: 'divider',
        marginTop: '64px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {!selectedProject ? (
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
            Project Details
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select a project to view details
          </Typography>
        </Box>
      ) : (
        <Box sx={{ p: 2 }}>
          {/* ── Header ── */}
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={1}>
            <Typography variant="subtitle1" fontWeight="bold" sx={{ lineHeight: 1.3, flex: 1, mr: 1 }}>
              {selectedProject.name}
            </Typography>
            {loading && <CircularProgress size={14} sx={{ mt: 0.5, flexShrink: 0 }} />}
          </Stack>

          {selectedProject.category && (
            <Chip
              label={selectedProject.category}
              size="small"
              variant="outlined"
              sx={{ mb: 1.5 }}
            />
          )}

          <Divider sx={{ mb: 2 }} />

          {/* ── Summary fields (always available immediately) ── */}
          <Stack spacing={1.5}>
            <Row label="Date" value={selectedProject.project_date ?? '—'} />
            <Row label="Visibility" value={selectedProject.visibility} />
            <Row label="Folder" value={selectedProject.folder_name} />
            {selectedProject.file_count != null && (
              <Row
                label="Files"
                value={`${selectedProject.file_count.toLocaleString()} files · ${formatBytes(selectedProject.disk_usage_bytes ?? 0)}`}
              />
            )}
            {selectedProject.media_types && selectedProject.media_types.length > 0 && (
              <Box>
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  Media Types
                </Typography>
                <Stack direction="row" gap={0.5} flexWrap="wrap" mt={0.5}>
                  {selectedProject.media_types.map((t) => (
                    <Chip key={t} label={t} size="small" />
                  ))}
                </Stack>
              </Box>
            )}
          </Stack>

          <Divider sx={{ my: 2 }} />

          {/* ── Detail fields (loaded async) ── */}
          <Stack spacing={1.5}>
            {loading ? (
              <>
                <Skeleton variant="text" width="60%" height={14} />
                <Skeleton variant="text" width="90%" height={14} />
                <Skeleton variant="text" width="75%" height={14} />
              </>
            ) : detail ? (
              <>
                <Tooltip title={detail.nas_path} placement="left" arrow>
                  <Box>
                    <Row label="NAS Path" value={detail.nas_path} />
                  </Box>
                </Tooltip>
                {detail.notes && <Row label="Notes" value={detail.notes} />}
                <Row label="Archived" value={detail.archived ? 'Yes' : 'No'} />
                <Row
                  label="Naming Convention"
                  value={
                    detail.naming_convention_valid == null
                      ? '—'
                      : detail.naming_convention_valid
                      ? '✓ Valid'
                      : '✗ Invalid'
                  }
                />
                <Row label="Last Scanned" value={formatDatetime(detail.last_scanned_at)} />
                <Row label="Last Backup" value={formatDatetime(detail.last_backup_at)} />
                {detail.backup_host && <Row label="Backup Host" value={detail.backup_host} />}
                <Row label="Changed Since Backup" value={detail.changed_since_backup ? 'Yes' : 'No'} />
                <Row label="Created" value={formatDatetime(detail.created_at)} />
                <Row label="Updated" value={formatDatetime(detail.updated_at)} />
              </>
            ) : null}
          </Stack>
        </Box>
      )}
    </Paper>
  )
}
