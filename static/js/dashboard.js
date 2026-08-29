// dashboard.js — Player Form Dashboard logic
// Handles the page-level search, profile loading, Chart.js rendering, and match history.

let battingChart = null;
let bowlingChart = null;

// ─── Page-level search bar ────────────────────────────────────────────────────
(function () {
    const input    = document.getElementById('dashboard-player-search');
    const dropdown = document.getElementById('dashboard-search-dropdown');
    if (!input || !dropdown) return;

    let debounceTimer;

    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const q = input.value.trim();
        if (q.length < 2) {
            dropdown.classList.add('hidden');
            dropdown.innerHTML = '';
            return;
        }
        debounceTimer = setTimeout(() => fetchSuggestions(q), 250);
    });

    async function fetchSuggestions(q) {
        try {
            const res  = await fetch(`/api/search-players?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            renderDropdown(data.players || []);
        } catch (_) {
            dropdown.classList.add('hidden');
        }
    }

    function renderDropdown(players) {
        dropdown.innerHTML = '';
        if (players.length === 0) {
            dropdown.classList.add('hidden');
            return;
        }
        players.forEach(p => {
            const li = document.createElement('li');
            li.className = 'search-item';
            li.innerHTML = `<span class="search-item-name">${p.player_name}</span><span class="search-item-team">${p.team}</span>`;
            li.addEventListener('click', () => {
                input.value = p.player_name;
                dropdown.classList.add('hidden');
                loadPlayer(p.player_name);
            });
            dropdown.appendChild(li);
        });
        dropdown.classList.remove('hidden');
    }

    document.addEventListener('click', (e) => {
        if (!document.querySelector('.dashboard-search-wrap').contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });

    // Auto-load if ?player= is in the URL
    const urlPlayer = new URLSearchParams(window.location.search).get('player');
    if (urlPlayer) {
        input.value = urlPlayer;
        loadPlayer(urlPlayer);
    }
})();


// ─── Load & render player profile ────────────────────────────────────────────
async function loadPlayer(name) {
    const spinner = document.getElementById('dashboard-spinner');
    const profile = document.getElementById('player-profile');

    spinner.classList.remove('hidden');
    profile.classList.add('hidden');

    try {
        const res  = await fetch(`/api/player/${encodeURIComponent(name)}`);
        const data = await res.json();

        if (!res.ok) {
            alert(data.error || 'Player not found.');
            spinner.classList.add('hidden');
            return;
        }

        renderProfile(data.player);
        spinner.classList.add('hidden');
        profile.classList.remove('hidden');

    } catch (err) {
        spinner.classList.add('hidden');
        alert('Network error — please try again.');
    }
}

// ─── Render functions ─────────────────────────────────────────────────────────
function renderProfile(p) {
    // Determine role
    const isBowler    = p.career_bowling_avg > 0 && p.wickets_last10 > 1;
    const isBatsman   = p.career_batting_avg >= 20;
    const role        = isBowler && isBatsman ? 'All-rounder' : isBowler ? 'Bowler' : 'Batsman';
    const roleClass   = role === 'Batsman' ? 'batsman' : role === 'Bowler' ? 'bowler' : 'allrounder';

    // Avatar initials
    const initials = p.player_name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
    document.getElementById('profile-avatar').textContent   = initials;
    document.getElementById('profile-name').textContent     = p.player_name;
    document.getElementById('profile-team').textContent     = p.team;
    document.getElementById('profile-matches').textContent  = `${p.career_matches} career matches`;
    const roleTag = document.getElementById('profile-role-tag');
    roleTag.textContent  = role;
    roleTag.className    = `role-tag role-${roleClass}`;

    // Career stats grid
    const statsGrid = document.getElementById('career-stats-grid');
    const stats = [
        { label: 'Batting Average',  value: p.career_batting_avg > 0  ? p.career_batting_avg  : '—', unit: '' },
        { label: 'Strike Rate',      value: p.career_strike_rate > 0  ? p.career_strike_rate  : '—', unit: '' },
        { label: 'Bowling Average',  value: p.career_bowling_avg > 0  ? p.career_bowling_avg  : '—', unit: '' },
        { label: 'Economy Rate',     value: p.career_economy > 0      ? p.career_economy      : '—', unit: '' },
        { label: 'Runs (Last 5)',    value: p.runs_last5,  unit: 'runs'  },
        { label: 'Runs (Last 10)',   value: p.runs_last10, unit: 'runs'  },
        { label: 'Wkts (Last 5)',    value: p.wickets_last5,  unit: 'wkts' },
        { label: 'Wkts (Last 10)',   value: p.wickets_last10, unit: 'wkts' },
    ];
    statsGrid.innerHTML = stats.map(s => `
        <div class="stat-card card">
            <span class="stat-card-label">${s.label}</span>
            <span class="stat-card-value">${s.value}</span>
            ${s.unit ? `<span class="stat-card-unit">${s.unit}</span>` : ''}
        </div>`).join('');

    // Charts
    renderCharts(p);

    // Match history table
    const tbody = document.getElementById('history-table-body');
    if (!p.recent_matches || p.recent_matches.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#94a3b8">No match history available.</td></tr>';
    } else {
        tbody.innerHTML = p.recent_matches.slice().reverse().map(m => `
            <tr>
                <td>${m.date?.slice(0,10) ?? '—'}</td>
                <td><span class="format-badge">${m.format}</span></td>
                <td>${m.opposition}</td>
                <td class="${m.runs > 50 ? 'highlight-good' : ''}">${m.runs ?? 0}</td>
                <td class="${m.wickets > 1 ? 'highlight-good' : ''}">${m.wickets ?? 0}</td>
            </tr>`).join('');
    }
}

function renderCharts(p) {
    const matches  = p.recent_matches || [];
    const labels   = matches.map((m, i) => `M${i + 1}`);
    const runs     = matches.map(m => m.runs   ?? 0);
    const wickets  = matches.map(m => m.wickets ?? 0);

    // Destroy old charts if re-loading
    if (battingChart)  battingChart.destroy();
    if (bowlingChart)  bowlingChart.destroy();

    const battingCtx = document.getElementById('batting-chart').getContext('2d');
    battingChart = new Chart(battingCtx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Runs',
                data: runs,
                backgroundColor: 'rgba(37, 99, 235, 0.7)',
                borderColor: '#2563eb',
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });

    const bowlingCtx = document.getElementById('bowling-chart').getContext('2d');
    bowlingChart = new Chart(bowlingCtx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Wickets',
                data: wickets,
                backgroundColor: 'rgba(220, 38, 38, 0.7)',
                borderColor: '#dc2626',
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}
