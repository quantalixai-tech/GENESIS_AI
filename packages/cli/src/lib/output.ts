/**
 * Genesis CLI — Terminal Output Library
 *
 * Provides consistent, beautiful terminal output across all CLI commands.
 * Uses chalk for colors and a simple table renderer.
 */

import chalk from 'chalk';

// =============================================================================
// ANSI / chalk theme
// =============================================================================

export const c = {
  brand: chalk.hex('#6366f1').bold,
  ok: chalk.hex('#10b981'),
  warn: chalk.hex('#f59e0b'),
  err: chalk.hex('#ef4444'),
  info: chalk.hex('#818cf8'),
  muted: chalk.gray,
  bold: chalk.bold,
  dim: chalk.dim,
};

// =============================================================================
// ASCII Banner
// =============================================================================

export function printBanner(): void {
  console.log('');
  console.log(c.brand('  ╔══════════════════════════════════════╗'));
  console.log(c.brand('  ║') + chalk.white.bold('        GENESIS AI  CLI  v0.4         ') + c.brand('║'));
  console.log(c.brand('  ║') + c.muted('   AI-Driven Software Development       ') + c.brand('║'));
  console.log(c.brand('  ╚══════════════════════════════════════╝'));
  console.log('');
}

// =============================================================================
// Log helpers
// =============================================================================

export function logOk(msg: string): void {
  console.log(`  ${c.ok('✓')} ${msg}`);
}

export function logWarn(msg: string): void {
  console.log(`  ${c.warn('⚠')} ${msg}`);
}

export function logErr(msg: string): void {
  console.log(`  ${c.err('✗')} ${msg}`);
}

export function logInfo(msg: string): void {
  console.log(`  ${c.info('→')} ${msg}`);
}

export function logStep(msg: string): void {
  console.log('');
  console.log(`${c.brand('▶')} ${chalk.bold(msg)}`);
}

export function logDim(msg: string): void {
  console.log(`  ${c.dim(msg)}`);
}

// =============================================================================
// Service status table
// =============================================================================

export interface ServiceRow {
  name: string;
  status: 'running' | 'healthy' | 'unhealthy' | 'stopped' | 'starting' | 'unknown';
  image: string;
  ports: string;
  note?: string;
}

function statusBadge(s: ServiceRow['status']): string {
  switch (s) {
    case 'healthy':
    case 'running':
      return c.ok('● healthy');
    case 'unhealthy':
      return c.err('● unhealthy');
    case 'stopped':
      return c.muted('○ stopped');
    case 'starting':
      return c.warn('◌ starting');
    default:
      return c.dim('? unknown');
  }
}

export function printServiceTable(rows: ServiceRow[]): void {
  const nameWidth = Math.max(12, ...rows.map((r) => r.name.length)) + 2;
  const statusWidth = 14;
  const portsWidth = Math.max(8, ...rows.map((r) => r.ports.length)) + 2;

  const header =
    chalk.bold('  ' + 'SERVICE'.padEnd(nameWidth)) +
    chalk.bold('STATUS'.padEnd(statusWidth)) +
    chalk.bold('PORTS'.padEnd(portsWidth)) +
    chalk.bold('IMAGE');

  console.log('');
  console.log(header);
  console.log('  ' + c.muted('─'.repeat(nameWidth + statusWidth + portsWidth + 30)));

  for (const row of rows) {
    const name = c.info(row.name.padEnd(nameWidth));
    const status = statusBadge(row.status).padEnd(statusWidth + 10); // badge has color codes
    const ports = c.dim(row.ports.padEnd(portsWidth));
    const image = c.muted(row.image);
    console.log(`  ${name}${status}${ports}${image}`);
  }

  console.log('');
}

// =============================================================================
// Endpoint table
// =============================================================================

export interface Endpoint {
  label: string;
  url: string;
}

export function printEndpoints(endpoints: Endpoint[]): void {
  console.log('');
  console.log(chalk.bold('  Endpoints:'));
  for (const ep of endpoints) {
    console.log(`  ${c.muted(ep.label.padEnd(18))} ${c.info(ep.url)}`);
  }
  console.log('');
}
