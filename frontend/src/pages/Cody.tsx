import { Bot } from 'lucide-react';
import { Card } from '../components/ui';
import { CodyChatPanel } from '../components/CodyChatPanel';

export function Cody() {
  return (
    <div className="max-w-3xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center gap-3 mb-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
          <Bot className="h-5 w-5 text-white" aria-hidden="true" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-text-primary">Cody</h1>
          <p className="text-sm text-text-tertiary">Your computer science companion</p>
        </div>
      </div>

      <Card padding="none" className="flex-1 min-h-0 flex flex-col overflow-hidden">
        <CodyChatPanel className="flex-1 min-h-0" />
      </Card>
    </div>
  );
}
