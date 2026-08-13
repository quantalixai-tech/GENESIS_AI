/**
 * @genesis/ui — ProgressSteps
 *
 * Step-by-step pipeline progress list (§9 of UI/UX Design Brief).
 * Displays ordered steps as done ✓ | active ● | pending ○
 *
 * Example:
 *   <ProgressSteps steps={[
 *     { id: '1', label: 'Understanding idea', state: 'done' },
 *     { id: '2', label: 'Generating backend', state: 'active' },
 *     { id: '3', label: 'Running tests',      state: 'pending' },
 *   ]} />
 */
import React, { type HTMLAttributes } from 'react';
import { cx } from '../../lib/utils';
import styles from './progress-steps.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type StepState = 'done' | 'active' | 'pending';

export interface Step {
  id: string;
  label: string;
  state: StepState;
  /** Optional sub-label (e.g. file name or detail). */
  detail?: string;
}

export interface ProgressStepsProps extends HTMLAttributes<HTMLOListElement> {
  steps: Step[];
}

// ── Icons ─────────────────────────────────────────────────────────────────────

const STEP_ICONS: Record<StepState, string> = {
  done:    '✓',
  active:  '●',
  pending: '○',
};

// ── Component ────────────────────────────────────────────────────────────────

export function ProgressSteps({
  steps,
  className,
  ...rest
}: ProgressStepsProps): React.JSX.Element {
  return (
    <ol className={cx(styles.list, className)} {...rest}>
      {steps.map((step) => (
        <li key={step.id} className={cx(styles.item, styles[step.state])}>
          <span className={styles.icon} aria-hidden="true">
            {STEP_ICONS[step.state]}
          </span>
          <span className={styles.textGroup}>
            <span className={styles.label}>{step.label}</span>
            {step.detail !== undefined && (
              <span className={styles.detail}>{step.detail}</span>
            )}
          </span>
        </li>
      ))}
    </ol>
  );
}
