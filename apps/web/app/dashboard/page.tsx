'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Button, StatusBadge, CardHeader, CardTitle, CardFooter, Spinner } from '@genesis/ui';
import { fetchClientApi, ApiError } from '../../lib/api';
import { NewProjectModal } from './NewProjectModal';
import styles from './page.module.css';
import Link from 'next/link';

interface UserResponse {
  id: string;
  email: string;
  created_at: string;
}

interface WorkspaceResponse {
  id: string;
  name: string;
  user_id: string;
  created_at: string;
}

interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  workspace_id: string;
  created_at: string;
  updated_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [workspaces, setWorkspaces] = useState<WorkspaceResponse[]>([]);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const u = (await fetchClientApi('/auth/me')) as UserResponse;
      setUser(u);

      const ws = (await fetchClientApi('/workspaces')) as WorkspaceResponse[];
      setWorkspaces(ws);

      if (ws.length > 0) {
        const ps = (await fetchClientApi(
          `/projects/?workspace_id=${ws[0]?.id ?? ''}`,
        )) as ProjectResponse[];
        setProjects(ps);
      }
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        router.push('/auth/login');
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const defaultWorkspace = workspaces[0] ?? null;

  const handleModalClose = () => {
    setModalOpen(false);
    // Refresh projects in case one was created
    loadData();
  };

  if (loading) {
    return (
      <div className={styles.loadingScreen}>
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <>
      <div className={styles.layout}>
        {/* Sidebar */}
        <aside className={styles.sidebar}>
          <div className={styles.brand}>
            <span className={styles.logo}>⬡</span>
            <span className={styles.brandName}>GENESIS AI</span>
          </div>

          <nav className={styles.nav}>
            <Link href="/dashboard" className={`${styles.navItem} ${styles.navItemActive}`}>
              <span className={styles.navIcon}>◈</span>
              Projects
            </Link>
          </nav>

          <div className={styles.userProfile}>
            <div className={styles.avatar}>
              {user?.email.charAt(0).toUpperCase() ?? '?'}
            </div>
            <div className={styles.userInfo}>
              <div className={styles.userEmail}>{user?.email}</div>
              <div className={styles.userRole}>Developer</div>
            </div>
          </div>
        </aside>

        {/* Main content */}
        <main className={styles.main}>
          <header className={styles.header}>
            <div>
              <h1 className={styles.title}>
                {defaultWorkspace ? defaultWorkspace.name : 'My Projects'}
              </h1>
              <p className={styles.headerSub}>
                {projects.length} project{projects.length !== 1 ? 's' : ''}
              </p>
            </div>
            <Button
              id="new-project-btn"
              variant="primary"
              onClick={() => setModalOpen(true)}
            >
              + New Project
            </Button>
          </header>

          <div className={styles.content}>
            {projects.length === 0 ? (
              <div className={styles.emptyState}>
                <div className={styles.emptyOrb} aria-hidden="true" />
                <div className={styles.emptyIcon}>🚀</div>
                <h2 className={styles.emptyTitle}>Ready to build something?</h2>
                <p className={styles.emptyText}>
                  Describe your idea to GENESIS AI and watch it come to life — from
                  requirements to working code, automatically.
                </p>
                <Button
                  id="create-first-project-btn"
                  variant="primary"
                  className={styles.emptyAction}
                  onClick={() => setModalOpen(true)}
                >
                  Create your first project
                </Button>
                <div className={styles.featureHints}>
                  {['💬 Conversational requirements', '🎨 UI generation', '⚡ Live preview'].map((f) => (
                    <span key={f} className={styles.hint}>{f}</span>
                  ))}
                </div>
              </div>
            ) : (
              <div className={styles.grid}>
                {projects.map((project) => (
                  <Link href={`/projects/${project.id}`} key={project.id} className={styles.card}>
                    <CardHeader>
                      <CardTitle className={styles.cardTitle}>{project.name}</CardTitle>
                      <StatusBadge status="active" />
                    </CardHeader>
                    <p className={styles.cardDesc}>
                      {project.description ?? 'No description provided.'}
                    </p>
                    <CardFooter className={styles.cardFooter}>
                      Updated {new Date(project.updated_at).toLocaleDateString()}
                    </CardFooter>
                  </Link>
                ))}

                {/* Quick add card */}
                <button
                  id="add-project-card-btn"
                  className={styles.addCard}
                  onClick={() => setModalOpen(true)}
                >
                  <span className={styles.addIcon}>+</span>
                  <span className={styles.addText}>New Project</span>
                </button>
              </div>
            )}
          </div>
        </main>
      </div>

      <NewProjectModal
        isOpen={modalOpen}
        onClose={handleModalClose}
        defaultWorkspaceId={defaultWorkspace?.id ?? null}
      />
    </>
  );
}
