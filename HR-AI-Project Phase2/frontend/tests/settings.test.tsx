import { render, screen, waitFor } from '@testing-library/react';  
import userEvent from '@testing-library/user-event'; 
import Settings from '../src/components/Settings';
import { describe, it, expect, vi } from 'vitest'; 
import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';
 
const waitForTime = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

describe('Settings Component Tests', () => {  
  const renderComponent = () => render(  
    <ChakraProvider>
      <Settings />  
      </ChakraProvider> 
  );  
  
  it('should render the settings icon', () => {  
    renderComponent();  
    expect(screen.getByTitle('Adjustments')).toBeInTheDocument();  
  });  
  
  it('should open the drawer when settings icon is clicked', async () => {  
    renderComponent();  
    const settingsIcon = screen.getByTitle('Adjustments');  
    userEvent.click(settingsIcon);  
    await waitFor(()=>expect(screen.getByText('Settings')).toBeVisible());  
  });  
  
  it('should toggle the customize system message switch', async () => {  
    renderComponent();  
    const settingsIcon = screen.getByTitle('Adjustments');  
    userEvent.click(settingsIcon);  
  
    await waitFor(()=>expect(screen.getByLabelText('Customize System Message?')).toBeInTheDocument())

    const switchElement = screen.getByLabelText('Customize System Message?');  
    expect(switchElement).not.toBeChecked();  
    userEvent.click(switchElement);  
  
    expect(switchElement).to.have.property('checked', false); 
  });  
  
  it('should save to localStorage when customize system message is toggled', async () => {  
    const localStorageMock = {  
      getItem: vi.fn(),  
      setItem: vi.fn(),  
      removeItem: vi.fn(),  
      clear: vi.fn(),  
    };  
    global.localStorage = localStorageMock;  
  
    renderComponent();  
    const settingsIcon = screen.getByTitle('Adjustments');  
    userEvent.click(settingsIcon);  
  
    await waitFor(()=>expect(screen.getByLabelText('Customize System Message?')).toBeInTheDocument())
    const switchElement = screen.getByLabelText('Customize System Message?');  
    userEvent.click(switchElement);  
  
    expect(localStorage.setItem).toHaveBeenCalled();  
  });  
  
  it('should show textarea when customize system message is enabled', async () => {  
    renderComponent();  
    const settingsIcon = screen.getByTitle('Adjustments');  
    userEvent.click(settingsIcon);  
  
    await waitFor(()=>expect(screen.getByLabelText('Customize System Message?')).toBeInTheDocument())
    const switchElement = screen.getByLabelText('Customize System Message?');  
    userEvent.click(switchElement);  
    await waitFor(()=>expect(screen.getByTestId('system-prompt')).toBeInTheDocument()) 
  });  
  
  it('should close drawer when close button is clicked', async() => {  
    renderComponent();  
    const settingsIcon = screen.getByTitle('Adjustments');  
    userEvent.click(settingsIcon);  

    await waitFor(()=>expect(screen.getByRole('button', { name: 'Close' })).toBeInTheDocument())
  
    const closeButton = screen.getByRole('button', { name: 'Close' });  
    userEvent.click(closeButton);  
  
    await waitFor(()=>expect(screen.queryByText('Settings')).not.toBeInTheDocument());  
  });  
});  
  
