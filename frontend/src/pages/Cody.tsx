import { Card } from '../components/ui';
import { CodyChatPanel } from '../components/CodyChatPanel';
import { CodyCharacter } from '../components/CodyCharacter';

export function Cody() {
  return (
    <div className="max-w-3xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center gap-3 mb-4">
        <CodyCharacter size={40} aria-hidden="true" />
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
