import { Card, CardContent, Input } from '../components/ui';

export function TestWithInput() {
  return (
    <Card>
      <CardContent className="space-y-6">
        <form>
          <Input
            label="Email"
            type="email"
            id="email"
            name="email"
            autoComplete="email"
            required
            value=""
            onChange={() => {}}
            placeholder="you@example.com"
            disabled={false}
          />
          <Input
            label="Password"
            type="password"
            id="password"
            name="password"
            autoComplete="current-password"
            required
            value=""
            onChange={() => {}}
            placeholder="••••••••"
            disabled={false}
          />
        </form>
      </CardContent>
    </Card>
  );
}