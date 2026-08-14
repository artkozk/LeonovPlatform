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
  network: '<circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/><path d="m10.6 7.7-4.2 8.1M13.4 7.7l4.2 8.1M8 19h8"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  maximize: '<path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5"/>',
  rotate: '<path d="M21 12a9 9 0 1 1-2.6-6.4L21 8"/><path d="M21 3v5h-5"/>',
  flag: '<path d="M5 22V4M5 4h11l-1 4 1 4H5"/>',
  lock: '<rect width="16" height="11" x="4" y="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
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

const priorityLabels = { low: 'Низкий', normal: 'Обычный', high: 'Высокий', critical: 'Критический' };
const priorityWeight = { critical: 0, high: 1, normal: 2, low: 3 };
const workstreamLabels = { business: 'Бизнес', platform: 'Разработка платформы', operations: 'Операционная работа' };
const editPolicyLabels = { shared: 'Общая: команда может изменять', owner_only: 'Личная: изменяет только ответственный' };

const navItems = [
  ['dashboard', 'Обзор', 'dashboard', 'Работа'], ['work', 'Работа', 'checkSquare', 'Работа'],
  ['meeting', 'Встречи', 'calendar', 'Работа'],
  ['principles', 'Правила и критерии', 'bookOpen', 'Основа'], ['goal', 'Цели', 'target', 'Бизнес'],
  ['idea', 'Идеи', 'lightbulb', 'Бизнес'], ['research', 'Исследования', 'flask', 'Бизнес'],
  ['decision', 'Решения', 'scale', 'Бизнес'], ['disagreement', 'Разногласия', 'gitCompare', 'Бизнес'],
  ['document', 'Документы', 'fileText', 'Бизнес'], ['graph', 'Карта связей', 'network', 'Контроль'],
  ['history', 'История', 'history', 'Контроль'],
  ['structure', 'Шаблоны карточек', 'settings', 'Настройки'],
];

const state = {
  me: null, users: [], records: [], notifications: [], activity: [], definitions: [], pendingQuestions: [],
  view: 'dashboard', search: '', statusFilter: '', ownerFilter: '', authMode: 'login', activeDetail: null,
  activeRecordTab: 'overview', activeActivity: null, historyMode: 'feed', activeRecordRequest: 0,
  workScope: 'all', workType: 'all', workStatus: 'active', workstreamFilter: 'all',
  graphData: null, graphInstance: null, graphFocusRecordId: '', graphDepth: 2, graphShowDiscussion: true,
  graphTypeFilter: 'all', graphSearch: '', graphSelectedId: '', graphLinkSourceId: '',
  recordWorkspace: [], activeWorkspaceRecordId: '', focusQuestionId: '',
  detailCache: new Map(), detailRequests: new Map(), searchTimer: null, suppressOverlayPop: false,
  presenceInteractions: 0, presenceLastSentAt: Date.now(), lastInteractionAt: Date.now(), aiSuggestionTimer: null,
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

function questionsCountLabel(count) {
  const mod100 = count % 100;
  const mod10 = count % 10;
  if (mod10 === 1 && mod100 !== 11) return `${count} вопрос`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} вопроса`;
  return `${count} вопросов`;
}

function interactionsCountLabel(count) {
  const mod100 = count % 100;
  const mod10 = count % 10;
  if (mod10 === 1 && mod100 !== 11) return `${count} взаимодействие`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} взаимодействия`;
  return `${count} взаимодействий`;
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

function isWorkRecord(record) {
  return ['task', 'question_set', 'research', 'decision', 'disagreement', 'meeting'].includes(record.type);
}

function isActiveRecord(record) {
  return !['completed', 'cancelled', 'archived', 'rejected'].includes(record.status);
}

function sortWorkRecords(a, b) {
  const priority = (priorityWeight[a.priority || 'normal'] ?? 2) - (priorityWeight[b.priority || 'normal'] ?? 2);
  if (priority) return priority;
  const deadline = sortByDeadline(a, b);
  if (deadline) return deadline;
  return new Date(b.updatedAt) - new Date(a.updatedAt);
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
  $('#profile-button').addEventListener('click', () => openProfile(state.me.id));
  $('#new-record-button').addEventListener('click', (event) => { event.stopPropagation(); toggleCreateMenu(); });
  $('#notification-button').addEventListener('click', () => { state.view = 'notifications'; render(); });
  $('#onboarding-button').addEventListener('click', () => openOnboarding(0));
  const globalSearchInput = $('#global-search-input');
  globalSearchInput.addEventListener('input', () => {
    clearTimeout(state.searchTimer);
    state.searchTimer = setTimeout(() => runGlobalSearch(globalSearchInput.value), 180);
  });
  globalSearchInput.addEventListener('focus', () => { if (globalSearchInput.value.trim()) runGlobalSearch(globalSearchInput.value); });
  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault(); globalSearchInput.focus(); globalSearchInput.select();
    }
    if (event.key === 'Escape' && !$('#global-search-results').hidden) $('#global-search-results').hidden = true;
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.create-control')) $('#create-menu').hidden = true;
    if (!event.target.closest('#global-search')) $('#global-search-results').hidden = true;
  });
  $('#menu-button').addEventListener('click', () => setSidebarOpen(!$('.sidebar').classList.contains('open')));
  $('#sidebar-backdrop').addEventListener('click', () => setSidebarOpen(false));
  bindSidebarSwipe();
  $('#record-dialog').addEventListener('click', (event) => { if (event.target === $('#record-dialog')) $('#record-dialog').close(); });
  $('#event-dialog').addEventListener('click', (event) => { if (event.target === $('#event-dialog')) $('#event-dialog').close(); });
  $('#create-dialog').addEventListener('click', (event) => { if (event.target === $('#create-dialog')) $('#create-dialog').close(); });
  $('#reason-dialog').addEventListener('click', (event) => { if (event.target === $('#reason-dialog')) $('#reason-dialog').close('cancel'); });
  $('#onboarding-dialog').addEventListener('click', (event) => { if (event.target === $('#onboarding-dialog')) finishOnboarding(); });
  $('#profile-dialog').addEventListener('click', (event) => { if (event.target === $('#profile-dialog')) $('#profile-dialog').close(); });
  $$('dialog').forEach((dialog) => dialog.addEventListener('close', () => {
    if (dialog.dataset.historyState === 'true' && history.state?.businessControlOverlay === dialog.id) {
      dialog.dataset.historyState = 'false';
      state.suppressOverlayPop = true;
      history.back();
    }
  }));
  window.addEventListener('popstate', () => {
    if (state.suppressOverlayPop) { state.suppressOverlayPop = false; return; }
    const dialog = [...$$('dialog[open]')].pop();
    if (dialog) { dialog.dataset.historyState = 'false'; dialog.close(); return; }
    if ($('.sidebar').classList.contains('open')) setSidebarOpen(false);
  });
  ['pointerdown', 'keydown', 'touchstart'].forEach((eventName) => document.addEventListener(eventName, () => {
    state.lastInteractionAt = Date.now(); state.presenceInteractions += 1;
  }, { passive: true }));
  setInterval(sendPresence, 30000);
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

function setSidebarOpen(open) {
  $('.sidebar').classList.toggle('open', open);
  $('#sidebar-backdrop').classList.toggle('visible', open);
  document.body.classList.toggle('mobile-nav-open', open);
}

function openModal(dialog) {
  if (dialog.open) return;
  dialog.showModal();
  history.pushState({ businessControlOverlay: dialog.id }, '');
  dialog.dataset.historyState = 'true';
}

function bindSidebarSwipe() {
  const sidebar = $('.sidebar');
  let startX = 0;
  let currentX = 0;
  sidebar.addEventListener('touchstart', (event) => { startX = event.touches[0].clientX; currentX = startX; }, { passive: true });
  sidebar.addEventListener('touchmove', (event) => { currentX = event.touches[0].clientX; }, { passive: true });
  sidebar.addEventListener('touchend', () => {
    if (startX - currentX > 56) setSidebarOpen(false);
    startX = 0; currentX = 0;
  }, { passive: true });
}

async function sendPresence() {
  if (!state.me || document.hidden) return;
  const now = Date.now();
  const active = now - state.lastInteractionAt < 90000;
  const elapsed = Math.min(60, Math.max(0, Math.round((now - state.presenceLastSentAt) / 1000)));
  const interactions = state.presenceInteractions;
  state.presenceLastSentAt = now; state.presenceInteractions = 0;
  try { await api('/api/presence', { method: 'POST', body: JSON.stringify({ activeSeconds: active ? elapsed : 0, interactions }) }); } catch (_) {}
}

async function runGlobalSearch(query) {
  const resultsNode = $('#global-search-results');
  const normalized = query.trim();
  if (!normalized) { resultsNode.hidden = true; resultsNode.innerHTML = ''; return; }
  resultsNode.hidden = false;
  resultsNode.innerHTML = `<div class="search-loading"><span class="spinner"></span> Ищем во всём проекте</div>`;
  try {
    const results = await api(`/api/search?q=${encodeURIComponent(normalized)}`);
    if ($('#global-search-input').value.trim() !== normalized) return;
    resultsNode.innerHTML = results.length ? results.map(renderSearchResult).join('') : `<div class="search-empty">Ничего не найдено</div>`;
    $$('[data-search-result]', resultsNode).forEach((button) => button.addEventListener('click', async () => {
      resultsNode.hidden = true;
      $('#global-search-input').value = '';
      await openRecord(button.dataset.recordId, { tab: button.dataset.questionId ? 'questions' : 'overview', questionId: button.dataset.questionId, workspace: $('#record-dialog').open });
    }));
  } catch (error) {
    resultsNode.innerHTML = `<div class="search-empty">${escapeHTML(error.message)}</div>`;
  }
}

function renderSearchResult(result) {
  const meta = typeMeta[result.type] || { singular: result.type === 'question' ? 'Вопрос' : result.type === 'answer' ? 'Ответ' : result.type === 'joint_decision' ? 'Совместный итог' : 'Запись', icon: result.type === 'question' || result.type === 'answer' ? 'messages' : result.type === 'joint_decision' ? 'scale' : 'fileText' };
  const context = String(result.context || '').replace(/\s+/g, ' ').trim();
  return `<button type="button" class="global-search-result" data-search-result="${result.id}" data-record-id="${result.recordId}" data-question-id="${result.questionId || ''}"><span class="type-icon">${icon(meta.icon)}</span><span><small>${escapeHTML(meta.singular)}</small><strong>${escapeHTML(result.title)}</strong>${context ? `<em>${escapeHTML(context.slice(0, 150))}${context.length > 150 ? '…' : ''}</em>` : ''}</span>${icon('chevronRight')}</button>`;
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
    const count = key === 'work'
      ? state.records.filter((record) => isWorkRecord(record) && isActiveRecord(record)).length
      : typeMeta[key] ? state.records.filter((record) => record.type === key && record.status !== 'archived').length : '';
    const groupLabel = group !== itemGroup ? `<p class="nav-group">${escapeHTML(itemGroup)}</p>` : '';
    group = itemGroup;
    return `${groupLabel}<button type="button" class="nav-item ${state.view === key ? 'active' : ''}" data-view="${key}" title="${escapeHTML(label)}">${icon(iconName)}<span>${escapeHTML(label)}</span>${count !== '' ? `<b>${count}</b>` : ''}</button>`;
  }).join('');
  $$('[data-view]', $('#main-nav')).forEach((button) => button.addEventListener('click', () => {
    state.view = button.dataset.view; state.statusFilter = ''; state.search = ''; state.ownerFilter = '';
    setSidebarOpen(false); render();
  }));
}

function renderContent() {
  const titles = Object.fromEntries(navItems);
  $('#main-content').classList.toggle('graph-main-content', state.view === 'graph');
  if (state.view !== 'graph' && state.graphInstance) {
    state.graphInstance.destroy(); state.graphInstance = null;
  }
  $('#page-title').textContent = titles[state.view] || (state.view === 'notifications' ? 'Уведомления' : 'Обзор');
  if (state.view === 'dashboard') return renderDashboard();
  if (state.view === 'work') return renderWorkList();
  if (state.view === 'graph') return renderGraph();
  if (typeMeta[state.view]) return renderRecordList(state.view);
  if (state.view === 'history') return renderHistory();
  if (state.view === 'principles') return renderPrinciples();
  if (state.view === 'structure') return renderStructure();
  if (state.view === 'notifications') return renderNotifications();
}

function renderDashboard() {
  const work = state.records.filter((record) => isWorkRecord(record) && isActiveRecord(record));
  const myWork = work.filter((record) => record.ownerId === state.me.id);
  const attention = myWork.filter((record) => ['overdue', 'urgent'].includes(deadlineState(record).className) || ['high', 'critical'].includes(record.priority));
  const pendingRecordIDs = new Set(state.pendingQuestions.map((question) => question.recordId));
  const focusWork = myWork.filter((record) => record.type !== 'question_set' || !pendingRecordIDs.has(record.id)).slice().sort(sortWorkRecords).slice(0, 4);
  const focusItems = [
    ...state.pendingQuestions.map((question) => ({ kind: 'question', question })),
    ...focusWork.map((record) => ({ kind: 'work', record })),
  ].slice(0, 4);
  $('#main-content').innerHTML = `
    <section class="workbench-grid">
      <article class="focus-panel">
        <div class="section-heading inverse"><div><p class="eyebrow">${attention.length ? `${attention.length} требуют внимания` : 'В порядке приоритета'}</p><h2>Следующая работа</h2></div><button class="text-button" data-go="work">Открыть всё ${icon('chevronRight')}</button></div>
        <div class="focus-list">${focusItems.length ? focusItems.map((item, index) => item.kind === 'work' ? renderFocusRecord(item.record, index === 0) : renderFocusQuestion(item.question, index === 0)).join('') : `<div class="focus-empty">${icon('check')}<strong>Открытой работы нет</strong><span>Создайте следующий конкретный шаг.</span></div>`}</div>
      </article>
      <aside class="capture-panel">
        <div><p class="eyebrow">Создать</p><h3>Быстрая фиксация</h3></div>
        <div class="quick-actions"><button type="button" class="quick-action idea" data-quick-create="idea"><span class="quick-icon">${icon('lightbulb')}</span><span><strong>Идея</strong><small>Название, детали позже</small></span>${icon('chevronRight')}</button><button type="button" class="quick-action task" data-quick-create="task"><span class="quick-icon">${icon('checkSquare')}</span><span><strong>Задача</strong><small>Кто, что и когда</small></span>${icon('chevronRight')}</button><button type="button" class="quick-action discussion" data-quick-create="meeting"><span class="quick-icon">${icon('calendar')}</span><span><strong>Встреча</strong><small>Заметки и результаты</small></span>${icon('chevronRight')}</button><button type="button" class="quick-action discussion" data-quick-create="question_set"><span class="quick-icon">${icon('messages')}</span><span><strong>Вопросы</strong><small>Два ответа и итог</small></span>${icon('chevronRight')}</button></div>
      </aside>
    </section>
    <section class="dashboard-grid">
      <div class="section-panel">
        <div class="section-heading"><div><p class="eyebrow">Команда</p><h3>Распределение работы</h3></div><span class="panel-note">${minutesLabel(work.reduce((sum, item) => sum + item.estimateMinutes, 0))} в плане</span></div>
        <div class="people-load">${state.users.map((user) => renderPersonLoad(user, work)).join('') || emptyState('Второй участник появится после регистрации.')}</div>
      </div>
      <div class="section-panel">
        <div class="section-heading"><div><p class="eyebrow">Командный радар</p><h3>Приоритеты и сроки</h3></div><button class="text-button" data-go="work">Открыть список</button></div>
        <div class="compact-list">${work.slice().sort(sortWorkRecords).slice(0, 7).map(renderCompactRecord).join('') || emptyState('Активной работы пока нет.')}</div>
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
  return `<button type="button" class="focus-record ${primary ? 'primary-focus' : ''}" data-open-record="${record.id}"><span class="focus-marker">${icon(typeMeta[record.type].icon)}</span><span class="focus-copy"><small>${primary ? 'Следующая работа' : escapeHTML(typeMeta[record.type].singular)} · ${escapeHTML(record.ownerUsername)}</small><strong>${escapeHTML(record.title)}</strong><span><em class="priority priority-${record.priority || 'normal'}">${priorityLabels[record.priority || 'normal']}</em><em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em></span></span><span class="focus-progress"><b>${record.progress}%</b><progress class="focus-meter" max="100" value="${record.progress}"></progress></span>${icon('chevronRight', 'row-chevron')}</button>`;
}

function renderFocusQuestion(question, primary = false) {
  const deadline = question.dueAt ? formatDate(question.dueAt) : 'Без срока';
  return `<button type="button" class="focus-record focus-question ${primary ? 'primary-focus' : ''}" data-open-record="${question.recordId}"><span class="focus-marker">${icon('messages')}</span><span class="focus-copy"><small>Ждёт вашего ответа · ${escapeHTML(question.recordTitle)}</small><strong>${escapeHTML(question.body)}</strong><em class="deadline normal">${escapeHTML(deadline)}</em></span><span class="focus-progress"><b>Ответить</b><progress class="focus-meter" max="100" value="0"></progress></span>${icon('chevronRight', 'row-chevron')}</button>`;
}

function renderPersonLoad(user, tasks) {
  const owned = tasks.filter((task) => task.ownerId === user.id);
  const minutes = owned.reduce((sum, task) => sum + task.estimateMinutes, 0);
  const progress = owned.length ? Math.round(owned.reduce((sum, task) => sum + task.progress, 0) / owned.length) : 0;
  return `<button type="button" class="person-load" data-user-profile="${user.id}"><span class="avatar">${escapeHTML(user.username.slice(0, 2).toUpperCase())}</span><span class="person-main"><strong>${escapeHTML(user.username)}</strong><small>${recordsCountLabel(owned.length)} · ${minutesLabel(minutes)}</small><progress class="progress-track" max="100" value="${progress}"></progress></span><b>${progress}%</b></button>`;
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
  if (!a.dueAt && !b.dueAt) return 0;
  if (!a.dueAt) return 1;
  if (!b.dueAt) return -1;
  return new Date(a.dueAt) - new Date(b.dueAt);
}

function renderCompactRecord(record) {
  const deadline = deadlineState(record);
  return `<button type="button" class="compact-record" data-open-record="${record.id}"><span class="type-icon type-${record.type}">${icon(typeMeta[record.type].icon)}</span><span><strong>${escapeHTML(record.title)}</strong><small>${escapeHTML(record.ownerUsername)} · ${minutesLabel(record.estimateMinutes)}</small></span><em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em>${icon('chevronRight', 'row-chevron')}</button>`;
}

function renderWorkList() {
  let records = state.records.filter((record) => isWorkRecord(record));
  if (state.ownerFilter) records = records.filter((record) => String(record.ownerId) === state.ownerFilter);
  else if (state.workScope === 'mine') records = records.filter((record) => record.ownerId === state.me.id);
  else if (state.workScope === 'partner') records = records.filter((record) => record.ownerId !== state.me.id);
  if (state.workType !== 'all') records = records.filter((record) => record.type === state.workType);
  if (state.workstreamFilter !== 'all') records = records.filter((record) => record.workstream === state.workstreamFilter);
  if (state.workStatus === 'active') records = records.filter(isActiveRecord);
  if (state.workStatus === 'overdue') records = records.filter((record) => isActiveRecord(record) && deadlineState(record).className === 'overdue');
  if (state.workStatus === 'completed') records = records.filter((record) => record.status === 'completed');
  if (state.workStatus === 'archived') records = records.filter((record) => record.status === 'archived');
  if (state.search) {
    const query = state.search.toLowerCase();
    records = records.filter((record) => `${record.title} ${record.description} ${record.ownerUsername}`.toLowerCase().includes(query));
  }
  records.sort(sortWorkRecords);
  const typeFilters = [
    ['all', 'Вся работа'], ['task', 'Задачи'], ['question_set', 'Вопросы'], ['research', 'Исследования'],
    ['decision', 'Решения'], ['disagreement', 'Разногласия'], ['meeting', 'Встречи'],
  ];
  $('#main-content').innerHTML = `
    <div class="work-title-row"><div><h1>Работа команды</h1><p>Все обязательства, обсуждения и исследования в одной очереди.</p></div><div class="work-create"><button type="button" class="secondary" data-work-create="question_set">${icon('messages')} Вопросы</button><button type="button" class="primary" data-work-create="task">${icon('plus')} Задача</button></div></div>
    <section class="work-controls" aria-label="Фильтры рабочей очереди">
      <div class="work-scope segmented compact">${[['all', 'Вся'], ['mine', 'Моя'], ['partner', 'Партнёра']].map(([value, label]) => `<button type="button" class="segment ${!state.ownerFilter && state.workScope === value ? 'active' : ''}" data-work-scope="${value}">${label}</button>`).join('')}</div>
      <div class="search-box work-search">${icon('search')}<input id="work-search" type="search" placeholder="Фильтр этой очереди" value="${escapeHTML(state.search)}"></div>
      <div class="work-status-tabs">${[['active', 'Активная'], ['overdue', 'Просрочена'], ['completed', 'Выполнена'], ['archived', 'Архив'], ['all', 'Вся']].map(([value, label]) => `<button type="button" class="${state.workStatus === value ? 'active' : ''}" data-work-status="${value}">${label}</button>`).join('')}</div>
    </section>
    <div class="workstream-tabs">${[['all', 'Все направления'], ...Object.entries(workstreamLabels)].map(([value, label]) => `<button type="button" class="workstream-${value} ${state.workstreamFilter === value ? 'active' : ''}" data-workstream-filter="${value}">${escapeHTML(label)}</button>`).join('')}</div>
    <div class="work-type-tabs">${typeFilters.map(([value, label]) => `<button type="button" class="${state.workType === value ? 'active' : ''}" data-work-type="${value}">${escapeHTML(label)}<b>${state.records.filter((record) => isWorkRecord(record) && (value === 'all' || record.type === value) && record.status !== 'archived').length}</b></button>`).join('')}</div>
    <section class="table-panel work-table-panel">
      <div class="record-table work-header"><span>Работа</span><span>Ответственный</span><span>Приоритет / статус</span><span>Срок / прогресс</span></div>
      <div class="record-rows">${records.map(renderWorkRow).join('') || `<div class="guided-empty work-empty">${icon('checkSquare')}<h3>В этом фильтре работы нет</h3><p>Измените фильтр или создайте следующий конкретный шаг.</p></div>`}</div>
    </section>`;
  $('#work-search').addEventListener('input', (event) => { state.search = event.target.value; renderWorkList(); });
  $$('[data-work-scope]').forEach((button) => button.addEventListener('click', () => { state.ownerFilter = ''; state.workScope = button.dataset.workScope; renderWorkList(); }));
  $$('[data-work-status]').forEach((button) => button.addEventListener('click', () => { state.workStatus = button.dataset.workStatus; renderWorkList(); }));
  $$('[data-work-type]').forEach((button) => button.addEventListener('click', () => { state.workType = button.dataset.workType; renderWorkList(); }));
  $$('[data-workstream-filter]').forEach((button) => button.addEventListener('click', () => { state.workstreamFilter = button.dataset.workstreamFilter; renderWorkList(); }));
  $$('[data-work-create]').forEach((button) => button.addEventListener('click', () => openCreateDialog(button.dataset.workCreate)));
  bindOpenRecords();
}

function renderWorkRow(record) {
  const deadline = deadlineState(record);
  const priority = record.priority || 'normal';
  return `<button type="button" class="record-table row work-row" data-open-record="${record.id}">
    <span class="record-title"><i class="type-icon type-${record.type}">${icon(typeMeta[record.type].icon)}</i><span><small>${escapeHTML(typeMeta[record.type].singular)} · <b class="workstream-mark workstream-${record.workstream || 'business'}">${escapeHTML(workstreamLabels[record.workstream || 'business'])}</b>${record.isRoot ? ' · Корень' : ''}</small><strong>${escapeHTML(record.title)}</strong><em>${escapeHTML(record.description || 'Без дополнительного контекста')}</em></span></span>
    <span><b class="owner-chip">${escapeHTML(record.ownerUsername)}</b><small>${record.editPolicy === 'owner_only' ? 'Только владелец' : 'Общая'} · ${minutesLabel(record.estimateMinutes)}</small></span>
    <span><em class="priority priority-${priority}">${icon('flag')} ${priorityLabels[priority]}</em><small>${escapeHTML(statusLabels[record.status] || record.status)}</small></span>
    <span><em class="deadline ${deadline.className}">${escapeHTML(deadline.label)}</em><progress class="progress-track" max="100" value="${record.progress}"></progress><small>${record.progress}%</small></span>
  </button>`;
}

async function renderGraph() {
  $('#main-content').classList.add('graph-main-content');
  $('#main-content').innerHTML = `
    <section class="graph-workspace">
      <header class="graph-toolbar">
        <div class="graph-mode segmented compact"><button type="button" class="segment ${!state.graphFocusRecordId ? 'active' : ''}" data-graph-mode="global">Весь проект</button><button type="button" class="segment ${state.graphFocusRecordId ? 'active' : ''}" data-graph-mode="local" ${state.graphFocusRecordId ? '' : 'disabled'}>Локальная карта</button></div>
        <div class="search-box graph-search">${icon('search')}<input id="graph-search" type="search" value="${escapeHTML(state.graphSearch)}" placeholder="Найти узел на карте"></div>
        <select id="graph-type-filter" aria-label="Тип узлов"><option value="all">Все типы</option>${Object.entries(typeMeta).map(([type, meta]) => `<option value="${type}" ${state.graphTypeFilter === type ? 'selected' : ''}>${meta.label}</option>`).join('')}</select>
        <label class="graph-toggle"><input id="graph-discussions" type="checkbox" ${state.graphShowDiscussion ? 'checked' : ''}> Вопросы и ответы</label>
        ${state.graphFocusRecordId ? `<label class="graph-depth">Глубина <input id="graph-depth" type="range" min="1" max="4" value="${state.graphDepth}"><b>${state.graphDepth}</b></label>` : ''}
        <div class="graph-icon-actions"><button type="button" class="icon-button" id="graph-relayout" title="Перестроить карту" aria-label="Перестроить карту">${icon('rotate')}</button><button type="button" class="icon-button" id="graph-fit" title="Показать карту целиком" aria-label="Показать карту целиком">${icon('maximize')}</button></div>
      </header>
      <div class="graph-stage"><div id="relationship-graph" role="application" aria-label="Интерактивная карта связей"><div class="graph-loading"><span class="spinner"></span><strong>Строим карту проекта</strong></div></div><aside id="graph-inspector" class="graph-inspector ${state.graphSelectedId ? 'open' : ''}">${renderGraphInspector()}</aside></div>
      <footer class="graph-legend"><span><i class="legend-card"></i> Карточка</span><span><i class="legend-question"></i> Вопрос</span><span><i class="legend-answer"></i> Ответ</span><span><i class="legend-decision"></i> Итог</span><em>Колесо или жест: масштаб · перетаскивание: перемещение · двойное нажатие: открыть</em></footer>
    </section>`;
  bindGraphControls();
  try {
    if (!state.graphData) state.graphData = await api('/api/graph');
    if (state.view !== 'graph') return;
    mountGraph();
  } catch (error) {
    $('#relationship-graph').innerHTML = `<div class="graph-error">${icon('help')}<strong>Карта не загрузилась</strong><p>${escapeHTML(error.message)}</p><button type="button" class="secondary" id="graph-retry">Повторить</button></div>`;
    $('#graph-retry')?.addEventListener('click', () => { state.graphData = null; renderGraph(); });
  }
}

function graphVisibleElements() {
  const data = state.graphData || { nodes: [], edges: [] };
  const nodeByID = new Map(data.nodes.map((node) => [node.id, node]));
  let allowed = new Set(data.nodes.map((node) => node.id));
  if (!state.graphShowDiscussion) allowed = new Set([...allowed].filter((id) => nodeByID.get(id)?.entityKind === 'record'));
  if (state.graphTypeFilter !== 'all') {
    allowed = new Set([...allowed].filter((id) => nodeByID.get(id)?.type === state.graphTypeFilter));
  }
  if (state.graphFocusRecordId) {
    const root = `record:${state.graphFocusRecordId}`;
    const adjacency = new Map(data.nodes.map((node) => [node.id, new Set()]));
    data.edges.forEach((edge) => {
      adjacency.get(edge.source)?.add(edge.target);
      adjacency.get(edge.target)?.add(edge.source);
    });
    const local = new Set([root]);
    let frontier = [root];
    for (let depth = 0; depth < state.graphDepth; depth += 1) {
      const next = [];
      frontier.forEach((id) => (adjacency.get(id) || []).forEach((neighbor) => { if (!local.has(neighbor)) { local.add(neighbor); next.push(neighbor); } }));
      frontier = next;
    }
    allowed = new Set([...allowed].filter((id) => local.has(id)));
  }
  const nodes = data.nodes.filter((node) => allowed.has(node.id));
  const edges = data.edges.filter((edge) => allowed.has(edge.source) && allowed.has(edge.target));
  return { nodes, edges };
}

function graphNodeSize(node) {
  if (node.entityKind !== 'record') return node.entityKind === 'joint_decision' ? 44 : 34;
  const degree = (state.graphData?.edges || []).filter((edge) => edge.source === node.id || edge.target === node.id).length;
  return Math.min(66, 42 + degree * 3);
}

function mountGraph() {
  if (!window.cytoscape) throw new Error('Модуль визуализации не загружен');
  if (state.graphInstance) state.graphInstance.destroy();
  const { nodes, edges } = graphVisibleElements();
  const elements = [
    ...nodes.map((node) => ({ data: { ...node, label: node.title, size: graphNodeSize(node) }, classes: `kind-${node.entityKind} type-${node.type} ${node.status === 'archived' ? 'is-archived' : ''}` })),
    ...edges.map((edge) => ({ data: { id: edge.id, source: edge.source, target: edge.target, label: edge.label, relationType: edge.relationType }, classes: `relation-${edge.relationType}` })),
  ];
  const container = $('#relationship-graph');
  container.innerHTML = '';
  const cy = window.cytoscape({
    container, elements, minZoom: .18, maxZoom: 2.4, wheelSensitivity: .18,
    style: [
      { selector: 'node', style: { width: 'data(size)', height: 'data(size)', label: 'data(label)', 'font-family': 'Inter Local, sans-serif', 'font-size': 11, 'font-weight': 600, color: '#25302b', 'text-wrap': 'wrap', 'text-max-width': 150, 'text-valign': 'bottom', 'text-margin-y': 9, 'background-color': '#f6f6f1', 'border-width': 2, 'border-color': '#73867e', 'overlay-opacity': 0 } },
      { selector: 'node.kind-question', style: { shape: 'round-rectangle', width: 42, height: 42, 'background-color': '#e6edf0', 'border-color': '#547b88', 'font-size': 10 } },
      { selector: 'node.kind-answer', style: { shape: 'ellipse', width: 32, height: 32, 'background-color': '#f5f0de', 'border-color': '#a87a25', 'font-size': 9 } },
      { selector: 'node.kind-joint_decision', style: { shape: 'diamond', width: 44, height: 44, 'background-color': '#dceae3', 'border-color': '#26705a', 'font-size': 10 } },
      { selector: 'node.type-idea', style: { 'background-color': '#fbefd4', 'border-color': '#aa711d' } },
      { selector: 'node.type-goal', style: { 'background-color': '#f6e5dc', 'border-color': '#b85c3e' } },
      { selector: 'node.type-task', style: { 'background-color': '#dce9e4', 'border-color': '#1f6657' } },
      { selector: 'node.type-question_set', style: { 'background-color': '#e1e9ec', 'border-color': '#456b78' } },
      { selector: 'node.type-criterion', style: { 'background-color': '#ebe7dd', 'border-color': '#6d6654' } },
      { selector: 'node:selected', style: { 'border-width': 4, 'border-color': '#101714', 'background-color': '#ffffff', 'underlay-color': '#1f6657', 'underlay-opacity': .13, 'underlay-padding': 9 } },
      { selector: 'edge', style: { width: 1.5, 'curve-style': 'bezier', 'line-color': '#aab4af', 'target-arrow-color': '#aab4af', 'target-arrow-shape': 'triangle', 'arrow-scale': .7, label: 'data(label)', 'font-family': 'Inter Local, sans-serif', 'font-size': 8, color: '#66716c', 'text-background-color': '#e9ebe8', 'text-background-opacity': .85, 'text-background-padding': 3, 'text-rotation': 'autorotate', 'overlay-opacity': 0 } },
      { selector: 'edge.relation-produced, edge.relation-leads_to', style: { width: 2.3, 'line-color': '#4c8172', 'target-arrow-color': '#4c8172' } },
      { selector: '.is-dimmed', style: { opacity: .12, 'text-opacity': 0 } },
      { selector: '.is-neighbor', style: { 'border-width': 3, 'border-color': '#1f6657' } },
      { selector: '.link-source', style: { 'border-width': 5, 'border-color': '#c33f51', 'underlay-color': '#c33f51', 'underlay-opacity': .12, 'underlay-padding': 10 } },
    ],
    layout: { name: nodes.length > 1 ? 'cose' : 'grid', animate: nodes.length < 120, animationDuration: 720, randomize: true, nodeRepulsion: 8000, idealEdgeLength: 105, edgeElasticity: 90, gravity: .18, componentSpacing: 90, fit: true, padding: 70 },
  });
  state.graphInstance = cy;
  cy.on('tap', 'node', (event) => selectGraphNode(event.target.id()));
  cy.on('mouseover', 'node', (event) => highlightGraphNeighborhood(event.target));
  cy.on('mouseout', 'node', () => applyGraphSearch());
  cy.on('tap', (event) => { if (event.target === cy) selectGraphNode(''); });
  let lastTapped = { id: '', time: 0 };
  cy.on('tap', 'node', (event) => {
    const now = Date.now(); const id = event.target.id();
    if (lastTapped.id === id && now - lastTapped.time < 360) openGraphNode(event.target.data());
    lastTapped = { id, time: now };
  });
  if (state.graphSelectedId && cy.$id(state.graphSelectedId).length) selectGraphNode(state.graphSelectedId, true);
  else if (state.graphFocusRecordId && cy.$id(`record:${state.graphFocusRecordId}`).length) selectGraphNode(`record:${state.graphFocusRecordId}`, true);
  applyGraphSearch();
}

function highlightGraphNeighborhood(node) {
  const cy = state.graphInstance;
  if (!cy) return;
  cy.elements().addClass('is-dimmed').removeClass('is-neighbor');
  const neighborhood = node.closedNeighborhood();
  neighborhood.removeClass('is-dimmed').addClass('is-neighbor');
  node.removeClass('is-neighbor');
}

function applyGraphSearch() {
  const cy = state.graphInstance;
  if (!cy) return;
  cy.elements().removeClass('is-dimmed is-neighbor');
  const query = state.graphSearch.trim().toLowerCase();
  if (!query) return;
  const matches = cy.nodes().filter((node) => `${node.data('title')} ${node.data('description') || ''}`.toLowerCase().includes(query));
  cy.elements().addClass('is-dimmed');
  matches.forEach((node) => node.closedNeighborhood().removeClass('is-dimmed'));
  if (matches.length) cy.animate({ fit: { eles: matches, padding: 120 }, duration: 260 });
}

function selectGraphNode(id, skipCenter = false) {
  const cy = state.graphInstance;
  if (!cy) return;
  state.graphSelectedId = id;
  cy.$(':selected').unselect();
  if (id && cy.$id(id).length) {
    cy.$id(id).select();
    if (!skipCenter) cy.animate({ center: { eles: cy.$id(id) }, zoom: Math.max(cy.zoom(), .9), duration: 240 });
  }
  $('#graph-inspector').innerHTML = renderGraphInspector();
  bindGraphInspector();
  $('#graph-inspector').classList.toggle('open', Boolean(id));
}

function renderGraphInspector() {
  const node = state.graphData?.nodes.find((item) => item.id === state.graphSelectedId);
  if (!node) return `<div class="graph-inspector-empty">${icon('network')}<strong>Выберите объект</strong><p>Здесь появятся содержание, ближайшие связи и быстрые действия.</p></div>`;
  const meta = typeMeta[node.type] || { singular: node.entityKind === 'question' ? 'Вопрос' : node.entityKind === 'answer' ? 'Ответ основателя' : node.entityKind === 'joint_decision' ? 'Совместный итог' : 'Объект', icon: node.entityKind === 'joint_decision' ? 'scale' : 'messages' };
  const edges = (state.graphData?.edges || []).filter((edge) => edge.source === node.id || edge.target === node.id);
  const neighbors = edges.slice(0, 8).map((edge) => {
    const targetID = edge.source === node.id ? edge.target : edge.source;
    const target = state.graphData.nodes.find((item) => item.id === targetID);
    return target ? `<button type="button" data-graph-neighbor="${target.id}"><span>${escapeHTML(edge.label)}</span><strong>${escapeHTML(target.title)}</strong></button>` : '';
  }).join('');
  const recordNode = node.entityKind === 'record';
  const canLink = recordNode && (node.editPolicy !== 'owner_only' || node.ownerUsername === state.me.username);
  const sourceActive = state.graphLinkSourceId === node.id;
  const context = recordNode ? `<div class="graph-node-context"><span class="workstream-mark workstream-${node.workstream || 'business'}">${escapeHTML(workstreamLabels[node.workstream || 'business'])}</span>${node.isRoot ? '<span class="root-mark">Новый корень</span>' : ''}${node.editPolicy === 'owner_only' ? `<span class="access-mark">${icon('lock')} Только владелец</span>` : ''}</div>` : '';
  return `<div class="graph-inspector-head"><span class="type-icon">${icon(meta.icon)}</span><button type="button" class="icon-button" data-close-graph-inspector aria-label="Закрыть">${icon('x')}</button></div><small>${escapeHTML(meta.singular)}${node.ownerUsername ? ` · ${escapeHTML(node.ownerUsername)}` : ''}</small><h2>${escapeHTML(node.title)}</h2>${context}${node.description ? `<p>${escapeHTML(node.description).replace(/\n/g, '<br>')}</p>` : ''}<div class="graph-inspector-actions"><button type="button" class="primary" data-open-graph-node>${icon('chevronRight')} Открыть</button><button type="button" class="secondary" data-focus-graph-node>${icon('network')} В фокус</button>${canLink ? `<button type="button" class="secondary ${sourceActive ? 'danger-action' : ''}" data-graph-link-source>${icon('link')} ${sourceActive ? 'Отменить связь' : state.graphLinkSourceId ? 'Связать сюда' : 'Создать связь'}</button>` : ''}</div>${state.graphLinkSourceId && state.graphLinkSourceId !== node.id && recordNode ? `<div class="graph-link-callout"><strong>Создать связь с выбранной карточкой?</strong><select id="graph-relation-type"><option value="related">Связано</option><option value="supports">Поддерживает</option><option value="depends_on">Зависит от</option><option value="leads_to">Приводит к</option></select><button type="button" class="primary" data-confirm-graph-link>Связать</button></div>` : ''}<section class="graph-neighbors"><header><span>Ближайшие связи</span><b>${edges.length}</b></header>${neighbors || '<p>Связей пока нет.</p>'}</section>`;
}

function bindGraphControls() {
  $$('[data-graph-mode]').forEach((button) => button.addEventListener('click', () => { if (button.dataset.graphMode === 'global') state.graphFocusRecordId = ''; renderGraph(); }));
  $('#graph-search').addEventListener('input', (event) => { state.graphSearch = event.target.value; applyGraphSearch(); });
  $('#graph-type-filter').addEventListener('change', (event) => { state.graphTypeFilter = event.target.value; mountGraph(); });
  $('#graph-discussions').addEventListener('change', (event) => { state.graphShowDiscussion = event.target.checked; mountGraph(); });
  $('#graph-depth')?.addEventListener('input', (event) => { state.graphDepth = Number(event.target.value); event.target.nextElementSibling.textContent = String(state.graphDepth); mountGraph(); });
  $('#graph-fit').addEventListener('click', () => state.graphInstance?.animate({ fit: { eles: state.graphInstance.elements(':visible'), padding: 70 }, duration: 320 }));
  $('#graph-relayout').addEventListener('click', () => state.graphInstance?.layout({ name: 'cose', animate: true, animationDuration: 650, randomize: true, nodeRepulsion: 8000, idealEdgeLength: 105, gravity: .18, fit: true, padding: 70 }).run());
}

function bindGraphInspector() {
  $('[data-close-graph-inspector]')?.addEventListener('click', () => selectGraphNode(''));
  $('[data-open-graph-node]')?.addEventListener('click', () => {
    const node = state.graphData.nodes.find((item) => item.id === state.graphSelectedId); if (node) openGraphNode(node);
  });
  $('[data-focus-graph-node]')?.addEventListener('click', () => {
    const node = state.graphData.nodes.find((item) => item.id === state.graphSelectedId); if (!node) return;
    state.graphFocusRecordId = node.recordId; state.graphDepth = 2; renderGraph();
  });
  $$('[data-graph-neighbor]').forEach((button) => button.addEventListener('click', () => selectGraphNode(button.dataset.graphNeighbor)));
  $('[data-graph-link-source]')?.addEventListener('click', () => {
    const node = state.graphData.nodes.find((item) => item.id === state.graphSelectedId); if (!node || node.entityKind !== 'record') return;
    if (!state.graphLinkSourceId) state.graphLinkSourceId = node.id;
    else if (state.graphLinkSourceId === node.id) state.graphLinkSourceId = '';
    $('#graph-inspector').innerHTML = renderGraphInspector(); bindGraphInspector();
    state.graphInstance.nodes().removeClass('link-source');
    if (state.graphLinkSourceId) state.graphInstance.$id(state.graphLinkSourceId).addClass('link-source');
  });
  $('[data-confirm-graph-link]')?.addEventListener('click', createGraphLink);
}

async function createGraphLink() {
  const source = state.graphData.nodes.find((item) => item.id === state.graphLinkSourceId);
  const target = state.graphData.nodes.find((item) => item.id === state.graphSelectedId);
  if (!source || !target || source.entityKind !== 'record' || target.entityKind !== 'record') return;
  try {
    await api(`/api/records/${source.recordId}/links`, { method: 'POST', body: JSON.stringify({ targetId: target.recordId, relationType: $('#graph-relation-type').value, reason: 'Связь создана на карте проекта' }) });
    state.graphData = await api('/api/graph'); state.graphLinkSourceId = ''; state.detailCache.delete(source.recordId); state.detailCache.delete(target.recordId); mountGraph(); selectGraphNode(target.id, true); toast('Связь добавлена');
  } catch (error) { toast(error.message, true); }
}

function openGraphNode(node) {
  if (!node?.recordId) return;
  openRecord(node.recordId, { tab: node.questionId ? 'questions' : 'overview', questionId: node.questionId, workspace: false });
}

function openGraphForRecord(recordId) {
  $('#record-dialog').close();
  state.graphFocusRecordId = recordId; state.graphSelectedId = `record:${recordId}`; state.graphDepth = 2; state.view = 'graph'; render();
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
  $$('[data-owner-filter]').forEach((node) => node.addEventListener('click', () => navigateToView('work', { ownerId: node.dataset.ownerFilter })));
  $$('[data-user-profile]').forEach((node) => node.addEventListener('click', () => openProfile(Number(node.dataset.userProfile))));
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

function addRecordWorkspaceItem(id, summary, preserve) {
  if (!preserve) state.recordWorkspace = [];
  const existing = state.recordWorkspace.find((item) => item.id === id);
  if (!existing) {
    state.recordWorkspace.push({ id, title: summary?.title || 'Карточка', type: summary?.type || 'document' });
    if (state.recordWorkspace.length > 6) state.recordWorkspace.shift();
  } else if (summary) {
    existing.title = summary.title;
    existing.type = summary.type;
  }
  state.activeWorkspaceRecordId = id;
}

async function openRecord(id, options = {}) {
  const requestID = ++state.activeRecordRequest;
  const cached = cachedRecordDetail(id);
  const summary = state.records.find((record) => record.id === id);
  const preserveWorkspace = Boolean(options.workspace || ($('#record-dialog').open && state.recordWorkspace.length));
  addRecordWorkspaceItem(id, cached?.record || summary, preserveWorkspace);
  state.focusQuestionId = options.questionId || '';
  state.activeRecordTab = options.tab || ((cached?.record.type || summary?.type) === 'question_set' ? 'questions' : 'overview');
  if (cached) {
    state.activeDetail = cached;
    renderRecordDialog();
  } else {
    state.activeDetail = null;
    renderRecordLoading(summary);
  }
  openModal($('#record-dialog'));
  try {
    const detail = await fetchRecordDetail(id, Boolean(cached));
    if (requestID !== state.activeRecordRequest || !$('#record-dialog').open) return;
    state.activeDetail = detail;
    addRecordWorkspaceItem(id, detail.record, true);
    renderRecordDialog();
  } catch (error) {
    if (requestID === state.activeRecordRequest) renderRecordLoadError(id, error.message);
  }
}

function renderRecordWorkspace() {
  if (state.recordWorkspace.length < 2) return '';
  return `<nav class="record-workspace-bar" aria-label="Открытые связанные карточки">${state.recordWorkspace.map((item) => `<span class="workspace-tab ${item.id === state.activeWorkspaceRecordId ? 'active' : ''}"><button type="button" data-workspace-record="${item.id}">${icon(typeMeta[item.type]?.icon || 'fileText')}<b>${escapeHTML(item.title)}</b></button><button type="button" data-close-workspace="${item.id}" aria-label="Закрыть ${escapeHTML(item.title)}">${icon('x')}</button></span>`).join('')}</nav>`;
}

function bindRecordWorkspace() {
  $$('[data-workspace-record]').forEach((button) => button.addEventListener('click', () => openRecord(button.dataset.workspaceRecord, { workspace: true })));
  $$('[data-close-workspace]').forEach((button) => button.addEventListener('click', async (event) => {
    event.stopPropagation();
    const id = button.dataset.closeWorkspace;
    const index = state.recordWorkspace.findIndex((item) => item.id === id);
    state.recordWorkspace = state.recordWorkspace.filter((item) => item.id !== id);
    if (id !== state.activeWorkspaceRecordId) { renderRecordDialog(); return; }
    const next = state.recordWorkspace[Math.max(0, index - 1)];
    if (!next) { $('#record-dialog').close(); return; }
    await openRecord(next.id, { workspace: true });
  }));
}

function renderRecordLoading(summary) {
  const meta = typeMeta[summary?.type] || { singular: 'Карточка', icon: 'fileText' };
  $('#record-dialog-content').innerHTML = `<div class="record-shell record-type-${summary?.type || 'document'} loading-shell ${state.recordWorkspace.length > 1 ? 'has-workspace' : ''}">${renderRecordWorkspace()}<div class="dialog-header record-dialog-header"><div><span class="record-kind">${icon(meta.icon)} ${escapeHTML(meta.singular)}</span><h2>${escapeHTML(summary?.title || 'Загружаем карточку')}</h2><p>Основные данные появятся сразу после ответа сервера</p></div><button type="button" class="close-button icon-button" data-close-dialog aria-label="Закрыть">${icon('x')}</button></div><div class="loading-tabs"><i></i><i></i><i></i></div><div class="dialog-layout"><div class="dialog-main"><div class="record-skeleton"><span class="skeleton-line wide"></span><span class="skeleton-line medium"></span><span class="skeleton-block"></span><div><span class="skeleton-line"></span><span class="skeleton-line short"></span></div></div></div><aside class="dialog-aside"><span class="skeleton-line"></span><span class="skeleton-line short"></span><span class="skeleton-line"></span></aside></div></div>`;
  $('[data-close-dialog]').addEventListener('click', () => $('#record-dialog').close());
  bindRecordWorkspace();
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

function nextRecordOptions(record) {
  return {
    goal: [['task', '', 'Задача'], ['criterion', 'preference', 'Критерий'], ['research', '', 'Исследование']],
    task: [['decision', '', 'Решение'], ['document', '', 'Документ'], ['question_set', '', 'Вопросы']],
    question_set: [['decision', 'insight', 'Вывод'], ['task', '', 'Задача'], ['criterion', 'preference', 'Критерий']],
    idea: [['research', '', 'Исследование'], ['task', '', 'Задача'], ['decision', '', 'Решение']],
    research: [['decision', '', 'Решение'], ['criterion', 'preference', 'Критерий'], ['task', '', 'Задача']],
    decision: [['task', '', 'Задача'], ['goal', '', 'Цель'], ['decision', 'rule', 'Правило']],
    disagreement: [['decision', '', 'Решение'], ['decision', 'rule', 'Правило'], ['question_set', '', 'Вопросы']],
    criterion: [['research', '', 'Исследование'], ['idea', '', 'Идея']],
    document: [['task', '', 'Задача'], ['decision', '', 'Решение']],
    meeting: [['task', '', 'Задача'], ['decision', '', 'Решение'], ['criterion', 'limitation', 'Ограничение'], ['idea', '', 'Идея'], ['research', '', 'Исследование']],
  }[record.type] || [];
}

function renderNextActions(record) {
  const options = nextRecordOptions(record);
  if (!options.length) return '';
  return `<section class="meeting-results next-actions"><header><div><p class="eyebrow">Следующий результат</p><h3>Продолжить цепочку</h3></div><button type="button" class="text-button" data-record-graph="${record.id}">${icon('network')} Посмотреть связи</button></header><div>${options.map(([type, kind, label]) => `<button type="button" data-create-linked="${type}" data-linked-kind="${kind}">${icon(typeMeta[type].icon)} ${label}</button>`).join('')}</div></section>`;
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
  const hasPriority = isWorkRecord(record) || record.type === 'goal';
  const hasEstimate = isWorkRecord(record) || record.type === 'goal';
  const hasManualProgress = record.type !== 'question_set' && (isWorkRecord(record) || record.type === 'goal');
  const hasResult = ['task', 'goal', 'research', 'decision', 'disagreement'].includes(record.type);
  const planningTitle = record.type === 'task' ? 'Исполнение' : record.type === 'meeting' ? 'Организатор и время' : hasDecisionMaker ? 'Ответственность за решение' : hasDeadline ? 'Планирование' : 'Владелец карточки';
  const dueLabel = ({ meeting: 'Дата и время', research: 'Срок исследования', decision: 'Срок решения', disagreement: 'Срок разбора' })[record.type] || 'Срок';
  const planningGrid = hasDecisionMaker && hasDeadline ? 'three' : hasDeadline ? 'two' : 'one';
  const origin = state.activeDetail.derivation;
  const canEdit = record.editPolicy !== 'owner_only' || record.ownerId === state.me.id;
  const canManageAccess = record.ownerId === state.me.id;
  const parentOptions = state.records.filter((item) => item.id !== record.id && item.status !== 'archived').map((item) => `<option value="${item.id}" ${record.parentId === item.id ? 'selected' : ''}>${escapeHTML(typeMeta[item.type]?.singular || 'Карточка')}: ${escapeHTML(item.title)}</option>`).join('');
  return `<div class="record-pane ${state.activeRecordTab === 'overview' ? 'active' : ''}" data-record-pane="overview">
    ${origin ? `<button type="button" class="origin-trace" data-related-record="${origin.sourceRecordId}"><span>${icon('link')}</span><span><small>Создано из совместного вывода</small><strong>${escapeHTML(origin.questionBody)}</strong><em>${escapeHTML(origin.decisionContent)}</em></span>${icon('chevronRight')}</button>` : ''}
    ${draft ? `<div class="draft-banner"><span><strong>Найден несохранённый черновик</strong><small>Можно восстановить текст или удалить черновик.</small></span><div><button type="button" class="secondary" data-restore-draft>Восстановить</button><button type="button" class="text-button" data-discard-draft>Удалить</button></div></div>` : ''}
    ${canEdit ? '' : `<div class="access-banner">${icon('lock')}<span><strong>Личная карточка ${escapeHTML(record.ownerUsername)}</strong><small>Вы можете просматривать её ход и связи, но изменять содержание может только ответственный.</small></span></div>`}
    <form id="record-edit-form" class="card-form record-overview-form" data-can-edit="${canEdit}">
      <div class="form-grid two"><label>Название<input name="title" value="${escapeHTML(record.title)}" required></label><label>${record.type === 'question_set' ? 'Статус рассчитывается автоматически' : 'Статус'}<select name="status" ${record.type === 'question_set' ? 'disabled' : ''}>${statuses.map((status) => `<option value="${status}" ${record.status === status ? 'selected' : ''}>${statusLabels[status]}</option>`).join('')}</select></label></div>
      <label>${language.description}<textarea name="description" rows="5">${escapeHTML(record.description)}</textarea></label>
      <details class="form-more" ${['task', 'meeting'].includes(record.type) ? 'open' : ''}><summary>${planningTitle}</summary><div class="form-more-body">
        <div class="form-grid ${planningGrid}"><label>${language.owner}<select name="ownerId" ${canManageAccess ? '' : 'disabled'}>${userOptions(record.ownerId)}</select></label>${hasDecisionMaker ? `<label>Принимает решение<select name="decisionMakerId"><option value="">Не указан</option>${userOptions(record.decisionMakerId)}</select></label>` : ''}${hasDeadline ? `<label>${dueLabel}<input name="dueAt" type="datetime-local" value="${toLocalInput(record.dueAt)}"></label>` : ''}</div>
        ${(hasPriority || hasEstimate || hasManualProgress) ? `<div class="form-grid ${hasEstimate && hasManualProgress ? 'four' : 'three'}">${hasPriority ? `<label>Приоритет<select name="priority">${Object.entries(priorityLabels).map(([value, label]) => `<option value="${value}" ${record.priority === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label>` : ''}${hasEstimate ? `<label>План, минут<input name="estimateMinutes" type="number" min="0" value="${record.estimateMinutes}"></label><label>Факт, минут<input name="actualMinutes" type="number" min="0" value="${record.actualMinutes || 0}"></label>` : ''}${hasManualProgress ? `<label>Прогресс, %<input name="progress" type="number" min="0" max="100" value="${record.progress}"></label>` : ''}</div>` : ''}
        <div class="record-organization"><div class="form-grid three"><label>Направление<select name="workstream">${Object.entries(workstreamLabels).map(([value, label]) => `<option value="${value}" ${record.workstream === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label>Доступ к изменениям<select name="editPolicy" ${canManageAccess ? '' : 'disabled'}>${Object.entries(editPolicyLabels).map(([value, label]) => `<option value="${value}" ${record.editPolicy === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label>Родитель в иерархии<select name="parentId"><option value="">Без родителя</option>${parentOptions}</select></label></div><label class="root-toggle"><input name="isRoot" type="checkbox" ${record.isRoot ? 'checked' : ''}> <span><strong>Сделать новым корнем</strong><small>Карточка станет самостоятельным началом новой крупной ветки и потеряет текущего родителя.</small></span></label></div>
        ${hasManualProgress ? `<label>Текущее обновление<input name="progressNote" value="${escapeHTML(record.progressNote)}" placeholder="Что изменилось с прошлого раза"></label>` : ''}
        ${hasResult ? `<label>${record.type === 'research' ? 'Вывод исследования' : record.type === 'decision' ? 'Принятое решение' : record.type === 'disagreement' ? 'Результат разбора' : 'Достигнутый результат'}<textarea name="result" rows="3">${escapeHTML(record.result)}</textarea></label>` : ''}
        ${record.type === 'question_set' ? `<div class="derived-progress"><span>Прогресс обсуждения рассчитывается по принятым итогам</span><strong>${record.progress}%</strong></div>` : ''}
      </div></details>
      <label id="record-reason-field" class="reason-field" hidden>Причина изменения <input name="reason" placeholder="Почему изменился статус или срок"></label>
      <div class="form-actions"><button type="submit" class="primary">Сохранить</button><span class="form-save-state" id="record-save-state">Изменений нет</span><button type="button" class="secondary" id="notify-partners">Уведомить</button>${record.type === 'task' ? `<button type="button" class="secondary" id="convert-to-questions">${icon('messages')} Сделать карточкой вопросов</button>` : ''}<button type="button" class="danger-text" id="archive-record">В архив</button></div>
    </form>
    ${renderNextActions(record)}
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
  return `<article class="question-item ${question.decision ? 'resolved' : ''}" data-question-id-anchor="${question.id}">
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
  const canEdit = record.editPolicy !== 'owner_only' || record.ownerId === state.me.id;
  const parent = record.parentId ? state.records.find((item) => item.id === record.parentId) : null;
  const ideaActions = record.type === 'idea' ? `<div class="idea-actions">${['review', 'main', 'rejected'].map((status) => `<button type="button" class="stage-action ${status}" data-stage="${status}" ${record.status === status || !canEdit ? 'disabled' : ''}>${statusLabels[status]}</button>`).join('')}</div>` : '';
  $('#record-dialog-content').innerHTML = `
    <div class="record-shell record-type-${record.type} ${state.recordWorkspace.length > 1 ? 'has-workspace' : ''}">
    ${renderRecordWorkspace()}
    <div class="dialog-header record-dialog-header"><div><span class="record-kind">${icon(typeMeta[record.type].icon)} ${typeMeta[record.type].singular}</span><h2>${escapeHTML(record.title)}</h2><p>Создал ${escapeHTML(record.authorUsername)} · ${formatDate(record.createdAt, true)}</p></div><div class="record-header-actions"><button type="button" class="icon-button" data-record-graph="${record.id}" title="Открыть локальную карту" aria-label="Открыть локальную карту">${icon('network')}</button><button type="button" class="close-button icon-button" data-close-dialog aria-label="Закрыть">${icon('x')}</button></div></div>
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
        <div class="fact"><span>Направление</span><strong class="workstream-mark workstream-${record.workstream || 'business'}">${escapeHTML(workstreamLabels[record.workstream || 'business'])}</strong></div>
        <div class="fact"><span>Доступ</span><strong>${record.editPolicy === 'owner_only' ? `${icon('lock')} Только владелец` : 'Общая карточка'}</strong></div>
        ${record.isRoot ? `<div class="fact"><span>Иерархия</span><strong>Новый корень</strong></div>` : parent ? `<button type="button" class="fact fact-link" data-related-record="${parent.id}"><span>Родитель</span><strong>${escapeHTML(parent.title)}</strong></button>` : ''}
        ${hasDeadline ? `<div class="fact"><span>${record.type === 'meeting' ? 'Дата' : 'Срок'}</span><strong class="deadline ${deadlineState(record).className}">${escapeHTML(deadlineState(record).label)}</strong></div>` : ''}
        <div class="fact"><span>Изменено</span><strong>${formatDate(record.updatedAt, true)}</strong></div>
        ${record.type === 'task' ? `<div class="fact"><span>Доказательств</span><strong>${record.proofCount}</strong></div>` : ''}
        ${record.type === 'question_set' ? `<div class="fact"><span>Решено вопросов</span><strong>${detail.questionWorkflow.resolved} / ${detail.questionWorkflow.questions.length}</strong></div>` : ''}
      </aside>
    </div></div>`;
  bindRecordDialogEvents();
  applyRecordAccess(record, canEdit);
  bindRecordWorkspace();
  $$('[data-record-graph]').forEach((button) => button.addEventListener('click', () => openGraphForRecord(record.id)));
  if (state.focusQuestionId) {
    requestAnimationFrame(() => {
      const question = $(`[data-question-id-anchor="${CSS.escape(state.focusQuestionId)}"]`);
      question?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      question?.classList.add('question-focus');
      state.focusQuestionId = '';
    });
  }
}

function applyRecordAccess(record, canEdit) {
  if (canEdit) return;
  const root = $('#record-dialog');
  const mutationSelectors = ['#record-edit-form input', '#record-edit-form select', '#record-edit-form textarea', '#record-edit-form button', '.section-form input', '.section-form textarea', '.section-form button', '#custom-section-form input', '#custom-section-form textarea', '#custom-section-form button', '.criterion-form input', '.criterion-form button', '#link-form select', '#link-form button', '[data-remove-link]', '[data-create-linked]', '[data-create-from-record]', '#add-questions-form textarea', '#add-questions-form button', '[data-select-answer]', '[data-custom-decision] textarea', '[data-custom-decision] button', '[data-create-output]', '[data-archive-question]', '#notify-partners', '#archive-record', '#convert-to-questions'];
  $$(mutationSelectors.join(','), root).forEach((node) => { node.disabled = true; node.setAttribute('aria-disabled', 'true'); });
  root.classList.add('record-readonly');
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
  const createOptions = nextRecordOptions(record);
  return `<details class="accordion" ${open ? 'open' : ''}><summary><span>Связанные записи</span><small>${links.length} связей</small></summary>${createOptions.length ? `<div class="linked-create"><span>Создать следующий объект</span>${createOptions.map(([type, kind, label]) => `<button type="button" data-create-linked="${type}" data-linked-kind="${kind}">${icon(typeMeta[type].icon)} ${label}</button>`).join('')}</div>` : ''}<div class="linked-list">${links.map((link) => `<div class="linked-item"><button type="button" data-related-record="${link.record.id}"><i class="type-icon type-${link.record.type}">${icon(typeMeta[link.record.type].icon)}</i><span><strong>${escapeHTML(link.record.title)}</strong><small>${escapeHTML(relationLabel(link))} · ${typeMeta[link.record.type].singular}</small></span></button><button type="button" class="icon-button danger-icon remove-link" data-remove-link="${link.id}" aria-label="Убрать связь" title="Убрать связь">${icon('x')}</button></div>`).join('') || emptyState('Связей пока нет.')}</div><form id="link-form" class="link-form"><select name="targetId" required><option value="">Выберите существующую карточку</option>${targets.map((target) => `<option value="${target.id}">${typeMeta[target.type].singular}: ${escapeHTML(target.title)}</option>`).join('')}</select><select name="relationType"><option value="related">Связано</option><option value="supports">Поддерживает</option><option value="depends_on">Зависит от</option><option value="result_of">Является результатом</option><option value="leads_to">Приводит к</option></select><button class="secondary" type="submit">${icon('link')} Связать</button></form></details>`;
}

function renderProofBlock(record, proofs) {
  const canComplete = record.ownerId === state.me.id || record.editPolicy === 'shared';
  return `<details class="accordion" open><summary><span>Подтверждение результата</span><small>${proofs.length} приложено</small></summary><div class="proof-list">${proofs.map((proof) => `<article class="proof"><header><strong>${escapeHTML(proof.authorUsername)}</strong><time>${formatDate(proof.createdAt, true)}</time></header>${proof.kind === 'link' && /^https?:\/\//i.test(proof.content) ? `<a href="${escapeHTML(proof.content)}" target="_blank" rel="noreferrer">${escapeHTML(proof.content)}</a>` : `<p>${escapeHTML(proof.content).replace(/\n/g, '<br>')}</p>`}</article>`).join('') || emptyState('Перед завершением приложите результат или ссылку на него.')}</div>${canComplete ? `<form id="proof-form" class="proof-form"><select name="kind"><option value="text">Текст</option><option value="link">Ссылка</option></select><textarea name="content" rows="4" placeholder="Что сделано или где находится результат" required></textarea><button class="secondary" type="submit">Приложить</button></form><div class="completion-box"><label>Краткий итог<textarea id="completion-result" rows="3" placeholder="Что получили в результате"></textarea></label><label class="check"><input id="notify-on-complete" type="checkbox" checked> Уведомить партнёра</label><button type="button" class="success" id="complete-task" ${proofs.length ? '' : 'disabled'}>Завершить задачу</button></div>` : ''}</details>`;
}

function buildRecordUpdate(form, record) {
  const values = recordFormValues(form);
  const body = { expectedUpdatedAt: record.updatedAt };
  const compare = (key, next, previous) => { if (String(next ?? '') !== String(previous ?? '')) body[key] = next; };
  compare('title', values.title.trim(), record.title);
  compare('description', values.description.trim(), record.description);
  if ('status' in values) compare('status', values.status, record.status);
  if ('ownerId' in values) compare('ownerId', Number(values.ownerId), record.ownerId);
  if ('decisionMakerId' in values) {
    if (values.decisionMakerId) compare('decisionMakerId', Number(values.decisionMakerId), record.decisionMakerId);
    else if (record.decisionMakerId) body.clearDecisionMaker = true;
  }
  if ('dueAt' in values) {
    const dueISO = values.dueAt ? new Date(values.dueAt).toISOString() : '';
    if (normalizedInstant(dueISO) !== normalizedInstant(record.dueAt)) body.dueAt = dueISO;
  }
  if ('priority' in values) compare('priority', values.priority, record.priority || 'normal');
  if ('workstream' in values) compare('workstream', values.workstream, record.workstream || 'business');
  if ('editPolicy' in values) compare('editPolicy', values.editPolicy, record.editPolicy || 'shared');
  if ('parentId' in values) compare('parentId', values.parentId, record.parentId || '');
  if (form.elements.isRoot) compare('isRoot', form.elements.isRoot.checked, Boolean(record.isRoot));
  if ('estimateMinutes' in values) compare('estimateMinutes', Number(values.estimateMinutes), record.estimateMinutes);
  if ('actualMinutes' in values) compare('actualMinutes', Number(values.actualMinutes), record.actualMinutes || 0);
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
  const rootToggle = editForm.elements.isRoot;
  const parentSelect = editForm.elements.parentId;
  rootToggle?.addEventListener('change', () => {
    if (rootToggle.checked && parentSelect) parentSelect.value = '';
  });
  parentSelect?.addEventListener('change', () => {
    if (parentSelect.value && rootToggle) rootToggle.checked = false;
  });
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
  $$('[data-related-record]').forEach((button) => button.addEventListener('click', () => openRecord(button.dataset.relatedRecord, { workspace: true })));
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
    openModal(dialog);
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
      await openRecord(output.id, { workspace: true });
    } catch (error) { toast(error.message, true); }
  });
  openModal($('#create-dialog'));
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
  const sourceRecord = preset.sourceRecordId ? state.records.find((record) => record.id === preset.sourceRecordId) : null;
  const defaultWorkstream = preset.workstream || sourceRecord?.workstream || 'business';
  const defaultParentID = preset.parentId ?? sourceRecord?.id ?? '';
  const defaultEditPolicy = preset.editPolicy || 'shared';
  const kindLabels = { preference: 'Критерий выбора', limitation: 'Ограничение', rule: 'Правило', insight: 'Вывод' };
  const displayName = kindLabels[preset.kind] || initialMeta.singular;
  const titleLabel = initialType === 'question_set' ? 'Название группы вопросов' : initialType === 'meeting' ? 'Тема встречи' : 'Название';
  const descriptionLabel = preset.kind === 'limitation' ? 'Как применять ограничение' : preset.kind === 'rule' ? 'Формулировка и область действия' : initialType === 'question_set' ? 'Зачем обсуждаем' : initialType === 'meeting' ? 'Повестка и заметки' : initialType === 'task' ? 'Ожидаемый результат' : 'Краткое описание';
  const parentOptions = state.records.filter((record) => record.status !== 'archived').map((record) => `<option value="${record.id}" ${defaultParentID === record.id ? 'selected' : ''}>${escapeHTML(typeMeta[record.type]?.singular || 'Карточка')}: ${escapeHTML(record.title)}</option>`).join('');
  const planned = ['task', 'goal', 'research', 'question_set', 'meeting', 'decision', 'disagreement'].includes(initialType);
  $('#create-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">${icon(initialMeta.icon)} Новая запись</span><h2>${escapeHTML(displayName)}</h2></div><button type="button" class="close-button icon-button" data-close-create aria-label="Закрыть">${icon('x')}</button></div><form id="create-record-form" class="card-form dialog-form"><label>${titleLabel}<input name="title" required maxlength="240" autofocus value="${escapeHTML(preset.title || '')}" placeholder="${initialType === 'question_set' ? 'Например: Договорённости основателей' : ''}"></label><label>${descriptionLabel}<textarea name="description" rows="5">${escapeHTML(preset.description || '')}</textarea></label><input type="hidden" name="type" value="${initialType}"><input type="hidden" name="kind" value="${escapeHTML(preset.kind || '')}">${planned ? `<div class="form-grid two"><label>${initialType === 'question_set' ? 'Координатор' : initialType === 'meeting' ? 'Организатор' : 'Ответственный'}<select name="ownerId">${userOptions(state.me.id)}</select></label><label>${initialType === 'meeting' ? 'Дата и время' : 'Срок'}<input name="dueAt" type="datetime-local"></label></div><div class="form-grid two"><label>Приоритет<select name="priority">${Object.entries(priorityLabels).map(([value, label]) => `<option value="${value}" ${value === 'normal' ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label>Оценка времени, минут<input name="estimateMinutes" type="number" min="0" value="0"></label></div>` : `<input type="hidden" name="ownerId" value="${state.me.id}"><input type="hidden" name="priority" value="normal"><input type="hidden" name="estimateMinutes" value="0">`}<details class="form-more create-organization" ${sourceRecord ? 'open' : ''}><summary>Место в проекте и доступ</summary><div class="form-more-body"><div class="form-grid three"><label>Направление<select name="workstream">${Object.entries(workstreamLabels).map(([value, label]) => `<option value="${value}" ${defaultWorkstream === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label>Доступ к изменениям<select name="editPolicy">${Object.entries(editPolicyLabels).map(([value, label]) => `<option value="${value}" ${defaultEditPolicy === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label>Родитель<select name="parentId"><option value="">Без родителя</option>${parentOptions}</select></label></div><label class="root-toggle"><input name="isRoot" type="checkbox" ${preset.isRoot ? 'checked' : ''}> <span><strong>Новый корень</strong><small>Начать самостоятельную крупную ветку вместо продолжения текущей цепочки.</small></span></label></div></details><div class="ai-suggestion"><span class="ai-suggestion-icon">AI</span><span><strong>Структура карточки</strong><small id="ai-suggestion-status">После названия система предложит приоритет, направление и место в иерархии.</small></span><button type="button" class="secondary" data-ai-suggest>Предложить</button></div><div class="form-actions"><button type="submit" class="primary">${icon('plus')} Создать</button><button type="button" class="secondary" data-close-create>Отмена</button></div></form>`;
  $$('[data-close-create]').forEach((button) => button.addEventListener('click', () => $('#create-dialog').close()));
  const createForm = $('#create-record-form');
  bindCreateSuggestion(createForm, initialType);
  $('#create-record-form').addEventListener('submit', async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget); const due = form.get('dueAt');
    try {
      const record = await api('/api/records', { method: 'POST', body: JSON.stringify({ type: form.get('type'), kind: form.get('kind'), title: form.get('title'), description: form.get('description'), ownerId: Number(form.get('ownerId')), dueAt: due ? new Date(due).toISOString() : '', priority: form.get('priority') || 'normal', workstream: form.get('workstream') || 'business', editPolicy: form.get('editPolicy') || 'shared', parentId: form.get('parentId') || '', isRoot: event.currentTarget.elements.isRoot.checked, estimateMinutes: Number(form.get('estimateMinutes')) }) });
      let linkError = '';
      if (preset.sourceRecordId) {
        try {
          await api(`/api/records/${preset.sourceRecordId}/links`, { method: 'POST', body: JSON.stringify({ targetId: record.id, relationType: preset.relationType || 'leads_to', reason: preset.reason || 'Карточка создана из связанного рабочего контекста' }) });
          state.detailCache.delete(preset.sourceRecordId);
        } catch (error) {
          linkError = `Карточка создана, но связь не добавлена: ${error.message}`;
        }
      }
      $('#create-dialog').close(); await loadData(true); toast(linkError || 'Карточка создана', Boolean(linkError)); await openRecord(record.id, { workspace: Boolean(preset.sourceRecordId) });
    } catch (error) { toast(error.message, true); }
  });
  openModal($('#create-dialog'));
}

function bindCreateSuggestion(form, recordType) {
  const tracked = ['priority', 'workstream', 'parentId'];
  tracked.forEach((name) => form.elements[name]?.addEventListener('change', () => { form.elements[name].dataset.userChanged = 'true'; }));
  const root = form.elements.isRoot;
  const parent = form.elements.parentId;
  root?.addEventListener('change', () => { if (root.checked && parent) parent.value = ''; });
  parent?.addEventListener('change', () => { if (parent.value && root) root.checked = false; });
  let requestNumber = 0;
  const suggest = async (force = false) => {
    const title = form.elements.title.value.trim();
    if (title.length < 4) return;
    const currentRequest = ++requestNumber;
    const status = $('#ai-suggestion-status');
    status.textContent = 'Анализируем карточку…';
    try {
      const suggestion = await api('/api/ai/suggest-record', { method: 'POST', body: JSON.stringify({ type: recordType, title, description: form.elements.description.value }) });
      if (currentRequest !== requestNumber || !form.isConnected) return;
      tracked.forEach((name) => {
        const field = form.elements[name];
        if (field && (force || field.dataset.userChanged !== 'true') && suggestion[name] !== undefined) field.value = suggestion[name];
      });
      if (suggestion.parentId && root) root.checked = false;
      const parentTitle = suggestion.parentId ? state.records.find((record) => record.id === suggestion.parentId)?.title : '';
      const source = suggestion.source === 'groq' ? 'Groq' : 'локальная модель';
      status.textContent = `${source}: ${priorityLabels[suggestion.priority]}, ${workstreamLabels[suggestion.workstream]}${parentTitle ? `, ветка «${parentTitle}»` : ', без родителя'}. ${suggestion.reason}`;
    } catch (error) {
      if (currentRequest === requestNumber) status.textContent = `Не удалось получить предложение: ${error.message}`;
    }
  };
  $('[data-ai-suggest]', form).addEventListener('click', () => suggest(true));
  ['title', 'description'].forEach((name) => form.elements[name].addEventListener('input', () => {
    clearTimeout(state.aiSuggestionTimer);
    state.aiSuggestionTimer = setTimeout(() => suggest(false), 700);
  }));
  if (form.elements.title.value.trim().length >= 4) suggest(false);
}

function actionLabel(action) {
  return ({ created: 'создал карточку', profile_updated: 'изменил профиль', updated: 'изменил карточку', converted_to_questions: 'преобразовал в карточку вопросов', archived: 'перенёс в архив', section_updated: 'обновил раздел', link_created: 'создал связь', link_removed: 'убрал связь', criterion_scored: 'оценил по критерию', proof_added: 'добавил доказательство', completed: 'завершил задачу', partners_notified: 'уведомил партнёра', questions_added: 'добавил вопросы', question_answered: 'ответил на вопрос', question_decided: 'зафиксировал совместное решение', question_archived: 'архивировал вопрос', output_created: 'превратил вывод в рабочую карточку', created_from_question: 'создал карточку из совместного вывода' }[action] || action);
}

function activityActionLabel(item) {
  if (item.entityType === 'user' && item.action === 'created') return 'зарегистрировался в проекте';
  return actionLabel(item.action);
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
  if (field === 'priority' && value) return priorityLabels[value] || value;
  if (field === 'workstream' && value) return workstreamLabels[value] || value;
  if (field === 'editPolicy' && value) return editPolicyLabels[value] || value;
  if (field === 'parentId' && value) return state.records.find((record) => record.id === value)?.title || value;
  if (field === 'actualMinutes' && value !== null && value !== undefined) return minutesLabel(Number(value));
  if (field === 'isRoot') return value ? 'Новый корень' : 'Обычная ветка';
  return formatActivityValue(value, truncate);
}

function activityChanges(item, full = false) {
  const fieldLabels = { username: 'Логин', type: 'Тип карточки', title: 'Название', description: 'Описание', status: 'Статус', ownerId: 'Ответственный', decisionMakerId: 'Принимает решение', dueAt: 'Срок', priority: 'Приоритет', workstream: 'Направление', editPolicy: 'Доступ', parentId: 'Родитель', isRoot: 'Иерархия', estimateMinutes: 'Оценка времени', actualMinutes: 'Фактическое время', progress: 'Прогресс', progressNote: 'Ход работы', result: 'Результат' };
  const changes = Object.entries(item.details || {}).filter(([, value]) => value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'before') && Object.prototype.hasOwnProperty.call(value, 'after'));
  if (!changes.length && Object.prototype.hasOwnProperty.call(item.details || {}, 'before') && Object.prototype.hasOwnProperty.call(item.details || {}, 'after')) {
    changes.push([item.details?.section || 'Содержание', { before: item.details.before, after: item.details.after }]);
  }
  if (!changes.length) return '';
  return changes.map(([field, value]) => `<span class="change-line"><b>${escapeHTML(fieldLabels[field] || field)}:</b> <del>${escapeHTML(activityDisplayValue(field, value.before, !full))}</del><i>→</i><ins>${escapeHTML(activityDisplayValue(field, value.after, !full))}</ins></span>`).join('');
}

function activityDetails(item) {
  const details = item.details || {};
  const rows = [];
  const target = details.targetId ? state.records.find((record) => record.id === details.targetId) : null;
  const relationLabels = { related: 'связано', supports: 'поддерживает', depends_on: 'зависит от', result_of: 'является результатом', leads_to: 'приводит к', produced: 'порождает' };
  if (item.action === 'questions_added' && details.count) rows.push(['Добавлено вопросов', String(details.count)]);
  if (['link_created', 'link_removed'].includes(item.action) && target) rows.push(['Связанная карточка', `${typeMeta[target.type]?.singular || 'Карточка'} «${target.title}»`]);
  if (['link_created', 'link_removed'].includes(item.action) && details.relationType) rows.push(['Характер связи', relationLabels[details.relationType] || details.relationType]);
  if (item.action === 'criterion_scored' && details.score !== undefined) rows.push(['Оценка', `${details.score} из 10`]);
  if (item.action === 'criterion_scored' && details.note) rows.push(['Обоснование', details.note]);
  if (item.action === 'proof_added') rows.push(['Подтверждение', details.kind === 'link' ? 'Ссылка' : 'Текстовый результат']);
  if (item.action === 'completed' && details.result) rows.push(['Полученный результат', details.result]);
  if (item.action === 'partners_notified' && details.message) rows.push(['Сообщение партнёру', details.message]);
  if (item.action === 'section_updated' && details.section) rows.push(['Раздел', details.section]);
  if (!rows.length) return '';
  return `<dl class="event-details">${rows.map(([label, value]) => `<div><dt>${escapeHTML(label)}</dt><dd>${escapeHTML(String(value))}</dd></div>`).join('')}</dl>`;
}

function activityContext(item) {
  const details = item.details || {};
  if (item.action === 'questions_added' && details.count) return questionsCountLabel(Number(details.count));
  if (item.action === 'question_answered') return 'Личная позиция сохранена';
  if (item.action === 'question_decided') return 'Совместный итог зафиксирован';
  if (item.action === 'link_created') {
    const target = state.records.find((record) => record.id === details.targetId);
    return target ? `Связь с «${target.title}»` : 'Новая связь между карточками';
  }
  if (item.action === 'proof_added') return 'Добавлено подтверждение результата';
  if (item.reason) return `Причина: ${item.reason}`;
  return recordTitleByActivity(item);
}

function recordTitleByActivity(item) {
  if (item.entityType === 'user') return item.details?.username || 'Участник проекта';
  return state.records.find((record) => record.id === item.entityId)?.title || item.details?.title || `${item.entityType} · ${item.entityId.slice(0, 8)}`;
}

function renderActivityItem(item) {
  return `<button type="button" class="activity-item" data-open-event="${item.id}"><span class="history-marker">${icon(typeMeta[item.entityType]?.icon || 'history')}</span><span><strong>${escapeHTML(item.actorUsername)} ${escapeHTML(activityActionLabel(item))}</strong><small>${escapeHTML(activityContext(item))}</small></span><time>${formatDate(item.createdAt, true)}</time>${icon('chevronRight', 'activity-arrow')}</button>`;
}

function durationLabel(seconds) {
  if (!seconds) return 'Нет данных';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  if (!hours) return `${minutes} мин`;
  return minutes ? `${hours} ч ${minutes} мин` : `${hours} ч`;
}

async function openProfile(userId) {
  const dialog = $('#profile-dialog');
  const user = state.users.find((item) => item.id === Number(userId));
  $('#profile-dialog-content').innerHTML = `<div class="profile-loading"><span class="spinner"></span><strong>Загружаем активность ${escapeHTML(user?.username || '')}</strong></div>`;
  openModal(dialog);
  try {
    const profile = await api(`/api/users/${userId}/profile`);
    const maxSeconds = Math.max(1, ...profile.activity.map((day) => day.activeSeconds));
    const accuracy = profile.estimateMinutes > 0 && profile.actualMinutes > 0 ? Math.round(profile.actualMinutes * 100 / profile.estimateMinutes) : 0;
    $('#profile-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">Участник проекта</span><h2>${escapeHTML(profile.user.username)}</h2><p>На платформе с ${formatDate(profile.user.createdAt)}</p></div><button type="button" class="close-button icon-button" data-close-profile aria-label="Закрыть">${icon('x')}</button></div><div class="profile-body"><section class="profile-summary"><span class="avatar profile-avatar">${escapeHTML(profile.user.username.slice(0, 2).toUpperCase())}</span><div><h3>${escapeHTML(profile.user.username)}</h3><p>${profile.user.id === state.me.id ? 'Ваш профиль активности' : 'Активность сооснователя'}</p></div>${profile.user.id === state.me.id ? `<button type="button" class="secondary" data-edit-profile>${icon('edit')} Изменить логин</button>` : ''}</section><div class="profile-metrics"><article><span>Активное время · 30 дней</span><strong>${durationLabel(profile.activeSeconds30Days)}</strong><small>Только взаимодействие с интерфейсом</small></article><article><span>Действия · 30 дней</span><strong>${profile.actions30Days}</strong><small>${interactionsCountLabel(profile.interactions30Days)} с UI</small></article><article><span>Завершено</span><strong>${profile.completedRecords}</strong><small>карточек с результатом</small></article><article><span>Факт к оценке</span><strong>${accuracy ? `${accuracy}%` : 'Нет данных'}</strong><small>${minutesLabel(profile.actualMinutes)} факт · ${minutesLabel(profile.estimateMinutes)} план</small></article></div><section class="activity-chart"><header><h3>Активность по дням</h3><span>Последние 30 дней</span></header><div>${profile.activity.length ? profile.activity.slice().reverse().map((day) => `<span title="${escapeHTML(day.date)} · ${durationLabel(day.activeSeconds)} · ${interactionsCountLabel(day.interactions)}"><i data-level="${Math.max(1, Math.ceil(day.activeSeconds * 5 / maxSeconds))}"></i><small>${day.date.slice(8)}</small></span>`).join('') : `<p>Активность начнёт накапливаться после взаимодействия с новой версией.</p>`}</div></section><section class="profile-actions"><header><h3>Последние действия</h3><span>${profile.recentActions.length}</span></header><div class="activity-list">${profile.recentActions.map(renderActivityItem).join('') || emptyState('Действий пока нет.')}</div></section></div>`;
    $$('[data-close-profile]').forEach((button) => button.addEventListener('click', () => dialog.close()));
    $('[data-edit-profile]')?.addEventListener('click', async () => {
      const username = await askText({ title: 'Изменить логин', label: 'Новый логин', defaultValue: state.me.username, required: true });
      if (!username || username === state.me.username) return;
      try {
        state.me = await api('/api/me', { method: 'PATCH', body: JSON.stringify({ username }) });
        $('#user-name').textContent = state.me.username; $('#user-avatar').textContent = state.me.username.slice(0, 2).toUpperCase();
        await loadData(true); await openProfile(state.me.id); toast('Логин изменён');
      } catch (error) { toast(error.message, true); }
    });
    $$('[data-open-event]', dialog).forEach((button) => button.addEventListener('click', () => openActivity(button.dataset.openEvent)));
  } catch (error) {
    $('#profile-dialog-content').innerHTML = `<div class="record-load-error">${icon('help')}<h2>Профиль не загрузился</h2><p>${escapeHTML(error.message)}</p><button type="button" class="secondary" data-close-profile>Закрыть</button></div>`;
    $('[data-close-profile]').addEventListener('click', () => dialog.close());
  }
}

function openActivity(id) {
  const item = state.activity.find((activity) => activity.id === id);
  if (!item) return toast('Событие не найдено', true);
  state.activeActivity = item;
  const record = state.records.find((candidate) => candidate.id === item.entityId);
  $('#event-dialog-content').innerHTML = `<div class="dialog-header"><div><span class="record-kind">${formatDate(item.createdAt, true)} · ${escapeHTML(item.actorUsername)}</span><h2>${escapeHTML(activityActionLabel(item))}</h2><p>${escapeHTML(recordTitleByActivity(item))}</p></div><button type="button" class="close-button icon-button" data-close-event aria-label="Закрыть">${icon('x')}</button></div><div class="event-body">${item.reason ? `<section class="event-reason-block"><span>Почему</span><p>${escapeHTML(item.reason)}</p></section>` : ''}${activityChanges(item, true) ? `<section class="event-section"><h3>Что изменилось</h3><div class="event-change-list">${activityChanges(item, true)}</div></section>` : ''}${activityDetails(item) ? `<section class="event-section"><h3>Содержание события</h3>${activityDetails(item)}</section>` : ''}<div class="form-actions">${record ? `<button type="button" class="primary" data-event-record="${record.id}">Открыть карточку</button>` : ''}<button type="button" class="secondary" data-close-event>Закрыть</button></div></div>`;
  $$('[data-close-event]', $('#event-dialog')).forEach((button) => button.addEventListener('click', () => $('#event-dialog').close()));
  $('[data-event-record]')?.addEventListener('click', async (event) => { $('#event-dialog').close(); await openRecord(event.currentTarget.dataset.eventRecord); });
  openModal($('#event-dialog'));
}

function renderHistory() {
  const groups = new Map();
  state.activity.forEach((item) => {
    const day = new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(item.createdAt));
    if (!groups.has(day)) groups.set(day, []);
    groups.get(day).push(item);
  });
  $('#main-content').innerHTML = `<div class="history-title"><h1>История проекта</h1><span>${state.activity.length} событий</span></div><section class="history-feed">${[...groups.entries()].map(([day, items]) => `<div class="history-day"><time>${escapeHTML(day)}</time><div class="activity-list">${items.map(renderActivityItem).join('')}</div></div>`).join('') || emptyState('История пока пуста.')}</section>`;
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
  openModal(dialog);
}

function finishOnboarding() {
  try { localStorage.setItem(onboardingKey(), new Date().toISOString()); } catch (_) {}
  if ($('#onboarding-dialog').open) $('#onboarding-dialog').close();
}

bootstrap();
