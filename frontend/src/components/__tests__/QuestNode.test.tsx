import React from 'react';
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../test/setup.tsx';
import { QuestRoadmap, type QuestNodeData } from '../QuestNode';

const NODE: QuestNodeData = {
  id: 'n1',
  title: 'Loops',
  type: 'lesson',
  status: 'completed',
};

function nodeCircle(title: string): HTMLElement {
  // The circle is the title's ancestor with the size-setting inline style;
  // its rounded-full class carries the state-specific color/border classes.
  const heading = screen.getByText(title);
  const wrapper = heading.closest('div.relative.flex.flex-col.items-center.transition-all')!;
  return wrapper.querySelector('.rounded-full') as HTMLElement;
}

describe('QuestRoadmap node states', () => {
  it('renders a completed node as solid blue with a checkmark', async () => {
    await renderWithProviders(<QuestRoadmap nodes={[{ ...NODE, status: 'completed' }]} />);
    const circle = nodeCircle('Loops');
    expect(circle.className).toContain('bg-primary-500');
    expect(circle.className).toContain('border-primary-500');
    expect(circle.className).not.toContain('border-dashed');
  });

  it('renders the current node larger, with an orange ring and glow', async () => {
    await renderWithProviders(<QuestRoadmap nodes={[{ ...NODE, status: 'current' }]} />);
    const circle = nodeCircle('Loops');
    expect(circle.className).toContain('bg-accent-500');
    expect(circle.className).toContain('shadow-glow-accent');
    expect(circle.className).toContain('ring-accent-500/30');
    // Larger than the base 56px horizontal size.
    expect(circle.style.width).toBe('68px');
  });

  it('renders a locked node with a dashed border and a lock icon, not the emoji', async () => {
    await renderWithProviders(<QuestRoadmap nodes={[{ ...NODE, status: 'locked' }]} />);
    const circle = nodeCircle('Loops');
    expect(circle.className).toContain('border-dashed');
    expect(circle.querySelector('svg.lucide-lock')).toBeInTheDocument();
    expect(circle.textContent).not.toContain('🔒');
  });

  it('renders an available node with plain outline styling -- no dash, no lock, no glow', async () => {
    await renderWithProviders(<QuestRoadmap nodes={[{ ...NODE, status: 'available' }]} />);
    const circle = nodeCircle('Loops');
    expect(circle.className).not.toContain('border-dashed');
    expect(circle.className).not.toContain('shadow-glow');
    expect(circle.querySelector('svg.lucide-lock')).not.toBeInTheDocument();
    expect(circle.querySelector('svg.lucide-check-circle')).not.toBeInTheDocument();
  });

  it('connects a completed node to the next with a blue line, distinct from the default gray connector', async () => {
    await renderWithProviders(
      <QuestRoadmap
        nodes={[
          { ...NODE, id: 'a', title: 'A', status: 'completed' },
          { ...NODE, id: 'b', title: 'B', status: 'locked' },
        ]}
      />
    );
    const list = screen.getByRole('list', { name: 'Learning roadmap' });
    const connectors = list.querySelectorAll('[aria-hidden="true"].absolute');
    expect(connectors.length).toBeGreaterThan(0);
    expect(connectors[0]).toHaveStyle({ background: 'linear-gradient(90deg, var(--color-primary-500), var(--color-primary-500))' });
  });
});
