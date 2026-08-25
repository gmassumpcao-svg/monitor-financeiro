# Google Apps Script — backend da planilha

Arquivo principal: [`Code.gs`](Code.gs)

## Propriedades do script

| Chave | Valor |
|-------|--------|
| `SPREADSHEET_ID` | ID da planilha (URL `/d/ID/edit`) |
| `API_TOKEN` | Segredo compartilhado com o site |

## Funções

- `setupSheets()` — cria abas `lancamentos`, `trabalhos`, `vinculos`, `meta`
- Web App `doGet` / `doPost` — API JSON

## Ações da API

Corpo POST (`Content-Type: text/plain`) com JSON:

```json
{ "token": "...", "action": "getAll" }
```

Ações: `setup`, `getAll`, `addLancamento`, `addTrabalho`, `addVinculo`, `setPending`, `setOnboarding`, `applyPagamentoVinculado`.

## Implantação

Implantar → App da Web → Executar como **Eu** → Acesso **Qualquer pessoa** → copiar URL `/exec` para o site em `docs/`.
