import { HTMLAttributes } from 'react';
import styles from './spinner.module.css';

type SpinnerSize = 'sm' | 'md' | 'lg';

interface SpinnerProps extends HTMLAttributes<HTMLSpanElement> {
  size?: SpinnerSize;
  label?: string;
}

const getSizeClass = (size: string) => {
  switch (size) {
    case 'sm': return styles.sm;
    case 'md': return styles.md;
    case 'lg': return styles.lg;
    default: return styles.md;
  }
};

export function Spinner({
  size = 'md',
  label = 'Loading…',
  className = '',
  ...rest
}: SpinnerProps): React.JSX.Element {
  const baseClasses = styles.base;
  const sizeClass = getSizeClass(size);
  const combinedClasses = `${baseClasses} ${sizeClass} ${className}`.trim();
  
  return (
    <span
      role="status"
      aria-label={label}
      className={combinedClasses}
      {...rest}
    />
  );
}
