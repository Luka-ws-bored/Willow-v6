import { render, screen, fireEvent } from '@testing-library/react';
import ModelSwitcher from '../organisms/ModelSwitcher';

describe('ModelSwitcher', () => {
  const mockModels = [
    { id: 'gpt-4', name: 'GPT-4', tps: 80, context: 8192, status: 'remote' },
    { id: 'llama-2', name: 'Llama 2 7B', tps: 120, context: 4096, status: 'local' }
  ];
  
  const mockOnSelect = jest.fn();
  const mockOnToggleChained = jest.fn();

  beforeEach(() => {
    mockOnSelect.mockClear();
    mockOnToggleChained.mockClear();
  });

  it('renders the active model name', () => {
    render(
      <ModelSwitcher 
        models={mockModels}
        activeModelId="gpt-4"
        chainedMode={false}
        onSelect={mockOnSelect}
        onToggleChained={mockOnToggleChained}
      />
    );

    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  it('opens dropdown when clicked', () => {
    render(
      <ModelSwitcher 
        models={mockModels}
        activeModelId="gpt-4"
        chainedMode={false}
        onSelect={mockOnSelect}
        onToggleChained={mockOnToggleChained}
      />
    );

    const dropdownButton = screen.getByText('GPT-4');
    fireEvent.click(dropdownButton);
    
    expect(screen.getByText('Llama 2 7B')).toBeInTheDocument();
  });

  it('calls onSelect when a model is selected', () => {
    render(
      <ModelSwitcher 
        models={mockModels}
        activeModelId="gpt-4"
        chainedMode={false}
        onSelect={mockOnSelect}
        onToggleChained={mockOnToggleChained}
      />
    );

    const dropdownButton = screen.getByText('GPT-4');
    fireEvent.click(dropdownButton);
    
    const modelOption = screen.getByText('Llama 2 7B');
    fireEvent.click(modelOption);
    
    expect(mockOnSelect).toHaveBeenCalledWith('llama-2');
  });

  it('calls onToggleChained when chained button is clicked', () => {
    render(
      <ModelSwitcher 
        models={mockModels}
        activeModelId="gpt-4"
        chainedMode={false}
        onSelect={mockOnSelect}
        onToggleChained={mockOnToggleChained}
      />
    );

    const chainedButton = screen.getByText('Chained');
    fireEvent.click(chainedButton);
    
    expect(mockOnToggleChained).toHaveBeenCalledWith(true);
  });
});