# 讲座运行时接口

`full-controls.css` 与 `full-runtime.js` 各内嵌一次即可。运行时把控件注入 `body`，不占用 1920 × 1080 的画布，也不修改幻灯片排版。独立三页检查页为 `runtime-selftest.html`，通过同目录的 HTTP 服务打开即可。

## DOM 约定

- `.deck-stage > .slide`：每页 `data-id` 为稳定的唯一页标识；`data-title` 用作目录标题，`data-section` 用作目录分组。
- `body[data-deck-id]`：稳定的整套讲座标识。本讲座是 `brclio-xiamen-ai-lecture-v1`。
- `[data-step="1|2|3"]`：少数需要讲述展开的元素；未标注内容一直可见。相同步骤可用于多个元素。普通跳页从步骤 0 开始；反向翻页回到上一页的最后一步。
- `[data-edit="唯一字段名"]`：可编辑文字。仅顶层标注生效，子元素不应重复标注。可另用 `data-edit-key` 覆盖键名。
- `.speaker-notes[hidden]`：每页讲者备注；运行时读取纯文字，默认关闭。
- `[data-toggle-group="组名"]`：组内按钮以 `data-toggle-target="面板id"` 指定目标，目标只须在同一页。初始优先选择 `aria-pressed="true"` 的按钮，否则选择未 `hidden` 的面板。切换时维护 `aria-pressed`、`hidden`，按钮左右方向键选择同组内容，空格和 Enter 保留原生按钮行为，不翻页。

## 演讲操作

- `→ / ↓ / 空格 / PageDown`：下一步，展开完毕再翻页。
- `← / ↑ / PageUp`：上一步，再返回上一页。
- `Home / End`：首页 / 末页；触摸横向滑动、鼠标纵向滚轮也可导航。
- `G`：搜索目录；`N`：讲者备注侧栏；`F`：全屏；`E`：编辑。
- `Esc`：依次关闭目录、备注或编辑模式。编辑文字、搜索输入和按钮的原生交互不会被翻页键覆盖。
- 左上角悬停显示编辑按钮，离开后延迟 400ms 隐藏。底部控件闲置 3.2 秒后隐藏，鼠标移动时恢复。
- 备注中的计时器需主动开始，支持暂停和归零；关闭侧栏不打断计时。

## 批量验收接口

```js
presentation.show(10, { step: 0, history: false }); // 第11页，0-based
presentation.setStep(1);
presentation.next();
presentation.previous();
presentation.currentSlide; // 当前页索引，等同 .index
presentation.currentStep;  // 当前步骤，等同 .step
presentation.maxStep;      // 当前页最多步骤
presentation.steps;        // 全部页面的步骤数
presentation.allSteps;    // 是否为全显模式
presentation.serialize(); // 返回清理后的完整 HTML 文本
presentation.save();      // 下载 HTML，并返回相同文本
```

`?present=all` 显示全部步骤；`?export=1` 同时隐藏控件；`?embed=1` 隐藏控件。`#11` 跳至 `data-id="11"`。`show(index, {history:false})` 不改 URL。

## 保存与导出

编辑以整套讲座标识、页 ID、字段名写入 `localStorage`。原文字哈希用于防止重新生成讲座后，旧编辑覆盖新的正文。`⌘/Ctrl+S` 下载一份完整 HTML，包含当前文字，保留原本内嵌的字体、图片、样式与脚本，移除注入控件、编辑状态、舞台缩放与步骤隐藏；重开时仅注入一份控件。导出不依赖 `localStorage`。粘贴只接受纯文字，换行保留。

打印媒体样式展示全部页和全部步骤，隐藏控件及备注。`prefers-reduced-motion: reduce` 关闭步骤的过渡和 12px 位移。

## 已验收

2026-11-19，以最终 50 页讲座在 Chromium 中检查：

- 4/6/19/21/34/38/39/48 页有步骤，其余直接导航；步骤展开、回退与首末页键正常。
- 第 11 页按钮点击、空格和组内左右键切换正常，不改变页码。
- 目录搜索、点击跳转；备注文本匹配当前页；计时器开始、暂停、归零；F 进入/退出全屏。
- 编辑时方向键与空格不翻页，本地刷新恢复文字。
- 实际执行 ⌘S 下载；导出含编辑、50 条备注、仅一份运行时；无注入 UI、contenteditable 和步骤隐藏。清空存储后重开导出，编辑仍在、控件仅一份。
- `?export=1` 全步骤可见、控件隐藏；打印模式 50 页可见、舞台缩放移除。
- 390 × 844 视口，舞台仍为 390 × 219.375，保持 16:9；模拟触摸滑动翻页正常。
- 减弱动态模式：步骤过渡 `0s`、位移 `none`。
- 验收用本地存储已清空，源讲座未留下测试文字。
