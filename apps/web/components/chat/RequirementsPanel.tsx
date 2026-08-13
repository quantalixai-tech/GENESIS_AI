'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle } from '@genesis/ui';
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

export function RequirementsPanel({ projectId }: { projectId: string }) {
  const [requirements, setRequirements] = useState<Requirement[]>([]);

  const loadRequirements = async () => {
    try {
      const data = await fetchClientApi(`/projects/${projectId}/requirements`);
      setRequirements(data as Requirement[]);
    } catch (err) {
      console.error('Failed to load requirements', err);
    }
  };

  // Poll for requirements every 5 seconds since the AI might extract them asynchronously
  useEffect(() => {
    loadRequirements();
    const interval = setInterval(loadRequirements, 5000);
    return () => clearInterval(interval);
  }, [projectId]);

  return (
    <div className={styles.requirementsPanel}>
      <h3 className={styles.panelTitle}>Extracted Requirements</h3>
      
      {requirements.length === 0 ? (
        <p className={styles.emptyRequirements}>No requirements extracted yet. Describe your app to the AI.</p>
      ) : (
        <div className={styles.requirementsList}>
          {requirements.map(req => (
            <Card key={req.id} className={styles.reqCard}>
              <CardHeader className={styles.reqHeader}>
                <CardTitle className={styles.reqTitle}>{req.title}</CardTitle>
              </CardHeader>
              <div className={styles.reqBody}>
                <p>{req.description}</p>
                <div className={styles.reqMeta}>
                  <span className={styles.badge}>{req.category}</span>
                  <span className={`${styles.badge} ${styles['badge' + req.priority]}`}>{req.priority}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
