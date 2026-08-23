"""Rule-based Portuguese agent for Monitor Financeiro v1.

Understands common phrases for the first-week flow and always confirms
before writing (via pending payload), except explicit sim/não.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Optional

from . import db
from . import summary as summary_mod

MONTHS = {
    "janeiro": 1,
    "jan": 1,
    "fevereiro": 2,
    "fev": 2,
    "marco": 3,
    "março": 3,
    "mar": 3,
    "abril": 4,
    "abr": 4,
    "maio": 5,
    "mai": 5,
    "junho": 6,
    "jun": 6,
    "julho": 7,
    "jul": 7,
    "agosto": 8,
    "ago": 8,
    "setembro": 9,
    "set": 9,
    "outubro": 10,
    "out": 10,
    "novembro": 11,
    "nov": 11,
    "dezembro": 12,
    "dez": 12,
}

PROF_INCOME_CATS = {
    "plantao": "plantao",
    "plantão": "plantao",
    "convenio": "convenio",
    "convênio": "convenio",
    "unimed": "convenio",
    "bradesco": "convenio",
    "sulamerica": "convenio",
    "sulamérica": "convenio",
    "particular": "honorario_particular",
    "honorario": "honorario_particular",
    "honorário": "honorario_particular",
}

PROF_EXPENSE_CATS = {
    "sala": "aluguel_sala",
    "aluguel de sala": "aluguel_sala",
    "material": "material",
    "contador": "pessoal_contador",
    "crm": "conselho_seguro",
    "das": "imposto",
    "imposto": "imposto",
}

PERS_EXPENSE_CATS = {
    "casa": "moradia",
    "aluguel": "moradia",
    "moradia": "moradia",
    "escola": "familia_escola",
    "familia": "familia_escola",
    "família": "familia_escola",
    "mercado": "alimentacao",
    "alimentação": "alimentacao",
    "alimentacao": "alimentacao",
    "comida": "alimentacao",
    "uber": "transporte",
    "carro": "transporte",
    "lazer": "lazer",
}


def _parse_amount_token(raw: str) -> Optional[float]:
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _money(text: str) -> Optional[float]:
    """Extract BRL amount, ignoring day/month fragments like 10/06."""
    cleaned = re.sub(r"\b\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?\b", " ", text)
    cleaned = re.sub(r"\b\d{1,2}[\/\-]\d{4}\b", " ", cleaned)

    explicit = re.findall(r"r\$\s*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+(?:[.,]\d{1,2})?)", cleaned, re.I)
    if explicit:
        return _parse_amount_token(explicit[-1])

    candidates = re.findall(
        r"(\d{1,3}(?:\.\d{3})*,\d{2}|\d{2,}(?:[.,]\d{1,2})?)",
        cleaned,
    )
    # Prefer the last plausible money token (skips lone 1-digit leftovers)
    for raw in reversed(candidates):
        val = _parse_amount_token(raw)
        if val is not None and val >= 1:
            return val
    return None


def _parse_date(text: str, default: Optional[date] = None) -> str:
    default = default or date.today()
    m = re.search(r"\b(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?\b", text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), m.group(3)
        year = default.year
        if y:
            year = int(y)
            if year < 100:
                year += 2000
        try:
            return date(year, mo, d).isoformat()
        except ValueError:
            pass
    return default.isoformat()


def _month_year(text: str) -> Optional[tuple[int, int]]:
    today = date.today()
    text_n = text.casefold()
    for name, mo in MONTHS.items():
        if re.search(rf"\b{re.escape(name)}\b", text_n):
            ym = re.search(rf"\b{re.escape(name)}\s+(?:de\s+)?(\d{{4}})\b", text_n)
            year = int(ym.group(1)) if ym else today.year
            # If month is ahead of current and no year, maybe previous year for "referente a"
            if not ym and mo > today.month and "referente" in text_n:
                year = today.year - 1
            return year, mo
    m = re.search(r"\b(\d{1,2})[\/\-](\d{4})\b", text)
    if m:
        return int(m.group(2)), int(m.group(1))
    if "este mês" in text_n or "esse mês" in text_n or "este mes" in text_n:
        return today.year, today.month
    if "mês passado" in text_n or "mes passado" in text_n:
        if today.month == 1:
            return today.year - 1, 12
        return today.year, today.month - 1
    return None


def _brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_trabalho(t: dict[str, Any]) -> str:
    bits = [t["data"], t["tipo"]]
    if t.get("local"):
        bits.append(t["local"])
    if t.get("pagador"):
        bits.append(t["pagador"])
    bits.append(f"esperado {_brl(t['valor_esperado'])}")
    bits.append(f"em aberto {_brl(t['saldo_receber'])}")
    return " · ".join(bits)


def handle(message: str) -> dict[str, Any]:
    text = (message or "").strip()
    if not text:
        return {
            "reply": "Pode falar — lançamento, trabalho feito, pagamento de convênio ou “como foi o mês?”.",
            "pending": db.get_pending(),
            "summary": summary_mod.summarize(),
        }

    low = text.casefold()
    pending = db.get_pending()

    # Confirm / cancel pending
    if pending and re.fullmatch(r"(sim|s|confirmo|confirma|ok|pode|pode gravar|isso)", low):
        return _apply_pending(pending)
    if pending and re.fullmatch(r"(não|nao|n|cancela|cancelar)", low):
        db.set_pending(None)
        return {
            "reply": "Ok, não gravei nada. Pode reformular.",
            "pending": None,
            "summary": summary_mod.summarize(),
        }

    # Onboarding
    if re.search(r"\b(sou eu|começo agora|comeco agora|olá|ola|oi)\b", low) or low in (
        "começar",
        "comecar",
        "start",
    ):
        profile = db.set_onboarding()
        return {
            "reply": (
                f"Olá. Sou o Monitor Financeiro — seu controle da vida (casa + trabalho).\n\n"
                f"Pode me dizer, por exemplo:\n"
                f"• “Recebi 4200 de plantão”\n"
                f"• “Paguei 2500 de aluguel de casa”\n"
                f"• “Fiz plantão dia 10/06 no Hospital X, Unimed, 1800”\n"
                f"• “Caiu 3600 da Unimed referente a junho”\n"
                f"• “Como foi o mês?”\n\n"
                f"Eu sempre peço confirmação antes de gravar."
            ),
            "pending": None,
            "summary": summary_mod.summarize(),
            "profile": profile,
        }

    # Month summary
    if re.search(r"como foi|resumo|caixa|sobrou|balanço|balanco", low):
        my = _month_year(low) or (date.today().year, date.today().month)
        s = summary_mod.summarize(my[0], my[1])
        reply = (
            f"**{s['mes']:02d}/{s['ano']}**\n"
            f"Entrou {_brl(s['entrou'])} · Saiu {_brl(s['saiu'])}\n"
            f"**Sobrou na conta:** {_brl(s['sobrou_conta'])}\n"
            f"A pagar (previsto): {_brl(s['a_pagar'])}\n"
            f"Reserva imposto (est. 20% prof.): {_brl(s['reserva_imposto_estimada'])}\n"
            f"**Sobrou de verdade:** {_brl(s['sobrou_verdade'])}\n\n"
            f"Pessoal → saldo {_brl(s['por_lente']['pessoal']['saldo'])}\n"
            f"Profissional → saldo {_brl(s['por_lente']['profissional']['saldo'])}"
        )
        return {"reply": reply, "pending": pending, "summary": s}

    if re.search(r"a receber|receber|em aberto|o que ainda", low) and "pagar" not in low:
        s = summary_mod.summarize()
        abertos = s["trabalhos_abertos"]
        if not abertos:
            reply = "Nada a receber no momento — todos os trabalhos estão quitados ou ainda não há trabalhos."
        else:
            lines = [f"• {_fmt_trabalho(t)}" for t in abertos[:12]]
            reply = f"**A receber:** {_brl(s['a_receber'])}\n" + "\n".join(lines)
        return {"reply": reply, "pending": pending, "summary": s}

    if re.search(r"a pagar|contas a pagar|vai sair", low):
        s = summary_mod.summarize()
        prev = [l for l in s["previstos"] if l["tipo"] == "saida"]
        if not prev:
            reply = f"**A pagar (previsto):** {_brl(s['a_pagar'])} — nenhuma conta prevista cadastrada."
        else:
            lines = [
                f"• {l['data_caixa']} · {l['categoria']} · {l['lente']} · {_brl(l['valor'])}"
                for l in prev
            ]
            reply = f"**A pagar:** {_brl(s['a_pagar'])}\n" + "\n".join(lines)
        return {"reply": reply, "pending": pending, "summary": s}

    # Convenio payment linking — core of v1
    if re.search(r"\b(caiu|recebi da|recebimento da|pagamento da|pagou a)\b", low) or (
        re.search(r"\breferente a\b", low) and _money(low)
    ):
        return _propose_vinculo(text, low)

    # Cash movements before "trabalho" (avoids “Recebi … plantão” becoming a shift)
    if re.search(r"\b(recebi|entrou|ganhei)\b", low):
        return _propose_lancamento(text, low, tipo="entrada")
    if re.search(r"\b(paguei|gastei|saí|saiu|despesa)\b", low):
        return _propose_lancamento(text, low, tipo="saida")

    # Work done (explicit verbs / “fiz …”)
    if re.search(r"\b(fiz|atendi|plantei)\b", low) or re.search(
        r"\b(registrar|cadastre|cadastrar)\s+(plantão|plantao|consulta|procedimento)\b", low
    ):
        return _propose_trabalho(text, low)

    if pending:
        return {
            "reply": (
                "Ainda tenho uma ação esperando confirmação. Responda **sim** ou **não**.\n"
                f"Pendente: {pending.get('label', pending.get('action'))}"
            ),
            "pending": pending,
            "summary": summary_mod.summarize(),
        }

    return {
        "reply": (
            "Não entendi com segurança. Exemplos:\n"
            "• Recebi 3000 de particular\n"
            "• Paguei 1800 de escola\n"
            "• Fiz plantão dia 05/06 no Hospital Y, Unimed, 2000\n"
            "• Caiu 4000 da Unimed referente a junho\n"
            "• Como foi o mês?"
        ),
        "pending": None,
        "summary": summary_mod.summarize(),
    }


def _guess_lente_categoria(low: str, tipo: str) -> tuple[str, str]:
    if tipo == "entrada":
        for k, cat in PROF_INCOME_CATS.items():
            if k in low:
                return "profissional", cat
        return "profissional", "outros_ganhos"

    for k, cat in PERS_EXPENSE_CATS.items():
        if k in low:
            # "aluguel de sala" is professional
            if "sala" in low:
                return "profissional", "aluguel_sala"
            return "pessoal", cat
    for k, cat in PROF_EXPENSE_CATS.items():
        if k in low:
            return "profissional", cat
    if "sala" in low or "crm" in low or "das" in low or "consultório" in low or "consultorio" in low:
        return "profissional", "outros"
    if "casa" in low or "escola" in low or "mercado" in low:
        return "pessoal", "outros"
    return "pessoal", "outros"  # ask via confirmation note


def _propose_lancamento(text: str, low: str, tipo: str) -> dict[str, Any]:
    valor = _money(text)
    if valor is None:
        return {
            "reply": "Não achei o valor. Ex.: “Recebi 4200 de plantão”.",
            "pending": db.get_pending(),
            "summary": summary_mod.summarize(),
        }
    lente, categoria = _guess_lente_categoria(low, tipo)
    data_caixa = _parse_date(text)
    status = "previsto" if re.search(r"\b(vou pagar|a pagar|previsto|vai sair)\b", low) else "realizado"
    pagador = None
    for name in ("unimed", "bradesco", "sulamerica", "sulamérica", "particular"):
        if name in low:
            pagador = name.capitalize() if name != "sulamérica" else "SulAmérica"
            if name == "unimed":
                pagador = "Unimed"
            break

    action = {
        "action": "create_lancamento",
        "label": f"{'Entrada' if tipo == 'entrada' else 'Saída'} {_brl(valor)} · {lente} · {categoria}",
        "payload": {
            "tipo": tipo,
            "valor": valor,
            "data_caixa": data_caixa,
            "lente": lente,
            "categoria": categoria,
            "status": status,
            "nota": text,
            "pagador": pagador,
        },
    }
    db.set_pending(action)
    ask_lente = ""
    if tipo == "saida" and lente == "pessoal" and not any(k in low for k in PERS_EXPENSE_CATS):
        ask_lente = "\n(Assumi **pessoal**. Se for profissional, cancele e diga “paguei … de sala/CRM/DAS”.)"
    return {
        "reply": (
            f"Posso gravar?\n"
            f"• Tipo: {'entrada' if tipo == 'entrada' else 'saída'}\n"
            f"• Valor: {_brl(valor)}\n"
            f"• Data: {data_caixa}\n"
            f"• Lente: {lente}\n"
            f"• Categoria: {categoria}\n"
            f"• Status: {status}\n"
            f"Responda **sim** ou **não**."
            f"{ask_lente}"
        ),
        "pending": action,
        "summary": summary_mod.summarize(),
    }


def _propose_trabalho(text: str, low: str) -> dict[str, Any]:
    valor = _money(text)
    if valor is None:
        return {
            "reply": "Para registrar o trabalho, preciso do valor esperado. Ex.: “Fiz plantão dia 10/06 no Hospital X, Unimed, 1800”.",
            "pending": db.get_pending(),
            "summary": summary_mod.summarize(),
        }
    if "consulta" in low:
        tipo = "consulta"
    elif "procedimento" in low:
        tipo = "procedimento"
    elif "plant" in low:
        tipo = "plantao"
    else:
        tipo = "outro"

    data_t = _parse_date(text)
    local = None
    m_loc = re.search(r"\bno\s+([^,]+?)(?:,|\s+unimed|\s+bradesco|\s+\d|$)", low)
    if m_loc:
        local = m_loc.group(1).strip().title()

    pagador = None
    for name in ("unimed", "bradesco", "sulamerica", "sulamérica", "particular", "hospital"):
        if name in low:
            pagador = {
                "unimed": "Unimed",
                "bradesco": "Bradesco",
                "sulamerica": "SulAmérica",
                "sulamérica": "SulAmérica",
                "particular": "Particular",
                "hospital": "Hospital",
            }[name]
            break

    action = {
        "action": "create_trabalho",
        "label": f"Trabalho {tipo} {data_t} {_brl(valor)}",
        "payload": {
            "data": data_t,
            "tipo": tipo,
            "local": local,
            "pagador": pagador,
            "valor_esperado": valor,
            "nota": text,
        },
    }
    db.set_pending(action)
    return {
        "reply": (
            f"Registrar trabalho feito?\n"
            f"• Data: {data_t}\n"
            f"• Tipo: {tipo}\n"
            f"• Local: {local or '—'}\n"
            f"• Pagador: {pagador or '—'}\n"
            f"• Valor esperado: {_brl(valor)}\n"
            f"Responda **sim** ou **não**."
        ),
        "pending": action,
        "summary": summary_mod.summarize(),
    }


def _propose_vinculo(text: str, low: str) -> dict[str, Any]:
    valor = _money(text)
    if valor is None:
        return {
            "reply": "Não achei o valor que caiu. Ex.: “Caiu 3600 da Unimed referente a junho”.",
            "pending": db.get_pending(),
            "summary": summary_mod.summarize(),
        }

    pagador = None
    for name, label in (
        ("unimed", "Unimed"),
        ("bradesco", "Bradesco"),
        ("sulamérica", "SulAmérica"),
        ("sulamerica", "SulAmérica"),
    ):
        if name in low:
            pagador = label
            break

    my = _month_year(low)
    if not my:
        return {
            "reply": "De qual mês é esse pagamento? Ex.: “referente a junho” ou “referente a 06/2026”.",
            "pending": db.get_pending(),
            "summary": summary_mod.summarize(),
        }

    year, month = my
    candidatos = db.trabalhos_abertos_no_periodo(year, month, pagador=pagador)
    if not candidatos:
        # broaden without pagador filter
        candidatos = db.trabalhos_abertos_no_periodo(year, month, pagador=None)
        if not candidatos:
            return {
                "reply": (
                    f"Não achei trabalhos em aberto em {month:02d}/{year}"
                    f"{f' para {pagador}' if pagador else ''}. "
                    f"Cadastre o trabalho primeiro (“Fiz plantão…”) e tente de novo. "
                    f"Não invento trabalho para fechar o valor."
                ),
                "pending": None,
                "summary": summary_mod.summarize(),
            }

    # Allocate payment across open works (oldest first)
    restante = valor
    alocacoes: list[dict[str, Any]] = []
    for t in sorted(candidatos, key=lambda x: x["data"]):
        if restante <= 0.009:
            break
        usa = min(t["saldo_receber"], restante)
        alocacoes.append({"trabalho_id": t["id"], "valor": round(usa, 2), "resumo": _fmt_trabalho(t)})
        restante = round(restante - usa, 2)

    data_caixa = _parse_date(text)
    action = {
        "action": "create_pagamento_vinculado",
        "label": f"Pagamento {_brl(valor)} → {len(alocacoes)} trabalho(s)",
        "payload": {
            "valor": valor,
            "data_caixa": data_caixa,
            "data_competencia": f"{year:04d}-{month:02d}-01",
            "pagador": pagador or "Convênio",
            "categoria": "convenio",
            "lente": "profissional",
            "nota": text,
            "alocacoes": alocacoes,
            "sobra": restante,
        },
    }
    db.set_pending(action)
    lines = [f"• {_brl(a['valor'])} → {a['resumo']}" for a in alocacoes]
    sobra_msg = ""
    if restante > 0.009:
        sobra_msg = (
            f"\n\nSobra {_brl(restante)} sem trabalho correspondente "
            f"(glosa inversa / outro período?). O lançamento entra mesmo assim; a sobra fica sem vínculo."
        )
    total_alocado = round(valor - restante, 2)
    esperado = round(sum(t["saldo_receber"] for t in candidatos), 2)
    diff_msg = ""
    if abs(valor - esperado) > 0.009 and restante <= 0.009 and total_alocado < esperado:
        diff_msg = f"\n(Pagamento parcial: em aberto no período era {_brl(esperado)}.)"
    elif valor + 0.009 < esperado and restante <= 0.009:
        diff_msg = f"\n(Em aberto no período: {_brl(esperado)}. Isto quita só parte.)"

    return {
        "reply": (
            f"Sugestão de vínculo para {_brl(valor)}"
            f"{f' da {pagador}' if pagador else ''} referente a {month:02d}/{year}:\n"
            + "\n".join(lines)
            + sobra_msg
            + diff_msg
            + "\n\nGravo o recebimento profissional e esses vínculos? **sim** / **não**."
        ),
        "pending": action,
        "summary": summary_mod.summarize(),
    }


def _apply_pending(pending: dict[str, Any]) -> dict[str, Any]:
    action = pending.get("action")
    payload = pending.get("payload") or {}

    if action == "create_lancamento":
        item = db.add_lancamento(**payload)
        db.set_pending(None)
        return {
            "reply": f"Gravado: {pending.get('label')} (id {item['id']}).",
            "pending": None,
            "summary": summary_mod.summarize(),
        }

    if action == "create_trabalho":
        item = db.add_trabalho(**payload)
        db.set_pending(None)
        return {
            "reply": f"Trabalho registrado (id {item['id']}). Ele entra em **a receber** até vincular um pagamento.",
            "pending": None,
            "summary": summary_mod.summarize(),
        }

    if action == "create_pagamento_vinculado":
        lanc = db.add_lancamento(
            tipo="entrada",
            valor=payload["valor"],
            data_caixa=payload["data_caixa"],
            data_competencia=payload.get("data_competencia"),
            lente="profissional",
            categoria=payload.get("categoria") or "convenio",
            status="realizado",
            nota=payload.get("nota"),
            pagador=payload.get("pagador"),
        )
        for a in payload.get("alocacoes") or []:
            db.add_vinculo(lanc["id"], a["trabalho_id"], a["valor"])
        db.set_pending(None)
        n = len(payload.get("alocacoes") or [])
        sobra = payload.get("sobra") or 0
        extra = f" Sobra sem vínculo: {_brl(sobra)}." if sobra > 0.009 else ""
        return {
            "reply": f"Recebimento gravado e vinculado a {n} trabalho(s).{extra}",
            "pending": None,
            "summary": summary_mod.summarize(),
        }

    db.set_pending(None)
    return {
        "reply": "Não consegui aplicar essa confirmação. Tente de novo.",
        "pending": None,
        "summary": summary_mod.summarize(),
    }
