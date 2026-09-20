import type { CapacitorConfig } from '@capacitor/cli'

/**
 * Capacitor wrap of the existing Vite build. No rewrite — this is what the
 * PWA work was building toward: the same `dist/` that Vercel serves, loaded
 * by a native shell that can receive push notifications.
 *
 * Push is the actual reason to be in a store. The behavioural coach's "the
 * market dropped, here is why not to sell" is worthless an hour late, and
 * iOS web push cannot carry it reliably.
 *
 * `appId` is permanent. Both stores treat it as identity and neither lets you
 * change it after the first submission, which is why it is decided here and
 * in docs/store-submission.md rather than at `npx cap add` time.
 */
const config: CapacitorConfig = {
  appId: 'app.lumos.mobile',
  appName: 'Lumos',
  webDir: 'dist',

  // No `server.url`. Pointing the shell at the live site is tempting and is
  // how you ship an app that is a browser in a costume — both stores reject
  // that, and it breaks entirely when the user is offline. The build is
  // bundled; only the API is remote.
  ios: {
    contentInset: 'always',
    // The app has no tracking, no advertising SDK and no IDFA, so
    // NSUserTrackingUsageDescription is deliberately absent: declaring it
    // would prompt users for permission to do something Lumos never does.
    // Verify this still holds before each release — an analytics SDK added
    // later would silently introduce an IDFA dependency and a rejection.
    limitsNavigationsToAppBoundDomains: true,
  },
  android: {
    allowMixedContent: false,
  },

  plugins: {
    SplashScreen: {
      launchShowDuration: 1200,
      launchAutoHide: true,
      // Matches the artwork's own background (#0A0B12), sampled rather than
      // guessed — see brand/generate-app-icons.py.
      backgroundColor: '#0A0B12',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
    PushNotifications: {
      // The coach's whole value is being timely, so the notification must
      // present itself even with the app in the foreground.
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#0A0B12',
    },
  },
}

export default config
