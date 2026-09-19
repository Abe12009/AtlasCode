import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { screen, render } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import { createTestI18n } from '../../../test/i18n-test';
import { GitFileEditor } from '../GitFileEditor';

describe('GitFileEditor', () => {
  it('refreshes the shown content when the selected file\'s authoritative content changes externally', async () => {
    // Regression test: after a merge conflict writes <<<<<<< markers straight
    // into working_files, the editor must show that new content -- not the
    // stale pre-merge text it had when the file was first selected. The
    // draft used to be seeded once from `files` at mount and never resynced.
    //
    // This deliberately does NOT use renderWithProviders' rerender: that
    // helper renders the first pass through a <Routes>/<Route> layer but
    // hands rerender() the bare element, so a rerender lands at a different
    // position in the tree and React remounts GitFileEditor from scratch --
    // which would make this test pass even with the resync effect deleted,
    // since a fresh mount reads the new `files` prop anyway. Rendering
    // GitFileEditor directly, at a stable position, both times is what
    // forces an update (not a remount) and actually exercises the bug.
    const i18n = await createTestI18n();
    const onSave = vi.fn();
    const { rerender } = render(
      <I18nextProvider i18n={i18n}>
        <GitFileEditor files={{ 'config.py': 'DEBUG = True  # staging' }} conflictedFiles={[]} onSave={onSave} />
      </I18nextProvider>
    );

    expect(screen.getByTestId('git-file-editor-textarea')).toHaveValue('DEBUG = True  # staging');

    const conflictContent = "<<<<<<< HEAD\nDEBUG = False\n=======\nDEBUG = True  # staging\n>>>>>>> feature\n";
    rerender(
      <I18nextProvider i18n={i18n}>
        <GitFileEditor files={{ 'config.py': conflictContent }} conflictedFiles={['config.py']} onSave={onSave} />
      </I18nextProvider>
    );

    expect(screen.getByTestId('git-file-editor-textarea')).toHaveValue(conflictContent);
  });
});
