const state = { data: null };
const $ = (id) => document.getElementById(id);
const fmt = (n, digits = 0) => n == null || !Number.isFinite(Number(n)) ? '—' : Number(n).toLocaleString('vi-VN', { maximumFractionDigits: digits, minimumFractionDigits: digits });
const pct = (n, digits = 3) => n == null ? '—' : `${fmt(Number(n) * 100, digits)}%`;
const labels = {
  credit_score: 'Điểm tín dụng',
  original_ltv: 'Original LTV',
  original_dti: 'DTI',
  original_interest_rate: 'Lãi suất ban đầu',
  original_loan_term: 'Kỳ hạn khoản vay',
};
const variableInfo = {
  credit_score: 'Điểm tín dụng tại thời điểm khởi tạo; điểm cao hơn thường gắn với hồ sơ tín dụng mạnh hơn.',
  original_ltv: 'Tỷ lệ dư nợ ban đầu trên giá trị tài sản bảo đảm.',
  original_dti: 'Tỷ lệ nghĩa vụ nợ trên thu nhập tại thời điểm cấp khoản vay.',
  original_interest_rate: 'Lãi suất hợp đồng tại thời điểm khởi tạo.',
  original_loan_term: 'Kỳ hạn khoản vay ban đầu, tính bằng tháng.',
};
const pageInfo = {
  overview: ['Tổng quan', 'DANH MỤC / 01', 'Tóm tắt danh mục Freddie Mac và các chỉ số trọng tâm.'],
  portfolio: ['Danh mục & dữ liệu', 'DỮ LIỆU / 02', 'Cơ cấu trạng thái khoản vay và mức độ bao phủ theo quý.'],
  competing: ['Rủi ro cạnh tranh', 'SURVIVAL / 03', 'Theo dõi xác suất vỡ nợ, trả trước và sống sót theo tuổi khoản vay.'],
  drivers: ['Yếu tố rủi ro', 'MODEL EFFECTS / 04', 'So sánh hazard ratio và khoảng tin cậy của các mô hình sự kiện.'],
  vintage: ['Phân tích vintage', 'COHORT / 05', 'So sánh xác suất vỡ nợ theo năm phát hành và thời gian theo dõi.'],
  models: ['Mô hình & hệ số', 'MODEL TABLES / 06', 'Tra cứu hệ số, độ bất định và xuất kết quả từng mô hình.'],
  variables: ['Từ điển biến', 'FEATURE GUIDE / 07', 'Ý nghĩa các biến giải thích xuất hiện trong phân tích.'],
  'loan-lookup': ['Tra cứu khoản vay', 'LOAN LEVEL / 08', 'Xem trạng thái và đặc điểm tín dụng của một khoản vay theo Loan ID.'],
  ecl: ['ECL sandbox', 'SCENARIO / 09', 'Thử các giả định EAD, LGD và kỳ hạn với PD CIF của danh mục.'],
  research: ['Bằng chứng & hàm ý', 'RESEARCH REVIEW / 13', 'Tài liệu nền, giới hạn suy luận và các câu hỏi cần bảo vệ bằng kết quả dự án.'],
  methodology: ['Phương pháp', 'METHOD NOTES / 10', 'Các định nghĩa và giới hạn diễn giải của phương pháp survival.'],
  diagnostics: ['Chẩn đoán', 'MODEL HEALTH / 11', 'Kiểm tra tính nhất quán của dữ liệu và giả định mô hình.'],
  exports: ['Tải kết quả', 'EXPORT CENTER / 12', 'Tải các bảng kết quả CSV được sinh bởi pipeline.'],
};
const routeGroup = {
  overview: 'overview', portfolio: 'portfolio', diagnostics: 'portfolio', exports: 'portfolio',
  competing: 'risk', drivers: 'risk', vintage: 'risk', models: 'risk', variables: 'risk', methodology: 'risk',
  'loan-lookup': 'loan', ecl: 'ecl',
  research: 'risk',
};
const workspaceTabs = {
  portfolio: [
    ['portfolio', 'Danh mục'], ['diagnostics', 'Chất lượng & kiểm tra'], ['exports', 'Tải kết quả'],
  ],
  risk: [
    ['competing', 'Survival & competing risks'], ['drivers', 'Yếu tố rủi ro'], ['vintage', 'Vintage'],
    ['models', 'Mô hình & hệ số'], ['variables', 'Từ điển biến'], ['methodology', 'Phương pháp'], ['research', 'Bằng chứng & hàm ý'],
  ],
};

function showPage(route) {
  if (!pageInfo[route]) route = 'overview';
  document.querySelectorAll('[data-page]').forEach((element) => { element.hidden = true; });
  document.querySelectorAll('[data-subpage]').forEach((element) => { element.hidden = true; });

  let parentRoute = route;
  if (['vintage'].includes(route)) parentRoute = 'drivers';
  if (['variables'].includes(route)) parentRoute = 'models';
  if (['methodology'].includes(route)) parentRoute = 'ecl';
  document.querySelectorAll(`[data-page="${parentRoute}"]`).forEach((element) => { element.hidden = false; });
  if (route === 'vintage') document.querySelectorAll('[data-page="vintage"]').forEach((element) => { element.hidden = false; });
  if (route === 'drivers' || route === 'vintage') {
    const root = document.querySelector('#drivers');
    root.classList.toggle('single-view', true);
    root.querySelector('.model-panel').hidden = route !== 'drivers';
    root.querySelector('.vintage-panel').hidden = route !== 'vintage';
  } else if (route === 'models' || route === 'variables') {
    const root = document.querySelector('.advanced-grid');
    root.classList.toggle('single-view', true);
    root.querySelector('.table-panel').hidden = route !== 'models';
    root.querySelector('.variable-panel').hidden = route !== 'variables';
  } else if (route === 'ecl' || route === 'methodology') {
    const root = document.querySelector('.ecl-grid');
    root.classList.toggle('single-view', true);
    root.querySelector('.ecl-panel').hidden = route !== 'ecl';
    root.querySelector('.methodology-panel').hidden = route !== 'methodology';
  }

  const isOverview = route === 'overview';
  document.querySelector('.page-heading[data-page="overview"]').hidden = !isOverview;
  $('route-heading').hidden = isOverview;
  $('route-title').textContent = pageInfo[route][0];
  $('route-kicker').textContent = pageInfo[route][1];
  $('route-description').textContent = pageInfo[route][2];
  $('route-updated').textContent = $('updated-at').textContent;
  const group = routeGroup[route];
  document.querySelectorAll('.nav-item[data-group]').forEach((item) => {
    const active = item.dataset.group === group;
    item.classList.toggle('active', active);
    if (active) item.setAttribute('aria-current', 'location'); else item.removeAttribute('aria-current');
  });
  const tabs = workspaceTabs[group] || [];
  const subnav = $('workspace-subnav');
  subnav.hidden = !tabs.length;
  subnav.innerHTML = tabs.map(([key, label]) => `<a class="workspace-tab${key === route ? ' active' : ''}" href="#${key}" data-route="${key}"${key === route ? ' aria-current="page"' : ''}>${label}</a>`).join('');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showToast(message) {
  const toast = $('toast');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2400);
}

function setText(id, value) { $(id).textContent = value; }

async function loadDashboard() {
  $('refresh').classList.add('spinning');
  try {
    const response = await fetch('/api/dashboard', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Máy chủ trả về ${response.status}`);
    state.data = await response.json();
    render(state.data);
  } catch (error) {
    showToast('Không tải được dữ liệu. Hãy chạy dashboard_server.py trong thư mục dự án.');
    console.error(error);
  } finally {
    $('refresh').classList.remove('spinning');
  }
}

function render(data) {
  const s = data.summary;
  setText('loans', fmt(s.loans));
  setText('defaults', fmt(s.defaults));
  setText('prepayments', fmt(s.prepayments));
  setText('pd60', s.pd60 == null ? '—' : fmt(s.pd60 * 100, 4));
  setText('default-share', s.loans ? `${fmt(s.defaults / s.loans * 100, 4)}%` : '—');
  setText('prepay-share', s.loans ? `${fmt(s.prepayments / s.loans * 100, 2)}%` : '—');
  setText('updated-at', data.updated ? new Date(data.updated * 1000).toLocaleString('vi-VN') : 'Chưa có dữ liệu');
  setText('route-updated', $('updated-at').textContent);
  renderHorizons(data, $('horizon-measure').value);
  renderCif(data.cif, data.km);
  renderOverview(data);
  renderPortfolio(data);
  renderQuarterlyQuality(data.quarterly_quality || []);
  renderForest(data.models.default, 'default');
  renderVariables(data);
  renderModelTable(data, 'default');
  renderVintage(data.vintage);
  renderVintageTrajectory(data.vintage_curve || []);
  renderEventAge(data.vintage_curve || []);
  renderModelCompare(data.models);
  renderAudit(data.audit);
  renderPh(data.ph);
  renderDiagnosticCharts(data);
  renderDownloads(data.downloads);
  updateEcl();
}

function renderHorizons(data, measure = 'default') {
  const root = $('horizons');
  const rows = measure === 'survival'
    ? data.km.map((r) => ({ month: r.month, value: r.survival }))
    : data.cif.map((r) => ({ month: r.month, value: r.default }));
  if (!rows?.length) { root.innerHTML = '<p class="empty-state">Chưa có bảng CIF.</p>'; return; }
  const values = rows.map((r) => (r.value ?? 0) * 100);
  const max = Math.max(...values, 0.0001);
  root.innerHTML = rows.map((row) => {
    const value = row.value == null ? null : row.value * 100;
    const width = value == null ? 0 : Math.max(1, value / max * 100);
    return `<div class="horizon-row"><span class="horizon-label">${row.month}M</span><div class="horizon-bar"><div class="horizon-fill" style="width:${width}%"></div></div><strong class="horizon-value">${value == null ? '—' : `${fmt(value, 4)}%`}</strong></div>`;
  }).join('');
}

function renderOverview(data) {
  const checkpoints = (data.cif || []).filter((row) => [12, 24, 36, 60].includes(row.month));
  const max = Math.max(...checkpoints.map((row) => row.default || 0), 0.0001);
  $('overview-horizon-bars').innerHTML = checkpoints.map((row) => `<a class="overview-horizon" href="#competing" data-route="competing"><div><span>${row.month} tháng</span><strong>${pct(row.default, 4)}</strong></div><span class="overview-bar"><i style="width:${Math.max(3, (row.default || 0) / max * 100)}%"></i></span></a>`).join('') || '<p class="empty-state">Chưa có các mốc CIF.</p>';
}

function renderCif(rows, kmRows = []) {
  const svg = $('cif-chart');
  const W = 720, H = 225, L = 48, R = 44, T = 12, B = 33;
  const pw = W - L - R, ph = H - T - B;
  const mode = $('chart-series-mode').value;
  const limit = Number($('age-limit').value) || 120;
  const source = mode === 'km' ? kmRows : rows;
  const filtered = source.filter((r) => r.month <= limit);
  const xs = filtered.map((r) => r.month);
  $('age-limit-value').value = `${limit}M`;
  document.querySelectorAll('[data-curve]').forEach((input) => { input.disabled = mode === 'km'; });
  const renderDetailTable = () => {
    $('survival-detail-body').innerHTML = [12, 24, 36, 60].map((month) => {
      const cif = rows.find((r) => r.month === month), km = kmRows.find((r) => r.month === month);
      return `<tr><td>${month} tháng</td><td>${pct(cif?.default, 4)}</td><td>${pct(cif?.prepayment, 2)}</td><td>${pct(km?.survival, 2)}</td></tr>`;
    }).join('');
  };
  if (!xs.length) { svg.innerHTML = ''; return; }
  const xMin = 0, xMax = Math.max(...xs, 12);
  const defaultMax = Math.max(...filtered.map((r) => (r.default || 0) * 100), .001) * 1.18;
  const prepayMax = Math.max(...filtered.map((r) => (r.prepayment || 0) * 100), 1) * 1.12;
  const x = (v) => L + (v - xMin) / (xMax - xMin || 1) * pw;
  const yd = (v) => T + ph - v / defaultMax * ph;
  const yp = (v) => T + ph - v / prepayMax * ph;
  const points = (key, yfn) => filtered.map((r) => `${x(r.month).toFixed(1)},${yfn((r[key] || 0) * 100).toFixed(1)}`).join(' ');
  let grid = '';
  if (mode === 'km') {
    for (let i = 0; i <= 4; i++) {
      const y = T + ph - i * ph / 4;
      grid += `<line x1="${L}" y1="${y}" x2="${W - R}" y2="${y}" stroke="#edf0f4"/><text x="${L - 8}" y="${y + 3}" text-anchor="end" class="svg-label">${i * 25}%</text>`;
    }
    const kmPoints = filtered.map((r) => `${x(r.month).toFixed(1)},${(T + ph - (r.survival || 0) * ph).toFixed(1)}`).join(' ');
    const dots = filtered.map((r) => `<circle cx="${x(r.month)}" cy="${T + ph - (r.survival || 0) * ph}" r="4" fill="#344f41"><title>${r.month} tháng · sống sót ${pct(r.survival, 2)}</title></circle>`).join('');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.innerHTML = `${grid}<polyline points="${kmPoints}" fill="none" stroke="#344f41" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>${dots}${filtered.map((r) => `<text x="${x(r.month)}" y="${H - 8}" text-anchor="middle" class="svg-label">${r.month}m</text>`).join('')}<text x="${L}" y="10" class="svg-axis-title">KAPLAN–MEIER · ALL-CAUSE SURVIVAL</text>`;
    renderDetailTable();
    return;
  }
  for (let i = 0; i <= 4; i++) {
    const y = T + ph - i * ph / 4;
    grid += `<line x1="${L}" y1="${y}" x2="${W - R}" y2="${y}" stroke="#edf0f4"/><text x="${L - 8}" y="${y + 3}" text-anchor="end" class="svg-label">${fmt(defaultMax * i / 4, 3)}%</text><text x="${W - R + 8}" y="${y + 3}" class="svg-label">${fmt(prepayMax * i / 4, 0)}%</text>`;
  }
  const xlabels = xs.map((m) => `<text x="${x(m)}" y="${H - 8}" text-anchor="middle" class="svg-label">${m}m</text>`).join('');
  const defs = filtered.map((r) => `<circle cx="${x(r.month)}" cy="${yd((r.default || 0) * 100)}" r="3.5" fill="#d86d61" stroke="white" stroke-width="1.5"><title>${r.month} tháng · Default CIF ${pct(r.default, 4)}</title></circle>`).join('');
  const showDefault = document.querySelector('[data-curve="default"]').checked;
  const showPrepay = document.querySelector('[data-curve="prepayment"]').checked;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `${grid}${showPrepay ? `<polyline points="${points('prepayment', yp)}" fill="none" stroke="#208b83" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>` : ''}${showDefault ? `<polyline points="${points('default', yd)}" fill="none" stroke="#d86d61" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>${defs}` : ''}${xlabels}<text x="${L}" y="10" class="svg-axis-title">DEFAULT · TRỤC TRÁI</text><text x="${W - R}" y="10" text-anchor="end" class="svg-axis-title">TRẢ TRƯỚC · TRỤC PHẢI</text>`;
  renderDetailTable();
}

function renderForest(rows, model = 'default') {
  const root = $('forest');
  if (!rows?.length) { root.innerHTML = '<p class="empty-state">Chưa có kết quả mô hình.</p>'; return; }
  $('forest-subtitle').textContent = model === 'finegray'
    ? 'Subdistribution HR trên mỗi 1 độ lệch chuẩn; implementation tự xây.'
    : 'Cause-specific hazard ratio trên mỗi 1 độ lệch chuẩn.';
  const min = .2, max = 4, logMin = Math.log(min), logMax = Math.log(max);
  const position = (v) => Math.max(0, Math.min(100, (Math.log(Math.max(min, Math.min(max, v))) - logMin) / (logMax - logMin) * 100));
  const nullX = position(1);
  const enriched = rows.map((row) => {
    const hr = Number(row.hazard_ratio_per_1_sd ?? row.HR), lo = Number(row.ci_lower_95 ?? row.CI_lower_95), hi = Number(row.ci_upper_95 ?? row.CI_upper_95);
    return { row, hr, lo, hi, significant: Number.isFinite(lo) && Number.isFinite(hi) && (lo > 1 || hi < 1) };
  });
  const filter = $('driver-filter').value;
  const sort = $('driver-sort').value;
  const significantCount = enriched.filter((item) => item.significant).length;
  let shown = filter === 'significant' ? enriched.filter((item) => item.significant) : enriched;
  shown = [...shown].sort((a, b) => sort === 'name'
    ? String(a.row.variable).localeCompare(String(b.row.variable))
    : Math.abs(Math.log(b.hr || 1)) - Math.abs(Math.log(a.hr || 1)));
  $('driver-summary').textContent = `${shown.length}/${enriched.length} biến · ${significantCount} CI không cắt 1`;
  root.innerHTML = shown.map(({ row, hr, lo, hi }) => {
    const a = position(lo), b = position(hi), p = position(hr);
    const pValue = Number(row.p_value);
    return `<div class="forest-row" data-variable="${row.variable}" title="p-value: ${Number.isFinite(pValue) ? fmt(pValue, 5) : '—'}"><span class="forest-name">${labels[row.variable] || row.variable}</span><div class="forest-plot"><div class="forest-track"></div><div class="forest-null" style="left:${nullX}%"></div><div class="forest-ci" style="left:${a}%;width:${Math.max(.6, b - a)}%"></div><div class="forest-point" style="left:calc(${p}% - 3px)"></div></div><span class="forest-value">${fmt(hr, 3)} <small>(${fmt(lo, 2)}–${fmt(hi, 2)})</small></span></div>`;
  }).join('') || '<p class="empty-state">Không có biến phù hợp bộ lọc.</p>';
}

function renderVintage(rows) {
  const svg = $('vintage-chart');
  const key = $('vintage-horizon').value;
  const values = (rows || []).filter((r) => r[key] != null);
  const W = 600, H = 220, L = 42, R = 12, T = 16, B = 34;
  const pw = W - L - R, ph = H - T - B;
  const max = Math.max(...values.map((r) => r[key]), 0.01) * 1.2;
  let grid = '';
  for (let i = 0; i <= 4; i++) {
    const y = T + ph - i * ph / 4;
    grid += `<line x1="${L}" y1="${y}" x2="${W - R}" y2="${y}" stroke="#edf0f4"/><text x="${L - 7}" y="${y + 3}" text-anchor="end" class="svg-label">${fmt(max * i / 4, 2)}%</text>`;
  }
  const slot = values.length ? pw / values.length : pw;
  const bars = values.map((r, i) => {
    const value = r[key], h = value / max * ph, bx = L + i * slot + slot * .24, bw = slot * .52;
    const current = i === values.length - 1;
    return `<rect x="${bx}" y="${T + ph - h}" width="${bw}" height="${h}" rx="3" fill="${current ? '#d8dee9' : '#263754'}"/><text x="${bx + bw / 2}" y="${H - 11}" text-anchor="middle" class="svg-label">${r.year}</text>`;
  }).join('');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `${grid}${bars}`;
  const best = [...values].sort((a, b) => a[key] - b[key])[0];
  const highest = [...values].sort((a, b) => b[key] - a[key])[0];
  $('vintage-insight').innerHTML = best && highest
    ? `<span>PD thấp nhất: <strong>${best.year}</strong> · ${pct(best[key] / 100, 4)}</span><span>PD cao nhất: <strong>${highest.year}</strong> · ${pct(highest[key] / 100, 4)}</span><span>${values.length} vintage có dữ liệu tại mốc này</span>`
    : 'Chưa có kết quả vintage.';
  const horizon = key.slice(2);
  $('vintage-table-body').innerHTML = values.map((row) => `<tr><td>${row.year}</td><td>${fmt(row[key], 4)}%</td><td>${fmt(row[`prepayment${horizon}`], 2)}%</td><td>${fmt(row[`survival${horizon}`], 2)}%</td></tr>`).join('');
}

const chartColors = ['#263754', '#208b83', '#bb913a', '#d86d61', '#637fae', '#768c68', '#9a6e8a', '#5b8292', '#b2764b', '#778096', '#6c9b81'];
function renderEventAge(rows) {
  const grouped = new Map();
  (rows || []).forEach((row) => {
    const age = Number(row.age);
    if (!Number.isFinite(age)) return;
    const item = grouped.get(age) || { atRisk: 0, defaults: 0, prepayments: 0 };
    item.atRisk += Number(row.at_risk) || 0;
    item.defaults += Number(row.default_events) || 0;
    item.prepayments += Number(row.prepayment_events) || 0;
    grouped.set(age, item);
  });
  const points = [...grouped].sort((a, b) => a[0] - b[0]).map(([age, row]) => ({ age, ...row }));
  const metric = $('event-age-metric').value;
  const draw = (id, key, color, name) => {
    const svg = $(id), W = 700, H = 225, L = 48, R = 12, T = 16, B = 34, pw = W - L - R, ph = H - T - B;
    const vals = points.map((p) => metric === 'rate' ? (p.atRisk ? p[key] / p.atRisk * 1000 : 0) : p[key]);
    const maxY = Math.max(...vals, 0.001) * 1.12, maxX = Math.max(...points.map((p) => p.age), 12);
    const x = (v) => L + v / maxX * pw, y = (v) => T + ph - v / maxY * ph;
    let grid = '';
    for (let i = 0; i <= 4; i++) { const gy = T + ph - i * ph / 4; grid += `<line x1="${L}" y1="${gy}" x2="${W - R}" y2="${gy}" stroke="#e9e4da"/><text x="${L - 7}" y="${gy + 3}" text-anchor="end" class="svg-label">${fmt(maxY * i / 4, metric === 'rate' ? 2 : 0)}</text>`; }
    const poly = points.map((p) => `${x(p.age).toFixed(1)},${y(metric === 'rate' ? (p.atRisk ? p[key] / p.atRisk * 1000 : 0) : p[key]).toFixed(1)}`).join(' ');
    const dots = points.filter((_, i) => i % 12 === 0 || i === points.length - 1).map((p) => { const v = metric === 'rate' ? (p.atRisk ? p[key] / p.atRisk * 1000 : 0) : p[key]; return `<circle cx="${x(p.age)}" cy="${y(v)}" r="2.5" fill="${color}"><title>${name} · tuổi ${p.age} tháng · ${metric === 'rate' ? `${fmt(v, 3)} / 1.000 risk set` : `${fmt(v)} sự kiện`} · risk set ${fmt(p.atRisk)}</title></circle>`; }).join('');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.innerHTML = `${grid}<polyline points="${poly}" fill="none" stroke="${color}" stroke-width="2.3" stroke-linejoin="round" stroke-linecap="round"/>${dots}<text x="${L}" y="${H - 8}" class="svg-label">0 tháng</text><text x="${W - R}" y="${H - 8}" text-anchor="end" class="svg-label">${maxX} tháng</text><text x="${L}" y="10" class="svg-axis-title">${metric === 'rate' ? 'SỰ KIỆN / 1.000 RISK SET' : 'SỐ SỰ KIỆN'}</text>`;
  };
  draw('default-age-chart', 'defaults', '#d86d61', 'Default');
  draw('prepay-age-chart', 'prepayments', '#208b83', 'Prepayment');
}

function renderModelCompare(models) {
  const svg = $('model-compare-chart');
  const series = [
    { key: 'default', label: 'Cox · Default', color: '#263754', hr: (r) => Number(r.hazard_ratio_per_1_sd ?? r.HR) },
    { key: 'prepayment', label: 'Cox · Trả trước', color: '#208b83', hr: (r) => Number(r.hazard_ratio_per_1_sd ?? r.HR) },
    { key: 'finegray', label: 'Fine–Gray · Default', color: '#bb913a', hr: (r) => Number(r.HR ?? r.hazard_ratio_per_1_sd) },
  ];
  const variables = [...new Set(series.flatMap((s) => (models?.[s.key] || []).map((r) => r.variable)))];
  const W = 820, H = Math.max(220, variables.length * 43 + 48), L = 190, R = 28, T = 17, plotW = W - L - R;
  const lo = Math.log(.2), hi = Math.log(5), x = (v) => L + (Math.log(Math.max(.2, Math.min(5, v))) - lo) / (hi - lo) * plotW;
  let body = '';
  const ticks = [.2, .5, 1, 2, 5].map((v) => `<line x1="${x(v)}" y1="${T}" x2="${x(v)}" y2="${H - 28}" stroke="${v === 1 ? '#9da894' : '#ece8df'}" ${v === 1 ? 'stroke-dasharray="4 3"' : ''}/><text x="${x(v)}" y="${H - 9}" text-anchor="middle" class="svg-label">${v}</text>`).join('');
  variables.forEach((variable, i) => {
    const cy = T + 20 + i * 43;
    body += `<text x="${L - 10}" y="${cy + 3}" text-anchor="end" class="svg-label">${labels[variable] || variable}</text><line x1="${L}" y1="${cy + 16}" x2="${W - R}" y2="${cy + 16}" stroke="#f0ede6"/>`;
    series.forEach((s, j) => {
      const row = (models?.[s.key] || []).find((r) => r.variable === variable), hr = row && s.hr(row);
      if (!Number.isFinite(hr) || hr <= 0) return;
      const cyPoint = cy + (j - 1) * 9;
      body += `<circle cx="${x(hr)}" cy="${cyPoint}" r="4" fill="${s.color}"><title>${s.label} · ${labels[variable] || variable}: HR ${fmt(hr, 4)}</title></circle>`;
    });
  });
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `${ticks}${body}<text x="${L}" y="10" class="svg-axis-title">HAZARD RATIO · THANG LOG · ĐƯỜNG ĐỨT ĐOẠN = HR 1</text>`;
}

function renderVintageTrajectory(rows) {
  const years = [...new Set((rows || []).map((r) => Number(r.year)))].sort((a, b) => a - b);
  const filters = $('vintage-year-filters');
  const existing = new Set([...filters.querySelectorAll('input')].map((input) => input.value));
  if (!years.every((year) => existing.has(String(year)))) {
    filters.innerHTML = years.map((year) => `<label><input type="checkbox" value="${year}" checked><i style="--vintage-color:${chartColors[years.indexOf(year) % chartColors.length]}"></i>${year}</label>`).join('');
  }
  const selected = new Set([...filters.querySelectorAll('input:checked')].map((input) => Number(input.value)));
  const measure = $('vintage-curve-measure').value;
  const svg = $('vintage-trajectory-chart');
  const groups = new Map();
  (rows || []).filter((r) => selected.has(Number(r.year)) && Number.isFinite(Number(r[measure]))).forEach((r) => { const list = groups.get(Number(r.year)) || []; list.push(r); groups.set(Number(r.year), list); });
  const W = 920, H = 330, L = 54, R = 22, T = 20, B = 39, pw = W - L - R, ph = H - T - B;
  const maxAge = Math.max(12, ...[...groups.values()].flat().map((r) => Number(r.age)));
  const allValues = [...groups.values()].flat().map((r) => Number(r[measure]));
  const maxY = measure === 'survival' ? 1 : Math.max(1e-7, ...allValues) * 1.12;
  const x = (v) => L + Number(v) / maxAge * pw, y = (v) => T + ph - Number(v) / maxY * ph;
  let grid = '';
  const axisDigits = measure === 'default_cif' ? 5 : measure === 'prepayment_cif' ? 1 : 0;
  for (let i = 0; i <= 4; i++) { const gy = T + ph - i * ph / 4, tick = maxY * i / 4 * 100; grid += `<line x1="${L}" y1="${gy}" x2="${W - R}" y2="${gy}" stroke="#e9e4da"/><text x="${L - 8}" y="${gy + 3}" text-anchor="end" class="svg-label">${fmt(tick, axisDigits)}%</text>`; }
  const lines = [...groups].map(([year, points]) => {
    points.sort((a, b) => a.age - b.age);
    const color = chartColors[years.indexOf(year) % chartColors.length];
    const path = points.map((row, i) => `${i ? 'L' : 'M'}${x(row.age).toFixed(1)},${y(row[measure]).toFixed(1)}`).join(' ');
    return `<path d="${path}" fill="none" stroke="${color}" stroke-width="2" opacity=".88"><title>Vintage ${year}</title></path>`;
  }).join('');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `${grid}${lines}<text x="${L}" y="${H - 10}" class="svg-label">0 tháng</text><text x="${W - R}" y="${H - 10}" text-anchor="end" class="svg-label">${maxAge} tháng</text><text x="${L}" y="11" class="svg-axis-title">${measure === 'survival' ? 'SỐNG SÓT' : measure === 'default_cif' ? 'DEFAULT CIF' : 'PREPAYMENT CIF'} · TỶ LỆ${measure === 'default_cif' ? ' · TRỤC Y CO GIÃN' : ''}</text>`;
}

function renderDiagnosticCharts(data) {
  const phSvg = $('ph-r2-chart'), rows = [...(data.ph || [])].sort((a, b) => (b.r2 || 0) - (a.r2 || 0));
  const W = 620, H = Math.max(170, rows.length * 32 + 32), L = 160, R = 58, top = 14, maxR2 = Math.max(.01, ...rows.map((r) => Number(r.r2) || 0));
  const bars = rows.map((row, i) => {
    const y = top + i * 32, width = (Number(row.r2) || 0) / maxR2 * (W - L - R);
    return `<text x="${L - 9}" y="${y + 13}" text-anchor="end" class="svg-label">${labels[row.variable] || row.variable}</text><rect x="${L}" y="${y}" width="${width}" height="16" fill="#bb913a" rx="2"><title>R² ${fmt(row.r2, 5)} · p ${fmt(row.p, 4)}</title></rect><text x="${L + width + 6}" y="${y + 12}" class="svg-label">${fmt(row.r2, 4)}</text>`;
  }).join('');
  phSvg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  phSvg.innerHTML = `${bars}<text x="${L}" y="10" class="svg-axis-title">R² · TƯƠNG QUAN RESIDUAL–THỜI GIAN</text>`;

  const checks = data.audit?.checks || [];
  const groups = [
    ['Kết quả', (r) => r.check?.startsWith('result:')],
    ['Mô hình đã fit', (r) => r.check?.startsWith('model:cause_specific_cox_')],
    ['Loan-level', (r) => r.check?.startsWith('loan_level:')],
    ['CIF', (r) => r.check?.startsWith('cif:')],
    ['Thẩm định phương pháp', (r) => r.check?.startsWith('method:') || r.check?.startsWith('study:') || r.check === 'model:time_varying_cox' || r.check === 'model:fine_gray_custom_convergence'],
  ];
  $('audit-group-chart').innerHTML = groups.map(([name, test]) => {
    const list = checks.filter(test), passed = list.filter((r) => String(r.passed).toLowerCase() === 'true').length;
    const pending = list.filter((r) => String(r.status).toUpperCase() === 'UNVERIFIED').length;
    const failed = list.filter((r) => String(r.status).toUpperCase() === 'FAIL' || String(r.passed).toLowerCase() === 'false').length;
    const passWidth = list.length ? passed / list.length * 100 : 0, failWidth = list.length ? failed / list.length * 100 : 0;
    return `<div class="audit-group-row"><div><strong>${name}</strong><span>${passed} đạt${failed ? ` · ${failed} lỗi` : ''}${pending ? ` · ${pending} chưa thẩm định` : ''}</span></div><div class="audit-group-track"><i style="width:${passWidth}%"></i><b style="width:${failWidth}%"></b></div></div>`;
  }).join('');
}

function renderAudit(audit) {
  const passed = audit?.passed || 0, failed = audit?.failed || 0, unverified = audit?.unverified || 0, total = audit?.total || 0;
  setText('audit-score', `${passed}/${total}`);
  const allGood = total > 0 && failed === 0 && unverified === 0;
  setText('audit-title', allGood ? 'Các kiểm tra đều đạt' : failed ? `${failed} kiểm tra thất bại` : unverified ? 'Còn nội dung chưa thẩm định' : 'Chưa có audit');
  setText('audit-description', allGood ? 'Các kiểm tra dữ liệu, kết quả và phương pháp trong audit đều hoàn tất.' : `${unverified} nội dung phương pháp chưa được xác nhận độc lập; PASS chỉ thể hiện kiểm tra cấu trúc và nhất quán.`);
  $('audit-badge').textContent = allGood ? 'HEALTHY' : failed ? 'REVIEW' : unverified ? 'UNVERIFIED' : 'NO DATA';
  $('audit-badge').classList.toggle('fail', failed > 0);
  $('audit-badge').classList.toggle('unverified', !failed && unverified > 0);
  const checks = audit?.checks || [];
  const isPassed = (row) => String(row?.passed).toLowerCase() === 'true';
  const pass = (key) => isPassed(checks.find((r) => r.check === key));
  const modelChecks = checks.filter((r) => r.check?.startsWith('model:cause_specific_cox_'));
  const list = [
    ['Mã hóa competing risk', pass('loan_level:event_consistency')],
    ['Loan ID duy nhất', pass('loan_level:unique_loan_id')],
    ['CIF identity', pass('cif:identity')],
    ['Cox models hội tụ', modelChecks.length > 0 && modelChecks.every(isPassed)],
  ];
  $('audit-list').innerHTML = list.map(([name, ok]) => `<div class="audit-check"><span class="check-mark ${ok ? '' : 'bad'}">${ok ? '✓' : '!'}</span>${name}</div>`).join('');
  $('audit-details-list').innerHTML = checks.map((row) => {
    const pending = String(row?.status).toUpperCase() === 'UNVERIFIED';
    const ok = isPassed(row);
    return `<div class="audit-detail-row"><span class="check-mark ${pending ? 'unverified' : ok ? '' : 'bad'}">${pending ? '?' : ok ? '✓' : '!'}</span><span>${row.check}</span><small>${row.scope ? `${row.scope} · ` : ''}${row.detail}</small></div>`;
  }).join('') || '<p>Chưa có bản audit.</p>';
}

function renderPh(rows) {
  const root = $('ph-list');
  if (!rows?.length) { root.innerHTML = '<p class="empty-state">Chưa có kết quả PH.</p>'; return; }
  const sorted = [...rows].sort((a, b) => $('ph-sort').value === 'r2'
    ? (b.r2 || 0) - (a.r2 || 0)
    : (a.p ?? 1) - (b.p ?? 1));
  const flaggedCount = rows.filter((row) => row.p != null && row.p < .05).length;
  $('ph-summary').textContent = `${rows.length} biến · ${flaggedCount} biến p < 0,05`;
  root.innerHTML = sorted.map((row) => {
    const p = row.p, r2 = row.r2 || 0, width = Math.max(2, Math.min(100, Math.sqrt(r2) * 100));
    const flagged = p != null && p < .05;
    return `<div class="ph-row"><span class="ph-name">${labels[row.variable] || row.variable}</span><div class="ph-bar"><div class="ph-fill" style="width:${width}%;background:${flagged ? '#c58d3a' : '#55a590'}"></div></div><span class="ph-stat">p ${p == null ? '—' : p < .001 ? '<.001' : fmt(p, 3)}</span></div>`;
  }).join('');
  const plots = ['credit_score', 'original_ltv', 'original_dti', 'original_interest_rate', 'original_loan_term'];
  $('ph-figures').innerHTML = `<details><summary>Mở biểu đồ Schoenfeld residual</summary><div class="ph-figure-grid">${plots.map((name) => `<a href="/results/ph_plots/schoenfeld_${name}.png" target="_blank" rel="noopener"><img src="/results/ph_plots/schoenfeld_${name}.png" alt="Schoenfeld residual: ${labels[name]}"><span>${labels[name]}</span></a>`).join('')}</div></details>`;
}

$('refresh').addEventListener('click', loadDashboard);
$('model-select').addEventListener('change', (event) => renderForest(state.data?.models?.[event.target.value] || [], event.target.value));
$('driver-filter').addEventListener('change', () => renderForest(state.data?.models?.[$('model-select').value] || [], $('model-select').value));
$('driver-sort').addEventListener('change', () => renderForest(state.data?.models?.[$('model-select').value] || [], $('model-select').value));
$('vintage-horizon').addEventListener('change', () => renderVintage(state.data?.vintage || []));
$('vintage-curve-measure').addEventListener('change', () => renderVintageTrajectory(state.data?.vintage_curve || []));
$('vintage-year-filters').addEventListener('change', () => renderVintageTrajectory(state.data?.vintage_curve || []));
$('event-age-metric').addEventListener('change', () => renderEventAge(state.data?.vintage_curve || []));
$('horizon-measure').addEventListener('change', (event) => renderHorizons(state.data, event.target.value));
$('chart-series-mode').addEventListener('change', () => renderCif(state.data?.cif || [], state.data?.km || []));
$('age-limit').addEventListener('input', () => renderCif(state.data?.cif || [], state.data?.km || []));
document.querySelectorAll('[data-curve]').forEach((input) => input.addEventListener('change', () => renderCif(state.data?.cif || [], state.data?.km || [])));
$('portfolio-unit').addEventListener('change', () => { if (state.data) renderPortfolio(state.data); });
$('quarterly-metric').addEventListener('change', () => renderQuarterlyQuality(state.data?.quarterly_quality || []));
$('table-model').addEventListener('change', (event) => renderModelTable(state.data, event.target.value));
$('model-compare-select').addEventListener('change', () => renderModelTable(state.data, $('table-model').value));
$('variable-search').addEventListener('input', (event) => {
  const query = event.target.value.trim().toLowerCase();
  document.querySelectorAll('.variable-item').forEach((item) => {
    item.hidden = !`${item.textContent} ${item.dataset.variable}`.toLowerCase().includes(query);
  });
});
$('ph-sort').addEventListener('change', () => renderPh(state.data?.ph || []));
$('export-search').addEventListener('input', () => renderDownloads(state.data?.downloads || []));
$('download-current').addEventListener('click', () => {
  const choice = $('table-model').value;
  const file = choice === 'default' ? 'cause_specific_cox_default.csv' : choice === 'prepayment' ? 'cause_specific_cox_prepayment.csv' : choice === 'sensitivity' ? 'cox_sensitivity_complete_case.csv' : 'fine_gray_default.csv';
  window.location.href = `/results/${file}`;
});
$('download-audit').addEventListener('click', () => { window.location.href = '/results/final_audit.csv'; });
$('ead').addEventListener('input', updateEcl);
$('lgd').addEventListener('input', updateEcl);
$('discount').addEventListener('input', updateEcl);
$('stress-multiplier').addEventListener('input', updateEcl);
$('upside-multiplier').addEventListener('input', updateEcl);
$('ecl-horizon').addEventListener('change', updateEcl);
document.addEventListener('click', (event) => {
  const item = event.target.closest('a[data-route]');
  if (!item) return;
  event.preventDefault();
  if (window.location.hash !== item.getAttribute('href')) window.location.hash = item.getAttribute('href');
  else showPage(item.dataset.route);
});
window.addEventListener('hashchange', () => showPage(window.location.hash.slice(1)));
showPage(window.location.hash.slice(1) || 'overview');
loadDashboard();
loadLoanSamples();

function renderPortfolio(data) {
  const total = data.summary.loans || 0;
  const items = [
    { label: 'Đã tất toán trước hạn', n: data.summary.prepayments, color: 'teal' },
    { label: 'Vỡ nợ', n: data.summary.defaults, color: 'coral' },
    { label: 'Còn sống / kiểm duyệt', n: data.summary.censored, color: 'navy' },
  ];
  $('event-stack').innerHTML = `<div class="event-stackbar">${items.map((x) => `<span class="stack-${x.color}" style="width:${total ? x.n / total * 100 : 0}%" title="${x.label}: ${fmt(x.n)}"></span>`).join('')}</div>`;
  const unit = $('portfolio-unit').value;
  $('event-legend').innerHTML = items.map((x) => `<div class="event-legend-item"><span class="legend-dot ${x.color}-fill"></span><span>${x.label}</span><strong>${unit === 'share' ? `${total ? fmt(x.n / total * 100, 2) : '0'}%` : fmt(x.n)}</strong><small>${unit === 'share' ? fmt(x.n) : `${total ? fmt(x.n / total * 100, 2) : '0'}%`}</small></div>`).join('');

  const parts = items.map((item) => ({ ...item, share: total ? item.n / total * 100 : 0 }));
  let cursor = 0;
  const stops = parts.map((item) => { const start = cursor; cursor += item.share; return `${item.color === 'teal' ? '#208b83' : item.color === 'coral' ? '#d86d61' : '#263754'} ${start}% ${cursor}%`; });
  $('portfolio-donut').style.background = `conic-gradient(${stops.join(',')})`;
  $('donut-total').textContent = fmt(total);
  $('donut-legend').innerHTML = parts.map((item) => `<div class="donut-key"><i class="legend-dot ${item.color}-fill"></i><span>${item.label}</span><strong>${fmt(item.share, 2)}%</strong><small>${fmt(item.n)} khoản</small></div>`).join('');

  const quarters = data.coverage || [];
  $('coverage-total').textContent = `${quarters.length} quý`;
  const years = [...new Set(quarters.map((q) => q.slice(0, 4)))];
  $('coverage-grid').innerHTML = years.map((year) => {
    const qs = [1, 2, 3, 4].map((q) => `${year}Q${q}`);
    return `<div class="coverage-year"><strong>${year}</strong><div>${qs.map((q) => `<i class="coverage-cell ${quarters.includes(q) ? 'has-data' : ''}" title="${q}"></i>`).join('')}</div></div>`;
  }).join('');
  $('coverage-year-chart').innerHTML = years.map((year) => {
    const count = quarters.filter((q) => q.startsWith(year)).length;
    return `<div class="coverage-bar-row"><span>${year}</span><div><i style="width:${count / 4 * 100}%"></i></div><strong>${count}/4 quý</strong></div>`;
  }).join('');

  const checks = data.audit?.checks || [];
  const lookup = (name) => checks.find((row) => row.check === name);
  const pass = (row) => String(row?.passed).toLowerCase() === 'true';
  const quality = [
    ['ID khoản vay duy nhất', lookup('loan_level:unique_loan_id')],
    ['Mã hóa sự kiện thống nhất', lookup('loan_level:event_consistency')],
    ['Thời gian theo dõi hợp lệ', lookup('loan_level:valid_time')],
    ['Cân bằng CIF', lookup('cif:identity')],
  ];
  $('portfolio-quality').innerHTML = quality.map(([label, row]) => `<div class="quality-chip ${pass(row) ? 'quality-ok' : 'quality-review'}"><strong>${pass(row) ? '✓' : '!'}</strong><span>${label}</span><small>${escapeHtml(row?.detail || 'Chưa có kết quả')}</small></div>`).join('');
}

function renderQuarterlyQuality(rows) {
  const svg = $('quarterly-profile-chart');
  const metric = $('quarterly-metric').value;
  const data = [...(rows || [])].sort((a, b) => String(a.period).localeCompare(String(b.period)));
  const W = 900, H = 245, L = 62, R = 18, T = 18, B = 40, pw = W - L - R, ph = H - T - B;
  const values = data.map((row) => Number(row[metric]) || 0), maxY = Math.max(1, ...values) * 1.12;
  const x = (i) => L + (data.length <= 1 ? 0 : i / (data.length - 1) * pw), y = (v) => T + ph - v / maxY * ph;
  let grid = '';
  for (let i = 0; i <= 4; i++) { const gy = T + ph - i * ph / 4; grid += `<line x1="${L}" y1="${gy}" x2="${W - R}" y2="${gy}" stroke="#e9e4da"/><text x="${L - 8}" y="${gy + 3}" text-anchor="end" class="svg-label">${fmt(maxY * i / 4)}</text>`; }
  const path = data.map((row, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(values[i]).toFixed(1)}`).join(' ');
  const dots = data.map((row, i) => `<circle cx="${x(i)}" cy="${y(values[i])}" r="3.1" fill="#71876e"><title>${row.period} · ${metric === 'loans' ? 'khoản vay' : metric === 'rows' ? 'lượt quan sát' : 'bản ghi'}: ${fmt(values[i])}</title></circle>`).join('');
  const ticks = data.filter((_, i) => i % 4 === 0 || i === data.length - 1).map((row) => { const i = data.indexOf(row); return `<text x="${x(i)}" y="${H - 12}" text-anchor="middle" class="svg-label">${row.period.slice(2)}</text>`; }).join('');
  const title = { loans: 'KHOẢN VAY ĐỘC LẬP', rows: 'LƯỢT QUAN SÁT', duplicate_loan_age: 'DÒNG TRÙNG LOAN ID–TUỔI', missing_interest_rate: 'GIÁ TRỊ THIẾU · LÃI SUẤT', missing_ltv: 'GIÁ TRỊ THIẾU · LTV' }[metric];
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `${grid}<path d="${path}" fill="none" stroke="#71876e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>${dots}${ticks}<text x="${L}" y="11" class="svg-axis-title">${title}</text>`;
  const totalRows = data.reduce((sum, row) => sum + (Number(row.rows) || 0), 0);
  const duplicateCount = data.reduce((sum, row) => sum + (Number(row.duplicate_loan_age) || 0), 0);
  const missingInterest = data.reduce((sum, row) => sum + (Number(row.missing_interest_rate) || 0), 0);
  const missingLtv = data.reduce((sum, row) => sum + (Number(row.missing_ltv) || 0), 0);
  $('quarterly-summary').innerHTML = `<span><strong>${data.length}</strong> quý</span><span><strong>${fmt(totalRows)}</strong> lượt quan sát</span><span><strong>${fmt(duplicateCount)}</strong> dòng trùng ID–tuổi</span><span><strong>${fmt(missingInterest + missingLtv)}</strong> ô thiếu lãi suất/LTV</span>`;
  const latest = [...data].reverse().slice(0, 10);
  $('quarterly-check-table').innerHTML = `<div class="quarterly-check-head"><span>Quý</span><span>Khoản vay</span><span>Lượt xem</span><span>Trùng ID–tuổi</span><span>Thiếu</span></div>${latest.map((row) => `<div class="quarterly-check-row"><strong>${row.period}</strong><span>${fmt(row.loans)}</span><span>${fmt(row.rows)}</span><span>${fmt(row.duplicate_loan_age)}</span><span>${fmt((Number(row.missing_interest_rate) || 0) + (Number(row.missing_ltv) || 0))}</span></div>`).join('')}`;
}

function renderModelTable(data, model) {
  const rows = data?.models?.[model] || [];
  const keys = model === 'finegray' || model === 'sensitivity'
    ? ['variable', 'coefficient', 'HR', 'SE', 'p_value', 'CI_lower_95', 'CI_upper_95']
    : ['variable', 'coefficient', 'hazard_ratio_per_1_sd', 'se', 'p_value', 'ci_lower_95', 'ci_upper_95'];
  const compareKey = $('model-compare-select').value;
  const compareRows = compareKey !== 'none' && compareKey !== model ? data?.models?.[compareKey] || [] : [];
  const compareName = $('model-compare-select').selectedOptions[0]?.textContent || '';
  const display = { variable: 'Biến', coefficient: 'β', hazard_ratio_per_1_sd: 'HR', HR: 'HR', se: 'SE', SE: 'SE', p_value: 'p-value', ci_lower_95: 'CI thấp', CI_lower_95: 'CI thấp', ci_upper_95: 'CI cao', CI_upper_95: 'CI cao' };
  $('model-table-head').innerHTML = `<tr>${keys.map((k) => `<th>${display[k] || k}</th>`).join('')}${compareRows.length ? `<th>${compareName} HR</th><th>Δ HR · %</th>` : ''}</tr>`;
  $('model-table-body').innerHTML = rows.length ? rows.map((row) => {
    const cells = keys.map((key) => {
      let value = row[key];
      if (key === 'variable') value = labels[value] || value;
      else if (key === 'p_value') value = Number(value) < .001 ? '<.001' : fmt(value, 3);
      else if (Number.isFinite(Number(value))) value = fmt(Number(value), 3);
      return `<td>${escapeHtml(value ?? '—')}</td>`;
    }).join('');
    let comparison = '';
    if (compareRows.length) {
      const other = compareRows.find((item) => item.variable === row.variable);
      const getHr = (item) => Number(item?.hazard_ratio_per_1_sd ?? item?.HR);
      const currentHr = getHr(row), otherHr = getHr(other);
      const delta = Number.isFinite(currentHr) && Number.isFinite(otherHr) && otherHr !== 0 ? (currentHr / otherHr - 1) * 100 : null;
      comparison = `<td>${Number.isFinite(otherHr) ? fmt(otherHr, 3) : '—'}</td><td>${delta == null ? '—' : `${fmt(delta, 1)}%`}</td>`;
    }
    return `<tr>${cells}${comparison}</tr>`;
  }).join('') : '<tr><td colspan="9">Không có kết quả cho mô hình này.</td></tr>';
  $('table-caption').textContent = model === 'finegray'
    ? 'Fine–Gray hiện là implementation tự xây; xem như kết quả tham khảo cho đến khi được benchmark.'
    : model === 'sensitivity'
      ? 'Ước lượng complete-case; so sánh với mô hình chính để đánh giá độ nhạy với xử lý dữ liệu thiếu.'
      : 'HR trên mỗi 1 SD; khoảng tin cậy 95% từ sai số chuẩn cause-specific Cox.';
}

function renderDownloads(files) {
  const query = $('export-search').value.trim().toLowerCase();
  const visible = (files || []).filter((file) => file.replaceAll('_', ' ').toLowerCase().includes(query));
  $('download-count').textContent = `${visible.length} / ${(files || []).length} tệp`;
  $('download-list').innerHTML = visible.map((file) => `<a class="download-link" href="/results/${file}"><span>CSV</span><strong>${file.replaceAll('_', ' ').replace('.csv', '')}</strong><i>↓</i></a>`).join('') || '<p class="empty-state">Không tìm thấy tệp phù hợp.</p>';
}

function renderVariables(data = state.data) {
  $('variable-list').innerHTML = Object.entries(variableInfo).map(([key, description]) => `<details class="variable-item" data-variable="${key}"><summary>${labels[key]}</summary><p>${description}</p></details>`).join('');
  const modelKeys = ['default', 'prepayment', 'finegray', 'sensitivity'];
  const findModelRow = (model, variable) => (data?.models?.[model] || []).find((row) => row.variable === variable);
  const getHr = (row) => Number(row?.hazard_ratio_per_1_sd ?? row?.HR);
  const getBounds = (row) => [Number(row?.ci_lower_95 ?? row?.CI_lower_95), Number(row?.ci_upper_95 ?? row?.CI_upper_95)];
  const stats = new Map((data?.feature_stats || []).map((row) => [row.variable, row]));
  $('variable-effect-body').innerHTML = Object.keys(variableInfo).map((variable) => {
    const stat = stats.get(variable);
    const cells = modelKeys.map((model) => {
      const row = findModelRow(model, variable), hr = getHr(row), [lo, hi] = getBounds(row);
      return `<td>${Number.isFinite(hr) ? `${fmt(hr, 3)} <small>(${fmt(lo, 2)}–${fmt(hi, 2)})</small>` : '—'}</td>`;
    }).join('');
    return `<tr><th>${labels[variable]}</th><td>${fmt(stat?.mean, 2)}</td><td>${fmt(stat?.std, 2)}</td>${cells}</tr>`;
  }).join('');
  $('variable-list').addEventListener('toggle', (event) => {
    if (event.target.tagName !== 'DETAILS') return;
    document.querySelectorAll('.forest-row').forEach((row) => row.classList.toggle('highlighted', event.target.open && row.dataset.variable === event.target.dataset.variable));
  }, true);
}

function updateEcl() {
  if (!state.data) return;
  const horizon = Number($('ecl-horizon').value);
  const row = state.data.cif.find((item) => item.month === horizon);
  const pdValue = row?.default;
  const ead = Math.max(0, Number($('ead').value) || 0);
  const lgd = Math.min(100, Math.max(0, Number($('lgd').value) || 0)) / 100;
  const rate = Math.max(0, Number($('discount').value) || 0) / 100;
  const result = pdValue == null ? null : ead * lgd * pdValue / Math.pow(1 + rate, horizon / 12);
  setText('ecl-pd', pct(pdValue, 4));
  setText('ecl-value', result == null ? '—' : result.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }));
  const stress = Math.max(1, Math.min(10, Number($('stress-multiplier').value) || 1));
  const upside = Math.max(0, Math.min(1, Number($('upside-multiplier').value) || 0));
  const horizons = [12, 24, 36, 60];
  const money = (value) => value == null ? '—' : value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  const scenarios = horizons.map((month) => {
    const pd = state.data.cif.find((item) => item.month === month)?.default;
    const calc = (multiplier) => pd == null ? null : ead * lgd * Math.min(1, pd * multiplier) / Math.pow(1 + rate, month / 12);
    return { month, upside: calc(upside), base: calc(1), stress: calc(stress) };
  });
  $('ecl-sensitivity').innerHTML = `<div class="ecl-scenario-head"><span>Kỳ hạn</span><span>Nhẹ · ×${fmt(upside, 2)}</span><span>Cơ sở</span><span>Stress · ×${fmt(stress, 2)}</span></div>${scenarios.map((row) => `<div class="ecl-scenario-row"><strong>${row.month}M</strong><span>${money(row.upside)}</span><span>${money(row.base)}</span><span>${money(row.stress)}</span></div>`).join('')}`;
  renderEclScenarioChart(scenarios);
}

function renderEclScenarioChart(rows) {
  const svg = $('ecl-scenario-chart'), W = 700, H = 230, L = 75, R = 18, T = 17, B = 34, pw = W - L - R, ph = H - T - B;
  const series = [
    { key: 'upside', color: '#208b83', name: 'Kịch bản nhẹ' },
    { key: 'base', color: '#263754', name: 'Cơ sở' },
    { key: 'stress', color: '#d86d61', name: 'Stress' },
  ];
  const maxY = Math.max(1, ...rows.flatMap((row) => series.map((s) => Number(row[s.key]) || 0))) * 1.15;
  const x = (i) => L + (rows.length <= 1 ? 0 : i / (rows.length - 1) * pw), y = (v) => T + ph - v / maxY * ph;
  let grid = '';
  for (let i = 0; i <= 4; i++) { const gy = T + ph - i * ph / 4; grid += `<line x1="${L}" y1="${gy}" x2="${W - R}" y2="${gy}" stroke="#e9e4da"/><text x="${L - 8}" y="${gy + 3}" text-anchor="end" class="svg-label">$${fmt(maxY * i / 4)}</text>`; }
  const lines = series.map((s) => {
    const path = rows.map((row, i) => `${i ? 'L' : 'M'}${x(i)},${y(Number(row[s.key]) || 0)}`).join(' ');
    const dots = rows.map((row, i) => `<circle cx="${x(i)}" cy="${y(Number(row[s.key]) || 0)}" r="3.4" fill="${s.color}"><title>${s.name} · ${row.month} tháng · $${fmt(row[s.key], 2)}</title></circle>`).join('');
    return `<path d="${path}" fill="none" stroke="${s.color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>${dots}`;
  }).join('');
  const ticks = rows.map((row, i) => `<text x="${x(i)}" y="${H - 10}" text-anchor="middle" class="svg-label">${row.month} tháng</text>`).join('');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `${grid}${lines}${ticks}<text x="${L}" y="10" class="svg-axis-title">EXPECTED LOSS MINH HỌA · USD</text>`;
}

function renderLoanProfile(loan) {
  const root = $('loan-profile'), svg = $('loan-profile-chart'), stats = state.data?.feature_stats || [];
  const rows = stats.map((item) => {
    const value = Number(loan[item.variable]), mean = Number(item.mean), std = Number(item.std);
    return { variable: item.variable, value, mean, std, z: Number.isFinite(value) && Number.isFinite(mean) && std > 0 ? (value - mean) / std : null };
  });
  const W = 720, H = Math.max(175, rows.length * 34 + 45), L = 185, R = 34, T = 21, B = 35, pw = W - L - R;
  const x = (z) => L + (Math.max(-3, Math.min(3, z)) + 3) / 6 * pw;
  let grid = '';
  for (let tick = -3; tick <= 3; tick++) grid += `<line x1="${x(tick)}" y1="${T - 3}" x2="${x(tick)}" y2="${H - B}" stroke="${tick === 0 ? '#9da894' : '#e9e4da'}" ${tick === 0 ? 'stroke-dasharray="4 3"' : ''}/><text x="${x(tick)}" y="${H - 12}" text-anchor="middle" class="svg-label">${tick}σ</text>`;
  const body = rows.map((row, i) => {
    const cy = T + 12 + i * 34, z = row.z;
    const marker = z == null ? `<text x="${W - R}" y="${cy + 3}" text-anchor="end" class="svg-label">Thiếu</text>` : `<circle cx="${x(z)}" cy="${cy}" r="5" fill="${z > 0 ? '#bb913a' : '#208b83'}"><title>${labels[row.variable] || row.variable}: ${fmt(row.value, 3)} · trung bình ${fmt(row.mean, 3)} · ${fmt(z, 2)} độ lệch chuẩn</title></circle><text x="${W - R}" y="${cy + 3}" text-anchor="end" class="svg-label">${z > 0 ? '+' : ''}${fmt(z, 2)}σ</text>`;
    return `<text x="${L - 10}" y="${cy + 3}" text-anchor="end" class="svg-label">${labels[row.variable] || row.variable}</text><line x1="${L}" y1="${cy}" x2="${W - R}" y2="${cy}" stroke="#efede5"/>${marker}`;
  }).join('');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `${grid}${body}<text x="${L}" y="11" class="svg-axis-title">VỊ TRÍ SO VỚI PHÂN PHỐI BIẾN · THANG Z ±3σ</text>`;
  root.hidden = !rows.length;
}

const loanFieldInfo = [
  ['loan_age', 'Tuổi khoản vay', (value) => `${fmt(value)} tháng`],
  ['monthly_reporting_period', 'Kỳ báo cáo cuối', (value) => value],
  ['event_type', 'Trạng thái cuối', (value) => value],
  ['credit_score', 'Điểm tín dụng ban đầu', (value) => fmt(value)],
  ['original_cltv', 'Original CLTV', (value) => `${fmt(value, 2)}%`],
  ['original_dti', 'Original DTI', (value) => `${fmt(value, 2)}%`],
  ['original_ltv', 'Original LTV', (value) => `${fmt(value, 2)}%`],
  ['original_interest_rate', 'Lãi suất ban đầu', (value) => `${fmt(value, 3)}%`],
  ['original_loan_term', 'Kỳ hạn ban đầu', (value) => `${fmt(value)} tháng`],
  ['current_interest_rate', 'Lãi suất hiện tại', (value) => `${fmt(value, 3)}%`],
  ['ltv', 'LTV hiện tại', (value) => `${fmt(value, 2)}%`],
];

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
}

async function loadLoanSamples() {
  try {
    const response = await fetch('/api/loan-samples', { cache: 'no-store' });
    const payload = await response.json();
    const ids = payload.loan_ids || [];
    if (!ids.length) return;
    $('loan-sample-list').innerHTML = ids.map((id) => `<button type="button" class="sample-id" data-loan-id="${escapeHtml(id)}">${escapeHtml(id)}</button>`).join('');
    $('loan-samples').hidden = false;
  } catch (error) { console.warn('Không tải được mã khoản vay mẫu.', error); }
}

async function searchLoan(loanId) {
  const root = $('loan-result');
  $('loan-profile').hidden = true;
  root.innerHTML = '<div class="lookup-loading"><span class="loading-line"></span><strong>Đang tìm khoản vay…</strong><p>Lần đầu có thể cần một lúc để quét cột Loan ID trong dữ liệu.</p></div>';
  try {
    const response = await fetch(`/api/loan?loan_id=${encodeURIComponent(loanId)}`, { cache: 'no-store' });
    const payload = await response.json();
    if (!response.ok || payload.error) throw new Error(payload.error || `Máy chủ trả về ${response.status}`);
    const loan = payload.loan;
    const eventClass = loan.event_type === 'Default' ? 'event-default' : loan.event_type === 'Voluntary Prepayment' ? 'event-prepaid' : 'event-censored';
    const fields = loanFieldInfo.map(([key, label, format]) => `<div class="loan-field"><span>${label}</span><strong>${escapeHtml(format(loan[key] ?? '—'))}</strong></div>`).join('');
    root.innerHTML = `<div class="loan-result-heading"><div><span>LOAN ID</span><strong>${escapeHtml(loan.loan_id)}</strong></div><span class="loan-status ${eventClass}">${escapeHtml(loan.event_type || 'Không rõ trạng thái')}</span></div><div class="loan-fields">${fields}</div>`;
    renderLoanProfile(loan);
  } catch (error) {
    root.innerHTML = `<div class="lookup-error"><strong>Không tra cứu được khoản vay</strong><p>${escapeHtml(error.message)}</p></div>`;
  }
}

$('loan-search').addEventListener('submit', (event) => {
  event.preventDefault();
  const loanId = $('loan-id-input').value.trim();
  if (loanId) searchLoan(loanId);
});
$('loan-sample-list').addEventListener('click', (event) => {
  const button = event.target.closest('[data-loan-id]');
  if (!button) return;
  $('loan-id-input').value = button.dataset.loanId;
  searchLoan(button.dataset.loanId);
});
