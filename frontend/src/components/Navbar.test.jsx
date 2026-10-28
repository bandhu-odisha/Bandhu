import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Navbar from './Navbar'

const URLS = {
  ankurayan: '/t/ankurayan-url/',
  people: '/t/people-url/',
  initiative_sevavrata: '/t/satabdi-url/',
}

const makeData = ({ sevavrata = true, isAdmin = false } = {}) => ({
  urls: URLS,
  user: { is_authenticated: false, is_admin: isAdmin },
  initiative_nav: { show_initiative_sevavrata: sevavrata },
  recent_activities: [{ id: 1, title: 'A notice', description: 'd', link: '#' }],
})

const linkTexts = (root) =>
  [...root.querySelectorAll('a')].map((a) => a.textContent.trim()).filter(Boolean)

const isBefore = (a, b) => Boolean(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING)

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({ ok: false, json: async () => ({}) })))
})
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

const dropdownItems = (container) => [...container.querySelectorAll('li a')].map((a) => a.textContent.trim())

describe('Navbar desktop menu', () => {
  it('puts Ankurayan first, before People, with its url', () => {
    render(<Navbar data={makeData()} />)
    const ank = screen.getByRole('link', { name: 'Ankurayan' })
    const people = screen.getByRole('link', { name: 'People' })
    expect(ank.getAttribute('href')).toBe(URLS.ankurayan)
    expect(isBefore(ank, people)).toBe(true)
    const nav = ank.parentElement
    expect(linkTexts(nav)[0]).toBe('Ankurayan')
  })

  it('has no Home or Contact link', () => {
    render(<Navbar data={makeData()} />)
    const texts = linkTexts(document.body)
    expect(texts).not.toContain('Home')
    expect(texts).not.toContain('Contact')
  })

  it('lists Odisha Satabdi first in Initiatives when enabled', async () => {
    render(<Navbar data={makeData({ sevavrata: true })} />)
    await userEvent.click(screen.getByRole('button', { name: /Initiatives/ }))
    const dd = document.body.querySelector('[data-support-dropdown]')
    expect(dd).not.toBeNull()
    const items = dropdownItems(dd)
    expect(items[0]).toBe('Odisha Satabdi')
    expect(within(dd).getByRole('link', { name: 'Odisha Satabdi' }).getAttribute('href')).toBe(URLS.initiative_sevavrata)
    expect(items[1]).toBe('Bandhughar')
    expect(items[2]).toBe('Other Activities')
    expect(items[items.length - 1]).toBe('Our Publications')
  })

  it('omits Odisha Satabdi when flag off and not admin', async () => {
    render(<Navbar data={makeData({ sevavrata: false })} />)
    await userEvent.click(screen.getByRole('button', { name: /Initiatives/ }))
    const items = dropdownItems(document.body.querySelector('[data-support-dropdown]'))
    expect(items).not.toContain('Odisha Satabdi')
    expect(items[0]).toBe('Bandhughar')
  })

  it('shows Odisha Satabdi first for admins even when flag off', async () => {
    render(<Navbar data={makeData({ sevavrata: false, isAdmin: true })} />)
    await userEvent.click(screen.getByRole('button', { name: /Initiatives/ }))
    expect(dropdownItems(document.body.querySelector('[data-support-dropdown]'))[0]).toBe('Odisha Satabdi')
  })
})

describe('Navbar mobile drawer', () => {
  const openDrawer = async (data) => {
    render(<Navbar data={data} />)
    await userEvent.click(screen.getByRole('button', { name: 'Open menu' }))
    return screen.getByRole('dialog', { name: 'Site menu' })
  }

  it('puts Ankurayan first, before People, with no Home or Contact', async () => {
    const drawer = await openDrawer(makeData())
    const ank = within(drawer).getByRole('link', { name: 'Ankurayan' })
    const people = within(drawer).getByRole('link', { name: 'People' })
    expect(ank.getAttribute('href')).toBe(URLS.ankurayan)
    expect(isBefore(ank, people)).toBe(true)
    const texts = linkTexts(drawer)
    expect(texts[0]).toBe('Ankurayan')
    expect(texts).not.toContain('Home')
    expect(texts).not.toContain('Contact')
  })

  it('lists Odisha Satabdi first under Initiatives when enabled', async () => {
    const drawer = await openDrawer(makeData({ sevavrata: true }))
    await userEvent.click(within(drawer).getByRole('button', { name: /Initiatives/ }))
    const list = within(drawer).getByRole('link', { name: 'Odisha Satabdi' }).closest('ul')
    const items = dropdownItems(list)
    expect(items[0]).toBe('Odisha Satabdi')
    expect(within(drawer).getByRole('link', { name: 'Odisha Satabdi' }).getAttribute('href')).toBe(URLS.initiative_sevavrata)
    expect(items[1]).toBe('Bandhughar')
    expect(items[items.length - 1]).toBe('Our Publications')
  })

  it('omits Odisha Satabdi when flag off and not admin', async () => {
    const drawer = await openDrawer(makeData({ sevavrata: false }))
    await userEvent.click(within(drawer).getByRole('button', { name: /Initiatives/ }))
    const list = within(drawer).getByRole('link', { name: 'Bandhughar' }).closest('ul')
    const items = dropdownItems(list)
    expect(items).not.toContain('Odisha Satabdi')
    expect(items[0]).toBe('Bandhughar')
  })
})
