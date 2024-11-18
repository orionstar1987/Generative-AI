import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi } from 'vitest';
import ChatFooter from '../src/components/ChatFooter';

describe('ChatFooter Component', () => {
  const defaultProps = {
    inputMessage: '',
    setInputMessage: vi.fn(),
    handleSendMessage: vi.fn(),
    aiResponseInprogress: false,
    isEnabled: true,
    inputRef: React.createRef<HTMLTextAreaElement>(),
  };

  const renderComponent = (props = {}) => {
    const mergedProps = { ...defaultProps, ...props };
    return render(<ChatFooter {...mergedProps} />);
  };

  it('renders without crashing', () => {
    renderComponent();
  });

  it('displays the input message', () => {
    const inputMessage = 'Hello, world!';
    renderComponent({ inputMessage });
    const textarea = screen.getByPlaceholderText('Ask your question...');
    expect(textarea).toHaveValue(inputMessage);
  });

  it('calls setInputMessage on textarea change', () => {
    renderComponent();
    const textarea = screen.getByPlaceholderText('Ask your question...');
    fireEvent.change(textarea, { target: { value: 'New message' } });
    expect(defaultProps.setInputMessage).toHaveBeenCalledWith('New message');
  });

  it('calls handleSendMessage on Enter key press', async () => {
    renderComponent();
    const textarea = screen.getByPlaceholderText('Ask your question...');
    fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
    expect(defaultProps.handleSendMessage).toHaveBeenCalled();
  });

  it('displays Spinner when aiResponseInprogress is true', () => {
    renderComponent({ aiResponseInprogress: true });
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays send icon when aiResponseInprogress is false', () => {
    renderComponent({ aiResponseInprogress: false });
    expect(screen.getByTestId('btn-send')).toBeInTheDocument();
  });

  it('calls handleSendMessage on send icon click', () => {
    renderComponent({ aiResponseInprogress: false, inputMessage: 'test' });
    const sendIcon = screen.getByTestId('btn-send');
    fireEvent.click(sendIcon);
    expect(defaultProps.handleSendMessage).toHaveBeenCalled();
  });

  it('textarea is read-only when aiResponseInprogress is true', () => {
    renderComponent({ aiResponseInprogress: true });
    const textarea = screen.getByPlaceholderText('Ask your question...');
    expect(textarea).toHaveAttribute('readonly');
  });

  it('textarea is disabled when isEnabled is false', () => {
    renderComponent({ isEnabled: false });
    const textarea = screen.getByPlaceholderText('Ask your question...');
    expect(textarea).toBeDisabled();
  });
});