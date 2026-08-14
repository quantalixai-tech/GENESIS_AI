'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Spinner } from '@genesis/ui';
import { fetchClientApi } from '../../lib/api';
import styles from './preview.module.css';

interface LivePreviewProps {
  projectId: string;
}

interface PreviewStatus {
  status: string;
  port: number | null;
  container_id: string | null;
}

type Device = 'desktop' | 'tablet' | 'mobile';

const DEVICE_ICONS: Record<Device, string> = {
  desktop: '🖥',
  tablet: '⬜',
  mobile: '📱',
};

export function LivePreview({ projectId }: LivePreviewProps) {
  const [status, setStatus] = useState<PreviewStatus>({
    status: 'stopped',
    port: null,
    container_id: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [device, setDevice] = useState<Device>('desktop');

  const fetchStatus = useCallback(async () => {
    try {
      const data = (await fetchClientApi(
        `/projects/${projectId}/preview/status`,
      )) as PreviewStatus;
      setStatus(data);
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch preview status';
      setError(msg);
    }
  }, [projectId]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = (await fetchClientApi(
        `/projects/${projectId}/preview/start`,
        { method: 'POST' },
      )) as PreviewStatus;
      setStatus(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start preview');
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await fetchClientApi(`/projects/${projectId}/preview/stop`, { method: 'POST' });
      await fetchStatus();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to stop preview');
    } finally {
      setLoading(false);
    }
  };

  const isRunning = status.status === 'running';
  const previewUrl = status.port ? `http://localhost:${status.port}` : null;

  return (
    <div className={styles.previewContainer}>
      {/* ── Header ─────────────────────────────────────── */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.panelLabel}>Live Preview</span>
          <span className={`${styles.statusBadge} ${isRunning ? styles.statusRunning : styles.statusStopped}`}>
            {status.status}
          </span>
        </div>

        {/* Device toggle */}
        <div className={styles.deviceToggle}>
          {(['desktop', 'tablet', 'mobile'] as Device[]).map((d) => (
            <button
              key={d}
              className={`${styles.deviceBtn} ${device === d ? styles.deviceBtnActive : ''}`}
              onClick={() => setDevice(d)}
              title={d.charAt(0).toUpperCase() + d.slice(1)}
              aria-pressed={device === d}
            >
              {DEVICE_ICONS[d]}
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className={styles.headerActions}>
          {isRunning ? (
            <>
              <button
                className={styles.iconBtn}
                onClick={fetchStatus}
                title="Refresh"
                aria-label="Refresh preview"
              >
                ↻
              </button>
              {previewUrl && (
                <a
                  className={styles.iconBtn}
                  href={previewUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  title="Open in new tab"
                  aria-label="Open preview in new tab"
                >
                  ↗
                </a>
              )}
              <button
                className={`${styles.iconBtn} ${styles.iconBtnDanger}`}
                onClick={handleStop}
                disabled={loading}
                title="Stop Preview"
                aria-label="Stop preview"
              >
                ■
              </button>
            </>
          ) : null}
        </div>
      </div>

      {/* ── Content ────────────────────────────────────── */}
      <div className={styles.previewContent}>
        {error ? (
          <div className={styles.errorState}>
            <div className={styles.errorIcon}>⚠</div>
            <p className={styles.errorText}>{error}</p>
            <button className={styles.retryBtn} onClick={fetchStatus}>
              Try again
            </button>
          </div>
        ) : loading ? (
          <div className={styles.loadingState}>
            <Spinner size="lg" />
            <p className={styles.loadingText}>Starting sandbox…</p>
          </div>
        ) : isRunning && previewUrl ? (
          <div className={styles.deviceFrame} data-device={device}>
            <iframe
              src={previewUrl}
              title="Live Application Preview"
              className={styles.iframe}
            />
          </div>
        ) : (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>⬡</div>
            <p className={styles.emptyTitle}>Preview not running</p>
            <p className={styles.emptySubtitle}>
              Start the preview to see your application live as it&apos;s being built.
            </p>
            <button className={styles.startBtn} onClick={handleStart}>
              ▶ Start Preview
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
