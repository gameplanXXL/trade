---
epic: 008
story: 05
title: "Team-Erstellung via UI"
status: backlog
story_points: 3
covers: [FR45, FR48]
---

## Story 8.5: Team-Erstellung via UI

Als Operator,
möchte ich neue Team-Instanzen über die UI erstellen,
damit ich ohne CLI neue Teams starten kann.

**Acceptance Criteria:**

**Given** Dashboard und REST-API
**When** ich TeamCreate implementiere
**Then** existiert `src/features/teams/TeamCreate.tsx`:
```tsx
export function TeamCreate() {
  const { templates } = useTemplates();
  const createTeam = useCreateTeam();

  const form = useForm<TeamCreateInput>({
    defaultValues: {
      name: '',
      template_name: 'conservative_llm',
      symbols: ['EUR/USD'],
      budget: 10000,
      mode: 'paper',
    },
  });

  const onSubmit = async (data: TeamCreateInput) => {
    await createTeam.mutateAsync(data);
    navigate('/dashboard');
  };

  return (
    <Form {...form}>
      <FormField name="name" label="Team-Name" />
      <FormField name="template_name" label="Template" type="select" options={templates} />
      <FormField name="symbols" label="Symbole" type="multi-select" />
      <FormField name="budget" label="Budget (€)" type="number" />
      <FormField name="mode" label="Modus" type="toggle" options={['paper', 'live']} />

      {form.watch('mode') === 'live' && (
        <Alert variant="warning">
          Live-Trading verwendet echtes Geld. Nur nach erfolgreicher Paper-Phase empfohlen.
        </Alert>
      )}

      <Button type="submit">Team erstellen</Button>
    </Form>
  );
}
```

**And** Validation:
  - Name: Required, 3-50 Zeichen
  - Budget: Min 100€
  - Symbols: Min 1

**And** Template-Preview zeigt Rollen und Pipeline

**Technical Notes:**
- React Hook Form für Form-Handling
- Zod für Validation
- Optimistic Update nach Submit

**Prerequisites:** Story 5.3, Story 7.3

