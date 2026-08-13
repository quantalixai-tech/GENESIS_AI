/**
 * @genesis/ui — Spinner
 *
 * Accessible loading indicator.
 * Sizes: sm | md | lg
 */
import React, { type HTMLAttributes } from 'react';
import { cx } from '../../lib/utils';
import styles from './spinner.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type SpinnerSize = 'sm' | 'md' | 'lg';

export interface SpinnerProps extends HTMLAttributes<HTMLSpanElement> {
  size?: SpinnerSize;
  /** Accessible label for screen readers. */
  label?: string;
}

// ── Component ────────────────────────────────────────────────────────────────

export function Spinner({
  size = 'md',
  label = 'Loading…',
  className,
  ...rest
}: SpinnerProps): React.JSX.Element {
  return (
    <span
      role="status"
      aria-label={label}
      className={cx(styles.base, styles[size], className)}
      {...rest}
    />
  );
}
