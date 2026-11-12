import { beforeEach, describe, expect, it } from 'vitest'
import { forgetUser, userKey } from './storage'

describe('forgetUser', () => {
  beforeEach(() => {
    const store = new Map()
    globalThis.localStorage = {
      get length() { return store.size },
      key: i => [...store.keys()][i] ?? null,
      getItem: k => (store.has(k) ? store.get(k) : null),
      setItem: (k, v) => store.set(k, String(v)),
      removeItem: k => store.delete(k),
      clear: () => store.clear(),
    }
  })

  it("removes one account's copies and keeps the device's and others'", () => {
    localStorage.setItem(userKey('holdings-TR', 'user_a'), '1')
    localStorage.setItem(userKey('quiz-draft', 'user_a'), '1')
    localStorage.setItem('lumos-profile-user_a', '1')
    localStorage.setItem(userKey('holdings-TR', 'user_b'), '1')
    localStorage.setItem('lumos-language', 'tr')
    forgetUser('user_a')
    expect(localStorage.length).toBe(2)
    expect(localStorage.getItem('lumos-language')).toBe('tr')
    expect(localStorage.getItem(userKey('holdings-TR', 'user_b'))).toBe('1')
  })
})
