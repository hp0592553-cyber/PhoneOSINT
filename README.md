# PhoneOSINT 🇧🇷

## Projeto focado em nome associado (branch Codex)

**Branch de trabalho:** `codex/issue-1-associated-names`  
**Único workflow:** [PhoneOSINT — Nome por número](.github/workflows/whatsapp-perfil.yml)

Para executar: **Actions > PhoneOSINT - Nome por numero > Run workflow > Use workflow from: codex/issue-1-associated-names**. Digite somente seu próprio número ou use o segredo `PHONE_NUMBER`, confirme a autorização e abra a aba **Summary**.

O resultado indica se o número é válido e aponta consultas manuais de nome nestas páginas oficiais:
- [Truecaller — pesquisa reversa de telefone](https://www.truecaller.com/reverse-phone-number-lookup)
- [Sync.ME — busca reversa de número](https://sync.me/pt-br/reverse-phone-lookup/)

Esses dois serviços podem retornar **nomes associados** quando disponíveis, mas **não são prova de titularidade** e não garantem a identidade atual. O workflow não possui acesso programático aos dados internos deles, não faz scraping e não executa automaticamente a pesquisa. **Sem uma fonte autorizada disponível para integração, não é tecnicamente possível prometer descobrir o nome de qualquer pessoa pelo número, gratuitamente, sem chave e sem interação.**

O recurso **local** `associated_names.py` permite guardar, com origem e data, um resultado obtido manualmente e autorizado. Esse resultado **não é descoberto pela ferramenta**. Não envie arquivos de evidências pessoais ao GitHub.



**WhatsApp (nome de perfil em mensagens recebidas):** [guia de configuração e limitações](WHATSAPP.md). Esta integração não busca usuários pelo número.

📚 [Fontes oficiais, limites legais e MP 1.396/2026](FONTES_E_LEGALIDADE.md)


Projeto Python de investigação **legal e local** de números brasileiros. Busca possíveis vínculos com **empresas** informados em bases oficiais, sem atribuir identidade a pessoas físicas.

## Testar seu próprio número sem chave (issue #1)

Em **Actions > PhoneOSINT - Consulta sem chave > Run workflow**, confirme a autorização.
Use preferencialmente **Settings > Secrets and variables > Actions > New repository secret**,
com nome `PHONE_NUMBER`, e deixe `numero` vazio. O secret tem prioridade se ambos existirem.
Alternativamente digite seu número brasileiro com DDD em `numero`: **inputs de
workflow_dispatch não são secretos**, mesmo se o relatório omitir o telefone. Não use esse
campo para informação que precise permanecer confidencial. Logs e resumo não incluem o
número; não há artefatos de consulta nem nomes como inputs. Revise quem tem acesso ao repositório.

Existe somente `.github/workflows/whatsapp-perfil.yml`. Ele executa testes e gera
um resumo com validação de formato e páginas oficiais para consulta manual. Validar
formato não comprova linha ativa. O modo básico não faz busca reversa externa, não encontra
nomes automaticamente e não envia mensagens. GitHub Actions depende da disponibilidade e
da franquia do plano; o código não usa serviços pagos de consulta.

### Registrar um nome observado manualmente

Abra [Truecaller](https://www.truecaller.com/) ou [Sync.ME](https://sync.me/), selecione
Brasil (+55) e digite seu próprio número na interface oficial. Respeite login, limites,
termos e eventuais cobranças; não há garantia de resultado ou gratuidade dos serviços.
Não foi verificada documentação oficial de URL parametrizada de busca: por isso usamos
apenas páginas iniciais, sem inserir o telefone em links e sem inventar endpoints.

Crie **localmente** `consulta.evidence.json` (ignorado pelo git), substituindo os valores
fictícios abaixo pelo número e pela evidência que você está autorizado a registrar:

```json
[
  {
    "number": "+5531900000000",
    "name": "PESSOA FICTÍCIA",
    "source": "truecaller",
    "checked_on": "2026-10-31",
    "authorized": true
  }
]
```

`source` aceita `truecaller` ou `sync_me`; informe a data real da observação, nunca futura.
`authorized` declara sua autorização, não é prova técnica de consentimento. O arquivo e os
nomes são fornecidos por você, não autenticados pela ferramenta. Não use dados vazados.

```bash
python associated_names.py --evidence consulta.evidence.json
```

O programa pede o telefone com entrada oculta e exibe localmente nome, origem, data e
**“nome associado, não verificado”**, omitindo o número. Conserva nomes divergentes e
sinaliza conflito; não escolhe um titular. Evidências inválidas são contadas e descartadas;
arquivos ilegíveis falham com mensagem genérica. Não execute esse comando em Actions:
nomes são pessoais e a saída local os contém. A ferramenta `phoneosint.py` anterior
continua disponível para empresas e sua saída JSON **inclui o número completo**.

Nomes de Truecaller/Sync.ME não comprovam nome atual do WhatsApp, posse da linha nem
titularidade na operadora. Nenhum registro encontrado não significa ausência de associação.

### O que as fontes permitem concluir

Verificação documental em 31/10/2026:

| Fonte oficial | Evidência e limitação | Implementação |
| --- | --- | --- |
| [Truecaller Privacy FAQ](https://www.truecaller.com/privacy/privacy-faq) | Perfis e buscas limitadas, controles de privacidade; não comprova API reversa aberta | Orientação manual |
| [Sync.ME recursos](https://sync.me/pt-br/features/) | Anuncia busca reversa; não documenta autorização para scraping ou API aberta nessa página | Orientação manual |
| [Twilio Lookup v2](https://www.twilio.com/docs/lookup/v2-api) / [Caller Name](https://www.twilio.com/docs/lookup/v2-api/caller-name) | Autenticação obrigatória; Caller Name cobre operadoras dos EUA e consultas são cobradas | Não integrado: não atende ao escopo brasileiro sem chave |

**Não identificamos nas fontes verificadas uma API autorizada e viável sem chave para
retornar nomes de números brasileiros.** Isso não é prova de inexistência universal.
Nenhuma automação de fontes foi adicionada: a existência de busca manual não autoriza
scraping, contorno de login ou de limites. Uma integração futura exige documentação,
termos compatíveis, consentimento, autenticação, limites e controle de acesso.
O importador CNPJ existente funciona offline com arquivos previamente obtidos;
o webhook WhatsApp exige configuração Meta e só lê perfis de remetentes recebidos,
sem pesquisa reversa de números arbitrários.

## Funcionalidades

- Validação e normalização E.164 de números brasileiros.
- **Novo:** importador offline de arquivos públicos do CNPJ da Receita Federal (Empresas + Estabelecimentos) para SQLite.
- Busca exata de empresas que tenham declarado um número de telefone; retorna razão social, CNPJ da empresa e data da extração.
- Importa apenas naturezas jurídicas 2046, 2054 e 2062 (sociedades anônimas e limitadas) e estabelecimentos ativos.
- Exclui empresários individuais/MEI, não acessa cadastros pessoais nem faz raspagem de sites.
- Múltiplas empresas vinculadas ao mesmo número são apresentadas como ambiguidade.
- Sem dados encontrados: **Titular não identificado**. Isso também pode indicar apenas base incompleta.

**Atenção:** telefone declarado no CNPJ NÃO comprova quem é o titular atual do chip, nem quem usa o WhatsApp. Cadastros podem ser antigos, incorretos ou conter números reutilizados.

## Executar no Codespaces

Abra Code > Codespaces > Create codespace no GitHub e rode:

~~~bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python phoneosint.py "+55 31 90000-0000"
~~~

O exemplo é fictício. Sem base de CNPJ ou evidência pública previamente carregada, nenhum nome é encontrado.

## Importar Dados Abertos da Receita Federal

Fontes oficiais:

- [Dados Abertos do CNPJ](https://dadosabertos.rfb.gov.br/CNPJ/)
- [Leiaute oficial: campos da empresa e dos telefones](https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf)
- [Portal empresarial recomendado pela Anatel](https://www.qualempresameligou.com.br/)
- [LGPD, orientações da ANPD](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes)

Baixe legitimamente os arquivos **Empresas*.zip** e **Estabelecimentos*.zip** de uma mesma extração mensal. Cada comando aceita **um par de arquivos**; se a extração for dividida em vários volumes, um único par produz um índice **incompleto**, não nacional. Os arquivos podem ser muito grandes; verifique espaço e custos do Codespaces. Não há download automático ou API oculta.

Importe, substituindo a data do exemplo pela data real de referência dos arquivos:

~~~bash
python cnpj_base.py --empresas Empresas0.zip --estabelecimentos Estabelecimentos0.zip --snapshot 2026-10-01 --db phoneosint_cnpj.sqlite
~~~

A data é fornecida manualmente e os arquivos não são autenticados automaticamente. Consulte o banco gerado:

~~~bash
python phoneosint.py "+55 31 90000-0000" --cnpj-db phoneosint_cnpj.sqlite
~~~

Os resultados são **associações empresariais históricas**, não titularidade da linha. Para consultar a titularidade de linhas empresariais abrangidas pela Anatel, utilize o portal Qual Empresa Me Ligou diretamente no navegador.

### Evidência empresarial informada manualmente (opcional)

Também é possível passar um arquivo JSON local do tipo:

~~~json
[
  {
    "number": "+5531900000000",
    "name": "EMPRESA EXEMPLO LTDA",
    "kind": "company_public",
    "source_url": "https://www.qualempresameligou.com.br/",
    "checked_on": "2026-10-31"
  }
]
~~~

**Os valores acima são inventados**, não são uma consulta real. Salve como consulta.evidence.json e use:

~~~bash
python phoneosint.py "+55 31 90000-0000" --evidence consulta.evidence.json
~~~

O projeto **não verifica automaticamente** esses dados.

## Privacidade e segurança

NÃO publicar números particulares, tokens, CPF, evidências ou bancos SQLite no GitHub. A LGPD pode incidir até sobre dados públicos usados para identificar pessoas naturais. Use apenas para finalidades legítimas, com minimização e respeito ao contexto de publicação. Não exponha uma API irrestrita de busca reversa. O arquivo .gitignore reduz o risco de envio acidental de dados, mas não substitui uma revisão antes do commit.
