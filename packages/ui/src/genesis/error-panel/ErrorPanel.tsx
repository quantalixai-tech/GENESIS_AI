'use client';
/**
 * @genesis/ui — ErrorPanel
 *
 * User-friendly error display with optional collapsible technical detail.
 * Implements §11 (Error UX) and §12 (Repair UX) of UI/UX Design Brief.
 *
 * Shows a human-readable message by default.
 * Technical details are hidden behind a disclosure toggle.
 */
'use client';

import React, { useState, type HTMLAttributes, type ReactNode } from 'react';
import { cx } from '../../lib/utils';
import styles from './error-panel.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export interface ErrorPanelProps extends HTMLAttributes<HTMLDivElement> {
  /** Short human-readable summary shown to all users. */
  message: string;
  /** Optional call-to-action label (e.g. "Retry", "Review Details"). */
  actionLabel?: string;
  onAction?: () => void;
  /** Technical detail string (stack trace, error code, etc.). */
  technicalDetail?: string;
  /** Extra content rendered inside the technical disclosure. */
  technicalChildren?: ReactNode;
  /** Label for the "show details" toggle — defaults to "Show technical details". */
  detailToggleLabel?: string;
}

// ── Component ────────────────────────────────────────────────────────────────

export function ErrorPanel({
  message,
  actionLabel,
  onAction,
  technicalDetail,
  technicalChildren,
  detailToggleLabel = 'Show technical details',
  className,
  ...rest
}: ErrorPanelProps): React.JSX.Element {
  const [detailOpen, setDetailOpen] = useState(false);
  const hasDetail =
    technicalDetail !== undefined || technicalChildren !== undefined;

  return (
    <div
      role="alert"
      className={cx(styles.root, className)}
      {...rest}
    >
      {/* Header */}
      <div className={styles.header}>
        <span className={styles.iconWrapper} aria-hidden="true">✕</span>
        <p className={styles.message}>{message}</p>
      </div>

      {/* Action */}
      {actionLabel !== undefined && onAction !== undefined && (
        <button
          type="button"
          className={styles.actionBtn}
          onClick={onAction}
        >
          {actionLabel}
        </button>
      )}

      {/* Technical detail disclosure */}
      {hasDetail && (
        <div className={styles.disclosure}>
          <button
            type="button"
            aria-expanded={detailOpen}
            className={styles.toggle}
            onClick={() => { setDetailOpen((p) => !p); }}
          >
            <span
              className={cx(styles.chevron, detailOpen && styles.chevronOpen)}
              aria-hidden="true"
            >
              ›
            </span>
            {detailToggleLabel}
          </button>

          {detailOpen && (
            <div className={styles.detail}>
              {technicalDetail !== undefined && (
                <pre className={styles.pre}>{technicalDetail}</pre>
              )}
              {technicalChildren}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
