/** Cliente da API Google Apps Script (Sheets). */
(function (global) {
  const LS_URL = "monitor_api_url";
  const LS_TOKEN = "monitor_api_token";

  function getConfig() {
    const cfg = global.MONITOR_CONFIG || {};
    return {
      apiUrl: (localStorage.getItem(LS_URL) || cfg.apiUrl || "").trim(),
      apiToken: (localStorage.getItem(LS_TOKEN) || cfg.apiToken || "").trim(),
    };
  }

  function saveConfig(apiUrl, apiToken) {
    localStorage.setItem(LS_URL, apiUrl.trim());
    localStorage.setItem(LS_TOKEN, apiToken.trim());
  }

  function configured() {
    const c = getConfig();
    return Boolean(c.apiUrl && c.apiToken);
  }

  async function call(action, extra = {}) {
    const { apiUrl, apiToken } = getConfig();
    if (!apiUrl || !apiToken) throw new Error("Configure a URL da API e o token.");

    const payload = { token: apiToken, action, ...extra };
    const res = await fetch(apiUrl, {
      method: "POST",
      // text/plain evita preflight CORS no Apps Script
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(payload),
      redirect: "follow",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Erro na API");
    return data;
  }

  /** Estado em memória sincronizado com a planilha */
  let state = {
    lancamentos: [],
    trabalhos: [],
    vinculos: [],
    profile: { name: "Médico", started_at: null, onboarding_done: 0 },
    pending: null,
  };

  function getState() {
    return state;
  }

  async function refresh() {
    const data = await call("getAll");
    state = {
      lancamentos: data.data.lancamentos || [],
      trabalhos: data.data.trabalhos || [],
      vinculos: data.data.vinculos || [],
      profile: data.data.profile || state.profile,
      pending: data.data.pending || null,
    };
    return state;
  }

  async function setPending(pending) {
    await call("setPending", { payload: pending });
    state.pending = pending;
  }

  async function setOnboarding(name) {
    const res = await call("setOnboarding", { name: name || "Médico" });
    state.profile = res.profile;
    return res.profile;
  }

  async function addLancamento(payload) {
    const res = await call("addLancamento", { payload });
    state.lancamentos.unshift(res.item);
    state.pending = null;
    await call("setPending", { payload: null });
    return res.item;
  }

  async function addTrabalho(payload) {
    const res = await call("addTrabalho", { payload });
    state.trabalhos.unshift(res.item);
    state.pending = null;
    await call("setPending", { payload: null });
    return res.item;
  }

  async function applyPagamentoVinculado(payload) {
    const res = await call("applyPagamentoVinculado", { payload });
    state.lancamentos.unshift(res.result.lancamento);
    (res.result.vinculos || []).forEach((v) => state.vinculos.unshift(v));
    state.pending = null;
    return res.result;
  }

  global.MonitorApi = {
    getConfig,
    saveConfig,
    configured,
    call,
    getState,
    refresh,
    setPending,
    setOnboarding,
    addLancamento,
    addTrabalho,
    applyPagamentoVinculado,
  };
})(window);
