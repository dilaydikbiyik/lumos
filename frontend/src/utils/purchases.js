import { isNativeApp } from './platform'

/**
 * In-app purchase in the store build, through RevenueCat.
 *
 * Apple requires a digital subscription bought inside an iOS app to go
 * through its in-app purchase, and forbids pointing to a web checkout from
 * the app. So the native shell sells through RevenueCat (which wraps
 * StoreKit and reports to the backend by webhook), and the web sells
 * through Lemon Squeezy. Without VITE_REVENUECAT_IOS_KEY the native app
 * simply shows no buy button.
 *
 * The RevenueCat offering must hold two packages whose identifiers are
 * "plus" and "pro", each granting the entitlement of the same name — that
 * is what the backend reads (docs/billing-setup.md).
 */
const API_KEY = import.meta.env.VITE_REVENUECAT_IOS_KEY

let configuredFor = null

async function sdk() {
  const { Purchases } = await import('@revenuecat/purchases-capacitor')
  return Purchases
}

export function nativePurchasesAvailable() {
  return isNativeApp() && Boolean(API_KEY)
}

/** Configure once per signed-in account; the Clerk id is the app user id,
    which is how the webhook finds the reader. */
export async function configurePurchases(userId) {
  if (!nativePurchasesAvailable() || !userId || configuredFor === userId) return
  const Purchases = await sdk()
  if (configuredFor) await Purchases.logIn({ appUserID: userId })
  else await Purchases.configure({ apiKey: API_KEY, appUserID: userId })
  configuredFor = userId
}

/** {plus, pro} → RevenueCat package, from the current offering. */
export async function nativePackages() {
  const Purchases = await sdk()
  const offerings = await Purchases.getOfferings()
  const packages = offerings?.current?.availablePackages || []
  const byPlan = {}
  for (const p of packages) {
    if (p.identifier === 'plus' || p.identifier === 'pro') byPlan[p.identifier] = p
  }
  return byPlan
}

export async function buyNative(pkg) {
  const Purchases = await sdk()
  return Purchases.purchasePackage({ aPackage: pkg })
}

export async function restoreNative() {
  const Purchases = await sdk()
  return Purchases.restorePurchases()
}
