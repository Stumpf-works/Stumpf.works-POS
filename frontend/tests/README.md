# Frontend Tests

Comprehensive test suite for the Stumpf.works POS frontend.

## Test Structure

```
src/
├── test/
│   ├── setup.ts              # Test setup and configuration
│   └── utils.tsx             # Test utilities and helpers
├── stores/
│   └── __tests__/            # Store tests
│       ├── authStore.test.ts
│       └── cartStore.test.ts
└── pages/
    └── __tests__/            # Component tests
        ├── LoginPage.test.tsx
        └── POSPage.test.tsx
```

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in watch mode
```bash
npm run test:watch
```

### Run tests with coverage
```bash
npm run test:coverage
```

### Run tests in UI mode
```bash
npm run test:ui
```

### Run specific test file
```bash
npm test -- LoginPage
```

### Run tests matching a pattern
```bash
npm test -- --grep "authentication"
```

## Test Coverage

Current coverage targets:
- Minimum coverage: 70%
- Target coverage: 80%+

View coverage report:
```bash
npm run test:coverage
open coverage/index.html
```

## Testing Stack

- **Vitest** - Fast unit test framework
- **React Testing Library** - React component testing
- **@testing-library/user-event** - User interaction simulation
- **@testing-library/jest-dom** - Custom jest matchers

## Writing Tests

### Component Test Example

```tsx
import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../../test/utils'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('should render correctly', () => {
    renderWithProviders(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('should handle user interaction', async () => {
    const user = userEvent.setup()
    renderWithProviders(<MyComponent />)

    await user.click(screen.getByRole('button'))

    expect(screen.getByText('Updated Text')).toBeInTheDocument()
  })
})
```

### Store Test Example

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { useMyStore } from '../myStore'

describe('MyStore', () => {
  beforeEach(() => {
    useMyStore.getState().reset()
  })

  it('should update state correctly', () => {
    useMyStore.getState().updateValue('new value')
    expect(useMyStore.getState().value).toBe('new value')
  })
})
```

### Hook Test Example

```typescript
import { renderHook, act } from '@testing-library/react'
import { useMyHook } from '../useMyHook'

describe('useMyHook', () => {
  it('should return expected values', () => {
    const { result } = renderHook(() => useMyHook())

    expect(result.current.value).toBe('initial')

    act(() => {
      result.current.update('new')
    })

    expect(result.current.value).toBe('new')
  })
})
```

## Best Practices

### 1. Use renderWithProviders
Always use the custom `renderWithProviders` function from test utils:

```tsx
import { renderWithProviders } from '../../test/utils'

renderWithProviders(<MyComponent />)
```

### 2. Query by Accessibility
Prefer accessible queries:

```tsx
// Good
screen.getByRole('button', { name: /submit/i })
screen.getByLabelText('Username')

// Avoid
screen.getByTestId('submit-button')
screen.getByClassName('username-input')
```

### 3. Simulate User Interactions
Use userEvent for realistic interactions:

```tsx
const user = userEvent.setup()
await user.click(button)
await user.type(input, 'text')
```

### 4. Wait for Async Updates
Use waitFor for async operations:

```tsx
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument()
})
```

### 5. Mock External Dependencies
Mock API calls and external services:

```tsx
vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))
```

### 6. Test User Workflows
Test complete user workflows, not just implementation details:

```tsx
it('should allow user to login', async () => {
  const user = userEvent.setup()

  renderWithProviders(<LoginPage />)

  await user.type(screen.getByLabelText(/username/i), 'testuser')
  await user.type(screen.getByLabelText(/password/i), 'password')
  await user.click(screen.getByRole('button', { name: /login/i }))

  await waitFor(() => {
    expect(screen.getByText(/welcome/i)).toBeInTheDocument()
  })
})
```

### 7. Clean Up After Tests
Always clean up state between tests:

```tsx
beforeEach(() => {
  useCartStore.getState().clearCart()
  vi.clearAllMocks()
})
```

## Common Patterns

### Testing Forms

```tsx
it('should submit form with valid data', async () => {
  const user = userEvent.setup()
  const onSubmit = vi.fn()

  renderWithProviders(<MyForm onSubmit={onSubmit} />)

  await user.type(screen.getByLabelText('Email'), 'test@example.com')
  await user.click(screen.getByRole('button', { name: 'Submit' }))

  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith({ email: 'test@example.com' })
  })
})
```

### Testing API Calls

```tsx
it('should fetch and display data', async () => {
  const { api } = await import('../../services/api')

  vi.mocked(api.get).mockResolvedValueOnce({
    data: { items: [{ id: 1, name: 'Item 1' }] },
  })

  renderWithProviders(<MyComponent />)

  await waitFor(() => {
    expect(screen.getByText('Item 1')).toBeInTheDocument()
  })
})
```

### Testing Error States

```tsx
it('should display error message on failure', async () => {
  const { api } = await import('../../services/api')

  vi.mocked(api.get).mockRejectedValueOnce({
    response: { data: { detail: 'Error occurred' } },
  })

  renderWithProviders(<MyComponent />)

  await waitFor(() => {
    expect(screen.getByText(/error occurred/i)).toBeInTheDocument()
  })
})
```

## Continuous Integration

Tests are automatically run on:
- Every push to any branch
- Every pull request
- Before deployment

See `.github/workflows/ci.yml` for CI configuration.

## Troubleshooting

### Tests timing out
Increase timeout in vitest.config.ts:
```ts
test: {
  testTimeout: 10000
}
```

### Tests failing randomly
Ensure proper cleanup and avoid shared state:
```tsx
beforeEach(() => {
  // Reset all state
  vi.clearAllMocks()
  cleanup()
})
```

### Mock not working
Ensure mock is defined before import:
```tsx
vi.mock('module', () => ({ ... }))
// Then import component
import MyComponent from './MyComponent'
```
