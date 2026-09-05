import type { MatchPair } from './types';

/**
 * Deterministic shuffle of the right-hand column.
 *
 * The pairing is only a puzzle if the two columns disagree, but a random
 * column would differ on every render and every language switch. Seeding from
 * the pair ids gives one fixed arrangement per blueprint, computed the same
 * way in the browser and in the tests.
 */
export function shuffledRight(pairs: MatchPair[]): MatchPair[] {
  let seed = 2166136261;
  for (const character of pairs.map((pair) => pair.id).join('|')) {
    seed = Math.imul(seed ^ character.charCodeAt(0), 16777619) >>> 0;
  }
  const nextRandom = () => {
    seed = (seed + 0x6d2b79f5) >>> 0;
    let t = seed;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  const out = [...pairs];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(nextRandom() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  // A right column in the same order as the left one would let a student match
  // row by row without reading a word, so rotate that arrangement out.
  if (out.every((pair, index) => pair.id === pairs[index].id)) {
    out.push(out.shift() as MatchPair);
  }
  return out;
}

