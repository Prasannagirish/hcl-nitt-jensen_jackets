import { Component } from 'react'

// A crash while drawing a page shows a plain message and a way back, not a blank screen.
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { failed: false }
  }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error) {
    console.error('page failed to draw', error)
  }

  render() {
    if (!this.state.failed) return this.props.children
    return (
      <main>
        <p className="notice error" role="alert">
          Something went wrong while showing this page. Your work on the server is not affected.
        </p>
        <div>
          <button className="primary" onClick={() => { window.location.hash = '#/'; window.location.reload() }}>
            Back to the start
          </button>
        </div>
      </main>
    )
  }
}
