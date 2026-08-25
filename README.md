# Monitor Financeiro

Controle de caixa, trabalhos médicos (plantões/consultas) e gastos — com chat por regras e confirmação antes de gravar.

Há **duas formas** de usar:

| Modo | Onde roda | Dados | Celular |
|------|-----------|-------|---------|
| **Local (Python)** | Mac com uvicorn | SQLite em `data/` | Só na mesma rede se `--host 0.0.0.0` |
| **Estático + Sheets** | GitHub Pages | Google Sheets | Sim, pela URL pública |

---

## Modo recomendado para o celular: GitHub Pages + Google Sheets

### 1. Criar a planilha e o Apps Script

1. Crie uma [planilha Google](https://sheets.google.com) vazia.
2. Copie o **ID** da URL: `https://docs.google.com/spreadsheets/d/`**`ID_AQUI`**`/edit`
3. Em **Extensões → Apps Script**, apague o código padrão e cole o conteúdo de [`gas/Code.gs`](gas/Code.gs).
4. Em **Projeto → Configurações → Propriedades do script**, adicione:
   - `SPREADSHEET_ID` = o ID da planilha
   - `API_TOKEN` = um segredo longo (ex.: `openssl rand -hex 24` no Terminal)
5. Selecione a função `setupSheets` e clique em **Executar** (autorize a conta Google).
6. **Implantar → Nova implantação → Tipo: App da Web**
   - Executar como: **Eu**
   - Quem tem acesso: **Qualquer pessoa**
7. Copie a URL que termina em `/exec`.

### 2. Configurar o site

1. Publique este repositório no GitHub.
2. Em **Settings → Pages**:
   - Source: **Deploy from a branch**
   - Branch: `main` (ou `master`), pasta **`/docs`**
3. Abra a URL do Pages (ex.: `https://SEU_USER.github.io/monitor-financeiro/`).
4. Na primeira visita, cole a **URL `/exec`** e o **API_TOKEN** (salvos só no navegador via `localStorage`).
5. Use **+ Ganho / + Gasto / + Trabalho** ou o chat (`Recebi 4200 de plantão` → **sim**).

Arquivos do site: pasta [`docs/`](docs/).  
Exemplo de config (sem segredos): [`docs/js/config.example.js`](docs/js/config.example.js).

> **Segurança:** o token no browser protege contra uso casual da URL do script, mas não é autenticação forte. Use repositório **privado** se possível e não compartilhe o token. É uma ferramenta pessoal (1 médico / 1 planilha).

### 3. Testar no celular

Abra a mesma URL do GitHub Pages no Safari/Chrome do celular (qualquer rede, com internet).

---

## Modo local (Python / FastAPI)

```bash
cd "/Users/gabrielassumpcao/Desktop/monitor-financeiro"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Abra http://127.0.0.1:8000 — UI em `static/` falando com a API Python e SQLite.

---

## Estrutura

```
app/           # API FastAPI + agente Python + SQLite
static/        # UI do modo local
docs/          # Site estático (GitHub Pages) + agente JS
gas/           # Google Apps Script (API sobre Sheets)
data/          # SQLite local (modo Python)
```
