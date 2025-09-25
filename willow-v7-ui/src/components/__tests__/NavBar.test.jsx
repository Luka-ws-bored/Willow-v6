import { render, screen, fireEvent } from '@testing-library/react';
import NavBar from '../organisms/NavBar';

describe('NavBar', () => {
  const mockOnTabClick = jest.fn();
  const mockOnSearch = jest.fn();

  beforeEach(() => {
    mockOnTabClick.mockClear();
    mockOnSearch.mockClear();
  });

  it('renders all tabs', () => {
    render(
      <NavBar 
        activeTab="Chat" 
        onTabClick={mockOnTabClick} 
        onSearch={mockOnSearch} 
      />
    );

    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Playground')).toBeInTheDocument();
    expect(screen.getByText('Prompt Vault')).toBeInTheDocument();
    expect(screen.getByText('RAG')).toBeInTheDocument();
    expect(screen.getByText('Agents')).toBeInTheDocument();
    expect(screen.getByText('Docs')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('calls onTabClick when a tab is clicked', () => {
    render(
      <NavBar 
        activeTab="Chat" 
        onTabClick={mockOnTabClick} 
        onSearch={mockOnSearch} 
      />
    );

    fireEvent.click(screen.getByText('RAG'));
    expect(mockOnTabClick).toHaveBeenCalledWith('RAG');
  });

  it('calls onSearch when search form is submitted', () => {
    render(
      <NavBar 
        activeTab="Chat" 
        onTabClick={mockOnTabClick} 
        onSearch={mockOnSearch} 
      />
    );

    const searchInput = screen.getByPlaceholderText('Search...');
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    
    const form = screen.getByRole('form');
    fireEvent.submit(form);
    
    expect(mockOnSearch).toHaveBeenCalledWith('test query');
  });
});