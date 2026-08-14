'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Alert, Spinner } from '@genesis/ui';
import { fetchClientApi, ApiError } from '../../lib/api';
import styles from './new-project-modal.module.css';

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultWorkspaceId: string | null;
}

export function NewProjectModal({ isOpen, onClose, defaultWorkspaceId }: NewProjectModalProps) {
  const router = useRouter();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'form' | 'creating'>('form');
  const nameRef = useRef<HTMLInputElement>(null);

  // Focus the name input when modal opens
  useEffect(() => {
    if (isOpen) {
      setName('');
      setDescription('');
      setError('');
      setStep('form');
      setTimeout(() => nameRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Close on Escape key
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !loading) onClose();
    };
    if (isOpen) document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [isOpen, loading, onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Project name is required');
      return;
    }

    setError('');
    setLoading(true);
    setStep('creating');

    try {
      let workspaceId = defaultWorkspaceId;

      // If no workspace exists, create one
      if (!workspaceId) {
        const ws = (await fetchClientApi('/workspaces', {
          method: 'POST',
          body: JSON.stringify({ name: 'My Workspace' }),
        })) as { id: string };
        workspaceId = ws.id;
      }

      // Create the project
      const project = (await fetchClientApi('/projects/', {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim() || null,
          workspace_id: workspaceId,
        }),
      })) as { id: string };

      // Redirect to workspace
      router.push(`/projects/${project.id}`);
    } catch (err) {
      setStep('form');
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to create project. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && !loading && onClose()}>
      <div className={styles.modal} role="dialog" aria-modal="true" aria-labelledby="modal-title">

        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerIcon}>⬡</div>
          <div>
            <h2 id="modal-title" className={styles.title}>New Project</h2>
            <p className={styles.subtitle}>Tell GENESIS AI what you want to build</p>
          </div>
          {!loading && (
            <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
              ✕
            </button>
          )}
        </div>

        {/* Creating state */}
        {step === 'creating' ? (
          <div className={styles.creatingState}>
            <Spinner size="lg" />
            <p className={styles.creatingTitle}>Setting up your workspace...</p>
            <p className={styles.creatingSubtitle}>This only takes a moment</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className={styles.form}>
            {error && (
              <Alert variant="error" className={styles.alert}>
                {error}
              </Alert>
            )}

            <div className={styles.field}>
              <label htmlFor="project-name" className={styles.label}>
                Project Name <span className={styles.required}>*</span>
              </label>
              <input
                ref={nameRef}
                id="project-name"
                type="text"
                className={styles.input}
                placeholder="e.g. Portfolio website, Task manager, E-commerce app..."
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={80}
                required
              />
            </div>

            <div className={styles.field}>
              <label htmlFor="project-desc" className={styles.label}>
                Brief Description <span className={styles.optional}>(optional)</span>
              </label>
              <textarea
                id="project-desc"
                className={styles.textarea}
                placeholder="What does this project do? Who is it for?"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                maxLength={300}
              />
            </div>

            <div className={styles.actions}>
              <button type="button" className={styles.cancelBtn} onClick={onClose}>
                Cancel
              </button>
              <Button type="submit" variant="primary" loading={loading} disabled={!name.trim()}>
                Create Project →
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
