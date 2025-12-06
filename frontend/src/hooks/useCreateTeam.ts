import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

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
  initial_budget: number;
  current_budget: number;
  mode: 'paper' | 'live';
  status: string;
  realized_pnl: number;
  unrealized_pnl: number;
  created_at: string;
  updated_at: string | null;
}

async function createTeam(data: TeamCreateInput): Promise<TeamResponse> {
  const response = await apiClient.post<TeamResponse>('/api/teams/', data);
  return response.data;
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
