import { fetchServerApi, ApiError } from '../../../lib/api';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import styles from './layout.module.css';
import React from 'react';

export const dynamic = 'force-dynamic';

interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  workspace_id: string;
  created_at: string;
  updated_at: string;
}

export default async function ProjectLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let project: ProjectResponse | null = null;

  try {
    const projects = (await fetchServerApi(`/projects/`)) as ProjectResponse[];
    project = projects.find((p) => p.id === id) || null;
    
    if (!project) {
      redirect('/dashboard');
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect('/auth/login');
    }
    console.error('Project fetch error:', error);
    redirect('/dashboard');
  }

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <Link href="/dashboard" className={styles.backLink}>
            ← Back
          </Link>
          <div className={styles.projectContext}>
            <span className={styles.projectName}>{project.name}</span>
            <span className={styles.projectDesc}>{project.description || 'AI Project'}</span>
          </div>
        </div>
        <nav className={styles.nav}>
          <Link href={`/projects/${project.id}`} className={`${styles.navItem} ${styles.navItemActive}`}>
            Chat & Requirements
          </Link>
          <Link href={`/projects/${project.id}/architecture`} className={styles.navItem}>
            Architecture
          </Link>
          <Link href={`/projects/${project.id}/code`} className={styles.navItem}>
            Codebase
          </Link>
        </nav>
      </aside>

      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}
