/**
 * @genesis/ui — Progress
 *
 * Determinate progress bar (0–100).
 * Pure HTML/CSS — no external dependencies.
 *
 * Sizes: sm | md | lg
 */
import React, { type HTMLAttributes } from 'react';
import { cx } from '../../lib/utils';
import styles from './progress.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type ProgressSize = 'sm' | 'md' | 'lg';

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  /** Value 0–100. */
  value: number;
  /** Max value — defaults to 100. */
  max?: number;
  size?: ProgressSize;
  /** Accessible label for screen readers. */
  label?: string;
  /** Show percentage text alongside the bar. */
  showLabel?: boolean;
}

// ── Component ────────────────────────────────────────────────────────────────

export function Progress({
  value,
  max = 100,
  size = 'md',
  label = 'Progress',
  showLabel = false,
  className,
  ...rest
}: ProgressProps): React.JSX.Element {
  const clamped = Math.min(Math.max(0, value), max);
  const pct = Math.round((clamped / max) * 100);

  return (
    <div className={cx(styles.root, className)} {...rest}>
      {showLabel && (
        <div className={styles.labelRow}>
          <span className={styles.labelText}>{label}</span>
          <span className={styles.labelValue}>{pct}%</span>
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label}
        className={cx(styles.track, styles[size])}
      >
        <div
          className={styles.fill}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
