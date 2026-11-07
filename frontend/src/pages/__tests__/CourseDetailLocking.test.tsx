import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../test/setup.tsx';
import { coursesApi } from '../../api/services';

const mockedCourses = vi.mocked(coursesApi);

/**
 * CourseDetail now renders the real per-lesson status from GET /courses/{id}
 * instead of defaulting every lesson to "available". A locked lesson must not
 * be a link: offering one promises a destination the API answers with 403.
 */
function lesson(id: number, title: string, status?: string) {
  return {
    id,
    slug: `l-${id}`,
    order: id,
    difficulty: 'beginner',
    estimated_minutes: 30,
    xp_reward: 50,
    is_project: false,
    translations: [{ language: 'en', title }],
    blocks: [],
    exercises: [],
    ...(status ? { status } : {}),
  };
}

function course(lessons: ReturnType<typeof lesson>[]) {
  return {
    id: 1,
    slug: 'python-basics',
    order: 1,
    difficulty: 'beginner',
    translations: [{ language: 'en', title: 'Python Foundations', description: 'd', skills: 'Variables' }],
    modules: [
      {
        id: 1,
        slug: 'getting-started',
        order: 1,
        translations: [{ language: 'en', title: 'Getting Started', description: 'Start here' }],
        lessons,
      },
    ],
  };
}

async function openTheModule() {
  const moduleButton = await screen.findByText('Getting Started');
  await userEvent.click(moduleButton);
}

describe('CourseDetail lesson locking', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders an unlocked lesson as a link to it', async () => {
    mockedCourses.getById.mockResolvedValue(
      course([lesson(1, 'What Is Programming?', 'current')]) as any,
    );

    renderWithProviders(null as any, { initialLanguage: 'en', courseId: '1' });
    await openTheModule();

    const row = await screen.findByTestId('lesson-row-1');
    expect(row.tagName).toBe('A');
    expect(row).toHaveAttribute('href', '/app/lessons/1');
    expect(row).not.toHaveAttribute('aria-disabled');
  });

  it('renders a locked lesson as a non-interactive row, not a link', async () => {
    mockedCourses.getById.mockResolvedValue(
      course([
        lesson(1, 'What Is Programming?', 'completed'),
        lesson(2, 'Variables and Values', 'locked'),
      ]) as any,
    );

    renderWithProviders(null as any, { initialLanguage: 'en', courseId: '1' });
    await openTheModule();

    const locked = await screen.findByTestId('lesson-row-2');
    expect(locked.tagName).not.toBe('A');
    expect(locked).not.toHaveAttribute('href');
    expect(locked).toHaveAttribute('aria-disabled', 'true');
    // Not tab-focusable: a plain div with no tabindex is skipped by the
    // keyboard, which is the point -- a focus stop that does nothing is worse
    // than no focus stop.
    expect(locked).not.toHaveAttribute('tabindex');
    expect(locked.querySelector('a')).toBeNull();
  });

  it('explains when a locked lesson opens', async () => {
    mockedCourses.getById.mockResolvedValue(
      course([lesson(1, 'One', 'completed'), lesson(2, 'Two', 'locked')]) as any,
    );

    renderWithProviders(null as any, { initialLanguage: 'en', courseId: '1' });
    await openTheModule();

    const locked = await screen.findByTestId('lesson-row-2');
    expect(locked).toHaveTextContent(/Opens after you complete the previous lesson/i);
    expect(locked).toHaveTextContent(/Locked/i);
  });

  it('shows no invented "Available" badge when the API sends no status', async () => {
    // The removed `lesson.status || 'available'` fallback is what used to make
    // every unknown-state lesson claim to be available.
    mockedCourses.getById.mockResolvedValue(
      course([lesson(1, 'No Status Lesson')]) as any,
    );

    renderWithProviders(null as any, { initialLanguage: 'en', courseId: '1' });
    await openTheModule();

    const row = await screen.findByTestId('lesson-row-1');
    expect(row).not.toHaveTextContent(/Available/i);
    // Still reachable: an absent status is not a lock.
    expect(row.tagName).toBe('A');
  });

  it('keeps the locked row out of the link set entirely', async () => {
    mockedCourses.getById.mockResolvedValue(
      course([
        lesson(1, 'One', 'completed'),
        lesson(2, 'Two', 'current'),
        lesson(3, 'Three', 'locked'),
      ]) as any,
    );

    renderWithProviders(null as any, { initialLanguage: 'en', courseId: '1' });
    await openTheModule();

    await waitFor(() => expect(screen.getByTestId('lesson-row-3')).toBeInTheDocument());
    const hrefs = Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href'));
    expect(hrefs).toContain('/app/lessons/1');
    expect(hrefs).toContain('/app/lessons/2');
    expect(hrefs).not.toContain('/app/lessons/3');
  });
});
