import dotenv from 'dotenv';
import pg from 'pg';

dotenv.config();

const { Pool } = pg;

// Railway injeta DATABASE_URL automaticamente quando o PostgreSQL está vinculado.
// Se não existir, usa as variáveis individuais como fallback.
const pool = process.env.DATABASE_URL
  ? new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false },
      max: 20,
      idleTimeoutMillis: 30000,
    })
  : new Pool({
      host:     process.env.DB_HOST     ?? 'localhost',
      port:     Number(process.env.DB_PORT ?? 5432),
      user:     process.env.DB_USER     ?? 'postgres',
      password: process.env.DB_PASSWORD ?? 'postgres',
      database: process.env.DB_NAME     ?? 'lucia_db',
      max: 20,
      idleTimeoutMillis: 30000,
    });

export { pool };