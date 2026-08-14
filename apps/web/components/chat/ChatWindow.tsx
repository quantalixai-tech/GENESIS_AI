'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import styles from './chat.module.css';
import { useChat } from '../../lib/hooks/use-chat';
import { MessageBubble } from './MessageBubble';

interface ChatWindowProps {
  projectId: string;
  initialConversationId?: string | null;
}

const SUGGESTIONS = [
  '💼 I want to build a task management app',
  '🛍️ Create an e-commerce storefront',
  '📊 Build a data analytics dashboard',
];

export function ChatWindow({ projectId, initialConversationId }: ChatWindowProps) {
  const { messages, isTyping, error, sendMessage, loadMessages } = useChat(
    projectId,
    initialConversationId || null,
  );
  const [inputValue, setInputValue] = useState('');
  const [activeConvId, setActiveConvId] = useState<string | null>(
    initialConversationId || null,
  );
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (activeConvId) loadMessages(activeConvId);
  }, [activeConvId, loadMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Auto-resize textarea
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const submit = useCallback(async () => {
    const content = inputValue.trim();
    if (!content || isTyping) return;

    setInputValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    let currentConvId = activeConvId;

    if (!currentConvId) {
      try {
        const res = await fetch(`/api/proxy/projects/${projectId}/conversations`, {
          method: 'POST',
        });
        const conv = (await res.json()) as { id: string };
        currentConvId = conv.id;
        setActiveConvId(currentConvId);
      } catch {
        return;
      }
    }

    if (currentConvId) {
      await sendMessage(content, currentConvId);
    }
  }, [inputValue, isTyping, activeConvId, projectId, sendMessage]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void submit();
    }
  };

  const handleSuggestion = (text: string) => {
    setInputValue(text.replace(/^[^\s]+\s/, '')); // strip emoji prefix
    textareaRef.current?.focus();
  };

  return (
    <div className={styles.chatContainer}>
      {/* Message list */}
      <div className={styles.messageList}>
        {messages.length === 0 && !isTyping && (
          <div className={styles.emptyState}>
            <div className={styles.emptyLogo}>⬡</div>
            <h2 className={styles.emptyHeading}>What do you want to build?</h2>
            <p className={styles.emptyHint}>
              Describe your idea and GENESIS AI will turn it into a working application.
            </p>
            <div className={styles.emptySuggestions}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className={styles.suggestionBtn}
                  onClick={() => handleSuggestion(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isTyping && (
          <div className={styles.typingIndicator}>
            <div className={styles.typingDots}>
              <span className={styles.typingDot} />
              <span className={styles.typingDot} />
              <span className={styles.typingDot} />
            </div>
            <span className={styles.typingText}>Genesis AI is thinking…</span>
          </div>
        )}

        {error && <div className={styles.errorMessage}>{error}</div>}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className={styles.inputForm}>
        <div className={styles.inputRow}>
          <textarea
            ref={textareaRef}
            className={styles.inputTextarea}
            value={inputValue}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Describe your application… (Enter to send, Shift+Enter for newline)"
            rows={1}
            disabled={isTyping}
            aria-label="Chat message"
          />
          <button
            className={styles.sendBtn}
            onClick={() => void submit()}
            disabled={!inputValue.trim() || isTyping}
            aria-label="Send message"
          >
            <span className={styles.sendIcon}>↑</span>
          </button>
        </div>
        {isTyping && (
          <div className={styles.agentActivity}>
            <span className={styles.agentDot} />
            Requirement agent is processing…
          </div>
        )}
      </div>
    </div>
  );
}
