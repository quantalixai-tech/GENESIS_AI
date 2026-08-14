'use client';

import React, { useEffect, useState } from 'react';
import styles from './chat.module.css';
import { fetchClientApi } from '../../lib/api';

interface Requirement {
  id: string;
  requirement_key: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: string;
}

const PRIORITY_CLASS: Record<string, string> = {
  high: styles.badgeHigh ?? '',
  medium: styles.badgeMedium ?? '',
  low: styles.badgeLow ?? '',
};

export function RequirementsPanel({ projectId }: { projectId: string }) {
  const [requirements, setRequirements] = useState<Requirement[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchClientApi(`/projects/${projectId}/requirements`);
        setRequirements(data as Requirement[]);
      } catch {
        // silently ignore — requirements accumulate gradually
      }
    };

    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [projectId]);

  return (
    <div className={styles.requirementsPanel}>
      {requirements.length === 0 ? (
        <div className={styles.emptyRequirements}>
          <div className={styles.emptyReqIcon}>📋</div>
          <p className={styles.emptyReqText}>
            Requirements will appear here as you describe your app to GENESIS AI.
          </p>
        </div>
      ) : (
        <div className={styles.requirementsList}>
          {requirements.map((req) => (
            <div key={req.id} className={styles.reqCard}>
              <div className={styles.reqHeader}>
                <span className={styles.reqTitle}>{req.title}</span>
                <span className={styles.reqStatusDot} title="Confirmed" />
              </div>
              {req.description && (
                <p className={styles.reqDesc}>{req.description}</p>
              )}
              <div className={styles.reqMeta}>
                <span className={`${styles.badge} ${styles.badgeCategory}`}>
                  {req.category}
                </span>
                <span className={`${styles.badge} ${PRIORITY_CLASS[req.priority.toLowerCase()] ?? styles.badgeLow}`}>
                  {req.priority}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
