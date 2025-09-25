import { render, screen, fireEvent } from '@testing-library/react';
import ChatMessage from '../molecules/ChatMessage';

describe('ChatMessage', () => {
  const mockMessage = {
    id: '1',
    author: 'ai',
    content: 'Hello, how can I help you today?',
    timeISO: '2023-05-20T10:00:00Z',
    metadata: { model: 'GPT-4' }
  };

  it('renders message content', () => {
    render(<ChatMessage {...mockMessage} />);

    expect(screen.getByText('Hello, how can I help you today?')).toBeInTheDocument();
    expect(screen.getByText('Willow AI')).toBeInTheDocument();
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  it('shows copy button', () => {
    render(<ChatMessage {...mockMessage} />);

    expect(screen.getByLabelText('Copy message')).toBeInTheDocument();
  });

  it('shows collapse button', () => {
    render(<ChatMessage {...mockMessage} />);

    expect(screen.getByLabelText('Collapse message')).toBeInTheDocument();
  });

  it('collapses content when collapse button is clicked', () => {
    render(<ChatMessage {...mockMessage} />);

    const collapseButton = screen.getByLabelText('Collapse message');
    fireEvent.click(collapseButton);
    
    expect(screen.queryByText('Hello, how can I help you today?')).not.toBeInTheDocument();
  });
});