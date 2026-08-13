/**
 * @genesis/ui — Card
 *
 * Polymorphic surface component. Renders as <div> or <a> depending on `href`.
 * Composed via sub-components: Card, CardHeader, CardTitle,
 * CardDescription, CardContent, CardFooter.
 */
import React, {
  type HTMLAttributes,
  type AnchorHTMLAttributes,
  type ReactNode,
} from 'react';
import { cx } from '../../lib/utils';
import styles from './card.module.css';

// ── Types ────────────────────────────────────────────────────────────────────

export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

interface CardBaseProps {
  className?: string;
  /** Enable hover lift + border highlight. */
  interactive?: boolean;
  padding?: CardPadding;
  children?: ReactNode;
}

interface CardAsDivProps
  extends CardBaseProps,
    HTMLAttributes<HTMLDivElement> {
  href?: never;
}

interface CardAsAnchorProps
  extends CardBaseProps,
    AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
}

export type CardProps = CardAsDivProps | CardAsAnchorProps;

// ── Root ─────────────────────────────────────────────────────────────────────

export function Card({
  children,
  className,
  href,
  interactive = false,
  padding = 'md',
  ...rest
}: CardProps): React.JSX.Element {
  const classes = cx(
    styles.base,
    styles[`padding-${padding}`],
    (interactive || href !== undefined) && styles.interactive,
    className,
  );

  if (href !== undefined) {
    return (
      <a
        href={href}
        className={classes}
        rel="noopener noreferrer"
        {...(rest as AnchorHTMLAttributes<HTMLAnchorElement>)}
      >
        {children}
      </a>
    );
  }

  return (
    <div className={classes} {...(rest as HTMLAttributes<HTMLDivElement>)}>
      {children}
    </div>
  );
}

// ── Sub-components ───────────────────────────────────────────────────────────

export function CardHeader({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLDivElement>): React.JSX.Element {
  return (
    <div className={cx(styles.header, className)} {...rest}>
      {children}
    </div>
  );
}

export function CardTitle({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLHeadingElement>): React.JSX.Element {
  return (
    <h3 className={cx(styles.title, className)} {...rest}>
      {children}
    </h3>
  );
}

export function CardDescription({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLParagraphElement>): React.JSX.Element {
  return (
    <p className={cx(styles.description, className)} {...rest}>
      {children}
    </p>
  );
}

export function CardContent({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLDivElement>): React.JSX.Element {
  return (
    <div className={cx(styles.content, className)} {...rest}>
      {children}
    </div>
  );
}

export function CardFooter({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLDivElement>): React.JSX.Element {
  return (
    <div className={cx(styles.footer, className)} {...rest}>
      {children}
    </div>
  );
}
