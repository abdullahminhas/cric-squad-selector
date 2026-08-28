// Squad generation form — handles API call, loading state, and renders results

document.getElementById('squad-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const format = document.getElementById('format').value;
    const team = document.getElementById('team').value;
    const opposition = document.getElementById('opposition').value;
    const btn = document.getElementById('generate-btn');
    const spinner = document.getElementById('loading-spinner');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    const resultsTitle = document.getElementById('results-title');
    const resultsMeta = document.getElementById('results-meta');

    // Show spinner, hide old results
    btn.disabled = true;
    btn.textContent = 'Generating…';
    spinner.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    resultsContainer.innerHTML = '';

    try {
        const response = await fetch('/api/generate-squad', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format, team, opposition })
        });

        const data = await response.json();

        if (!response.ok) {
            resultsContainer.innerHTML = `<p class="error-msg">${data.error || 'Something went wrong. Please try again.'}</p>`;
            resultsSection.classList.remove('hidden');
            return;
        }

        const now = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
        resultsTitle.textContent = `${format} Squad — ${team} vs ${opposition}`;
        resultsMeta.textContent = `Generated on ${now} · ${data.squad.length} players selected`;
        resultsContainer.innerHTML = renderSquadGroups(data.squad, format);
        resultsSection.classList.remove('hidden');

    } catch (err) {
        resultsContainer.innerHTML = `<p class="error-msg">Network error — make sure the server is running.</p>`;
        resultsSection.classList.remove('hidden');
    } finally {
        spinner.classList.add('hidden');
        btn.disabled = false;
        btn.textContent = 'Generate Squad';
    }
});

function renderSquadGroups(squad, format) {
    if (!squad || squad.length === 0) {
        return '<p class="empty-state">No players found for this combination. Try a different format or opposition.</p>';
    }

    const batsmen = squad.filter(p => p.role === 'Batsman');
    const bowlers = squad.filter(p => p.role === 'Bowler');
    const allrounders = squad.filter(p => p.role === 'All-rounder');

    let html = '';
    if (batsmen.length) html += renderGroup('Batsmen', batsmen, format);
    if (allrounders.length) html += renderGroup('All-rounders', allrounders, format);
    if (bowlers.length) html += renderGroup('Bowlers', bowlers, format);
    return html;
}

function renderGroup(title, players, format) {
    const cards = players.map(p => renderPlayerCard(p, format)).join('');
    return `
    <div class="squad-group">
        <h3 class="group-title">${title} <span class="group-count">${players.length}</span></h3>
        <div class="player-grid">${cards}</div>
    </div>`;
}

function renderPlayerCard(p, format) {
    const captainBadge = p.captain === 'Captain'
        ? '<span class="badge badge-captain">C</span>'
        : p.captain === 'Vice-Captain'
        ? '<span class="badge badge-vc">VC</span>'
        : '';

    const roleClass = p.role === 'Batsman' ? 'batsman'
        : p.role === 'Bowler' ? 'bowler'
        : 'allrounder';

    const prob = p.selection_probability ?? 0;
    const probColor = prob >= 70 ? '#2E7D32' : prob >= 40 ? '#E65100' : '#B71C1C';

    // Key stat line: for bowlers show economy, for batsmen/allrounders show batting avg
    const isBowler = p.role === 'Bowler';
    const keyStatLabel = isBowler ? 'Economy (Career)' : 'Batting Avg (Career)';
    const keyStatValue = isBowler
        ? (p.career_economy > 0 ? p.career_economy.toFixed(1) : '—')
        : (p.career_batting_avg > 0 ? p.career_batting_avg.toFixed(1) : '—');

    const recentLabel = isBowler ? 'Wkts (Last 5)' : 'Runs (Last 5)';
    const recentValue = isBowler
        ? (p.wickets_last5 ?? 0)
        : (p.runs_last5 > 0 ? p.runs_last5.toFixed(0) : '—');

    // One-line selection rationale
    const rationale = selectionRationale(p);

    return `
    <div class="player-card">
        <div class="player-card-header">
            <div>
                <span class="player-name">${p.player_name}</span>
                ${captainBadge}
            </div>
            <span class="role-tag role-${roleClass}">${p.role}</span>
        </div>
        <div class="player-team">${p.team}</div>

        <div class="prob-bar-wrap">
            <div class="prob-bar" style="width:${prob}%; background:${probColor}"></div>
        </div>
        <div class="prob-label" style="color:${probColor}">${prob}% selection confidence</div>

        <div class="player-stats">
            <div class="stat-item">
                <span class="stat-label">${keyStatLabel}</span>
                <span class="stat-value">${keyStatValue}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">${recentLabel}</span>
                <span class="stat-value">${recentValue}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Avg vs Opposition</span>
                <span class="stat-value">${p.avg_vs_opposition > 0 ? p.avg_vs_opposition.toFixed(1) : '—'}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Predicted Score</span>
                <span class="stat-value stat-score">${p.predicted_runs_capped.toFixed(1)}</span>
            </div>
        </div>

        <p class="rationale">${rationale}</p>
    </div>`;
}

function selectionRationale(p) {
    // Simple rule-based one-liner based on which stat is strongest
    const hasOppRecord = p.avg_vs_opposition > 20;
    const hasRecentForm = p.runs_last5 > 30 || p.wickets_last5 > 1;
    const hasCareerAvg = p.career_batting_avg > 30;

    if (hasOppRecord && hasRecentForm) {
        return 'Selected for strong recent form and a proven record against this opposition.';
    } else if (hasOppRecord) {
        return 'Selected primarily for a high average against this opposition.';
    } else if (hasRecentForm) {
        return 'Selected based on strong recent match form.';
    } else if (hasCareerAvg) {
        return 'Selected based on a consistent career batting average.';
    } else {
        return 'Selected by the ML ensemble as the best available option for this combination.';
    }
}
