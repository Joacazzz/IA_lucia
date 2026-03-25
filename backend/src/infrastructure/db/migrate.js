import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { pool } from './postgresPool.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const sql = readFileSync(join(__dirname, '../../../migrations/001_create_tickets.sql'), 'utf8');

async function migrate() {
  const client = await pool.connect();
  try {
    console.log('Rodando migration...');
    await client.query(sql);
    console.log('Migration concluída com sucesso!');
  } catch (err) {
    console.error('Erro na migration:', err.message);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

migrate();