import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchBar } from '../../../components/library/SearchBar';
import { describe, it, expect, vi } from 'vitest';

describe('SearchBar', () => {
  it('renders with placeholder text', () => {
    render(<SearchBar onSearch={vi.fn()} />);

    expect(screen.getByPlaceholderText('Search stories...')).toBeInTheDocument();
  });

  it('debounces search input', async () => {
    const handleSearch = vi.fn();
    render(<SearchBar onSearch={handleSearch} debounceMs={100} />);

    const input = screen.getByRole('textbox');

    fireEvent.change(input, { target: { value: 'test' } });

    // Should not call immediately
    expect(handleSearch).not.toHaveBeenCalled();

    // Should call after debounce delay
    await waitFor(() => {
      expect(handleSearch).toHaveBeenCalledWith('test');
    }, { timeout: 200 });
  });

  it('shows clear button when text is entered', () => {
    render(<SearchBar onSearch={vi.fn()} />);

    const input = screen.getByRole('textbox');

    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();

    fireEvent.change(input, { target: { value: 'test' } });

    expect(screen.getByLabelText('Clear search')).toBeInTheDocument();
  });

  it('clears search when clear button is clicked', () => {
    const handleSearch = vi.fn();
    render(<SearchBar onSearch={handleSearch} />);

    const input = screen.getByRole('textbox') as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'test' } });

    const clearButton = screen.getByLabelText('Clear search');
    fireEvent.click(clearButton);

    expect(input.value).toBe('');
    expect(handleSearch).toHaveBeenCalledWith('');
  });
});
