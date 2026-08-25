/** Resumos: caixa, trabalhos, gastos (port de app/summary.py + trechos de db). */
(function (global) {
  const MONTH_LABELS = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

  function today() {
    return new Date();
  }

  function monthBounds(year, month) {
    const t = today();
    return [year || t.getFullYear(), month || t.getMonth() + 1];
  }

  function shiftMonth(year, month, delta) {
    const idx = year * 12 + (month - 1) + delta;
    return [Math.floor(idx / 12), (idx % 12) + 1];
  }

  function listLancamentos(state, year, month) {
    let rows = state.lancamentos || [];
    if (year && month) {
      const prefix = `${String(year).padStart(4, "0")}-${String(month).padStart(2, "0")}`;
      rows = rows.filter((l) => String(l.data_caixa || "").startsWith(prefix));
    }
    return rows.slice().sort((a, b) => String(b.data_caixa).localeCompare(String(a.data_caixa)));
  }

  function trabalhosComRecebido(state) {
    const byTrabalho = {};
    (state.vinculos || []).forEach((v) => {
      byTrabalho[v.trabalho_id] = (byTrabalho[v.trabalho_id] || 0) + Number(v.valor || 0);
    });
    return (state.trabalhos || [])
      .map((t) => {
        const valor_recebido = Math.round((byTrabalho[t.id] || 0) * 100) / 100;
        const valor_esperado = Number(t.valor_esperado) || 0;
        const saldo_receber = Math.round((valor_esperado - valor_recebido) * 100) / 100;
        let status_recebimento = "aberto";
        if (saldo_receber <= 0.009) status_recebimento = "pago";
        else if (valor_recebido > 0) status_recebimento = "parcial";
        return { ...t, valor_esperado, valor_recebido, saldo_receber, status_recebimento };
      })
      .sort((a, b) => String(b.data).localeCompare(String(a.data)));
  }

  function trabalhosAbertosNoPeriodo(state, year, month, pagador) {
    const prefix = `${String(year).padStart(4, "0")}-${String(month).padStart(2, "0")}`;
    let items = trabalhosComRecebido(state).filter(
      (t) => String(t.data).startsWith(prefix) && t.status_recebimento !== "pago"
    );
    if (pagador) {
      const key = pagador.toLowerCase();
      items = items.filter((t) => String(t.pagador || "").toLowerCase().includes(key));
    }
    return items;
  }

  function lensTotals(items, lente) {
    let ent = 0;
    let sai = 0;
    for (const i of items) {
      if (lente === "pessoal" && i.lente !== "pessoal") continue;
      if (lente === "profissional" && i.lente !== "profissional" && i.lente !== "misto") continue;
      if (lente === "misto" && i.lente !== "misto") continue;
      if (i.tipo === "entrada") ent += Number(i.valor) || 0;
      else sai += Number(i.valor) || 0;
    }
    return {
      entrou: Math.round(ent * 100) / 100,
      saiu: Math.round(sai * 100) / 100,
      saldo: Math.round((ent - sai) * 100) / 100,
    };
  }

  function summarize(state, year, month) {
    const [y, m] = monthBounds(year, month);
    const lancs = listLancamentos(state, y, m);
    const realizados = lancs.filter((l) => l.status === "realizado");
    const previstos = lancs.filter((l) => l.status === "previsto");

    const entrou = Math.round(
      realizados.filter((i) => i.tipo === "entrada").reduce((s, i) => s + Number(i.valor), 0) * 100
    ) / 100;
    const saiu = Math.round(
      realizados.filter((i) => i.tipo === "saida").reduce((s, i) => s + Number(i.valor), 0) * 100
    ) / 100;
    const sobrou_conta = Math.round((entrou - saiu) * 100) / 100;
    const a_pagar = Math.round(
      previstos.filter((i) => i.tipo === "saida").reduce((s, i) => s + Number(i.valor), 0) * 100
    ) / 100;

    const trabalhos = trabalhosComRecebido(state);
    const a_receber = Math.round(
      trabalhos.filter((t) => t.saldo_receber > 0).reduce((s, t) => s + t.saldo_receber, 0) * 100
    ) / 100;
    const abertos = trabalhos.filter((t) => t.status_recebimento !== "pago");

    const prof = lensTotals(realizados, "profissional");
    const reserva_imposto = Math.round(prof.entrou * 0.2 * 100) / 100;
    const sobrou_verdade = Math.round((sobrou_conta - a_pagar - reserva_imposto) * 100) / 100;

    return {
      ano: y,
      mes: m,
      entrou,
      saiu,
      sobrou_conta,
      a_pagar,
      a_receber,
      reserva_imposto_estimada: reserva_imposto,
      sobrou_verdade,
      por_lente: {
        pessoal: lensTotals(realizados, "pessoal"),
        profissional: prof,
      },
      lancamentos: lancs,
      trabalhos_abertos: abertos,
      previstos,
    };
  }

  function trabalhosView(state) {
    const items = trabalhosComRecebido(state);
    const pago = items.filter((t) => t.status_recebimento === "pago").length;
    const parcial = items.filter((t) => t.status_recebimento === "parcial").length;
    const aberto = items.filter((t) => t.status_recebimento === "aberto").length;
    const esperado = Math.round(items.reduce((s, t) => s + t.valor_esperado, 0) * 100) / 100;
    const recebido = Math.round(items.reduce((s, t) => s + t.valor_recebido, 0) * 100) / 100;
    return {
      trabalhos: items,
      totais: {
        quantidade: items.length,
        pago,
        parcial,
        aberto,
        esperado,
        recebido,
        em_aberto: Math.round((esperado - recebido) * 100) / 100,
      },
    };
  }

  function gastosPorPeriodo(state, meses = 6) {
    const t = today();
    const periods = [];
    const allSaidas = [];
    for (let offset = -(meses - 1); offset <= 0; offset++) {
      const [y, m] = shiftMonth(t.getFullYear(), t.getMonth() + 1, offset);
      const lancs = listLancamentos(state, y, m).filter(
        (l) => l.tipo === "saida" && l.status === "realizado"
      );
      allSaidas.push(...lancs);
      const pessoal = Math.round(
        lancs.filter((l) => l.lente === "pessoal").reduce((s, l) => s + Number(l.valor), 0) * 100
      ) / 100;
      const profissional = Math.round(
        lancs
          .filter((l) => l.lente === "profissional" || l.lente === "misto")
          .reduce((s, l) => s + Number(l.valor), 0) * 100
      ) / 100;
      const total = Math.round((pessoal + profissional) * 100) / 100;
      periods.push({
        ano: y,
        mes: m,
        label: `${MONTH_LABELS[m]}/${String(y).slice(2)}`,
        total,
        pessoal,
        profissional,
      });
    }
    const byCat = {};
    const byLente = {};
    for (const l of allSaidas) {
      byCat[l.categoria] = (byCat[l.categoria] || 0) + Number(l.valor);
      byLente[l.lente] = (byLente[l.lente] || 0) + Number(l.valor);
    }
    const categorias = Object.entries(byCat)
      .map(([categoria, total]) => ({ categoria, total: Math.round(total * 100) / 100 }))
      .sort((a, b) => b.total - a.total);
    const max_mes = Math.max(...periods.map((p) => p.total), 0) || 1;
    return {
      meses,
      periodos: periods,
      max_mes,
      categorias,
      por_lente: Object.fromEntries(
        Object.entries(byLente).map(([k, v]) => [k, Math.round(v * 100) / 100])
      ),
      total_periodo: Math.round(periods.reduce((s, p) => s + p.total, 0) * 100) / 100,
    };
  }

  global.MonitorSummary = {
    summarize,
    trabalhosView,
    gastosPorPeriodo,
    trabalhosComRecebido,
    trabalhosAbertosNoPeriodo,
    listLancamentos,
  };
})(window);
