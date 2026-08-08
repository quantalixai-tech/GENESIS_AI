'use client';

import { CSSProperties, ReactNode, ButtonHTMLAttributes } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
  loading?: boolean;
  fullWidth?: boolean;
}

const variantStyles: Record<ButtonVariant, CSSProperties> = {
  primary: {
    background: 'linear-gradient(135deg, #6366f1, #7c3aed)',
    color: '#fff',
    border: '1px solid transparent',
    boxShadow: '0 4px 14px rgba(99, 102, 241, 0.3)',
  },
  secondary: {
    background: 'rgba(255, 255, 255, 0.03)',
    color: '#94a3b8',
    border: '1px solid rgba(255, 255, 255, 0.08)',
  },
  ghost: {
    background: 'transparent',
    color: '#94a3b8',
    border: '1px solid transparent',
  },
  danger: {
    background: 'rgba(239, 68, 68, 0.1)',
    color: '#ef4444',
    border: '1px solid rgba(239, 68, 68, 0.3)',
  },
};

const sizeStyles: Record<ButtonSize, CSSProperties> = {
  sm: { padding: '0.35rem 0.85rem', fontSize: '0.8rem' },
  md: { padding: '0.6rem 1.25rem', fontSize: '0.875rem' },
  lg: { padding: '0.75rem 1.75rem', fontSize: '0.95rem' },
};

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  loading = false,
  fullWidth = false,
  disabled,
  style,
  ...rest
}: ButtonProps): React.JSX.Element {
  const isDisabled = disabled || loading;

  return (
    <button
      {...rest}
      disabled={isDisabled}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.4rem',
        fontFamily: 'inherit',
        fontWeight: 600,
        borderRadius: '10px',
        cursor: isDisabled ? 'not-allowed' : 'pointer',
        opacity: isDisabled ? 0.5 : 1,
        transition: 'transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease',
        width: fullWidth ? '100%' : undefined,
        whiteSpace: 'nowrap',
        letterSpacing: '0.01em',
        ...variantStyles[variant],
        ...sizeStyles[size],
        ...style,
      }}
    >
      {loading && (
        <span
          style={{
            width: '0.9em',
            height: '0.9em',
            borderRadius: '50%',
            border: '2px solid currentColor',
            borderTopColor: 'transparent',
            display: 'inline-block',
            animation: 'genesis-spin 0.7s linear infinite',
          }}
          aria-hidden="true"
        />
      )}
      {children}
    </button>
  );
}
