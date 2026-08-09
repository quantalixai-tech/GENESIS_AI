import { HTMLAttributes, ReactNode } from 'react';
import styles from './badge.module.css';

type BadgeVariant = 'active' | 'planned' | 'error' | 'warning' | 'neutral' | 'info';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?: BadgeVariant;
}

const getVariantClass = (variant: string) => {
  switch (variant) {
    case 'active': return styles.active;
    case 'planned': return styles.planned;
    case 'error': return styles.error;
    case 'warning': return styles.warning;
    case 'neutral': return styles.neutral;
    case 'info': return styles.info;
    default: return styles.neutral;
  }
};

export function Badge({
  children,
  variant = 'neutral',
  className = '',
  ...rest
}: BadgeProps): React.JSX.Element {
  const baseClasses = styles.base;
  const variantClass = getVariantClass(variant);
  const combinedClasses = `${baseClasses} ${variantClass} ${className}`.trim();
  
  return (
    <span
      className={combinedClasses}
      {...rest}
    >
      {children}
    </span>
  );
}
