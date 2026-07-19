import type React from 'react';
import clsx from 'clsx';

type ButtonProps = {
  variant?:
    | 'primary'
    | 'gray'
    | 'like'
    | 'active_like'
    | 'active_primary'
    | 'kakao'
    | 'google'
    | 'modal_primary'
    | 'modal_secondary'
    | 'cta_primary';
  size?:
    | 'sm'
    | 'md'
    | 'lg'
    | 'card'
    | 'modal'
    | 'onboarding'
    | 'social'
    | 'cta';
  disabled?: boolean;
  leftIcon?: React.ReactNode;
  fullWidth?: boolean;
  children?: React.ReactNode;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  leftIcon,
  fullWidth,
  children,
  className,
  ...props
}: ButtonProps) {
  const base =
    'group overflow-hidden flex items-center justify-center transition-all duration-300 focus:outline-none cursor-pointer disabled:cursor-not-allowed';
  const variants = {
    primary:
      'bg-screen-0 text-primary-900 border border-primary-900 hover:bg-primary-900 hover:text-gray-0 hover:border-primary-900 disabled:bg-gray-50 disabled:text-gray-600 disabled:border-gray-100 disabled:cursor-not-allowed',
    active_primary: 'bg-primary-900 text-gray-0 border border-primary-900',
    gray: 'bg-screen-0 text-gray-800 border border-gray-800 hover:bg-gray-800 hover:text-gray-0 hover:border-gray-800',
    like: 'bg-screen-0 text-button-like border border-button-like hover:bg-button-like hover:text-gray-0 hover:border-button-like',
    active_like: 'bg-button-like text-gray-0 border border-button-like',

    kakao: 'bg-button-kakao text-[#371C1D] hover:bg-button-kakao_hover',
    google: 'bg-button-google text-gray-900 hover:bg-button-google_hover',

    modal_primary:
      'bg-primary-900 text-gray-0 disabled:bg-gray-50 disabled:text-gray-600 hover:bg-primary-900/80 disabled:border-gray-100 disabled:cursor-not-allowed',
    modal_secondary:
      'bg-gray-0 text-gray-700 border-[0.5px] border-gray-700 hover:bg-gray-700 hover:text-gray-0 disabled:bg-gray-50 disabled:text-gray-600 disabled:border-gray-100 disabled:cursor-not-allowed',
    cta_primary:
      'bg-primary-900 text-gray-0 border border-primary-900 disabled:bg-gray-50 disabled:text-gray-600 disabled:border-gray-100',
  };

  const sizes = {
    sm: 'typo-body_bold12 px-2 py-1.5 rounded-sm gap-2',
    md: 'typo-body_bold12 px-3 py-2.5 rounded-sm gap-2',
    lg: 'typo-body_bold12 px-4 py-3 rounded-sm gap-2.5',
    card: 'typo-body_bold10 min-w-7 h-7 rounded-full',
    modal: 'typo-body_bold12 px-2 py-3 rounded-sm',
    onboarding: 'typo-body_bold16 px-5 py-2.5 rounded-full',
    social: 'typo-body_bold16 px-4 py-2.5 rounded-lg gap-1',
    cta: 'typo-body_bold16 px-4 py-2.5 rounded-sm',
  };

  return (
    <button
      disabled={disabled}
      className={clsx(
        base,
        variants[variant],
        sizes[size],
        fullWidth ? 'w-full' : 'w-fit',
        className
      )}
      {...props}
    >
      {leftIcon}
      {children}
    </button>
  );
}
