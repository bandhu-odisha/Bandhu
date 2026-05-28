/** Bandhu logo: circular emblem with central swirl, six symbols, line, and Odia text ବନ୍ଧୁ */
export default function BandhuLogo({ className = 'w-12 h-14', ...props }) {
  return (
    <svg
      viewBox="0 0 80 100"
      fill="none"
      stroke="currentColor"
      strokeWidth="1"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden
      {...props}
    >
      {/* Outer circle */}
      <circle cx="40" cy="36" r="16" />
      {/* Central swirl - four curved arms */}
      <path d="M40 28 Q44 32 40 36 Q36 32 40 28" />
      <path d="M40 44 Q36 40 40 36 Q44 40 40 44" />
      <path d="M32 36 Q36 32 40 36 Q36 40 32 36" />
      <path d="M48 36 Q44 40 40 36 Q44 32 48 36" />
      {/* Six symbols on the circle - top: circle with dot */}
      <circle cx="40" cy="18" r="3.5" />
      <circle cx="40" cy="18" r="1" fill="currentColor" />
      {/* top-right: lotus petals */}
      <g transform="translate(52 22)">
        <path d="M0 -3 Q2 0 0 3 Q-2 0 0 -3" />
        <path d="M2.6 1.5 Q0 3 -2.6 1.5 Q0 0 2.6 1.5" />
        <path d="M2.6 -1.5 Q0 -3 -2.6 -1.5 Q0 0 2.6 -1.5" />
      </g>
      {/* right: arrow */}
      <path d="M60 36 l-5-3 v6 z" />
      <line x1="55" y1="36" x2="52" y2="36" />
      {/* bottom-right: concentric circles */}
      <circle cx="52" cy="52" r="3" />
      <circle cx="52" cy="52" r="1.5" />
      <circle cx="52" cy="52" r="0.6" fill="currentColor" />
      {/* bottom-left: leaf */}
      <path d="M28 52 Q24 56 26 58 Q28 54 28 52" />
      {/* top-left: leaf */}
      <path d="M28 22 Q24 26 26 30 Q28 26 28 22" />
      {/* Horizontal line below emblem */}
      <line x1="30" y1="58" x2="50" y2="58" strokeWidth="1.2" />
      {/* Odia: ବନ୍ଧୁ (Bandhu) */}
      <text
        x="40"
        y="78"
        textAnchor="middle"
        fill="currentColor"
        stroke="none"
        fontSize="13"
        fontWeight="500"
        fontFamily="'Noto Sans Oriya', 'Noto Sans Odia', system-ui, sans-serif"
      >
        ବନ୍ଧୁ
      </text>
    </svg>
  )
}
