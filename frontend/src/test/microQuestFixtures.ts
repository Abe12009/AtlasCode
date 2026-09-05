/** A lesson shaped like the real Micro-Quest reference lesson (lesson 9):
 * hook -> reading blocks -> blueprint -> exam_tip -> one code exercise. */
export const mockMicroQuestLesson = {
  id: 9,
  slug: 'problem-solving-control-flow',
  order: 4,
  difficulty: 'intermediate',
  estimated_minutes: 10,
  xp_reward: 60,
  is_project: false,
  translations: [
    {
      language: 'en',
      title: 'Problem Solving with Control Flow',
      story: 'Combine conditions and loops',
      objective: 'Solve problems by combining if/else with loops',
      skills: 'Algorithmic thinking',
    },
    {
      language: 'fr',
      title: 'Résolution de Problèmes avec le Contrôle de Flux',
      story: 'Combinez conditions et boucles',
      objective: 'Résoudre des problèmes',
      skills: 'Pensée algorithmique',
    },
    {
      language: 'ar',
      title: 'حل المشكلات مع التحكم في التدفق',
      story: 'اجمع الشروط والحلقات',
      objective: 'حل المشكلات',
      skills: 'التفكير الخوارزمي',
    },
  ],
  blocks: [
    {
      id: 900,
      block_type: 'hook',
      order: 0,
      content: 'A school needs the total of every even-numbered locker.',
      code_example: null,
      config: JSON.stringify({
        kind: 'hook',
        challenge: {
          en: 'How can a program add up only the numbers it wants, automatically?',
          fr: 'Comment un programme peut-il additionner seulement les nombres voulus, automatiquement ?',
          ar: 'كيف يمكن لبرنامج أن يجمع الأعداد التي يريدها فقط تلقائيًا؟',
        },
        learn: {
          en: 'You will combine a loop with a condition to build a running total.',
          fr: "Vous allez combiner une boucle et une condition pour construire un total cumulé.",
          ar: 'ستجمع بين حلقة وشرط لبناء مجموع تراكمي.',
        },
      }),
      translations: [
        { language: 'en', content: 'A school needs the total of every even-numbered locker.', code_example: null },
        { language: 'fr', content: 'Une école a besoin du total de tous les casiers pairs.', code_example: null },
        { language: 'ar', content: 'تحتاج مدرسة إلى مجموع كل الخزانات ذات الأرقام الزوجية.', code_example: null },
      ],
    },
    {
      id: 901,
      block_type: 'text',
      order: 1,
      content: 'Real programming problems often need both decisions and repetition.',
      code_example: null,
      config: null,
      translations: [
        { language: 'en', content: 'Real programming problems often need both decisions and repetition.', code_example: null },
      ],
    },
    {
      id: 902,
      block_type: 'code',
      order: 2,
      content: 'Finding the largest number:',
      code_example: 'numbers = [15, 42, 8]\nlargest = numbers[0]',
      config: null,
      translations: [
        { language: 'en', content: 'Finding the largest number:', code_example: 'numbers = [15, 42, 8]\nlargest = numbers[0]' },
      ],
    },
    {
      id: 903,
      block_type: 'blueprint',
      order: 4,
      content: 'Put the four steps of the pattern in the order a program would run them.',
      code_example: null,
      config: JSON.stringify({
        kind: 'order_steps',
        steps: [
          { id: 'init', label: { en: 'Start a total at zero', fr: 'Démarrer un total à zéro', ar: 'ابدأ بمجموع قيمته صفر' } },
          { id: 'visit', label: { en: 'Look at the next number', fr: 'Passer au nombre suivant', ar: 'انتقل إلى العدد التالي' } },
          { id: 'decide', label: { en: 'Ask: is this number even?', fr: 'Se demander : ce nombre est-il pair ?', ar: 'اسأل: هل هذا العدد زوجي؟' } },
          { id: 'update', label: { en: 'If it is, add it to the total', fr: "Si oui, l'ajouter au total", ar: 'إذا كان كذلك، أضفه إلى المجموع' } },
        ],
        correct_order: ['init', 'visit', 'decide', 'update'],
        success: {
          en: 'That is the pattern. Now write it in Python.',
          fr: 'Voilà le schéma. À vous de l’écrire en Python.',
          ar: 'هذا هو النمط. والآن اكتبه بلغة Python.',
        },
        hint: {
          en: 'The total has to exist before the loop can add anything to it.',
          fr: 'Le total doit exister avant que la boucle puisse y ajouter quelque chose.',
          ar: 'يجب أن يوجد المجموع قبل أن تضيف الحلقة إليه أي شيء.',
        },
      }),
      translations: [
        {
          language: 'en',
          content: 'Put the four steps of the pattern in the order a program would run them.',
          code_example: null,
        },
        {
          language: 'fr',
          content: "Remettez les quatre étapes du schéma dans l'ordre où un programme les exécuterait.",
          code_example: null,
        },
        {
          language: 'ar',
          content: 'رتّب خطوات النمط الأربع بالترتيب الذي ينفّذها به البرنامج.',
          code_example: null,
        },
      ],
    },
    {
      id: 904,
      block_type: 'exam_tip',
      order: 5,
      content: 'Everything indented under a for or if line belongs to it.',
      code_example: null,
      config: JSON.stringify({ kind: 'exam_tip' }),
      translations: [
        { language: 'en', content: 'Everything indented under a for or if line belongs to it.', code_example: null },
        { language: 'fr', content: 'Tout ce qui est indenté sous une ligne for ou if lui appartient.', code_example: null },
        { language: 'ar', content: 'كل ما يُزاح إلى الداخل تحت سطر for أو if ينتمي إليه.', code_example: null },
      ],
    },
  ],
  exercises: [
    {
      id: 918,
      exercise_type: 'code_writing',
      order: 1,
      xp_reward: 15,
      starter_code: 'total = 0\nfor i in range(1, 21):\n    if i % 2 == 0:\n        total += i\nprint("Sum of evens:", total)',
      translations: [
        {
          language: 'en',
          prompt: 'Find the sum of all even numbers from 1 to 20.',
          hint: 'Use % 2 == 0 to check if even, then add to total',
          explanation: null,
        },
      ],
      options: [],
    },
  ],
};

export function questSubmitResponse(overrides: Record<string, unknown> = {}) {
  return {
    is_correct: false,
    xp_earned: 0,
    feedback: 'Incorrect solution',
    output: '',
    error: 'Incorrect solution',
    is_completed: false,
    lesson_completed: false,
    ...overrides,
  };
}

/** A lesson shaped like the second reference Micro-Quest (lesson 12, "Scope
 * and Function Design"): the same hook -> reading -> blueprint -> exam_tip
 * skeleton, but with a match_pairs blueprint and a prediction exercise. Its
 * only job here is to prove the flow does not care which of either it gets. */
export const mockMatchPairsLesson = {
  id: 12,
  slug: 'scope-and-function-design',
  order: 3,
  difficulty: 'intermediate',
  estimated_minutes: 35,
  xp_reward: 50,
  is_project: false,
  translations: [
    { language: 'en', title: 'Scope and Function Design', story: 'Where variables live', objective: 'Local vs global', skills: 'Scope' },
    { language: 'fr', title: 'Portée et Conception de Fonctions', story: 'Où vivent les variables', objective: 'Locale vs globale', skills: 'Portée' },
    { language: 'ar', title: 'النطاق وتصميم الدوال', story: 'أين تعيش المتغيرات', objective: 'محلي مقابل عام', skills: 'النطاق' },
  ],
  blocks: [
    {
      id: 1200,
      block_type: 'hook',
      order: 0,
      content: 'A classmate adds a total inside a function and the rest of the program keeps reading the old value.',
      code_example: null,
      config: JSON.stringify({
        kind: 'hook',
        challenge: {
          en: 'When two variables share a name, how does Python decide which one a line is talking about?',
          fr: 'Quand deux variables portent le même nom, comment Python décide-t-il de laquelle une ligne parle ?',
          ar: 'حين يحمل متغيّران الاسم نفسه، كيف تقرّر Python أيّهما يقصده السطر؟',
        },
        learn: {
          en: 'You will learn where a name lives so you can predict which value a line will read.',
          fr: 'Vous allez apprendre où vit un nom pour prédire quelle valeur une ligne va lire.',
          ar: 'ستتعلّم أين يعيش الاسم لتتوقّع أي قيمة سيقرأها السطر.',
        },
      }),
      translations: [
        { language: 'en', content: 'A classmate adds a total inside a function and the rest of the program keeps reading the old value.', code_example: null },
        { language: 'fr', content: "Un camarade ajoute un total dans une fonction et le reste du programme lit l'ancienne valeur.", code_example: null },
        { language: 'ar', content: 'يضيف زميل متغيّر total داخل دالة فيظل باقي البرنامج يقرأ القيمة القديمة.', code_example: null },
      ],
    },
    {
      id: 1201,
      block_type: 'text',
      order: 1,
      content: 'Variables created inside a function are local. Variables outside are global.',
      code_example: null,
      config: null,
      translations: [
        { language: 'en', content: 'Variables created inside a function are local. Variables outside are global.', code_example: null },
      ],
    },
    {
      id: 1202,
      block_type: 'blueprint',
      order: 4,
      content: 'Connect each way of naming a value to where that value actually lives.',
      code_example: null,
      config: JSON.stringify({
        kind: 'match_pairs',
        pairs: [
          {
            id: 'local',
            left: { en: 'Local variable', fr: 'Variable locale', ar: 'متغيّر محلي' },
            right: {
              en: 'Exists only while its own function is running',
              fr: "N'existe que pendant l'exécution de sa propre fonction",
              ar: 'لا يوجد إلا أثناء تنفيذ الدالة التي يخصّها',
            },
          },
          {
            id: 'global',
            left: { en: 'Global variable', fr: 'Variable globale', ar: 'متغيّر عام' },
            right: {
              en: 'Created outside every function, and lasts for the whole run',
              fr: 'Créée en dehors de toute fonction, et dure pendant toute exécution',
              ar: 'يُنشَأ خارج كل الدوال ويبقى طوال التشغيل',
            },
          },
          {
            id: 'parameter',
            left: { en: 'Parameter', fr: 'Paramètre', ar: 'معامِل' },
            right: {
              en: 'A name that receives a value at the moment of the call',
              fr: "Un nom qui reçoit une valeur au moment de l'appel",
              ar: 'اسم يتلقّى قيمة في لحظة الاستدعاء',
            },
          },
          {
            id: 'return',
            left: { en: 'Return value', fr: 'Valeur de retour', ar: 'القيمة المُعادة' },
            right: {
              en: 'The result a function hands back to whoever called it',
              fr: "Le résultat qu'une fonction renvoie à celui qui l'a appelée",
              ar: 'النتيجة التي تعيدها الدالة إلى من استدعاها',
            },
          },
        ],
        success: {
          en: 'Assigning to a name inside a function creates a new local name.',
          fr: "Affecter un nom dans une fonction crée un nouveau nom local.",
          ar: 'الإسناد إلى اسم داخل الدالة يُنشئ اسمًا محليًا جديدًا.',
        },
        hint: {
          en: 'Ask where the name was created, not where it is being used.',
          fr: 'Demandez-vous où le nom a été créé, pas où il est utilisé.',
          ar: 'اسأل أين أُنشئ الاسم، لا أين يُستعمل.',
        },
      }),
      translations: [
        { language: 'en', content: 'Connect each way of naming a value to where that value actually lives.', code_example: null },
        { language: 'fr', content: "Reliez chaque façon de nommer une valeur à l'endroit où elle vit.", code_example: null },
        { language: 'ar', content: 'صِل كل طريقة لتسمية قيمة بالمكان الذي تعيش فيه.', code_example: null },
      ],
    },
    {
      id: 1203,
      block_type: 'exam_tip',
      order: 5,
      content: 'Reading a global inside a function works; assigning to it does not.',
      code_example: null,
      config: JSON.stringify({ kind: 'exam_tip' }),
      translations: [
        { language: 'en', content: 'Reading a global inside a function works; assigning to it does not.', code_example: null },
        { language: 'fr', content: "Lire une globale dans une fonction fonctionne ; lui affecter une valeur non.", code_example: null },
        { language: 'ar', content: 'قراءة متغيّر عام داخل دالة تعمل، أما الإسناد إليه فلا.', code_example: null },
      ],
    },
  ],
  exercises: [
    {
      id: 1222,
      exercise_type: 'prediction',
      order: 1,
      xp_reward: 10,
      starter_code: 'x = 10\n\ndef modify():\n    x = 20\n    print("Inside:", x)\n\nmodify()\nprint("Outside:", x)',
      translations: [
        {
          language: 'en',
          prompt: 'What will this print? The function creates its own local x.',
          hint: "Local x doesn't affect global x",
          explanation: null,
        },
        {
          language: 'fr',
          prompt: "Qu'affichera ceci ? La fonction crée sa propre variable locale x.",
          hint: "Le x local n'affecte pas le x global",
          explanation: null,
        },
        {
          language: 'ar',
          prompt: 'ماذا سيطبع هذا؟ الدالة تنشئ متغير x محلي خاص بها.',
          hint: 'المتغير x المحلي لا يؤثر على x العام',
          explanation: null,
        },
      ],
      options: [],
    },
  ],
};

/** The same lesson with a blueprint kind no build knows about. Used to prove a
 * lesson authored against a future version degrades instead of crashing. */
export const mockUnknownBlueprintLesson = {
  ...mockMatchPairsLesson,
  id: 99,
  blocks: mockMatchPairsLesson.blocks.map((block) =>
    block.block_type === 'blueprint'
      ? { ...block, config: JSON.stringify({ kind: 'draw_flowchart', nodes: [] }) }
      : block,
  ),
};

/** The same lesson whose blueprint config is not JSON at all. */
export const mockBrokenBlueprintLesson = {
  ...mockMatchPairsLesson,
  id: 98,
  blocks: mockMatchPairsLesson.blocks.map((block) =>
    block.block_type === 'blueprint' ? { ...block, config: '{not json' } : block,
  ),
};

/** A lesson shaped like the third reference Micro-Quest (lesson 38,
 * "Searching Algorithms"): the same hook -> reading -> blueprint -> exam_tip
 * skeleton, with a spot_the_bug blueprint and a debugging exercise. */
export const mockSpotTheBugLesson = {
  id: 38,
  slug: 'searching-algorithms',
  order: 3,
  difficulty: 'intermediate',
  estimated_minutes: 40,
  xp_reward: 60,
  is_project: false,
  translations: [
    { language: 'en', title: 'Searching Algorithms', story: 'Find items efficiently', objective: 'Binary search', skills: 'Search' },
    { language: 'fr', title: 'Algorithmes de Recherche', story: 'Trouvez efficacement', objective: 'Recherche binaire', skills: 'Recherche' },
    { language: 'ar', title: 'خوارزميات البحث', story: 'ابحث بكفاءة', objective: 'البحث الثنائي', skills: 'البحث' },
  ],
  blocks: [
    {
      id: 1300,
      block_type: 'hook',
      order: 0,
      content: 'A phone book with 2,000 names, sorted alphabetically.',
      code_example: null,
      config: JSON.stringify({
        kind: 'hook',
        challenge: {
          en: 'What exact rule decides which half to search next?',
          fr: 'Quelle règle décide de la moitié à explorer ensuite ?',
          ar: 'ما القاعدة التي تحدد أي نصف يُبحث فيه لاحقًا؟',
        },
        learn: {
          en: 'You will pin down the exact boundaries binary search depends on.',
          fr: 'Vous allez déterminer les limites dont dépend la recherche binaire.',
          ar: 'ستحدد الحدود التي يعتمد عليها البحث الثنائي.',
        },
      }),
      translations: [
        { language: 'en', content: 'A phone book with 2,000 names, sorted alphabetically.', code_example: null },
        { language: 'fr', content: 'Un annuaire de 2 000 noms, trié alphabétiquement.', code_example: null },
        { language: 'ar', content: 'دفتر هاتف يحتوي على 2000 اسم، مرتّب أبجديًا.', code_example: null },
      ],
    },
    {
      id: 1301,
      block_type: 'blueprint',
      order: 4,
      content: 'Read these claims about the binary search above. Exactly one of them is wrong.',
      code_example: null,
      config: JSON.stringify({
        kind: 'spot_the_bug',
        snippet: 'left, right = 0, len(arr) - 1\nwhile left <= right:\n    mid = (left + right) // 2',
        statements: [
          { id: 'sorted', text: { en: 'Binary search requires the array to already be sorted.', fr: 'La recherche binaire exige un tableau déjà trié.', ar: 'يتطلب البحث الثنائي أن تكون المصفوفة مرتّبة.' } },
          { id: 'halves', text: { en: 'Each comparison discards half of the remaining search space.', fr: 'Chaque comparaison élimine la moitié restante.', ar: 'كل مقارنة تستبعد نصف المساحة المتبقية.' } },
          { id: 'bound', text: { en: 'The initial right boundary should be len(arr), the length of the array.', fr: 'La limite droite initiale doit être len(arr).', ar: 'يجب أن يكون الحد الأيمن الابتدائي len(arr).' } },
          { id: 'logn', text: { en: 'Binary search runs in O(log n) time.', fr: 'La recherche binaire est en O(log n).', ar: 'يعمل البحث الثنائي بزمن O(log n).' } },
        ],
        buggy_id: 'bound',
        success: {
          en: 'Exactly — the initial right boundary must be len(arr) - 1.',
          fr: 'Exactement — la limite droite initiale doit être len(arr) - 1.',
          ar: 'بالضبط — يجب أن يكون الحد الأيمن الابتدائي len(arr) - 1.',
        },
        hint: {
          en: 'Which one describes an index one position past the last real element?',
          fr: "Laquelle décrit un index une position après le dernier élément ?",
          ar: 'أيّها يصف فهرسًا يقع بموضع واحد بعد آخر عنصر؟',
        },
      }),
      translations: [
        { language: 'en', content: 'Read these claims about the binary search above. Exactly one of them is wrong.', code_example: null },
        { language: 'fr', content: 'Lisez ces affirmations sur la recherche binaire. Une seule est fausse.', code_example: null },
        { language: 'ar', content: 'اقرأ هذه العبارات حول البحث الثنائي. واحدة منها فقط خاطئة.', code_example: null },
      ],
    },
    {
      id: 1302,
      block_type: 'exam_tip',
      order: 5,
      content: 'Integer floor division always rounds down.',
      code_example: null,
      config: JSON.stringify({ kind: 'exam_tip' }),
      translations: [
        { language: 'en', content: 'Integer floor division always rounds down.', code_example: null },
        { language: 'fr', content: 'La division entière arrondit toujours vers le bas.', code_example: null },
        { language: 'ar', content: 'القسمة الصحيحة تُقرّب دائمًا لأسفل.', code_example: null },
      ],
    },
  ],
  exercises: [
    {
      id: 1349,
      exercise_type: 'debugging',
      order: 1,
      xp_reward: 15,
      starter_code: 'def binary_search(arr, target):\n    left, right = 0, len(arr)\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid\n        else:\n            right = mid\n    return -1',
      translations: [
        {
          language: 'en',
          prompt: "Fix the binary search: right bound off by one, and left/right updates don't exclude mid.",
          hint: 'right should be len(arr)-1, left=mid+1, right=mid-1',
          explanation: null,
        },
      ],
      options: [],
    },
  ],
};

/** A lesson shaped like Phase 11's lesson 15 ("Tuples and Sets"): a
 * spot_the_bug blueprint ending in a fill_blank exercise — the first
 * Micro-Quest reference lesson to use that exercise type. */
export const mockFillBlankLesson = {
  id: 15,
  slug: 'tuples-and-sets',
  order: 2,
  difficulty: 'beginner',
  estimated_minutes: 35,
  xp_reward: 50,
  is_project: false,
  translations: [
    { language: 'en', title: 'Tuples and Sets', story: 'Immutable sequences and unique collections', objective: 'Use tuples and sets', skills: 'Tuples, sets' },
    { language: 'fr', title: 'Tuples et Ensembles', story: 'Séquences immuables', objective: 'Utiliser tuples et ensembles', skills: 'Tuples, ensembles' },
    { language: 'ar', title: 'التوابل والمجموعات', story: 'تسلسلات غير قابلة للتغيير', objective: 'استخدام التوابل والمجموعات', skills: 'التوابل، المجموعات' },
  ],
  blocks: [
    {
      id: 1400,
      block_type: 'hook',
      order: 0,
      content: 'A student stores exam dates as a tuple, and a friend’s fix crashes instantly.',
      code_example: null,
      config: JSON.stringify({
        kind: 'hook',
        challenge: { en: 'Why does one collection refuse to change, while another refuses duplicates?' },
        learn: { en: 'You will pin down what makes a tuple different from a set.' },
      }),
      translations: [
        { language: 'en', content: 'A student stores exam dates as a tuple, and a friend’s fix crashes instantly.', code_example: null },
        { language: 'fr', content: 'Un élève stocke des dates dans un tuple, et le correctif d’un ami plante.', code_example: null },
        { language: 'ar', content: 'يخزّن تلميذ تواريخ في صف، وإصلاح صديقه يتوقف فورًا.', code_example: null },
      ],
    },
    {
      id: 1401,
      block_type: 'blueprint',
      order: 4,
      content: 'Read these claims about tuples and sets. Exactly one of them is wrong.',
      code_example: null,
      config: JSON.stringify({
        kind: 'spot_the_bug',
        statements: [
          { id: 'immutable', text: { en: "A tuple's contents cannot be changed after it is created" } },
          { id: 'dedup', text: { en: 'A set automatically removes duplicate values' } },
          { id: 'mixed', text: { en: 'A tuple can hold values of different types' } },
          { id: 'editable', text: { en: 'A tuple can be modified in place, the same way a list can' } },
        ],
        buggy_id: 'editable',
        success: { en: 'Right — a tuple can never be modified in place.' },
        hint: { en: "Which one contradicts 'immutable'?" },
      }),
      translations: [
        { language: 'en', content: 'Read these claims about tuples and sets. Exactly one of them is wrong.', code_example: null },
        { language: 'fr', content: 'Lisez ces affirmations. Une seule est fausse.', code_example: null },
        { language: 'ar', content: 'اقرأ هذه العبارات. واحدة منها فقط خاطئة.', code_example: null },
      ],
    },
    {
      id: 1402,
      block_type: 'exam_tip',
      order: 5,
      content: 'A single-item tuple needs a trailing comma.',
      code_example: null,
      config: JSON.stringify({ kind: 'exam_tip' }),
      translations: [
        { language: 'en', content: 'A single-item tuple needs a trailing comma.', code_example: null },
        { language: 'fr', content: 'Un tuple à un élément a besoin d’une virgule finale.', code_example: null },
        { language: 'ar', content: 'يحتاج الصف بعنصر واحد فاصلة في النهاية.', code_example: null },
      ],
    },
  ],
  exercises: [
    {
      id: 1526,
      exercise_type: 'fill_blank',
      order: 1,
      xp_reward: 10,
      starter_code: '# Tuple - fixed data\npoint = (____, ____)\n\n# Set - unique values\ncolors = {____, "red", "green", "red"}',
      translations: [
        { language: 'en', prompt: 'Fill in the tuple coordinates (10, 20) and add "blue" to the set.', hint: 'Tuples use parentheses, sets use curly braces', explanation: null },
      ],
      options: [],
    },
  ],
};

/** A lesson shaped like Phase 11's lesson 32 ("Commits and History"): a
 * match_pairs blueprint ending in an ordering exercise — proving the
 * architecture over that exercise type too. */
export const mockOrderingLesson = {
  id: 32,
  slug: 'commits-and-history',
  order: 2,
  difficulty: 'beginner',
  estimated_minutes: 35,
  xp_reward: 50,
  is_project: false,
  translations: [
    { language: 'en', title: 'Commits and History', story: 'Navigate your project history', objective: 'View and compare commits', skills: 'git log, git diff' },
    { language: 'fr', title: 'Commits et Historique', story: 'Naviguez votre historique', objective: 'Voir les commits', skills: 'git log' },
    { language: 'ar', title: 'الـ Commits والتاريخ', story: 'تنقل في تاريخ مشروعك', objective: 'عرض التسجيلات', skills: 'git log' },
  ],
  blocks: [
    {
      id: 1500,
      block_type: 'hook',
      order: 0,
      content: 'A project has 200 commits, and something broke three weeks ago.',
      code_example: null,
      config: JSON.stringify({
        kind: 'hook',
        challenge: { en: 'How do you find out what changed and when, without guessing?' },
        learn: { en: 'You will connect Git history commands to what each shows you.' },
      }),
      translations: [
        { language: 'en', content: 'A project has 200 commits, and something broke three weeks ago.', code_example: null },
        { language: 'fr', content: 'Un projet a 200 commits, et quelque chose s’est cassé.', code_example: null },
        { language: 'ar', content: 'يحتوي مشروع على 200 تسجيلة، وتعطّل شيء ما.', code_example: null },
      ],
    },
    {
      id: 1501,
      block_type: 'blueprint',
      order: 4,
      content: 'Connect each Git command to what it actually shows you.',
      code_example: null,
      config: JSON.stringify({
        kind: 'match_pairs',
        pairs: [
          { id: 'log', left: { en: 'git log' }, right: { en: 'The full commit history' } },
          { id: 'diff', left: { en: 'git diff' }, right: { en: 'What has changed but is not committed' } },
          { id: 'show', left: { en: 'git show HEAD' }, right: { en: 'What the last commit changed' } },
          { id: 'head_parent', left: { en: 'HEAD~1' }, right: { en: 'The commit before the current one' } },
        ],
        success: { en: 'Exactly right.' },
        hint: { en: 'Which looks at uncommitted changes?' },
      }),
      translations: [
        { language: 'en', content: 'Connect each Git command to what it actually shows you.', code_example: null },
        { language: 'fr', content: 'Reliez chaque commande à ce qu’elle montre.', code_example: null },
        { language: 'ar', content: 'صِل كل أمر بما يعرضه.', code_example: null },
      ],
    },
    {
      id: 1502,
      block_type: 'exam_tip',
      order: 5,
      content: 'HEAD always means the current commit.',
      code_example: null,
      config: JSON.stringify({ kind: 'exam_tip' }),
      translations: [
        { language: 'en', content: 'HEAD always means the current commit.', code_example: null },
        { language: 'fr', content: 'HEAD signifie toujours le commit actuel.', code_example: null },
        { language: 'ar', content: 'يعني HEAD دائمًا التسجيلة الحالية.', code_example: null },
      ],
    },
  ],
  exercises: [
    {
      id: 1543,
      exercise_type: 'ordering',
      order: 1,
      xp_reward: 10,
      starter_code: null,
      translations: [
        { language: 'en', prompt: 'Order the commands to create a commit and view history.', hint: 'Init, add, commit, then log', explanation: null },
      ],
      options: [
        { id: 9001, order: 1, translations: [{ language: 'en', text: 'git init' }] },
        { id: 9002, order: 2, translations: [{ language: 'en', text: 'git add .' }] },
        { id: 9003, order: 3, translations: [{ language: 'en', text: 'git commit -m "Initial commit"' }] },
        { id: 9004, order: 4, translations: [{ language: 'en', text: 'git log --oneline' }] },
      ],
    },
  ],
};

/** A lesson progress row as the backend returns it. */
export function questProgress(overrides: Record<string, unknown> = {}) {
  return {
    id: 501,
    lesson_id: 9,
    status: 'in_progress',
    completed_at: null,
    xp_earned: 0,
    current_block: 0,
    ...overrides,
  };
}
