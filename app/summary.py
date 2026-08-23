"""Monthly cash and “sobrou de verdade” summary."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Optional

from . import db

MONTH_LABELS = [
    "",
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def month_bounds(year: Optional[int] = None, month: Optional[int] = None) -> tuple[int, int]:
    today = date.today()
    return year or today.year, month or today.month


def _shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    idx = year * 12 + (month - 1) + delta
    return idx // 12, idx % 12 + 1


def gastos_por_periodo(meses: int = 6) -> dict[str, Any]:
    """Aggregate realized expenses by month and category for the last N months."""
    today = date.today()
    periods: list[dict[str, Any]] = []
    all_saidas: list[dict[str, Any]] = []

    for offset in range(-(meses - 1), 1):
        y, m = _shift_month(today.year, today.month, offset)
        lancs = [
            l
            for l in db.list_lancamentos(y, m)
            if l["tipo"] == "saida" and l["status"] == "realizado"
        ]
        all_saidas.extend(lancs)
        pessoal = round(sum(l["valor"] for l in lancs if l["lente"] == "pessoal"), 2)
        profissional = round(
            sum(l["valor"] for l in lancs if l["lente"] in ("profissional", "misto")), 2
        )
        total = round(pessoal + profissional, 2)
        periods.append(
            {
                "ano": y,
                "mes": m,
                "label": f"{MONTH_LABELS[m]}/{str(y)[2:]}",
                "total": total,
                "pessoal": pessoal,
                "profissional": profissional,
            }
        )

    by_cat: dict[str, float] = defaultdict(float)
    by_lente: dict[str, float] = defaultdict(float)
    for l in all_saidas:
        by_cat[l["categoria"]] += l["valor"]
        by_lente[l["lente"]] += l["valor"]

    categorias = [
        {"categoria": k, "total": round(v, 2)}
        for k, v in sorted(by_cat.items(), key=lambda x: -x[1])
    ]
    max_mes = max((p["total"] for p in periods), default=0) or 1

    return {
        "meses": meses,
        "periodos": periods,
        "max_mes": max_mes,
        "categorias": categorias,
        "por_lente": {k: round(v, 2) for k, v in by_lente.items()},
        "total_periodo": round(sum(p["total"] for p in periods), 2),
    }


def trabalhos_view() -> dict[str, Any]:
    items = db.trabalhos_com_recebido()
    pago = sum(1 for t in items if t["status_recebimento"] == "pago")
    parcial = sum(1 for t in items if t["status_recebimento"] == "parcial")
    aberto = sum(1 for t in items if t["status_recebimento"] == "aberto")
    esperado = round(sum(t["valor_esperado"] for t in items), 2)
    recebido = round(sum(t["valor_recebido"] for t in items), 2)
    return {
        "trabalhos": items,
        "totais": {
            "quantidade": len(items),
            "pago": pago,
            "parcial": parcial,
            "aberto": aberto,
            "esperado": esperado,
            "recebido": recebido,
            "em_aberto": round(esperado - recebido, 2),
        },
    }


def summarize(year: Optional[int] = None, month: Optional[int] = None) -> dict[str, Any]:
    y, m = month_bounds(year, month)
    lancs = db.list_lancamentos(y, m)
    realizados = [l for l in lancs if l["status"] == "realizado"]
    previstos = [l for l in lancs if l["status"] == "previsto"]

    def total(items: list[dict], tipo: str, lente: Optional[str] = None) -> float:
        s = 0.0
        for i in items:
            if i["tipo"] != tipo:
                continue
            if lente and i["lente"] != lente and not (lente == "profissional" and i["lente"] == "misto"):
                # For lens filter: exact match; "total" ignores lens
                if lente == "pessoal" and i["lente"] != "pessoal":
                    continue
                if lente == "profissional" and i["lente"] not in ("profissional", "misto"):
                    continue
            if lente is None:
                pass
            s += i["valor"]
        return round(s, 2)

    def lens_totals(items: list[dict], lente: str) -> dict[str, float]:
        ent = 0.0
        sai = 0.0
        for i in items:
            if lente == "pessoal" and i["lente"] != "pessoal":
                continue
            if lente == "profissional" and i["lente"] not in ("profissional", "misto"):
                continue
            if lente == "misto" and i["lente"] != "misto":
                continue
            if i["tipo"] == "entrada":
                ent += i["valor"]
            else:
                sai += i["valor"]
        return {
            "entrou": round(ent, 2),
            "saiu": round(sai, 2),
            "saldo": round(ent - sai, 2),
        }

    entrou = round(sum(i["valor"] for i in realizados if i["tipo"] == "entrada"), 2)
    saiu = round(sum(i["valor"] for i in realizados if i["tipo"] == "saida"), 2)
    sobrou_conta = round(entrou - saiu, 2)

    a_pagar = round(sum(i["valor"] for i in previstos if i["tipo"] == "saida"), 2)
    # Also include unpaid future-looking previsto entradas? skip for v1

    trabalhos = db.trabalhos_com_recebido()
    a_receber = round(sum(t["saldo_receber"] for t in trabalhos if t["saldo_receber"] > 0), 2)
    abertos = [t for t in trabalhos if t["status_recebimento"] != "pago"]

    # Reserva simples: 20% dos ganhos profissionais realizados do mês (heurística v1)
    prof = lens_totals(realizados, "profissional")
    reserva_imposto = round(prof["entrou"] * 0.20, 2)
    sobrou_verdade = round(sobrou_conta - a_pagar - reserva_imposto, 2)

    return {
        "ano": y,
        "mes": m,
        "entrou": entrou,
        "saiu": saiu,
        "sobrou_conta": sobrou_conta,
        "a_pagar": a_pagar,
        "a_receber": a_receber,
        "reserva_imposto_estimada": reserva_imposto,
        "sobrou_verdade": sobrou_verdade,
        "por_lente": {
            "pessoal": lens_totals(realizados, "pessoal"),
            "profissional": lens_totals(realizados, "profissional"),
        },
        "lancamentos": lancs,
        "trabalhos_abertos": abertos,
        "previstos": previstos,
    }
