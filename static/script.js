let statsInterval = null;
let isRunning = false;
let selectedCount = -1; // default: unlimited

// ─── COUNT SELECTOR ───
document.querySelectorAll('.count-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.count-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedCount = parseInt(this.dataset.value);
    });
});

// ─── PHONE INPUT ───
document.getElementById('phone').addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '').slice(0, 10);
});

// ─── ENTER KEY ───
document.getElementById('phone').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') startAttack();
});

// ─── ADD LOG ───
function addLog(message, type = 'info') {
    const log = document.getElementById('log-output');
    const time = new Date().toLocaleTimeString();
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    line.textContent = `[${time}] ${message}`;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
}

function clearLog() {
    document.getElementById('log-output').innerHTML = '';
    addLog('[SYSTEM] Console cleared.', 'system');
}

// ─── START ATTACK ───
async function startAttack(turbo = false) {
    const phone = document.getElementById('phone').value.trim();
    if (!phone || phone.length !== 10) {
        addLog('❌ ERROR: Please enter a valid 10-digit number!', 'error');
        return;
    }

    const types = [];
    if (document.getElementById('chk-sms').checked) types.push('sms');
    if (document.getElementById('chk-call').checked) types.push('call');
    if (document.getElementById('chk-whatsapp').checked) types.push('whatsapp');

    if (types.length === 0) {
        addLog('❌ ERROR: Select at least one attack type!', 'error');
        return;
    }

    const count = selectedCount;

    // Disable inputs
    document.getElementById('phone').disabled = true;
    document.querySelectorAll('.count-btn').forEach(b => b.style.pointerEvents = 'none');
    document.getElementById('btn-start').style.display = 'none';
    document.getElementById('btn-turbo').style.display = 'none';
    document.getElementById('btn-stop').style.display = 'flex';

    document.getElementById('target-display').textContent = `+91 ${phone}`;
    document.getElementById('target-display').className = 'status-value attacking';
    document.getElementById('status-text').textContent = turbo ? '⚡ TURBO MODE ACTIVE!' : '⚡ ATTACKING...';
    document.getElementById('status-text').className = 'status-value attacking';
    document.getElementById('stats-section').style.display = 'block';

    const countLabel = count === -1 ? '♾ UNLIMITED' : count;
    const modeLabel = turbo ? '🚀 TURBO' : 'NORMAL';
    addLog(`🚀 [${modeLabel}] INITIATING on +91 ${phone} | Type: ${types.join(', ')} | Count: ${countLabel}`, 'system');
    addLog(`🎯 Sending attack request to server...`, 'info');

    const res = await fetch('/api/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone, types, count, turbo})
    });
    const data = await res.json();

    if (!data.success) {
        addLog(`❌ ERROR: ${data.error}`, 'error');
        stopAttackUI();
        return;
    }

    addLog(`✅ ${data.message}`, 'success');
    isRunning = true;

    if (statsInterval) clearInterval(statsInterval);
    statsInterval = setInterval(fetchStats, 800); // Faster polling
}

// ─── FETCH STATS ───
async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        if (!res.ok) return;
        const stats = await res.json();

        document.getElementById('stat-sms').textContent = stats.sms_sent || 0;
        document.getElementById('stat-call').textContent = stats.calls_sent || 0;
        document.getElementById('stat-whatsapp').textContent = stats.whatsapp_sent || 0;
        document.getElementById('stat-total').textContent = stats.total || 0;
        document.getElementById('stat-failed').textContent = stats.failed || 0;

        const total = (stats.total || 0) + (stats.failed || 0);
        const pct = total > 0 ? ((stats.total || 0) / total) * 100 : 0;
        document.getElementById('progress-fill').style.width = Math.min(pct, 100) + '%';

        const statusRes = await fetch('/api/status');
        const status = await statusRes.json();
        if (!status.running && isRunning) {
            addLog(`✅ ATTACK COMPLETE! Total hits: ${stats.total} | Failed: ${stats.failed}`, 'success');
            stopAttackUI();
        }
    } catch (e) {
        // silently retry
    }
}

// ─── STOP ATTACK ───
async function stopAttack() {
    await fetch('/api/stop', {method: 'POST'});
    addLog('⛔ ATTACK MANUALLY STOPPED BY USER', 'error');
    stopAttackUI();
}

function stopAttackUI() {
    isRunning = false;
    if (statsInterval) {
        clearInterval(statsInterval);
        statsInterval = null;
    }

    document.getElementById('phone').disabled = false;
    document.querySelectorAll('.count-btn').forEach(b => b.style.pointerEvents = 'auto');
    document.getElementById('btn-start').style.display = 'flex';
    document.getElementById('btn-turbo').style.display = 'flex';
    document.getElementById('btn-stop').style.display = 'none';

    document.getElementById('status-text').textContent = '✅ COMPLETE';
    document.getElementById('status-text').className = 'status-value done';

    // Fetch final stats
    fetchStats();
}

// ─── AUTO-START if page loads with running state ───
window.addEventListener('load', async () => {
    try {
        const res = await fetch('/api/status');
        const status = await res.json();
        if (status.running) {
            document.getElementById('status-text').textContent = '⚡ ATTACKING...';
            document.getElementById('status-text').className = 'status-value attacking';
            document.getElementById('btn-start').style.display = 'none';
            document.getElementById('btn-turbo').style.display = 'none';
            document.getElementById('btn-stop').style.display = 'flex';
            document.getElementById('stats-section').style.display = 'block';
            document.getElementById('phone').disabled = true;
            isRunning = true;
            statsInterval = setInterval(fetchStats, 800);
            addLog('🔄 Reconnected to active attack session.', 'system');
        }
    } catch(e) {}
});