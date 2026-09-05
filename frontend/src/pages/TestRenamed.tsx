import { Card, CardContent as CC, Input, Button } from '../components/ui';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { Code } from 'lucide-react';

export function TestRenamed() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-secondary px-4 py-12">
      <div className="w-full max-w-md">
        <Card className="w-full">
          <CC className="space-y-6">
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

            <Button fullWidth>Sign in</Button>

            <div className="grid grid-cols-2 gap-3">
              <Button variant="outline" fullWidth>Google</Button>
              <Button variant="outline" fullWidth>GitHub</Button>
            </div>

            <div className="text-center mt-6">
              <p className="text-text-secondary">
                Don't have an account?{' '}
                <Link to="/register" className="text-accent-primary hover:text-accent-primary-hover font-medium">
                  Sign up
                </Link>
              </p>
            </div>
          </CC>
        </Card>
      </div>
    </div>
  );
}