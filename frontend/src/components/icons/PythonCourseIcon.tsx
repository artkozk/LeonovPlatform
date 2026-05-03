import { useId } from "react";

export type CourseIconProps = {
  size?: number;
  className?: string;
};

export function PythonCourseIcon({ size = 72, className }: CourseIconProps) {
  const scopeId = useId().replace(/:/g, "");
  const blueGradientId = `${scopeId}-python-blue`;
  const yellowGradientId = `${scopeId}-python-yellow`;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 112 112"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <rect x="1" y="1" width="110" height="110" rx="24" fill="#F8FAFC" />
      <rect x="1" y="1" width="110" height="110" rx="24" stroke="#E2E8F0" />

      <path
        d="M54.9188 0.0009C50.3351 0.0222 45.9578 0.4131 42.1063 1.0947C30.7601 3.0992 28.7001 7.2948 28.7 15.0322V25.251H55.5125V28.6572H28.7H18.6375C10.845 28.6572 4.0217 33.3409 1.8875 42.251C-0.5743 52.4639 -0.6835 58.837 1.8875 69.501C3.7935 77.4389 8.345 83.0948 16.1375 83.0948H25.3563V70.8448C25.3563 61.9949 33.0134 54.1885 42.1063 54.1885H68.8875C76.3425 54.1885 82.2938 48.0504 82.2938 40.5635V15.0322C82.2938 7.7659 76.1638 2.3074 68.8875 1.0947C64.2815 0.3279 59.5024 -0.0204 54.9188 0.0009ZM40.4188 8.2197C43.1883 8.2197 45.45 10.5183 45.45 13.3447C45.45 16.161 43.1883 18.4385 40.4188 18.4385C37.6393 18.4385 35.3875 16.1611 35.3875 13.3447C35.3875 10.5184 37.6393 8.2197 40.4188 8.2197Z"
        fill={`url(#${blueGradientId})`}
      />
      <path
        d="M85.6375 28.6572V40.5635C85.6375 49.7942 77.8116 57.5635 68.8875 57.5635H42.1063C34.7704 57.5635 28.7 63.842 28.7 71.1885V96.7197C28.7 103.9861 35.0186 108.2601 42.1063 110.3448C50.5936 112.8404 58.7325 113.2914 68.8875 110.3448C75.6377 108.3904 82.2938 104.4572 82.2938 96.7197V86.501H55.5125V83.0948H82.2938H95.7C103.4925 83.0948 106.3963 77.6594 109.1062 69.501C111.9056 61.1021 111.7865 53.0252 109.1062 42.251C107.1805 34.4936 103.5024 28.6572 95.7 28.6572H85.6375ZM70.575 93.3135C73.3545 93.3135 75.6063 95.5909 75.6063 98.4072C75.6063 101.2336 73.3545 103.5322 70.575 103.5322C67.8054 103.5322 65.5438 101.2336 65.5438 98.4072C65.5438 95.5909 67.8054 93.3135 70.575 93.3135Z"
        fill={`url(#${yellowGradientId})`}
      />

      <defs>
        <linearGradient id={blueGradientId} x1="26.6489" y1="20.6038" x2="135.6652" y2="114.3977" gradientUnits="userSpaceOnUse">
          <stop stopColor="#5A9FD4" />
          <stop offset="1" stopColor="#306998" />
        </linearGradient>
        <linearGradient id={yellowGradientId} x1="150.9611" y1="192.3518" x2="112.0314" y2="137.273" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFD43B" />
          <stop offset="1" stopColor="#FFE873" />
        </linearGradient>
      </defs>
    </svg>
  );
}
