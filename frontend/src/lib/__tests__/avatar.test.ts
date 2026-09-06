import { describe, it, expect } from 'vitest';
import {
  DEFAULT_AVATAR_CONFIG,
  parseAvatarConfig,
  serializeAvatarConfig,
  SKIN_TONES,
  HAIR_STYLES,
  HAIR_COLORS,
  FACE_STYLES,
  OUTFITS,
  ACCESSORIES,
  type AvatarConfig,
} from '../avatar';

describe('avatar config serialization', () => {
  it('round-trips a config through serialize/parse', () => {
    const config: AvatarConfig = {
      skinTone: 'tone-5',
      hair: 'curly',
      hairColor: 'red',
      face: 'grin',
      outfit: 'hoodie',
      accessory: 'cap',
    };
    const parsed = parseAvatarConfig(serializeAvatarConfig(config));
    expect(parsed).toEqual(config);
  });

  it('falls back to the default config for null/undefined input', () => {
    expect(parseAvatarConfig(null)).toEqual(DEFAULT_AVATAR_CONFIG);
    expect(parseAvatarConfig(undefined)).toEqual(DEFAULT_AVATAR_CONFIG);
    expect(parseAvatarConfig('')).toEqual(DEFAULT_AVATAR_CONFIG);
  });

  it('falls back to the default config for malformed JSON rather than throwing', () => {
    expect(() => parseAvatarConfig('{not valid json')).not.toThrow();
    expect(parseAvatarConfig('{not valid json')).toEqual(DEFAULT_AVATAR_CONFIG);
  });

  it('fills in missing fields from an older/partial saved config', () => {
    const partial = JSON.stringify({ skinTone: 'tone-1' });
    const parsed = parseAvatarConfig(partial);
    expect(parsed.skinTone).toBe('tone-1');
    expect(parsed.hair).toBe(DEFAULT_AVATAR_CONFIG.hair);
    expect(parsed.face).toBe(DEFAULT_AVATAR_CONFIG.face);
  });

  it('every default config value is a real option in its own catalog', () => {
    expect(SKIN_TONES.some((t) => t.id === DEFAULT_AVATAR_CONFIG.skinTone)).toBe(true);
    expect(HAIR_STYLES.some((h) => h.id === DEFAULT_AVATAR_CONFIG.hair)).toBe(true);
    expect(HAIR_COLORS.some((c) => c.id === DEFAULT_AVATAR_CONFIG.hairColor)).toBe(true);
    expect(FACE_STYLES.some((f) => f.id === DEFAULT_AVATAR_CONFIG.face)).toBe(true);
    expect(OUTFITS.some((o) => o.id === DEFAULT_AVATAR_CONFIG.outfit)).toBe(true);
    expect(ACCESSORIES.some((a) => a.id === DEFAULT_AVATAR_CONFIG.accessory)).toBe(true);
  });

  it('every catalog entry has a unique id', () => {
    for (const catalog of [SKIN_TONES, HAIR_STYLES, HAIR_COLORS, FACE_STYLES, OUTFITS, ACCESSORIES]) {
      const ids = catalog.map((entry) => entry.id);
      expect(new Set(ids).size).toBe(ids.length);
    }
  });
});
