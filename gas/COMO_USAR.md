# Duas formas de usar (médico no celular)

A planilha fica **na sua conta** e pode continuar **privada**.  
O que muda é só a implantação do Apps Script.

---

## Opção A — GitHub Pages (sem login Google no celular)

Ideal se o médico **não** deve usar conta Google.

1. Arquivos no Apps Script: **Code.gs** + **Index.html** completo (`gas/Index.html`, ~1900+ linhas).
2. Propriedades: `SPREADSHEET_ID`, `API_TOKEN`
3. Rodar `setupSheets()` uma vez
4. Implantar App da Web:
   - Executar como: **Eu**
   - Quem tem acesso: **Qualquer pessoa** ← anônimo (não “com Conta do Google”)
   - **Nova versão** → Implantar
5. Teste em aba anônima:
   `URL/exec?action=getAll&token=SEU_TOKEN&callback=cb`  
   Deve aparecer `cb({...})`, **não** tela de login.
6. No site do GitHub Pages: cole URL `/exec` + token → Salvar

**Não** deixe a planilha pública. Com “Executar como: Eu”, o script acessa a planilha privada.

---

## Opção B — Abrir `/exec` (UI dentro do Apps Script)

1. Cole o **Index.html completo** (com CSS e JS dentro — se ficar sem estilo e com “—”, o HTML está incompleto)
2. Acesso: **Qualquer pessoa com Conta do Google** (ou Só eu)
3. Médico abre `/exec` logado no **Gmail dele**
4. Opcional: `ALLOWED_EMAILS=medico@gmail.com`

---

## Se o `/exec` abrir sem cores e com traços “—”

Você colou um Index.html **curto** (só o esqueleto).  
Substitua pelo arquivo `gas/Index.html` do projeto (arquivo grande) e faça **Nova versão**.
