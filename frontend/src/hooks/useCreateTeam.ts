import { useMutation, useQueryClient } from '@tanstack/react-query';

export interface TeamCreateInput {
  name: string;
  template_name: string;
  symbols: string[];
  budget: number;
  mode: 'paper' | 'live';
}

interface TeamResponse {
  id: number;
  name: string;
  template_name: string;
  symbols: string[];
  budget: number;
  mode: 'paper' | 'live';
  status: string;
}

async function createTeam(data: TeamCreateInput): Promise<TeamResponse> {
  const response = await fetch('/api/teams/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to create team');
  }

  return response.json();
}

export function useCreateTeam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTeam,
    onSuccess: () => {
      // Invalidate teams query to refetch the list
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });
}
