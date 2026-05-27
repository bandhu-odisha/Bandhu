/**
 * Login / Logout on the React landing navbar — matches Django
 * `.navbar .navbar-nav a.nav-button.btn` in css/custom.css (not the wider marketing CTAs).
 */
/** Navbar Login / Logout / Updates — dark navy pill (same palette as Updates CTA). */
export const LANDING_NAVBAR_AUTH_BUTTON_CLASS =
  'inline-flex cursor-pointer items-center justify-center rounded-full border border-[#004a52]/20 bg-[#0b3540] px-3.5 py-2 text-xs font-heading font-bold leading-tight text-white no-underline whitespace-nowrap ' +
  'shadow-[0_5px_16px_rgba(11,53,64,0.26)] ' +
  'transition-[background-color,box-shadow,transform] duration-300 ease-out ' +
  'hover:bg-[#005E66] hover:text-white hover:shadow-[0_8px_22px_rgba(11,53,64,0.34)] hover:-translate-y-0.5 ' +
  'motion-reduce:hover:translate-y-0 motion-reduce:transition-[background-color,box-shadow] ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#005E66]/40 focus-visible:ring-offset-2 active:translate-y-0 ' +
  'sm:px-4 sm:py-2 sm:text-sm'

const CTA_PILL_BASE =
  'inline-flex items-center justify-center rounded-full px-8 py-2.5 text-base font-heading font-bold leading-tight no-underline whitespace-nowrap sm:px-10 ' +
  'transition-[background-color,color,box-shadow,transform,border-color] duration-300 ease-out ' +
  'hover:no-underline focus:no-underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ' +
  'hover:-translate-y-0.5 active:translate-y-0 motion-reduce:hover:translate-y-0'

/** Dark pill on light / white backgrounds */
export const CTA_PILL_CLASS =
  `${CTA_PILL_BASE} border border-[#004a52]/20 bg-[#0b3540] text-white ` +
  'shadow-[0_6px_20px_rgba(11,53,64,0.28)] hover:bg-[#005E66] hover:text-white ' +
  'hover:shadow-[0_10px_28px_rgba(11,53,64,0.36)] focus-visible:ring-[#005E66]/40'

/** White pill on dark backgrounds (footer, hero overlays, etc.) */
export const CTA_PILL_ON_DARK_CLASS =
  `${CTA_PILL_BASE} border border-white/40 bg-white text-[#005E66] ` +
  'shadow-[0_6px_22px_rgba(0,0,0,0.22)] hover:bg-slate-50 hover:text-[#004a52] ' +
  'hover:shadow-[0_10px_28px_rgba(0,0,0,0.3)] focus-visible:ring-white/55'

export function ctaPillClass(onDarkSurface = false) {
  return onDarkSurface ? CTA_PILL_ON_DARK_CLASS : CTA_PILL_CLASS
}

/** Outlined pill for secondary toggles (e.g. gallery filters when inactive). */
export const CTA_PILL_OUTLINE_CLASS =
  'inline-flex items-center justify-center rounded-full border-2 border-[#005E66] bg-transparent px-8 py-2.5 text-base font-heading font-bold leading-tight text-[#005E66] transition-colors duration-200 hover:bg-[#005E66]/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#005E66]/35 focus-visible:ring-offset-2 whitespace-nowrap sm:px-10'
