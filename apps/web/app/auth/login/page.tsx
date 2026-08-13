'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Input, Alert } from '@genesis/ui';
import { fetchClientApi, ApiError } from '../../../lib/api';
import styles from './page.module.css';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await fetchClientApi('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      
      // Navigate to dashboard on success
      router.push('/dashboard');
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={styles.main}>
      <div className={styles.orb} aria-hidden="true" />
      <div className={styles.orbSecondary} aria-hidden="true" />

      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.logo}>⬡</div>
          <h1 className={styles.title}>Welcome back</h1>
          <p className={styles.subtitle}>Log in to GENESIS AI</p>
        </div>

        {error && (
          <Alert variant="error" className={styles.errorAlert}>
            {error}
          </Alert>
        )}

        <form className={styles.form} onSubmit={handleSubmit}>
          <Input
            label="Email"
            type="email"
            name="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
          
          <Input
            label="Password"
            type="password"
            name="password"
            placeholder="••••••••"
            value={password}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            required
            disabled={loading}
          />

          <Button type="submit" fullWidth loading={loading} className={styles.submitBtn}>
            Log In
          </Button>
        </form>

        <div className={styles.footer}>
          <p className={styles.footerText}>
            Don't have an account?{' '}
            <Link href="/auth/signup" className={styles.link}>
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
