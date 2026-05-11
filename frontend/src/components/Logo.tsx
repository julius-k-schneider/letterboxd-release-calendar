type LogoProps = {
  size?: number;
};

export function Logo({ size = 48 }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Letterboxd Release Calendar logo"
    >
      <defs>
        <clipPath id="calendar-body">
          <rect x="6" y="12" width="52" height="46" rx="6" />
        </clipPath>
      </defs>

      <rect x="6" y="12" width="52" height="46" rx="6" fill="#f5f5f4" />

      <g clipPath="url(#calendar-body)">
        <rect x="6" y="12" width="17.34" height="14" fill="#00E054" />
        <rect x="23.34" y="12" width="17.32" height="14" fill="#40BCF4" />
        <rect x="40.66" y="12" width="17.34" height="14" fill="#FF8000" />
      </g>

      <rect x="18" y="6" width="5" height="14" rx="2.5" fill="#2a2f37" />
      <rect x="41" y="6" width="5" height="14" rx="2.5" fill="#2a2f37" />
      <circle cx="20.5" cy="13" r="1.2" fill="#f5f5f4" />
      <circle cx="43.5" cy="13" r="1.2" fill="#f5f5f4" />

      <text
        x="32"
        y="49"
        textAnchor="middle"
        fontFamily="Inter, -apple-system, BlinkMacSystemFont, sans-serif"
        fontWeight="700"
        fontSize="20"
        fill="#15181d"
        letterSpacing="-0.5"
      >
        31
      </text>
    </svg>
  );
}
