import { useEffect, useState } from 'react';

import { createUser, fetchUsers } from './services/userApi';

export function App() {
  const [users, setUsers] = useState([]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadUsers = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetchUsers();
      setUsers(response);
    } catch (err) {
      setError(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setError('');
      await createUser({ name, email });
      setName('');
      setEmail('');
      await loadUsers();
    } catch (err) {
      setError(err.message || 'Failed to create user');
    }
  };

  return (
    <main className="mx-auto min-h-screen max-w-3xl p-6 text-slate-100">
      <header className="mb-6 rounded-lg border border-slate-700 bg-slate-900 p-4">
        <h1 className="text-2xl font-bold">Users Dashboard</h1>
        <p className="text-slate-400">React + FastAPI + PostgreSQL</p>
      </header>

      <section className="mb-6 rounded-lg border border-slate-700 bg-slate-900 p-4">
        <h2 className="mb-4 text-lg font-semibold">Create User</h2>
        <form className="grid gap-3 md:grid-cols-3" onSubmit={handleSubmit}>
          <input
            className="rounded border border-slate-600 bg-slate-800 p-2"
            placeholder="Name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
          <input
            className="rounded border border-slate-600 bg-slate-800 p-2"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <button className="rounded bg-indigo-500 px-3 py-2 font-medium hover:bg-indigo-400" type="submit">
            Add User
          </button>
        </form>
      </section>

      <section className="rounded-lg border border-slate-700 bg-slate-900 p-4">
        <h2 className="mb-4 text-lg font-semibold">User List</h2>

        {loading && <p className="text-slate-400">Loading users...</p>}
        {error && <p className="rounded bg-red-900/40 p-2 text-red-200">{error}</p>}

        {!loading && !users.length ? (
          <p className="text-slate-400">No users found.</p>
        ) : (
          <ul className="space-y-2">
            {users.map((user) => (
              <li className="rounded border border-slate-700 p-3" key={user.id}>
                <p className="font-medium">{user.name}</p>
                <p className="text-sm text-slate-400">{user.email}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
