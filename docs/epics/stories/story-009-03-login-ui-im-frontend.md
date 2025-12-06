---
epic: 009
story: 03
title: "Login-UI im Frontend"
status: completed
story_points: 3
covers: [FR50]
---

## Story 9.3: Login-UI im Frontend

Als Operator,
möchte ich eine Login-Seite,
damit ich mich am Dashboard anmelden kann.

**Acceptance Criteria:**

**Given** Auth-API
**When** ich Login-UI implementiere
**Then** existiert `src/features/auth/LoginForm.tsx`:
```tsx
export function LoginForm() {
  const login = useLogin();
  const form = useForm<LoginInput>();

  const onSubmit = async (data: LoginInput) => {
    try {
      await login.mutateAsync(data);
      navigate('/dashboard');
    } catch (error) {
      form.setError('root', { message: 'Ungültige Anmeldedaten' });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Trading Platform</CardTitle>
          <CardDescription>Melde dich an, um fortzufahren</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <FormField name="username" label="Benutzername" />
            <FormField name="password" label="Passwort" type="password" />
            {form.formState.errors.root && (
              <Alert variant="destructive">{form.formState.errors.root.message}</Alert>
            )}
            <Button type="submit" className="w-full" disabled={login.isPending}>
              {login.isPending ? <Spinner /> : 'Anmelden'}
            </Button>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
```

**And** Auth-State in Zustand Store
**And** Protected Routes redirecten zu Login
**And** Automatischer Logout bei 401

**Technical Notes:**
- Cookie wird automatisch bei Requests gesendet
- Axios Interceptor für 401-Handling
- Remember-Me optional (längere Session)

**Prerequisites:** Story 1.5, 9.2

