'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Button, Input, Spinner } from '@genesis/ui';
import styles from './chat.module.css';
import { useChat } from '../../lib/hooks/use-chat';
import { MessageBubble } from './MessageBubble';

interface ChatWindowProps {
  projectId: string;
  initialConversationId?: string | null;
}

export function ChatWindow({ projectId, initialConversationId }: ChatWindowProps) {
  const { messages, isTyping, error, sendMessage, loadMessages, setMessages } = useChat(projectId, initialConversationId || null);
  const [inputValue, setInputValue] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  
  // We need a local state for the active conversation id, in case we just created one
  const [activeConvId, setActiveConvId] = useState<string | null>(initialConversationId || null);

  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    }
  }, [activeConvId, loadMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isTyping) return;

    const content = inputValue.trim();
    setInputValue('');

    let currentConvId = activeConvId;

    // If no conversation exists, we must create one first
    if (!currentConvId) {
      try {
        const res = await fetch(`/api/proxy/projects/${projectId}/conversations`, {
          method: 'POST'
        });
        const conv = await res.json();
        currentConvId = conv.id;
        setActiveConvId(currentConvId);
      } catch (err) {
        console.error('Failed to create conversation', err);
        return;
      }
    }

    if (currentConvId) {
      await sendMessage(content, currentConvId);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messageList}>
        {messages.length === 0 && !isTyping && (
          <div className={styles.emptyState}>
            <h2>Start a new conversation</h2>
            <p>Describe what you want to build...</p>
          </div>
        )}
        
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        
        {isTyping && messages.length > 0 && !messages[messages.length - 1]?.isStreaming && (
          <div className={styles.typingIndicator}>
            <Spinner size="sm" /> <span>Genesis AI is thinking...</span>
          </div>
        )}
        
        {error && (
          <div className={styles.errorMessage}>
            {error}
          </div>
        )}
        
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className={styles.inputForm}>
        <Input 
          label="Message"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          placeholder="Describe your application..."
          disabled={isTyping}
          className={styles.inputField}
        />
        <Button type="submit" disabled={!inputValue.trim() || isTyping} variant="primary">
          Send
        </Button>
      </form>
    </div>
  );
}
