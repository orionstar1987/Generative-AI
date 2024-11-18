import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import '@testing-library/jest-dom'
import createFetchMock from 'vitest-fetch-mock';

const fetcher = createFetchMock(vi);
fetcher.enableMocks();

Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
  value: vi.fn(),
  writable: true,
});

// runs a clean after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
})

