/**
 * @genesis/ui — Alert
 *
 * Contextual feedback panel. Four severity variants aligned with
 * the Genesis UX principle of Transparency (UX-005) and
 * Error UX (§11 of UI/UX Design Brief).
 *
 * Variants: info | success | warning | error
 */
import React, { type HTMLAttributes, type ReactNode } from 'react';
import { cx } from '../../lib/utils';
import styles from './alert.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type AlertVariant = 'info' | 'success' | 'warning' | 'error';

export interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
  /** Override the auto-selected icon with a custom node. */
  icon?: ReactNode;
  /** Hide the default icon entirely. */
  hideIcon?: boolean;
}

// ── Default icons ─────────────────────────────────────────────────────────────

const DEFAULT_ICONS: Record<AlertVariant, string> = {
  info:    'ℹ',
  success: '✓',
  warning: '⚠',
  error:   '✕',
};

// ── Component ────────────────────────────────────────────────────────────────

export function Alert({
  variant = 'info',
  title,
  children,
  icon,
  hideIcon = false,
  className,
  ...rest
}: AlertProps): React.JSX.Element {
  const resolvedIcon = icon ?? DEFAULT_ICONS[variant];

  return (
    <div
      role={variant === 'error' || variant === 'warning' ? 'alert' : 'status'}
      className={cx(styles.root, styles[variant], className)}
      {...rest}
    >
      {!hideIcon && (
        <span className={styles.icon} aria-hidden="true">
          {resolvedIcon}
        </span>
      )}

      <div className={styles.body}>
        {title !== undefined && (
          <p className={styles.title}>{title}</p>
        )}
        <div className={styles.content}>{children}</div>
      </div>
    </div>
  );
}
