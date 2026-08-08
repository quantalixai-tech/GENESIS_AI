import { CSSProperties, ReactNode } from 'react';

type BadgeVariant = 'active' | 'planned' | 'error' | 'warning' | 'neutral' | 'info';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  className?: string;
  style?: CSSProperties;
}

const variantStyles: Record<BadgeVariant, CSSProperties> = {
  active: {
    background: 'rgba(16, 185, 129, 0.1)',
    color: '#10b981',
    border: '1px solid rgba(16, 185, 129, 0.2)',
  },
  planned: {
    background: 'rgba(71, 85, 105, 0.1)',
    color: '#64748b',
    border: '1px solid rgba(71, 85, 105, 0.2)',
  },
  error: {
    background: 'rgba(239, 68, 68, 0.1)',
    color: '#ef4444',
    border: '1px solid rgba(239, 68, 68, 0.2)',
  },
  warning: {
    background: 'rgba(245, 158, 11, 0.1)',
    color: '#f59e0b',
    border: '1px solid rgba(245, 158, 11, 0.2)',
  },
  neutral: {
    background: 'rgba(255, 255, 255, 0.04)',
    color: '#94a3b8',
    border: '1px solid rgba(255, 255, 255, 0.08)',
  },
  info: {
    background: 'rgba(99, 102, 241, 0.1)',
    color: '#818cf8',
    border: '1px solid rgba(99, 102, 241, 0.2)',
  },
};

export function Badge({
  children,
  variant = 'neutral',
  className,
  style,
}: BadgeProps): React.JSX.Element {
  return (
    <span
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.3rem',
        padding: '0.2rem 0.55rem',
        borderRadius: '100px',
        fontSize: '0.7rem',
        fontWeight: 600,
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
        whiteSpace: 'nowrap',
        ...variantStyles[variant],
        ...style,
      }}
    >
      {children}
    </span>
  );
}
