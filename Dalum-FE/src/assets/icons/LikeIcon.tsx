import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & {
  size?: number;
  color?: string;
};

const LikeIcon: React.FC<IconProps> = ({
  size = 32,
  color = "currentColor",
  ...props
}) => {
  return (
    <svg
      width={size}
      height={(size * 30) / 32}
      viewBox="0 0 32 30"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M23.2 0C20.416 0 17.744 1.296 16 3.328C14.256 1.296 11.584 0 8.8 0C3.872 0 0 3.856 0 8.8C0 14.832 5.44 19.776 13.68 27.248L16 29.36L18.32 27.248C26.56 19.776 32 14.832 32 8.8C32 3.856 28.128 0 23.2 0Z"
        fill={color}
      />
    </svg>
  );
};

export default LikeIcon;
