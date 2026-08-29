// search.js — Global navbar search bar (runs on every page)
// Provides autocomplete and redirects to the Player Dashboard on selection.

(function () {
    const input    = document.getElementById('nav-player-search');
    const dropdown = document.getElementById('nav-search-dropdown');
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
                window.location.href = `/player-dashboard?player=${encodeURIComponent(p.player_name)}`;
            });
            dropdown.appendChild(li);
        });
        dropdown.classList.remove('hidden');
    }

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
        if (!document.getElementById('nav-search-wrap').contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });

    // If we're on the player dashboard with a ?player= param, pre-fill input
    const urlPlayer = new URLSearchParams(window.location.search).get('player');
    if (urlPlayer) input.value = urlPlayer;
})();
