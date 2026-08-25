/**
 * Monitor Financeiro — API sobre Google Sheets
 *
 * Setup (uma vez):
 * 1. Crie uma planilha Google Sheets vazia.
 * 2. Extensões > Apps Script > cole este arquivo.
 * 3. Propriedades do script (engrenagem > Propriedades do script):
 *      API_TOKEN = um segredo longo (ex.: openssl rand -hex 24)
 *      SPREADSHEET_ID = id da planilha (da URL /d/ID/edit)
 * 4. Execute a função setupSheets() uma vez (autorizar).
 * 5. Implantar > Nova implantação > App da Web
 *      Executar como: Eu
 *      Quem tem acesso: Qualquer pessoa
 * 6. Copie a URL da implantação para docs/js/config.js
 */

var SHEETS = {
  lancamentos: [
    "id",
    "tipo",
    "valor",
    "data_caixa",
    "data_competencia",
    "lente",
    "categoria",
    "status",
    "nota",
    "pagador",
    "created_at",
  ],
  trabalhos: [
    "id",
    "data",
    "tipo",
    "local",
    "pagador",
    "valor_esperado",
    "nota",
    "created_at",
  ],
  vinculos: ["id", "lancamento_id", "trabalho_id", "valor", "created_at"],
  meta: ["key", "value"],
};

function setupSheets() {
  var ss = getSpreadsheet_();
  Object.keys(SHEETS).forEach(function (name) {
    var sh = ss.getSheetByName(name);
    if (!sh) sh = ss.insertSheet(name);
    sh.clear();
    sh.getRange(1, 1, 1, SHEETS[name].length).setValues([SHEETS[name]]);
  });
  // remove default Sheet1 if empty
  var def = ss.getSheetByName("Página1") || ss.getSheetByName("Sheet1");
  if (def && ss.getSheets().length > 1) {
    try {
      ss.deleteSheet(def);
    } catch (e) {}
  }
  setMeta_("profile", JSON.stringify({ name: "Médico", started_at: null, onboarding_done: 0 }));
  setMeta_("pending", "");
  return { ok: true, spreadsheetId: ss.getId() };
}

function doGet(e) {
  var params = (e && e.parameter) || {};
  // payload/name podem vir como JSON string na query (JSONP)
  params = normalizeParams_(params);
  var result = dispatch_(params);
  if (params.callback) {
    return ContentService.createTextOutput(
      params.callback + "(" + JSON.stringify(result) + ")"
    ).setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return json_(result);
}

function doPost(e) {
  var body = {};
  try {
    var raw = (e && e.postData && e.postData.contents) || "{}";
    body = JSON.parse(raw);
  } catch (err) {
    return json_({ ok: false, error: "JSON inválido" });
  }
  return json_(dispatch_(normalizeParams_(body)));
}

function normalizeParams_(req) {
  var out = {};
  for (var k in req) {
    if (Object.prototype.hasOwnProperty.call(req, k)) out[k] = req[k];
  }
  if (typeof out.payload === "string") {
    if (out.payload === "" || out.payload === "null") {
      out.payload = null;
    } else {
      try {
        out.payload = JSON.parse(out.payload);
      } catch (err) {
        // mantém string se não for JSON
      }
    }
  }
  return out;
}

/** Retorna objeto JS (não ContentService). */
function dispatch_(req) {
  try {
    if (!checkToken_(req.token)) {
      return { ok: false, error: "Token inválido" };
    }
    var action = String(req.action || "getAll");
    if (action === "setup") return setupSheets();
    if (action === "getAll") return { ok: true, data: getAll_() };
    if (action === "addLancamento") return { ok: true, item: addLancamento_(req.payload || {}) };
    if (action === "addTrabalho") return { ok: true, item: addTrabalho_(req.payload || {}) };
    if (action === "addVinculo") return { ok: true, item: addVinculo_(req.payload || {}) };
    if (action === "setPending") {
      setMeta_("pending", req.payload == null ? "" : JSON.stringify(req.payload));
      return { ok: true };
    }
    if (action === "setOnboarding") {
      var profile = {
        name: req.name || "Médico",
        started_at: now_(),
        onboarding_done: 1,
      };
      setMeta_("profile", JSON.stringify(profile));
      return { ok: true, profile: profile };
    }
    if (action === "applyPagamentoVinculado") {
      return { ok: true, result: applyPagamentoVinculado_(req.payload || {}) };
    }
    return { ok: false, error: "Ação desconhecida: " + action };
  } catch (err) {
    return { ok: false, error: String(err && err.message ? err.message : err) };
  }
}

function checkToken_(token) {
  var expected = PropertiesService.getScriptProperties().getProperty("API_TOKEN");
  return expected && token && String(token) === String(expected);
}

function getSpreadsheet_() {
  var id = PropertiesService.getScriptProperties().getProperty("SPREADSHEET_ID");
  if (!id) throw new Error("Defina SPREADSHEET_ID nas propriedades do script");
  return SpreadsheetApp.openById(id);
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function now_() {
  return Utilities.formatDate(new Date(), Session.getScriptTimeZone() || "America/Sao_Paulo", "yyyy-MM-dd'T'HH:mm:ss");
}

function uid_() {
  return Utilities.getUuid().replace(/-/g, "").slice(0, 12);
}

function sheet_(name) {
  var sh = getSpreadsheet_().getSheetByName(name);
  if (!sh) throw new Error("Aba ausente: " + name + " — execute setupSheets()");
  return sh;
}

function readRows_(name) {
  var sh = sheet_(name);
  var values = sh.getDataRange().getValues();
  if (values.length < 2) return [];
  var headers = values[0].map(String);
  var out = [];
  for (var i = 1; i < values.length; i++) {
    var row = values[i];
    if (!row[0]) continue;
    var obj = {};
    for (var c = 0; c < headers.length; c++) {
      var key = headers[c];
      var val = row[c];
      if (val instanceof Date) {
        val = Utilities.formatDate(val, Session.getScriptTimeZone() || "America/Sao_Paulo", "yyyy-MM-dd");
      }
      if ((key === "valor" || key === "valor_esperado") && val !== "" && val != null) {
        val = Number(val);
      }
      obj[key] = val === "" ? null : val;
    }
    out.push(obj);
  }
  return out;
}

function appendRow_(name, obj) {
  var headers = SHEETS[name];
  var row = headers.map(function (h) {
    var v = obj[h];
    return v == null ? "" : v;
  });
  sheet_(name).appendRow(row);
  return obj;
}

function getMetaMap_() {
  var rows = readRows_("meta");
  var map = {};
  rows.forEach(function (r) {
    map[r.key] = r.value;
  });
  return map;
}

function setMeta_(key, value) {
  var sh = sheet_("meta");
  var values = sh.getDataRange().getValues();
  for (var i = 1; i < values.length; i++) {
    if (String(values[i][0]) === key) {
      sh.getRange(i + 1, 2).setValue(value == null ? "" : value);
      return;
    }
  }
  sh.appendRow([key, value == null ? "" : value]);
}

function getAll_() {
  var meta = getMetaMap_();
  var pending = null;
  if (meta.pending) {
    try {
      pending = JSON.parse(meta.pending);
    } catch (e) {
      pending = null;
    }
  }
  var profile = { name: "Médico", started_at: null, onboarding_done: 0 };
  if (meta.profile) {
    try {
      profile = JSON.parse(meta.profile);
    } catch (e) {}
  }
  return {
    lancamentos: readRows_("lancamentos"),
    trabalhos: readRows_("trabalhos"),
    vinculos: readRows_("vinculos"),
    profile: profile,
    pending: pending,
  };
}

function addLancamento_(p) {
  var item = {
    id: uid_(),
    tipo: p.tipo,
    valor: Number(p.valor),
    data_caixa: p.data_caixa,
    data_competencia: p.data_competencia || p.data_caixa,
    lente: p.lente,
    categoria: p.categoria,
    status: p.status || "realizado",
    nota: p.nota || "",
    pagador: p.pagador || "",
    created_at: now_(),
  };
  return appendRow_("lancamentos", item);
}

function addTrabalho_(p) {
  var item = {
    id: uid_(),
    data: p.data,
    tipo: p.tipo,
    local: p.local || "",
    pagador: p.pagador || "",
    valor_esperado: Number(p.valor_esperado),
    nota: p.nota || "",
    created_at: now_(),
  };
  return appendRow_("trabalhos", item);
}

function addVinculo_(p) {
  var item = {
    id: uid_(),
    lancamento_id: p.lancamento_id,
    trabalho_id: p.trabalho_id,
    valor: Number(p.valor),
    created_at: now_(),
  };
  return appendRow_("vinculos", item);
}

function applyPagamentoVinculado_(p) {
  var lanc = addLancamento_({
    tipo: "entrada",
    valor: p.valor,
    data_caixa: p.data_caixa,
    data_competencia: p.data_competencia,
    lente: "profissional",
    categoria: p.categoria || "convenio",
    status: "realizado",
    nota: p.nota,
    pagador: p.pagador,
  });
  var vinculos = [];
  (p.alocacoes || []).forEach(function (a) {
    vinculos.push(
      addVinculo_({
        lancamento_id: lanc.id,
        trabalho_id: a.trabalho_id,
        valor: a.valor,
      })
    );
  });
  setMeta_("pending", "");
  return { lancamento: lanc, vinculos: vinculos };
}
