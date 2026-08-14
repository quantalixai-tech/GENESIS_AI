import React from 'react';
import styles from './chat.module.css';
import ReactMarkdown from 'react-markdown';
import { type Message } from '../../lib/hooks/use-chat';

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`${styles.messageWrapper} ${isUser ? styles.messageUser : styles.messageAssistant}`}
    >
      {/* AI avatar */}
      {!isUser && (
        <div className={styles.avatarWrap}>
          <div className={styles.avatarAi} title="Genesis AI">
            ⬡
          </div>
        </div>
      )}

      {/* Bubble */}
      <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleAssistant}`}>
        {isUser ? (
          <p className={styles.messageText}>{message.content}</p>
        ) : (
          <div className={styles.markdownContent}>
            {message.content ? (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            ) : message.isStreaming ? (
              <span className={styles.cursor} aria-label="Generating…" />
            ) : null}
          </div>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className={styles.avatarWrap}>
          <div className={styles.avatarUser} title="You">
            U
          </div>
        </div>
      )}
    </div>
  );
}
