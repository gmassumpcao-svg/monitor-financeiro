/** Agente por regras em português (port de app/agent.py). */
(function (global) {
  const MONTHS = {
    janeiro: 1, jan: 1, fevereiro: 2, fev: 2, marco: 3, março: 3, mar: 3,
    abril: 4, abr: 4, maio: 5, mai: 5, junho: 6, jun: 6, julho: 7, jul: 7,
    agosto: 8, ago: 8, setembro: 9, set: 9, outubro: 10, out: 10,
    novembro: 11, nov: 11, dezembro: 12, dez: 12,
  };

  const PROF_INCOME_CATS = {
    plantao: "plantao", plantão: "plantao", convenio: "convenio", convênio: "convenio",
    unimed: "convenio", bradesco: "convenio", sulamerica: "convenio", sulamérica: "convenio",
    particular: "honorario_particular", honorario: "honorario_particular", honorário: "honorario_particular",
  };

  const PROF_EXPENSE_CATS = {
    sala: "aluguel_sala", "aluguel de sala": "aluguel_sala", material: "material",
    contador: "pessoal_contador", crm: "conselho_seguro", das: "imposto", imposto: "imposto",
  };

  const PERS_EXPENSE_CATS = {
    casa: "moradia", aluguel: "moradia", moradia: "moradia", escola: "familia_escola",
    familia: "familia_escola", família: "familia_escola", mercado: "alimentacao",
    alimentação: "alimentacao", alimentacao: "alimentacao", comida: "alimentacao",
    uber: "transporte", carro: "transporte", lazer: "lazer",
  };

  function brl(v) {
    return (Number(v) || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  function parseAmountToken(raw) {
    let s = raw;
    if (s.includes(",") && s.includes(".")) s = s.replace(/\./g, "").replace(",", ".");
    else if (s.includes(",")) s = s.replace(",", ".");
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
  }

  function money(text) {
    let cleaned = text.replace(/\b\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?\b/g, " ");
    cleaned = cleaned.replace(/\b\d{1,2}[\/\-]\d{4}\b/g, " ");
    const explicit = [...cleaned.matchAll(/r\$\s*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+(?:[.,]\d{1,2})?)/gi)];
    if (explicit.length) return parseAmountToken(explicit[explicit.length - 1][1]);
    const candidates = [...cleaned.matchAll(/(\d{1,3}(?:\.\d{3})*,\d{2}|\d{2,}(?:[.,]\d{1,2})?)/g)];
    for (let i = candidates.length - 1; i >= 0; i--) {
      const val = parseAmountToken(candidates[i][1]);
      if (val != null && val >= 1) return val;
    }
    return null;
  }

  function parseDate(text, defaultDate) {
    const d0 = defaultDate || new Date();
    const m = text.match(/\b(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?\b/);
    if (m) {
      let year = d0.getFullYear();
      if (m[3]) {
        year = Number(m[3]);
        if (year < 100) year += 2000;
      }
      const mo = Number(m[2]);
      const d = Number(m[1]);
      const dt = new Date(year, mo - 1, d);
      if (dt.getFullYear() === year && dt.getMonth() === mo - 1 && dt.getDate() === d) {
        return `${year}-${String(mo).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
      }
    }
    return `${d0.getFullYear()}-${String(d0.getMonth() + 1).padStart(2, "0")}-${String(d0.getDate()).padStart(2, "0")}`;
  }

  function monthYear(text) {
    const today = new Date();
    const textN = text.toLowerCase();
    for (const [name, mo] of Object.entries(MONTHS)) {
      if (new RegExp(`\\b${name}\\b`).test(textN)) {
        const ym = textN.match(new RegExp(`\\b${name}\\s+(?:de\\s+)?(\\d{4})\\b`));
        let year = ym ? Number(ym[1]) : today.getFullYear();
        if (!ym && mo > today.getMonth() + 1 && textN.includes("referente")) year = today.getFullYear() - 1;
        return [year, mo];
      }
    }
    const m = textN.match(/\b(\d{1,2})[\/\-](\d{4})\b/);
    if (m) return [Number(m[2]), Number(m[1])];
    if (/este mês|esse mês|este mes|esse mes/.test(textN)) return [today.getFullYear(), today.getMonth() + 1];
    if (/mês passado|mes passado/.test(textN)) {
      if (today.getMonth() === 0) return [today.getFullYear() - 1, 12];
      return [today.getFullYear(), today.getMonth()];
    }
    return null;
  }

  function fmtTrabalho(t) {
    const bits = [t.data, t.tipo];
    if (t.local) bits.push(t.local);
    if (t.pagador) bits.push(t.pagador);
    bits.push(`esperado ${brl(t.valor_esperado)}`);
    bits.push(`em aberto ${brl(t.saldo_receber)}`);
    return bits.join(" · ");
  }

  function guessLenteCategoria(low, tipo) {
    if (tipo === "entrada") {
      for (const [k, cat] of Object.entries(PROF_INCOME_CATS)) {
        if (low.includes(k)) return ["profissional", cat];
      }
      return ["profissional", "outros_ganhos"];
    }
    for (const [k, cat] of Object.entries(PERS_EXPENSE_CATS)) {
      if (low.includes(k)) {
        if (low.includes("sala")) return ["profissional", "aluguel_sala"];
        return ["pessoal", cat];
      }
    }
    for (const [k, cat] of Object.entries(PROF_EXPENSE_CATS)) {
      if (low.includes(k)) return ["profissional", cat];
    }
    if (/sala|crm|das|consultório|consultorio/.test(low)) return ["profissional", "outros"];
    if (/casa|escola|mercado/.test(low)) return ["pessoal", "outros"];
    return ["pessoal", "outros"];
  }

  async function proposeLancamento(text, low, tipo) {
    const state = MonitorApi.getState();
    const valor = money(text);
    if (valor == null) {
      return {
        reply: "Não achei o valor. Ex.: “Recebi 4200 de plantão”.",
        pending: state.pending,
        summary: MonitorSummary.summarize(state),
      };
    }
    const [lente, categoria] = guessLenteCategoria(low, tipo);
    const data_caixa = parseDate(text);
    const status = /\b(vou pagar|a pagar|previsto|vai sair)\b/.test(low) ? "previsto" : "realizado";
    let pagador = null;
    for (const name of ["unimed", "bradesco", "sulamerica", "sulamérica", "particular"]) {
      if (low.includes(name)) {
        pagador = { unimed: "Unimed", bradesco: "Bradesco", sulamerica: "SulAmérica", sulamérica: "SulAmérica", particular: "Particular" }[name];
        break;
      }
    }
    const action = {
      action: "create_lancamento",
      label: `${tipo === "entrada" ? "Entrada" : "Saída"} ${brl(valor)} · ${lente} · ${categoria}`,
      payload: { tipo, valor, data_caixa, lente, categoria, status, nota: text, pagador },
    };
    await MonitorApi.setPending(action);
    let askLente = "";
    if (tipo === "saida" && lente === "pessoal" && !Object.keys(PERS_EXPENSE_CATS).some((k) => low.includes(k))) {
      askLente = "\n(Assumi **pessoal**. Se for profissional, cancele e diga “paguei … de sala/CRM/DAS”.)";
    }
    return {
      reply:
        `Posso gravar?\n• Tipo: ${tipo === "entrada" ? "entrada" : "saída"}\n• Valor: ${brl(valor)}\n` +
        `• Data: ${data_caixa}\n• Lente: ${lente}\n• Categoria: ${categoria}\n• Status: ${status}\n` +
        `Responda **sim** ou **não**.${askLente}`,
      pending: action,
      summary: MonitorSummary.summarize(MonitorApi.getState()),
    };
  }

  async function proposeTrabalho(text, low) {
    const state = MonitorApi.getState();
    const valor = money(text);
    if (valor == null) {
      return {
        reply: "Para registrar o trabalho, preciso do valor esperado. Ex.: “Fiz plantão dia 10/06 no Hospital X, Unimed, 1800”.",
        pending: state.pending,
        summary: MonitorSummary.summarize(state),
      };
    }
    let tipo = "outro";
    if (low.includes("consulta")) tipo = "consulta";
    else if (low.includes("procedimento")) tipo = "procedimento";
    else if (low.includes("plant")) tipo = "plantao";

    const data_t = parseDate(text);
    let local = null;
    const mLoc = low.match(/\bno\s+([^,]+?)(?:,|\s+unimed|\s+bradesco|\s+\d|$)/);
    if (mLoc) local = mLoc[1].trim().replace(/\b\w/g, (c) => c.toUpperCase());

    let pagador = null;
    const map = { unimed: "Unimed", bradesco: "Bradesco", sulamerica: "SulAmérica", sulamérica: "SulAmérica", particular: "Particular", hospital: "Hospital" };
    for (const [name, label] of Object.entries(map)) {
      if (low.includes(name)) { pagador = label; break; }
    }

    const action = {
      action: "create_trabalho",
      label: `Trabalho ${tipo} ${data_t} ${brl(valor)}`,
      payload: { data: data_t, tipo, local, pagador, valor_esperado: valor, nota: text },
    };
    await MonitorApi.setPending(action);
    return {
      reply:
        `Registrar trabalho feito?\n• Data: ${data_t}\n• Tipo: ${tipo}\n• Local: ${local || "—"}\n` +
        `• Pagador: ${pagador || "—"}\n• Valor esperado: ${brl(valor)}\nResponda **sim** ou **não**.`,
      pending: action,
      summary: MonitorSummary.summarize(MonitorApi.getState()),
    };
  }

  async function proposeVinculo(text, low) {
    const state = MonitorApi.getState();
    const valor = money(text);
    if (valor == null) {
      return {
        reply: "Não achei o valor que caiu. Ex.: “Caiu 3600 da Unimed referente a junho”.",
        pending: state.pending,
        summary: MonitorSummary.summarize(state),
      };
    }
    let pagador = null;
    for (const [name, label] of [["unimed", "Unimed"], ["bradesco", "Bradesco"], ["sulamérica", "SulAmérica"], ["sulamerica", "SulAmérica"]]) {
      if (low.includes(name)) { pagador = label; break; }
    }
    const my = monthYear(low);
    if (!my) {
      return {
        reply: "De qual mês é esse pagamento? Ex.: “referente a junho” ou “referente a 06/2026”.",
        pending: state.pending,
        summary: MonitorSummary.summarize(state),
      };
    }
    const [year, month] = my;
    let candidatos = MonitorSummary.trabalhosAbertosNoPeriodo(state, year, month, pagador);
    if (!candidatos.length) {
      candidatos = MonitorSummary.trabalhosAbertosNoPeriodo(state, year, month, null);
      if (!candidatos.length) {
        return {
          reply:
            `Não achei trabalhos em aberto em ${String(month).padStart(2, "0")}/${year}` +
            `${pagador ? ` para ${pagador}` : ""}. Cadastre o trabalho primeiro (“Fiz plantão…”) e tente de novo.`,
          pending: null,
          summary: MonitorSummary.summarize(state),
        };
      }
    }
    let restante = valor;
    const alocacoes = [];
    for (const t of candidatos.slice().sort((a, b) => String(a.data).localeCompare(String(b.data)))) {
      if (restante <= 0.009) break;
      const usa = Math.min(t.saldo_receber, restante);
      alocacoes.push({ trabalho_id: t.id, valor: Math.round(usa * 100) / 100, resumo: fmtTrabalho(t) });
      restante = Math.round((restante - usa) * 100) / 100;
    }
    const data_caixa = parseDate(text);
    const action = {
      action: "create_pagamento_vinculado",
      label: `Pagamento ${brl(valor)} → ${alocacoes.length} trabalho(s)`,
      payload: {
        valor, data_caixa,
        data_competencia: `${year}-${String(month).padStart(2, "0")}-01`,
        pagador: pagador || "Convênio", categoria: "convenio", lente: "profissional",
        nota: text, alocacoes, sobra: restante,
      },
    };
    await MonitorApi.setPending(action);
    const lines = alocacoes.map((a) => `• ${brl(a.valor)} → ${a.resumo}`);
    let sobraMsg = "";
    if (restante > 0.009) {
      sobraMsg = `\n\nSobra ${brl(restante)} sem trabalho correspondente. O lançamento entra mesmo assim; a sobra fica sem vínculo.`;
    }
    const totalAlocado = Math.round((valor - restante) * 100) / 100;
    const esperado = Math.round(candidatos.reduce((s, t) => s + t.saldo_receber, 0) * 100) / 100;
    let diffMsg = "";
    if (Math.abs(valor - esperado) > 0.009 && restante <= 0.009 && totalAlocado < esperado) {
      diffMsg = `\n(Pagamento parcial: em aberto no período era ${brl(esperado)}.)`;
    } else if (valor + 0.009 < esperado && restante <= 0.009) {
      diffMsg = `\n(Em aberto no período: ${brl(esperado)}. Isto quita só parte.)`;
    }
    return {
      reply:
        `Sugestão de vínculo para ${brl(valor)}${pagador ? ` da ${pagador}` : ""} referente a ${String(month).padStart(2, "0")}/${year}:\n` +
        lines.join("\n") + sobraMsg + diffMsg +
        "\n\nGravo o recebimento profissional e esses vínculos? **sim** / **não**.",
      pending: action,
      summary: MonitorSummary.summarize(MonitorApi.getState()),
    };
  }

  async function applyPending(pending) {
    const action = pending.action;
    const payload = pending.payload || {};
    if (action === "create_lancamento") {
      const item = await MonitorApi.addLancamento(payload);
      return {
        reply: `Gravado: ${pending.label} (id ${item.id}).`,
        pending: null,
        summary: MonitorSummary.summarize(MonitorApi.getState()),
      };
    }
    if (action === "create_trabalho") {
      const item = await MonitorApi.addTrabalho(payload);
      return {
        reply: `Trabalho registrado (id ${item.id}). Ele entra em **a receber** até vincular um pagamento.`,
        pending: null,
        summary: MonitorSummary.summarize(MonitorApi.getState()),
      };
    }
    if (action === "create_pagamento_vinculado") {
      await MonitorApi.applyPagamentoVinculado(payload);
      const n = (payload.alocacoes || []).length;
      const sobra = payload.sobra || 0;
      const extra = sobra > 0.009 ? ` Sobra sem vínculo: ${brl(sobra)}.` : "";
      return {
        reply: `Recebimento gravado e vinculado a ${n} trabalho(s).${extra}`,
        pending: null,
        summary: MonitorSummary.summarize(MonitorApi.getState()),
      };
    }
    await MonitorApi.setPending(null);
    return {
      reply: "Não consegui aplicar essa confirmação. Tente de novo.",
      pending: null,
      summary: MonitorSummary.summarize(MonitorApi.getState()),
    };
  }

  async function handle(message) {
    const text = (message || "").trim();
    const state = MonitorApi.getState();
    if (!text) {
      return {
        reply: "Pode falar — lançamento, trabalho feito, pagamento de convênio ou “como foi o mês?”.",
        pending: state.pending,
        summary: MonitorSummary.summarize(state),
      };
    }
    const low = text.toLowerCase();
    let pending = state.pending;

    if (pending && /^(sim|s|confirmo|confirma|ok|pode|pode gravar|isso)$/.test(low)) {
      return applyPending(pending);
    }
    if (pending && /^(não|nao|n|cancela|cancelar)$/.test(low)) {
      await MonitorApi.setPending(null);
      return {
        reply: "Ok, não gravei nada. Pode reformular.",
        pending: null,
        summary: MonitorSummary.summarize(MonitorApi.getState()),
      };
    }

    if (/\b(sou eu|começo agora|comeco agora|olá|ola|oi)\b/.test(low) || ["começar", "comecar", "start"].includes(low)) {
      const profile = await MonitorApi.setOnboarding();
      return {
        reply:
          "Olá. Sou o Monitor Financeiro — seu controle da vida (casa + trabalho).\n\n" +
          "Pode me dizer, por exemplo:\n" +
          "• “Recebi 4200 de plantão”\n• “Paguei 2500 de aluguel de casa”\n" +
          "• “Fiz plantão dia 10/06 no Hospital X, Unimed, 1800”\n" +
          "• “Caiu 3600 da Unimed referente a junho”\n• “Como foi o mês?”\n\n" +
          "Eu sempre peço confirmação antes de gravar.",
        pending: null,
        summary: MonitorSummary.summarize(MonitorApi.getState()),
        profile,
      };
    }

    if (/como foi|resumo|caixa|sobrou|balanço|balanco/.test(low)) {
      const my = monthYear(low) || [new Date().getFullYear(), new Date().getMonth() + 1];
      const s = MonitorSummary.summarize(state, my[0], my[1]);
      const reply =
        `**${String(s.mes).padStart(2, "0")}/${s.ano}**\n` +
        `Entrou ${brl(s.entrou)} · Saiu ${brl(s.saiu)}\n` +
        `**Sobrou na conta:** ${brl(s.sobrou_conta)}\n` +
        `A pagar (previsto): ${brl(s.a_pagar)}\n` +
        `Reserva imposto (est. 20% prof.): ${brl(s.reserva_imposto_estimada)}\n` +
        `**Sobrou de verdade:** ${brl(s.sobrou_verdade)}\n\n` +
        `Pessoal → saldo ${brl(s.por_lente.pessoal.saldo)}\n` +
        `Profissional → saldo ${brl(s.por_lente.profissional.saldo)}`;
      return { reply, pending, summary: s };
    }

    if (/a receber|receber|em aberto|o que ainda/.test(low) && !low.includes("pagar")) {
      const s = MonitorSummary.summarize(state);
      const abertos = s.trabalhos_abertos;
      const reply = !abertos.length
        ? "Nada a receber no momento — todos os trabalhos estão quitados ou ainda não há trabalhos."
        : `**A receber:** ${brl(s.a_receber)}\n` + abertos.slice(0, 12).map((t) => `• ${fmtTrabalho(t)}`).join("\n");
      return { reply, pending, summary: s };
    }

    if (/a pagar|contas a pagar|vai sair/.test(low)) {
      const s = MonitorSummary.summarize(state);
      const prev = s.previstos.filter((l) => l.tipo === "saida");
      const reply = !prev.length
        ? `**A pagar (previsto):** ${brl(s.a_pagar)} — nenhuma conta prevista cadastrada.`
        : `**A pagar:** ${brl(s.a_pagar)}\n` +
          prev.map((l) => `• ${l.data_caixa} · ${l.categoria} · ${l.lente} · ${brl(l.valor)}`).join("\n");
      return { reply, pending, summary: s };
    }

    if (/\b(caiu|recebi da|recebimento da|pagamento da|pagou a)\b/.test(low) || (/\breferente a\b/.test(low) && money(low))) {
      return proposeVinculo(text, low);
    }
    if (/\b(recebi|entrou|ganhei)\b/.test(low)) return proposeLancamento(text, low, "entrada");
    if (/\b(paguei|gastei|saí|saiu|despesa)\b/.test(low)) return proposeLancamento(text, low, "saida");
    if (/\b(fiz|atendi|plantei)\b/.test(low) || /\b(registrar|cadastre|cadastrar)\s+(plantão|plantao|consulta|procedimento)\b/.test(low)) {
      return proposeTrabalho(text, low);
    }

    if (pending) {
      return {
        reply: `Ainda tenho uma ação esperando confirmação. Responda **sim** ou **não**.\nPendente: ${pending.label || pending.action}`,
        pending,
        summary: MonitorSummary.summarize(state),
      };
    }

    return {
      reply:
        "Não entendi com segurança. Exemplos:\n• Recebi 3000 de particular\n• Paguei 1800 de escola\n" +
        "• Fiz plantão dia 05/06 no Hospital Y, Unimed, 2000\n• Caiu 4000 da Unimed referente a junho\n• Como foi o mês?",
      pending: null,
      summary: MonitorSummary.summarize(state),
    };
  }

  /** Criação direta via formulário (com confirmação implícita). */
  async function createFromForm(kind, fields) {
    if (kind === "gasto" || kind === "ganho") {
      const item = await MonitorApi.addLancamento({
        tipo: kind === "ganho" ? "entrada" : "saida",
        valor: Number(fields.valor),
        data_caixa: fields.data,
        lente: fields.lente,
        categoria: fields.categoria,
        status: fields.status || "realizado",
        nota: fields.nota || "",
        pagador: fields.pagador || "",
      });
      return { ok: true, item, summary: MonitorSummary.summarize(MonitorApi.getState()) };
    }
    if (kind === "trabalho") {
      const item = await MonitorApi.addTrabalho({
        data: fields.data,
        tipo: fields.tipo,
        local: fields.local || "",
        pagador: fields.pagador || "",
        valor_esperado: Number(fields.valor),
        nota: fields.nota || "",
      });
      return { ok: true, item, summary: MonitorSummary.summarize(MonitorApi.getState()) };
    }
    throw new Error("Tipo de formulário desconhecido");
  }

  global.MonitorAgent = { handle, createFromForm, brl };
})(window);
