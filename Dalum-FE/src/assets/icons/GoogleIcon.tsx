import type React from "react";
import type { SVGProps } from 'react';

type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

const GoogleIcon: React.FC<IconProps> = ({ size = 32, ...props }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <rect width="32" height="32" rx="16" fill="#F2F2F2" />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M24.64 16.2042C24.64 15.566 24.5827 14.9524 24.4764 14.3633H16V17.8446H20.8436C20.635 18.9696 20.0009 19.9228 19.0477 20.561V22.8192H21.9564C23.6582 21.2524 24.64 18.9451 24.64 16.2042Z"
        fill="#4285F4"
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M15.9998 25C18.4298 25 20.467 24.1941 21.9561 22.8195L19.0475 20.5613C18.2416 21.1013 17.2107 21.4204 15.9998 21.4204C13.6557 21.4204 11.6716 19.8372 10.9638 17.71H7.95703V20.0418C9.43794 22.9831 12.4816 25 15.9998 25Z"
        fill="#34A853"
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M10.9641 17.7101C10.7841 17.1701 10.6818 16.5933 10.6818 16.0001C10.6818 15.4069 10.7841 14.8301 10.9641 14.2901V11.9583H7.95727C7.34773 13.1733 7 14.5478 7 16.0001C7 17.4523 7.34773 18.8269 7.95727 20.0419L10.9641 17.7101Z"
        fill="#FBBC05"
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M15.9998 10.5795C17.3211 10.5795 18.5075 11.0336 19.4402 11.9255L22.0216 9.34409C20.4629 7.89182 18.4257 7 15.9998 7C12.4816 7 9.43794 9.01682 7.95703 11.9582L10.9638 14.29C11.6716 12.1627 13.6557 10.5795 15.9998 10.5795Z"
        fill="#EA4335"
      />
    </svg>
  );
};

export default GoogleIcon;
