import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', minHeight: '100vh', gap: '16px',
          fontFamily: 'Inter, sans-serif', color: '#374151'
        }}>
          <h2>Something went wrong</h2>
          <p style={{ color: '#6B7280' }}>{this.state.error?.message}</p>
          <button
            onClick={() => window.location.href = '/'}
            style={{
              padding: '10px 24px', borderRadius: '8px',
              background: '#4F46E5', color: '#fff', border: 'none', cursor: 'pointer'
            }}
          >
            Go Home
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
