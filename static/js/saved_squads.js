// ─── Load Saved Squads on page load ──────────────────────────────────────────
(async function () {
    const spinner   = document.getElementById('squads-spinner');
    const emptyEl   = document.getElementById('squads-empty');
    const listEl    = document.getElementById('squads-list');

    try {
        const res  = await fetch('/api/my-squads');

        // If not logged in, redirect to login
        if (res.status === 401) {
            window.location.href = '/login';
            return;
        }

        const data = await res.json();
        const squads = data.squads || [];

        spinner.classList.add('hidden');

        if (squads.length === 0) {
            emptyEl.classList.remove('hidden');
            return;
        }

        listEl.classList.remove('hidden');
        listEl.innerHTML = squads.map(renderSquadCard).join('');

        // Attach delete listeners
        listEl.querySelectorAll('.delete-squad-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteSquad(btn.dataset.id, btn));
        });

    } catch (_) {
        spinner.classList.add('hidden');
        listEl.innerHTML = '<p class="error-msg">Failed to load squads. Please refresh.</p>';
        listEl.classList.remove('hidden');
    }
})();


// ─── Render a single squad card ───────────────────────────────────────────────
function renderSquadCard(squad) {
    const playerRows = squad.players.map(p => {
        const roleClass = p.role === 'Batsman' ? 'batsman'
            : p.role === 'Bowler' ? 'bowler' : 'allrounder';
        const captainBadge = p.captain === 'Captain'
            ? '<span class="badge badge-captain">C</span>'
            : p.captain === 'Vice-Captain'
            ? '<span class="badge badge-vc">VC</span>'
            : '';
        return `
        <div class="saved-player-row">
            <a href="/player-dashboard?player=${encodeURIComponent(p.player_name)}" class="saved-player-name">${p.player_name}</a>
            ${captainBadge}
            <span class="role-tag role-${roleClass} role-tag-sm">${p.role}</span>
        </div>`;
    }).join('');

    return `
    <div class="saved-squad-card card" id="squad-card-${squad.id}">
        <div class="saved-squad-header">
            <div>
                <h3 class="saved-squad-label">${squad.label}</h3>
                <span class="saved-squad-meta">${squad.created_at}</span>
            </div>
            <button class="delete-squad-btn" data-id="${squad.id}" title="Delete squad">Delete</button>
        </div>
        <div class="saved-players-grid">
            ${playerRows}
        </div>
    </div>`;
}


// ─── Delete a saved squad ─────────────────────────────────────────────────────
async function deleteSquad(id, btn) {
    btn.disabled = true;
    btn.textContent = '…';

    try {
        const res = await fetch(`/api/saved-squad/${id}`, { method: 'DELETE' });

        if (res.ok) {
            const card = document.getElementById(`squad-card-${id}`);
            if (card) {
                card.style.transition = 'opacity 0.3s';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.remove();
                    // Show empty state if no cards left
                    if (!document.querySelector('.saved-squad-card')) {
                        document.getElementById('squads-list').classList.add('hidden');
                        document.getElementById('squads-empty').classList.remove('hidden');
                    }
                }, 300);
            }
        } else {
            btn.disabled = false;
            btn.textContent = 'Delete';
        }
    } catch (_) {
        btn.disabled = false;
        btn.textContent = 'Delete';
    }
}
