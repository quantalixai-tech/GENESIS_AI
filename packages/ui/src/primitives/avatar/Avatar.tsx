'use client';

/**
 * @genesis/ui — Avatar
 *
 * Displays a user avatar image with automatic fallback to initials.
 * No external dependencies — pure React + CSS Modules.
 *
 * Sizes: sm | md | lg | xl
 */
import React, { useState, type ImgHTMLAttributes } from 'react';
import { cx } from '../../lib/utils';
import styles from './avatar.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type AvatarSize = 'sm' | 'md' | 'lg' | 'xl';

export interface AvatarProps extends ImgHTMLAttributes<HTMLImageElement> {
  /** Full name or display name — used to generate initials. */
  name: string;
  size?: AvatarSize;
  className?: string;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 0 || parts[0] === undefined) return '?';
  const first = parts[0][0] ?? '';
  const last = parts.length > 1 ? (parts[parts.length - 1]?.[0] ?? '') : '';
  return `${first}${last}`.toUpperCase();
}

// ── Component ────────────────────────────────────────────────────────────────

export function Avatar({
  name,
  src,
  size = 'md',
  className,
  alt,
  ...rest
}: AvatarProps): React.JSX.Element {
  const [imgError, setImgError] = useState(false);
  const showFallback = src === undefined || src === '' || imgError;

  return (
    <span
      className={cx(styles.root, styles[size], className)}
      aria-label={alt ?? name}
      role="img"
    >
      {showFallback ? (
        <span className={styles.initials} aria-hidden="true">
          {getInitials(name)}
        </span>
      ) : (
        <img
          src={src}
          alt={alt ?? name}
          className={styles.image}
          onError={() => { setImgError(true); }}
          {...rest}
        />
      )}
    </span>
  );
}
