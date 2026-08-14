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

const NAV_ITEMS = [
  { href: '', label: 'Chat & Build', icon: '💬' },
  { href: '/architecture', label: 'Architecture', icon: '🏗️' },
  { href: '/code', label: 'Codebase', icon: '⌨️' },
  { href: '/git', label: 'Git History', icon: '🔀' },
] as const;

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
    project = (await fetchServerApi(`/projects/${id}`)) as ProjectResponse;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect('/auth/login');
    }
    redirect('/dashboard');
  }

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        {/* Back link */}
        <div className={styles.brand}>
          <Link href="/dashboard" className={styles.backLink}>
            ← All Projects
          </Link>
        </div>

        {/* Project context */}
        <div className={styles.projectContext}>
          <div className={styles.projectIconWrap}>
            <span className={styles.projectIcon}>⬡</span>
          </div>
          <div className={styles.projectInfo}>
            <span className={styles.projectName}>{project.name}</span>
            <span className={styles.projectDesc}>
              {project.description || 'AI-powered project'}
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className={styles.nav} aria-label="Project navigation">
          {NAV_ITEMS.map(({ href, label, icon }) => (
            <Link
              key={href}
              href={`/projects/${id}${href}`}
              className={styles.navItem}
            >
              <span className={styles.navItemIcon}>{icon}</span>
              {label}
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className={styles.sidebarFooter}>
          <div className={styles.statusRow}>
            <span className={styles.statusDot} />
            <span className={styles.statusText}>Active session</span>
          </div>
        </div>
      </aside>

      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}
