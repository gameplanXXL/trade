import { useQuery } from '@tanstack/react-query';

interface Template {
  name: string;
  description: string;
  roles: string[];
  pipeline: string;
}

async function fetchTemplates(): Promise<Template[]> {
  const response = await fetch('/api/team-templates/');
  if (!response.ok) {
    throw new Error('Failed to fetch templates');
  }
  return response.json();
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
