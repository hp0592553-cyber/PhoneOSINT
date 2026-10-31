# PhoneOSINT 🇧🇷

📚 [Fontes oficiais, limites legais e MP 1.396/2026](FONTES_E_LEGALIDADE.md)


Projeto Python de investigação **legal e local** de números brasileiros. Busca possíveis vínculos com **empresas** informados em bases oficiais, sem atribuir identidade a pessoas físicas.

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
