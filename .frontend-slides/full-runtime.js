/* === BRCLIO LECTURE: NAVIGATION, OPTIONAL REVEALS, NOTES AND TEXT EDITING === */
(() => {
  'use strict';
  if (window.presentation && window.presentation.brclioRuntime) return;

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const hash = value => {
    let n = 2166136261;
    for (const c of String(value)) { n ^= c.codePointAt(0); n = Math.imul(n, 16777619); }
    return (n >>> 0).toString(36);
  };
  const make = (tag, attrs = {}, text = '') => {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
    if (text) el.textContent = text;
    return el;
  };

  /* Only simple text formatting is restored from this page's own local edits. */
  function cleanMarkup(html) {
    const template = document.createElement('template');
    template.innerHTML = String(html);
    const allowed = new Set(['SPAN', 'BR', 'STRONG', 'EM', 'B', 'I', 'U', 'S', 'SUB', 'SUP', 'MARK', 'DIV', 'P', 'A']);
    for (const el of [...template.content.querySelectorAll('*')].reverse()) {
      if (['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'LINK', 'META'].includes(el.tagName)) { el.remove(); continue; }
      if (!allowed.has(el.tagName)) { el.replaceWith(...el.childNodes); continue; }
      for (const attr of [...el.attributes]) {
        const safeLink = el.tagName === 'A' && attr.name === 'href' && /^(https?:|mailto:|#)/i.test(attr.value);
        if (attr.name !== 'class' && !safeLink) el.removeAttribute(attr.name);
      }
    }
    return template.innerHTML;
  }

  class SlidePresentation {
    constructor() {
      this.stage = $('.deck-stage');
      this.slides = $$('.deck-stage > .slide');
      if (!this.stage || !this.slides.length) throw new Error('Missing presentation slides.');
      this.brclioRuntime = true;
      this.index = 0;
      this.step = 0;
      this.isEditing = false;
      this.directoryOpen = false;
      this.notesOpen = false;
      this.lastWheel = 0;
      this.editTimers = new Map();
      this.timerElapsed = 0;
      this.timerStarted = null;
      this.lastUiMove = 0;
      const params = new URLSearchParams(location.search);
      this.exportMode = params.get('export') === '1';
      this.allSteps = this.exportMode || params.get('present') === 'all';
      this.embed = params.has('embed');
      this.deckId = document.documentElement.dataset.deckId || document.body.dataset.deckId || this.stage.dataset.deckId || $('meta[name="deck-id"]')?.content || document.title;
      this.storagePrefix = 'brclio-slides:v1:' + hash(this.deckId) + ':';
      this.ids = this.slides.map((slide, i) => slide.dataset.id || String(i + 1).padStart(2, '0'));
      this.stepElements = this.slides.map(slide => $$('[data-step]', slide));
      this.steps = this.stepElements.map(nodes => Math.max(0, ...nodes.map(el => this.stepNumber(el))));
      this.initialToggleGroups = [];
      this.injectControls();
      this.prepareEditing();
      this.prepareToggles();
      this.bindEvents();
      document.body.classList.add('deck-ready');
      document.body.classList.toggle('deck-export', this.exportMode);
      document.body.classList.toggle('deck-embed', this.embed);
      this.fit();
      this.show(this.indexFromHash(), { history: false });
      this.keepControlsVisible();
    }

    get currentSlide() { return this.index; }
    get currentStep() { return this.step; }
    get maxStep() { return this.steps[this.index] || 0; }
    stepNumber(el) { return Math.max(1, Math.min(3, Number.parseInt(el.dataset.step, 10) || 1)); }

    /* === CHROME: INJECT ONCE, OUTSIDE THE 1920 × 1080 CANVAS === */
    injectControls() {
      $$('[data-deck-ui]').forEach(el => el.remove());
      this.ui = make('div', { class: 'deck-ui', 'data-deck-ui': '' });
      this.ui.innerHTML = `
        <div class="deck-progress" role="progressbar" aria-label="演讲进度" aria-valuemin="1"><div class="deck-progress-fill"></div></div>
        <nav class="deck-controls" aria-label="幻灯片控制">
          <button type="button" data-action="previous" title="上一页或上一步（←）" aria-label="上一页或上一步">←</button>
          <output class="deck-counter" aria-live="polite" aria-atomic="true"></output>
          <button type="button" data-action="next" title="继续（→ 或空格）" aria-label="下一步或下一页">→</button>
          <span class="deck-control-divider" aria-hidden="true"></span>
          <button type="button" data-action="directory" title="目录（G）">目录</button>
          <button type="button" data-action="notes" title="讲者备注（N）" aria-pressed="false">备注</button>
          <button type="button" data-action="fullscreen" title="全屏（F）">全屏</button>
          <button type="button" data-action="save" title="保存为 HTML（⌘/Ctrl+S）">保存</button>
          <span class="deck-step-count" aria-live="polite"></span>
        </nav>
        <button type="button" class="deck-edit-hotzone" tabindex="-1" aria-label="进入文字编辑"></button>
        <button type="button" class="deck-edit-toggle" title="编辑文字（E）" aria-pressed="false">编辑</button>
        <div class="deck-toast" role="status" aria-live="polite"></div>
        <div class="deck-directory-backdrop" hidden>
          <section class="deck-directory" role="dialog" aria-modal="true" aria-labelledby="deck-directory-title">
            <header class="deck-panel-header"><h2 id="deck-directory-title">讲座目录</h2><button type="button" data-action="close-directory" aria-label="关闭目录">关闭 ×</button></header>
            <input class="deck-directory-search" type="search" placeholder="查找标题或章节" aria-label="查找幻灯片">
            <div class="deck-directory-list"></div>
            <p class="deck-directory-empty" hidden>没有找到相关页面。</p>
          </section>
        </div>
        <aside class="deck-notes-panel" hidden aria-label="讲者备注">
          <header class="deck-panel-header"><h2>讲者备注</h2><button type="button" data-action="close-notes" aria-label="关闭备注">关闭 ×</button></header>
          <div class="deck-timer"><output aria-label="已讲时间">00:00</output><button type="button" data-action="timer">开始计时</button><button type="button" data-action="reset-timer">归零</button></div>
          <p class="deck-notes-location"></p><h3 class="deck-notes-title"></h3><div class="deck-notes-copy"></div>
        </aside>`;
      document.body.append(this.ui);
      this.counter = $('.deck-counter', this.ui);
      this.progress = $('.deck-progress', this.ui);
      this.progressFill = $('.deck-progress-fill', this.ui);
      this.stepCount = $('.deck-step-count', this.ui);
      this.editButton = $('.deck-edit-toggle', this.ui);
      this.directory = $('.deck-directory-backdrop', this.ui);
      this.directorySearch = $('.deck-directory-search', this.ui);
      this.notesPanel = $('.deck-notes-panel', this.ui);
      this.buildDirectory();
      this.ui.addEventListener('click', e => {
        const button = e.target.closest('button[data-action]');
        if (!button) return;
        const actions = {
          previous: () => this.previous(), next: () => this.next(),
          directory: () => this.openDirectory(), 'close-directory': () => this.closeDirectory(),
          notes: () => this.toggleNotes(), 'close-notes': () => this.toggleNotes(false),
          fullscreen: () => this.toggleFullscreen(), save: () => this.save(),
          timer: () => this.toggleTimer(), 'reset-timer': () => this.resetTimer()
        };
        actions[button.dataset.action]?.();
      });
      this.directory.addEventListener('click', e => { if (e.target === this.directory) this.closeDirectory(); });
      this.directorySearch.addEventListener('input', () => this.filterDirectory());
      const hotzone = $('.deck-edit-hotzone', this.ui);
      const showEdit = () => { clearTimeout(this.editHideTimer); this.editButton.classList.add('show'); };
      const hideEdit = () => { this.editHideTimer = setTimeout(() => { if (!this.isEditing) this.editButton.classList.remove('show'); }, 400); };
      [hotzone, this.editButton].forEach(el => { el.addEventListener('mouseenter', showEdit); el.addEventListener('mouseleave', hideEdit); });
      hotzone.addEventListener('click', () => this.toggleEdit());
      this.editButton.addEventListener('click', () => this.toggleEdit());
      $('.deck-controls', this.ui).addEventListener('mouseenter', () => { clearTimeout(this.idleTimer); document.body.classList.remove('deck-ui-idle'); });
      $('.deck-controls', this.ui).addEventListener('mouseleave', () => this.keepControlsVisible());
    }

    buildDirectory() {
      const list = $('.deck-directory-list', this.ui);
      let lastSection = null, group = null;
      this.directoryButtons = [];
      this.slides.forEach((slide, i) => {
        const section = slide.dataset.section || '讲座内容';
        if (section !== lastSection) {
          group = make('section', { class: 'deck-directory-group' });
          group.append(make('h3', {}, section)); list.append(group); lastSection = section;
        }
        const button = make('button', { type: 'button', class: 'deck-directory-item', 'data-page-index': String(i) });
        button.append(make('span', { class: 'deck-directory-number' }, String(i + 1).padStart(2, '0')));
        button.append(make('span', { class: 'deck-directory-label' }, this.slideTitle(i)));
        button.dataset.search = (section + ' ' + this.slideTitle(i)).toLowerCase();
        button.addEventListener('click', () => { this.show(i); this.closeDirectory(); });
        group.append(button); this.directoryButtons.push(button);
      });
    }
    slideTitle(i) { return this.slides[i].dataset.title || $('h1,h2', this.slides[i])?.textContent.trim() || `第 ${i + 1} 页`; }
    filterDirectory() {
      const term = this.directorySearch.value.trim().toLowerCase();
      let visible = 0;
      this.directoryButtons.forEach(button => { button.hidden = !button.dataset.search.includes(term); if (!button.hidden) visible++; });
      $$('.deck-directory-group', this.ui).forEach(group => { group.hidden = !$$('.deck-directory-item', group).some(el => !el.hidden); });
      $('.deck-directory-empty', this.ui).hidden = visible !== 0;
    }
    openDirectory() {
      if (this.directoryOpen) return;
      this.returnFocus = document.activeElement;
      this.directoryOpen = true; this.directory.hidden = false; this.stage.inert = true;
      this.directorySearch.value = ''; this.filterDirectory(); this.keepControlsVisible();
      this.directorySearch.focus();
    }
    closeDirectory() {
      if (!this.directoryOpen) return;
      this.directoryOpen = false; this.directory.hidden = true; this.stage.inert = false;
      if (this.returnFocus?.isConnected && !this.returnFocus.closest('[inert]')) this.returnFocus.focus({ preventScroll: true });
      this.keepControlsVisible();
    }

    /* === NAVIGATION: FEW INTENTIONAL STEPS, OTHERWISE ONE KEY PER SLIDE === */
    fit() {
      const scale = Math.min(innerWidth / 1920, innerHeight / 1080);
      this.stage.style.transform = `translate(${(innerWidth - 1920 * scale) / 2}px, ${(innerHeight - 1080 * scale) / 2}px) scale(${scale})`;
    }
    indexFromHash() {
      let value;
      try { value = decodeURIComponent(location.hash.slice(1)); } catch (_) { value = ''; }
      if (!value) return 0;
      const direct = this.ids.indexOf(value);
      return direct >= 0 ? direct : Math.max(0, Math.min(this.slides.length - 1, (Number.parseInt(value, 10) || 1) - 1));
    }
    show(index, options = {}) {
      if (typeof options === 'boolean') options = { history: options };
      const target = Math.max(0, Math.min(this.slides.length - 1, Math.trunc(Number(index) || 0)));
      if (this.slides[this.index]?.contains(document.activeElement)) document.activeElement.blur();
      this.index = target;
      this.step = Math.max(0, Math.min(this.maxStep, Number(options.step) || 0));
      this.slides.forEach((slide, i) => {
        const active = i === this.index;
        slide.classList.toggle('active', active); slide.classList.toggle('visible', active);
        slide.setAttribute('aria-hidden', String(!active)); slide.inert = !active;
      });
      this.renderSteps(); this.updateControls(); this.updateNotes();
      if (options.history !== false) {
        try { history.replaceState(null, '', '#' + encodeURIComponent(this.ids[this.index])); } catch (_) { /* local file history may be restricted */ }
      }
      this.keepControlsVisible();
    }
    goTo(index) { this.show(index); }
    setStep(step) { this.step = Math.max(0, Math.min(this.maxStep, Number(step) || 0)); this.renderSteps(); this.updateControls(); }
    renderSteps() {
      const all = this.allSteps || this.isEditing;
      this.stepElements.forEach((elements, i) => elements.forEach(el => {
        const hide = !all && this.stepNumber(el) > (i === this.index ? this.step : 0);
        el.classList.toggle('deck-step-hidden', hide);
        el.inert = hide;
        el.setAttribute('aria-hidden', String(hide));
      }));
    }
    next() {
      if (!this.allSteps && !this.isEditing && this.step < this.maxStep) this.setStep(this.step + 1);
      else if (this.index < this.slides.length - 1) this.show(this.index + 1);
      this.keepControlsVisible();
    }
    previous() {
      if (!this.allSteps && !this.isEditing && this.step > 0) this.setStep(this.step - 1);
      else if (this.index > 0) this.show(this.index - 1, { step: this.allSteps ? 0 : this.steps[this.index - 1] });
      this.keepControlsVisible();
    }
    updateControls() {
      this.counter.textContent = `${this.index + 1} / ${this.slides.length}`;
      this.progress.setAttribute('aria-valuemax', String(this.slides.length));
      this.progress.setAttribute('aria-valuenow', String(this.index + 1));
      this.progressFill.style.transform = `scaleX(${(this.index + 1) / this.slides.length})`;
      this.stepCount.textContent = this.maxStep && !this.allSteps && !this.isEditing ? `展开 ${this.step}/${this.maxStep}` : '';
      $('[data-action="previous"]', this.ui).disabled = this.index === 0 && (this.step === 0 || this.allSteps || this.isEditing);
      $('[data-action="next"]', this.ui).disabled = this.index === this.slides.length - 1 && (this.step >= this.maxStep || this.allSteps || this.isEditing);
      this.directoryButtons.forEach((button, i) => { if (i === this.index) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current'); });
    }

    /* === TWO-VIEW CASE STUDIES: AN ACCESSIBLE, LOCAL SWITCH === */
    prepareToggles() {
      this.slides.forEach(slide => {
        const containers = new Set($$('[data-toggle-target]', slide).map(button => button.closest('[data-toggle-group]') || slide));
        containers.forEach(container => {
          const buttons = $$('[data-toggle-target]', container).filter(button => (button.closest('[data-toggle-group]') || slide) === container);
          const valid = buttons.map(button => ({ button, panel: document.getElementById(button.dataset.toggleTarget) })).filter(pair => pair.panel && slide.contains(pair.panel));
          if (!valid.length) return;
          const first = valid.find(pair => pair.button.getAttribute('aria-pressed') === 'true') || valid.find(pair => !pair.panel.hidden) || valid[0];
          const group = { pairs: valid, initialId: first.panel.id };
          this.initialToggleGroups.push(group);
          valid.forEach((pair, index) => {
            pair.button.setAttribute('aria-controls', pair.panel.id);
            if (pair.button.tagName === 'BUTTON') pair.button.type = 'button';
            pair.button.addEventListener('click', e => { e.stopPropagation(); this.selectToggle(group, pair.panel.id); });
            pair.button.addEventListener('keydown', e => {
              if (!['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
              e.preventDefault(); e.stopPropagation();
              const next = valid[(index + (e.key === 'ArrowRight' ? 1 : valid.length - 1)) % valid.length];
              this.selectToggle(group, next.panel.id); next.button.focus();
            });
          });
          this.selectToggle(group, first.panel.id);
        });
      });
    }
    selectToggle(group, id) {
      group.pairs.forEach(({ button, panel }) => {
        const selected = panel.id === id;
        button.setAttribute('aria-pressed', String(selected));
        button.classList.toggle('deck-toggle-selected', selected); panel.hidden = !selected;
      });
    }

    /* === NOTES: CLOSED BY DEFAULT; TIMER IS STARTED DELIBERATELY === */
    toggleNotes(open = !this.notesOpen) {
      this.notesOpen = Boolean(open); this.notesPanel.hidden = !this.notesOpen;
      $('[data-action="notes"]', this.ui).setAttribute('aria-pressed', String(this.notesOpen));
      document.body.classList.toggle('deck-notes-open', this.notesOpen);
      this.updateNotes(); this.keepControlsVisible();
    }
    updateNotes() {
      $('.deck-notes-location', this.ui).textContent = `${this.index + 1} / ${this.slides.length} · ${this.slides[this.index].dataset.section || '讲座内容'}`;
      $('.deck-notes-title', this.ui).textContent = this.slideTitle(this.index);
      $('.deck-notes-copy', this.ui).textContent = $('.speaker-notes', this.slides[this.index])?.textContent.trim() || '本页没有补充备注。';
      this.renderTimer();
    }
    elapsed() { return this.timerElapsed + (this.timerStarted === null ? 0 : performance.now() - this.timerStarted); }
    renderTimer() {
      const seconds = Math.floor(this.elapsed() / 1000), minutes = Math.floor(seconds / 60);
      $('.deck-timer output', this.ui).textContent = `${String(minutes).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
      $('[data-action="timer"]', this.ui).textContent = this.timerStarted === null ? (this.timerElapsed ? '继续' : '开始计时') : '暂停';
    }
    toggleTimer() {
      if (this.timerStarted === null) { this.timerStarted = performance.now(); this.timerInterval = setInterval(() => this.renderTimer(), 1000); }
      else { this.timerElapsed = this.elapsed(); this.timerStarted = null; clearInterval(this.timerInterval); }
      this.renderTimer();
    }
    resetTimer() { clearInterval(this.timerInterval); this.timerStarted = null; this.timerElapsed = 0; this.renderTimer(); }

    /* === TEXT EDITING: STABLE PER-SLIDE KEYS, NO NAVIGATION WHILE TYPING === */
    prepareEditing() {
      this.fields = [];
      this.slides.forEach((slide, i) => {
        const counts = new Map();
        $$('[data-edit]', slide).filter(el => !el.parentElement.closest('[data-edit]')).forEach((node, j) => {
          const name = node.dataset.editKey || node.dataset.edit || `text-${j + 1}`;
          const duplicate = counts.get(name) || 0; counts.set(name, duplicate + 1);
          const key = this.storagePrefix + this.ids[i] + ':' + name + (duplicate ? `-${duplicate + 1}` : '');
          const field = { node, key, baseHash: hash(node.innerHTML) };
          try {
            const saved = JSON.parse(localStorage.getItem(key) || 'null');
            if (saved && typeof saved.html === 'string' && (saved.baseHash === field.baseHash || hash(saved.html) === field.baseHash)) node.innerHTML = cleanMarkup(saved.html);
          } catch (_) { /* storage may be unavailable for local files; export still works */ }
          node.addEventListener('input', () => {
            clearTimeout(this.editTimers.get(key));
            this.editTimers.set(key, setTimeout(() => this.persist(field), 140));
          });
          node.addEventListener('paste', e => {
            if (!this.isEditing) return;
            e.preventDefault();
            const text = e.clipboardData?.getData('text/plain') || '';
            const selection = getSelection();
            if (!selection?.rangeCount) return;
            const range = selection.getRangeAt(0);
            if (!node.contains(range.commonAncestorContainer)) return;
            range.deleteContents();
            const fragment = document.createDocumentFragment();
            text.replace(/\r\n?/g, '\n').split('\n').forEach((line, i) => {
              if (i) fragment.append(document.createElement('br'));
              fragment.append(document.createTextNode(line));
            });
            const last = fragment.lastChild;
            range.insertNode(fragment);
            if (last) range.setStartAfter(last);
            range.collapse(true); selection.removeAllRanges(); selection.addRange(range);
            node.dispatchEvent(new Event('input', { bubbles: true }));
          });
          this.fields.push(field);
        });
      });
    }
    persist(field) {
      clearTimeout(this.editTimers.get(field.key)); this.editTimers.delete(field.key);
      try { localStorage.setItem(field.key, JSON.stringify({ html: cleanMarkup(field.node.innerHTML), baseHash: field.baseHash })); }
      catch (_) { if (!this.storageWarned) { this.storageWarned = true; this.toast('本地记忆不可用，可用“保存”下载文件。'); } }
    }
    flushEdits() { this.fields.forEach(field => { if (this.editTimers.has(field.key) || this.isEditing) this.persist(field); }); }
    toggleEdit(active = !this.isEditing) {
      this.isEditing = Boolean(active);
      document.body.classList.toggle('deck-editing', this.isEditing);
      this.fields.forEach(({ node }) => {
        if (this.isEditing) { node.setAttribute('contenteditable', 'true'); node.setAttribute('spellcheck', 'false'); }
        else { node.removeAttribute('contenteditable'); node.removeAttribute('spellcheck'); }
      });
      this.editButton.classList.toggle('active', this.isEditing);
      this.editButton.setAttribute('aria-pressed', String(this.isEditing));
      this.editButton.textContent = this.isEditing ? '完成编辑' : '编辑';
      this.flushEdits(); this.renderSteps(); this.updateControls(); this.keepControlsVisible();
      if (this.isEditing) this.toast('点击文字即可修改；⌘/Ctrl+S 保存文件。');
    }

    /* === EXPORT: KEEP EDITS, REMOVE ONLY TRANSIENT UI AND RUNTIME STATE === */
    serialize() {
      this.flushEdits();
      const clone = document.documentElement.cloneNode(true);
      $$('[data-deck-ui]', clone).forEach(el => el.remove());
      const body = $('body', clone);
      ['deck-ready', 'deck-editing', 'deck-ui-idle', 'deck-notes-open', 'deck-embed', 'deck-export'].forEach(name => body.classList.remove(name));
      const stage = $('.deck-stage', clone);
      stage.removeAttribute('inert'); stage.style.removeProperty('transform');
      if (!stage.getAttribute('style')) stage.removeAttribute('style');
      $$('.deck-stage > .slide', clone).forEach((slide, i) => {
        slide.classList.toggle('active', i === 0); slide.classList.toggle('visible', i === 0);
        slide.removeAttribute('aria-hidden'); slide.removeAttribute('inert');
      });
      $$('[data-step]', clone).forEach(el => { el.classList.remove('deck-step-hidden'); el.removeAttribute('inert'); el.removeAttribute('aria-hidden'); });
      $$('[data-edit]', clone).forEach(el => { el.removeAttribute('contenteditable'); el.removeAttribute('spellcheck'); });
      this.initialToggleGroups.forEach(group => {
        group.pairs.forEach(({ button, panel }) => {
          const clonePanel = $$('[id]', clone).find(el => el.id === panel.id);
          const cloneButton = $$('[data-toggle-target]', clone).find(el => el.dataset.toggleTarget === panel.id);
          const selected = panel.id === group.initialId;
          if (clonePanel) clonePanel.hidden = !selected;
          if (cloneButton) { cloneButton.setAttribute('aria-pressed', String(selected)); cloneButton.classList.remove('deck-toggle-selected'); }
        });
      });
      return '<!DOCTYPE html>\n' + clone.outerHTML;
    }
    save() {
      const html = this.serialize();
      const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = make('a', { href: url, download: (document.title || '讲座幻灯片').replace(/[\\/:*?"<>|]/g, '-').slice(0, 100) + '.html' });
      this.ui.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
      this.toast('已保存当前文字，文件正在下载。');
      return html;
    }

    /* === KEYBOARD, TOUCH AND PRESENTATION HELPERS === */
    bindEvents() {
      addEventListener('resize', () => this.fit());
      addEventListener('hashchange', () => this.show(this.indexFromHash(), { history: false }));
      addEventListener('beforeunload', () => this.flushEdits());
      document.addEventListener('fullscreenchange', () => { $('[data-action="fullscreen"]', this.ui).textContent = document.fullscreenElement ? '退出全屏' : '全屏'; this.fit(); });
      document.addEventListener('keydown', e => this.onKey(e));
      document.addEventListener('pointermove', () => { if (performance.now() - this.lastUiMove > 150) { this.lastUiMove = performance.now(); this.keepControlsVisible(); } });
      document.addEventListener('focusin', e => { if (this.ui.contains(e.target)) this.keepControlsVisible(); });
      this.stage.addEventListener('wheel', e => {
        if (this.isEditing || this.directoryOpen || this.embed || e.ctrlKey || e.metaKey) return;
        if (Math.abs(e.deltaY) < 25 || Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
        e.preventDefault();
        if (Date.now() - this.lastWheel > 650) { e.deltaY > 0 ? this.next() : this.previous(); this.lastWheel = Date.now(); }
      }, { passive: false });
      this.stage.addEventListener('touchstart', e => {
        if (e.touches.length !== 1 || this.isEditing || e.target.closest('button,a,input,textarea,select,[contenteditable="true"]')) { this.touchStart = null; return; }
        this.touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY, at: performance.now() };
      }, { passive: true });
      this.stage.addEventListener('touchend', e => {
        if (!this.touchStart) return;
        const touch = e.changedTouches[0], dx = touch.clientX - this.touchStart.x, dy = touch.clientY - this.touchStart.y;
        if (Math.abs(dx) >= 45 && Math.abs(dx) > Math.abs(dy) * 1.3 && performance.now() - this.touchStart.at < 1400) dx < 0 ? this.next() : this.previous();
        this.touchStart = null; this.keepControlsVisible();
      }, { passive: true });
      this.stage.addEventListener('touchcancel', () => { this.touchStart = null; }, { passive: true });
    }
    onKey(e) {
      if (e.isComposing) return;
      const key = e.key.toLowerCase();
      if ((e.ctrlKey || e.metaKey) && key === 's' && !e.altKey) { e.preventDefault(); this.save(); return; }
      if (key === 'escape') {
        if (this.directoryOpen) { e.preventDefault(); this.closeDirectory(); }
        else if (this.notesOpen) { e.preventDefault(); this.toggleNotes(false); }
        else if (this.isEditing) { e.preventDefault(); document.activeElement?.blur(); this.toggleEdit(false); }
        return;
      }
      if (this.directoryOpen) {
        if (e.key === 'Tab') {
          const focusable = $$('button,input,[tabindex]:not([tabindex="-1"])', this.directory).filter(el => !el.disabled && el.getClientRects().length);
          const first = focusable[0], last = focusable[focusable.length - 1];
          if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
          else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
        }
        return;
      }
      const target = e.target instanceof Element ? e.target : null;
      if (target?.isContentEditable || target?.closest('input,textarea,select') || e.ctrlKey || e.metaKey || e.altKey) return;
      if (['g', 'n', 'e', 'f'].includes(key)) {
        e.preventDefault();
        ({ g: () => this.openDirectory(), n: () => this.toggleNotes(), e: () => this.toggleEdit(), f: () => this.toggleFullscreen() })[key]();
        return;
      }
      if (target?.closest('.deck-notes-panel')) return;
      if (target?.closest('button,a') && [' ', 'Enter'].includes(e.key)) return;
      if (['ArrowRight', 'ArrowDown', ' ', 'PageDown'].includes(e.key)) { e.preventDefault(); this.next(); }
      else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) { e.preventDefault(); this.previous(); }
      else if (e.key === 'Home') { e.preventDefault(); this.show(0); }
      else if (e.key === 'End') { e.preventDefault(); this.show(this.slides.length - 1); }
    }
    async toggleFullscreen() {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
        else this.toast('当前浏览器不支持全屏，可使用浏览器的全屏菜单。');
      } catch (_) { this.toast('未能进入全屏，请使用浏览器的全屏菜单。'); }
    }
    keepControlsVisible() {
      clearTimeout(this.idleTimer); document.body.classList.remove('deck-ui-idle');
      this.idleTimer = setTimeout(() => {
        if (!this.isEditing && !this.directoryOpen && !this.notesOpen && !this.ui.contains(document.activeElement)) document.body.classList.add('deck-ui-idle');
      }, 3200);
    }
    toast(message) {
      const node = $('.deck-toast', this.ui); node.textContent = message; node.classList.add('show');
      clearTimeout(this.toastTimer); this.toastTimer = setTimeout(() => node.classList.remove('show'), 3200);
    }
  }

  const boot = () => { if (!window.presentation?.brclioRuntime) window.presentation = new SlidePresentation(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
