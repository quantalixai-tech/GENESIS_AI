import { useState, useCallback } from 'react';
import { fetchClientApi } from '../api';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at?: string;
  isStreaming?: boolean;
}

export function useChat(projectId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch existing messages for a given conversation
  const loadMessages = useCallback(async (convId: string) => {
    try {
      const data = await fetchClientApi(`/projects/${projectId}/conversations/${convId}/messages`);
      setMessages(data as Message[]);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  }, [projectId]);

  const sendMessage = useCallback(async (content: string, convId: string) => {
    // Optimistically add the user message
    const tempUserMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, tempUserMsg]);
    setIsTyping(true);
    setError(null);

    try {
      // 1. Send the message to the DB
      await fetchClientApi(`/projects/${projectId}/conversations/${convId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content }),
      });

      // 2. Stream the AI response
      // fetchClientApi wraps standard fetch to proxy the request and add cookies.
      // We need to use native fetch against the proxy manually for SSE, as fetchClientApi parses JSON.
      const encodedMsg = encodeURIComponent(content);
      const sseUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1'}/projects/${projectId}/conversations/${convId}/stream?message=${encodedMsg}`;
      
      const eventSource = new EventSource(sseUrl, { withCredentials: true });
      
      const tempAiMsgId = crypto.randomUUID();
      setMessages(prev => [...prev, { id: tempAiMsgId, role: 'assistant', content: '', isStreaming: true }]);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'token') {
            setMessages(prev => prev.map(msg => 
              msg.id === tempAiMsgId 
                ? { ...msg, content: msg.content + data.content } 
                : msg
            ));
          } else if (data.type === 'done') {
            setMessages(prev => prev.map(msg => 
              msg.id === tempAiMsgId ? { ...msg, isStreaming: false } : msg
            ));
            setIsTyping(false);
            eventSource.close();
          } else if (data.type === 'error') {
            setError(data.message || 'Error generating response');
            setIsTyping(false);
            setMessages(prev => prev.map(msg => 
              msg.id === tempAiMsgId ? { ...msg, isStreaming: false } : msg
            ));
            eventSource.close();
          }
        } catch (e) {
          console.error('SSE Parse Error:', e);
        }
      };

      eventSource.onerror = (err) => {
        console.error('EventSource Error:', err);
        setError('Connection lost while generating response.');
        setIsTyping(false);
        setMessages(prev => prev.map(msg => 
          msg.id === tempAiMsgId ? { ...msg, isStreaming: false } : msg
        ));
        eventSource.close();
      };

    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
      setIsTyping(false);
    }
  }, [projectId]);

  return {
    messages,
    isTyping,
    error,
    sendMessage,
    loadMessages,
    setMessages
  };
}
