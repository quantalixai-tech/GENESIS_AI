/**
 * CSS Modules type declaration.
 * Tells TypeScript that any `*.module.css` import is an object
 * whose keys are class name strings.
 */
declare module '*.module.css' {
  const styles: { readonly [className: string]: string };
  export default styles;
}
