import clsx from "clsx";

type ButtonProps = {
  variant?:
    | "primary"
    | "gray"
    | "like"
    | "social_kakao"
    | "social_naver"
    | "social_google"
    | "modal_primary"
    | "modal_secondary";
  size?: "sm" | "md" | "lg" | "modal" | "social" | "cta";
  disabled?: boolean;
  leftIcon?: React.ReactNode;
  fullWidth?: boolean;
  children: React.ReactNode;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({
  variant = "primary",
  size = "md",
  disabled = false,
  leftIcon,
  fullWidth,
  children,
  className,
  ...props
}: ButtonProps) {
  const base =
    "w-fit flex items-center justify-center transition-colors duration-200 focus:outline-none";

  const variants = {
    primary:
      "bg-screen-0 text-primary-900 border border-primary-900 hover:bg-primary-900 hover:text-gray-0 hover:border-primary-900 disabled:bg-gray-100 disabled:text-gray-600 disabled:border-gray-100",
    gray: "bg-screen-0 text-gray-800 border border-gray-800 hover:bg-gray-800 hover:text-gray-0 hover:border-gray-800",
    like: "bg-screen-0 text-button-like border border-button-like hover:bg-button-like hover:text-gray-0 hover:border-button-like",

    social_kakao: "bg-button-kakao text-[#371C1D]",
    social_naver: "bg-button-naver text-gray-0",
    social_google: "bg-button-google text-gray-900",

    modal_primary: "bg-primary-900 text-gray-0",
    modal_secondary: "bg-secondary-900 text-primary-900",
  };

  const sizes = {
    sm: "typo-body_bold12 px-2 py-1.5 rounded-sm gap-2",
    md: "typo-body_bold12 px-3 py-2.5 rounded-sm gap-2",
    lg: "typo-body_bold14 px-4 py-3 rounded-sm gap-2.5",
    modal: "typo-body_bold18 h-14 px-2 py-4 rounded-lg",
    social: "typo-body_bold18 px-4 py-2.5 rounded-lg gap-1",
    cta: "typo-body_bold20 px-4 py-2.5 rounded-sm",
  };

  return (
    <button
      disabled={disabled}
      className={clsx(
        base,
        variants[variant],
        sizes[size],
        fullWidth ? "w-full" : "w-fit",
        className,
      )}
      {...props}
    >
      {leftIcon}
      {children}
    </button>
  );
}
