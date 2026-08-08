import { CSSProperties, ReactNode } from 'react';

interface CodeProps {
  children: ReactNode;
  className?: string;
  /** Render as a block code element instead of inline. */
  block?: boolean;
}

const inlineStyle: CSSProperties = {
  fontFamily: 'var(--font-mono, "Courier New", monospace)',
  fontSize: '0.875em',
  background: 'rgba(99, 102, 241, 0.08)',
  color: '#818cf8',
  padding: '0.1em 0.4em',
  borderRadius: '4px',
  border: '1px solid rgba(99, 102, 241, 0.15)',
};

const blockStyle: CSSProperties = {
  ...inlineStyle,
  display: 'block',
  padding: '1rem 1.25rem',
  borderRadius: '8px',
  fontSize: '0.875rem',
  lineHeight: 1.6,
  overflowX: 'auto',
  whiteSpace: 'pre',
};

export function Code({ children, className, block = false }: CodeProps): React.JSX.Element {
  if (block) {
    return (
      <pre className={className} style={blockStyle}>
        <code>{children}</code>
      </pre>
    );
  }
  return (
    <code className={className} style={inlineStyle}>
      {children}
    </code>
  );
}
