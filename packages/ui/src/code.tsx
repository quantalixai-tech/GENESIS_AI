import { ReactNode } from 'react';
import styles from './code.module.css';

interface CodeProps {
  children: ReactNode;
  className?: string;
  /** Render as a block code element instead of inline. */
  block?: boolean;
}

export function Code({ children, className = '', block = false }: CodeProps): React.JSX.Element {
  if (block) {
    const combinedClasses = `${styles.block} ${className}`.trim();
    return (
      <pre className={combinedClasses}>
        <code>{children}</code>
      </pre>
    );
  }
  
  const combinedClasses = `${styles.inline} ${className}`.trim();
  return (
    <code className={combinedClasses}>
      {children}
    </code>
  );
}
