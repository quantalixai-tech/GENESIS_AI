/**
 * Genesis CLI — Configuration
 *
 * Platform configuration management.
 *
 * Phase 0.3+: Load from settings.json, validate against schema,
 * merge with environment variable overrides.
 */

// TODO(phase-0.3): Implement configuration loading

export interface GenesisConfig {
  /** Infrastructure service endpoints */
  services: {
    postgres: {
      host: string;
      port: number;
      database: string;
      user: string;
    };
    nats: {
      host: string;
      port: number;
    };
    minio: {
      host: string;
      port: number;
    };
  };
  /** Platform settings */
  platform: {
    env: 'development' | 'staging' | 'production';
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };
}

/** Default configuration — matches .env.development values */
export const defaultConfig: GenesisConfig = {
  services: {
    postgres: {
      host: process.env.POSTGRES_HOST ?? 'localhost',
      port: parseInt(process.env.POSTGRES_PORT ?? '5432', 10),
      database: process.env.POSTGRES_DB ?? 'genesis',
      user: process.env.POSTGRES_USER ?? 'genesis',
    },
    nats: {
      host: process.env.NATS_HOST ?? 'localhost',
      port: parseInt(process.env.NATS_PORT ?? '4222', 10),
    },
    minio: {
      host: process.env.MINIO_HOST ?? 'localhost',
      port: parseInt(process.env.MINIO_PORT ?? '9000', 10),
    },
  },
  platform: {
    env: (process.env.GENESIS_ENV ?? 'development') as GenesisConfig['platform']['env'],
    logLevel: (process.env.GENESIS_LOG_LEVEL ?? 'info') as GenesisConfig['platform']['logLevel'],
  },
};
