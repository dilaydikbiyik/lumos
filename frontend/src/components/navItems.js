// Labels are i18n KEYS — resolved at render time so a language switch
// re-labels the nav without a reload.
//
// Home first, then by how often a returning reader needs each one. The bar
// used to open with Explore and end with the Dashboard — the screen a
// signed-in reader lands on (utils/homeRoute) sat in the last slot, and the
// risk quiz, answered once, held the second. The first tab is where the app
// opens, so it is the dashboard; the quiz goes last.
export const NAV_ITEMS = [
  { path: '/dashboard', icon: 'dashboard', label: 'nav.dashboard' },
  { path: '/recommend', icon: 'portfolio', label: 'nav.portfolio' },
  { path: '/holdings',  icon: 'holdings',  label: 'nav.holdings'  },
  { path: '/explore',   icon: 'explore',   label: 'nav.explore'   },
  { path: '/profile',   icon: 'chat',      label: 'nav.profile'   },
]
