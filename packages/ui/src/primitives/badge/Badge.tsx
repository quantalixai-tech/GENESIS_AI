/**
 * @genesis/ui — Badge
 *
 * Semantic status label. Variants match Genesis platform states.
 *
 * Variants: default | success | warning | error | info | neutral
 * Options:  dot (adds a coloured pulse dot)
 */
import React, { type HTMLAttributes, type ReactNode } from 'react';
import { cx } from '../../lib/utils';
import styles from './badge.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type BadgeVariant =
  | 'default'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'neutral';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?: BadgeVariant;
  /** Renders a small coloured dot before the label. */
  dot?: boolean;
}

// ── Component ────────────────────────────────────────────────────────────────

export function Badge({
  children,
  variant = 'neutral',
  dot = false,
  className,
  ...rest
}: BadgeProps): React.JSX.Element {
  return (
    <span
      className={cx(styles.base, styles[variant], className)}
      {...rest}
    >
      {dot && <span className={styles.dot} aria-hidden="true" />}
      {children}
    </span>
  );
}
