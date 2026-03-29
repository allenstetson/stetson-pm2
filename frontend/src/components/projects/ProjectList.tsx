import { useEffect, useRef, useState } from 'react';
import { Alert, Box, CircularProgress, Typography } from '@mui/material';
import { fetchProjects } from '../../api/projects';
import { ProjectSummary } from '../../types/project';
import { ProjectCard } from './ProjectCard';
import { SearchFilterBar } from './SearchFilterBar';

const DEBOUNCE_MS = 300;

interface ProjectListProps {
  selectedProjectId: string | null;
  onSelectProject: (project: ProjectSummary | null) => void;
}

export function ProjectList({ selectedProjectId, onSelectProject }: ProjectListProps) {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchText, setSearchText] = useState('');
  const [category, setCategory] = useState<string | null>(null);
  const [changedSinceBackup, setChangedSinceBackup] = useState(false);
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search text
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const handleSearchChange = (value: string) => {
    setSearchText(value);
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => setDebouncedSearch(value), DEBOUNCE_MS);
  };

  const handleCategoryChange = (value: string | null) => {
    setCategory(value);
    onSelectProject(null);
  };

  const handleChangedSinceBackupChange = (value: boolean) => {
    setChangedSinceBackup(value);
    onSelectProject(null);
  };

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchProjects({
          q: debouncedSearch || undefined,
          category: category || undefined,
          changedSinceBackup: changedSinceBackup || undefined,
        });
        if (!cancelled) {
          setProjects(data.items);
          setTotal(data.total);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unknown error');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [debouncedSearch, category, changedSinceBackup]);

  const hasFilters = debouncedSearch.trim() !== '' || category !== null || changedSinceBackup;

  return (
    <Box>
      <SearchFilterBar
        searchText={searchText}
        category={category}
        changedSinceBackup={changedSinceBackup}
        onSearchChange={handleSearchChange}
        onCategoryChange={handleCategoryChange}
        onChangedSinceBackupChange={handleChangedSinceBackupChange}
      />

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" py={6}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mt: 2 }}>
          Could not load projects: {error}
        </Alert>
      ) : projects.length === 0 ? (
        <Box py={6} textAlign="center">
          <Typography variant="body1" color="text.secondary">
            {hasFilters ? 'No projects match your search.' : 'No projects found.'}
          </Typography>
        </Box>
      ) : (
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
            {total} project{total !== 1 ? 's' : ''}
          </Typography>
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              selected={project.id === selectedProjectId}
              onSelect={() =>
                onSelectProject(project.id === selectedProjectId ? null : project)
              }
            />
          ))}
        </Box>
      )}
    </Box>
  );
}
