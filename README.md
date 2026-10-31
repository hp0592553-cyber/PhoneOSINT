# PhoneOSINT 🇧🇷

Protótipo Python para investigação **legal, transparente e verificável** de números brasileiros.

## O que faz

- Valida números do Brasil e normaliza para E.164.
- Informa região telefônica e tipo de linha, quando disponível.
- Permite associar **nome empresarial** a um número somente a partir de uma evidência local documentada, sem verificação automática da fonte.
- Retorna **Titular não identificado** quando não houver evidência.
- Mostra o caminho oficial para consulta de números empresariais.

**Limitação:** não existe consulta pública universal ao nome do titular de qualquer celular pessoal. Nome empresarial, nome em aplicativo e titular cadastral não são equivalentes.

## Codespaces

Abra o repositório em **Code > Codespaces > Create codespace** e rode:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python phoneosint.py "+55 31 90000-0000"
```

O último comando usa um número ilustrativo. O programa não envia esse número para nenhum servidor.

### Evidência empresarial local (opcional)

Após consultar legitimamente uma fonte, crie no seu ambiente um arquivo `consulta.evidence.json` — **não comite números privados**:

```json
[
  {
    "number": "+5531900000000",
    "name": "EMPRESA EXEMPLO LTDA",
    "kind": "company_public",
    "source_url": "https://www.qualempresameligou.com.br/",
    "checked_on": "2026-10-31"
  }
]
```

Dados acima são **fictícios** e não comprovam nenhum titular real. O endereço precisa ser conferido com o resultado efetivamente encontrado na fonte. Rode:

```bash
python phoneosint.py "+55 31 90000-0000" --evidence consulta.evidence.json
```

Isso exibe **nome empresarial informado por evidência (não verificado automaticamente)**. Somente comparar números completos e comprovar data e origem; a aplicação não acessa o portal automaticamente.

## Fontes

- [Qual Empresa Me Ligou](https://www.qualempresameligou.com.br/) — identifica linhas atribuídas a empresas (razão social/CNPJ), quando abrangidas pelo serviço.
- [Anatel: chamadas abusivas](https://www.gov.br/anatel/pt-br/consumidor/chamadas-abusivas).
- [ANPD: bases legais de tratamento de dados](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes).

## Privacidade

Sem bots de vazamentos, scraping não autorizado, buscas por CPF, enumeração em massa ou uso de sessões do WhatsApp. Nunca publique números particulares, dados pessoais, tokens ou arquivos de consulta em GitHub. O `.gitignore` exclui `*.evidence.json`, mas outros nomes de arquivo ainda podem ser publicados.

Próximo passo: estudar uma integração permitida e documentada com fonte pública de **pessoas jurídicas**, antes de automatizar qualquer consulta.
