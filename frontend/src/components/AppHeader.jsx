import { SignedIn, UserButton } from '@clerk/clerk-react'
import LumosLogo from './LumosLogo'
import MarketSwitcher from './MarketSwitcher'
import LanguageSwitcher from './LanguageSwitcher'

/**
 * The one header every signed-in page uses.
 *
 * It exists because the market and language selectors lived only in the
 * desktop sidebar, which does not render below 768px — so a phone user could
 * not change their market at all, and could only change language on the
 * landing page. Nine pages had hand-copied the same three lines, so there was
 * no single place to fix that.
 *
 * The selectors are marked `mobile-only`: on desktop the sidebar already
 * shows them and a second copy would be clutter.
 */
export default function AppHeader() {
  return (
    <header className="navbar">
      <LumosLogo />
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 'auto' }}>
        <div className="mobile-only" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <MarketSwitcher compact />
          <LanguageSwitcher compact />
        </div>
        <SignedIn><UserButton afterSignOutUrl="/" /></SignedIn>
      </div>
    </header>
  )
}
