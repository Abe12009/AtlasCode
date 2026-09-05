import type { Exercise, ExerciseSubmitRequest } from '../types';

export type SubmitVars = { exerciseId: number } & Omit<ExerciseSubmitRequest, 'exercise_id'>;

/** Exercise types answered by writing and running code. Everything else is
 * answered directly, so it gets a real answer widget instead of an editor. */
export const CODE_EXERCISE_TYPES = ['code_writing', 'debugging', 'visual_programming'];

export function isCodeExercise(exercise: Exercise): boolean {
  return CODE_EXERCISE_TYPES.includes(exercise.exercise_type);
}
