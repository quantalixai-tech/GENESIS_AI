/**
 * @genesis/ui — Button
 *
 * Variants: primary | secondary | ghost | danger
 * Sizes:    sm | md | lg
 *
 * All styles live in button.module.css.
 * Extend via `className` prop — class is appended last.
 */
'use client';

import React, { type ButtonHTMLAttributes, type ReactNode } from 'react';
import { cx } from '../../lib/utils';
import styles from './button.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
  /** Show inline spinner and disable interaction. */
  loading?: boolean;
  /** Expand to fill container width. */
  fullWidth?: boolean;
  /** Render icon-only with square proportions (no horizontal padding). */
  iconOnly?: boolean;
}

// ── Component ────────────────────────────────────────────────────────────────

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  loading = false,
  fullWidth = false,
  iconOnly = false,
  disabled,
  className,
  ...rest
}: ButtonProps): React.JSX.Element {
  const isDisabled = disabled === true || loading;

  return (
    <button
      {...rest}
      disabled={isDisabled}
      aria-busy={loading ? true : undefined}
      className={cx(
        styles.base,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth,
        iconOnly && styles.iconOnly,
        isDisabled && styles.disabled,
        className,
      )}
    >
      {loading && (
        <span className={styles.spinner} aria-hidden="true" />
      )}
      {children}
    </button>
  );
}
