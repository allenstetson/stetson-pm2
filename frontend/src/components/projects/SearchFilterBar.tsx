import { InputAdornment, Stack, TextField, ToggleButton, ToggleButtonGroup } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

const CATEGORIES = ['home', 'school', 'work'] as const;

interface SearchFilterBarProps {
  searchText: string;
  category: string | null;
  onSearchChange: (value: string) => void;
  onCategoryChange: (value: string | null) => void;
}

export function SearchFilterBar({
  searchText,
  category,
  onSearchChange,
  onCategoryChange,
}: SearchFilterBarProps) {
  const handleCategory = (_: React.MouseEvent<HTMLElement>, value: string | null) => {
    onCategoryChange(value);
  };

  return (
    <Stack direction="row" spacing={1.5} alignItems="center" mb={2} flexWrap="wrap" useFlexGap>
      <TextField
        size="small"
        placeholder="Search projects…"
        value={searchText}
        onChange={(e) => onSearchChange(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon fontSize="small" />
            </InputAdornment>
          ),
        }}
        sx={{ minWidth: 220 }}
      />

      <ToggleButtonGroup
        value={category}
        exclusive
        onChange={handleCategory}
        size="small"
        aria-label="category filter"
      >
        {CATEGORIES.map((cat) => (
          <ToggleButton key={cat} value={cat} aria-label={cat}>
            {cat}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Stack>
  );
}
