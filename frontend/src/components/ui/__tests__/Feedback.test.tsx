import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Progress } from '../Feedback';

describe('Progress', () => {
  it('shows the percentage exactly once when only showLabel is set', () => {
    render(<Progress value={57} max={100} showLabel />);

    expect(screen.getAllByText('57%')).toHaveLength(1);
  });

  it('shows only the custom label when label is set without showLabel', () => {
    render(<Progress value={57} max={100} label="42/100 XP to next level" />);

    expect(screen.getByText('42/100 XP to next level')).toBeInTheDocument();
    expect(screen.queryByText('57%')).not.toBeInTheDocument();
  });

  it('shows the custom label and the percentage once each when both are set', () => {
    // Regression test: label and showLabel together used to render the
    // percentage twice (once as the label's own fallback, once from
    // showLabel) whenever no distinct label text was given, and any
    // caller whose label itself was a percentage string (e.g.
    // LessonDetail.tsx's old `label={`${pct}%`}`) duplicated visibly.
    render(<Progress value={57} max={100} label="42/100 XP to next level" showLabel />);

    expect(screen.getAllByText('42/100 XP to next level')).toHaveLength(1);
    expect(screen.getAllByText('57%')).toHaveLength(1);
  });

  it('renders no label row when neither label nor showLabel is set', () => {
    render(<Progress value={57} max={100} />);

    expect(screen.queryByText('57%')).not.toBeInTheDocument();
  });
});
