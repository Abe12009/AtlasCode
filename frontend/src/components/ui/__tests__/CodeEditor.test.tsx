import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../test/setup.tsx';
import { CodeEditor } from '../CodeEditor';

describe('CodeEditor', () => {
  it('renders the toolbar with filename, language, and a status dot', async () => {
    await renderWithProviders(<CodeEditor code="print(1)" onChange={() => {}} language="python" />);
    expect(screen.getByText('solution.py')).toBeInTheDocument();
    expect(screen.getByText('python')).toBeInTheDocument();
    expect(screen.getByTestId('code-editor-status-dot')).toBeInTheDocument();
  });

  it('shows the run button and calls onRun when clicked', async () => {
    const user = userEvent.setup();
    const onRun = vi.fn();
    await renderWithProviders(<CodeEditor code="" onChange={() => {}} onRun={onRun} />);
    await user.click(screen.getByTestId('code-editor-run-btn'));
    expect(onRun).toHaveBeenCalled();
  });

  it('renders the given code inside the editor', async () => {
    await renderWithProviders(<CodeEditor code="print('hello')" onChange={() => {}} />);
    expect(screen.getByTestId('code-editor')).toHaveTextContent("print('hello')");
  });

  it('calls onChange when the user types', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    await renderWithProviders(<CodeEditor code="" onChange={onChange} />);
    const editor = screen.getByTestId('code-editor').querySelector('.cm-content') as HTMLElement;
    editor.focus();
    await user.type(editor, 'x');
    expect(onChange).toHaveBeenCalled();
  });

  it('omits the toolbar when showToolbar is false', async () => {
    await renderWithProviders(<CodeEditor code="" onChange={() => {}} showToolbar={false} />);
    expect(screen.queryByText('solution.py')).not.toBeInTheDocument();
  });
});
