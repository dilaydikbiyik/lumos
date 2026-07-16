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

// Single source of truth for an asset's colour — the pie, the legend and
// any card that talks about the same asset must all agree.
export function sliceColor(allocation, index = 0) {
  return CATEGORY_COLORS[allocation.category] || COLORS[index % COLORS.length]
}
