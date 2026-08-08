import { CSSProperties, ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  /** Renders the card as an anchor tag. */
  href?: string;
  /** Hover effect — adds border highlight and slight lift. */
  interactive?: boolean;
  padding?: 'sm' | 'md' | 'lg' | 'none';
}

const paddingMap = {
  none: '0',
  sm: '1rem',
  md: '1.5rem',
  lg: '2rem',
};

const baseStyle: CSSProperties = {
  background: '#16161f',
  border: '1px solid rgba(255, 255, 255, 0.08)',
  borderRadius: '12px',
  display: 'block',
  textDecoration: 'none',
  color: 'inherit',
  transition: 'border-color 0.2s ease, transform 0.2s ease',
};

export function Card({
  children,
  className,
  style,
  href,
  interactive = false,
  padding = 'md',
}: CardProps): React.JSX.Element {
  const cardStyle: CSSProperties = {
    ...baseStyle,
    padding: paddingMap[padding],
    cursor: href || interactive ? 'pointer' : undefined,
    ...style,
  };

  if (href) {
    return (
      <a
        href={href}
        className={className}
        style={cardStyle}
        rel="noopener noreferrer"
      >
        {children}
      </a>
    );
  }

  return (
    <div className={className} style={cardStyle}>
      {children}
    </div>
  );
}
