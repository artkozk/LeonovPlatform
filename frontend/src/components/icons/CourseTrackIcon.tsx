import { type ReactNode, useId } from "react";

import type { CourseIconKey } from "../../lib/courseIconKey";
import { PythonCourseIcon } from "./PythonCourseIcon";

export type CourseIconProps = {
  size?: number;
  className?: string;
};

function CourseTile({ size = 72, className, children }: CourseIconProps & { children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 96 96"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <rect x="1" y="1" width="94" height="94" rx="22" fill="#F8FAFC" />
      <rect x="1" y="1" width="94" height="94" rx="22" stroke="#E2E8F0" />
      {children}
    </svg>
  );
}

export function JavaCourseIcon({ size = 72, className }: CourseIconProps) {
  const scopeId = useId().replace(/:/g, "");
  const steamGradientId = `${scopeId}-java-steam`;
  const cupGradientId = `${scopeId}-java-cup`;

  return (
    <CourseTile size={size} className={className}>
      <path
        d="M37 28C37 28 43 31.5 39 36.5C35.6 40.7 35 43 41 46C46.5 48.9 44.7 51.2 41.9 53.2"
        stroke={`url(#${steamGradientId})`}
        strokeWidth="3.2"
        strokeLinecap="round"
      />
      <path
        d="M50 24C50 24 57.5 29 52.5 35C48.6 39.6 48.5 42.3 55 45.3C61 48.2 58.2 51 55 53"
        stroke={`url(#${steamGradientId})`}
        strokeWidth="3.2"
        strokeLinecap="round"
      />
      <path
        d="M29 58.5C29 54.9 31.9 52 35.5 52H57.7C61.3 52 64.2 54.9 64.2 58.5V60.7C64.2 66.7 59.4 71.5 53.4 71.5H39.8C33.8 71.5 29 66.7 29 60.7V58.5Z"
        fill={`url(#${cupGradientId})`}
      />
      <path
        d="M64.1 55.8H66.6C70.7 55.8 74 59.1 74 63.2C74 67.3 70.7 70.6 66.6 70.6H64.1"
        stroke="#2563EB"
        strokeWidth="3.2"
        strokeLinecap="round"
      />
      <path
        d="M27.5 74.5H70.5"
        stroke="#94A3B8"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <defs>
        <linearGradient id={steamGradientId} x1="35" y1="26" x2="59" y2="56" gradientUnits="userSpaceOnUse">
          <stop stopColor="#F97316" />
          <stop offset="1" stopColor="#EA580C" />
        </linearGradient>
        <linearGradient id={cupGradientId} x1="29" y1="52" x2="65" y2="72" gradientUnits="userSpaceOnUse">
          <stop stopColor="#60A5FA" />
          <stop offset="1" stopColor="#2563EB" />
        </linearGradient>
      </defs>
    </CourseTile>
  );
}

export function FrontendCourseIcon({ size = 72, className }: CourseIconProps) {
  return (
    <CourseTile size={size} className={className}>
      <svg x="14" y="10" width="68" height="78" viewBox="64 96 384 416" aria-hidden="true">
        <polygon fill="#E44D26" points="107.644,470.877 74.633,100.62 437.367,100.62 404.321,470.819 255.778,512" />
        <polygon fill="#F16529" points="256,480.523 376.03,447.246 404.27,130.894 256,130.894" />
        <polygon
          fill="#EBEBEB"
          points="256,268.217 195.91,268.217 191.76,221.716 256,221.716 256,176.305 255.843,176.305 142.132,176.305 143.219,188.488 154.38,313.627 256,313.627"
        />
        <polygon
          fill="#EBEBEB"
          points="256,386.153 255.801,386.206 205.227,372.55 201.994,336.333 177.419,336.333 156.409,336.333 162.771,407.634 255.791,433.457 256,433.399"
        />
        <polygon
          fill="#FFFFFF"
          points="255.843,268.217 255.843,313.627 311.761,313.627 306.49,372.521 255.843,386.191 255.843,433.435 348.937,407.634 349.62,399.962 360.291,280.411 361.399,268.217 349.162,268.217"
        />
        <polygon
          fill="#FFFFFF"
          points="255.843,176.305 255.843,204.509 255.843,221.605 255.843,221.716 365.385,221.716 365.385,221.716 365.531,221.716 366.442,211.509 368.511,188.488 369.597,176.305"
        />
      </svg>
    </CourseTile>
  );
}

export function GoCourseIcon({ size = 72, className }: CourseIconProps) {
  return (
    <CourseTile size={size} className={className}>
      <text
        x="48"
        y="58"
        textAnchor="middle"
        fill="#0284C7"
        fontSize="40"
        fontWeight="700"
        fontFamily="'Geologica', 'IBM Plex Sans', 'Segoe UI', sans-serif"
        letterSpacing="-0.04em"
      >
        go
      </text>
    </CourseTile>
  );
}

export function DefaultCourseIcon({ size = 72, className }: CourseIconProps) {
  return (
    <CourseTile size={size} className={className}>
      <rect x="24" y="24" width="48" height="48" rx="12" fill="#FFFFFF" stroke="#E2E8F0" />
      <path
        d="M34 39H62"
        stroke="#94A3B8"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <path
        d="M34 48H62"
        stroke="#94A3B8"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <path
        d="M34 57H51"
        stroke="#94A3B8"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </CourseTile>
  );
}

export function CourseTrackIcon({ iconKey, size = 72, className }: CourseIconProps & { iconKey: CourseIconKey }) {
  if (iconKey === "python") return <PythonCourseIcon size={size} className={className} />;
  if (iconKey === "java") return <JavaCourseIcon size={size} className={className} />;
  if (iconKey === "go") return <GoCourseIcon size={size} className={className} />;
  if (iconKey === "frontend") return <FrontendCourseIcon size={size} className={className} />;
  return <DefaultCourseIcon size={size} className={className} />;
}
