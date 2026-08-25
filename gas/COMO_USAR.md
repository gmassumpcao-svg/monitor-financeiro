# Como usar o Monitor no Apps Script

## 1. Cole os arquivos no Apps Script

No editor do Apps Script, cole **TODOS** os arquivos HTML + `Code.gs`.

Use **Arquivo > Novo > Arquivo HTML** com estes nomes exatos:

- `Index`
- `Styles`
- `ApiJs`
- `SummaryJs`
- `AgentJs`
- `AppJs`

E mantenha/atualize o `Code.gs`.

## 2. Propriedades do script

Configure as propriedades do script:

- `SPREADSHEET_ID` — ID da planilha do Google Sheets
- `API_TOKEN` — token da API (mesmo valor usado pelo backend)

## 3. Rodar `setupSheets`

No editor, execute a função `setupSheets` uma vez para preparar as abas/estrutura na planilha.

## 4. Nova implantação (App da Web)

1. **Implantar > Nova implantação**
2. Tipo: **App da Web**
3. **Executar como:** Eu
4. **Quem tem acesso:** "Qualquer pessoa com Conta do Google" **OU** "Só eu"

## 5. Abrir no celular

- Abra a URL `/exec` no celular **logado na Conta do Google**
- **NÃO** use GitHub Pages para conectar a API neste modo
- Favoritar a URL no celular para acesso rápido
