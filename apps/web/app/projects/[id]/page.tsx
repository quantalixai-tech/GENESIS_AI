import React from 'react';
import { ChatWindow } from '../../../components/chat/ChatWindow';
import { RequirementsPanel } from '../../../components/chat/RequirementsPanel';

export const dynamic = 'force-dynamic';

export default async function ProjectChatPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div style={{ display: 'flex', height: '100%', width: '100%' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <ChatWindow projectId={id} />
      </div>
      <RequirementsPanel projectId={id} />
    </div>
  );
}
