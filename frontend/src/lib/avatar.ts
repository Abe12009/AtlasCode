/**
 * The built-avatar system: a small catalog of original layer choices,
 * serialized as plain JSON (never a rendered image). Storing structured data
 * instead of a picture means:
 *  - it's tiny (a few dozen bytes vs. tens of KB for an image),
 *  - it re-renders crisply at any size,
 *  - the art can be improved later without re-processing every user's avatar,
 *  - there is nothing here resembling a specific real character design —
 *    every shape below is original and generic (circles, simple paths).
 *
 * AvatarFace.tsx is the renderer; AvatarBuilder.tsx is the picker UI.
 */

export interface AvatarConfig {
  skinTone: string;
  hair: string;
  hairColor: string;
  face: string;
  outfit: string;
  accessory: string;
}

export const DEFAULT_AVATAR_CONFIG: AvatarConfig = {
  skinTone: 'tone-3',
  hair: 'short',
  hairColor: 'brown',
  face: 'smile',
  outfit: 'tee',
  accessory: 'none',
};

export const SKIN_TONES: { id: string; label: string; color: string }[] = [
  { id: 'tone-1', label: 'Porcelain', color: '#FFE0BD' },
  { id: 'tone-2', label: 'Fair', color: '#F1C27D' },
  { id: 'tone-3', label: 'Medium', color: '#E0AC69' },
  { id: 'tone-4', label: 'Tan', color: '#C68642' },
  { id: 'tone-5', label: 'Deep', color: '#8D5524' },
  { id: 'tone-6', label: 'Espresso', color: '#5C3A21' },
];

export const HAIR_STYLES: { id: string; label: string }[] = [
  { id: 'bald', label: 'Bald' },
  { id: 'short', label: 'Short' },
  { id: 'buzz', label: 'Buzz' },
  { id: 'curly', label: 'Curly' },
  { id: 'long', label: 'Long' },
  { id: 'bun', label: 'Bun' },
  { id: 'afro', label: 'Afro' },
  { id: 'spiky', label: 'Spiky' },
];

export const HAIR_COLORS: { id: string; color: string }[] = [
  { id: 'black', color: '#2B2118' },
  { id: 'brown', color: '#6B4226' },
  { id: 'blonde', color: '#D9B26F' },
  { id: 'red', color: '#A64B2A' },
  { id: 'gray', color: '#9AA0A6' },
  { id: 'blue', color: '#4C6FE0' },
];

export const FACE_STYLES: { id: string; label: string }[] = [
  { id: 'smile', label: 'Smile' },
  { id: 'grin', label: 'Grin' },
  { id: 'calm', label: 'Calm' },
  { id: 'wink', label: 'Wink' },
  { id: 'glasses', label: 'Glasses' },
  { id: 'shades', label: 'Sunglasses' },
];

export const OUTFITS: { id: string; label: string; color: string }[] = [
  { id: 'tee', label: 'T-Shirt', color: '#3B82F6' },
  { id: 'hoodie', label: 'Hoodie', color: '#7C3AED' },
  { id: 'buttonup', label: 'Button-up', color: '#F8FAFC' },
  { id: 'blazer', label: 'Blazer', color: '#1F2937' },
  { id: 'tank', label: 'Tank Top', color: '#F97316' },
];

export const ACCESSORIES: { id: string; label: string }[] = [
  { id: 'none', label: 'None' },
  { id: 'earrings', label: 'Earrings' },
  { id: 'headphones', label: 'Headphones' },
  { id: 'cap', label: 'Cap' },
  { id: 'beanie', label: 'Beanie' },
];

export function serializeAvatarConfig(config: AvatarConfig): string {
  return JSON.stringify(config);
}

export function parseAvatarConfig(raw: string | null | undefined): AvatarConfig {
  if (!raw) return DEFAULT_AVATAR_CONFIG;
  try {
    const parsed = JSON.parse(raw);
    return { ...DEFAULT_AVATAR_CONFIG, ...parsed };
  } catch {
    return DEFAULT_AVATAR_CONFIG;
  }
}
