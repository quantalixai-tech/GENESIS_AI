/**
 * @genesis/ui — Public API
 *
 * Modular design system for the GENESIS AI platform.
 *
 * Structure:
 *   primitives/ — base UI atoms (button, badge, card, input, spinner, code, avatar)
 *   feedback/   — feedback patterns (alert, progress)
 *   genesis/    — platform-specific composed components
 *
 * Usage:
 *   import { Button, Card, StatusBadge } from '@genesis/ui';
 */

// ── Lib ───────────────────────────────────────────────────────────────────────
export { cx } from './lib/utils';

// ── Primitives ────────────────────────────────────────────────────────────────
export { Button } from './primitives/button/Button';
export type { ButtonProps, ButtonVariant, ButtonSize } from './primitives/button/Button';

export { Badge } from './primitives/badge/Badge';
export type { BadgeProps, BadgeVariant } from './primitives/badge/Badge';

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from './primitives/card/Card';
export type { CardProps, CardPadding } from './primitives/card/Card';

export { Spinner } from './primitives/spinner/Spinner';
export type { SpinnerProps, SpinnerSize } from './primitives/spinner/Spinner';

export { Code } from './primitives/code/Code';
export type { CodeProps } from './primitives/code/Code';

export { Input } from './primitives/input/Input';
export type { InputProps } from './primitives/input/Input';

export { Avatar } from './primitives/avatar/Avatar';
export type { AvatarProps, AvatarSize } from './primitives/avatar/Avatar';

// ── Feedback ──────────────────────────────────────────────────────────────────
export { Alert } from './feedback/alert/Alert';
export type { AlertProps, AlertVariant } from './feedback/alert/Alert';

export { Progress } from './feedback/progress/Progress';
export type { ProgressProps, ProgressSize } from './feedback/progress/Progress';

// ── Genesis platform components ───────────────────────────────────────────────
export { StatusBadge } from './genesis/status-badge/StatusBadge';
export type { StatusBadgeProps, PlatformStatus } from './genesis/status-badge/StatusBadge';

export { ProgressSteps } from './genesis/progress-steps/ProgressSteps';
export type { ProgressStepsProps, Step, StepState } from './genesis/progress-steps/ProgressSteps';

export { ErrorPanel } from './genesis/error-panel/ErrorPanel';
export type { ErrorPanelProps } from './genesis/error-panel/ErrorPanel';
