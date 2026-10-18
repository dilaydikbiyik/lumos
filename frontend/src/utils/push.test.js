import { describe, it, expect } from 'vitest'
import { urlBase64ToUint8Array } from './push'

describe('VAPID key conversion', () => {
  // The single most error-prone line in the push feature, and it fails
  // SILENTLY: a wrong conversion produces a subscription that never
  // arrives, or one encrypted for nobody. No exception, no log.
  it('restores padding that unpadded base64 dropped', () => {
    // "Lumos" -> standard base64 "THVtb3M=" with one pad character.
    expect(Array.from(urlBase64ToUint8Array('THVtb3M')))
      .toEqual([76, 117, 109, 111, 115])
  })

  it('converts the URL-safe alphabet back to standard base64', () => {
    // 0xFB 0xFF encodes as "+/8=" in standard base64 and "-_8" URL-safe.
    // Without both substitutions atob throws or returns the wrong bytes.
    expect(Array.from(urlBase64ToUint8Array('-_8'))).toEqual([251, 255])
  })

  it('handles input that needs no padding', () => {
    expect(Array.from(urlBase64ToUint8Array('THVt'))).toEqual([76, 117, 109])
  })

  it('produces the 65 bytes a real VAPID public key decodes to', () => {
    // An uncompressed EC point is 0x04 || X || Y. A key that decodes to any
    // other length is one the browser will reject, so the length is the
    // cheapest end-to-end check available without a network.
    // 87 unpadded characters, which is what 65 bytes encodes to: 65 is
    // 3*21 + 2, so the final group is 3 characters rather than 4. My first
    // attempt used 86 and decoded to 64 — the arithmetic is exactly the
    // kind of off-by-one this test exists to catch.
    const key = 'BE2FeSYz47' + 'A'.repeat(77)
    const bytes = urlBase64ToUint8Array(key)
    expect(bytes.length).toBe(65)
    expect(bytes[0]).toBe(4)
  })
})
