/**
 * @genesis/ui — StatusBadge
 *
 * Semantic platform status indicator built on top of Badge.
 * Maps Genesis-specific states to visual variants.
 *
 * States: active | building | planned | error | pending-approval | done
 */
import React from 'react';
import { Badge } from '../../primitives/badge/Badge';
import type { BadgeProps } from '../../primitives/badge/Badge';

// ── Types ────────────────────────────────────────────────────────────────────

export type PlatformStatus =
  | 'active'
  | 'building'
  | 'planned'
  | 'error'
  | 'pending-approval'
  | 'done';

export interface StatusBadgeProps
  extends Omit<BadgeProps, 'variant' | 'children'> {
  status: PlatformStatus;
  /** Override the default label derived from status. */
  label?: string;
}

// ── Status config ─────────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<
  PlatformStatus,
  { label: string; variant: BadgeProps['variant']; dot: boolean }
> = {
  active:           { label: 'Active',           variant: 'success', dot: true  },
  building:         { label: 'Building',         variant: 'info',    dot: true  },
  planned:          { label: 'Planned',          variant: 'neutral', dot: false },
  error:            { label: 'Error',            variant: 'error',   dot: false },
  'pending-approval': { label: 'Needs Approval', variant: 'warning', dot: true  },
  done:             { label: 'Done',             variant: 'success', dot: false },
};

// ── Component ────────────────────────────────────────────────────────────────

export function StatusBadge({
  status,
  label,
  ...rest
}: StatusBadgeProps): React.JSX.Element {
  const config = STATUS_CONFIG[status];

  return (
    <Badge variant={config.variant} dot={config.dot} {...rest}>
      {label ?? config.label}
    </Badge>
  );
}
