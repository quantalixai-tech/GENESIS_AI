/**
 * @genesis/ui — Input
 *
 * Accessible text input with label, helper text, and error state.
 *
 * All state is communicated structurally:
 *   - `error` string → renders error message + aria-describedby
 *   - `helperText`   → renders helper text below field
 *   - `required`     → adds * to label, sets aria-required
 */
'use client';

import React, {
  type InputHTMLAttributes,
  type ReactNode,
  useId,
} from 'react';
import { cx } from '../../lib/utils';
import styles from './input.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  /** Visible label — always required for accessibility. */
  label: string;
  /** Hint text displayed below the field. */
  helperText?: string;
  /** Error message — renders field in error state when non-empty. */
  error?: string;
  /** Optional icon node rendered on the left inside the field. */
  leadingIcon?: ReactNode;
  /** Optional node rendered on the right inside the field. */
  trailingElement?: ReactNode;
}

// ── Component ────────────────────────────────────────────────────────────────

export function Input({
  label,
  helperText,
  error,
  leadingIcon,
  trailingElement,
  className,
  required,
  disabled,
  ...rest
}: InputProps): React.JSX.Element {
  const id = useId();
  const helperId = `${id}-helper`;
  const errorId = `${id}-error`;
  const hasError = Boolean(error);

  return (
    <div className={styles.root}>
      {/* Label */}
      <label htmlFor={id} className={styles.label}>
        {label}
        {required === true && (
          <span className={styles.required} aria-hidden="true"> *</span>
        )}
      </label>

      {/* Field wrapper */}
      <div
        className={cx(
          styles.fieldWrapper,
          hasError && styles.fieldWrapperError,
          disabled === true && styles.fieldWrapperDisabled,
        )}
      >
        {leadingIcon !== undefined && (
          <span className={styles.leadingIcon} aria-hidden="true">
            {leadingIcon}
          </span>
        )}

        <input
          id={id}
          required={required}
          disabled={disabled}
          aria-required={required}
          aria-invalid={hasError ? true : undefined}
          aria-describedby={
            hasError
              ? errorId
              : helperText !== undefined
                ? helperId
                : undefined
          }
          className={cx(
            styles.input,
            leadingIcon !== undefined && styles.inputWithLeading,
            trailingElement !== undefined && styles.inputWithTrailing,
            className,
          )}
          {...rest}
        />

        {trailingElement !== undefined && (
          <span className={styles.trailingElement}>{trailingElement}</span>
        )}
      </div>

      {/* Sub-label: error takes priority over helper */}
      {hasError ? (
        <p id={errorId} role="alert" className={styles.errorText}>
          {error}
        </p>
      ) : helperText !== undefined ? (
        <p id={helperId} className={styles.helperText}>
          {helperText}
        </p>
      ) : null}
    </div>
  );
}
