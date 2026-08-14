import React from 'react';
import { ChatWindow } from '../../../components/chat/ChatWindow';
import { RequirementsPanel } from '../../../components/chat/RequirementsPanel';
import { LivePreview } from '../../../components/preview/LivePreview';
import styles from './workspace.module.css';

export const dynamic = 'force-dynamic';

export default async function ProjectChatPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className={styles.workspace}>
      {/* ── Left: Chat ─────────────────────────── */}
      <div className={styles.chatPanel}>
        <div className={styles.panelHeader}>
          <span className={styles.panelLabel}>Conversation</span>
        </div>
        <div className={styles.panelFill}>
          <ChatWindow projectId={id} />
        </div>
      </div>

      {/* ── Center: Live Preview ────────────────── */}
      <div className={styles.previewPanel}>
        <div className={styles.panelFill}>
          <LivePreview projectId={id} />
        </div>
      </div>

      {/* ── Right: Requirements ─────────────────── */}
      <div className={styles.requirementsPanel}>
        <div className={styles.panelHeader}>
          <span className={styles.panelLabel}>Requirements</span>
        </div>
        <div className={styles.panelFill}>
          <RequirementsPanel projectId={id} />
        </div>
      </div>
    </div>
  );
}
