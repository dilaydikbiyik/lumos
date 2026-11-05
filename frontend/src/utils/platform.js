import { Capacitor } from '@capacitor/core'

/**
 * Running inside the App Store / Play Store build rather than a browser.
 *
 * The web build is bundled into a Capacitor shell for the stores, and some
 * things that are right on the web are wrong there: there is nothing to
 * "add to the home screen" in an app that is already installed, and the
 * Web Push API this app uses on the web does not exist in the shell's
 * WebView — native push goes through APNs/FCM instead.
 *
 * Capacitor.isNativePlatform() is false in every browser, so importing this
 * costs the web build nothing but a few kilobytes.
 */
export function isNativeApp() {
  try {
    return Capacitor.isNativePlatform()
  } catch {
    return false
  }
}
