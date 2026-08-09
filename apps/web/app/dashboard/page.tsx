import { fetchServerApi, ApiError } from '../../lib/api';
import { redirect } from 'next/navigation';
import { Button } from '@genesis/ui';
import styles from './page.module.css';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

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

export default async function DashboardPage() {
  let user: UserResponse | null = null;
  let workspaces: WorkspaceResponse[] = [];
  let projects: ProjectResponse[] = [];

  try {
    // 1. Fetch current user
    user = (await fetchServerApi('/auth/me')) as UserResponse;

    // 2. Fetch workspaces
    workspaces = (await fetchServerApi('/workspaces')) as WorkspaceResponse[];

    // 3. If they have a workspace, fetch projects for the first one
    if (workspaces.length > 0) {
      projects = (await fetchServerApi(
        `/projects/?workspace_id=${workspaces[0]?.id ?? ''}`,
      )) as ProjectResponse[];
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect('/auth/login');
    }
    // For other errors, let Next.js error boundary handle it, or show empty state
    console.error('Dashboard fetch error:', error);
  }

  const defaultWorkspace = workspaces[0];

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <span className={styles.logo}>⬡</span>
          <span className={styles.brandName}>GENESIS AI</span>
        </div>

        <nav className={styles.nav}>
          <Link href="/dashboard" className={`${styles.navItem} ${styles.navItemActive}`}>
            Projects
          </Link>
          <Link href="/dashboard/settings" className={styles.navItem}>
            Settings
          </Link>
        </nav>

        <div className={styles.userProfile}>
          <div className={styles.avatar}>
            {user?.email.charAt(0).toUpperCase()}
          </div>
          <div className={styles.userInfo}>
            <div className={styles.userEmail}>{user?.email}</div>
          </div>
        </div>
      </aside>

      <main className={styles.main}>
        <header className={styles.header}>
          <h1 className={styles.title}>
            {defaultWorkspace ? defaultWorkspace.name : 'Projects'}
          </h1>
          <Button variant="primary">
            + New Project
          </Button>
        </header>

        <div className={styles.content}>
          {projects.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>🚀</div>
              <h2 className={styles.emptyTitle}>Ready to build something?</h2>
              <p className={styles.emptyText}>
                Describe your idea to GENESIS AI and watch it come to life.
              </p>
              <Button variant="primary" className={styles.emptyAction}>
                Create your first project
              </Button>
            </div>
          ) : (
            <div className={styles.grid}>
              {projects.map((project) => (
                <Link href={`/projects/${project.id}`} key={project.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>{project.name}</h3>
                    <div className={styles.statusBadge}>Active</div>
                  </div>
                  <p className={styles.cardDesc}>
                    {project.description || 'No description provided.'}
                  </p>
                  <div className={styles.cardFooter}>
                    Updated {new Date(project.updated_at).toLocaleDateString()}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
