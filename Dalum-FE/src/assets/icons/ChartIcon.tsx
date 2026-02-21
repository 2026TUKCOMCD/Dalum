import type React from "react";
import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
  color?: string;
};

const ChartIcon: React.FC<IconProps> = ({
  size = 32,
  color = "currentColor",
  ...props
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M27.2 0H4.8C2.08 0 0 2.08 0 4.8V27.2C0 29.92 2.08 32 4.8 32H27.2C29.92 32 32 29.92 32 27.2V4.8C32 2.08 29.92 0 27.2 0ZM9.6 24C9.6 24.96 8.96 25.6 8 25.6C7.04 25.6 6.4 24.96 6.4 24V17.6C6.4 16.64 7.04 16 8 16C8.96 16 9.6 16.64 9.6 17.6V24ZM17.6 24C17.6 24.96 16.96 25.6 16 25.6C15.04 25.6 14.4 24.96 14.4 24V8C14.4 7.04 15.04 6.4 16 6.4C16.96 6.4 17.6 7.04 17.6 8V24ZM25.6 24C25.6 24.96 24.96 25.6 24 25.6C23.04 25.6 22.4 24.96 22.4 24V14.4C22.4 13.44 23.04 12.8 24 12.8C24.96 12.8 25.6 13.44 25.6 14.4V24Z"
        fill={color}
      />
    </svg>
  );
};

export default ChartIcon;
