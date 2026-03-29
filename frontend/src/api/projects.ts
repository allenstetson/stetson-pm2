/// <reference types="vite/client" />
import { ProjectDetail, ProjectListResponse } from '../types/project';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface FetchProjectsParams {
  skip?: number;
  limit?: number;
  q?: string;
  category?: string;
  changedSinceBackup?: boolean;
  token?: string;
}

export async function fetchProjects(
  params: FetchProjectsParams = {}
): Promise<ProjectListResponse> {
  const { skip = 0, limit = 100, q, category, changedSinceBackup, token } = params;
  const qs = new URLSearchParams();
  qs.set('skip', String(skip));
  qs.set('limit', String(limit));
  if (q) qs.set('q', q);
  if (category) qs.set('category', category);
  if (changedSinceBackup !== undefined) qs.set('changed_since_backup', String(changedSinceBackup));
  const url = `${API_BASE}/api/projects?${qs.toString()}`;

  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(url, { headers });

  if (!response.ok) {
    throw new Error(
      `Failed to fetch projects: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<ProjectListResponse>;
}

export async function fetchProject(id: string, token?: string): Promise<ProjectDetail> {
  const url = `${API_BASE}/api/projects/${id}`;

  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(url, { headers });

  if (!response.ok) {
    throw new Error(
      `Failed to fetch project: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<ProjectDetail>;
}

export async function recordBackup(
  id: string,
  backupHost: string
): Promise<ProjectDetail> {
  const url = `${API_BASE}/api/projects/${id}/backup`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ backup_host: backupHost }),
  });

  if (!response.ok) {
    throw new Error(
      `Failed to record backup: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<ProjectDetail>;
}

export async function updateProjectVisibility(
  id: string,
  visibility: string,
  token: string,
): Promise<ProjectDetail> {
  const url = `${API_BASE}/api/projects/${id}/visibility`;

  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ visibility }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update visibility: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<ProjectDetail>;
}
