import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

const NaverIcon: React.FC<IconProps> = ({ size = 32, ...props }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <rect width="32" height="32" rx="16" fill="#03C75A" />
      <path
        d="M18.39 16.14L12.71 8H8V23.2H12.93V15.06L18.61 23.2H23.32V8H18.39V16.14Z"
        fill="white"
      />
    </svg>
  );
};

export default NaverIcon;
