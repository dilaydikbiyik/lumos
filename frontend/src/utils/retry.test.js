import { describe, expect, it } from 'vitest'
import { withRetry } from './retry'

const noWait = () => Promise.resolve()

describe('withRetry', () => {
  it('returns the first success after transient failures', async () => {
    let calls = 0
    const load = async () => { calls += 1; if (calls < 3) throw new Error('dropped'); return 'tr' }
    await expect(withRetry(load, { wait: noWait })).resolves.toBe('tr')
    expect(calls).toBe(3)
  })

  it('gives up after the last attempt with the real error', async () => {
    let calls = 0
    const load = async () => { calls += 1; throw new Error(`fail ${calls}`) }
    await expect(withRetry(load, { tries: 2, wait: noWait })).rejects.toThrow('fail 2')
    expect(calls).toBe(2)
  })
})
