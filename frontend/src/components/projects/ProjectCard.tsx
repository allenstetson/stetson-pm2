import { ProjectSummary } from '../../types/project';
import {
  Card,
  CardActionArea,
  CardContent,
  Chip,
  Stack,
  Typography,
} from '@mui/material';

interface ProjectCardProps {
  project: ProjectSummary;
  selected: boolean;
  onSelect: () => void;
}

const CATEGORY_COLORS: Record<string, 'default' | 'primary' | 'secondary' | 'success' | 'warning'> = {
  home: 'primary',
  school: 'success',
  work: 'secondary',
};

const VISIBILITY_COLORS: Record<string, 'default' | 'error' | 'warning' | 'info'> = {
  sensitive: 'error',
  work: 'warning',
  school: 'info',
  family: 'default',
};

const MEDIA_LABELS: Record<string, string> = {
  photo: '📷 Photo',
  video: '🎬 Video',
  document: '📄 Document',
  audio: '🎵 Audio',
  other: 'Other',
};

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

export function ProjectCard({ project, selected, onSelect }: ProjectCardProps) {
  const categoryColor = CATEGORY_COLORS[project.category ?? ''] ?? 'default';
  const visibilityColor = VISIBILITY_COLORS[project.visibility] ?? 'default';

  return (
    <Card
      variant="outlined"
      sx={{
        mb: 1.5,
        borderLeft: selected ? '3px solid' : '1px solid',
        borderLeftColor: selected ? 'primary.main' : 'divider',
        boxShadow: selected ? 3 : 0,
        transition: 'box-shadow 0.15s ease, border-left-color 0.15s ease',
      }}
    >
      <CardActionArea onClick={onSelect} sx={{ display: 'block' }}>
      <CardContent sx={{ pb: '12px !important' }}>
        {/* Header row: name + visibility badge */}
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={0.5}>
          <Typography variant="subtitle1" fontWeight="bold" sx={{ lineHeight: 1.3 }}>
            {project.name}
          </Typography>
          <Chip
            label={project.visibility}
            color={visibilityColor}
            size="small"
            variant={project.visibility === 'sensitive' ? 'filled' : 'outlined'}
            sx={{ ml: 1, flexShrink: 0 }}
          />
        </Stack>

        {/* Meta row: category + date */}
        <Stack direction="row" gap={1} alignItems="center" mb={1} flexWrap="wrap">
          {project.category && (
            <Chip
              label={project.category}
              color={categoryColor}
              size="small"
              variant="outlined"
            />
          )}
          {project.project_date && (
            <Typography variant="caption" color="text.secondary">
              {project.project_date}
            </Typography>
          )}
          {project.file_count != null && project.disk_usage_bytes != null && (
            <Typography variant="caption" color="text.secondary">
              {project.file_count.toLocaleString()} files · {formatBytes(project.disk_usage_bytes)}
            </Typography>
          )}
        </Stack>

        {/* Media type chips */}
        {project.media_types && project.media_types.length > 0 && (
          <Stack direction="row" gap={0.5} flexWrap="wrap">
            {project.media_types.map((type) => (
              <Chip
                key={type}
                label={MEDIA_LABELS[type] ?? type}
                size="small"
                sx={{ fontSize: '0.7rem' }}
              />
            ))}
          </Stack>
        )}

        {/* Backup state badge */}
        {project.changed_since_backup && (
          <Stack direction="row" gap={0.5} mt={0.5}>
            <Chip
              label="Changed since backup"
              size="small"
              color="warning"
              variant="outlined"
              sx={{ fontSize: '0.7rem' }}
            />
          </Stack>
        )}
      </CardContent>
      </CardActionArea>
    </Card>
  );
}
