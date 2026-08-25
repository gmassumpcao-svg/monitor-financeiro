# Como o médico usa o Monitor (você NÃO precisa ser o usuário)

A planilha e o Apps Script ficam **na sua conta Google** (você é o “dono” técnico).  
O **médico** usa no celular com a **conta Google dele**.

```text
Você (dono)          Médico (usuário)
cria planilha   →    abre /exec no celular
implanta script →    logado no Gmail DELE
guarda dados    ←    lança gastos / plantões
```

## 1. Arquivos no Apps Script

Cole **Code.gs** + HTMLs com estes nomes:

`Index` · `Styles` · `ApiJs` · `SummaryJs` · `AgentJs` · `AppJs`

## 2. Propriedades do script

| Chave | Valor |
|-------|--------|
| `SPREADSHEET_ID` | ID da planilha |
| `API_TOKEN` | segredo qualquer (ex. `openssl rand -hex 24`) |
| `ALLOWED_EMAILS` | e-mail Google do médico, ex. `medico@gmail.com` (opcional, recomendado) |

## 3. `setupSheets` uma vez

## 4. Implantação (importante)

1. **Implantar → Nova implantação → App da Web**
2. **Executar como:** **Eu** (sua conta — grava na sua planilha)
3. **Quem tem acesso:** **Qualquer pessoa com Conta do Google**  
   (não use “Só eu”, senão só você abre)
4. Copie a URL que termina em `/exec`

## 5. O que enviar para o médico

1. A URL `/exec`
2. Pedido: “Entre no Gmail **seu** e abra este link; favorite na tela inicial”

Ele **não** precisa do GitHub Pages nem do `API_TOKEN`.

## Por que o GitHub Pages dá Failed to fetch?

Porque o script está pedindo login Google. Para o médico, o caminho certo é a **URL `/exec`**, não o Pages.

## Se quiser Pages público depois

Aí a implantação precisa ser **Qualquer pessoa** (anônimo). Só faça isso se aceitar o risco de quem tiver URL+token gravar na planilha.
