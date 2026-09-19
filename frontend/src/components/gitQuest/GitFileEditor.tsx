import { useEffect, useState } from 'react';
import { Plus, AlertTriangle } from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';
import { Button, cn } from '../ui';

interface GitFileEditorProps {
  files: Record<string, string>;
  conflictedFiles: string[];
  onSave: (file: string, content: string) => void;
}

/**
 * The working directory: a file list plus a plain-text editor for the
 * selected one. Not a real code editor (no syntax highlighting) -- Git
 * Quest's files are short and the point is the git workflow, not the code.
 * Real git has no "edit" command; this is the mechanics real git leaves to
 * "your text editor," made explicit as its own panel rather than overloaded
 * onto the terminal's command line.
 */
export function GitFileEditor({ files, conflictedFiles, onSave }: GitFileEditorProps) {
  const { t } = useTranslation();
  const fileNames = Object.keys(files);
  const [selected, setSelected] = useState<string | null>(fileNames[0] ?? null);
  const [draft, setDraft] = useState<string>(selected ? files[selected] : '');
  const [newFileName, setNewFileName] = useState('');
  const [addingFile, setAddingFile] = useState(false);

  // The selected file's *authoritative* content can change for reasons this
  // panel didn't cause -- most importantly, a merge conflict writes
  // <<<<<<< markers straight into working_files. Without this, the draft
  // shown (and the stale pre-conflict content the student would then "save"
  // right back) never picks that up, since `selected` stays the same file
  // and a bare useState only reads `files` once, at mount.
  useEffect(() => {
    if (selected) setDraft(files[selected] ?? '');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, selected ? files[selected] : undefined]);

  const selectFile = (name: string) => {
    setSelected(name);
  };

  const save = () => {
    if (!selected) return;
    onSave(selected, draft);
  };

  const createFile = () => {
    const name = newFileName.trim();
    if (!name) return;
    onSave(name, '');
    setSelected(name);
    setDraft('');
    setNewFileName('');
    setAddingFile(false);
  };

  return (
    <div className="border border-border-primary rounded-xl overflow-hidden" dir="ltr">
      <div className="flex items-center justify-between px-3 py-2 bg-bg-secondary border-b border-border-primary">
        <span className="text-xs font-semibold uppercase tracking-wide text-text-quaternary">
          {t('git_quest.working_directory')}
        </span>
        <button
          type="button"
          onClick={() => setAddingFile((v) => !v)}
          className="p-1 rounded hover:bg-bg-tertiary text-text-tertiary hover:text-text-primary"
          aria-label={t('git_quest.new_file')}
          data-testid="git-new-file-button"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {addingFile && (
        <div className="flex items-center gap-2 px-3 py-2 border-b border-border-primary bg-bg-secondary/50">
          <input
            type="text"
            value={newFileName}
            onChange={(e) => setNewFileName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && createFile()}
            placeholder={t('git_quest.new_file_placeholder')}
            className="flex-1 bg-bg-primary border border-border-primary rounded-lg px-2 py-1 text-sm text-text-primary focus:outline-none focus:border-primary-500"
            data-testid="git-new-file-input"
            autoFocus
          />
          <Button size="sm" onClick={createFile}>{t('git_quest.create')}</Button>
        </div>
      )}

      <div className="flex flex-wrap gap-1 p-2 border-b border-border-primary">
        {fileNames.length === 0 && (
          <span className="text-sm text-text-quaternary px-1">{t('git_quest.no_files_yet')}</span>
        )}
        {fileNames.map((name) => {
          const conflicted = conflictedFiles.includes(name);
          return (
            <button
              key={name}
              type="button"
              onClick={() => selectFile(name)}
              data-testid={`git-file-tab-${name}`}
              className={cn(
                'px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1 transition-colors',
                selected === name ? 'bg-primary-500/15 text-primary-400 border border-primary-500/40' : 'text-text-tertiary hover:bg-bg-secondary',
                conflicted && 'border border-warning-500/60',
              )}
            >
              {conflicted && <AlertTriangle className="h-3 w-3 text-warning-500" />}
              {name}
            </button>
          );
        })}
      </div>

      {selected && (
        <div className="p-2 space-y-2">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={8}
            className="w-full rounded-lg bg-bg-code text-gray-100 font-mono text-sm p-3 focus:outline-none resize-y"
            data-testid="git-file-editor-textarea"
            spellCheck={false}
          />
          <Button size="sm" onClick={save} data-testid="git-file-save-button">
            {t('git_quest.save_file')}
          </Button>
        </div>
      )}
    </div>
  );
}
