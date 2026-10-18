import { describe, it, expect } from 'vitest'
import { isIosSafari, isStandaloneDisplay } from './install'

// Real user-agent strings, because the two bugs this guards against are
// both "the obvious check matches the wrong set of devices".
const UA = {
  iphoneSafari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
  iphoneChrome: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.89 Mobile/15E148 Safari/604.1',
  iphoneFirefox: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/124.0 Mobile/15E148 Safari/605.1.15',
  ipadOS: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
  macSafari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
  androidChrome: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
}

describe('iOS Safari detection', () => {
  it('recognises iPhone Safari, which is the one browser that can install', () => {
    expect(isIosSafari({ userAgent: UA.iphoneSafari, maxTouchPoints: 5 })).toBe(true)
  })

  it('recognises an iPad even though iPadOS claims to be a Mac', () => {
    // The bug a user-agent test for "iPad" produces: it matches no iPad
    // made since 2019, because iPadOS 13+ reports "Macintosh".
    expect(isIosSafari({ userAgent: UA.ipadOS, maxTouchPoints: 5 })).toBe(true)
  })

  it('does not mistake a real Mac for an iPad', () => {
    // Same user-agent as the iPad above. Touch points are the ONLY thing
    // telling them apart, which is why the function takes them.
    expect(isIosSafari({ userAgent: UA.macSafari, maxTouchPoints: 0 })).toBe(false)
  })

  it('excludes Chrome and Firefox on iOS, which cannot install at all', () => {
    // They are WebKit underneath and have no Add to Home Screen, so the
    // Share-sheet instructions would send the reader hunting for a menu
    // item that does not exist.
    expect(isIosSafari({ userAgent: UA.iphoneChrome, maxTouchPoints: 5 })).toBe(false)
    expect(isIosSafari({ userAgent: UA.iphoneFirefox, maxTouchPoints: 5 })).toBe(false)
  })

  it('is false on Android, which gets the real prompt instead', () => {
    expect(isIosSafari({ userAgent: UA.androidChrome, maxTouchPoints: 5 })).toBe(false)
  })

  it('survives a navigator it cannot read', () => {
    expect(isIosSafari(undefined)).toBe(false)
    expect(isIosSafari({})).toBe(false)
  })
})

describe('already-installed detection', () => {
  const mm = matches => () => ({ matches })

  it('is true in standalone display mode', () => {
    expect(isStandaloneDisplay(mm(true), {})).toBe(true)
  })

  it('is true via Safari\'s own flag, the only signal on iOS', () => {
    expect(isStandaloneDisplay(mm(false), { standalone: true })).toBe(true)
  })

  it('is false in a normal browser tab', () => {
    expect(isStandaloneDisplay(mm(false), { standalone: false })).toBe(false)
  })

  it('falls back to the Safari flag when matchMedia throws', () => {
    const throwing = () => { throw new Error('no matchMedia') }
    expect(isStandaloneDisplay(throwing, { standalone: true })).toBe(true)
    expect(isStandaloneDisplay(throwing, {})).toBe(false)
  })
})
