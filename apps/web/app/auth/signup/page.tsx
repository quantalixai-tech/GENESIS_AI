'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@genesis/ui';
import { fetchClientApi, ApiError } from '../../../lib/api';
import styles from '../login/page.module.css'; // Reusing login styles for consistency
import Link from 'next/link';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      await fetchClientApi('/api/auth/signup', {
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
          <h1 className={styles.title}>Create an account</h1>
          <p className={styles.subtitle}>Get started with GENESIS AI</p>
        </div>

        {error && (
          <div className={styles.errorAlert} role="alert">
            {error}
          </div>
        )}

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.label}>Email</label>
            <input
              type="email"
              id="email"
              name="email"
              className={styles.input}
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.label}>Password</label>
            <input
              type="password"
              id="password"
              name="password"
              className={styles.input}
              placeholder="Min. 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              minLength={8}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="confirmPassword" className={styles.label}>Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              className={styles.input}
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={loading}
              minLength={8}
            />
          </div>

          <Button type="submit" fullWidth loading={loading} className={styles.submitBtn}>
            Sign Up
          </Button>
        </form>

        <div className={styles.footer}>
          <p className={styles.footerText}>
            Already have an account?{' '}
            <Link href="/auth/login" className={styles.link}>
              Log in
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
