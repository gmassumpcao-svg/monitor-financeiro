# Deploy checklist

## Apps Script (obrigatório)

1. Cole `gas/Code.gs` + `gas/Index.html` **completo** (gere com `python3 gas/build_index.py`).
2. Propriedades: `SPREADSHEET_ID`, `API_TOKEN` (+ `ALLOWED_EMAILS` opcional).
3. Rode `setupSheets()` uma vez.
4. Implantar → App da Web → **Nova versão** (sempre nova versão após colar HTML).
5. Detalhes dos dois modos: [`gas/COMO_USAR.md`](../gas/COMO_USAR.md).

## GitHub Pages (opcional — Modo B)

1. Push em `main`.
2. Settings → Pages → Branch `main` / folder `/docs`.
3. App da Web com acesso **Qualquer pessoa** (anônimo).
4. No site: cole URL `/exec` + `API_TOKEN` (botão Testar URL).

Arquivo `.nojekyll` nesta pasta evita processamento Jekyll.
