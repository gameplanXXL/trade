import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

import { useTemplates } from '@/hooks/useTemplates';
import { useCreateTeam, type TeamCreateInput } from '@/hooks/useCreateTeam';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

// Validation schema
const teamCreateSchema = z.object({
  name: z.string().min(3, 'Name muss mindestens 3 Zeichen haben').max(50, 'Name darf maximal 50 Zeichen haben'),
  template_name: z.string().min(1, 'Bitte wähle ein Template'),
  symbols: z.array(z.string()).min(1, 'Mindestens ein Symbol erforderlich'),
  budget: z.number().min(100, 'Budget muss mindestens 100€ betragen'),
  mode: z.enum(['paper', 'live']),
});

const AVAILABLE_SYMBOLS = [
  'EUR/USD',
  'GBP/USD',
  'USD/JPY',
  'AUD/USD',
  'USD/CHF',
  'NZD/USD',
  'USD/CAD',
];

export function TeamCreate() {
  const navigate = useNavigate();
  const { templates, isLoading: templatesLoading } = useTemplates();
  const createTeam = useCreateTeam();

  const form = useForm<TeamCreateInput>({
    resolver: zodResolver(teamCreateSchema),
    defaultValues: {
      name: '',
      template_name: 'conservative_llm',
      symbols: ['EUR/USD'],
      budget: 10000,
      mode: 'paper',
    },
  });

  const onSubmit = async (data: TeamCreateInput) => {
    try {
      await createTeam.mutateAsync(data);
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to create team:', error);
    }
  };

  const isLiveMode = form.watch('mode') === 'live';
  const selectedSymbols = form.watch('symbols');

  const toggleSymbol = (symbol: string) => {
    const current = selectedSymbols || [];
    if (current.includes(symbol)) {
      form.setValue('symbols', current.filter(s => s !== symbol));
    } else {
      form.setValue('symbols', [...current, symbol]);
    }
  };

  return (
    <div className="container mx-auto py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Neues Team erstellen</CardTitle>
          <CardDescription>
            Erstelle ein neues Trading-Team basierend auf einem Template
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Team Name */}
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Team-Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Mein Trading Team" {...field} />
                    </FormControl>
                    <FormDescription>
                      Ein eindeutiger Name für dein Team (3-50 Zeichen)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Template Selection */}
              <FormField
                control={form.control}
                name="template_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Template</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      disabled={templatesLoading}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Wähle ein Template" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {templates.map((template) => (
                          <SelectItem key={template.name} value={template.name}>
                            {template.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Das Template bestimmt die Agent-Rollen und Pipeline
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Symbols Selection */}
              <FormField
                control={form.control}
                name="symbols"
                render={() => (
                  <FormItem>
                    <FormLabel>Trading-Symbole</FormLabel>
                    <div className="grid grid-cols-2 gap-2">
                      {AVAILABLE_SYMBOLS.map((symbol) => (
                        <div key={symbol} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`symbol-${symbol}`}
                            checked={selectedSymbols?.includes(symbol)}
                            onChange={() => toggleSymbol(symbol)}
                            className="h-4 w-4 rounded border-gray-300"
                          />
                          <label
                            htmlFor={`symbol-${symbol}`}
                            className="text-sm font-medium leading-none cursor-pointer"
                          >
                            {symbol}
                          </label>
                        </div>
                      ))}
                    </div>
                    <FormDescription>
                      Wähle mindestens ein Währungspaar
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Budget */}
              <FormField
                control={form.control}
                name="budget"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Budget (€)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="10000"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value))}
                      />
                    </FormControl>
                    <FormDescription>
                      Startkapital für das Team (mindestens 100€)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Mode Toggle */}
              <FormField
                control={form.control}
                name="mode"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Live-Trading</FormLabel>
                      <FormDescription>
                        Aktiviere Live-Trading mit echtem Geld
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value === 'live'}
                        onCheckedChange={(checked) =>
                          field.onChange(checked ? 'live' : 'paper')
                        }
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              {/* Live Mode Warning */}
              {isLiveMode && (
                <Alert variant="warning">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Warnung: Live-Trading</AlertTitle>
                  <AlertDescription>
                    Live-Trading verwendet echtes Geld. Stelle sicher, dass das Team
                    vorher erfolgreich im Paper-Modus getestet wurde.
                  </AlertDescription>
                </Alert>
              )}

              {/* Submit Button */}
              <div className="flex gap-4">
                <Button
                  type="submit"
                  disabled={createTeam.isPending}
                  className="flex-1"
                >
                  {createTeam.isPending ? 'Erstelle Team...' : 'Team erstellen'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                >
                  Abbrechen
                </Button>
              </div>

              {/* Error Message */}
              {createTeam.isError && (
                <Alert variant="destructive">
                  <AlertTitle>Fehler</AlertTitle>
                  <AlertDescription>
                    {createTeam.error?.message || 'Team konnte nicht erstellt werden'}
                  </AlertDescription>
                </Alert>
              )}
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
