/** A lesson whose exercises exercise every non-code answer UI.
 *
 * Note what is deliberately absent from every option: `is_correct`. The API
 * stops sending it, so the UI genuinely cannot know the answer before the
 * backend replies — these fixtures mirror that contract.
 */
export const mockMcqLesson = {
  id: 61,
  slug: 'arrays-and-objects',
  order: 1,
  difficulty: 'beginner',
  estimated_minutes: 25,
  xp_reward: 50,
  is_project: false,
  translations: [
    {
      language: 'en',
      title: 'Arrays and Objects',
      story: 'Learn arrays and objects',
      objective: 'Create and access arrays and objects',
      skills: 'Arrays, Objects',
    },
    {
      language: 'fr',
      title: 'Tableaux et Objets',
      story: 'Apprenez les tableaux',
      objective: 'Créer et accéder aux tableaux',
      skills: 'Tableaux, Objets',
    },
    {
      language: 'ar',
      title: 'المصفوفات والكائنات',
      story: 'تعلم المصفوفات',
      objective: 'إنشاء المصفوفات والوصول إليها',
      skills: 'المصفوفات، الكائنات',
    },
  ],
  blocks: [
    {
      id: 900,
      block_type: 'text',
      order: 1,
      content: 'Arrays hold ordered lists.',
      code_example: null,
      translations: [
        { language: 'en', content: 'Arrays hold ordered lists.', code_example: null },
      ],
    },
  ],
  exercises: [
    {
      id: 601,
      exercise_type: 'multiple_choice',
      order: 1,
      xp_reward: 10,
      starter_code: null,
      translations: [
        {
          language: 'en',
          prompt: 'What does destructuring do?',
          hint: 'Think about pulling values out',
          explanation: 'It extracts values into variables.',
        },
      ],
      options: [
        { id: 9001, order: 1, translations: [{ language: 'en', text: 'It deletes the object' }] },
        { id: 9002, order: 2, translations: [{ language: 'en', text: 'It extracts values into variables' }] },
        { id: 9003, order: 3, translations: [{ language: 'en', text: 'It sorts the array' }] },
        { id: 9004, order: 4, translations: [{ language: 'en', text: 'It converts to a string' }] },
      ],
    },
  ],
};

/** Same lesson shape, but the single exercise is a prediction. */
export const mockPredictionLesson = {
  ...mockMcqLesson,
  id: 62,
  exercises: [
    {
      id: 602,
      exercise_type: 'prediction',
      order: 1,
      xp_reward: 10,
      starter_code: 'print("Line 1")\nprint("Line 2")',
      translations: [
        {
          language: 'en',
          prompt: 'What will this code print?',
          hint: 'One line per print',
          explanation: 'Each print writes a line.',
        },
      ],
      options: [],
    },
  ],
};

/** Same lesson shape, but the single exercise is a fill-in-the-blank. */
export const mockFillBlankLesson = {
  ...mockMcqLesson,
  id: 63,
  exercises: [
    {
      id: 603,
      exercise_type: 'fill_blank',
      order: 1,
      xp_reward: 10,
      starter_code: 'student_name = "____"\nstudent_age = ____',
      translations: [
        {
          language: 'en',
          prompt: 'Fill in the blanks.',
          hint: 'Text goes in quotes',
          explanation: 'Strings are quoted.',
        },
      ],
      options: [],
    },
  ],
};

export function submitResponse(overrides: Record<string, unknown> = {}) {
  return {
    is_correct: false,
    xp_earned: 0,
    feedback: 'That is not the right answer.',
    output: '',
    error: 'Incorrect answer',
    is_completed: false,
    lesson_completed: false,
    ...overrides,
  };
}
