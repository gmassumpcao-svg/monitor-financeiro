# Google Apps Script — backend da planilha

Arquivos: [`Code.gs`](Code.gs) + [`Index.html`](Index.html) (UI completa embutida).

Regenere o Index a partir de `docs/` com:

```bash
python3 gas/build_index.py
```

Não precisa de HTMLs separados (`Styles`, `ApiJs`, etc.).

Guia completo (Modo A `/exec` + Modo B Pages): [`COMO_USAR.md`](COMO_USAR.md).

## Propriedades do script

| Chave | Valor |
|-------|--------|
| `SPREADSHEET_ID` | ID da planilha (URL `/d/ID/edit`) |
| `API_TOKEN` | Segredo (obrigatório) |
| `ALLOWED_EMAILS` | Opcional — e-mails Google autorizados no Modo A |

## Funções

- `setupSheets()` — cria abas `lancamentos`, `trabalhos`, `vinculos`, `meta`
- `apiCall(req)` — chamado pelo app embutido (`google.script.run`); injeta o token
- Web App `doGet` / `doPost` — HTML do app ou API JSON/JSONP

## Implantação

- **Modo A (celular):** Executar como **Eu** → acesso **Qualquer pessoa com Conta do Google** → abrir `/exec`
- **Modo B (Pages):** acesso **Qualquer pessoa** (anônimo) → colar `/exec` + token no overlay do site

A planilha pode ficar **privada** nos dois modos.
