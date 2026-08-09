#!/usr/bin/env node
/**
 * Genesis CLI — Main Entry Point
 *
 * Commands:
 *   genesis setup              — First-time environment setup
 *   genesis start              — Start core infrastructure (postgres, nats, minio)
 *   genesis start --platform   — Start full platform (+ API, worker, web)
 *   genesis start --build      — Rebuild images before starting
 *   genesis stop               — Stop services
 *   genesis stop --platform    — Stop platform services too
 *   genesis stop --volumes     — Remove volumes (DESTRUCTIVE)
 *   genesis dev                — Start API + web in dev mode (hot-reload)
 *   genesis dev --api          — Start API only in dev mode
 *   genesis dev --web          — Start web only in dev mode
 *   genesis status             — Show service health table
 *   genesis status --platform  — Include platform services
 *   genesis logs [service]     — Tail service logs
 *   genesis logs -f            — Follow logs
 *   genesis migrate            — Apply database migrations
 *   genesis migrate --check    — Check for pending migrations
 *   genesis migrate --history  — Show migration history
 *   genesis migrate --rollback — Roll back one migration
 *   genesis doctor             — Run platform health checks
 */

import { Command } from 'commander';
import { printBanner, c } from './lib/output.js';
import { registerSetupCommand } from './commands/setup.js';
import { registerStartCommand } from './commands/start.js';
import { registerStopCommand } from './commands/stop.js';
import { registerDevCommand } from './commands/dev.js';
import { registerStatusCommand } from './commands/status.js';
import { registerLogsCommand } from './commands/logs.js';
import { registerMigrateCommand } from './commands/migrate.js';
import { registerDoctorCommand } from './commands/doctor.js';
import { registerConfigCommand } from './commands/config.js';

const program = new Command();

program
  .name('genesis')
  .description('Genesis AI Platform CLI')
  .version('0.4.0', '-v, --version', 'Show version')
  .addHelpText('beforeAll', '')
  .addHelpText('afterAll', `
  ${c.muted('Quick start:')}
    ${c.info('genesis setup')}                  ${c.muted('Create .env and generate JWT_SECRET')}
    ${c.info('genesis start')}                  ${c.muted('Start core infra (postgres, nats, minio)')}
    ${c.info('genesis migrate')}                ${c.muted('Apply database migrations')}
    ${c.info('genesis dev')}                    ${c.muted('Start API + web with hot-reload')}

  ${c.muted('Production:')}
    ${c.info('genesis start --platform --build')} ${c.muted('Build and start full stack')}

  ${c.muted('Docs:')} https://github.com/quantalixai/GENESIS_AI
  `);

// Register all commands first (so outputHelp shows them)
registerSetupCommand(program);
registerStartCommand(program);
registerStopCommand(program);
registerDevCommand(program);
registerStatusCommand(program);
registerLogsCommand(program);
registerMigrateCommand(program);
registerDoctorCommand(program);
registerConfigCommand(program);

// Show banner + help when run with no args, then exit 0
const noArgs = process.argv.length === 2;
if (noArgs) {
  printBanner();
  program.outputHelp();
  process.exit(0);
}

program.parse(process.argv);
