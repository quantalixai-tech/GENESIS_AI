import { HTMLAttributes, AnchorHTMLAttributes, ReactNode } from 'react';
import styles from './card.module.css';

interface CardBaseProps {
  className?: string;
  /** Hover effect — adds border highlight and slight lift. */
  interactive?: boolean;
  padding?: 'sm' | 'md' | 'lg' | 'none';
}

interface CardAsDivProps extends CardBaseProps, HTMLAttributes<HTMLDivElement> {
  href?: never;
}

interface CardAsAnchorProps extends CardBaseProps, AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
}

type CardProps = CardAsDivProps | CardAsAnchorProps;

const getPaddingClass = (padding: string) => {
  switch (padding) {
    case 'none': return styles.paddingNone;
    case 'sm': return styles.paddingSm;
    case 'md': return styles.paddingMd;
    case 'lg': return styles.paddingLg;
    default: return styles.paddingMd;
  }
};

export function Card({
  children,
  className = '',
  href,
  interactive = false,
  padding = 'md',
  ...rest
}: CardProps): React.JSX.Element {
  const baseClasses = styles.base;
  const paddingClass = getPaddingClass(padding);
  const interactiveClasses = interactive || href ? styles.interactive : '';
  const combinedClasses = `${baseClasses} ${paddingClass} ${interactiveClasses} ${className}`.trim();

  if (href) {
    return (
      <a
        href={href}
        className={combinedClasses}
        rel="noopener noreferrer"
        {...(rest as AnchorHTMLAttributes<HTMLAnchorElement>)}
      >
        {children}
      </a>
    );
  }

  return (
    <div className={combinedClasses} {...(rest as HTMLAttributes<HTMLDivElement>)}>
      {children}
    </div>
  );
}
