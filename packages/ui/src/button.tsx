'use client';

import { ReactNode, ButtonHTMLAttributes } from 'react';
import styles from './button.module.css';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
  loading?: boolean;
  fullWidth?: boolean;
}

const getVariantClass = (variant: string) => {
  switch (variant) {
    case 'primary': return styles.primary;
    case 'secondary': return styles.secondary;
    case 'ghost': return styles.ghost;
    case 'danger': return styles.danger;
    default: return styles.primary;
  }
};

const getSizeClass = (size: string) => {
  switch (size) {
    case 'sm': return styles.sm;
    case 'md': return styles.md;
    case 'lg': return styles.lg;
    default: return styles.md;
  }
};

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  loading = false,
  fullWidth = false,
  disabled,
  className = '',
  ...rest
}: ButtonProps): React.JSX.Element {
  const isDisabled = disabled || loading;
  
  const baseClasses = styles.base;
  const variantClass = getVariantClass(variant);
  const sizeClass = getSizeClass(size);
  const widthClass = fullWidth ? styles.fullWidth : '';
  const disabledClass = isDisabled ? styles.disabled : '';
  
  const combinedClasses = `${baseClasses} ${variantClass} ${sizeClass} ${widthClass} ${disabledClass} ${className}`.trim();

  return (
    <button
      {...rest}
      disabled={isDisabled}
      className={combinedClasses}
    >
      {loading && (
        <span
          className={styles.spinner}
          aria-hidden="true"
        />
      )}
      {children}
    </button>
  );
}
