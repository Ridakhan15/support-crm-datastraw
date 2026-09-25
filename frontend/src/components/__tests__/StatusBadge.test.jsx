import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import StatusBadge from '../StatusBadge.jsx'
import PriorityBadge from '../PriorityBadge.jsx'

describe('StatusBadge', () => {
  it('renders the status text', () => {
    render(<StatusBadge status="In Progress" />)
    expect(screen.getByText('In Progress')).toBeInTheDocument()
  })
})

describe('PriorityBadge', () => {
  it('renders the priority text', () => {
    render(<PriorityBadge priority="High" />)
    expect(screen.getByText('High')).toBeInTheDocument()
  })
})
