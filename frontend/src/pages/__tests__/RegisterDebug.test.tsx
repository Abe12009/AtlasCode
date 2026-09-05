import React from 'react';
import { render, screen } from '@testing-library/react';
import { Register } from '../Register';
import { renderWithProviders } from '../../test/setup.tsx';

describe('Register Page Debug', () => {
  it('renders something', async () => {
    const { container } = await renderWithProviders(<Register />);
    console.log('Container HTML:', container.innerHTML);
    expect(container.innerHTML).toContain('AtlasCode');
  });
});