// Pie-slice palette — gece / ateşböceği(altın) / kahve / ember / teal / mor.
// Gold stays amber (a gold asset shown in any other colour reads wrong).
export const COLORS = ['#7C6FF7', '#5B8EF0', '#3DD68C', '#F5A524', '#F5515F', '#A78BFA', '#34D399']

export const CATEGORY_COLORS = {
  gold:   '#F5A524',  // ateşböceği amber
  stocks: '#E8663F',  // ember
  reit:   '#7A4A93',  // mor / erik
  bond:   '#1FB2A6',  // teal
  cash:   '#9C5A34',  // kahve (V5 palette)
  fund:   '#3DD68C',
}

// Category tells you WHAT an asset is, so it owns the hue — a gold slice has to
// read as gold. But a portfolio can hold two of the same kind (two REIT ETFs,
// say), and painting both the identical purple makes the chart unreadable:
// adjacent slices merge into one and the legend can't be matched back to them.
// Siblings therefore keep the hue and separate by lightness.
const SIBLING_LIGHTNESS_STEPS = [0, 16, -13, 30, -24]

function hexToHsl(hex) {
  const n = parseInt(hex.slice(1), 16)
  const r = ((n >> 16) & 255) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255
  const max = Math.max(r, g, b), min = Math.min(r, g, b)
  const l = (max + min) / 2
  if (max === min) return { h: 0, s: 0, l: l * 100 }
  const d = max - min
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
  const h = max === r ? ((g - b) / d + (g < b ? 6 : 0))
          : max === g ? (b - r) / d + 2
          : (r - g) / d + 4
  return { h: h * 60, s: s * 100, l: l * 100 }
}

function shade(hex, deltaL) {
  if (!deltaL) return hex
  const { h, s, l } = hexToHsl(hex)
  // Clamped well inside the range: a near-white or near-black slice loses the
  // hue that made the colour meaningful in the first place.
  const next = Math.min(78, Math.max(24, l + deltaL))
  return `hsl(${h.toFixed(0)} ${s.toFixed(0)}% ${next.toFixed(0)}%)`
}

/**
 * Colours for a whole allocation list, index-aligned with the input.
 * Built from the full list because a slice's colour depends on how many
 * siblings share its category — it cannot be decided one asset at a time.
 */
export function allocationColors(allocations = []) {
  const seen = {}
  return allocations.map((a, i) => {
    const base = CATEGORY_COLORS[a.category]
    if (!base) return COLORS[i % COLORS.length]
    const rank = seen[a.category] = (seen[a.category] ?? -1) + 1
    return shade(base, SIBLING_LIGHTNESS_STEPS[rank % SIBLING_LIGHTNESS_STEPS.length])
  })
}

// Single source of truth for an asset's colour — the pie, the legend and any
// card that talks about the same asset must all agree. Pass the full list to
// get sibling-aware shading; without it, the plain category colour.
export function sliceColor(allocation, index = 0, allocations = null) {
  if (allocations) return allocationColors(allocations)[index] ?? COLORS[index % COLORS.length]
  return CATEGORY_COLORS[allocation.category] || COLORS[index % COLORS.length]
}
