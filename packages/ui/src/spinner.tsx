import { CSSProperties } from 'react';

type SpinnerSize = 'sm' | 'md' | 'lg';

interface SpinnerProps {
  size?: SpinnerSize;
  label?: string;
  style?: CSSProperties;
}

const sizeMap: Record<SpinnerSize, string> = {
  sm: '1rem',
  md: '1.5rem',
  lg: '2.5rem',
};

export function Spinner({
  size = 'md',
  label = 'Loading…',
  style,
}: SpinnerProps): React.JSX.Element {
  const dim = sizeMap[size];
  return (
    <span
      role="status"
      aria-label={label}
      style={{
        display: 'inline-block',
        width: dim,
        height: dim,
        borderRadius: '50%',
        border: '2px solid rgba(99, 102, 241, 0.2)',
        borderTopColor: '#6366f1',
        animation: 'genesis-spin 0.7s linear infinite',
        flexShrink: 0,
        ...style,
      }}
    />
  );
}

/**
 * Inject the required @keyframes genesis-spin animation once.
 * Include this in your root layout or globals.css.
 *
 * @keyframes genesis-spin {
 *   to { transform: rotate(360deg); }
 * }
 */
