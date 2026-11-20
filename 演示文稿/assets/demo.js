(() => {
  const form = document.getElementById('rename-demo');
  if (!form) return;
  const name = form.elements.event, result = Array.from(form.querySelectorAll('[data-out]')), status = document.getElementById('demo-status');
  const clear = msg => {result.forEach(el => el.textContent = '？'); status.textContent = msg};
  name.addEventListener('input', () => clear('点「预览」查看新名称。'));
  form.addEventListener('submit', e => {
    e.preventDefault();
    const val = name.value.trim();
    if (!val) {clear('请先填入活动名称。');name.focus();return}
    if (/[\\/:*?"<>|]/.test(val)) {clear('请去掉文件名中不能使用的符号。');name.focus();return}
    result.forEach((el,i) => el.textContent = val + '-' + String(i+1).padStart(2,'0') + '.jpg');
    status.textContent = '已预览 2 个名称，原文件不变。';
  })
})();
