/* ── Animate counter up ─────────────────────────────────────── */
function animateCounter(el, target, duration = 700) {
  const isFloat  = String(target).includes('.');
  const start    = performance.now();
  const from     = 0;
  (function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const ease     = 1 - Math.pow(1 - progress, 3); // cubic ease-out
    const current  = from + (target - from) * ease;
    el.textContent = isFloat
      ? current.toFixed(2)
      : Math.round(current).toLocaleString('en-IN');
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = isFloat
      ? target.toFixed(2)
      : Number(target).toLocaleString('en-IN');
  })(start);
}

function animateAllCounters(container) {
  container.querySelectorAll('.stat-value, .kpi-value').forEach(el => {
    const raw = el.textContent.replace(/[₹,]/g, '').trim();
    const num = parseFloat(raw);
    if (!isNaN(num) && num > 0) animateCounter(el, num);
  });
}

function staggerItems(container, selector, baseDelay = 0, step = 60) {
  container.querySelectorAll(selector).forEach((el, i) => {
    el.style.animationDelay = `${baseDelay + i * step}ms`;
  });
}

/* ── Constants ──────────────────────────────────────────────── */
const FILE_ICONS = {
  '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
  '.svg': '🖼️', '.webp': '🖼️', '.ico': '🖼️', '.tiff': '🖼️',
  '.pdf': '📄', '.doc': '📄', '.docx': '📄', '.txt': '📄',
  '.pptx': '📊', '.ppt': '📊', '.md': '📄', '.rtf': '📄',
  '.csv': '📊', '.xlsx': '📊', '.xls': '📊', '.json': '📋', '.xml': '📋',
  '.mp4': '🎥', '.avi': '🎥', '.mov': '🎥', '.mkv': '🎥',
  '.mp3': '🎵', '.wav': '🎵', '.aac': '🎵',
  '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦',
  '.py': '🐍', '.js': '💻', '.html': '🌐', '.css': '🎨',
  '.java': '☕', '.cpp': '💻', '.go': '💻',
};

const FILE_ICONS_MAP = {
  '🖼️': ['.jpg','.jpeg','.png','.gif','.svg','.webp','.ico','.tiff'],
  '📄': ['.pdf','.doc','.docx','.txt','.pptx','.ppt','.md','.rtf'],
  '📊': ['.csv','.xlsx','.xls'],
  '📋': ['.json','.xml'],
  '🎥': ['.mp4','.avi','.mov','.mkv'],
  '🎵': ['.mp3','.wav','.aac'],
  '📦': ['.zip','.rar','.7z','.tar'],
  '🐍': ['.py'],
  '🌐': ['.html'],
  '🎨': ['.css'],
  '💻': ['.js','.java','.cpp','.go'],
};

function getFileIcon(ext) {
  for (const [icon, exts] of Object.entries(FILE_ICONS_MAP)) {
    if (exts.includes(ext)) return icon;
  }
  return '📎';
}

const FOLDER_COLORS = {
  Images:    { bg: '#F3E8FF', color: '#7E22CE' },
  Documents: { bg: '#DBEAFE', color: '#1D4ED8' },
  Data:      { bg: '#D1FAE5', color: '#065F46' },
  Videos:    { bg: '#FEE2E2', color: '#991B1B' },
  Audio:     { bg: '#FEF3C7', color: '#92400E' },
  Archives:  { bg: '#F1F5F9', color: '#475569' },
  Code:      { bg: '#CFFAFE', color: '#155E75' },
  Other:     { bg: '#F8FAFC', color: '#64748B' },
};

/* ── State ──────────────────────────────────────────────────── */
let currentDemo = 'organizer';
const sampleCache = {};
const mergerTabData = {};
let mergerActiveTab = 'sales_jan';

/* ── Navigation ─────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => switchDemo(btn.dataset.demo));
  });
  switchDemo('organizer');
  loadEmailConfigStatus();
});

function switchDemo(demoId) {
  currentDemo = demoId;
  document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.demo === demoId));
  document.querySelectorAll('.demo-section').forEach(s => s.classList.toggle('active', s.id === `demo-${demoId}`));
  if (!sampleCache[demoId]) loadSample(demoId);
}

/* ── Load sample data ────────────────────────────────────────── */
async function loadSample(demoId) {
  try {
    const res = await fetch(`/api/sample/${demoId}`);
    if (!res.ok) { showSampleError(demoId, await res.json()); return; }
    const data = await res.json();
    sampleCache[demoId] = data;
    renderSample(demoId, data);
  } catch (e) {
    showSampleError(demoId, {detail: 'Could not reach server. Is app.py running?'});
  }
}

function showSampleError(demoId, err) {
  const msg = err?.detail || 'Unknown error';
  console.warn(`Sample load error (${demoId}):`, msg);
}

function renderSample(demoId, data) {
  const fn = { organizer: renderOrganizerSample, merger: renderMergerSample,
               cleaner: renderCleanerSample, report: renderReportSample,
               email: renderEmailSample }[demoId];
  if (fn) fn(data);
}

/* ── Demo 1: Organizer sample ────────────────────────────────── */
function renderOrganizerSample(data) {
  const grid = document.getElementById('organizer-sample');
  const pill = document.getElementById('organizer-count');
  if (pill) pill.textContent = `${data.count} files`;
  grid.innerHTML = data.files.map(f => `
    <div class="file-chip">
      <span class="file-chip-icon">${getFileIcon(f.ext)}</span>
      <span>${f.name}</span>
    </div>`).join('');
}

/* ── Demo 2: Merger sample ───────────────────────────────────── */
function renderMergerSample(data) {
  const tabBar = document.getElementById('merger-tabs');
  Object.assign(mergerTabData, data);

  tabBar.innerHTML = Object.keys(data).map((key, i) => {
    const label = key.replace('sales_', '').replace('jan','Jan').replace('feb','Feb').replace('mar','Mar');
    return `<button class="tab-btn${i===0?' active':''}" onclick="switchMergerTab('${key}',this)">${label} (${data[key].rows} rows)</button>`;
  }).join('');

  mergerActiveTab = Object.keys(data)[0];
  showMergerTab(mergerActiveTab);
}

function switchMergerTab(key, btn) {
  mergerActiveTab = key;
  document.querySelectorAll('#merger-tabs .tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  showMergerTab(key);
}

function showMergerTab(key) {
  const d = mergerTabData[key];
  if (!d) return;
  document.getElementById('merger-sample').innerHTML = buildTable(d.columns, d.preview);
}

/* ── Demo 3: Cleaner sample ──────────────────────────────────── */
function renderCleanerSample(data) {
  document.getElementById('cleaner-sample').innerHTML = buildMessyTable(data.columns, data.preview);
}

/* ── Demo 4: Report sample ───────────────────────────────────── */
function renderReportSample(data) {
  document.getElementById('report-sample').innerHTML = buildTable(data.columns, data.preview);
}

/* ── Demo 5: Email sample ────────────────────────────────────── */
function renderEmailSample(data) {
  document.getElementById('email-sample').innerHTML = buildTable(data.columns, data.preview);
}

/* ── Run demo ────────────────────────────────────────────────── */
async function runDemo(demoId) {
  const btn  = document.getElementById(`btn-${demoId}`);
  const spin = document.getElementById(`spin-${demoId}`);
  btn.disabled = true;
  if (spin) { spin.classList.add('active'); }

  try {
    const res = await fetch(`/api/run/${demoId}`, {method: 'POST'});
    if (!res.ok) {
      const err = await res.json();
      alert(`Error: ${err.detail || 'Something went wrong'}`);
      return;
    }
    const data = await res.json();
    renderResult(demoId, data);
  } catch (e) {
    alert('Could not reach server. Is app.py running?');
  } finally {
    btn.disabled = false;
    if (spin) spin.classList.remove('active');
  }
}

function renderResult(demoId, data) {
  const fn = { organizer: renderOrganizerResult, merger: renderMergerResult,
               cleaner: renderCleanerResult, report: renderReportResult,
               email: renderEmailResult }[demoId];
  if (fn) fn(data);
}

/* ── Organizer result ────────────────────────────────────────── */
function renderOrganizerResult(data) {
  const panel = document.getElementById('result-organizer');
  const body  = document.getElementById('organizer-result-body');
  panel.classList.remove('hidden');

  const totalSizeMB = data.total_size ? (data.total_size / 1024 / 1024).toFixed(2) : '—';
  const dups = data.duplicates || [];

  const statsHtml = `
    <div class="stats-row" style="margin-top:0;margin-bottom:16px;">
      <div class="stat-card">
        <div class="stat-label">Files Organised</div>
        <div class="stat-value">${data.total}</div>
        <div class="stat-sub">all categorised</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Smart Folders</div>
        <div class="stat-value">${Object.keys(data.tree).length}</div>
        <div class="stat-sub">created by type</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Size</div>
        <div class="stat-value" style="font-size:20px">${totalSizeMB} MB</div>
        <div class="stat-sub">data processed</div>
      </div>
      <div class="stat-card" style="${dups.length>0 ? 'border-color:var(--warning)' : 'border-color:var(--success)'}">
        <div class="stat-label" style="${dups.length>0 ? 'color:var(--warning)' : 'color:var(--success)'}">Duplicates</div>
        <div class="stat-value" style="${dups.length>0 ? 'color:var(--warning)' : 'color:var(--success)'}">${dups.length}</div>
        <div class="stat-sub">${dups.length > 0 ? 'flagged for review' : 'all unique files'}</div>
      </div>
    </div>`;

  // Size-by-category bars
  const sizeCat = data.size_by_category || {};
  const maxSize = Math.max(...Object.values(sizeCat), 1);
  const sizeHtml = Object.keys(sizeCat).length > 0 ? `
    <div class="section-label">SIZE BY CATEGORY</div>
    <div class="mini-chart" style="margin-bottom:16px">
      ${Object.entries(sizeCat).map(([cat, bytes]) => {
        const col = FOLDER_COLORS[cat] || FOLDER_COLORS.Other;
        const pct = (bytes / maxSize * 100).toFixed(0);
        const kb  = (bytes / 1024).toFixed(1);
        return `<div class="mini-bar-row">
          <span class="mini-bar-label">${cat}</span>
          <div class="mini-bar-track">
            <div class="mini-bar-fill" style="width:${pct}%;background:${col.color}"></div>
          </div>
          <span class="mini-bar-val">${kb} KB</span>
        </div>`;
      }).join('')}
    </div>` : '';

  const dupHtml = dups.length > 0 ? `
    <div class="dup-warning">
      ⚠️ <strong>${dups.length} potential duplicate${dups.length>1?'s':''} detected:</strong> ${dups.join(', ')} — review before deleting
    </div>` : '';

  const treeHtml = Object.entries(data.tree).map(([folder, files]) => {
    const col = FOLDER_COLORS[folder] || FOLDER_COLORS.Other;
    const filesHtml = files.map(f =>
      `<div class="folder-file-item">${getFileIcon(f.slice(f.lastIndexOf('.')).toLowerCase())} ${f}</div>`
    ).join('');
    return `
      <div class="folder-item">
        <div class="folder-header" style="background:${col.bg};color:${col.color}">
          <span>📁 ${folder}</span>
          <span class="badge" style="background:${col.bg};color:${col.color}">${files.length} file${files.length>1?'s':''}</span>
        </div>
        <div class="folder-files">${filesHtml}</div>
      </div>`;
  }).join('');

  body.innerHTML = statsHtml + sizeHtml + dupHtml +
    `<div class="section-label">FOLDER STRUCTURE</div><div class="folder-tree">${treeHtml}</div>`;
  animateAllCounters(body);
  staggerItems(panel, '.folder-item', 0, 80);
  staggerItems(panel, '.file-chip',   0, 30);
}

/* ── Merger result ───────────────────────────────────────────── */
function renderMergerResult(data) {
  const panel = document.getElementById('result-merger');
  const body  = document.getElementById('merger-result-body');
  panel.classList.remove('hidden');

  const perFile = data.per_file_stats || [];

  // Pipeline flow
  const pipeNodes = perFile.map(f => `
    <div class="pipe-node">
      <div class="pipe-icon">📄</div>
      <div class="pipe-name">${f.name}</div>
      <div class="pipe-rows">${f.rows} rows</div>
      <div class="pipe-rev">₹${Number(f.revenue).toLocaleString('en-IN',{maximumFractionDigits:0})}</div>
    </div>`).join('<div class="pipe-arrow">+</div>');

  const pipelineHtml = pipeNodes ? `
    <div class="pipeline-flow">
      ${pipeNodes}
      <div class="pipe-arrow">=</div>
      <div class="pipe-node pipe-master">
        <div class="pipe-icon">📊</div>
        <div class="pipe-name">Master</div>
        <div class="pipe-rows">${data.rows_after} rows</div>
        <div class="pipe-rev" style="color:var(--success)">Merged!</div>
      </div>
    </div>` : '';

  // Stats
  const statsHtml = `
    <div class="stats-row" style="margin-top:0;margin-bottom:16px;">
      <div class="stat-card">
        <div class="stat-label">Files Merged</div>
        <div class="stat-value">${data.files_merged}</div>
        <div class="stat-sub">CSV files combined</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Rows</div>
        <div class="stat-value">${data.rows_after}</div>
        <div class="stat-sub">${data.rows_before} before dedup</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Duplicates</div>
        <div class="stat-value" style="color:${data.duplicates_removed>0?'var(--warning)':'var(--success)'}">${data.duplicates_removed}</div>
        <div class="stat-sub">cross-file removed</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Columns</div>
        <div class="stat-value">${(data.columns||[]).length}</div>
        <div class="stat-sub">fields preserved</div>
      </div>
    </div>`;

  // Revenue comparison bars
  const maxRev = Math.max(...perFile.map(f => f.revenue), 1);
  const revBarsHtml = perFile.length > 0 ? `
    <div class="section-label">REVENUE BY SOURCE FILE</div>
    <div class="mini-chart" style="margin-bottom:16px">
      ${perFile.map(f => {
        const pct = (f.revenue / maxRev * 100).toFixed(0);
        return `<div class="mini-bar-row">
          <span class="mini-bar-label">${f.name}</span>
          <div class="mini-bar-track">
            <div class="mini-bar-fill" style="width:${pct}%"></div>
          </div>
          <span class="mini-bar-val">₹${Number(f.revenue).toLocaleString('en-IN',{maximumFractionDigits:0})}</span>
        </div>`;
      }).join('')}
    </div>` : '';

  body.innerHTML = pipelineHtml + statsHtml + revBarsHtml +
    `<div class="section-label">FIRST 10 ROWS OF MERGED FILE</div>${buildTable(data.columns, data.preview)}`;
  animateAllCounters(body);
  staggerItems(panel, '.pipe-node', 0, 100);
}

/* ── Cleaner result ──────────────────────────────────────────── */
function renderCleanerResult(data) {
  const ba    = document.getElementById('result-cleaner');
  const stats = document.getElementById('cleaner-stats');
  ba.classList.remove('hidden');
  stats.classList.remove('hidden');

  document.getElementById('cleaner-before').innerHTML = buildMessyTable(
    Object.keys(data.before[0] || {}), data.before
  );
  document.getElementById('cleaner-after').innerHTML = buildCleanTable(
    Object.keys(data.after[0] || {}), data.after, data.before
  );

  const before = data.quality_before || 0;
  const after  = data.quality_after  || 0;
  const cBefore = before < 50 ? '#DC2626' : before < 75 ? '#D97706' : '#059669';
  const cAfter  = after  < 50 ? '#DC2626' : after  < 75 ? '#D97706' : '#059669';

  const qualityHtml = `
    <div style="flex:0 0 100%">
      <div class="quality-section">
        <div class="quality-compare">
          <div class="quality-item">
            <div class="gauge" style="--pct:${before};--c:${cBefore}">
              <span class="gauge-val">${before}%</span>
            </div>
            <div class="quality-label">Before</div>
          </div>
          <div class="quality-arrow">→</div>
          <div class="quality-item">
            <div class="gauge" style="--pct:${after};--c:${cAfter}">
              <span class="gauge-val">${after}%</span>
            </div>
            <div class="quality-label">After</div>
          </div>
        </div>
        <div class="quality-title">Data Quality Score</div>
      </div>
    </div>`;

  const issueIcons = {
    'ALL_CAPS names': '🔤', 'Uppercase emails': '📧', 'Invalid email format': '⚠️',
    'Non-standard phones': '📱', 'Extra whitespace': '📐',
    'Duplicate rows': '🔁', 'Blank/empty rows': '⬜',
  };
  const issues = data.issues_found || {};
  const issueHtml = Object.keys(issues).length > 0 ? `
    <div style="flex:0 0 100%">
      <div class="section-label" style="margin-bottom:8px">ISSUES FOUND & FIXED</div>
      <div class="issue-list" style="margin-bottom:0">
        ${Object.entries(issues).map(([type, count]) =>
          `<div class="issue-item">
            <span class="issue-icon">${issueIcons[type] || '⚠️'}</span>
            <span class="issue-name">${type}</span>
            <span class="issue-count">✓ ${count} fixed</span>
          </div>`).join('')}
      </div>
    </div>` : '';

  stats.innerHTML = qualityHtml + issueHtml + `
    <div class="stat-card">
      <div class="stat-label">Rows Before</div>
      <div class="stat-value">${data.rows_before}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Blank Rows</div>
      <div class="stat-value" style="color:var(--danger)">${data.blanks_removed}</div>
      <div class="stat-sub">removed</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Duplicates</div>
      <div class="stat-value" style="color:var(--warning)">${data.duplicates_removed}</div>
      <div class="stat-sub">removed</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Clean Rows</div>
      <div class="stat-value" style="color:var(--success)">${data.rows_after}</div>
      <div class="stat-sub">100% valid</div>
    </div>`;
  animateAllCounters(stats);
  staggerItems(stats, '.issue-item', 0, 70);
  staggerItems(stats, '.stat-card',  200, 80);
}

/* ── Report result ───────────────────────────────────────────── */
let _lastReportUrl = '/output/sales_report.html';

function renderReportResult(data) {
  const panel = document.getElementById('result-report');
  const stats = document.getElementById('report-stats');
  panel.classList.remove('hidden');
  _lastReportUrl = data.report_url || '/output/sales_report.html';

  // KPI 2×2 grid
  const kpiHtml = `
    <div class="kpi-grid">
      <div class="kpi-tile">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">₹${Number(data.total_revenue).toLocaleString('en-IN',{maximumFractionDigits:0})}</div>
        <div class="kpi-sub">${data.total_orders} orders</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">₹${Number(data.avg_order||0).toLocaleString('en-IN',{maximumFractionDigits:0})}</div>
        <div class="kpi-sub">per transaction</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-label">Top Performer</div>
        <div class="kpi-value" style="font-size:15px">${data.top_person}</div>
        <div class="kpi-sub">₹${Number(data.top_person_revenue||0).toLocaleString('en-IN',{maximumFractionDigits:0})}</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-label">Next Month Est.</div>
        <div class="kpi-value" style="font-size:15px">₹${Number(data.forecast_amount||0).toLocaleString('en-IN',{maximumFractionDigits:0})}</div>
        <div class="kpi-sub">projected trend</div>
      </div>
    </div>`;

  // Monthly mini bar chart
  const monthly = data.monthly_data || [];
  const maxRev  = Math.max(...monthly.map(m => m.revenue), 1);
  const monthlyHtml = monthly.length > 0 ? `
    <div class="section-label">MONTHLY REVENUE TREND</div>
    <div class="mini-chart" style="margin-bottom:16px">
      ${monthly.map(m => {
        const pct = (m.revenue / maxRev * 100).toFixed(0);
        const growthTag = m.growth_pct != null
          ? `<span class="growth-pill ${m.growth_pct >= 0 ? 'pos' : 'neg'}">${m.growth_pct >= 0 ? '+' : ''}${m.growth_pct}%</span>`
          : '';
        return `<div class="mini-bar-row">
          <span class="mini-bar-label">${m.month}</span>
          <div class="mini-bar-track">
            <div class="mini-bar-fill" style="width:${pct}%"></div>
          </div>
          <span class="mini-bar-val">₹${Number(m.revenue).toLocaleString('en-IN',{maximumFractionDigits:0})}</span>
          ${growthTag}
        </div>`;
      }).join('')}
    </div>` : '';

  // Product revenue bars
  const products = data.product_data || [];
  const maxPRev  = Math.max(...products.map(p => p.revenue), 1);
  const productHtml = products.length > 0 ? `
    <div class="section-label">TOP PRODUCTS BY REVENUE</div>
    <div class="mini-chart" style="margin-bottom:0">
      ${products.slice(0, 5).map(p => {
        const pct = (p.revenue / maxPRev * 100).toFixed(0);
        return `<div class="mini-bar-row">
          <span class="mini-bar-label" title="${p.product}">${p.product}</span>
          <div class="mini-bar-track">
            <div class="mini-bar-fill" style="width:${pct}%;background:linear-gradient(90deg,var(--violet),#A855F7)"></div>
          </div>
          <span class="mini-bar-val">${p.share_pct}%</span>
        </div>`;
      }).join('')}
    </div>` : '';

  stats.innerHTML = kpiHtml + monthlyHtml + productHtml;
  animateAllCounters(stats);
  staggerItems(stats, '.kpi-tile', 0, 80);
}

function openReport() {
  window.open(_lastReportUrl + '?t=' + Date.now(), '_blank');
}

async function exportReport(format) {
  const btn  = document.getElementById(`btn-export-${format}`);
  const spin = document.getElementById(`spin-export-${format}`);
  btn.disabled = true;
  spin.classList.add('active');
  try {
    const res = await fetch(`/api/export/${format}`);
    if (!res.ok) {
      const err = await res.json();
      alert(`Export failed: ${err.detail || 'Unknown error'}`);
      return;
    }
    const blob = await res.blob();
    const ext  = format === 'pdf' ? 'pdf' : 'pptx';
    const a    = document.createElement('a');
    a.href     = URL.createObjectURL(blob);
    a.download = `sales_report.${ext}`;
    a.click();
    URL.revokeObjectURL(a.href);
  } catch (e) {
    alert('Export failed. Make sure the server is running and you generated the report first.');
  } finally {
    btn.disabled = false;
    spin.classList.remove('active');
  }
}

/* ── Email config ────────────────────────────────────────────── */
async function loadEmailConfigStatus() {
  try {
    const res = await fetch('/api/config/email');
    if (!res.ok) return;
    const data = await res.json();
    updateConfigBadge(data.configured, data.sender_email, data.resend_active, data.provider);
  } catch {}
}

function updateConfigBadge(configured, email, resendActive, provider) {
  const badge = document.getElementById('config-status-badge');
  if (!badge) return;
  if (resendActive && provider) {
    badge.textContent = `⚡ ${provider} active`;
    badge.className = 'cfg-badge cfg-ok';
  } else if (configured) {
    badge.textContent = `✓ ${email}`;
    badge.className = 'cfg-badge cfg-ok';
  } else {
    badge.textContent = 'Not configured';
    badge.className = 'cfg-badge cfg-not';
  }
}

function toggleConfig() {
  const body  = document.getElementById('config-body');
  const arrow = document.getElementById('toggle-arrow');
  const open  = body.classList.toggle('open');
  arrow.classList.toggle('open', open);
}

async function saveEmailConfig() {
  const email = document.getElementById('cfg-email').value.trim();
  const pass  = document.getElementById('cfg-pass').value;
  const msg   = document.getElementById('cfg-msg');
  const spin  = document.getElementById('spin-cfg');

  if (!email || !pass) { msg.textContent = 'Please fill both fields.'; msg.className = 'cfg-msg err'; return; }

  spin.classList.add('active');
  msg.textContent = '';
  try {
    const res = await fetch('/api/config/email', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({sender_email: email, sender_password: pass})
    });
    const data = await res.json();
    if (!res.ok) { msg.textContent = data.detail || 'Save failed.'; msg.className = 'cfg-msg err'; return; }
    msg.textContent = '✓ Saved! Config stored locally.';
    msg.className = 'cfg-msg ok';
    updateConfigBadge(true, email, false);
    document.getElementById('cfg-pass').value = '';
    setTimeout(() => { toggleConfig(); }, 1200);
  } catch (e) {
    msg.textContent = 'Could not reach server.';
    msg.className = 'cfg-msg err';
  } finally {
    spin.classList.remove('active');
  }
}

async function sendRealEmail() {
  const input  = document.getElementById('proof-email');
  const btn    = document.getElementById('btn-real-send');
  const spin   = document.getElementById('spin-real');
  const result = document.getElementById('send-result');
  const email  = input.value.trim();

  if (!email) { result.textContent = '⚠ Enter a recipient email.'; result.className = 'send-result err'; return; }

  btn.disabled = true;
  spin.classList.add('active');
  result.textContent = '⏳ Sending…';
  result.className = 'send-result';

  try {
    const res = await fetch('/api/send-test-email', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({recipient_email: email})
    });
    const data = await res.json();
    if (!res.ok) {
      result.textContent = `✗ ${data.detail || 'Send failed.'}`;
      result.className = 'send-result err';
    } else {
      result.textContent = `✅ Email sent to ${data.to}! Check the inbox (and spam folder).`;
      result.className = 'send-result ok';
    }
  } catch (e) {
    result.textContent = '✗ Could not reach server.';
    result.className = 'send-result err';
  } finally {
    btn.disabled = false;
    spin.classList.remove('active');
  }
}

/* ── Email result ────────────────────────────────────────────── */
function renderEmailResult(data) {
  const panel  = document.getElementById('result-email');
  const body   = document.getElementById('email-result-body');
  panel.classList.remove('hidden');

  const cards = data.results.map(r => `
    <div class="email-card">
      <div class="email-card-head">
        <div class="email-avatar">${r.name[0]}</div>
        <div>
          <div class="email-to">${r.name} — ${r.company}</div>
          <div class="email-addr">${r.to}</div>
        </div>
        <div class="email-status"><span class="badge badge-green">✓ Ready</span></div>
      </div>
      <div class="email-card-body">
        <div class="email-subject">📌 ${r.subject}</div>
        <div class="email-snippet">Hi ${r.name}, your automated report for ${r.company} is ready…</div>
      </div>
    </div>`).join('');

  body.innerHTML = `
    <div style="margin-bottom:14px;">
      <span class="badge badge-green" style="font-size:12px;padding:4px 12px;">
        ✓ ${data.emails_prepared} personalised emails ready to send
      </span>
      <span style="font-size:12px;color:var(--muted);margin-left:10px;">(demo_mode=True — not actually sent)</span>
    </div>
    <div class="email-cards">${cards}</div>`;
  staggerItems(body, '.email-card', 0, 90);
}

/* ── Table builders ──────────────────────────────────────────── */
function buildTable(columns, rows) {
  if (!rows || rows.length === 0) return '<p style="color:var(--muted);font-size:13px;">No data</p>';
  const head = `<tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr>`;
  const body = rows.map(row =>
    `<tr>${columns.map(c => `<td>${row[c] ?? ''}</td>`).join('')}</tr>`
  ).join('');
  return `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
}

function isMessy(val) {
  if (!val || val.trim() === '') return false;
  // All caps, leading/trailing spaces, non-standard phone, uppercase email
  if (val !== val.trim()) return true;
  if (val === val.toUpperCase() && val.length > 2 && /[A-Z]/.test(val)) return true;
  if (/[A-Z]/.test(val) && val.includes('@')) return true;
  return false;
}

function buildMessyTable(columns, rows) {
  if (!rows || rows.length === 0) return '<p style="color:var(--muted)">No data</p>';
  const head = `<tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr>`;
  const body = rows.map(row => {
    const cells = columns.map(c => {
      const v = row[c] ?? '';
      const messy = isMessy(v);
      return `<td class="${messy ? 'cell-messy' : ''}">${v || '<em style="color:#ccc">empty</em>'}</td>`;
    }).join('');
    return `<tr>${cells}</tr>`;
  }).join('');
  return `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
}

function buildCleanTable(columns, rows, beforeRows) {
  if (!rows || rows.length === 0) return '<p style="color:var(--muted)">No data</p>';
  // Build lookup of original messy values
  const messySet = new Set();
  (beforeRows || []).forEach(r => columns.forEach(c => { if (isMessy(r[c])) messySet.add(`${c}:${String(r[c]).trim()}`); }));

  const head = `<tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr>`;
  const body = rows.map(row => {
    const cells = columns.map(c => {
      const v = row[c] ?? '';
      const changed = messySet.has(`${c}:${v}`) === false && v !== '';
      return `<td class="${changed ? 'cell-clean' : ''}">${v}</td>`;
    }).join('');
    return `<tr>${cells}</tr>`;
  }).join('');
  return `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
}
