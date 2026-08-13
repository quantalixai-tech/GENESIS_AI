import React from 'react';
import { Avatar } from '@genesis/ui';
import styles from './chat.module.css';
import ReactMarkdown from 'react-markdown';
import { type Message } from '../../lib/hooks/use-chat';

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`${styles.messageWrapper} ${isUser ? styles.messageUser : styles.messageAssistant}`}>
      {!isUser && (
        <Avatar name="Genesis AI" className={styles.avatar} size="sm" />
      )}
      <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleAssistant}`}>
        {isUser ? (
          <p className={styles.messageText}>{message.content}</p>
        ) : (
          <div className={styles.markdownContent}>
            {message.content ? (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            ) : message.isStreaming ? (
              <span className={styles.cursor}></span>
            ) : null}
          </div>
        )}
      </div>
      {isUser && (
        <Avatar name="User" className={styles.avatar} size="sm" />
      )}
    </div>
  );
}
