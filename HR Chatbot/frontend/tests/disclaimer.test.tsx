import { render, screen, fireEvent } from '@testing-library/react';  
import Disclaimer from '../src/components/Disclaimer'; 
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
 

describe('Disclaimer Component', () => {  
  it('should open the modal when the component is mounted', () => {  
    const agreedMock = vi.fn();  
    render(<Disclaimer agreed={agreedMock} />);  
    expect(screen.getByText(/DISCLAIMER:/i)).toBeInTheDocument();  
  });  
  
  it('should call the agreed function with false when Cancel is clicked', () => {  
    const agreedMock = vi.fn();  
    render(<Disclaimer agreed={agreedMock} />);  
    fireEvent.click(screen.getByText('Cancel'));  
    expect(agreedMock).toHaveBeenCalledWith(false);  
  });  
  
  it('should call the agreed function with true when Agree is clicked', () => {  
    const agreedMock = vi.fn();  
    render(<Disclaimer agreed={agreedMock} />);  
    fireEvent.click(screen.getByText('I Agree'));  
    expect(agreedMock).toHaveBeenCalledWith(true);  
  });  
});  
