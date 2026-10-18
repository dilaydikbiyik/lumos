/**
 * Can this browser install a web app, and how?
 *
 * Pure functions taking a navigator-like object, because the answers are
 * the easiest thing in this app to get silently wrong and there is no DOM
 * in the test environment. Both branches below are a real device class that
 * a naive check misses:
 *
 *   iPadOS 13 and later report themselves as "Macintosh". A user-agent test
 *   for iPad therefore matches NO iPad made since 2019. Touch points are
 *   the distinguishing signal: a Mac with a touchscreen does not exist.
 *
 *   Chrome, Firefox and Edge on iOS are WebKit underneath and cannot add to
 *   the home screen at all. They are iOS, they are not Safari, and the
 *   Share-sheet gesture genuinely is not available to them — so telling
 *   their readers to tap Share sends them hunting for a menu item that is
 *   not there.
 */

/** Already running as an installed app, so there is nothing to suggest. */
export function isStandaloneDisplay(matchMedia, nav) {
  try {
    if (matchMedia && matchMedia('(display-mode: standalone)').matches) return true
  } catch { /* fall through to the Safari flag */ }
  // Safari's own non-standard property, still the only signal on iOS.
  return Boolean(nav && nav.standalone === true)
}

/** iOS Safari specifically — the only iOS browser that can install. */
export function isIosSafari(nav) {
  if (!nav || typeof nav.userAgent !== 'string') return false
  const ua = nav.userAgent
  const iPadAsMac = /Macintosh/.test(ua) && (nav.maxTouchPoints || 0) > 1
  if (!/iPhone|iPad|iPod/.test(ua) && !iPadAsMac) return false
  // The WebKit-wrapped third-party browsers, by their own UA tokens.
  return !/CriOS|FxiOS|EdgiOS|OPiOS/.test(ua)
}
