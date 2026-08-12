const typeMeta = {
  goal: { label: 'Цели', singular: 'Цель', code: 'ЦЛ' },
  task: { label: 'Задачи', singular: 'Задача', code: 'ЗД' },
  idea: { label: 'Идеи', singular: 'Идея', code: 'ИД' },
  criterion: { label: 'Критерии', singular: 'Критерий', code: 'КР' },
  research: { label: 'Исследования', singular: 'Исследование', code: 'ИС' },
  decision: { label: 'Решения', singular: 'Решение', code: 'РШ' },
  disagreement: { label: 'Разногласия', singular: 'Разногласие', code: 'РЗ' },
  document: { label: 'Документы', singular: 'Документ', code: 'ДК' },
};

const statusLabels = {
  draft: 'Черновик', inbox: 'Все идеи', review: 'На рассмотрении', main: 'Главная идея',
  rejected: 'Отклонено', planned: 'Не начато', in_progress: 'В работе', blocked: 'Заблокировано',
  completed: 'Выполнено', postponed: 'Перенесено', cancelled: 'Отменено', archived: 'Архив',
};

const statusesByType = {
  idea: ['inbox', 'review', 'main', 'rejected'],
  goal: ['planned', 'in_progress', 'blocked', 'completed', 'postponed', 'cancelled'],
  task: ['planned', 'in_progress', 'blocked', 'postponed', 'cancelled'],
  default: ['draft', 'in_progress', 'completed', 'cancelled'],
};

const navItems = [
  ['dashboard', 'Проект'], ['goal', 'Цели'], ['task', 'Задачи'], ['idea', 'Идеи'],
  ['criterion', 'Критерии'], ['research', 'Исследования'], ['decision', 'Решения'],
  ['disagreement', 'Разногласия'], ['document', 'Документы'], ['history', 'История изменений'],
  ['timeline', 'Timeline / Хронология'], ['structure', 'Структура карточек'], ['notifications', 'Уведомления'],
];

const state = {
  me: null, users: [], records: [], notifications: [], activity: [], definitions: [],
  view: 'dashboard', search: '', statusFilter: '', ownerFilter: '', authMode: 'login', activeDetail: null,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHTML(value = '') {
  return String(value).replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
}

function formatDate(value, withTime = false) {
  if (!value) return 'Без срока';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('ru-RU', withTime ? { dateStyle: 'medium', timeStyle: 'short' } : { day: '2-digit', month: 'short', year: 'numeric' }).format(date);
}

function toLocalInput(value) {
  if (!value) return '';
  const date = new Date(value);
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

function minutesLabel(minutes) {
  if (!minutes) return 'Не оценено';
  if (minutes < 60) return `${minutes} мин`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} ч ${rest} мин` : `${hours} ч`;
}

function deadlineState(record) {
  if (record.status === 'completed') return { className: 'done', label: 'Выполнено' };
  if (!record.dueAt) return { className: 'none', label: 'Без срока' };
  const delta = new Date(record.dueAt).getTime() - Date.now();
  if (delta < 0) return { className: 'overdue', label: `Просрочено · ${formatDate(record.dueAt)}` };
  if (delta <= 86400000) return { className: 'urgent', label: `Менее суток · ${formatDate(record.dueAt)}` };
  if (delta <= 259200000) return { className: 'soon', label: `Скоро · ${formatDate(record.dueAt)}` };
  return { className: 'normal', label: formatDate(record.dueAt) };
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: 'same-origin',
    ...options,
    headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) },
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith('/api/auth/')) showAuth();
    throw new Error(data.error || 'Ошибка запроса');
  }
  return data;
}

function toast(message, error = false) {
  const node = $('#toast');
  node.textContent = message;
  node.className = `toast visible${error ? ' error' : ''}`;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { node.className = 'toast'; }, 3200);
}

function showAuth() {
  $('#app-root').hidden = true;
  $('#auth-root').hidden = false;
}

function showApp() {
  $('#auth-root').hidden = true;
  $('#app-root').hidden = false;
  $('#user-name').textContent = state.me.username;
  $('#user-avatar').textContent = state.me.username.slice(0, 2).toUpperCase();
}

async function bootstrap() {
  bindGlobalEvents();
  try {
    state.me = await api('/api/me');
    showApp();
    await loadData();
  } catch (error) {
    showAuth();
  }
}

async function loadData(silent = false) {
  if (!silent) $('#sync-state').textContent = 'Обновление…';
  const [users, records, notifications, activity, definitions] = await Promise.all([
    api('/api/users'), api('/api/records?includeArchived=true'), api('/api/notifications'),
    api('/api/activity'), api('/api/section-definitions'),
  ]);
  Object.assign(state, { users, records, notifications, activity, definitions });
  $('#sync-state').textContent = 'Сохранено';
  render();
}

function bindGlobalEvents() {
  $$('[data-auth-mode]').forEach((button) => button.addEventListener('click', () => setAuthMode(button.dataset.authMode)));
  $('#auth-form').addEventListener('submit', submitAuth);
  $('#logout-button').addEventListener('click', async () => { await api('/api/auth/logout', { method: 'POST' }); location.reload(); });
  $('#profile-button').addEventListener('click', async () => {
    const username = await askText({ title: 'Профиль', label: 'Логин', defaultValue: state.me.username, required: true });
    if (!username || username === state.me.username) return;
    try {
      state.me = await api('/api/me', { method: 'PATCH', body: JSON.stringify({ username }) });
      $('#user-name').textContent = state.me.username;
      $('#user-avatar').textContent = state.me.username.slice(0, 2).toUpperCase();
      await loadData(true);
      toast('Логин изменён');
    } catch (error) { toast(error.message, true); }
  });
  $('#new-record-button').addEventListener('click', () => openCreateDialog(typeMeta[state.view] ? state.view : 'idea'));
  $('#menu-button').addEventListener('click', () => $('.sidebar').classList.toggle('open'));
  $('#record-dialog').addEventListener('click', (event) => { if (event.target === $('#record-dialog')) $('#record-dialog').close(); });
  $('#create-dialog').addEventListener('click', (event) => { if (event.target === $('#create-dialog')) $('#create-dialog').close(); });
  $('#reason-dialog').addEventListener('click', (event) => { if (event.target === $('#reason-dialog')) $('#reason-dialog').close('cancel'); });
  setInterval(async () => {
    if (!state.me) return;
    try {
      state.notifications = await api('/api/notifications');
      renderNav();
      if (state.view === 'notifications') renderContent();
    } catch (_) {}
  }, 30000);
}

function setAuthMode(mode) {
  state.authMode = mode;
  $$('[data-auth-mode]').forEach((button) => button.classList.toggle('active', button.dataset.authMode === mode));
  $('#email-field').hidden = mode !== 'register';
  $('#email-field input').required = mode === 'register';
  $('#login-label').textContent = mode === 'register' ? 'Логин' : 'Логин или почта';
  $('#auth-submit').textContent = mode === 'register' ? 'Создать аккаунт' : 'Войти';
  $('#auth-form').password.autocomplete = mode === 'register' ? 'new-password' : 'current-password';
  $('#auth-error').textContent = '';
}

async function submitAuth(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const body = state.authMode === 'register'
    ? { email: form.get('email'), username: form.get('login'), password: form.get('password') }
    : { login: form.get('login'), password: form.get('password') };
  try {
    state.me = await api(`/api/auth/${state.authMode}`, { method: 'POST', body: JSON.stringify(body) });
    showApp();
    await loadData();
  } catch (error) {
    $('#auth-error').textContent = error.message;
  }
}

function render() {
  renderNav();
  renderContent();
}

function renderNav() {
  const unread = state.notifications.filter((item) => !item.readAt).length;
  $('#main-nav').innerHTML = navItems.map(([key, label]) => {
    const count = typeMeta[key] ? state.records.filter((record) => record.type === key && record.status !== 'archived').length : key === 'notifications' ? unread : '';
    return `<button type="button" class="nav-item ${state.view === key ? 'active' : ''}" data-view="${key}"><span class="nav-glyph">${typeMeta[key]?.code || ({ dashboard: 'ПР', history: 'ИС', timeline: 'ХР', structure: 'СТ', notifications: 'УВ' }[key])}</span><span>${label}</span>${count !== '' ? `<b>${count}</b>` : ''}</button>`;
  }).join('');
  $$('[data-view]', $('#main-nav')).forEach((button) => button.addEventListener('click', () => {
    state.view = button.dataset.view; state.statusFilter = ''; state.search = ''; state.ownerFilter = '';
    $('.sidebar').classList.remove('open'); render();
  }));
}

function renderContent() {
  const titles = Object.fromEntries(navItems);
  $('#page-title').textContent = titles[state.view] || 'Проект';
  $('#new-record-button').hidden = ['history', 'timeline', 'structure', 'notifications'].includes(state.view);
  if (state.view === 'dashboard') return renderDashboard();
  if (typeMeta[state.view]) return renderRecordList(state.view);
  if (state.view === 'history') return renderHistory();
  if (state.view === 'timeline') return renderTimeline();
  if (state.view === 'structure') return renderStructure();
  if (state.view === 'notifications') return renderNotifications();
}

function renderDashboard() {
  const active = state.records.filter((record) => !['completed', 'cancelled', 'archived', 'rejected'].includes(record.status));
  const tasks = active.filter((record) => record.type === 'task');
  const overdue = tasks.filter((record) => deadlineState(record).className === 'overdue');
  const ideas = state.records.filter((record) => record.type === 'idea' && record.status !== 'archived');
  const mainIdeas = ideas.filter((record) => record.status === 'main');
  $('#main-content').innerHTML = `
    <section class="metrics-grid">
      ${metric('Активные задачи', tasks.length, 'В работе у команды')}
      ${metric('Просрочено', overdue.length, overdue.length ? 'Требуют внимания' : 'Сроки соблюдаются', overdue.length ? 'danger' : '')}
      ${metric('Все идеи', ideas.length, 'Ничего не потеряно')}
      ${metric('Главные идеи', mainIdeas.length, 'Текущий фокус', 'accent')}
    </section>
    <section class="dashboard-grid">
      <div class="section-panel">
        <div class="section-heading"><div><p class="eyebrow">Команда</p><h3>Загрузка по задачам</h3></div></div>
        <div class="people-load">${state.users.map((user) => renderPersonLoad(user, tasks)).join('') || emptyState('Второй участник появится после регистрации.')}</div>
      </div>
      <div class="section-panel">
        <div class="section-heading"><div><p class="eyebrow">Ближайшее</p><h3>Сроки и контроль</h3></div><button class="text-button" data-go="task">Все задачи</button></div>
        <div class="compact-list">${tasks.slice().sort(sortByDeadline).slice(0, 7).map(renderCompactRecord).join('') || emptyState('Активных задач пока нет.')}</div>
      </div>
    </section>
    <section class="section-panel">
      <div class="section-heading"><div><p class="eyebrow">Лента проекта</p><h3>Последние изменения</h3></div><button class="text-button" data-go="history">Вся история</button></div>
      <div class="activity-list">${state.activity.slice(0, 8).map(renderActivityItem).join('') || emptyState('История появится после первой карточки.')}</div>
    </section>`;
  bindOpenRecords();
  $$('[data-go]').forEach((button) => button.addEventListener('click', () => { state.view = button.dataset.go; render(); }));
}

function metric(label, value, note, tone = '') {
  return `<div class="metric ${tone}"><span>${escapeHTML(label)}</span><strong>${value}</strong><small>${escapeHTML(note)}</small></div>`;
}

function renderPersonLoad(user, tasks) {
  const owned = tasks.filter((task) => task.ownerId === user.id);
  const minutes = owned.reduce((sum, task) => sum + task.estimateMinutes, 0);
  const progress = owned.length ? Math.round(owned.reduce((sum, task) => sum + task.progress, 0) / owned.length) : 0;
  return `<button type="button" class="person-load" data-owner-filter="${user.id}"><span class="avatar">${escapeHTML(user.username.slice(0, 2).toUpperCase())}</span><span class="person-main"><strong>${escapeHTML(user.username)}</strong><small>${owned.length} задач · ${minutesLabel(minutes)}</small><span class="progress-track"><i style="width:${progress}%"></i></span></span><b>${progress}%</b></button>`;
}

function sortByDeadline(a, b) {
  if (!a.dueAt) return 1;
  if (!b.dueAt) return -1;
  return new Date(a.dueAt) - new Date(b.dueAt);
}

function renderCompactRecord(record) {
  const deadline = deadlineState(record);
  return `<button type="button" class="compact-record" data-open-record="${record.id}"><span class="type-code">${typeMeta[record.type].code}</span><span><strong>${escapeHTML(record.title)}</strong><small>${escapeHTML(record.ownerUsername)} · ${minutesLabel(record.estimateMinutes)}</small></span><em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em></button>`;
}

function renderRecordList(type) {
  let records = state.records.filter((record) => record.type === type);
  if (!state.statusFilter) records = records.filter((record) => record.status !== 'archived');
  if (state.statusFilter) records = records.filter((record) => record.status === state.statusFilter);
  if (state.ownerFilter) records = records.filter((record) => String(record.ownerId) === state.ownerFilter);
  if (state.search) {
    const query = state.search.toLowerCase();
    records = records.filter((record) => `${record.title} ${record.description}`.toLowerCase().includes(query));
  }
  const statusTabs = type === 'idea' ? ['all', 'inbox', 'review', 'main', 'rejected', 'archived'] : ['all', ...(statusesByType[type] || statusesByType.default), 'archived'];
  $('#main-content').innerHTML = `
    <div class="list-toolbar">
      <div class="search-box"><input id="record-search" type="search" placeholder="Поиск по карточкам" value="${escapeHTML(state.search)}"></div>
      <select id="owner-filter" aria-label="Ответственный"><option value="">Все ответственные</option>${state.users.map((user) => `<option value="${user.id}" ${state.ownerFilter === String(user.id) ? 'selected' : ''}>${escapeHTML(user.username)}</option>`).join('')}</select>
      <span class="record-total">${records.length} записей</span>
    </div>
    <div class="status-tabs">${statusTabs.map((status) => `<button type="button" data-status-filter="${status === 'all' ? '' : status}" class="${state.statusFilter === (status === 'all' ? '' : status) ? 'active' : ''}">${status === 'all' ? 'Все' : statusLabels[status]}</button>`).join('')}</div>
    <section class="table-panel">
      <div class="record-table header ${type === 'task' || type === 'goal' ? '' : 'simple'}"><span>Карточка</span><span>Ответственный</span><span>Статус</span><span>${type === 'task' || type === 'goal' ? 'Срок / прогресс' : 'Изменено'}</span></div>
      <div class="record-rows">${records.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)).map(renderRecordRow).join('') || emptyState('Карточек в этом представлении пока нет.')}</div>
    </section>`;
  $('#record-search').addEventListener('input', (event) => { state.search = event.target.value; renderRecordList(type); });
  $('#owner-filter').addEventListener('change', (event) => { state.ownerFilter = event.target.value; renderRecordList(type); });
  $$('[data-status-filter]').forEach((button) => button.addEventListener('click', () => { state.statusFilter = button.dataset.statusFilter; renderRecordList(type); }));
  bindOpenRecords();
}

function renderRecordRow(record) {
  const isPlannable = record.type === 'task' || record.type === 'goal';
  const deadline = deadlineState(record);
  return `<button type="button" class="record-table row ${isPlannable ? '' : 'simple'}" data-open-record="${record.id}">
    <span class="record-title"><i class="type-code">${typeMeta[record.type].code}</i><span><strong>${escapeHTML(record.title)}</strong><small>${escapeHTML(record.description || 'Без описания')}</small></span></span>
    <span><b class="owner-chip">${escapeHTML(record.ownerUsername)}</b><small>создал ${escapeHTML(record.authorUsername)}</small></span>
    <span><em class="status status-${record.status}">${escapeHTML(statusLabels[record.status] || record.status)}</em></span>
    <span>${isPlannable ? `<em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em><span class="progress-track"><i style="width:${record.progress}%"></i></span><small>${record.progress}% · ${minutesLabel(record.estimateMinutes)}</small>` : `<b>${formatDate(record.updatedAt, true)}</b><small>${record.type === 'idea' ? 'Одна карточка во всех списках' : typeMeta[record.type].singular}</small>`}</span>
  </button>`;
}

function emptyState(text) {
  return `<div class="empty-state">${escapeHTML(text)}</div>`;
}

function bindOpenRecords() {
  $$('[data-open-record]').forEach((node) => node.addEventListener('click', () => openRecord(node.dataset.openRecord)));
  $$('[data-owner-filter]').forEach((node) => node.addEventListener('click', () => { state.view = 'task'; state.ownerFilter = node.dataset.ownerFilter; render(); }));
}

async function openRecord(id) {
  try {
    state.activeDetail = await api(`/api/records/${id}`);
    renderRecordDialog();
    $('#record-dialog').showModal();
  } catch (error) { toast(error.message, true); }
}

function renderRecordDialog() {
  const detail = state.activeDetail;
  const record = detail.record;
  const statuses = statusesByType[record.type] || statusesByType.default;
  const allLinkTargets = state.records.filter((item) => item.id !== record.id && item.status !== 'archived');
  const criteria = state.records.filter((item) => item.type === 'criterion' && item.status !== 'archived');
  const activity = state.activity.filter((item) => item.entityId === record.id);
  const ideaActions = record.type === 'idea' ? `<div class="idea-actions">${['review', 'main', 'rejected'].map((status) => `<button type="button" class="stage-action ${status}" data-stage="${status}" ${record.status === status ? 'disabled' : ''}>${statusLabels[status]}</button>`).join('')}</div>` : '';
  $('#record-dialog-content').innerHTML = `
    <div class="dialog-header"><div><span class="record-kind">${typeMeta[record.type].singular} · ${record.id.slice(0, 8)}</span><h2>${escapeHTML(record.title)}</h2><p>Создал ${escapeHTML(record.authorUsername)} · ${formatDate(record.createdAt, true)}</p></div><button type="button" class="close-button" data-close-dialog aria-label="Закрыть">×</button></div>
    ${ideaActions}
    <div class="dialog-layout">
      <div class="dialog-main">
        <form id="record-edit-form" class="card-form">
          <div class="form-grid two"><label>Название<input name="title" value="${escapeHTML(record.title)}" required></label><label>Статус<select name="status">${statuses.map((status) => `<option value="${status}" ${record.status === status ? 'selected' : ''}>${statusLabels[status]}</option>`).join('')}</select></label></div>
          <label>Описание<textarea name="description" rows="4">${escapeHTML(record.description)}</textarea></label>
          <div class="form-grid three"><label>Ответственный<select name="ownerId">${userOptions(record.ownerId)}</select></label><label>Принимает решение<select name="decisionMakerId"><option value="">Не указан</option>${userOptions(record.decisionMakerId)}</select></label><label>Срок<input name="dueAt" type="datetime-local" value="${toLocalInput(record.dueAt)}"></label></div>
          ${(record.type === 'task' || record.type === 'goal') ? `<div class="form-grid three"><label>Оценка, минут<input name="estimateMinutes" type="number" min="0" value="${record.estimateMinutes}"></label><label>Прогресс, %<input name="progress" type="number" min="0" max="100" value="${record.progress}"></label><label>Текущий статус работы<input name="progressNote" value="${escapeHTML(record.progressNote)}" placeholder="Что уже сделано"></label></div>` : ''}
          ${(record.type === 'task' || record.type === 'goal') ? `<label>Результат<textarea name="result" rows="3">${escapeHTML(record.result)}</textarea></label>` : ''}
          <label>Причина изменения статуса или срока<input name="reason" placeholder="Обязательно при изменении статуса или срока"></label>
          <div class="form-actions"><button type="submit" class="primary">Сохранить карточку</button><button type="button" class="secondary" id="notify-partners">Уведомить партнёра</button><button type="button" class="danger-text" id="archive-record">В архив</button></div>
        </form>
        <section class="accordion-stack">
          ${detail.sections.map(renderSection).join('')}
          <details class="accordion"><summary><span>Добавить свой раздел</span><small>Для этой карточки</small></summary><form id="custom-section-form" class="inline-editor"><input name="title" placeholder="Название раздела" required><textarea name="content" rows="4" placeholder="Содержание"></textarea><button class="secondary" type="submit">Добавить раздел</button></form></details>
          ${record.type !== 'criterion' ? renderCriteriaBlock(criteria, detail.scores) : ''}
          ${renderLinksBlock(detail.links, allLinkTargets)}
          ${record.type === 'task' ? renderProofBlock(record, detail.proofs) : ''}
          <details class="accordion"><summary><span>История карточки</span><small>${activity.length} событий</small></summary><div class="activity-list inside">${activity.map(renderActivityItem).join('') || emptyState('Изменений пока нет.')}</div></details>
        </section>
      </div>
      <aside class="dialog-aside">
        <div class="fact"><span>Ответственный</span><strong>${escapeHTML(record.ownerUsername)}</strong></div>
        <div class="fact"><span>Статус</span><strong>${escapeHTML(statusLabels[record.status])}</strong></div>
        <div class="fact"><span>Срок</span><strong class="deadline ${deadlineState(record).className}">${escapeHTML(deadlineState(record).label)}</strong></div>
        <div class="fact"><span>Изменено</span><strong>${formatDate(record.updatedAt, true)}</strong></div>
        ${record.type === 'task' ? `<div class="fact"><span>Доказательств</span><strong>${record.proofCount}</strong></div>` : ''}
      </aside>
    </div>`;
  bindRecordDialogEvents();
}

function userOptions(selected) {
  return state.users.map((user) => `<option value="${user.id}" ${Number(selected) === user.id ? 'selected' : ''}>${escapeHTML(user.username)}</option>`).join('');
}

function renderSection(section) {
  return `<details class="accordion"><summary><span>${escapeHTML(section.title)}</span><small>${section.content ? 'Заполнено' : 'Не заполнено'}</small></summary><form class="section-form inline-editor" data-section-id="${escapeHTML(section.id)}" data-definition-id="${escapeHTML(section.definitionId || '')}"><input name="title" value="${escapeHTML(section.title)}" ${section.definitionId ? 'readonly' : ''}><textarea name="content" rows="6" placeholder="Запишите факты, позиции и выводы">${escapeHTML(section.content)}</textarea><input name="reason" placeholder="Причина изменения (необязательно)"><button class="secondary" type="submit">Сохранить раздел</button></form></details>`;
}

function renderCriteriaBlock(criteria, scores) {
  const scoreMap = new Map(scores.map((score) => [score.criterionId, score]));
  return `<details class="accordion"><summary><span>Оценка по критериям</span><small>${scores.length} оценок</small></summary><div class="criteria-list">${criteria.map((criterion) => { const current = scoreMap.get(criterion.id); return `<form class="criterion-form" data-criterion-id="${criterion.id}"><div><strong>${escapeHTML(criterion.title)}</strong><small>${escapeHTML(criterion.description)}</small></div><input name="score" type="number" min="0" max="10" value="${current?.score ?? 0}" aria-label="Оценка"><input name="note" value="${escapeHTML(current?.note || '')}" placeholder="Комментарий"><button class="secondary" type="submit">Оценить</button></form>`; }).join('') || emptyState('Сначала создайте критерии в отдельном разделе.')}</div></details>`;
}

function renderLinksBlock(links, targets) {
  return `<details class="accordion"><summary><span>Связанные записи</span><small>${links.length} связей</small></summary><div class="linked-list">${links.map((link) => `<div class="linked-item"><button type="button" data-related-record="${link.record.id}"><i class="type-code">${typeMeta[link.record.type].code}</i><span><strong>${escapeHTML(link.record.title)}</strong><small>${escapeHTML(link.relationType)} · ${typeMeta[link.record.type].singular}</small></span></button><button type="button" class="remove-link" data-remove-link="${link.id}" aria-label="Убрать связь">×</button></div>`).join('') || emptyState('Связей пока нет.')}</div><form id="link-form" class="link-form"><select name="targetId" required><option value="">Выберите карточку</option>${targets.map((target) => `<option value="${target.id}">${typeMeta[target.type].singular}: ${escapeHTML(target.title)}</option>`).join('')}</select><input name="relationType" value="related" placeholder="Тип связи"><button class="secondary" type="submit">Связать</button></form></details>`;
}

function renderProofBlock(record, proofs) {
  return `<details class="accordion" open><summary><span>Доказательства выполнения</span><small>${proofs.length} приложено</small></summary><div class="proof-list">${proofs.map((proof) => `<article class="proof"><header><strong>${escapeHTML(proof.authorUsername)}</strong><time>${formatDate(proof.createdAt, true)}</time></header>${proof.kind === 'link' && /^https?:\/\//i.test(proof.content) ? `<a href="${escapeHTML(proof.content)}" target="_blank" rel="noreferrer">${escapeHTML(proof.content)}</a>` : `<p>${escapeHTML(proof.content).replace(/\n/g, '<br>')}</p>`}</article>`).join('') || emptyState('Ответственный должен приложить текст или ссылку до завершения задачи.')}</div>${record.ownerId === state.me.id ? `<form id="proof-form" class="proof-form"><select name="kind"><option value="text">Текст</option><option value="link">Ссылка</option></select><textarea name="content" rows="4" placeholder="Вопросы, цели, результат или ссылка на материал" required></textarea><button class="secondary" type="submit">Добавить доказательство</button></form><div class="completion-box"><label>Итог задачи<textarea id="completion-result" rows="3" placeholder="Кратко опишите полученный результат"></textarea></label><label class="check"><input id="notify-on-complete" type="checkbox" checked> Уведомить партнёра о выполнении</label><button type="button" class="success" id="complete-task" ${proofs.length ? '' : 'disabled'}>Завершить задачу</button></div>` : ''}</details>`;
}

function bindRecordDialogEvents() {
  const detail = state.activeDetail;
  const record = detail.record;
  $('[data-close-dialog]').addEventListener('click', () => $('#record-dialog').close());
  $('#record-edit-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const body = {};
    const compare = (key, next, previous) => { if (String(next ?? '') !== String(previous ?? '')) body[key] = next; };
    compare('title', form.get('title').trim(), record.title);
    compare('description', form.get('description').trim(), record.description);
    compare('status', form.get('status'), record.status);
    compare('ownerId', Number(form.get('ownerId')), record.ownerId);
    const decisionMaker = form.get('decisionMakerId');
    if (decisionMaker) compare('decisionMakerId', Number(decisionMaker), record.decisionMakerId);
    else if (record.decisionMakerId) body.clearDecisionMaker = true;
    const dueValue = form.get('dueAt');
    const dueISO = dueValue ? new Date(dueValue).toISOString() : '';
    compare('dueAt', dueISO, record.dueAt || '');
    if (form.has('estimateMinutes')) compare('estimateMinutes', Number(form.get('estimateMinutes')), record.estimateMinutes);
    if (form.has('progress')) compare('progress', Number(form.get('progress')), record.progress);
    if (form.has('progressNote')) compare('progressNote', form.get('progressNote').trim(), record.progressNote);
    if (form.has('result')) compare('result', form.get('result').trim(), record.result);
    body.reason = form.get('reason').trim();
    if (Object.keys(body).length === 1) return toast('Изменений нет');
    await mutateRecord(`/api/records/${record.id}`, { method: 'PATCH', body: JSON.stringify(body) });
  });
  $$('[data-stage]').forEach((button) => button.addEventListener('click', async () => {
    const reason = await askText({ title: 'Причина решения', label: `Почему идея переходит в статус «${statusLabels[button.dataset.stage]}»?`, required: true });
    if (reason === null) return;
    await mutateRecord(`/api/records/${record.id}`, { method: 'PATCH', body: JSON.stringify({ status: button.dataset.stage, reason }) });
  }));
  $('#notify-partners').addEventListener('click', async () => {
    const message = await askText({ title: 'Уведомить партнёра', label: 'Сообщение', defaultValue: `Посмотри карточку «${record.title}»`, required: true });
    if (message === null) return;
    try { await api(`/api/records/${record.id}/notify`, { method: 'POST', body: JSON.stringify({ message }) }); toast('Уведомление отправлено'); await loadData(true); } catch (error) { toast(error.message, true); }
  });
  $('#archive-record').addEventListener('click', async () => {
    const reason = await askText({ title: 'Перенести в архив', label: 'Почему карточка больше не активна?', required: true });
    if (!reason) return;
    await mutateRecord(`/api/records/${record.id}/archive`, { method: 'POST', body: JSON.stringify({ reason }) }, true);
  });
  $$('.section-form').forEach((formNode) => formNode.addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    await mutateDetail(`/api/records/${record.id}/sections`, { method: 'POST', body: JSON.stringify({ sectionId: event.currentTarget.dataset.sectionId, definitionId: event.currentTarget.dataset.definitionId || null, title: form.get('title'), content: form.get('content'), reason: form.get('reason') }) });
  }));
  $('#custom-section-form').addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/sections`, { method: 'POST', body: JSON.stringify({ title: form.get('title'), content: form.get('content') }) }); });
  $$('.criterion-form').forEach((formNode) => formNode.addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/criteria/${event.currentTarget.dataset.criterionId}`, { method: 'PUT', body: JSON.stringify({ score: Number(form.get('score')), note: form.get('note'), reason: '' }) }); }));
  $('#link-form').addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/links`, { method: 'POST', body: JSON.stringify({ targetId: form.get('targetId'), relationType: form.get('relationType') }) }); });
  $$('[data-remove-link]').forEach((button) => button.addEventListener('click', async () => { const reason = await askText({ title: 'Убрать связь', label: 'Почему связь больше не актуальна?', required: true }); if (!reason) return; await mutateDetail(`/api/records/${record.id}/links/${button.dataset.removeLink}/remove`, { method: 'POST', body: JSON.stringify({ reason }) }); }));
  $$('[data-related-record]').forEach((button) => button.addEventListener('click', () => openRecord(button.dataset.relatedRecord)));
  if ($('#proof-form')) $('#proof-form').addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/proofs`, { method: 'POST', body: JSON.stringify({ kind: form.get('kind'), content: form.get('content') }) }); });
  if ($('#complete-task')) $('#complete-task').addEventListener('click', async () => { await mutateRecord(`/api/records/${record.id}/complete`, { method: 'POST', body: JSON.stringify({ result: $('#completion-result').value, notifyPartners: $('#notify-on-complete').checked }) }); });
}

function askText({ title, label, defaultValue = '', required = false }) {
  const dialog = $('#reason-dialog');
  $('#reason-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">Фиксация решения</span><h2>${escapeHTML(title)}</h2></div><button type="button" class="close-button" data-cancel-reason aria-label="Закрыть">×</button></div><form id="reason-form" class="card-form dialog-form"><label>${escapeHTML(label)}<textarea name="value" rows="4" ${required ? 'required' : ''}>${escapeHTML(defaultValue)}</textarea></label><div class="form-actions"><button type="submit" class="primary">Подтвердить</button><button type="button" class="secondary" data-cancel-reason>Отмена</button></div></form>`;
  return new Promise((resolve) => {
    let settled = false;
    const finish = (value) => { if (settled) return; settled = true; dialog.close(); resolve(value); };
    $$('[data-cancel-reason]', dialog).forEach((button) => button.addEventListener('click', () => finish(null)));
    $('#reason-form').addEventListener('submit', (event) => { event.preventDefault(); const value = new FormData(event.currentTarget).get('value').trim(); if (required && !value) return; finish(value); });
    dialog.addEventListener('close', () => { if (!settled) { settled = true; resolve(null); } }, { once: true });
    dialog.showModal();
  });
}

async function mutateDetail(path, options) {
  try { await api(path, options); state.activeDetail = await api(`/api/records/${state.activeDetail.record.id}`); await loadData(true); renderRecordDialog(); toast('Сохранено'); } catch (error) { toast(error.message, true); }
}

async function mutateRecord(path, options, close = false) {
  try { await api(path, options); await loadData(true); if (close) $('#record-dialog').close(); else { state.activeDetail = await api(`/api/records/${state.activeDetail.record.id}`); renderRecordDialog(); } toast('Сохранено'); } catch (error) { toast(error.message, true); }
}

function openCreateDialog(initialType) {
  $('#create-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">Новая запись</span><h2>Создать карточку</h2><p>Запись сразу попадёт в нужный раздел.</p></div><button type="button" class="close-button" data-close-create>×</button></div><form id="create-record-form" class="card-form dialog-form"><div class="form-grid two"><label>Тип<select name="type">${Object.entries(typeMeta).map(([key, meta]) => `<option value="${key}" ${initialType === key ? 'selected' : ''}>${meta.singular}</option>`).join('')}</select></label><label>Ответственный<select name="ownerId">${userOptions(state.me.id)}</select></label></div><label>Название<input name="title" required maxlength="240" autofocus></label><label>Описание<textarea name="description" rows="5"></textarea></label><div class="form-grid two"><label>Срок<input name="dueAt" type="datetime-local"></label><label>Оценка времени, минут<input name="estimateMinutes" type="number" min="0" value="0"></label></div><div class="form-actions"><button type="submit" class="primary">Создать</button><button type="button" class="secondary" data-close-create>Отмена</button></div></form>`;
  $$('[data-close-create]').forEach((button) => button.addEventListener('click', () => $('#create-dialog').close()));
  $('#create-record-form').addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget); const due = form.get('dueAt');
    try {
      const record = await api('/api/records', { method: 'POST', body: JSON.stringify({ type: form.get('type'), title: form.get('title'), description: form.get('description'), ownerId: Number(form.get('ownerId')), dueAt: due ? new Date(due).toISOString() : '', estimateMinutes: Number(form.get('estimateMinutes')) }) });
      $('#create-dialog').close(); await loadData(true); toast('Карточка создана'); await openRecord(record.id);
    } catch (error) { toast(error.message, true); }
  });
  $('#create-dialog').showModal();
}

function actionLabel(action) {
  return ({ created: 'создал карточку', profile_updated: 'изменил профиль', updated: 'изменил карточку', archived: 'перенёс в архив', section_updated: 'обновил раздел', link_created: 'создал связь', link_removed: 'убрал связь', criterion_scored: 'оценил по критерию', proof_added: 'добавил доказательство', completed: 'завершил задачу', partners_notified: 'уведомил партнёра' }[action] || action);
}

function formatActivityValue(value) {
  if (value === null || value === undefined || value === '') return 'не указано';
  if (typeof value === 'object') return JSON.stringify(value);
  const text = String(value);
  return text.length > 140 ? `${text.slice(0, 137)}…` : text;
}

function activityDisplayValue(field, value) {
  if (field === 'status' && value) return statusLabels[value] || value;
  if ((field === 'ownerId' || field === 'decisionMakerId') && value) return state.users.find((user) => user.id === Number(value))?.username || value;
  if (field === 'dueAt' && value) return formatDate(value, true);
  if (field === 'estimateMinutes' && value !== null && value !== undefined) return minutesLabel(Number(value));
  if (field === 'progress' && value !== null && value !== undefined) return `${value}%`;
  return formatActivityValue(value);
}

function activityChanges(item) {
  const fieldLabels = { username: 'Логин', title: 'Название', description: 'Описание', status: 'Статус', ownerId: 'Ответственный', decisionMakerId: 'Принимает решение', dueAt: 'Срок', estimateMinutes: 'Оценка времени', progress: 'Прогресс', progressNote: 'Ход работы', result: 'Результат' };
  const changes = Object.entries(item.details || {}).filter(([, value]) => value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'before') && Object.prototype.hasOwnProperty.call(value, 'after'));
  if (!changes.length) return '';
  return changes.map(([field, value]) => `<span class="change-line"><b>${escapeHTML(fieldLabels[field] || field)}:</b> <del>${escapeHTML(activityDisplayValue(field, value.before))}</del><i>→</i><ins>${escapeHTML(activityDisplayValue(field, value.after))}</ins></span>`).join('');
}

function recordTitleByActivity(item) {
  return state.records.find((record) => record.id === item.entityId)?.title || item.details?.title || `${item.entityType} · ${item.entityId.slice(0, 8)}`;
}

function renderActivityItem(item) {
  return `<button type="button" class="activity-item" ${state.records.some((record) => record.id === item.entityId) ? `data-open-record="${item.entityId}"` : ''}><span class="avatar tiny">${escapeHTML(item.actorUsername.slice(0, 2).toUpperCase())}</span><span><strong>${escapeHTML(item.actorUsername)} ${escapeHTML(actionLabel(item.action))}</strong><small>${escapeHTML(recordTitleByActivity(item))}${item.reason ? ` · Причина: ${escapeHTML(item.reason)}` : ''}</small>${activityChanges(item)}</span><time>${formatDate(item.createdAt, true)}</time></button>`;
}

function renderHistory() {
  $('#main-content').innerHTML = `<div class="list-toolbar"><div><p class="eyebrow">Аудит</p><h3>Кто, когда и что изменил</h3></div><span class="record-total">${state.activity.length} событий</span></div><section class="section-panel"><div class="activity-list">${state.activity.map(renderActivityItem).join('') || emptyState('История пока пуста.')}</div></section>`;
  bindOpenRecords();
}

function renderTimeline() {
  const events = [
    ...state.activity.map((item) => ({ date: item.createdAt, kind: 'activity', item })),
    ...state.records.filter((record) => record.dueAt).map((record) => ({ date: record.dueAt, kind: 'deadline', record })),
  ].sort((a, b) => new Date(b.date) - new Date(a.date));
  $('#main-content').innerHTML = `<div class="timeline">${events.map((event) => event.kind === 'activity' ? `<div class="timeline-row"><time>${formatDate(event.date, true)}</time><i></i><div>${renderActivityItem(event.item)}</div></div>` : `<div class="timeline-row deadline-row"><time>${formatDate(event.date, true)}</time><i></i><div><button type="button" class="timeline-deadline" data-open-record="${event.record.id}"><span class="type-code">${typeMeta[event.record.type].code}</span><span><strong>Срок: ${escapeHTML(event.record.title)}</strong><small>${escapeHTML(event.record.ownerUsername)} · ${statusLabels[event.record.status]}</small></span></button></div></div>`).join('') || emptyState('Событий пока нет.')}</div>`;
  bindOpenRecords();
}

function renderStructure() {
  $('#main-content').innerHTML = `<section class="section-panel"><div class="section-heading"><div><p class="eyebrow">Универсальные пункты</p><h3>Структура карточек</h3></div></div><form id="definition-form" class="definition-form"><input name="name" placeholder="Название нового пункта" required><select name="scopeType"><option value="">Все типы карточек</option>${Object.entries(typeMeta).map(([key, meta]) => `<option value="${key}">${meta.label}</option>`).join('')}</select><select name="kind"><option value="universal">Универсальный</option><option value="template">Шаблонный</option></select><button class="primary" type="submit">Добавить</button></form><div class="definition-list">${state.definitions.map((definition) => `<div class="definition-row ${definition.active ? '' : 'inactive'}"><span><strong>${escapeHTML(definition.name)}</strong><small>${definition.scopeType ? typeMeta[definition.scopeType].label : 'Все карточки'} · ${definition.kind === 'universal' ? 'универсальный' : 'шаблонный'}</small></span><button type="button" class="secondary" data-toggle-definition="${definition.id}" data-active="${definition.active}">${definition.active ? 'Отключить' : 'Восстановить'}</button></div>`).join('')}</div></section>`;
  $('#definition-form').addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); try { await api('/api/section-definitions', { method: 'POST', body: JSON.stringify({ name: form.get('name'), scopeType: form.get('scopeType') || null, kind: form.get('kind') }) }); await loadData(true); toast('Пункт добавлен'); } catch (error) { toast(error.message, true); } });
  $$('[data-toggle-definition]').forEach((button) => button.addEventListener('click', async () => { try { await api(`/api/section-definitions/${button.dataset.toggleDefinition}`, { method: 'PATCH', body: JSON.stringify({ active: button.dataset.active !== 'true', reason: button.dataset.active === 'true' ? 'Пункт больше не используется в новых карточках' : 'Пункт снова нужен' }) }); await loadData(true); toast('Структура обновлена'); } catch (error) { toast(error.message, true); } }));
}

function renderNotifications() {
  $('#main-content').innerHTML = `<div class="list-toolbar"><div><p class="eyebrow">Личный кабинет</p><h3>Уведомления</h3></div><button type="button" class="secondary" id="read-all">Прочитать все</button></div><section class="section-panel"><div class="notification-list">${state.notifications.map((item) => `<button type="button" class="notification ${item.readAt ? '' : 'unread'}" data-notification-id="${item.id}" data-entity-id="${escapeHTML(item.entityId || '')}"><i></i><span><strong>${escapeHTML(item.title)}</strong><p>${escapeHTML(item.body)}</p><small>${formatDate(item.createdAt, true)}</small></span></button>`).join('') || emptyState('Уведомлений пока нет.')}</div></section>`;
  $('#read-all').addEventListener('click', async () => { await api('/api/notifications/read-all', { method: 'POST' }); await loadData(true); });
  $$('[data-notification-id]').forEach((button) => button.addEventListener('click', async () => { await api(`/api/notifications/${button.dataset.notificationId}/read`, { method: 'POST' }); if (button.dataset.entityId) await openRecord(button.dataset.entityId); await loadData(true); }));
}

bootstrap();
