/**
 * Height for a lesson-style "app shell" page (fixed header, internally
 * scrolling body, fixed footer nav) that lives inside the global `Layout`.
 *
 * `Layout`'s `<main>` reserves `pt-20 pb-8` (5rem + 2rem = 7rem) around the
 * routed page for the fixed header and breathing room — see
 * `src/components/Layout.tsx`. A child that also claims a full `100vh`
 * ignores that reservation and ends up 7rem taller than the space it was
 * actually given, pushing its own bottom controls off-screen on any
 * viewport short enough that the overflow isn't obviously scrollable.
 *
 * `100dvh` (rather than `100vh`) additionally accounts for a mobile
 * browser's collapsing address bar, so the same calculation holds on phones.
 *
 * Any lesson-shaped page (classic `LessonDetail`, `MicroQuestLesson`, and
 * future ones) should size its root to this instead of `h-screen`.
 */
export const LESSON_SHELL_HEIGHT_CLASS = 'h-[calc(100dvh-7rem)]';
