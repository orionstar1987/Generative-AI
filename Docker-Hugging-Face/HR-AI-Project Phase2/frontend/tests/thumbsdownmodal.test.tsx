import { render, fireEvent, screen } from '@testing-library/react';  
import ThumbsDown from '../src/components/thumbsdownmodal';  
import { describe, it, expect, vi, beforeEach  } from 'vitest';
import React from 'react';
  
describe('ThumbsDown Component', () => {  
    const mockOnYesClick = vi.fn();  
    const mockOnNoClick = vi.fn();  
  
    beforeEach(() => {  
        render(<ThumbsDown OnYesClick={mockOnYesClick} OnNoClick={mockOnNoClick} />);  
    });  
  
   it('renders thumbs down icon', () => {  
        const thumbsDownIcon = screen.getByTitle('Dislike');  
        expect(thumbsDownIcon).toBeInTheDocument();  
    });  
  
   it('opens modal on thumbs down icon click', () => {  
        const thumbsDownIcon = screen.getByTitle('Dislike');  
        fireEvent.click(thumbsDownIcon);  
        const modal = screen.getByRole('dialog');  
        expect(modal).toBeInTheDocument();  
    });  
});  
  
