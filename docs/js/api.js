/** Cliente da API Google Apps Script (Sheets) via JSONP — evita CORS/Failed to fetch. */
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
    localStorage.setItem(LS_URL, apiUrl.trim().replace(/\?.*$/, ""));
    localStorage.setItem(LS_TOKEN, apiToken.trim());
  }

  function configured() {
    const c = getConfig();
    return Boolean(c.apiUrl && c.apiToken);
  }

  function jsonp(apiUrl, params) {
    return new Promise((resolve, reject) => {
      const callbackName = "gas_cb_" + Date.now() + "_" + Math.floor(Math.random() * 1e6);
      const script = document.createElement("script");
      const timer = setTimeout(() => {
        cleanup();
        reject(new Error("Tempo esgotado. Confira a URL /exec e a implantação (Qualquer pessoa)."));
      }, 25000);

      function cleanup() {
        clearTimeout(timer);
        try {
          delete window[callbackName];
        } catch (e) {
          window[callbackName] = undefined;
        }
        if (script.parentNode) script.parentNode.removeChild(script);
      }

      window[callbackName] = (data) => {
        cleanup();
        resolve(data);
      };

      script.onerror = () => {
        cleanup();
        reject(
          new Error(
            "Falha ao carregar o Apps Script. Use a URL que termina em /exec, acesso “Qualquer pessoa”, e faça Nova versão após atualizar o Code.gs."
          )
        );
      };

      const q = new URLSearchParams();
      Object.keys(params).forEach((key) => {
        const val = params[key];
        if (val === undefined) return;
        if (val === null) {
          q.set(key, "null");
          return;
        }
        if (typeof val === "object") {
          q.set(key, JSON.stringify(val));
          return;
        }
        q.set(key, String(val));
      });
      q.set("callback", callbackName);

      const base = apiUrl.replace(/\?.*$/, "").replace(/\/$/, "");
      script.src = base + "?" + q.toString();
      document.body.appendChild(script);
    });
  }

  async function call(action, extra = {}) {
    const { apiUrl, apiToken } = getConfig();
    if (!apiUrl || !apiToken) throw new Error("Configure a URL da API e o token.");
    if (!/\/exec$/i.test(apiUrl.replace(/\?.*$/, ""))) {
      throw new Error("A URL deve terminar em /exec (não use /dev).");
    }

    const params = { token: apiToken, action, ...extra };
    const data = await jsonp(apiUrl, params);
    if (!data || !data.ok) throw new Error((data && data.error) || "Erro na API");
    return data;
  }

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
