let auth = '';
let currentEmail = '';
let currentTable = 'stats';

function login() {
  const user = document.getElementById('user').value;
  const pass = document.getElementById('pass').value;
  auth = 'Basic ' + btoa(user + ':' + pass);
  loadPlayers();
}

function loadPlayers() {
  axios.get('/players', { headers: { Authorization: auth } })
    .then(res => {
      const playersList = document.getElementById('players');
      playersList.innerHTML = '';
      res.data.players.forEach(email => {
        const li = document.createElement('li');
        li.textContent = email;
        li.onclick = () => selectPlayer(email);
        playersList.appendChild(li);
      });
      document.getElementById('login').style.display = 'none';
      document.getElementById('content').style.display = 'block';
    })
    .catch(err => alert('Login failed'));
}

function selectPlayer(email) {
  currentEmail = email;
  document.getElementById('tableSelect').value = currentTable;
  loadDetails();
}

function loadDetails() {
  axios.get(`/data/${currentTable}/${encodeURIComponent(currentEmail)}`, { headers: { Authorization: auth } })
    .then(res => {
      document.getElementById('details').value = JSON.stringify(res.data, null, 2);
    });
}

function changeTable() {
  currentTable = document.getElementById('tableSelect').value;
  if (currentEmail) loadDetails();
}

function saveData() {
  let data;
  try {
    data = JSON.parse(document.getElementById('details').value);
  } catch (e) {
    alert('Invalid JSON');
    return;
  }
  axios.put(`/data/${currentTable}/${encodeURIComponent(currentEmail)}`, data, { headers: { Authorization: auth } })
    .then(() => alert('Saved'))
    .catch(() => alert('Save failed'));
}
