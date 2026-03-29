/// <reference types="vite/client" />
import { ProjectListResponse } from '../types/project';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface FetchProjectsParams {
  skip?: number;
  limit?: number;
}

export async function fetchProjects(
  params: FetchProjectsParams = {}
): Promise<ProjectListResponse> {
  const { skip = 0, limit = 100 } = params;
  const url = `${API_BASE}/api/projects?skip=${skip}&limit=${limit}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Failed to fetch projects: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<ProjectListResponse>;
}
