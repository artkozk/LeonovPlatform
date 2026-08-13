const typeMeta = {
  goal: { label: 'Цели', singular: 'Цель', icon: 'target' },
  task: { label: 'Задачи', singular: 'Задача', icon: 'checkSquare' },
  question_set: { label: 'Вопросы', singular: 'Карточка вопросов', icon: 'messages' },
  idea: { label: 'Идеи', singular: 'Идея', icon: 'lightbulb' },
  criterion: { label: 'Критерии', singular: 'Критерий', icon: 'sliders' },
  research: { label: 'Исследования', singular: 'Исследование', icon: 'flask' },
  decision: { label: 'Решения', singular: 'Решение', icon: 'scale' },
  disagreement: { label: 'Разногласия', singular: 'Разногласие', icon: 'gitCompare' },
  document: { label: 'Документы', singular: 'Документ', icon: 'fileText' },
  meeting: { label: 'Встречи', singular: 'Встреча', icon: 'calendar' },
};

const iconPaths = {
  dashboard: '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  checkSquare: '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="m9 12 2 2 4-4"/>',
  messages: '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/><path d="M8 9h8M8 13h5"/>',
  lightbulb: '<path d="M9 18h6M10 22h4"/><path d="M8.3 14.5A7 7 0 1 1 15.7 14.5c-.9.7-1.2 1.4-1.2 2.5h-5c0-1.1-.3-1.8-1.2-2.5Z"/>',
  sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3"/><path d="M1 14h6M9 8h6M17 16h6"/>',
  flask: '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M7.5 15h9"/>',
  scale: '<path d="m16 16 3-8 3 8a5 5 0 0 1-6 0ZM2 16l3-8 3 8a5 5 0 0 1-6 0ZM7 21h10M12 3v18M3 7h18"/>',
  gitCompare: '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7M11 18H8a2 2 0 0 1-2-2V9"/>',
  fileText: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  x: '<path d="m18 6-12 12M6 6l12 12"/>',
  chevronRight: '<path d="m9 18 6-6-6-6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
  archive: '<path d="M21 8v13H3V8M1 3h22v5H1zM10 12h4"/>',
  send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  link: '<path d="M10 13a5 5 0 0 0 7.1.1l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1"/><path d="M14 11a5 5 0 0 0-7.1-.1l-2 2A5 5 0 0 0 12 20l1.1-1.1"/>',
  edit: '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.6 2.6 0 0 1 5 1c0 2-2.5 2-2.5 4M12 18h.01"/>',
  calendar: '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
  bookOpen: '<path d="M2 3h6a4 4 0 0 1 4 4v14a4 4 0 0 0-4-4H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a4 4 0 0 1 4-4h6z"/>',
};

function icon(name, className = '') {
  return `<svg class="icon ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.help}</svg>`;
}

const statusLabels = {
  draft: 'Черновик', inbox: 'Все идеи', review: 'На рассмотрении', main: 'Главная идея',
  rejected: 'Отклонено', planned: 'Не начато', in_progress: 'В работе', blocked: 'Заблокировано',
  completed: 'Выполнено', postponed: 'Перенесено', cancelled: 'Отменено', archived: 'Архив',
};

const statusesByType = {
  idea: ['inbox', 'review', 'main', 'rejected'],
  goal: ['planned', 'in_progress', 'blocked', 'completed', 'postponed', 'cancelled'],
  task: ['planned', 'in_progress', 'blocked', 'postponed', 'completed', 'cancelled'],
  question_set: ['planned', 'in_progress', 'blocked', 'completed', 'postponed', 'cancelled'],
  meeting: ['planned', 'in_progress', 'completed', 'postponed', 'cancelled'],
  default: ['draft', 'in_progress', 'completed', 'cancelled'],
};

const navItems = [
  ['dashboard', 'Обзор', 'dashboard', 'Работа'], ['task', 'Задачи', 'checkSquare', 'Работа'],
  ['question_set', 'Вопросы', 'messages', 'Работа'], ['meeting', 'Встречи', 'calendar', 'Работа'],
  ['principles', 'Правила и критерии', 'bookOpen', 'Основа'], ['goal', 'Цели', 'target', 'Бизнес'],
  ['idea', 'Идеи', 'lightbulb', 'Бизнес'], ['research', 'Исследования', 'flask', 'Бизнес'],
  ['decision', 'Решения', 'scale', 'Бизнес'], ['disagreement', 'Разногласия', 'gitCompare', 'Бизнес'],
  ['document', 'Документы', 'fileText', 'Бизнес'], ['history', 'История', 'history', 'Контроль'],
  ['structure', 'Шаблоны карточек', 'settings', 'Настройки'],
];

const state = {
  me: null, users: [], records: [], notifications: [], activity: [], definitions: [], pendingQuestions: [],
  view: 'dashboard', search: '', statusFilter: '', ownerFilter: '', authMode: 'login', activeDetail: null,
  activeRecordTab: 'overview', activeActivity: null, historyMode: 'feed', activeRecordRequest: 0,
  detailCache: new Map(), detailRequests: new Map(),
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

function normalizedInstant(value) {
  if (!value) return '';
  const time = new Date(value).getTime();
  return Number.isNaN(time) ? String(value) : String(time);
}

function recordDraftKey(recordId) {
  return `business-control:draft:${state.me?.id || 'anonymous'}:${recordId}`;
}

function loadRecordDraft(recordId) {
  try { return JSON.parse(localStorage.getItem(recordDraftKey(recordId)) || 'null'); } catch (_) { return null; }
}

function saveRecordDraft(recordId, values) {
  try { localStorage.setItem(recordDraftKey(recordId), JSON.stringify({ values, savedAt: new Date().toISOString() })); } catch (_) {}
}

function clearRecordDraft(recordId) {
  try { localStorage.removeItem(recordDraftKey(recordId)); } catch (_) {}
}

function recordFormValues(form) {
  const data = new FormData(form);
  return Object.fromEntries([...data.entries()].map(([key, value]) => [key, String(value)]));
}

function applyRecordDraft(form, draft) {
  Object.entries(draft?.values || {}).forEach(([name, value]) => {
    const field = form.elements.namedItem(name);
    if (field && name !== 'reason') field.value = value;
  });
  updateRecordFormState(form, state.activeDetail.record, true);
}

function minutesLabel(minutes) {
  if (!minutes) return 'Не оценено';
  if (minutes < 60) return `${minutes} мин`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} ч ${rest} мин` : `${hours} ч`;
}

function recordsCountLabel(count) {
  const mod100 = count % 100;
  const mod10 = count % 10;
  if (mod10 === 1 && mod100 !== 11) return `${count} запись`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} записи`;
  return `${count} записей`;
}

function discussionsCountLabel(count) {
  const mod100 = count % 100;
  const mod10 = count % 10;
  if (mod10 === 1 && mod100 !== 11) return `${count} обсуждения`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} обсуждений`;
  return `${count} обсуждений`;
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
    const error = new Error(data.error || 'Ошибка запроса');
    error.status = response.status;
    throw error;
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
    maybeShowOnboarding();
  } catch (error) {
    showAuth();
  }
}

async function loadData(silent = false) {
  if (!silent) $('#sync-state').textContent = 'Обновление…';
  const [users, records, notifications, activity, definitions, pendingQuestions] = await Promise.all([
    api('/api/users'), api('/api/records?includeArchived=true'), api('/api/notifications'),
    api('/api/activity'), api('/api/section-definitions'), api('/api/questions/pending'),
  ]);
  const projectActivity = activity.filter((item) => typeMeta[item.entityType] || item.entityType === 'section_definition');
  const recordsByID = new Map(records.map((record) => [record.id, record]));
  state.detailCache.forEach((detail, id) => {
    const current = recordsByID.get(id);
    if (!current || current.updatedAt !== detail.record.updatedAt) state.detailCache.delete(id);
  });
  Object.assign(state, { users, records, notifications, activity: projectActivity, definitions, pendingQuestions });
  $('#sync-state').textContent = 'На связи';
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
  $('#new-record-button').addEventListener('click', (event) => { event.stopPropagation(); toggleCreateMenu(); });
  $('#notification-button').addEventListener('click', () => { state.view = 'notifications'; render(); });
  $('#onboarding-button').addEventListener('click', () => openOnboarding(0));
  document.addEventListener('click', (event) => { if (!event.target.closest('.create-control')) $('#create-menu').hidden = true; });
  $('#menu-button').addEventListener('click', () => $('.sidebar').classList.toggle('open'));
  $('#record-dialog').addEventListener('click', (event) => { if (event.target === $('#record-dialog')) $('#record-dialog').close(); });
  $('#event-dialog').addEventListener('click', (event) => { if (event.target === $('#event-dialog')) $('#event-dialog').close(); });
  $('#create-dialog').addEventListener('click', (event) => { if (event.target === $('#create-dialog')) $('#create-dialog').close(); });
  $('#reason-dialog').addEventListener('click', (event) => { if (event.target === $('#reason-dialog')) $('#reason-dialog').close('cancel'); });
  $('#onboarding-dialog').addEventListener('click', (event) => { if (event.target === $('#onboarding-dialog')) finishOnboarding(); });
  setInterval(async () => {
    if (!state.me) return;
    try {
      state.notifications = await api('/api/notifications');
      renderNav();
      renderNotificationBadge();
      if (state.view === 'notifications') renderContent();
    } catch (_) {}
  }, 30000);
}

function setAuthMode(mode) {
  state.authMode = mode;
  $$('[data-auth-mode]').forEach((button) => button.classList.toggle('active', button.dataset.authMode === mode));
  $('#auth-heading-title').textContent = mode === 'register' ? 'Создайте аккаунт' : 'Войдите в проект';
  $('#auth-heading-copy').textContent = mode === 'register' ? 'Регистрация займёт меньше минуты, подтверждение почты не требуется.' : 'Продолжите работу с того места, где остановились.';
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
    maybeShowOnboarding();
  } catch (error) {
    $('#auth-error').textContent = error.message;
  }
}

function render() {
  renderNav();
  renderNotificationBadge();
  renderContent();
}

function renderNotificationBadge() {
  const unread = state.notifications.filter((item) => !item.readAt).length;
  const badge = $('#notification-badge');
  badge.textContent = unread > 99 ? '99+' : String(unread);
  badge.hidden = unread === 0;
}

function renderNav() {
  let group = '';
  $('#main-nav').innerHTML = navItems.map(([key, label, iconName, itemGroup]) => {
    const count = typeMeta[key] ? state.records.filter((record) => record.type === key && record.status !== 'archived').length : '';
    const groupLabel = group !== itemGroup ? `<p class="nav-group">${escapeHTML(itemGroup)}</p>` : '';
    group = itemGroup;
    return `${groupLabel}<button type="button" class="nav-item ${state.view === key ? 'active' : ''}" data-view="${key}" title="${escapeHTML(label)}">${icon(iconName)}<span>${escapeHTML(label)}</span>${count !== '' ? `<b>${count}</b>` : ''}</button>`;
  }).join('');
  $$('[data-view]', $('#main-nav')).forEach((button) => button.addEventListener('click', () => {
    state.view = button.dataset.view; state.statusFilter = ''; state.search = ''; state.ownerFilter = '';
    $('.sidebar').classList.remove('open'); render();
  }));
}

function renderContent() {
  const titles = Object.fromEntries(navItems);
  $('#page-title').textContent = titles[state.view] || (state.view === 'notifications' ? 'Уведомления' : 'Обзор');
  if (state.view === 'dashboard') return renderDashboard();
  if (typeMeta[state.view]) return renderRecordList(state.view);
  if (state.view === 'history') return renderHistory();
  if (state.view === 'principles') return renderPrinciples();
  if (state.view === 'structure') return renderStructure();
  if (state.view === 'notifications') return renderNotifications();
}

function renderDashboard() {
  const active = state.records.filter((record) => !['completed', 'cancelled', 'archived', 'rejected'].includes(record.status));
  const tasks = active.filter((record) => record.type === 'task');
  const overdue = tasks.filter((record) => deadlineState(record).className === 'overdue');
  const myTasks = tasks.filter((record) => record.ownerId === state.me.id);
  const attention = myTasks.filter((record) => ['overdue', 'urgent'].includes(deadlineState(record).className));
  const focusTasks = myTasks.slice().sort((a, b) => {
    const priority = { overdue: 0, urgent: 1, soon: 2, normal: 3, none: 4, done: 5 };
    return priority[deadlineState(a).className] - priority[deadlineState(b).className] || sortByDeadline(a, b);
  }).slice(0, 4);
  const urgentFocus = focusTasks.filter((record) => ['overdue', 'urgent'].includes(deadlineState(record).className));
  const regularFocus = focusTasks.filter((record) => !['overdue', 'urgent'].includes(deadlineState(record).className));
  const focusItems = [
    ...urgentFocus.map((record) => ({ kind: 'task', record })),
    ...state.pendingQuestions.map((question) => ({ kind: 'question', question })),
    ...regularFocus.map((record) => ({ kind: 'task', record })),
  ].slice(0, 4);
  $('#main-content').innerHTML = `
    <section class="project-brief">
      <div><p class="eyebrow">${formatDate(new Date().toISOString())} · рабочая очередь</p><h1>${attention.length ? `${attention.length} ${attention.length === 1 ? 'задача требует' : 'задачи требуют'} внимания` : `Следующее важное действие`}</h1><p>${attention.length ? 'Начните с просроченных и срочных обязательств.' : 'Ответьте на открытый вопрос или продолжите ближайшую задачу.'}</p></div>
    </section>
    <section class="workbench-grid">
      <article class="focus-panel">
        <div class="section-heading inverse"><div><p class="eyebrow">Требует действия</p><h2>Рабочая очередь</h2></div><button class="text-button" data-go="task">Задачи ${icon('chevronRight')}</button></div>
        <div class="focus-list">${focusItems.length ? focusItems.map((item, index) => item.kind === 'task' ? renderFocusRecord(item.record, index === 0) : renderFocusQuestion(item.question, index === 0)).join('') : `<div class="focus-empty">${icon('check')}<strong>Срочных задач и вопросов нет</strong><span>Можно зафиксировать следующий шаг.</span></div>`}</div>
      </article>
      <aside class="capture-panel">
        <div><p class="eyebrow">Создать</p><h3>Быстрая фиксация</h3></div>
        <div class="quick-actions"><button type="button" class="quick-action idea" data-quick-create="idea"><span class="quick-icon">${icon('lightbulb')}</span><span><strong>Идея</strong><small>Название, детали позже</small></span>${icon('chevronRight')}</button><button type="button" class="quick-action task" data-quick-create="task"><span class="quick-icon">${icon('checkSquare')}</span><span><strong>Задача</strong><small>Кто, что и когда</small></span>${icon('chevronRight')}</button><button type="button" class="quick-action discussion" data-quick-create="meeting"><span class="quick-icon">${icon('calendar')}</span><span><strong>Встреча</strong><small>Заметки и результаты</small></span>${icon('chevronRight')}</button><button type="button" class="quick-action discussion" data-quick-create="question_set"><span class="quick-icon">${icon('messages')}</span><span><strong>Вопросы</strong><small>Два ответа и итог</small></span>${icon('chevronRight')}</button></div>
      </aside>
    </section>
    <section class="dashboard-grid">
      <div class="section-panel">
        <div class="section-heading"><div><p class="eyebrow">Команда</p><h3>Распределение работы</h3></div><span class="panel-note">${minutesLabel(tasks.reduce((sum, task) => sum + task.estimateMinutes, 0))} в плане</span></div>
        <div class="people-load">${state.users.map((user) => renderPersonLoad(user, tasks)).join('') || emptyState('Второй участник появится после регистрации.')}</div>
      </div>
      <div class="section-panel">
        <div class="section-heading"><div><p class="eyebrow">Командный радар</p><h3>Ближайшие сроки</h3></div><button class="text-button" data-go="task">Открыть список</button></div>
        <div class="compact-list">${tasks.slice().sort(sortByDeadline).slice(0, 7).map(renderCompactRecord).join('') || emptyState('Активных задач пока нет.')}</div>
      </div>
    </section>`;
  bindOpenRecords();
  $$('[data-quick-create]').forEach((button) => button.addEventListener('click', () => openCreateDialog(button.dataset.quickCreate)));
  $$('[data-go]').forEach((button) => button.addEventListener('click', () => { navigateToView(button.dataset.go); }));
}

function navigateToView(view, options = {}) {
  state.view = view;
  state.statusFilter = options.status || '';
  state.search = options.search || '';
  state.ownerFilter = options.ownerId ? String(options.ownerId) : '';
  render();
}

function metric(label, value, note, tone = '', iconName = 'dashboard') {
  return `<div class="metric ${tone}"><span class="metric-icon">${icon(iconName)}</span><span>${escapeHTML(label)}</span><strong>${value}</strong><small>${escapeHTML(note)}</small></div>`;
}

function renderFocusRecord(record, primary = false) {
  const deadline = deadlineState(record);
  return `<button type="button" class="focus-record ${primary ? 'primary-focus' : ''}" data-open-record="${record.id}"><span class="focus-marker">${icon('checkSquare')}</span><span class="focus-copy"><small>${primary ? 'Следующая задача' : escapeHTML(record.ownerUsername)}</small><strong>${escapeHTML(record.title)}</strong><em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em></span><span class="focus-progress"><b>${record.progress}%</b><progress class="focus-meter" max="100" value="${record.progress}"></progress></span>${icon('chevronRight', 'row-chevron')}</button>`;
}

function renderFocusQuestion(question, primary = false) {
  const deadline = question.dueAt ? formatDate(question.dueAt) : 'Без срока';
  return `<button type="button" class="focus-record focus-question ${primary ? 'primary-focus' : ''}" data-open-record="${question.recordId}"><span class="focus-marker">${icon('messages')}</span><span class="focus-copy"><small>Ждёт вашего ответа · ${escapeHTML(question.recordTitle)}</small><strong>${escapeHTML(question.body)}</strong><em class="deadline normal">${escapeHTML(deadline)}</em></span><span class="focus-progress"><b>Ответить</b><progress class="focus-meter" max="100" value="0"></progress></span>${icon('chevronRight', 'row-chevron')}</button>`;
}

function renderPersonLoad(user, tasks) {
  const owned = tasks.filter((task) => task.ownerId === user.id);
  const minutes = owned.reduce((sum, task) => sum + task.estimateMinutes, 0);
  const progress = owned.length ? Math.round(owned.reduce((sum, task) => sum + task.progress, 0) / owned.length) : 0;
  return `<button type="button" class="person-load" data-owner-filter="${user.id}"><span class="avatar">${escapeHTML(user.username.slice(0, 2).toUpperCase())}</span><span class="person-main"><strong>${escapeHTML(user.username)}</strong><small>${owned.length} задач · ${minutesLabel(minutes)}</small><progress class="progress-track" max="100" value="${progress}"></progress></span><b>${progress}%</b></button>`;
}

function renderPrinciples() {
  const groups = [
    { kind: 'preference', title: 'Что нам подходит', copy: 'Положительные критерии выбора сфер и идей.', icon: 'target' },
    { kind: 'limitation', title: 'Чего избегаем', copy: 'Ограничения, которые идея не должна нарушать.', icon: 'archive' },
    { kind: 'rule', title: 'Как принимаем решения', copy: 'Договорённости, к которым возвращаемся при разногласиях.', icon: 'scale' },
  ];
  const records = state.records.filter((record) => (['preference', 'limitation', 'rule'].includes(record.kind) || (record.type === 'criterion' && !record.kind)) && record.status !== 'archived');
  $('#main-content').innerHTML = `<div class="page-heading"><div><p class="eyebrow">Основа отбора</p><h1>Правила и критерии</h1><p>Рабочие выводы, которые влияют на выбор идей и совместные решения.</p></div></div><div class="principle-grid">${groups.map((group) => {
    const items = records.filter((record) => record.kind === group.kind || (group.kind === 'preference' && record.type === 'criterion' && !record.kind));
    return `<section class="principle-column"><header><span class="type-icon">${icon(group.icon)}</span><div><h3>${group.title}</h3><p>${group.copy}</p></div><b>${items.length}</b></header><div class="principle-list">${items.map((record) => `<button type="button" data-open-record="${record.id}"><strong>${escapeHTML(record.title)}</strong><span>${escapeHTML(record.description || 'Без пояснения')}</span>${icon('chevronRight')}</button>`).join('') || emptyState('Пока ничего не зафиксировано.')}</div><button type="button" class="text-button principle-add" data-create-principle="${group.kind}">${icon('plus')} Добавить</button></section>`;
  }).join('')}</div>`;
  bindOpenRecords();
  $$('[data-create-principle]').forEach((button) => button.addEventListener('click', () => openCreateDialog(button.dataset.createPrinciple === 'rule' ? 'decision' : 'criterion', { kind: button.dataset.createPrinciple })));
}

function sortByDeadline(a, b) {
  if (!a.dueAt) return 1;
  if (!b.dueAt) return -1;
  return new Date(a.dueAt) - new Date(b.dueAt);
}

function renderCompactRecord(record) {
  const deadline = deadlineState(record);
  return `<button type="button" class="compact-record" data-open-record="${record.id}"><span class="type-icon type-${record.type}">${icon(typeMeta[record.type].icon)}</span><span><strong>${escapeHTML(record.title)}</strong><small>${escapeHTML(record.ownerUsername)} · ${minutesLabel(record.estimateMinutes)}</small></span><em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em>${icon('chevronRight', 'row-chevron')}</button>`;
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
      <select id="owner-filter" aria-label="${type === 'question_set' ? 'Координатор' : type === 'meeting' ? 'Организатор' : 'Ответственный'}"><option value="">${type === 'question_set' ? 'Все координаторы' : type === 'meeting' ? 'Все организаторы' : 'Все ответственные'}</option>${state.users.map((user) => `<option value="${user.id}" ${state.ownerFilter === String(user.id) ? 'selected' : ''}>${escapeHTML(user.username)}</option>`).join('')}</select>
      <span class="record-total">${recordsCountLabel(records.length)}</span>
    </div>
    <div class="status-tabs">${statusTabs.map((status) => `<button type="button" data-status-filter="${status === 'all' ? '' : status}" class="${state.statusFilter === (status === 'all' ? '' : status) ? 'active' : ''}">${status === 'all' ? 'Все' : statusLabels[status]}</button>`).join('')}</div>
    <section class="table-panel">
      <div class="record-table header ${['task', 'goal', 'question_set', 'meeting'].includes(type) ? '' : 'simple'}"><span>Карточка</span><span>${type === 'question_set' ? 'Координатор' : type === 'meeting' ? 'Организатор' : 'Ответственный'}</span><span>Статус</span><span>${['task', 'goal', 'question_set', 'meeting'].includes(type) ? 'Дата / прогресс' : 'Изменено'}</span></div>
      <div class="record-rows">${records.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)).map(renderRecordRow).join('') || emptyState('Карточек в этом представлении пока нет.')}</div>
    </section>`;
  $('#record-search').addEventListener('input', (event) => { state.search = event.target.value; renderRecordList(type); });
  $('#owner-filter').addEventListener('change', (event) => { state.ownerFilter = event.target.value; renderRecordList(type); });
  $$('[data-status-filter]').forEach((button) => button.addEventListener('click', () => { state.statusFilter = button.dataset.statusFilter; renderRecordList(type); }));
  bindOpenRecords();
}

function renderRecordRow(record) {
  const isPlannable = ['task', 'goal', 'question_set', 'meeting'].includes(record.type);
  const deadline = deadlineState(record);
  return `<button type="button" class="record-table row ${isPlannable ? '' : 'simple'}" data-open-record="${record.id}">
    <span class="record-title"><i class="type-icon type-${record.type}">${icon(typeMeta[record.type].icon)}</i><span><strong>${escapeHTML(record.title)}</strong><small>${escapeHTML(record.description || 'Без описания')}</small></span></span>
    <span><b class="owner-chip">${escapeHTML(record.ownerUsername)}</b><small>создал ${escapeHTML(record.authorUsername)}</small></span>
    <span><em class="status status-${record.status}">${escapeHTML(statusLabels[record.status] || record.status)}</em></span>
    <span>${isPlannable ? `<em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em><progress class="progress-track" max="100" value="${record.progress}"></progress><small>${record.progress}% · ${minutesLabel(record.estimateMinutes)}</small>` : `<b>${formatDate(record.updatedAt, true)}</b><small>${record.type === 'idea' ? 'Одна карточка во всех списках' : typeMeta[record.type].singular}</small>`}</span>
  </button>`;
}

function emptyState(text) {
  return `<div class="empty-state">${escapeHTML(text)}</div>`;
}

function bindOpenRecords() {
  $$('[data-open-record]').forEach((node) => {
    node.addEventListener('click', () => openRecord(node.dataset.openRecord));
    node.addEventListener('pointerenter', () => prefetchRecord(node.dataset.openRecord), { once: true });
    node.addEventListener('focus', () => prefetchRecord(node.dataset.openRecord), { once: true });
  });
  $$('[data-open-event]').forEach((node) => node.addEventListener('click', () => openActivity(node.dataset.openEvent)));
  $$('[data-owner-filter]').forEach((node) => node.addEventListener('click', () => navigateToView('task', { ownerId: node.dataset.ownerFilter })));
}

function cachedRecordDetail(id) {
  const detail = state.detailCache.get(id);
  const summary = state.records.find((record) => record.id === id);
  if (!detail || (summary && summary.updatedAt !== detail.record.updatedAt)) return null;
  return detail;
}

async function fetchRecordDetail(id, force = false) {
  if (!force) {
    const cached = cachedRecordDetail(id);
    if (cached) return cached;
  }
  if (state.detailRequests.has(id)) return state.detailRequests.get(id);
  const request = api(`/api/records/${id}`).then((detail) => {
    const previous = state.detailCache.get(id);
    if (previous?.relationsLoaded && previous.record.updatedAt === detail.record.updatedAt) {
      detail.links = previous.links;
      detail.scores = previous.scores;
      detail.relationsLoaded = true;
    }
    state.detailCache.set(id, detail);
    return detail;
  }).finally(() => state.detailRequests.delete(id));
  state.detailRequests.set(id, request);
  return request;
}

function prefetchRecord(id) {
  if (!cachedRecordDetail(id) && !state.detailRequests.has(id)) fetchRecordDetail(id).catch(() => {});
}

async function openRecord(id) {
  const requestID = ++state.activeRecordRequest;
  const cached = cachedRecordDetail(id);
  const summary = state.records.find((record) => record.id === id);
  state.activeRecordTab = (cached?.record.type || summary?.type) === 'question_set' ? 'questions' : 'overview';
  if (cached) {
    state.activeDetail = cached;
    renderRecordDialog();
  } else {
    state.activeDetail = null;
    renderRecordLoading(summary);
  }
  if (!$('#record-dialog').open) $('#record-dialog').showModal();
  try {
    const detail = await fetchRecordDetail(id, Boolean(cached));
    if (requestID !== state.activeRecordRequest || !$('#record-dialog').open) return;
    state.activeDetail = detail;
    renderRecordDialog();
  } catch (error) {
    if (requestID === state.activeRecordRequest) renderRecordLoadError(id, error.message);
  }
}

function renderRecordLoading(summary) {
  const meta = typeMeta[summary?.type] || { singular: 'Карточка', icon: 'fileText' };
  $('#record-dialog-content').innerHTML = `<div class="record-shell record-type-${summary?.type || 'document'} loading-shell"><div class="dialog-header record-dialog-header"><div><span class="record-kind">${icon(meta.icon)} ${escapeHTML(meta.singular)}</span><h2>${escapeHTML(summary?.title || 'Загружаем карточку')}</h2><p>Основные данные появятся сразу после ответа сервера</p></div><button type="button" class="close-button icon-button" data-close-dialog aria-label="Закрыть">${icon('x')}</button></div><div class="loading-tabs"><i></i><i></i><i></i></div><div class="dialog-layout"><div class="dialog-main"><div class="record-skeleton"><span class="skeleton-line wide"></span><span class="skeleton-line medium"></span><span class="skeleton-block"></span><div><span class="skeleton-line"></span><span class="skeleton-line short"></span></div></div></div><aside class="dialog-aside"><span class="skeleton-line"></span><span class="skeleton-line short"></span><span class="skeleton-line"></span></aside></div></div>`;
  $('[data-close-dialog]').addEventListener('click', () => $('#record-dialog').close());
}

function renderRecordLoadError(id, message) {
  $('#record-dialog-content').innerHTML = `<div class="record-load-error">${icon('help')}<h2>Карточка не загрузилась</h2><p>${escapeHTML(message)}</p><div><button type="button" class="primary" data-retry-record="${id}">Повторить</button><button type="button" class="secondary" data-close-dialog>Закрыть</button></div></div>`;
  $('[data-retry-record]').addEventListener('click', () => openRecord(id));
  $('[data-close-dialog]').addEventListener('click', () => $('#record-dialog').close());
}

function recordTabs(record, detail, activity) {
  const filledSections = detail.sections.filter((section) => section.content).length;
  const tabs = [
    ['overview', 'Обзор', ''],
    ['content', 'Содержание', `${filledSections}/${detail.sections.length}`],
    ['relations', record.type === 'idea' ? 'Критерии и связи' : 'Связи', detail.relationsLoaded ? `${detail.links.length}` : ''],
    ['history', 'История', `${activity.length}`],
  ];
  if (record.type === 'question_set') {
    const workflow = detail.questionWorkflow || { questions: [], resolved: 0 };
    tabs.unshift(['questions', 'Вопросы и ответы', `${workflow.resolved}/${workflow.questions.length}`]);
    tabs.splice(2, 1);
  }
  return tabs.map(([key, label, count]) => `<button type="button" class="record-tab ${state.activeRecordTab === key ? 'active' : ''}" data-record-tab="${key}"><span>${label}</span>${count ? `<b>${count}</b>` : ''}</button>`).join('');
}

function renderRecordOverview(record, statuses) {
  const draft = loadRecordDraft(record.id);
  const language = {
    task: { description: 'Контекст и условия готовности', owner: 'Исполнитель' },
    goal: { description: 'Какой результат должен быть достигнут', owner: 'Владелец цели' },
    question_set: { description: 'Контекст обсуждения', owner: 'Координатор' },
    idea: { description: 'Краткая гипотеза или суть мысли', owner: 'Куратор' },
    criterion: { description: 'Что означает критерий и как его оценивать', owner: 'Владелец критерия' },
    research: { description: 'Исследовательский вопрос и ожидаемый вывод', owner: 'Исследователь' },
    decision: { description: 'Какой вопрос решаем и какие варианты рассмотрены', owner: 'Ответственный' },
    disagreement: { description: 'Предмет разногласия и контекст', owner: 'Координатор' },
    document: { description: 'Краткое содержание документа', owner: 'Владелец' },
    meeting: { description: 'Повестка, заметки и договорённости', owner: 'Организатор' },
  }[record.type];
  const hasDeadline = ['task', 'goal', 'question_set', 'research', 'decision', 'disagreement', 'meeting'].includes(record.type);
  const hasDecisionMaker = ['decision', 'disagreement'].includes(record.type);
  const hasWork = ['task', 'goal'].includes(record.type);
  const planningTitle = record.type === 'task' ? 'Исполнение' : record.type === 'meeting' ? 'Организатор и время' : hasDecisionMaker ? 'Ответственность за решение' : hasDeadline ? 'Планирование' : 'Владелец карточки';
  const dueLabel = ({ meeting: 'Дата и время', research: 'Срок исследования', decision: 'Срок решения', disagreement: 'Срок разбора' })[record.type] || 'Срок';
  const planningGrid = hasDecisionMaker && hasDeadline ? 'three' : hasDeadline ? 'two' : 'one';
  const origin = state.activeDetail.derivation;
  return `<div class="record-pane ${state.activeRecordTab === 'overview' ? 'active' : ''}" data-record-pane="overview">
    ${origin ? `<button type="button" class="origin-trace" data-related-record="${origin.sourceRecordId}"><span>${icon('link')}</span><span><small>Создано из совместного вывода</small><strong>${escapeHTML(origin.questionBody)}</strong><em>${escapeHTML(origin.decisionContent)}</em></span>${icon('chevronRight')}</button>` : ''}
    ${draft ? `<div class="draft-banner"><span><strong>Найден несохранённый черновик</strong><small>Можно восстановить текст или удалить черновик.</small></span><div><button type="button" class="secondary" data-restore-draft>Восстановить</button><button type="button" class="text-button" data-discard-draft>Удалить</button></div></div>` : ''}
    <form id="record-edit-form" class="card-form record-overview-form">
      <div class="form-grid two"><label>Название<input name="title" value="${escapeHTML(record.title)}" required></label><label>${record.type === 'question_set' ? 'Статус рассчитывается автоматически' : 'Статус'}<select name="status" ${record.type === 'question_set' ? 'disabled' : ''}>${statuses.map((status) => `<option value="${status}" ${record.status === status ? 'selected' : ''}>${statusLabels[status]}</option>`).join('')}</select></label></div>
      <label>${language.description}<textarea name="description" rows="5">${escapeHTML(record.description)}</textarea></label>
      <details class="form-more" ${['task', 'meeting'].includes(record.type) ? 'open' : ''}><summary>${planningTitle}</summary><div class="form-more-body">
        <div class="form-grid ${planningGrid}"><label>${language.owner}<select name="ownerId">${userOptions(record.ownerId)}</select></label>${hasDecisionMaker ? `<label>Принимает решение<select name="decisionMakerId"><option value="">Не указан</option>${userOptions(record.decisionMakerId)}</select></label>` : ''}${hasDeadline ? `<label>${dueLabel}<input name="dueAt" type="datetime-local" value="${toLocalInput(record.dueAt)}"></label>` : ''}</div>
        ${hasWork ? `<div class="form-grid three"><label>Плановая оценка, минут<input name="estimateMinutes" type="number" min="0" value="${record.estimateMinutes}"></label><label>Прогресс, %<input name="progress" type="number" min="0" max="100" value="${record.progress}"></label><label>Текущее обновление<input name="progressNote" value="${escapeHTML(record.progressNote)}" placeholder="Что изменилось с прошлого раза"></label></div>${record.type === 'goal' ? `<label>Достигнутый результат<textarea name="result" rows="3">${escapeHTML(record.result)}</textarea></label>` : ''}` : ''}
        ${record.type === 'question_set' ? `<div class="derived-progress"><span>Прогресс обсуждения рассчитывается по принятым итогам</span><strong>${record.progress}%</strong></div>` : ''}
      </div></details>
      <label id="record-reason-field" class="reason-field" hidden>Причина изменения <input name="reason" placeholder="Почему изменился статус или срок"></label>
      <div class="form-actions"><button type="submit" class="primary">Сохранить</button><span class="form-save-state" id="record-save-state">Изменений нет</span><button type="button" class="secondary" id="notify-partners">Уведомить</button>${record.type === 'task' ? `<button type="button" class="secondary" id="convert-to-questions">${icon('messages')} Сделать карточкой вопросов</button>` : ''}<button type="button" class="danger-text" id="archive-record">В архив</button></div>
    </form>
    ${record.type === 'meeting' ? `<section class="meeting-results"><header><div><p class="eyebrow">После встречи</p><h3>Превратить заметки в работу</h3></div></header><div><button type="button" data-create-from-record="task">${icon('checkSquare')} Задача</button><button type="button" data-create-from-record="decision">${icon('scale')} Решение</button><button type="button" data-create-from-record="limitation">${icon('archive')} Ограничение</button><button type="button" data-create-from-record="idea">${icon('lightbulb')} Идея</button><button type="button" data-create-from-record="research">${icon('flask')} Исследование</button></div></section>` : ''}
    ${(record.type === 'task') ? renderProofBlock(record, state.activeDetail.proofs) : ''}
  </div>`;
}

function renderRecordContent(detail) {
  return `<div class="record-pane ${state.activeRecordTab === 'content' ? 'active' : ''}" data-record-pane="content"><section class="accordion-stack content-stack">${detail.sections.map(renderSection).join('')}<details class="accordion"><summary><span>Добавить свой раздел</span><small>Только для этой карточки</small></summary><form id="custom-section-form" class="inline-editor"><input name="title" placeholder="Название раздела" required><textarea name="content" rows="4" placeholder="Содержание"></textarea><button class="secondary" type="submit">Добавить раздел</button></form></details></section></div>`;
}

function renderQuestionWorkflow(detail) {
  const workflow = detail.questionWorkflow || { questions: [], userCount: state.users.length, answered: 0, expected: 0, resolved: 0 };
  const completion = workflow.questions.length ? Math.round(workflow.resolved * 100 / workflow.questions.length) : 0;
  return `<div class="record-pane ${state.activeRecordTab === 'questions' ? 'active' : ''}" data-record-pane="questions">
    <section class="question-summary"><div><p class="eyebrow">Совместная проработка</p><h3>${workflow.resolved} из ${workflow.questions.length} вопросов решено</h3><p>Каждый основатель отвечает отдельно. Итог можно выбрать из ответа или сформулировать заново.</p></div><div class="question-progress"><strong>${completion}%</strong><progress class="progress-track" max="100" value="${completion}"></progress><small>${workflow.answered} из ${workflow.expected} ответов</small></div></section>
    <section class="question-list">${workflow.questions.map((question, index) => renderQuestionItem(question, index, workflow.userCount)).join('') || `<div class="guided-empty">${icon('messages')}<h3>Добавьте первый список вопросов</h3><p>Вставьте несколько строк. Каждая строка станет отдельным вопросом внутри этой карточки.</p></div>`}</section>
    <details class="add-questions" ${workflow.questions.length ? '' : 'open'}><summary>${icon('plus')} Добавить вопросы</summary><form id="add-questions-form"><label>Один вопрос на строку<textarea name="questions" rows="5" placeholder="Как распределяем роли?&#10;Как принимаем спорные решения?&#10;Как часто сверяем цели?" required></textarea><small>Нумерацию можно вставлять вместе с текстом, система уберёт её автоматически.</small></label><button type="submit" class="primary">${icon('plus')} Добавить в карточку</button></form></details>
  </div>`;
}

function renderQuestionItem(question, index, userCount) {
  const allAnswered = question.answers.length >= userCount && userCount > 0;
  const answerByUser = new Map(question.answers.map((answer) => [answer.authorId, answer]));
  return `<article class="question-item ${question.decision ? 'resolved' : ''}">
    <header class="question-header"><span class="question-number">${index + 1}</span><div><h3>${escapeHTML(question.body)}</h3><p>${question.decision ? 'Совместный итог зафиксирован' : `${question.answers.length} из ${userCount} ответов готово`}</p></div><span class="status ${question.decision ? 'status-completed' : 'status-in_progress'}">${question.decision ? 'Решено' : 'Обсуждаем'}</span><button type="button" class="icon-button danger-icon" data-archive-question="${question.id}" title="Архивировать вопрос" aria-label="Архивировать вопрос">${icon('archive')}</button></header>
    <div class="answer-grid">${state.users.map((user) => renderFounderAnswer(question, user, answerByUser.get(user.id))).join('')}${state.users.length < 2 ? renderMissingFounder() : ''}</div>
    ${question.decision ? renderJointDecision(question) : allAnswered ? renderDecisionComposer(question) : `<div class="waiting-note">${icon('clock')} Итог станет доступен после ответов всех основателей.</div>`}
  </article>`;
}

function renderMissingFounder() {
  return `<section class="answer-panel missing-founder"><header><span class="avatar">?</span><span><strong>Второй основатель</strong><small>Аккаунт ещё не зарегистрирован</small></span></header><div class="answer-placeholder">После регистрации партнёр увидит этот вопрос в блоке «Ждут ответа».</div></section>`;
}

function renderFounderAnswer(question, user, answer) {
  const isMe = user.id === state.me.id;
  return `<section class="answer-panel ${answer ? 'answered' : ''}"><header><span class="avatar">${escapeHTML(user.username.slice(0, 2).toUpperCase())}</span><span><strong>${escapeHTML(user.username)}</strong><small>${answer ? `Ответ обновлён ${formatDate(answer.updatedAt, true)}` : 'Ответа пока нет'}</small></span>${answer ? `<span class="answer-ready">${icon('check')} Готово</span>` : ''}</header>${isMe ? `<form class="answer-form" data-question-answer="${question.id}"><textarea name="content" rows="5" placeholder="Ваш развёрнутый ответ" required>${escapeHTML(answer?.content || '')}</textarea><button type="submit" class="secondary">${icon('send')} ${answer ? 'Обновить ответ' : 'Отправить ответ'}</button></form>` : answer ? `<div class="answer-content">${escapeHTML(answer.content).replace(/\n/g, '<br>')}</div>` : `<div class="answer-placeholder">Ожидаем позицию партнёра</div>`}</section>`;
}

function renderJointDecision(question) {
  const source = question.decision.sourceAuthorUsername ? `Выбрано из ответа ${question.decision.sourceAuthorUsername}` : 'Сформулировано после обсуждения';
  const outputLabels = { preference: 'Критерий', limitation: 'Ограничение', rule: 'Правило', insight: 'Вывод', task: 'Задача', idea: 'Идея', research: 'Исследование', goal: 'Цель' };
  return `<section class="joint-decision"><span class="decision-icon">${icon('scale')}</span><div><p class="eyebrow">Совместный итог</p><blockquote>${escapeHTML(question.decision.content).replace(/\n/g, '<br>')}</blockquote><small>${escapeHTML(source)} · зафиксировал ${escapeHTML(question.decision.decidedByUsername)}</small>${question.outputs?.length ? `<div class="decision-outputs"><span>Уже используется:</span>${question.outputs.map((output) => `<button type="button" data-related-record="${output.recordId}">${escapeHTML(outputLabels[output.kind || output.type] || typeMeta[output.type]?.singular || 'Карточка')}: ${escapeHTML(output.title)}</button>`).join('')}</div>` : ''}</div><div class="decision-actions"><details class="output-menu"><summary>${icon('plus')} Использовать вывод</summary><div>${Object.entries(outputLabels).map(([kind, label]) => `<button type="button" data-create-output="${kind}" data-question-id="${question.id}">${escapeHTML(label)}</button>`).join('')}</div></details><details><summary>${icon('edit')} Изменить итог</summary>${renderDecisionComposer(question, true)}</details></div></section>`;
}

function renderDecisionComposer(question, compact = false) {
  return `<section class="decision-composer ${compact ? 'compact' : ''}"><div><p class="eyebrow">Зафиксировать совместное решение</p><h4>Выберите готовый ответ или напишите новый итог</h4></div><div class="decision-options">${question.answers.map((answer) => `<button type="button" class="answer-choice" data-select-answer="${answer.id}" data-question-id="${question.id}"><span class="avatar tiny">${escapeHTML(answer.authorUsername.slice(0, 2).toUpperCase())}</span><span><strong>Принять ответ ${escapeHTML(answer.authorUsername)}</strong><small>${escapeHTML(answer.content.slice(0, 120))}${answer.content.length > 120 ? '…' : ''}</small></span>${icon('chevronRight')}</button>`).join('')}</div><form class="custom-decision-form" data-custom-decision="${question.id}"><textarea name="content" rows="4" placeholder="Новая совместная формулировка после обсуждения" required>${compact && question.decision && !question.decision.sourceAnswerId ? escapeHTML(question.decision.content) : ''}</textarea><button type="submit" class="primary">${icon('check')} Сохранить общий итог</button></form></section>`;
}

function renderRecordRelations(record, detail, criteria, targets) {
  const content = detail.relationsLoaded
    ? `<section class="accordion-stack content-stack">${record.type === 'idea' ? renderCriteriaBlock(criteria, detail.scores, true) : ''}${renderLinksBlock(record, detail.links, targets, true)}</section>`
    : `<div class="relations-loading"><span class="spinner"></span><strong>Подготавливаем связи</strong><small>Основная карточка уже доступна, эта часть загружается отдельно.</small></div>`;
  return `<div class="record-pane ${state.activeRecordTab === 'relations' ? 'active' : ''}" data-record-pane="relations">${content}</div>`;
}

function renderRecordHistory(activity) {
  return `<div class="record-pane ${state.activeRecordTab === 'history' ? 'active' : ''}" data-record-pane="history"><section class="history-pane"><div class="section-heading"><div><p class="eyebrow">Аудит карточки</p><h3>${activity.length} событий</h3></div></div><div class="activity-list">${activity.map(renderActivityItem).join('') || emptyState('Изменений пока нет.')}</div></section></div>`;
}

function renderRecordDialog() {
  const detail = state.activeDetail;
  const record = detail.record;
  const statuses = [...(statusesByType[record.type] || statusesByType.default)];
  if (!statuses.includes(record.status)) statuses.push(record.status);
  const allLinkTargets = state.records.filter((item) => item.id !== record.id && item.status !== 'archived');
  const criteria = state.records.filter((item) => item.type === 'criterion' && item.status !== 'archived');
  const activity = state.activity.filter((item) => item.entityId === record.id);
  const hasDeadline = ['task', 'goal', 'question_set', 'research', 'decision', 'disagreement', 'meeting'].includes(record.type);
  const ideaActions = record.type === 'idea' ? `<div class="idea-actions">${['review', 'main', 'rejected'].map((status) => `<button type="button" class="stage-action ${status}" data-stage="${status}" ${record.status === status ? 'disabled' : ''}>${statusLabels[status]}</button>`).join('')}</div>` : '';
  $('#record-dialog-content').innerHTML = `
    <div class="record-shell record-type-${record.type}">
    <div class="dialog-header record-dialog-header"><div><span class="record-kind">${icon(typeMeta[record.type].icon)} ${typeMeta[record.type].singular} · ${record.id.slice(0, 8)}</span><h2>${escapeHTML(record.title)}</h2><p>Создал ${escapeHTML(record.authorUsername)} · ${formatDate(record.createdAt, true)}</p></div><button type="button" class="close-button icon-button" data-close-dialog aria-label="Закрыть">${icon('x')}</button></div>
    ${ideaActions}
    <nav class="record-tabs" aria-label="Разделы карточки">${recordTabs(record, detail, activity)}</nav>
    <div class="dialog-layout">
      <div class="dialog-main">
        ${record.type === 'question_set' ? renderQuestionWorkflow(detail) : ''}
        ${renderRecordOverview(record, statuses)}
        ${renderRecordContent(detail)}
        ${renderRecordRelations(record, detail, criteria, allLinkTargets)}
        ${renderRecordHistory(activity)}
      </div>
      <aside class="dialog-aside">
        <div class="fact"><span>${record.type === 'question_set' ? 'Координатор' : record.type === 'meeting' ? 'Организатор' : 'Ответственный'}</span><strong>${escapeHTML(record.ownerUsername)}</strong></div>
        <div class="fact"><span>Статус</span><strong>${escapeHTML(statusLabels[record.status])}</strong></div>
        ${hasDeadline ? `<div class="fact"><span>${record.type === 'meeting' ? 'Дата' : 'Срок'}</span><strong class="deadline ${deadlineState(record).className}">${escapeHTML(deadlineState(record).label)}</strong></div>` : ''}
        <div class="fact"><span>Изменено</span><strong>${formatDate(record.updatedAt, true)}</strong></div>
        ${record.type === 'task' ? `<div class="fact"><span>Доказательств</span><strong>${record.proofCount}</strong></div>` : ''}
        ${record.type === 'question_set' ? `<div class="fact"><span>Решено вопросов</span><strong>${detail.questionWorkflow.resolved} / ${detail.questionWorkflow.questions.length}</strong></div>` : ''}
      </aside>
    </div></div>`;
  bindRecordDialogEvents();
}

function userOptions(selected) {
  return state.users.map((user) => `<option value="${user.id}" ${Number(selected) === user.id ? 'selected' : ''}>${escapeHTML(user.username)}</option>`).join('');
}

function renderSection(section) {
  return `<details class="accordion"><summary><span>${escapeHTML(section.title)}</span><small>${section.content ? 'Заполнено' : 'Не заполнено'}</small></summary><form class="section-form inline-editor" data-section-id="${escapeHTML(section.id)}" data-definition-id="${escapeHTML(section.definitionId || '')}"><input name="title" value="${escapeHTML(section.title)}" ${section.definitionId ? 'readonly' : ''}><textarea name="content" rows="6" placeholder="Запишите факты, позиции и выводы">${escapeHTML(section.content)}</textarea><input name="reason" placeholder="Причина изменения (необязательно)"><button class="secondary" type="submit">Сохранить раздел</button></form></details>`;
}

function renderCriteriaBlock(criteria, scores, open = false) {
  const scoreMap = new Map(scores.map((score) => [score.criterionId, score]));
  const kindLabels = { preference: 'Критерий', limitation: 'Ограничение' };
  return `<details class="accordion" ${open ? 'open' : ''}><summary><span>Оценка по критериям</span><small>${scores.length} оценок · 0 не подходит, 10 полностью подходит</small></summary><div class="criteria-list">${criteria.map((criterion) => { const current = scoreMap.get(criterion.id); return `<form class="criterion-form" data-criterion-id="${criterion.id}"><div><span class="criterion-kind">${kindLabels[criterion.kind] || 'Критерий'}</span><strong>${escapeHTML(criterion.title)}</strong><small>${escapeHTML(criterion.description)}</small></div><input name="score" type="number" min="0" max="10" value="${current?.score ?? 0}" aria-label="Оценка соответствия от 0 до 10"><input name="note" value="${escapeHTML(current?.note || '')}" placeholder="Почему такая оценка"><button class="secondary" type="submit">Оценить</button></form>`; }).join('') || emptyState('Сначала зафиксируйте критерии в разделе «Правила и критерии».')}</div></details>`;
}

function renderLinksBlock(record, links, targets, open = false) {
  const relationLabel = (link) => {
    const outgoing = link.sourceId === record.id;
    const labels = {
      related: ['Связано', 'Связано'], supports: ['Поддерживает', 'Поддерживается'],
      depends_on: ['Зависит от', 'Нужно для'], result_of: ['Является результатом', 'Дало результат'],
      leads_to: ['Приводит к', 'Следует из'], produced: ['Породило', 'Создано из'],
    };
    return (labels[link.relationType] || [link.relationType, link.relationType])[outgoing ? 0 : 1];
  };
  const createOptions = {
    goal: [['task', '', 'Задача'], ['criterion', 'preference', 'Критерий']],
    idea: [['research', '', 'Исследование'], ['task', '', 'Задача'], ['decision', '', 'Решение']],
    research: [['decision', '', 'Решение'], ['criterion', 'preference', 'Критерий']],
    decision: [['task', '', 'Задача'], ['goal', '', 'Цель']],
    disagreement: [['decision', '', 'Решение'], ['decision', 'rule', 'Правило']],
    criterion: [['research', '', 'Исследование']],
    meeting: [['task', '', 'Задача'], ['decision', '', 'Решение'], ['criterion', 'limitation', 'Ограничение'], ['idea', '', 'Идея'], ['research', '', 'Исследование']],
  }[record.type] || [];
  return `<details class="accordion" ${open ? 'open' : ''}><summary><span>Связанные записи</span><small>${links.length} связей</small></summary>${createOptions.length ? `<div class="linked-create"><span>Создать следующий объект</span>${createOptions.map(([type, kind, label]) => `<button type="button" data-create-linked="${type}" data-linked-kind="${kind}">${icon(typeMeta[type].icon)} ${label}</button>`).join('')}</div>` : ''}<div class="linked-list">${links.map((link) => `<div class="linked-item"><button type="button" data-related-record="${link.record.id}"><i class="type-icon type-${link.record.type}">${icon(typeMeta[link.record.type].icon)}</i><span><strong>${escapeHTML(link.record.title)}</strong><small>${escapeHTML(relationLabel(link))} · ${typeMeta[link.record.type].singular}</small></span></button><button type="button" class="icon-button danger-icon remove-link" data-remove-link="${link.id}" aria-label="Убрать связь" title="Убрать связь">${icon('x')}</button></div>`).join('') || emptyState('Связей пока нет.')}</div><form id="link-form" class="link-form"><select name="targetId" required><option value="">Выберите существующую карточку</option>${targets.map((target) => `<option value="${target.id}">${typeMeta[target.type].singular}: ${escapeHTML(target.title)}</option>`).join('')}</select><select name="relationType"><option value="related">Связано</option><option value="supports">Поддерживает</option><option value="depends_on">Зависит от</option><option value="result_of">Является результатом</option><option value="leads_to">Приводит к</option></select><button class="secondary" type="submit">${icon('link')} Связать</button></form></details>`;
}

function renderProofBlock(record, proofs) {
  return `<details class="accordion" open><summary><span>Подтверждение результата</span><small>${proofs.length} приложено</small></summary><div class="proof-list">${proofs.map((proof) => `<article class="proof"><header><strong>${escapeHTML(proof.authorUsername)}</strong><time>${formatDate(proof.createdAt, true)}</time></header>${proof.kind === 'link' && /^https?:\/\//i.test(proof.content) ? `<a href="${escapeHTML(proof.content)}" target="_blank" rel="noreferrer">${escapeHTML(proof.content)}</a>` : `<p>${escapeHTML(proof.content).replace(/\n/g, '<br>')}</p>`}</article>`).join('') || emptyState('Перед завершением приложите результат или ссылку на него.')}</div>${record.ownerId === state.me.id ? `<form id="proof-form" class="proof-form"><select name="kind"><option value="text">Текст</option><option value="link">Ссылка</option></select><textarea name="content" rows="4" placeholder="Что сделано или где находится результат" required></textarea><button class="secondary" type="submit">Приложить</button></form><div class="completion-box"><label>Краткий итог<textarea id="completion-result" rows="3" placeholder="Что получили в результате"></textarea></label><label class="check"><input id="notify-on-complete" type="checkbox" checked> Уведомить партнёра</label><button type="button" class="success" id="complete-task" ${proofs.length ? '' : 'disabled'}>Завершить задачу</button></div>` : ''}</details>`;
}

function buildRecordUpdate(form, record) {
  const values = recordFormValues(form);
  const body = { expectedUpdatedAt: record.updatedAt };
  const compare = (key, next, previous) => { if (String(next ?? '') !== String(previous ?? '')) body[key] = next; };
  compare('title', values.title.trim(), record.title);
  compare('description', values.description.trim(), record.description);
  if ('status' in values) compare('status', values.status, record.status);
  compare('ownerId', Number(values.ownerId), record.ownerId);
  if ('decisionMakerId' in values) {
    if (values.decisionMakerId) compare('decisionMakerId', Number(values.decisionMakerId), record.decisionMakerId);
    else if (record.decisionMakerId) body.clearDecisionMaker = true;
  }
  if ('dueAt' in values) {
    const dueISO = values.dueAt ? new Date(values.dueAt).toISOString() : '';
    if (normalizedInstant(dueISO) !== normalizedInstant(record.dueAt)) body.dueAt = dueISO;
  }
  if ('estimateMinutes' in values) compare('estimateMinutes', Number(values.estimateMinutes), record.estimateMinutes);
  if ('progress' in values) compare('progress', Number(values.progress), record.progress);
  if ('progressNote' in values) compare('progressNote', values.progressNote.trim(), record.progressNote);
  if ('result' in values) compare('result', values.result.trim(), record.result);
  const substantiveKeys = Object.keys(body).filter((key) => key !== 'expectedUpdatedAt');
  const reasonRequired = Object.prototype.hasOwnProperty.call(body, 'status') || Object.prototype.hasOwnProperty.call(body, 'dueAt');
  if (reasonRequired) body.reason = values.reason.trim();
  return { body, substantiveKeys, reasonRequired, values };
}

function updateRecordFormState(form, record, persist = false) {
  const { substantiveKeys, reasonRequired, values } = buildRecordUpdate(form, record);
  const reasonField = $('#record-reason-field');
  if (reasonField) {
    reasonField.hidden = !reasonRequired;
    reasonField.querySelector('input').required = reasonRequired;
  }
  const status = $('#record-save-state');
  if (status) status.textContent = substantiveKeys.length ? 'Есть несохранённые изменения' : 'Изменений нет';
  form.classList.toggle('dirty', substantiveKeys.length > 0);
  if (persist && substantiveKeys.length) saveRecordDraft(record.id, values);
  if (persist && !substantiveKeys.length) clearRecordDraft(record.id);
}

function bindRecordDialogEvents() {
  const detail = state.activeDetail;
  const record = detail.record;
  $('[data-close-dialog]').addEventListener('click', () => $('#record-dialog').close());
  $$('[data-record-tab]').forEach((button) => button.addEventListener('click', async () => {
    state.activeRecordTab = button.dataset.recordTab;
    $$('.record-tab').forEach((tab) => tab.classList.toggle('active', tab.dataset.recordTab === state.activeRecordTab));
    $$('[data-record-pane]').forEach((pane) => pane.classList.toggle('active', pane.dataset.recordPane === state.activeRecordTab));
    if (state.activeRecordTab === 'relations' && !state.activeDetail.relationsLoaded) await loadRecordRelations(record.id);
  }));
  const editForm = $('#record-edit-form');
  editForm.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
      event.preventDefault();
      editForm.requestSubmit();
    }
  });
  editForm.addEventListener('input', () => updateRecordFormState(editForm, record, true));
  editForm.addEventListener('change', () => updateRecordFormState(editForm, record, true));
  $('[data-restore-draft]')?.addEventListener('click', () => {
    applyRecordDraft(editForm, loadRecordDraft(record.id));
    $('[data-restore-draft]').closest('.draft-banner').remove();
    toast('Черновик восстановлен');
  });
  $('[data-discard-draft]')?.addEventListener('click', () => {
    clearRecordDraft(record.id);
    $('[data-discard-draft]').closest('.draft-banner').remove();
    toast('Черновик удалён');
  });
  editForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const { body, substantiveKeys, reasonRequired } = buildRecordUpdate(event.currentTarget, record);
    if (!substantiveKeys.length) return toast('Изменений нет');
    if (reasonRequired && !body.reason) {
      $('#record-reason-field').hidden = false;
      event.currentTarget.elements.reason.focus();
      return toast('Укажите причину изменения статуса или срока', true);
    }
    await mutateRecord(`/api/records/${record.id}`, { method: 'PATCH', body: JSON.stringify(body) }, false, true);
  });
  $$('[data-stage]').forEach((button) => button.addEventListener('click', async () => {
    const reason = await askText({ title: 'Причина решения', label: `Почему идея переходит в статус «${statusLabels[button.dataset.stage]}»?`, required: true });
    if (reason === null) return;
    await mutateRecord(`/api/records/${record.id}`, { method: 'PATCH', body: JSON.stringify({ status: button.dataset.stage, reason, expectedUpdatedAt: record.updatedAt }) });
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
  $('#convert-to-questions')?.addEventListener('click', async () => {
    const reason = await askText({ title: 'Преобразовать карточку', label: 'Почему эта запись должна стать карточкой вопросов?', defaultValue: 'Задача изначально создана для совместной проработки списка вопросов', required: true });
    if (!reason) return;
    state.activeRecordTab = 'questions';
    const converted = await mutateRecord(`/api/records/${record.id}/convert-to-questions`, { method: 'POST', body: JSON.stringify({ reason, expectedUpdatedAt: record.updatedAt }) });
    if (converted) toast('Карточка преобразована. Теперь добавьте вопросы по одному на строку');
    else state.activeRecordTab = 'overview';
  });
  $$('.section-form').forEach((formNode) => formNode.addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    await mutateDetail(`/api/records/${record.id}/sections`, { method: 'POST', body: JSON.stringify({ sectionId: event.currentTarget.dataset.sectionId, definitionId: event.currentTarget.dataset.definitionId || null, title: form.get('title'), content: form.get('content'), reason: form.get('reason') }) });
  }));
  $('#custom-section-form')?.addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/sections`, { method: 'POST', body: JSON.stringify({ title: form.get('title'), content: form.get('content') }) }); });
  $$('.criterion-form').forEach((formNode) => formNode.addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/criteria/${event.currentTarget.dataset.criterionId}`, { method: 'PUT', body: JSON.stringify({ score: Number(form.get('score')), note: form.get('note'), reason: '' }) }); }));
  $('#link-form')?.addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/links`, { method: 'POST', body: JSON.stringify({ targetId: form.get('targetId'), relationType: form.get('relationType') }) }); });
  $$('[data-remove-link]').forEach((button) => button.addEventListener('click', async () => { const reason = await askText({ title: 'Убрать связь', label: 'Почему связь больше не актуальна?', required: true }); if (!reason) return; await mutateDetail(`/api/records/${record.id}/links/${button.dataset.removeLink}/remove`, { method: 'POST', body: JSON.stringify({ reason }) }); }));
  $$('[data-related-record]').forEach((button) => button.addEventListener('click', () => openRecord(button.dataset.relatedRecord)));
  $$('[data-create-from-record]').forEach((button) => button.addEventListener('click', () => {
    const requested = button.dataset.createFromRecord;
    const type = requested === 'limitation' ? 'criterion' : requested;
    openCreateDialog(type, { kind: requested === 'limitation' ? 'limitation' : '', description: `Источник: встреча «${record.title}»\n\n${record.description}`.trim(), sourceRecordId: record.id, relationType: 'produced', reason: 'Создано из заметок встречи' });
  }));
  $$('[data-create-linked]').forEach((button) => button.addEventListener('click', () => {
    openCreateDialog(button.dataset.createLinked, { kind: button.dataset.linkedKind, sourceRecordId: record.id, relationType: 'leads_to', reason: `Следующий объект создан из карточки «${record.title}»` });
  }));
  $$('[data-open-event]', $('#record-dialog')).forEach((button) => button.addEventListener('click', () => openActivity(button.dataset.openEvent)));
  $('#add-questions-form')?.addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    await mutateDetail(`/api/records/${record.id}/questions`, { method: 'POST', body: JSON.stringify({ questions: form.get('questions') }) });
  });
  $$('[data-question-answer]').forEach((formNode) => formNode.addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    await mutateDetail(`/api/records/${record.id}/questions/${event.currentTarget.dataset.questionAnswer}/answer`, { method: 'PUT', body: JSON.stringify({ content: form.get('content') }) });
  }));
  $$('[data-select-answer]').forEach((button) => button.addEventListener('click', async () => {
    await mutateDetail(`/api/records/${record.id}/questions/${button.dataset.questionId}/decision`, { method: 'POST', body: JSON.stringify({ mode: 'answer', answerId: button.dataset.selectAnswer }) });
  }));
  $$('[data-custom-decision]').forEach((formNode) => formNode.addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    await mutateDetail(`/api/records/${record.id}/questions/${event.currentTarget.dataset.customDecision}/decision`, { method: 'POST', body: JSON.stringify({ mode: 'custom', content: form.get('content') }) });
  }));
  $$('[data-create-output]').forEach((button) => button.addEventListener('click', () => {
    const question = detail.questionWorkflow.questions.find((item) => item.id === button.dataset.questionId);
    if (!question?.decision) return;
    const titles = { preference: question.decision.content, limitation: question.decision.content, rule: question.body, insight: question.body, task: `Реализовать: ${question.body}`, idea: question.decision.content, research: `Проверить: ${question.body}`, goal: question.decision.content };
    openQuestionOutputDialog(record, question, button.dataset.createOutput, String(titles[button.dataset.createOutput] || question.body).slice(0, 240));
  }));
  $$('[data-archive-question]').forEach((button) => button.addEventListener('click', async () => {
    const reason = await askText({ title: 'Архивировать вопрос', label: 'Почему вопрос больше не нужен?', required: true });
    if (!reason) return;
    await mutateDetail(`/api/records/${record.id}/questions/${button.dataset.archiveQuestion}/archive`, { method: 'POST', body: JSON.stringify({ reason }) });
  }));
  if ($('#proof-form')) $('#proof-form').addEventListener('submit', async (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); await mutateDetail(`/api/records/${record.id}/proofs`, { method: 'POST', body: JSON.stringify({ kind: form.get('kind'), content: form.get('content') }) }); });
  if ($('#complete-task')) $('#complete-task').addEventListener('click', async () => { await mutateRecord(`/api/records/${record.id}/complete`, { method: 'POST', body: JSON.stringify({ result: $('#completion-result').value, notifyPartners: $('#notify-on-complete').checked }) }); });
}

async function loadRecordRelations(recordID) {
  try {
    const relations = await api(`/api/records/${recordID}/relations`);
    if (!state.activeDetail || state.activeDetail.record.id !== recordID) return;
    state.activeDetail = { ...state.activeDetail, ...relations, relationsLoaded: true };
    state.detailCache.set(recordID, state.activeDetail);
    renderRecordDialog();
  } catch (error) {
    const loading = $('.relations-loading');
    if (loading) loading.innerHTML = `${icon('help')}<strong>Связи не загрузились</strong><small>${escapeHTML(error.message)}</small><button type="button" class="secondary" data-retry-relations>Повторить</button>`;
    $('[data-retry-relations]')?.addEventListener('click', () => loadRecordRelations(recordID));
  }
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

function openQuestionOutputDialog(sourceRecord, question, kind, defaultTitle) {
  const labels = { preference: 'Критерий выбора', limitation: 'Ограничение', rule: 'Правило', insight: 'Вывод', task: 'Задача', idea: 'Идея', research: 'Исследование', goal: 'Цель' };
  const planned = ['task', 'goal', 'research'].includes(kind);
  $('#create-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">${icon('link')} Результат совместного вывода</span><h2>${labels[kind]}</h2><p>Источник сохранится автоматически: группа вопросов → вопрос → совместный итог → новая карточка.</p></div><button type="button" class="close-button icon-button" data-close-create aria-label="Закрыть">${icon('x')}</button></div><form id="question-output-form" class="card-form dialog-form"><div class="source-context"><span>Вопрос</span><strong>${escapeHTML(question.body)}</strong><blockquote>${escapeHTML(question.decision.content)}</blockquote></div><label>Название<input name="title" required maxlength="240" value="${escapeHTML(defaultTitle)}"></label><label>Как применять<textarea name="description" rows="4">${escapeHTML(question.decision.content)}</textarea></label>${planned ? `<div class="form-grid two"><label>Ответственный<select name="ownerId">${userOptions(state.me.id)}</select></label><label>Срок<input name="dueAt" type="datetime-local"></label></div>` : `<input type="hidden" name="ownerId" value="${state.me.id}">`}<div class="form-actions"><button type="submit" class="primary">${icon('plus')} Создать и связать</button><button type="button" class="secondary" data-close-create>Отмена</button></div></form>`;
  $$('[data-close-create]').forEach((button) => button.addEventListener('click', () => $('#create-dialog').close()));
  $('#question-output-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const due = form.get('dueAt');
    try {
      const output = await api(`/api/records/${sourceRecord.id}/questions/${question.id}/outputs`, { method: 'POST', body: JSON.stringify({ kind, title: form.get('title'), description: form.get('description'), ownerId: Number(form.get('ownerId')), dueAt: due ? new Date(due).toISOString() : '' }) });
      $('#create-dialog').close();
      state.detailCache.delete(sourceRecord.id);
      await loadData(true);
      toast('Результат создан и связан');
      await openRecord(output.id);
    } catch (error) { toast(error.message, true); }
  });
  $('#create-dialog').showModal();
}

async function mutateDetail(path, options) {
  try {
    const recordID = state.activeDetail.record.id;
    await api(path, options);
    state.detailCache.delete(recordID);
    const [detail] = await Promise.all([fetchRecordDetail(recordID, true), loadData(true)]);
    state.activeDetail = detail;
    if (state.activeRecordTab === 'relations') {
      const relations = await api(`/api/records/${recordID}/relations`);
      state.activeDetail = { ...state.activeDetail, ...relations, relationsLoaded: true };
      state.detailCache.set(recordID, state.activeDetail);
    }
    renderRecordDialog();
    toast('Сохранено');
    return true;
  } catch (error) { toast(error.message, true); return false; }
}

async function mutateRecord(path, options, close = false, clearDraftOnSuccess = false) {
  try {
    const recordID = state.activeDetail.record.id;
    await api(path, options);
    if (clearDraftOnSuccess) clearRecordDraft(recordID);
    state.detailCache.delete(recordID);
    const [detail] = await Promise.all([close ? Promise.resolve(null) : fetchRecordDetail(recordID, true), loadData(true)]);
    if (close) $('#record-dialog').close();
    else { state.activeDetail = detail; renderRecordDialog(); }
    toast('Сохранено');
    return true;
  } catch (error) {
    toast(error.message, true);
    return false;
  }
}

function toggleCreateMenu() {
  const menu = $('#create-menu');
  menu.innerHTML = `
    <button type="button" data-create-type="idea">${icon('lightbulb')}<span><strong>Быстрая идея</strong><small>Сохранить мысль без оценки</small></span></button>
    <button type="button" data-create-type="task">${icon('checkSquare')}<span><strong>Задача</strong><small>Себе или партнёру</small></span></button>
    <button type="button" data-create-type="meeting">${icon('calendar')}<span><strong>Встреча</strong><small>Повестка, заметки и результаты</small></span></button>
    <button type="button" data-create-type="question_set">${icon('messages')}<span><strong>Карточка вопросов</strong><small>Несколько вопросов, личные ответы и итоги</small></span></button>
    <button type="button" data-create-type="other">${icon('plus')}<span><strong>Другая карточка</strong><small>Цель, исследование, решение или документ</small></span></button>`;
  menu.hidden = !menu.hidden;
  $$('[data-create-type]', menu).forEach((button) => button.addEventListener('click', (event) => {
    event.stopPropagation(); menu.hidden = true; openCreateDialog(button.dataset.createType === 'other' ? 'goal' : button.dataset.createType);
  }));
}

function openCreateDialog(initialType = 'idea', preset = {}) {
  const initialMeta = typeMeta[initialType];
  const kindLabels = { preference: 'Критерий выбора', limitation: 'Ограничение', rule: 'Правило', insight: 'Вывод' };
  const displayName = kindLabels[preset.kind] || initialMeta.singular;
  const titleLabel = initialType === 'question_set' ? 'Название группы вопросов' : initialType === 'meeting' ? 'Тема встречи' : 'Название';
  const descriptionLabel = preset.kind === 'limitation' ? 'Как применять ограничение' : preset.kind === 'rule' ? 'Формулировка и область действия' : initialType === 'question_set' ? 'Зачем обсуждаем' : initialType === 'meeting' ? 'Повестка и заметки' : initialType === 'task' ? 'Ожидаемый результат' : 'Краткое описание';
  $('#create-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">${icon(initialMeta.icon)} Новая запись</span><h2>${escapeHTML(displayName)}</h2></div><button type="button" class="close-button icon-button" data-close-create aria-label="Закрыть">${icon('x')}</button></div><form id="create-record-form" class="card-form dialog-form"><label>${titleLabel}<input name="title" required maxlength="240" autofocus value="${escapeHTML(preset.title || '')}" placeholder="${initialType === 'question_set' ? 'Например: Договорённости основателей' : ''}"></label><label>${descriptionLabel}<textarea name="description" rows="5">${escapeHTML(preset.description || '')}</textarea></label><input type="hidden" name="type" value="${initialType}"><input type="hidden" name="kind" value="${escapeHTML(preset.kind || '')}">${['task', 'goal', 'research', 'question_set', 'meeting'].includes(initialType) ? `<div class="form-grid two"><label>${initialType === 'question_set' ? 'Координатор' : initialType === 'meeting' ? 'Организатор' : 'Ответственный'}<select name="ownerId">${userOptions(state.me.id)}</select></label><label>${initialType === 'meeting' ? 'Дата и время' : 'Срок'}<input name="dueAt" type="datetime-local"></label></div>` : `<input type="hidden" name="ownerId" value="${state.me.id}">`}${initialType === 'task' ? `<label>Оценка времени, минут<input name="estimateMinutes" type="number" min="0" value="0"></label>` : `<input type="hidden" name="estimateMinutes" value="0">`}<div class="form-actions"><button type="submit" class="primary">${icon('plus')} Создать</button><button type="button" class="secondary" data-close-create>Отмена</button></div></form>`;
  $$('[data-close-create]').forEach((button) => button.addEventListener('click', () => $('#create-dialog').close()));
  $('#create-record-form').addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget); const due = form.get('dueAt');
    try {
      const record = await api('/api/records', { method: 'POST', body: JSON.stringify({ type: form.get('type'), kind: form.get('kind'), title: form.get('title'), description: form.get('description'), ownerId: Number(form.get('ownerId')), dueAt: due ? new Date(due).toISOString() : '', estimateMinutes: Number(form.get('estimateMinutes')) }) });
      let linkError = '';
      if (preset.sourceRecordId) {
        try {
          await api(`/api/records/${preset.sourceRecordId}/links`, { method: 'POST', body: JSON.stringify({ targetId: record.id, relationType: preset.relationType || 'leads_to', reason: preset.reason || 'Карточка создана из связанного рабочего контекста' }) });
          state.detailCache.delete(preset.sourceRecordId);
        } catch (error) {
          linkError = `Карточка создана, но связь не добавлена: ${error.message}`;
        }
      }
      $('#create-dialog').close(); await loadData(true); toast(linkError || 'Карточка создана', Boolean(linkError)); await openRecord(record.id);
    } catch (error) { toast(error.message, true); }
  });
  $('#create-dialog').showModal();
}

function actionLabel(action) {
  return ({ created: 'создал карточку', profile_updated: 'изменил профиль', updated: 'изменил карточку', converted_to_questions: 'преобразовал в карточку вопросов', archived: 'перенёс в архив', section_updated: 'обновил раздел', link_created: 'создал связь', link_removed: 'убрал связь', criterion_scored: 'оценил по критерию', proof_added: 'добавил доказательство', completed: 'завершил задачу', partners_notified: 'уведомил партнёра', questions_added: 'добавил вопросы', question_answered: 'ответил на вопрос', question_decided: 'зафиксировал совместное решение', question_archived: 'архивировал вопрос', output_created: 'превратил вывод в рабочую карточку', created_from_question: 'создал карточку из совместного вывода' }[action] || action);
}

function formatActivityValue(value, truncate = true) {
  if (value === null || value === undefined || value === '') return 'не указано';
  if (typeof value === 'object') return JSON.stringify(value);
  const text = String(value);
  return truncate && text.length > 140 ? `${text.slice(0, 137)}…` : text;
}

function activityDisplayValue(field, value, truncate = true) {
  if (field === 'status' && value) return statusLabels[value] || value;
  if (field === 'type' && value) return typeMeta[value]?.singular || value;
  if ((field === 'ownerId' || field === 'decisionMakerId') && value) return state.users.find((user) => user.id === Number(value))?.username || value;
  if (field === 'dueAt' && value) return formatDate(value, true);
  if (field === 'estimateMinutes' && value !== null && value !== undefined) return minutesLabel(Number(value));
  if (field === 'progress' && value !== null && value !== undefined) return `${value}%`;
  return formatActivityValue(value, truncate);
}

function activityChanges(item, full = false) {
  const fieldLabels = { username: 'Логин', title: 'Название', description: 'Описание', status: 'Статус', ownerId: 'Ответственный', decisionMakerId: 'Принимает решение', dueAt: 'Срок', estimateMinutes: 'Оценка времени', progress: 'Прогресс', progressNote: 'Ход работы', result: 'Результат' };
  const changes = Object.entries(item.details || {}).filter(([, value]) => value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'before') && Object.prototype.hasOwnProperty.call(value, 'after'));
  if (!changes.length && Object.prototype.hasOwnProperty.call(item.details || {}, 'before') && Object.prototype.hasOwnProperty.call(item.details || {}, 'after')) {
    changes.push([item.details?.section || 'Содержание', { before: item.details.before, after: item.details.after }]);
  }
  if (!changes.length) return '';
  return changes.map(([field, value]) => `<span class="change-line"><b>${escapeHTML(fieldLabels[field] || field)}:</b> <del>${escapeHTML(activityDisplayValue(field, value.before, !full))}</del><i>→</i><ins>${escapeHTML(activityDisplayValue(field, value.after, !full))}</ins></span>`).join('');
}

function activityDetails(item) {
  const changedFields = new Set(Object.entries(item.details || {}).filter(([, value]) => value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'before') && Object.prototype.hasOwnProperty.call(value, 'after')).map(([field]) => field));
  const fieldLabels = { title: 'Название', status: 'Статус', ownerId: 'Ответственный', targetId: 'Связанная карточка', relationType: 'Тип связи', section: 'Раздел', score: 'Оценка', note: 'Комментарий', kind: 'Тип доказательства', proofCount: 'Доказательств', result: 'Результат', message: 'Сообщение' };
  const details = Object.entries(item.details || {}).filter(([field]) => !changedFields.has(field) && !['before', 'after'].includes(field));
  if (!details.length) return '';
  return `<dl class="event-details">${details.map(([field, value]) => `<div><dt>${escapeHTML(fieldLabels[field] || field)}</dt><dd>${escapeHTML(activityDisplayValue(field, value, false))}</dd></div>`).join('')}</dl>`;
}

function recordTitleByActivity(item) {
  return state.records.find((record) => record.id === item.entityId)?.title || item.details?.title || `${item.entityType} · ${item.entityId.slice(0, 8)}`;
}

function renderActivityItem(item) {
  return `<button type="button" class="activity-item" data-open-event="${item.id}"><span class="avatar tiny">${escapeHTML(item.actorUsername.slice(0, 2).toUpperCase())}</span><span><strong>${escapeHTML(item.actorUsername)} ${escapeHTML(actionLabel(item.action))}</strong><small>${escapeHTML(recordTitleByActivity(item))}${item.reason ? ` · Причина: ${escapeHTML(item.reason)}` : ''}</small>${activityChanges(item)}</span><time>${formatDate(item.createdAt, true)}</time><span class="activity-arrow" aria-hidden="true">›</span></button>`;
}

function openActivity(id) {
  const item = state.activity.find((activity) => activity.id === id);
  if (!item) return toast('Событие не найдено', true);
  state.activeActivity = item;
  const record = state.records.find((candidate) => candidate.id === item.entityId);
  $('#event-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">Событие · ${formatDate(item.createdAt, true)}</span><h2>${escapeHTML(actionLabel(item.action))}</h2><p>${escapeHTML(item.actorUsername)} · ${escapeHTML(typeMeta[item.entityType]?.singular || item.entityType)}</p></div><button type="button" class="close-button" data-close-event aria-label="Закрыть">×</button></div><div class="event-body"><section class="event-summary"><span class="avatar">${escapeHTML(item.actorUsername.slice(0, 2).toUpperCase())}</span><div><p class="eyebrow">Связанная запись</p><h3>${escapeHTML(recordTitleByActivity(item))}</h3>${item.reason ? `<p class="event-reason"><b>Причина:</b> ${escapeHTML(item.reason)}</p>` : ''}</div></section>${activityChanges(item, true) ? `<section class="event-section"><p class="eyebrow">Что изменилось</p><div class="event-change-list">${activityChanges(item, true)}</div></section>` : ''}${activityDetails(item) ? `<section class="event-section"><p class="eyebrow">Подробности</p>${activityDetails(item)}</section>` : ''}<div class="form-actions">${record ? `<button type="button" class="primary" data-event-record="${record.id}">Открыть карточку</button>` : ''}<button type="button" class="secondary" data-close-event>Закрыть</button></div></div>`;
  $$('[data-close-event]', $('#event-dialog')).forEach((button) => button.addEventListener('click', () => $('#event-dialog').close()));
  $('[data-event-record]')?.addEventListener('click', async (event) => { $('#event-dialog').close(); await openRecord(event.currentTarget.dataset.eventRecord); });
  if (!$('#event-dialog').open) $('#event-dialog').showModal();
}

function renderHistory() {
  const isTimeline = state.historyMode === 'timeline';
  const events = [
    ...state.activity.map((item) => ({ date: item.createdAt, kind: 'activity', item })),
    ...state.records.filter((record) => record.dueAt).map((record) => ({ date: record.dueAt, kind: 'deadline', record })),
  ].sort((a, b) => new Date(b.date) - new Date(a.date));
  $('#main-content').innerHTML = `<div class="page-heading"><div><p class="eyebrow">Память проекта</p><h1>История</h1><p>Решения, изменения и сроки в одном месте.</p></div><div class="view-switch"><button type="button" data-history-mode="feed" class="${!isTimeline ? 'active' : ''}">Лента</button><button type="button" data-history-mode="timeline" class="${isTimeline ? 'active' : ''}">По времени</button></div></div>${isTimeline ? `<div class="timeline">${events.map((event) => event.kind === 'activity' ? `<div class="timeline-row"><time>${formatDate(event.date, true)}</time><i></i><div>${renderActivityItem(event.item)}</div></div>` : `<div class="timeline-row deadline-row"><time>${formatDate(event.date, true)}</time><i></i><div><button type="button" class="timeline-deadline" data-open-record="${event.record.id}"><span class="type-icon">${icon(typeMeta[event.record.type].icon)}</span><span><strong>Срок: ${escapeHTML(event.record.title)}</strong><small>${escapeHTML(event.record.ownerUsername)} · ${statusLabels[event.record.status]}</small></span></button></div></div>`).join('') || emptyState('Событий пока нет.')}</div>` : `<section class="section-panel"><div class="activity-list">${state.activity.map(renderActivityItem).join('') || emptyState('История пока пуста.')}</div></section>`}`;
  $$('[data-history-mode]').forEach((button) => button.addEventListener('click', () => { state.historyMode = button.dataset.historyMode; renderHistory(); }));
  bindOpenRecords();
}

function renderStructure() {
  const configurableTypes = Object.entries(typeMeta).filter(([key]) => !['question_set', 'meeting'].includes(key));
  const selectedType = state.structureType || 'idea';
  state.structureType = selectedType;
  const definitions = state.definitions.filter((definition) => definition.scopeType === selectedType || !definition.scopeType);
  $('#main-content').innerHTML = `<div class="page-heading"><div><p class="eyebrow">Настройки</p><h1>Шаблоны карточек</h1><p>Выберите тип и настройте дополнительные смысловые блоки. Основные поля карточки не меняются.</p></div></div><div class="template-editor"><aside>${configurableTypes.map(([key, meta]) => `<button type="button" data-structure-type="${key}" class="${selectedType === key ? 'active' : ''}">${icon(meta.icon)}<span>${meta.label}</span><b>${state.definitions.filter((definition) => definition.scopeType === key && definition.active).length}</b></button>`).join('')}</aside><section><header><div><h2>${typeMeta[selectedType].label}</h2><p>Блоки появляются во вкладке «Содержание» карточек этого типа.</p></div><button type="button" class="secondary" data-add-template-block>${icon('plus')} Добавить блок</button></header><div class="template-block-list">${definitions.map((definition) => `<article class="template-block ${definition.active ? '' : 'inactive'}"><span class="drag-handle">⋮⋮</span><div><strong>${escapeHTML(definition.name)}</strong><small>${definition.scopeType ? `Только ${typeMeta[definition.scopeType].label.toLowerCase()}` : 'Во всех карточках'}</small></div><button type="button" class="text-button" data-toggle-definition="${definition.id}" data-active="${definition.active}">${definition.active ? 'Скрыть' : 'Вернуть'}</button></article>`).join('') || emptyState('Дополнительных блоков нет.')}</div></section></div>`;
  $$('[data-structure-type]').forEach((button) => button.addEventListener('click', () => { state.structureType = button.dataset.structureType; renderStructure(); }));
  $('[data-add-template-block]').addEventListener('click', async () => { const name = await askText({ title: `Новый блок для «${typeMeta[selectedType].label}»`, label: 'Название смыслового блока', required: true }); if (!name) return; try { await api('/api/section-definitions', { method: 'POST', body: JSON.stringify({ name, scopeType: selectedType, kind: 'universal' }) }); await loadData(true); state.structureType = selectedType; renderStructure(); toast('Блок добавлен'); } catch (error) { toast(error.message, true); } });
  $$('[data-toggle-definition]').forEach((button) => button.addEventListener('click', async () => { try { await api(`/api/section-definitions/${button.dataset.toggleDefinition}`, { method: 'PATCH', body: JSON.stringify({ active: button.dataset.active !== 'true', reason: button.dataset.active === 'true' ? 'Пункт больше не используется в новых карточках' : 'Пункт снова нужен' }) }); await loadData(true); toast('Структура обновлена'); } catch (error) { toast(error.message, true); } }));
}

function renderNotifications() {
  $('#main-content').innerHTML = `<div class="list-toolbar"><div><p class="eyebrow">Личный кабинет</p><h3>Уведомления</h3></div><button type="button" class="secondary" id="read-all">Прочитать все</button></div><section class="section-panel"><div class="notification-list">${state.notifications.map((item) => `<button type="button" class="notification ${item.readAt ? '' : 'unread'}" data-notification-id="${item.id}" data-entity-id="${escapeHTML(item.entityId || '')}"><i></i><span><strong>${escapeHTML(item.title)}</strong><p>${escapeHTML(item.body)}</p><small>${formatDate(item.createdAt, true)}</small></span></button>`).join('') || emptyState('Уведомлений пока нет.')}</div></section>`;
  $('#read-all').addEventListener('click', async () => { await api('/api/notifications/read-all', { method: 'POST' }); await loadData(true); });
  $$('[data-notification-id]').forEach((button) => button.addEventListener('click', async () => { await api(`/api/notifications/${button.dataset.notificationId}/read`, { method: 'POST' }); if (button.dataset.entityId) await openRecord(button.dataset.entityId); await loadData(true); }));
}

const onboardingSteps = [
  { icon: 'lightbulb', label: 'Сначала фиксируем', title: 'Мысль достаточно назвать', text: 'Быстрая идея попадает во входящие без оценки. Аргументы, критерии и решение добавляются позже, когда появится время на разбор.' },
  { icon: 'checkSquare', label: 'Работа команды', title: 'Задача хранит ожидаемый результат', text: 'Укажите исполнителя, срок и условия готовности. Исполнитель добавит доказательство, а история сохранит изменения.' },
  { icon: 'messages', label: 'Совместные вопросы', title: 'Одна карточка, несколько вопросов', text: 'Каждый вопрос получает отдельные ответы обоих основателей. Итог можно выбрать из ответа или сформулировать после обсуждения.' },
  { icon: 'history', label: 'Ничего не исчезает', title: 'Статус меняет представление, а не объект', text: 'Архив, причины изменений и единая история помогают восстановить, что произошло и почему.' },
];

function onboardingKey() {
  return `business-control:onboarding:${state.me?.id || 'anonymous'}:v2`;
}

function maybeShowOnboarding() {
  try { if (!localStorage.getItem(onboardingKey())) openOnboarding(0); } catch (_) {}
}

function openOnboarding(step = 0) {
  const item = onboardingSteps[step];
  const dialog = $('#onboarding-dialog');
  $('#onboarding-dialog-content').innerHTML = `<div class="onboarding-visual"><span>${icon(item.icon)}</span><div class="onboarding-chain">${onboardingSteps.map((_, index) => `<i class="${index <= step ? 'active' : ''}"></i>`).join('')}</div></div><div class="onboarding-copy"><p class="eyebrow">${escapeHTML(item.label)} · ${step + 1}/${onboardingSteps.length}</p><h2>${escapeHTML(item.title)}</h2><p>${escapeHTML(item.text)}</p><div class="onboarding-actions">${step ? `<button type="button" class="secondary" data-onboarding-step="${step - 1}">Назад</button>` : `<button type="button" class="text-button" data-skip-onboarding>Пропустить</button>`}<button type="button" class="primary" data-onboarding-step="${step + 1}">${step === onboardingSteps.length - 1 ? `${icon('check')} Начать работу` : `Далее ${icon('chevronRight')}`}</button></div></div>`;
  $$('[data-onboarding-step]', dialog).forEach((button) => button.addEventListener('click', () => { const next = Number(button.dataset.onboardingStep); if (next >= onboardingSteps.length) finishOnboarding(); else openOnboarding(next); }));
  $('[data-skip-onboarding]', dialog)?.addEventListener('click', finishOnboarding);
  if (!dialog.open) dialog.showModal();
}

function finishOnboarding() {
  try { localStorage.setItem(onboardingKey(), new Date().toISOString()); } catch (_) {}
  if ($('#onboarding-dialog').open) $('#onboarding-dialog').close();
}

bootstrap();
