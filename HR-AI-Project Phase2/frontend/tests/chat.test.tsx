import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { expect, describe, it, beforeEach, beforeAll, afterEach } from 'vitest';
import Chat from '../src/pages/Chat';
import React from 'react';
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter';

describe('App Component', () => {
  let mock;
  const renderComponent = () => {
    return render(
      <Chat />)
  }

  afterEach(() => {
    mock.reset()
  })

  beforeEach(() => {
    mock.onPost('/api/session').reply(200, { sessionId: '1', user: 'localhost user', isAdmin: false });
  })

  beforeAll(() => {
    mock = new MockAdapter(axios)
  })


  it('renders the App component with initial elements', () => {
    renderComponent();
    expect(screen.getByAltText(/Wind Creek Hospitality/)).toBeInTheDocument();
    expect(screen.getByText(/AskHR/)).toBeInTheDocument();
    expect(screen.getByText(/Hello! I'm the Wind Creek HR Assistant/)).toBeInTheDocument();
  });

  it('handles message input correctly', async () => {
    renderComponent()
    const textarea = screen.getByPlaceholderText('Ask your question...')
    fireEvent.change(textarea, { target: { value: 'hello' } });
    expect(textarea).toHaveValue('hello');
  });


  it('calls handleSendMessage when send button is clicked', async () => {

    mock.onPost('/api/chat').reply(200, { sessionId: '1', messageId: '1', message: 'Hi, How can I help you?' })

    renderComponent();
    const textarea = screen.getByPlaceholderText('Ask your question...')
    fireEvent.change(textarea, { target: { value: 'Hello' } });

    const sendButton = screen.getByTestId('btn-send');

    fireEvent.click(sendButton);

    const sessionRequest = mock.history.post.find(req => req.url === '/api/session');

    await waitFor(() => expect(sessionRequest).toBeDefined());

    const chatRequest = mock.history.post.find(req => req.url === '/api/chat');

    await waitFor(() => expect(chatRequest).toBeDefined());

    await waitFor(() => expect(screen.getByText('Hi, How can I help you?')).toBeInTheDocument());
  });

  it('handles message regeneration', async () => {
    mock.onPost('/api/chat').reply(200, { sessionId: '1', messageId: '1', message: 'Hi, How can I help you?' })

    renderComponent();
    const textarea = screen.getByPlaceholderText('Ask your question...')
    fireEvent.change(textarea, { target: { value: 'Hello' } });

    const sendButton = screen.getByTestId('btn-send');

    fireEvent.click(sendButton);

    const sessionRequest = mock.history.post.find(req => req.url === '/api/session');

    await waitFor(() => expect(sessionRequest).toBeDefined());

    const chatRequest = mock.history.post.find(req => req.url === '/api/chat');

    await waitFor(() => expect(chatRequest).toBeDefined());

    await waitFor(() => expect(screen.getByText('Hi, How can I help you?')).toBeInTheDocument());

    const dislikeButton = screen.getAllByTitle('Dislike')[0];
    fireEvent.click(dislikeButton);

    await waitFor(() => expect(screen.getAllByText('I apologize, my previous answer may not have been accurate. Can I try answering your question again?')).toHaveLength(1))

    const regenerateButton = screen.getByText('Yes');

    fireEvent.click(regenerateButton);

    expect(mock.history.post.length).toBe(4);

  });
});
