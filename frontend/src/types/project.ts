export interface ProjectSummary {
  id: string;
  name: string;
  category: string | null;
  project_date: string | null; // ISO date string: "YYYY-MM-DD"
  media_types: string[];
  visibility: string;
  folder_name: string;
  file_count: number | null;
  disk_usage_bytes: number | null;
}

export interface ProjectDetail extends ProjectSummary {
  nas_path: string;
  local_path: string | null;
  archived: boolean;
  thumbnail_path: string | null;
  notes: string | null;
  naming_convention_valid: boolean | null;
  last_scanned_at: string | null;  // ISO datetime string
  last_backup_at: string | null;   // ISO datetime string
  backup_host: string | null;
  changed_since_backup: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  items: ProjectSummary[];
  total: number;
}
