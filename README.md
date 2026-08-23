# Monitor Financeiro

Agente pessoal da vida financeira do médico (casa + trabalho). Recorte da v1 em [`v1.md`](v1.md).

## Rodar local

```bash
cd "Projetos Pessoais IA/monitor-financeiro"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Abra http://127.0.0.1:8000

Visões na interface:
- **Caixa** — entrou / saiu / sobrou
- **Trabalhos realizados** — lista com status de pagamento
- **Gastos por período** — últimos 6 meses (pessoal vs profissional) + categorias

Dados ficam em `data/monitor.db` (SQLite). Sem API de IA na v1 — o agente usa regras em português. Sem custo por mensagem.

## Fluxo da primeira semana

1. `sou eu, começo agora`
2. `Recebi 4200 de plantão` → **sim**
3. `Paguei 2500 de aluguel de casa` → **sim**
4. `Fiz plantão dia 10/06 no Hospital X, Unimed, 1800` → **sim**
5. `Caiu 1800 da Unimed referente a junho` → **sim**
6. `Como foi o mês?`
