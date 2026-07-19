// Social apps open links in an embedded webview instead of the real browser.
// Google refuses OAuth in those (error: disallowed_useragent), so "Sign in with
// Google" simply fails for anyone arriving from a LinkedIn or Instagram post —
// exactly the traffic a launch post brings. We can't fix their webview, but we
// can tell the user to open the page in their browser before they hit the wall.
const IN_APP_MARKERS = [
  'LinkedInApp',
  'FBAN', 'FBAV', 'FB_IAB',   // Facebook / Messenger
  'Instagram',
  'Twitter',
  'Line/',
  'MicroMessenger',           // WeChat
]

export function isInAppBrowser() {
  if (typeof navigator === 'undefined') return false
  const ua = navigator.userAgent || ''
  return IN_APP_MARKERS.some(marker => ua.includes(marker))
}
