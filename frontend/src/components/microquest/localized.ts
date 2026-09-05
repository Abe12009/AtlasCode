import type { LocalizedText } from './types';

/** Resolve a per-language string from a block's config.
 *
 * Config carries structured data (step labels, pair sides, hints), so unlike
 * block prose it is not stored in lesson_block_translations — each value holds
 * every language inline. English is the guaranteed fallback. */
export function localized(text: LocalizedText | undefined, language: string): string {
  if (!text) return '';
  return text[language] ?? text.en ?? '';
}
