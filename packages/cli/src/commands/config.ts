/**
 * genesis config — View/edit platform configuration
 *
 * Phase 1.0: Implement interactive config editor.
 * For now: print current configuration values from .env.
 */

import type { Command } from 'commander';
import { existsSync, readFileSync } from 'node:fs';
import { logStep, logInfo, logWarn, c } from '../lib/output.js';
import { ENV_FILE } from '../lib/compose.js';

export function registerConfigCommand(program: Command): void {
  program
    .command('config')
    .description('View platform configuration')
    .action(async () => {
      logStep('Platform Configuration');

      if (!existsSync(ENV_FILE)) {
        logWarn('.env not found. Run genesis setup first.');
        return;
      }

      const raw = readFileSync(ENV_FILE, 'utf-8');
      console.log('');

      for (const line of raw.split('\n')) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) {
          console.log(c.muted('  ' + line));
          continue;
        }
        if (!trimmed.includes('=')) { console.log('  ' + line); continue; }
        const idx = trimmed.indexOf('=');
        const key = trimmed.slice(0, idx).trim();
        const val = trimmed.slice(idx + 1).trim();
        // Redact secrets
        const isSecret = /secret|password|key|token/i.test(key);
        const display = isSecret && val ? '***' : val;
        logInfo(`${key.padEnd(32)} ${c.muted(display)}`);
      }

      console.log('');
    });
}
