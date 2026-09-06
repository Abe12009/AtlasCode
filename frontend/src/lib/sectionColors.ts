/**
 * Per-section accent colors for the course catalog (light mode only — dark
 * mode keeps the neutral/primary treatment already in place). Keyed by the
 * Section slug seeded in backend/app/seed/sections.py; a slug with no entry
 * here falls back to the neutral default so a new section never breaks.
 */
export interface SectionColor {
  bg: string;
  border: string;
  text: string;
}

const SECTION_COLORS: Record<string, SectionColor> = {
  programming: { bg: '#EAF1FE', border: '#3B6FE0', text: '#2347A8' },
  'data-structures-algorithms': { bg: '#EAF7EE', border: '#2E9E52', text: '#1E6B38' },
  'computer-systems': { bg: '#F3EEFC', border: '#7B4FE0', text: '#4E2FA8' },
  networking: { bg: '#EAF6F7', border: '#1D95A8', text: '#146A78' },
  databases: { bg: '#FDF1E7', border: '#D9822B', text: '#96591A' },
  'software-engineering': { bg: '#FCEEEE', border: '#D9483F', text: '#96261F' },
  'ai-machine-learning': { bg: '#F7EEFB', border: '#A83FC9', text: '#6E1F8A' },
  cybersecurity: { bg: '#E3E8F0', border: '#24344F', text: '#182338' },
};

const DEFAULT_COLOR: SectionColor = { bg: '#F1EEFC', border: '#5B3FE0', text: '#3B23A8' };

export function getSectionColor(slug: string | null | undefined): SectionColor {
  if (!slug) return DEFAULT_COLOR;
  return SECTION_COLORS[slug] ?? DEFAULT_COLOR;
}
