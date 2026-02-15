import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

const KakaoIcon: React.FC<IconProps> = ({ size = 32, ...props }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <rect width="32" height="32" rx="16" fill="#FAE100" />
      <path
        d="M16.3811 9.14531C12.036 9.14531 8.51562 11.9283 8.51562 15.364C8.51562 17.5988 10.008 19.5595 12.2478 20.6558C12.0834 21.2687 11.6524 22.8806 11.5652 23.2245C11.458 23.653 11.7221 23.6455 11.894 23.5309C12.0286 23.4412 14.0491 22.0659 14.9211 21.473C15.3945 21.5427 15.8828 21.5801 16.3811 21.5801C20.7262 21.5801 24.2466 18.7972 24.2466 15.3615C24.2466 11.9258 20.7262 9.14282 16.3811 9.14282"
        fill="#371C1D"
      />
    </svg>
  );
};

export default KakaoIcon;
