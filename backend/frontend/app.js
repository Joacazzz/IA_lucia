const usersList = document.getElementById('users');
const userForm = document.getElementById('user-form');

async function fetchUsers() {
  const response = await fetch('/api/v1/users');
  const users = await response.json();
  usersList.innerHTML = '';

  users.forEach((user) => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${user.name} (${user.email})</span><button data-id="${user.id}">Excluir</button>`;
    li.querySelector('button').addEventListener('click', () => removeUser(user.id));
    usersList.appendChild(li);
  });
}

async function removeUser(id) {
  await fetch(`/api/v1/users/${id}`, { method: 'DELETE' });
  await fetchUsers();
}

userForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;

  await fetch('/api/v1/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email }),
  });

  userForm.reset();
  await fetchUsers();
});

fetchUsers();
