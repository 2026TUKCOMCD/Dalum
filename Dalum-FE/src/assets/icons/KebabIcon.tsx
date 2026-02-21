import type React from "react";
import type { SVGProps } from 'react';

type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
  color?: string;
};

const KebabIcon: React.FC<IconProps> = ({
  size = 10,
  color = "currentColor",
  ...props
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 2 10"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <circle cx="1" cy="1" r="1" fill={color} />
      <circle cx="1" cy="5" r="1" fill={color} />
      <circle cx="1" cy="9" r="1" fill={color} />
    </svg>
  );
};

export default KebabIcon;
