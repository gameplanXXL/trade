import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface Template {
  name: string;
  display_name: string;
  description: string;
  version: string;
  roles: string[];
  pipeline: string;
}

async function fetchTemplates(): Promise<Template[]> {
  const response = await apiClient.get<Template[]>('/api/team-templates/');
  return response.data;
}

export function useTemplates() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['templates'],
    queryFn: fetchTemplates,
  });

  return {
    templates: data ?? [],
    isLoading,
    error,
  };
}
