const brl = (v) =>
  (Number(v) || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const setupOverlay = document.getElementById("setup-overlay");
const modalOverlay = document.getElementById("modal-overlay");

const STATUS_LABEL = {
  pago: "Pago",
  parcial: "Parcial",
  aberto: "Em aberto",
};

function todayISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function addBubble(text, who) {
  const div = document.createElement("div");
  div.className = `bubble ${who}`;
  div.textContent = String(text || "").replace(/\*\*(.*?)\*\*/g, "$1");
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderList(el, items, emptyText) {
  el.innerHTML = "";
  if (!items.length) {
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = emptyText;
    el.appendChild(p);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  }
}

function paintSummary(s) {
  document.getElementById("month-label").textContent = `${String(s.mes).padStart(2, "0")}/${s.ano}`;
  document.getElementById("m-entrou").textContent = brl(s.entrou);
  document.getElementById("m-saiu").textContent = brl(s.saiu);
  document.getElementById("m-conta").textContent = brl(s.sobrou_conta);
  document.getElementById("m-verdade").textContent = brl(s.sobrou_verdade);
  document.getElementById("m-pessoal").textContent = brl(s.por_lente.pessoal.saldo);
  document.getElementById("m-prof").textContent = brl(s.por_lente.profissional.saldo);
  document.getElementById("m-receber").textContent = brl(s.a_receber);
  document.getElementById("m-pagar").textContent = brl(s.a_pagar);

  renderList(
    document.getElementById("list-receber"),
    (s.trabalhos_abertos || []).map(
      (t) => `${t.data} · ${t.tipo}${t.pagador ? " · " + t.pagador : ""} · ${brl(t.saldo_receber)}`
    ),
    "Nada em aberto"
  );
  renderList(
    document.getElementById("list-pagar"),
    (s.previstos || [])
      .filter((l) => l.tipo === "saida")
      .map((l) => `${l.data_caixa} · ${l.categoria} · ${brl(l.valor)}`),
    "Nenhuma conta prevista"
  );
  renderList(
    document.getElementById("list-lanc"),
    (s.lancamentos || []).map(
      (l) => `${l.data_caixa} · ${l.tipo} · ${l.lente} · ${l.categoria} · ${brl(l.valor)}`
    ),
    "Sem lançamentos neste mês"
  );
}

function paintTrabalhos(data) {
  const t = data.totais || {};
  document.getElementById("t-esperado").textContent = brl(t.esperado);
  document.getElementById("t-recebido").textContent = brl(t.recebido);
  document.getElementById("t-aberto").textContent = brl(t.em_aberto);
  document.getElementById("trabalhos-status").innerHTML = `
    <span class="badge pago">${t.pago || 0} pagos</span>
    <span class="badge parcial">${t.parcial || 0} parciais</span>
    <span class="badge aberto">${t.aberto || 0} em aberto</span>
  `;
  const body = document.getElementById("trabalhos-body");
  const empty = document.getElementById("trabalhos-empty");
  const rows = data.trabalhos || [];
  body.innerHTML = "";
  empty.hidden = rows.length > 0;
  for (const item of rows) {
    const tr = document.createElement("tr");
    const localPagador = [item.local, item.pagador].filter(Boolean).join(" · ") || "—";
    tr.innerHTML = `
      <td>${item.data}</td>
      <td>${item.tipo}</td>
      <td>${localPagador}</td>
      <td>${brl(item.valor_esperado)}</td>
      <td>${brl(item.valor_recebido)}</td>
      <td><span class="badge ${item.status_recebimento}">${STATUS_LABEL[item.status_recebimento] || item.status_recebimento}</span></td>
    `;
    body.appendChild(tr);
  }
}

function paintGastos(data) {
  document.getElementById("g-total").textContent = brl(data.total_periodo);
  document.getElementById("g-pessoal").textContent = brl(data.por_lente.pessoal || 0);
  document.getElementById("g-prof").textContent = brl(
    (data.por_lente.profissional || 0) + (data.por_lente.misto || 0)
  );
  document.getElementById("g-meses").textContent = String(data.meses);
  const bars = document.getElementById("gastos-bars");
  bars.innerHTML = "";
  const max = data.max_mes || 1;
  for (const p of data.periodos || []) {
    const col = document.createElement("div");
    col.className = "bar-col";
    const hPessoal = Math.round((p.pessoal / max) * 140);
    const hProf = Math.round((p.profissional / max) * 140);
    col.innerHTML = `
      <div class="bar-value">${p.total ? brl(p.total).replace(/\s/g, "\u00a0") : "—"}</div>
      <div class="bar-stack" title="${p.label}: ${brl(p.total)}">
        <div class="bar-seg profissional" style="height:${hProf}px"></div>
        <div class="bar-seg pessoal" style="height:${hPessoal}px"></div>
      </div>
      <div class="bar-label">${p.label}</div>
    `;
    bars.appendChild(col);
  }
  const cats = document.getElementById("gastos-cats");
  cats.innerHTML = "";
  const catMax = (data.categorias[0] && data.categorias[0].total) || 1;
  if (!(data.categorias || []).length) {
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = "Sem gastos no período.";
    cats.appendChild(p);
    return;
  }
  for (const c of data.categorias) {
    const li = document.createElement("li");
    const pct = Math.max(4, Math.round((c.total / catMax) * 100));
    li.innerHTML = `
      <span>${c.categoria}</span>
      <strong>${brl(c.total)}</strong>
      <div class="cat-track"><div class="cat-fill" style="width:${pct}%"></div></div>
    `;
    cats.appendChild(li);
  }
}

function paintAll() {
  const state = MonitorApi.getState();
  paintSummary(MonitorSummary.summarize(state));
  paintTrabalhos(MonitorSummary.trabalhosView(state));
  paintGastos(MonitorSummary.gastosPorPeriodo(state, 6));
}

async function refreshAll() {
  await MonitorApi.refresh();
  paintAll();
}

function setView(name) {
  document.querySelectorAll(".view-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === name);
  });
  document.querySelectorAll(".view").forEach((panel) => {
    const on = panel.id === `view-${name}`;
    panel.hidden = !on;
    panel.classList.toggle("active", on);
  });
}

document.querySelectorAll(".view-btn").forEach((btn) => {
  btn.addEventListener("click", () => setView(btn.dataset.view));
});

function showSetup(force) {
  const cfg = MonitorApi.getConfig();
  const urlEl = document.getElementById("cfg-url");
  const tokenEl = document.getElementById("cfg-token");
  if (urlEl) urlEl.value = cfg.apiUrl || "";
  if (tokenEl) tokenEl.value = cfg.apiToken || "";
  const err = document.getElementById("setup-error");
  if (err) err.hidden = true;
  if (force || !MonitorApi.configured()) setupOverlay.hidden = false;
}

document.getElementById("btn-config").addEventListener("click", () => showSetup(true));

const cfgSave = document.getElementById("cfg-save");
if (cfgSave) {
  cfgSave.addEventListener("click", async () => {
    const url = document.getElementById("cfg-url").value.trim();
    const token = document.getElementById("cfg-token").value.trim();
    const err = document.getElementById("setup-error");
    if (!url || !token) {
      err.textContent = "Preencha URL e token.";
      err.hidden = false;
      return;
    }
    MonitorApi.saveConfig(url, token);
    try {
      await refreshAll();
      setupOverlay.hidden = true;
      addBubble("Conectado à planilha. Pode lançar pelo formulário ou pelo chat.", "bot");
    } catch (e) {
      err.textContent =
        `Falha: ${e.message}. Solução: abra a URL /exec no navegador logado no Google (não use esta página do GitHub Pages).`;
      err.hidden = false;
    }
  });
}

function openModal(kind) {
  document.getElementById("f-kind").value = kind;
  document.getElementById("modal-title").textContent =
    kind === "ganho" ? "Novo ganho" : kind === "gasto" ? "Novo gasto" : "Novo trabalho";
  document.getElementById("f-valor").value = "";
  document.getElementById("f-data").value = todayISO();
  document.getElementById("f-lente").value = kind === "ganho" ? "profissional" : "pessoal";
  document.getElementById("f-categoria").value = kind === "ganho" ? "plantao" : "outros";
  document.getElementById("f-tipo").value = "plantao";
  document.getElementById("f-pagador").value = "";
  document.getElementById("f-status").value = "realizado";
  document.getElementById("f-nota").value = "";
  document.getElementById("modal-error").hidden = true;

  const isTrabalho = kind === "trabalho";
  document.getElementById("wrap-lente").hidden = isTrabalho;
  document.getElementById("wrap-categoria").hidden = isTrabalho;
  document.getElementById("wrap-status").hidden = isTrabalho;
  document.getElementById("wrap-tipo").hidden = !isTrabalho;
  modalOverlay.hidden = false;
}

document.querySelectorAll("[data-open]").forEach((btn) => {
  btn.addEventListener("click", () => openModal(btn.dataset.open));
});

document.getElementById("modal-cancel").addEventListener("click", () => {
  modalOverlay.hidden = true;
});

document.getElementById("modal-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const kind = document.getElementById("f-kind").value;
  const err = document.getElementById("modal-error");
  try {
    await MonitorAgent.createFromForm(kind, {
      valor: document.getElementById("f-valor").value,
      data: document.getElementById("f-data").value,
      lente: document.getElementById("f-lente").value,
      categoria: document.getElementById("f-categoria").value || "outros",
      status: document.getElementById("f-status").value,
      tipo: document.getElementById("f-tipo").value,
      pagador: document.getElementById("f-pagador").value,
      local: document.getElementById("f-pagador").value,
      nota: document.getElementById("f-nota").value,
    });
    await refreshAll();
    modalOverlay.hidden = true;
    addBubble(`Salvo: ${kind}.`, "bot");
  } catch (ex) {
    err.textContent = ex.message || String(ex);
    err.hidden = false;
  }
});

async function sendMessage(text) {
  addBubble(text, "user");
  const data = await MonitorAgent.handle(text);
  addBubble(data.reply || "Sem resposta.", "bot");
  if (data.summary) paintSummary(data.summary);
  await refreshAll();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  input.focus();
  try {
    await sendMessage(text);
  } catch (err) {
    addBubble(`Falha: ${err.message}`, "bot");
  }
});

(async function boot() {
  if (MonitorApi.isEmbedded && MonitorApi.isEmbedded()) {
    const btn = document.getElementById("btn-config");
    if (btn) btn.hidden = true;
    setupOverlay.hidden = true;
    try {
      await refreshAll();
      addBubble(
        "Olá. Monitor conectado à sua planilha.\nUse + Ganho / + Gasto / + Trabalho ou o chat.",
        "bot"
      );
    } catch (err) {
      addBubble(`Não consegui carregar: ${err.message}\nConfira SPREADSHEET_ID e se rodou setupSheets().`, "bot");
    }
    return;
  }

  showSetup(false);
  if (!MonitorApi.configured()) {
    addBubble(
      "Este GitHub Pages só funciona se o Apps Script estiver como “Qualquer pessoa”.\nMais fácil: abra a URL /exec do Apps Script no celular (logado no Google).",
      "bot"
    );
    return;
  }
  try {
    await refreshAll();
    setupOverlay.hidden = true;
    addBubble(
      "Olá. Sou o Monitor Financeiro.\nUse + Ganho / + Gasto / + Trabalho ou o chat — eu confirmo antes de gravar no chat.",
      "bot"
    );
  } catch (err) {
    showSetup(true);
    addBubble(`Não consegui carregar os dados: ${err.message}`, "bot");
  }
})();
