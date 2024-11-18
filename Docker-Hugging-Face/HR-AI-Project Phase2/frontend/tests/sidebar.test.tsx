import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import SideBar from '../src/components/SideBar';
import { describe, it, expect, vi, afterEach, beforeAll } from 'vitest';
import React from 'react';
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter';

// Test cases  
describe('SideBar Component', () => {
  const mockOnActivityClick = vi.fn();
  const mockOnClearChat = vi.fn();
  let mock;

  afterEach(() => {
    mock.reset()
  })

  beforeAll(() => {
    mock = new MockAdapter(axios)
  })


  it('renders the collapsed sidebar by default', () => {
    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={true} isAdmin={false} />);
    expect(screen.getByTitle('Expand Menu')).toBeInTheDocument();
  });

  it('expands and collapses the sidebar when menu button is clicked', async () => {
    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={true} />);
    const menuButton = screen.getByTitle('Expand Menu');
    fireEvent.click(menuButton);

    // Wait for the animation to complete and check if the sidebar is visible  
    await waitFor(() => expect(screen.queryByRole('button', { name: 'New Chat' })).toBeInTheDocument());

    // Click again to collapse  
    fireEvent.click(menuButton);
    await waitFor(() => expect(screen.queryByRole('button', { name: 'New Chat' })).not.toBeInTheDocument());
  });

  it('fetches sessions when the sidebar is expanded', async () => {
    const mockData = [{ SessionId: '1', Question: 'How do I test?' }]
    mock.onGet("/api/recent").reply(200, mockData);

    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={true} isAdmin={false} />);

    const menuButton = screen.getByTitle('Expand Menu');

    fireEvent.click(menuButton);

    // Check if the session is displayed  
    await waitFor(() => expect(screen.getByText('How do I test?')).toBeInTheDocument());
  });

  it('handles click on session item', async () => {

    mock.onGet("/api/recent").reply(200, [{ SessionId: '1', Question: 'Session 1' }]);

    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={true} isAdmin={false} />);
    const menuButton = screen.getByTitle('Expand Menu');
    fireEvent.click(menuButton);

    const request = mock.history.get.find(req => req.url === '/api/recent');

    expect(request).toBeDefined();

    await waitFor(()=>expect(screen.getByText('Session 1')).toBeInTheDocument())
    const sessionItem = screen.getByText('Session 1');
    fireEvent.click(sessionItem);

    expect(mockOnActivityClick).toHaveBeenCalledWith('1');
  });

  it('shows and hides more sessions when "Show More" is clicked', async () => {
    const sessions = new Array(10).fill(null).map((_, index) => ({ SessionId: `${index}`, Question: `Question ${index}` }));
    mock.onGet("/api/recent").reply(200, sessions);

    vi.spyOn(window, 'scrollTo').mockImplementationOnce((x, y) => { });

    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={true} isAdmin={false} />);
    const menuButton = screen.getByTitle('Expand Menu');
    fireEvent.click(menuButton);
    
    const request = mock.history.get.find(req => req.url === '/api/recent');

    expect(request).toBeDefined();

    await waitFor(()=>expect(screen.getByText('Show More')).toBeInTheDocument())
    const showMoreButton = screen.getByText('Show More');
    fireEvent.click(showMoreButton);

    expect(screen.getByText('Show Less')).toBeInTheDocument();
    expect(screen.getByText('Question 9')).toBeInTheDocument();
  });

  it('calls onClearChat when the new chat button is clicked', () => {
    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={true} isAdmin={false} />);
    const newChatButton = screen.getByTitle('New Chat');
    fireEvent.click(newChatButton);

    expect(mockOnClearChat).toHaveBeenCalled();
  });

  it('shows settings when enabled', async () => {
    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={true} isAdmin={false} />);
    const menuButton = screen.getByTitle('Expand Menu');
    fireEvent.click(menuButton);
    await waitFor(() => expect(screen.getByTitle('Adjustments')).toBeInTheDocument());
  });

  it('hides settings when disabled', () => {
    render(<SideBar onActivityClick={mockOnActivityClick} onClearChat={mockOnClearChat} enableSettings={false} isAdmin={false} />);
    const menuButton = screen.getByTitle('Expand Menu');
    fireEvent.click(menuButton);

    expect(screen.queryByText('Adjustments')).not.toBeInTheDocument();
  });
});  
