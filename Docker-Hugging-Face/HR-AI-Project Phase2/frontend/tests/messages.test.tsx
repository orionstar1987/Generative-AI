import { render, screen, fireEvent, waitFor } from '@testing-library/react';  
import userEvent from '@testing-library/user-event'; 
import { describe, it, expect, vi } from 'vitest'; 
import Messages from '../src/components/Messages';
import React from 'react';
  
const mockMessages = [  
  { messageId: '1', message: 'Message 1', role: 'user', isLiked: null, submittedFeedback: false },  
  { messageId: '1', message: 'Message 2', role: 'assistant', isLiked: null, submittedFeedback: false } , 
  { messageId: '2', message: 'Message 3', role: 'user', isLiked: null, submittedFeedback: false },  
  { messageId: '2', message: 'Message 4', role: 'assistant', isLiked: null, submittedFeedback: false }  
];  
  
const mockMessageFeedbackClick = vi.fn();  
const mockOnMessageRegenerateClick = vi.fn();  
const scrollIntoViewMock = vi.fn();
  
describe('Messages Component', () => {  
  
  window.HTMLElement.prototype.scrollIntoView = scrollIntoViewMock;

  it('should render all messages', () => {  
    
    render(<Messages  
      messages={mockMessages}  
      messageFeedbackClick={mockMessageFeedbackClick}  
      OnMessageRegenerateClick={mockOnMessageRegenerateClick}  
      isEnabled={true}  
      loginUserName={'testuser@example.com'}  
    />);  
  
    const messageElements = screen.getAllByText('Message 1');  
    expect(messageElements).toHaveLength(1);  
  });  
  
  it('should call messageFeedbackClick with correct parameters when like button is clicked', async () => {  
    const messages = [...mockMessages] 
    messages[1].isLiked = null
    messages[1].submittedFeedback = false
    render(<Messages  
      messages={messages}  
      messageFeedbackClick={mockMessageFeedbackClick}  
      OnMessageRegenerateClick={mockOnMessageRegenerateClick}  
      isEnabled={true}  
      loginUserName={'testuser@example.com'}  
    />);  
  
    const likeButton = screen.getAllByTitle('Like')[0];  
    fireEvent.click(likeButton);  
    expect(mockMessageFeedbackClick).toHaveBeenCalledWith('1', true, false);   
  });  
  
  it('should call messageFeedbackClick with correct parameters when liked button is clicked', async () => {  
    const messages = [...mockMessages] 
    messages[1].isLiked = true
    messages[1].submittedFeedback = true
    render(<Messages  
      messages={messages}  
      messageFeedbackClick={mockMessageFeedbackClick}  
      OnMessageRegenerateClick={mockOnMessageRegenerateClick}  
      isEnabled={true}  
      loginUserName={'testuser@example.com'}  
    />);  
  
    const likeButton = screen.getAllByTitle('Liked')[0];  
    fireEvent.click(likeButton);  
    expect(mockMessageFeedbackClick).toHaveBeenCalledWith('1', null, true);
  });  

  it('should call messageFeedbackClick with correct parameters when dislike button is clicked', () => { 
    const messages = [...mockMessages] 
    messages[1].isLiked = null
    messages[1].submittedFeedback = false

    render(<Messages  
      messages={messages}  
      messageFeedbackClick={mockMessageFeedbackClick}  
      OnMessageRegenerateClick={mockOnMessageRegenerateClick}  
      isEnabled={true}  
      loginUserName={'testuser@example.com'}  
    />);  
  
    const dislikeButton = screen.getAllByTitle('Dislike')[0];  
    fireEvent.click(dislikeButton);  
    expect(mockMessageFeedbackClick).toHaveBeenCalledWith('1', false, false);  
  });  
  
  it('should call messageFeedbackClick with correct parameters when disliked button is clicked', async () => { 
    const messages = [...mockMessages] 
    messages[1].isLiked = false
    messages[1].submittedFeedback = true
    render(<Messages  
      messages={messages}  
      messageFeedbackClick={mockMessageFeedbackClick}  
      OnMessageRegenerateClick={mockOnMessageRegenerateClick}  
      isEnabled={true}  
      loginUserName={'testuser@example.com'}  
    />);  
  
    const likeButton = screen.getAllByTitle('Disliked')[0];  
    fireEvent.click(likeButton);  
    expect(mockMessageFeedbackClick).toHaveBeenCalledWith('1', null, true);
  }); 

  it('should open the modal for regenerate answer when latest message dislike button is clicked', async () => { 
    const messages = [...mockMessages] 
    messages[1].isLiked = null
    messages[1].submittedFeedback = false 
    messages[3].isLiked = null
    messages[3].submittedFeedback = false 
    render(<Messages  
      messages={messages}  
      messageFeedbackClick={mockMessageFeedbackClick}  
      OnMessageRegenerateClick={mockOnMessageRegenerateClick}  
      isEnabled={true}  
      loginUserName={'testuser@example.com'}  
    />);  
  
    const dislikeButton = screen.getAllByTitle('Dislike')[1];  
    fireEvent.click(dislikeButton);  
    
    await waitFor(()=>expect(screen.getAllByText('I apologize, my previous answer may not have been accurate. Can I try answering your question again?')).toHaveLength(1))
  });  
  

  it('should copy message to clipboard and show copied icon', async () => {  
    window.prompt  = vi.fn()
    render(<Messages  
      messages={mockMessages}  
      messageFeedbackClick={mockMessageFeedbackClick}  
      OnMessageRegenerateClick={mockOnMessageRegenerateClick}  
      isEnabled={true}  
      loginUserName={'testuser@example.com'}  
    />);  
  
    const copyButtons = screen.getAllByTitle('Copy message');  
    userEvent.click(copyButtons[0]);  
    
    await waitFor(()=>expect(screen.getAllByTitle('Copied')).toHaveLength(1));  
  });  
  
});  
