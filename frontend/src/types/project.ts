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

export interface ProjectListResponse {
  items: ProjectSummary[];
  total: number;
}
