/**
 * THE BLUEPRINT CONTRACT
 * =======================
 * Every blueprint interaction (order_steps, match_pairs, spot_the_bug, and
 * whatever comes next) is three things, each owned by exactly one place:
 *
 *   1. A typed config shape, defined here (e.g. `SpotTheBugConfig`) — the
 *      author-facing data the backend serves as JSON.
 *   2. A validating type guard, defined here next to its shape (e.g.
 *      `isSpotTheBugConfig`) — the only thing allowed to say "this parsed
 *      JSON is actually safe to render as an X". Never trust `config.kind`
 *      alone; a guard checks every field the component depends on.
 *   3. A component, one file under `microquest/`, that owns everything about
 *      showing and playing that one puzzle: its own interaction state (which
 *      item is selected, what's been tried), its own correct-answer check
 *      (comparing against the config, never asking the server), text through
 *      `localized(value, language)` so every string honours the block's
 *      per-language config, an accessible *native* control where one exists
 *      (a real `<input type="radio">`/`<button>`, not a styled `<div>`; see
 *      SpotTheBugBlueprint and the MCQ answer panel it mirrors), and layout
 *      that holds up at 320px (min-w-0, break-words, no fixed widths).
 *      Its only link back to the lesson is `solved` (in) and `onSolved` (out)
 *      — it never reads or writes anything else about lesson state.
 *
 * `Blueprint.tsx` is the only file that maps `config.kind` to a component —
 * everything else, including `MicroQuestLesson.tsx`, treats "which blueprint
 * is this" as none of its business and only ever renders `<Blueprint config=
 * {...} .../>`. A config Blueprint.tsx's guards don't recognise renders its
 * `UnsupportedBlueprint` fallback and unlocks the quest instead of crashing —
 * a broken warm-up must never strand a student in front of a lesson they
 * cannot finish.
 */

/** A string keyed by language code ('en' | 'fr' | 'ar'), always with an 'en' fallback. */
export type LocalizedText = Record<string, string>;

export interface HookConfig {
  kind: 'hook';
  challenge: LocalizedText;
  learn: LocalizedText;
}

export interface BlueprintStep {
  id: string;
  label: LocalizedText;
}

/** "Put these plain-language steps in the order a program runs them." */
export interface OrderStepsConfig {
  kind: 'order_steps';
  steps: BlueprintStep[];
  correct_order: string[];
  success?: LocalizedText;
  hint?: LocalizedText;
}

/** One concept and the meaning it belongs to. The pairing *is* the answer:
 * left and right of the same object go together. */
export interface MatchPair {
  id: string;
  left: LocalizedText;
  right: LocalizedText;
}

/** "Connect each concept to what it actually does." */
export interface MatchPairsConfig {
  kind: 'match_pairs';
  pairs: MatchPair[];
  success?: LocalizedText;
  hint?: LocalizedText;
}

/** One claim about the concept being taught, true or false. Exactly one of a
 * `SpotTheBugConfig`'s statements is wrong; the rest are correct. */
export interface BugStatement {
  id: string;
  text: LocalizedText;
}

/** "Read these claims about how the code behaves. Exactly one is wrong — which
 * one?" A single-select puzzle, mechanically distinct from both reordering
 * (order_steps) and pairwise connecting (match_pairs): the student picks one
 * item out of several rather than arranging or linking them. It teaches the
 * habit a debugging exercise actually asks for — read a claim about the code
 * critically and decide whether it holds — without stating what the fix is. */
export interface SpotTheBugConfig {
  kind: 'spot_the_bug';
  /** Optional code shown above the statements, for context. Rendered through
   * the shared CodeBlock, so it stays LTR under Arabic RTL like every other
   * code sample. */
  snippet?: string;
  statements: BugStatement[];
  /** The one statement id that is actually false. */
  buggy_id: string;
  success?: LocalizedText;
  hint?: LocalizedText;
}

/** Every blueprint interaction this build can render. */
export type BlueprintConfig = OrderStepsConfig | MatchPairsConfig | SpotTheBugConfig;

/** Whatever JSON.parse actually returned. A lesson authored later may carry a
 * `kind` this build has never heard of, or a config that lost a field, so the
 * parsed value is only narrowed to a real config by the guards below — the
 * renderer falls back instead of crashing the lesson. */
export type AnyBlueprintConfig = Record<string, unknown>;

export interface ExamTipConfig {
  kind: 'exam_tip';
}

function isLocalizedText(value: unknown): value is LocalizedText {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false;
  const entries = Object.entries(value as Record<string, unknown>);
  return entries.length > 0 && entries.every(([, text]) => typeof text === 'string');
}

function isNonEmptyId(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** True only for a config this build can actually render as an ordering puzzle:
 * at least two identified steps, and a correct order that is a permutation of
 * exactly those steps. */
export function isOrderStepsConfig(config: unknown): config is OrderStepsConfig {
  if (!isObject(config) || config.kind !== 'order_steps') return false;
  const { steps, correct_order: correctOrder } = config as Partial<OrderStepsConfig>;
  if (!Array.isArray(steps) || steps.length < 2) return false;
  if (!steps.every((step) => isNonEmptyId(step?.id) && isLocalizedText(step?.label))) return false;
  if (!Array.isArray(correctOrder) || correctOrder.length !== steps.length) return false;
  const ids = new Set(steps.map((step) => step.id));
  if (ids.size !== steps.length) return false;
  return correctOrder.every(isNonEmptyId) && new Set(correctOrder).size === ids.size
    && correctOrder.every((id) => ids.has(id));
}

/** True only for a config this build can render as a matching puzzle: at least
 * two uniquely identified pairs, each with both sides written in every
 * language the lesson ships. */
export function isMatchPairsConfig(config: unknown): config is MatchPairsConfig {
  if (!isObject(config) || config.kind !== 'match_pairs') return false;
  const { pairs } = config as Partial<MatchPairsConfig>;
  if (!Array.isArray(pairs) || pairs.length < 2) return false;
  if (!pairs.every((pair) => isNonEmptyId(pair?.id) && isLocalizedText(pair?.left) && isLocalizedText(pair?.right))) {
    return false;
  }
  return new Set(pairs.map((pair) => pair.id)).size === pairs.length;
}

/** True only for a config this build can render as a spot-the-bug puzzle: at
 * least three uniquely identified statements, each localized, with exactly
 * one designated as the buggy one. */
export function isSpotTheBugConfig(config: unknown): config is SpotTheBugConfig {
  if (!isObject(config) || config.kind !== 'spot_the_bug') return false;
  const { statements, buggy_id: buggyId, snippet } = config as Partial<SpotTheBugConfig>;
  if (snippet !== undefined && typeof snippet !== 'string') return false;
  if (!Array.isArray(statements) || statements.length < 3) return false;
  if (!statements.every((s) => isNonEmptyId(s?.id) && isLocalizedText(s?.text))) return false;
  const ids = new Set(statements.map((s) => s.id));
  if (ids.size !== statements.length) return false;
  return isNonEmptyId(buggyId) && ids.has(buggyId);
}

/** Quest stages, in the order a student reaches them. The array order *is* the
 * ranking used to decide which of two stages is further along. */
export const QUEST_STAGES = ['hook', 'blueprint', 'quest', 'complete'] as const;

export type QuestStage = (typeof QUEST_STAGES)[number];

export function isQuestStage(value: unknown): value is QuestStage {
  return typeof value === 'string' && (QUEST_STAGES as readonly string[]).includes(value);
}

/** The further of two stages. Progress only ever moves forward. */
export function furthestStage(a: QuestStage, b: QuestStage): QuestStage {
  return QUEST_STAGES.indexOf(a) >= QUEST_STAGES.indexOf(b) ? a : b;
}
