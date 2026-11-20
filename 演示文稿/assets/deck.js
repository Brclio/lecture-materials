(() => {
  "use strict";

  const stylesheet = new URL("control.css", document.currentScript.src).href;

  function start() {
    const stage = document.getElementById("stage");
    const slides = Array.from(stage?.querySelectorAll(".slide") || []);
    if (!slides.length) return;

    const interactive = "a, button, input, select, textarea, summary, [role=button], [contenteditable]:not([contenteditable=false])";
    const pad = n => String(n).padStart(2, "0");
    const folio = n => pad(n + 1) + " / " + pad(slides.length);
    const title = n => slides[n].dataset.title || slides[n].querySelector("h1, h2")?.textContent.trim() || "第 " + (n + 1) + " 页";
    const part = n => slides[n].dataset.part || "讲座";
    let index = 0;
    let presenter = null;
    let noticeTimer;
    let dialogPage = "";
    let returnFocus = null;

    const make = (tag, className, value) => {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (value !== undefined) node.textContent = value;
      return node;
    };

    function button(label, description, action, className) {
      const node = make("button", className, label);
      node.type = "button";
      node.setAttribute("aria-label", description);
      node.title = description;
      node.addEventListener("click", action);
      return node;
    }

    const bar = make("nav", "bdc-bar");
    bar.setAttribute("aria-label", "放映控制");
    const previous = button("‹", "上一页（←）", () => show(index - 1), "bdc-arrow");
    const menu = button("菜单", "打开演示菜单", () => openDialog("menu"), "bdc-menu");
    const next = button("›", "下一页（→）", () => show(index + 1), "bdc-arrow");
    bar.append(previous, menu, next);

    const dialog = make("dialog", "bdc-dialog");
    dialog.id = "brclio-deck-dialog";
    dialog.setAttribute("aria-labelledby", "brclio-deck-dialog-heading");
    const dialogHead = make("div", "bdc-dialog-head");
    const dialogHeading = make("h2", "bdc-dialog-title");
    dialogHeading.id = "brclio-deck-dialog-heading";
    const close = button("关闭", "关闭并返回放映（Esc）", () => dialog.close(), "bdc-close");
    dialogHead.append(dialogHeading, close);
    const dialogContent = make("div", "bdc-dialog-body");
    dialog.append(dialogHead, dialogContent);
    const notice = make("div", "bdc-notice");
    notice.hidden = true;
    notice.setAttribute("role", "status");
    document.body.append(bar, dialog, notice);

    function say(message) {
      clearTimeout(noticeTimer);
      notice.textContent = message;
      notice.hidden = false;
      noticeTimer = setTimeout(() => { notice.hidden = true; }, 4500);
    }

    function fromHash() {
      const match = /^#([1-9]\d*)$/.exec(location.hash);
      return match ? Math.min(Number(match[1]), slides.length) - 1 : 0;
    }

    function updatePresenter() {
      if (!presenter || presenter.closed) return;
      const doc = presenter.document;
      doc.getElementById("bdc-position").textContent = folio(index);
      doc.getElementById("bdc-part").textContent = part(index);
      doc.getElementById("bdc-title").textContent = title(index);
      const source = slides[index].querySelector("aside.notes");
      const notes = doc.getElementById("bdc-notes");
      notes.replaceChildren();
      if (source?.children.length) {
        for (const child of source.children) {
          if (child.tagName === "SCRIPT" || child.tagName === "STYLE") continue;
          const item = doc.createElement("p");
          item.textContent = child.textContent.trim();
          if (item.textContent) notes.append(item);
        }
      } else {
        notes.textContent = source?.textContent.trim() || "本页无讲述提示。";
      }
      doc.getElementById("bdc-notes-area").scrollTop = 0;
      doc.getElementById("bdc-up-next").textContent = index < slides.length - 1 ? title(index + 1) : "已到最后一页";
      doc.getElementById("bdc-prev").disabled = index === 0;
      doc.getElementById("bdc-next").disabled = index === slides.length - 1;
      doc.title = pad(index + 1) + " · " + title(index) + "｜讲者视图";
    }

    function show(requested) {
      index = Math.max(0, Math.min(requested, slides.length - 1));
      slides.forEach((slide, n) => {
        const active = n === index;
        slide.classList.toggle("active", active);
        slide.setAttribute("aria-hidden", active ? "false" : "true");
        slide.inert = !active;
      });
      previous.disabled = index === 0;
      next.disabled = index === slides.length - 1;
      const hash = "#" + (index + 1);
      if (location.hash !== hash) {
        try {
          history.replaceState(null, "", hash);
        } catch {
          location.hash = hash;
        }
      }
      updatePresenter();
    }

    async function toggleFullscreen() {
      try {
        if (document.fullscreenElement || document.webkitFullscreenElement) {
          const leave = document.exitFullscreen || document.webkitExitFullscreen;
          await leave.call(document);
        } else {
          const enter = document.documentElement.requestFullscreen || document.documentElement.webkitRequestFullscreen;
          await enter.call(document.documentElement);
        }
      } catch {
        say("请使用浏览器的全屏命令。");
      }
    }

    function openPresenter() {
      if (dialog.open) dialog.close();
      if (presenter && !presenter.closed) {
        presenter.focus();
        updatePresenter();
        return;
      }
      presenter = window.open("", "_blank", "popup=yes,width=800,height=700,resizable=yes,scrollbars=yes");
      if (!presenter) {
        say("浏览器拦截了讲者窗口，请允许此页面弹出窗口，再按 P。");
        return;
      }
      const doc = presenter.document;
      doc.open();
      doc.write(`<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>讲者视图</title></head>
<body class="bdc-presenter">
  <header class="bdc-pres-head"><strong>讲者视图</strong><span id="bdc-position"></span></header>
  <main id="bdc-notes-area" class="bdc-pres-current">
    <div id="bdc-part" class="bdc-pres-part"></div>
    <h1 id="bdc-title"></h1>
    <h2 class="bdc-pres-label">讲述提示</h2><div id="bdc-notes"></div>
  </main>
  <footer class="bdc-pres-foot"><div class="bdc-pres-preview"><span class="bdc-pres-label">下一页</span><strong id="bdc-up-next"></strong></div>
    <nav aria-label="控制观众屏幕"><button id="bdc-prev" type="button">← 上一页</button><button id="bdc-next" type="button">下一页 →</button></nav>
  </footer>
</body></html>`);
      doc.close();
      const style = doc.createElement("link");
      style.rel = "stylesheet";
      style.href = stylesheet;
      doc.head.append(style);
      doc.getElementById("bdc-prev").addEventListener("click", () => show(index - 1));
      doc.getElementById("bdc-next").addEventListener("click", () => show(index + 1));
      doc.addEventListener("keydown", event => {
        if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing) return;
        if (event.key === " " && event.target.closest?.("button")) return;
        handleNavigation(event);
      });
      updatePresenter();
      presenter.focus();
    }

    function addMenuItem(label, key, action) {
      const item = button(label, label + (key ? "（" + key + "）" : ""), action, "bdc-option");
      if (key) item.append(make("kbd", "", key));
      dialogContent.append(item);
    }

    function renderMenu() {
      addMenuItem("幻灯片总览", "O", () => openDialog("overview"));
      addMenuItem("打开讲者窗口", "P", openPresenter);
      addMenuItem("切换全屏", "F", () => { dialog.close(); toggleFullscreen(); });
      const resources = make("a", "bdc-option", "讲座资料");
      resources.href = new URL("resources.html", location.href).href;
      resources.target = "_blank";
      resources.rel = "noopener";
      resources.setAttribute("aria-label", "在新标签页打开讲座资料");
      resources.append(make("span", "bdc-out", "↗"));
      dialogContent.append(resources);
      addMenuItem("操作说明", "?", () => openDialog("help"));
    }

    function renderOverview() {
      let group;
      let lastPart;
      slides.forEach((slide, n) => {
        const label = part(n);
        if (lastPart !== label) {
          group = make("section", "bdc-group");
          group.append(make("h3", "", label));
          dialogContent.append(group);
          lastPart = label;
        }
        const item = button("", "转到第 " + (n + 1) + " 页：" + title(n), () => {
          dialog.close();
          show(n);
        }, "bdc-slide-choice");
        item.append(make("span", "bdc-choice-num", pad(n + 1)), make("span", "", title(n)));
        if (n === index) item.setAttribute("aria-current", "page");
        group.append(item);
      });
    }

    function renderHelp() {
      const rows = [
        ["→ / ↓ / 空格 / PageDown", "下一页"],
        ["← / ↑ / PageUp", "上一页"],
        ["Home / End", "首页 / 末页"],
        ["F", "进入或退出全屏"],
        ["O / P", "幻灯片总览 / 独立讲者窗口"],
        ["? / Esc", "操作说明 / 关闭面板"]
      ];
      rows.forEach(([keys, action]) => {
        const row = make("div", "bdc-help-row");
        row.append(make("span", "", action), make("kbd", "", keys));
        dialogContent.append(row);
      });
      dialogContent.append(make("p", "bdc-hint", "触屏可左右滑动翻页。使用双屏时，将放映页放到投影屏幕，把讲者窗口留在自己的电脑上。"));
    }

    function openDialog(page) {
      if (dialog.open && page === dialogPage) {
        dialog.close();
        return;
      }
      if (!dialog.open) returnFocus = document.activeElement;
      dialogPage = page;
      dialog.dataset.page = page;
      dialogHeading.textContent = { menu: "演示菜单", overview: "幻灯片总览", help: "操作说明" }[page];
      dialogContent.replaceChildren();
      if (page === "overview") renderOverview();
      else if (page === "help") renderHelp();
      else renderMenu();
      if (!dialog.open) dialog.showModal();
      dialogContent.scrollTop = 0;
      if (page === "overview") {
        const current = dialogContent.querySelector("[aria-current=page]");
        current?.focus({ preventScroll: true });
        current?.scrollIntoView({ block: "nearest" });
      } else close.focus({ preventScroll: true });
    }

    dialog.addEventListener("close", () => {
      dialogPage = "";
      if (returnFocus?.isConnected && !returnFocus.closest?.("[inert]")) returnFocus.focus({ preventScroll: true });
      returnFocus = null;
    });
    dialog.addEventListener("click", event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    });

    function handleNavigation(event) {
      const keys = {
        ArrowRight: index + 1, ArrowDown: index + 1, PageDown: index + 1, " ": index + 1,
        ArrowLeft: index - 1, ArrowUp: index - 1, PageUp: index - 1, Home: 0, End: slides.length - 1
      };
      if (!Object.hasOwn(keys, event.key)) return false;
      event.preventDefault();
      show(keys[event.key]);
      return true;
    }

    document.addEventListener("keydown", event => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey || event.isComposing) return;
      const target = event.target;
      if (stage.contains(target) && target.closest?.("input,select,textarea,[contenteditable]:not([contenteditable=false])")) {
        if (event.key === "Escape") { event.preventDefault(); target.blur(); }
        return;
      }
      if (stage.contains(target) && target.closest?.(interactive) && (event.key === " " || event.key === "Enter")) return;
      const key = event.key.toLowerCase();
      if (dialog.open) {
        if (key === "o" || key === "?") {
          event.preventDefault();
          openDialog(key === "o" ? "overview" : "help");
        }
        return;
      }
      if (event.key === " " && target.closest?.(interactive)) return;
      if (handleNavigation(event)) return;
      if (event.repeat || !["f", "o", "p", "?"].includes(key)) return;
      event.preventDefault();
      if (key === "p") openPresenter();
      else if (key === "f") toggleFullscreen();
      else openDialog(key === "o" ? "overview" : "help");
    });

    let touchStart = null;
    stage.addEventListener("touchstart", event => {
      touchStart = null;
      if (dialog.open || event.touches.length !== 1 || event.target.closest?.(interactive)) return;
      const point = event.touches[0];
      touchStart = { x: point.clientX, y: point.clientY };
    }, { passive: true });
    stage.addEventListener("touchcancel", () => { touchStart = null; }, { passive: true });
    stage.addEventListener("touchend", event => {
      if (!touchStart || !event.changedTouches.length) return;
      const point = event.changedTouches[0];
      const dx = point.clientX - touchStart.x;
      const dy = point.clientY - touchStart.y;
      touchStart = null;
      if (Math.abs(dx) >= 55 && Math.abs(dx) > Math.abs(dy) * 1.6 && !window.getSelection()?.toString()) {
        show(index + (dx < 0 ? 1 : -1));
      }
    }, { passive: true });

    slides.forEach((slide, n) => {
      for (const node of slide.querySelectorAll(".folio")) node.textContent = folio(n);
    });
    window.addEventListener("hashchange", () => show(fromHash()));
    show(fromHash());
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
