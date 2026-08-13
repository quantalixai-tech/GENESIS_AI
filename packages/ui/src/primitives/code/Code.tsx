/**
 * @genesis/ui — Code
 *
 * Inline or block code display.
 * - `block={false}` (default) → renders <code>
 * - `block={true}`            → renders <pre><code>
 */
import React, { type ReactNode } from 'react';
import { cx } from '../../lib/utils';
import styles from './code.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export interface CodeProps {
  children: ReactNode;
  className?: string;
  /** Render as a block pre/code element instead of inline. */
  block?: boolean;
}

// ── Component ────────────────────────────────────────────────────────────────

export function Code({
  children,
  className,
  block = false,
}: CodeProps): React.JSX.Element {
  if (block) {
    return (
      <pre className={cx(styles.block, className)}>
        <code>{children}</code>
      </pre>
    );
  }
  return (
    <code className={cx(styles.inline, className)}>{children}</code>
  );
}
