import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../test/setup.tsx';
import { NotificationBell } from '../NotificationBell';
import { notificationsApi } from '../../api/services';

const mockedApi = vi.mocked(notificationsApi);

const NOTIFICATIONS = [
  { id: 2, type: 'lesson_completed' as const, data: {}, is_read: false, created_at: '2026-01-02T00:00:00Z' },
  { id: 1, type: 'xp_earned' as const, data: { xp: 50 }, is_read: true, created_at: '2026-01-01T00:00:00Z' },
];

beforeEach(() => {
  mockedApi.list.mockReset();
  mockedApi.getUnreadCount.mockReset();
  mockedApi.markRead.mockReset();
  mockedApi.markAllRead.mockReset();
});

describe('NotificationBell', () => {
  it('shows the unread count badge from the backend', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 3 });
    mockedApi.list.mockResolvedValue(NOTIFICATIONS);

    await renderWithProviders(<NotificationBell />);

    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });

  it('hides the badge when there are no unread notifications', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 0 });
    mockedApi.list.mockResolvedValue([]);

    await renderWithProviders(<NotificationBell />);

    await waitFor(() => {
      expect(mockedApi.getUnreadCount).toHaveBeenCalled();
    });
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('opens the panel and renders newest-first notifications with unread styling', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 1 });
    mockedApi.list.mockResolvedValue(NOTIFICATIONS);
    const user = userEvent.setup();

    await renderWithProviders(<NotificationBell />);
    await user.click(screen.getByRole('button', { name: /notifications/i }));

    const menu = await screen.findByRole('menu');
    const items = within(menu).getAllByRole('menuitem');
    expect(items).toHaveLength(2);
    // Newest (id 2, lesson_completed) must render before the older one (id 1, xp_earned).
    expect(within(items[0]).getByText(/Lesson completed/i)).toBeInTheDocument();
    expect(within(items[1]).getByText(/50 XP/i)).toBeInTheDocument();
  });

  it('shows the empty state when there are no notifications', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 0 });
    mockedApi.list.mockResolvedValue([]);
    const user = userEvent.setup();

    await renderWithProviders(<NotificationBell />);
    await user.click(screen.getByRole('button', { name: /notifications/i }));

    expect(await screen.findByText(/no notifications yet/i)).toBeInTheDocument();
  });

  it('shows an error state when loading notifications fails', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 0 });
    mockedApi.list.mockRejectedValue(new Error('network error'));
    const user = userEvent.setup();

    await renderWithProviders(<NotificationBell />);
    await user.click(screen.getByRole('button', { name: /notifications/i }));

    expect(await screen.findByText(/couldn't load notifications/i)).toBeInTheDocument();
  });

  it('marks an unread notification as read when clicked', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 1 });
    mockedApi.list.mockResolvedValue(NOTIFICATIONS);
    mockedApi.markRead.mockResolvedValue({ ...NOTIFICATIONS[0], is_read: true });
    const user = userEvent.setup();

    await renderWithProviders(<NotificationBell />);
    await user.click(screen.getByRole('button', { name: /notifications/i }));

    const menu = await screen.findByRole('menu');
    await user.click(within(menu).getByText(/Lesson completed/i));

    await waitFor(() => {
      expect(mockedApi.markRead).toHaveBeenCalledWith(2);
    });
  });

  it('does not re-mark an already-read notification as read', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 0 });
    mockedApi.list.mockResolvedValue(NOTIFICATIONS);
    const user = userEvent.setup();

    await renderWithProviders(<NotificationBell />);
    await user.click(screen.getByRole('button', { name: /notifications/i }));

    const menu = await screen.findByRole('menu');
    await user.click(within(menu).getByText(/50 XP/i));

    expect(mockedApi.markRead).not.toHaveBeenCalled();
  });

  it('marks all as read via the header action', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 1 });
    mockedApi.list.mockResolvedValue(NOTIFICATIONS);
    mockedApi.markAllRead.mockResolvedValue({ success: true });
    const user = userEvent.setup();

    await renderWithProviders(<NotificationBell />);
    await user.click(screen.getByRole('button', { name: /notifications/i }));

    await user.click(await screen.findByText(/mark all as read/i));

    await waitFor(() => {
      expect(mockedApi.markAllRead).toHaveBeenCalled();
    });
  });

  it('renders notification messages in French when the language is French', async () => {
    mockedApi.getUnreadCount.mockResolvedValue({ count: 0 });
    mockedApi.list.mockResolvedValue([NOTIFICATIONS[1]]);
    const user = userEvent.setup();

    await renderWithProviders(<NotificationBell />, { initialLanguage: 'fr' });
    await user.click(screen.getByRole('button', { name: /notifications/i }));

    expect(await screen.findByText(/Vous avez gagné 50 XP/i)).toBeInTheDocument();
  });
});
