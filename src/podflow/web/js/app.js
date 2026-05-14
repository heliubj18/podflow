// ===== State =====
let selectedFile = null;
let selectedMode = 'dialogue';
let selectedTemplate = null;
let currentTaskId = null;
let ws = null;

// ===== LLM Provider Presets =====
const LLM_PRESETS = {
  ollama: { base_url: 'http://localhost:11434/v1', model: 'qwen2.5:14b' },
  llamacpp: { base_url: 'http://localhost:8080/v1', model: 'qwen2.5-14b' },
  openai: { base_url: 'https://api.openai.com/v1', model: 'gpt-4o' },
  deepseek: { base_url: 'https://api.deepseek.com/v1', model: 'deepseek-chat' },
  siliconflow: { base_url: 'https://api.siliconflow.cn/v1', model: 'Qwen/Qwen2.5-32B-Instruct' },
  custom: { base_url: '', model: '' }
};

// ===== Navigation =====
function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

  const page = document.getElementById(`page-${pageId}`);
  if (page) page.classList.add('active');

  const link = document.querySelector(`.nav-link[data-page="${pageId}"]`);
  if (link) link.classList.add('active');

  if (pageId === 'history') loadTaskList();
  if (pageId === 'settings') loadSettings();
}

function showDetail(taskId) {
  currentTaskId = taskId;
  showPage('detail');
  loadTaskDetail(taskId);
  connectWS(taskId);
}

// ===== Upload Zone =====
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const urlInput = document.getElementById('url-input');
const selectedFileDiv = document.getElementById('selected-file');
const btnStart = document.getElementById('btn-start');

uploadZone.addEventListener('click', (e) => {
  if (e.target !== urlInput) fileInput.click();
});

uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
  uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  const files = e.dataTransfer.files;
  if (files.length > 0) handleFileSelect(files[0]);
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
});

urlInput.addEventListener('input', (e) => {
  const url = e.target.value.trim();
  if (url) {
    selectedFile = null;
    fileInput.value = '';
    selectedFileDiv.hidden = false;
    selectedFileDiv.textContent = `URL: ${url}`;
    checkStartButton();
  } else {
    selectedFileDiv.hidden = true;
    checkStartButton();
  }
});

function handleFileSelect(file) {
  selectedFile = file;
  urlInput.value = '';
  selectedFileDiv.hidden = false;
  selectedFileDiv.textContent = `已选择: ${file.name}`;
  checkStartButton();
}

function checkStartButton() {
  const hasInput = selectedFile || urlInput.value.trim();
  btnStart.disabled = !hasInput;
}

// ===== Mode Selection =====
document.querySelectorAll('.mode-option').forEach(opt => {
  opt.addEventListener('click', () => {
    document.querySelectorAll('.mode-option').forEach(o => o.classList.remove('selected'));
    opt.classList.add('selected');
    selectedMode = opt.dataset.mode;
    loadTemplates();
  });
});

// ===== Template Selection =====
async function loadTemplates() {
  try {
    const res = await fetch(`/api/templates?mode=${selectedMode}`);
    const templates = await res.json();
    const list = document.getElementById('template-list');

    list.innerHTML = templates.map(t => `
      <div class="template-item" data-id="${t.id}">
        <h4>${t.name}</h4>
        <p>${t.description}</p>
      </div>
    `).join('');

    list.querySelectorAll('.template-item').forEach(item => {
      item.addEventListener('click', () => {
        list.querySelectorAll('.template-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        selectedTemplate = item.dataset.id;
      });
    });
  } catch (err) {
    console.error('Failed to load templates:', err);
  }
}

// ===== Task Creation =====
btnStart.addEventListener('click', async () => {
  if (btnStart.disabled) return;

  const formData = new FormData();

  if (selectedFile) {
    formData.append('file', selectedFile);
  } else if (urlInput.value.trim()) {
    formData.append('url', urlInput.value.trim());
  } else {
    return;
  }

  formData.append('mode', selectedMode);
  if (selectedTemplate) formData.append('template_id', selectedTemplate);

  try {
    btnStart.disabled = true;
    btnStart.textContent = '创建中...';

    const res = await fetch('/api/tasks', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) throw new Error('Failed to create task');

    const task = await res.json();
    showDetail(task.id);
  } catch (err) {
    alert('创建任务失败: ' + err.message);
    btnStart.disabled = false;
    btnStart.textContent = '开始生成播客';
  }
});

// ===== Task List =====
async function loadTaskList() {
  try {
    const res = await fetch('/api/tasks');
    const tasks = await res.json();

    const list = document.getElementById('task-list');

    if (tasks.length === 0) {
      list.innerHTML = '<p style="text-align:center;color:var(--text-dim)">暂无任务</p>';
      return;
    }

    list.innerHTML = tasks.map(t => `
      <div class="task-card" data-id="${t.id}">
        <div class="task-card-title">${t.source_name || t.id}</div>
        <span class="task-card-status ${t.status}">${getStatusText(t.status)}</span>
        <p style="color:var(--text-dim);margin-top:0.5rem">创建于 ${new Date(t.created_at).toLocaleString('zh-CN')}</p>
      </div>
    `).join('');

    list.querySelectorAll('.task-card').forEach(card => {
      card.addEventListener('click', () => showDetail(card.dataset.id));
    });
  } catch (err) {
    console.error('Failed to load tasks:', err);
  }
}

function getStatusText(status) {
  const map = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  };
  return map[status] || status;
}

// ===== Task Detail =====
async function loadTaskDetail(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}`);
    const task = await res.json();
    renderTaskDetail(task);
  } catch (err) {
    console.error('Failed to load task:', err);
  }
}

function renderTaskDetail(task) {
  const container = document.getElementById('task-detail');

  let html = `
    <h2>${task.source_name || task.id}</h2>
    <p style="color:var(--text-dim)">模式: ${task.mode === 'dialogue' ? '双人播客' : '单人讲座'}</p>
    <p style="color:var(--text-dim)">状态: <span class="task-card-status ${task.status}">${getStatusText(task.status)}</span></p>
  `;

  // Stages
  if (task.stages && task.stages.length > 0) {
    html += '<div class="stage-list">';
    task.stages.forEach(stage => {
      const icon = getStageIcon(stage.status);
      html += `
        <div class="stage-item">
          <div class="stage-icon ${stage.status}">${icon}</div>
          <div style="flex:1">
            <strong>${getStageName(stage.name)}</strong>
            ${stage.progress ? `
              <div class="progress-bar">
                <div class="progress-fill" style="width:${stage.progress}%"></div>
              </div>
            ` : ''}
          </div>
        </div>
      `;
    });
    html += '</div>';
  }

  // Results
  if (task.status === 'completed' && task.outputs) {
    html += '<div class="result-section">';
    html += '<h3>生成结果</h3>';

    if (task.outputs.audio_file) {
      html += `
        <audio class="audio-player" controls>
          <source src="/outputs/${task.outputs.audio_file}" type="audio/mpeg">
        </audio>
      `;
    }

    html += '<div class="download-buttons">';
    if (task.outputs.audio_file) {
      html += `<a href="/outputs/${task.outputs.audio_file}" download>下载音频</a>`;
    }
    if (task.outputs.script_file) {
      html += `<a href="/outputs/${task.outputs.script_file}" download>下载脚本</a>`;
    }
    html += '</div>';
    html += '</div>';
  }

  // Error
  if (task.status === 'failed' && task.error) {
    html += `<div class="result-section" style="border-color:var(--error)">
      <h3 style="color:var(--error)">错误信息</h3>
      <div class="log-area">${task.error}</div>
    </div>`;
  }

  container.innerHTML = html;
}

function getStageIcon(status) {
  const icons = {
    completed: '✓',
    running: '⟳',
    pending: '○',
    failed: '✗'
  };
  return icons[status] || '○';
}

function getStageName(name) {
  const map = {
    parse: '文档解析',
    outline: '大纲生成',
    script: '脚本生成',
    tts: '语音合成',
    mix: '音频混音'
  };
  return map[name] || name;
}

// ===== WebSocket =====
function connectWS(taskId) {
  if (ws) ws.close();

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${protocol}//${window.location.host}/api/ws/${taskId}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'task_update') {
      renderTaskDetail(data.task);
    }
  };

  ws.onerror = (err) => {
    console.error('WebSocket error:', err);
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
  };
}

// ===== Settings =====
async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    const settings = await res.json();

    // LLM
    document.getElementById('llm-provider').value = settings.llm?.provider || 'ollama';
    document.getElementById('llm-base-url').value = settings.llm?.base_url || '';
    document.getElementById('llm-api-key').value = settings.llm?.api_key || '';
    document.getElementById('llm-model').value = settings.llm?.model || '';

    // TTS
    document.getElementById('tts-provider').value = settings.tts?.provider || 'edge-tts';

    // Load voice options
    await loadVoiceOptions(settings.tts?.provider || 'edge-tts');

    document.getElementById('tts-host-voice').value = settings.tts?.host_voice || '';
    document.getElementById('tts-guest-voice').value = settings.tts?.guest_voice || '';
  } catch (err) {
    console.error('Failed to load settings:', err);
  }
}

async function loadVoiceOptions(provider) {
  const hostSelect = document.getElementById('tts-host-voice');
  const guestSelect = document.getElementById('tts-guest-voice');

  // Default voices per provider
  const voices = {
    'edge-tts': [
      { value: 'zh-CN-YunxiNeural', label: '云希 (男)' },
      { value: 'zh-CN-XiaoxiaoNeural', label: '晓晓 (女)' },
      { value: 'zh-CN-YunyangNeural', label: '云扬 (男)' },
      { value: 'zh-CN-XiaoyiNeural', label: '晓伊 (女)' }
    ],
    'voxcpm2': [
      { value: 'speaker_1', label: 'Speaker 1' },
      { value: 'speaker_2', label: 'Speaker 2' }
    ],
    'chattts': [
      { value: 'seed_1234_restored_emb', label: 'Seed 1234' },
      { value: 'seed_5678_restored_emb', label: 'Seed 5678' }
    ],
    'openai-tts': [
      { value: 'alloy', label: 'Alloy' },
      { value: 'echo', label: 'Echo' },
      { value: 'fable', label: 'Fable' },
      { value: 'onyx', label: 'Onyx' },
      { value: 'nova', label: 'Nova' },
      { value: 'shimmer', label: 'Shimmer' }
    ]
  };

  const options = voices[provider] || [];
  const html = options.map(v => `<option value="${v.value}">${v.label}</option>`).join('');

  hostSelect.innerHTML = html;
  guestSelect.innerHTML = html;
}

document.getElementById('llm-provider').addEventListener('change', (e) => {
  const preset = LLM_PRESETS[e.target.value];
  if (preset) {
    document.getElementById('llm-base-url').value = preset.base_url;
    document.getElementById('llm-model').value = preset.model;
  }
});

document.getElementById('tts-provider').addEventListener('change', (e) => {
  loadVoiceOptions(e.target.value);
});

document.getElementById('btn-test-llm').addEventListener('click', async () => {
  const btn = document.getElementById('btn-test-llm');
  const result = document.getElementById('llm-test-result');

  btn.disabled = true;
  btn.textContent = '测试中...';
  result.textContent = '';

  try {
    const res = await fetch('/api/settings/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: document.getElementById('llm-provider').value,
        base_url: document.getElementById('llm-base-url').value,
        api_key: document.getElementById('llm-api-key').value,
        model: document.getElementById('llm-model').value
      })
    });

    const data = await res.json();

    if (data.success) {
      result.textContent = '✓ 连接成功';
      result.style.color = 'var(--success)';
    } else {
      result.textContent = '✗ ' + (data.error || '连接失败');
      result.style.color = 'var(--error)';
    }
  } catch (err) {
    result.textContent = '✗ 请求失败';
    result.style.color = 'var(--error)';
  } finally {
    btn.disabled = false;
    btn.textContent = '测试连接';
  }
});

document.getElementById('btn-save-settings').addEventListener('click', async () => {
  const btn = document.getElementById('btn-save-settings');
  btn.disabled = true;
  btn.textContent = '保存中...';

  try {
    const settings = {
      llm: {
        provider: document.getElementById('llm-provider').value,
        base_url: document.getElementById('llm-base-url').value,
        api_key: document.getElementById('llm-api-key').value,
        model: document.getElementById('llm-model').value
      },
      tts: {
        provider: document.getElementById('tts-provider').value,
        host_voice: document.getElementById('tts-host-voice').value,
        guest_voice: document.getElementById('tts-guest-voice').value
      }
    };

    const res = await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });

    if (!res.ok) throw new Error('Failed to save');

    alert('设置已保存');
  } catch (err) {
    alert('保存失败: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '保存设置';
  }
});

// ===== Navigation Event Listeners =====
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const page = link.dataset.page;
    if (page) showPage(page);
  });
});

// ===== Initialize =====
loadTemplates();
