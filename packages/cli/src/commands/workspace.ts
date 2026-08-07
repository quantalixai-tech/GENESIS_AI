/**
 * genesis workspace
 *
 * Manage Genesis workspaces from the CLI.
 *
 * Sub-commands (Phase 0.4+):
 *   genesis workspace list         — List all workspaces
 *   genesis workspace create <name> — Create a new workspace
 *   genesis workspace open <name>   — Open a workspace
 *   genesis workspace delete <name> — Delete a workspace
 *   genesis workspace export <name> — Export workspace to archive
 *   genesis workspace import <path> — Import workspace from archive
 *
 * Workspaces are the top-level organizational unit in Genesis.
 * Each workspace contains multiple projects.
 */

// TODO(phase-0.4): Implement workspace command
export const workspaceCommand = {
  name: 'workspace',
  description: 'Manage Genesis workspaces',
  handler: async () => {
    throw new Error('Not implemented — Phase 0.4');
  },
};
