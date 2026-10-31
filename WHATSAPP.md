# Nome de perfil do WhatsApp — integração oficial

Esta integração lida com o **nome de perfil informado no webhook de uma mensagem recebida** na sua conta da **WhatsApp Business Platform (Cloud API)**.

Ela **não** permite digitar um telefone qualquer e revelar o nome do usuário do WhatsApp. Não há integração oficial pública para esse tipo de consulta irrestrita. O campo de nome é escolhido pelo próprio usuário, pode mudar e **não comprova titularidade cadastral**.

## Um unico workflow: pesquisar meu numero sem enviar mensagem

Acesse [Actions > PhoneOSINT - Consultar meu numero](https://github.com/hp0592553-cyber/PhoneOSINT/actions/workflows/whatsapp-perfil.yml) e clique em **Run workflow**.

- **numero**: informe seu numero com DDD. **Nao e campo secreto**: dados de entrada podem aparecer em metadados do GitHub Actions. Para maior privacidade, deixe em branco e configure o segredo `PHONE_NUMBER` em **Settings > Secrets and variables > Actions**.
- **confirmo_numero_meu**: marque apenas se este for seu numero ou tiver autorizacao.
- **pesquisar_web**: opcional. Quando marcado, envia o numero para a **API oficial do Brave Search** (servico de terceiros) a fim de buscar mencoes PUBLICAS. Pode existir custo de API. Exige segredo `BRAVE_SEARCH_API_KEY`, obtido em https://api.search.brave.com/.

No resultado, abra a **aba Summary** da execucao. Ali sao exibidos validacao, tipo, regiao e, se a busca foi habilitada e a chave configurada, titulos e dominios de ate cinco paginas encontradas. Nao sao mostrados o numero completo ou trechos contendo seu numero. Os resultados NAO sao confirmacoes de identidade.

**Sem chave da Brave:** o teste valida formato e regiao, mas nao faz busca externa. **Sem mensagem ao WhatsApp:** o nome do perfil nao pode ser obtido diretamente pela API oficial. A pesquisa web nao consulta o cadastro privado de usuarios do WhatsApp.

A pesquisa Brave ocorre apenas se voce marcar a opcao; consulte os termos e custos do seu plano antes. A pesquisa pode retornar nada, paginas antigas ou mencoes a outra pessoa que tenha usado o numero no passado.

Para descobrir o numero cadastrado na sua conta WhatsApp, abra **WhatsApp > Configuracoes > seu perfil** no proprio celular. A funcao oficial **Conta > Pedir dados da conta** tambem permite obter seu relatorio privado, sem mensagens:
https://faq.whatsapp.com/526463418847093/?cms_platform=web&locale=pt_BR

## Teste imediato, sem conta Meta

No Codespaces, execute:

```bash
python whatsapp_profile.py --demo
python -m unittest discover -s tests -p 'test_whatsapp_profile.py' -v
```

A demonstração usa **USUARIO DE TESTE** e um número fictício. O GitHub Actions em `.github/workflows/whatsapp-perfil.yml` testa o código e **não recebe dados reais de WhatsApp**.

## Como obter um nome REAL com seu próprio número

1. Configure uma conta/app na [Meta for Developers](https://developers.facebook.com/) com **WhatsApp Business Platform Cloud API** e um número de negócio para receber mensagens. Normalmente esse número será diferente do seu número pessoal de teste.
2. Configure no aplicativo o webhook de **messages**, com uma URL **HTTPS** pública de um servidor sob seu controle.
3. Configure, no ambiente desse servidor, `META_APP_SECRET` (segredo do app) e `META_VERIFY_TOKEN` (um token que você escolheu). **Nunca** salve esses valores no GitHub nem publique-os em screenshots/logs.
4. Inicie o receptor em um ambiente de desenvolvimento (ele usa somente a biblioteca padrão do Python):

   ```bash
   python whatsapp_profile.py --serve --host 127.0.0.1 --port 8080
   ```

5. Use um proxy/túnel HTTPS confiável ou implante em servidor HTTPS, com encaminhamento para a porta 8080; configure a URL de callback no painel da Meta como `https://SEU-DOMINIO/webhook`. Não exponha um webhook de produção diretamente no Codespaces. A assinatura `X-Hub-Signature-256` é verificada antes de processar dados.
6. Envie **do seu próprio WhatsApp** uma mensagem para o número do negócio. Se o campo `contacts[].profile.name` estiver presente, o programa exibirá o nome de perfil **no terminal do servidor**, sem registrar número nem texto da mensagem.

O receptor não grava banco de dados, não responde às mensagens nem consulta nomes de terceiros. A verificação com a Meta precisa de uma URL acessível externamente; o GitHub Actions, sozinho, **não funciona como webhook público**.

## Formato e privacidade

- O extrator aceita apenas contatos que correspondam ao **remetente da mensagem recebida**, e ignora cartões de contato encaminhados.
- Para contas com `@username`, o `wa_id`/telefone pode não ser fornecido. O programa não tenta reconstruí-lo.
- Payloads de arquivo JSON (`--file`) são **não autenticados**, devem ser usados apenas para desenvolvimento e podem ser forjados.
- Se o usuário não enviou mensagem ou o campo não veio, o nome não pode ser obtido dessa forma.
- Não solicite mensagens em massa nem publique ou compartilhe nomes de terceiros sem base legal.

## Referências

- [WhatsApp Help: editar seu nome de perfil](https://faq.whatsapp.com/859240711908360/)
- [Meta: documentação de webhooks do WhatsApp](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview)
- [Exemplo do campo contacts.profile.name](https://whatsapp.serpro.gov.br/api-docs/documentacao/tipos_mensagens_recebidas/)
- [Meta: nomes de usuário do WhatsApp](https://about.fb.com/br/news/2026/06/e-hora-de-reservar-seu-nome-de-usuario-do-whatsapp/)
