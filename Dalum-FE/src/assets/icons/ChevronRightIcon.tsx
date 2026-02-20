import type React from 'react';
import type { SVGProps } from 'react';

type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
  color?: string;
};

const ChevronRightIcon: React.FC<IconProps> = ({
  size = 14,
  color = 'currentColor',
  ...props
}) => {
  return (
    <svg
      width={(size * 8) / 14}
      height={size}
      viewBox="0 0 8 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M0.75 12.75L6.75 6.75L0.75 0.75"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default ChevronRightIcon;
