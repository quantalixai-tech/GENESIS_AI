/**
 * Joins CSS class names, filtering out any falsy values.
 * Zero external dependencies — pure TypeScript implementation.
 *
 * @example
 *   cx(styles.base, isActive && styles.active, props.className)
 */
export function cx(
  ...classes: Array<string | undefined | null | false | 0>
): string {
  return classes.filter(Boolean).join(' ');
}
