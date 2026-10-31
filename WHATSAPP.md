# Nome de perfil do WhatsApp — integração oficial

Esta integração lida com o **nome de perfil informado no webhook de uma mensagem recebida** na sua conta da **WhatsApp Business Platform (Cloud API)**.

Ela **não** permite digitar um telefone qualquer e revelar o nome do usuário do WhatsApp. Não há integração oficial pública para esse tipo de consulta irrestrita. O campo de nome é escolhido pelo próprio usuário, pode mudar e **não comprova titularidade cadastral**.

## Um único workflow: sem chave, sem mensagens

Acesse [Actions > PhoneOSINT - Consulta sem chave](https://github.com/hp0592553-cyber/PhoneOSINT/actions/workflows/whatsapp-perfil.yml) e clique em **Run workflow**.

- Digite o número **que é seu**, com DDD, no campo `numero`; ou configure o segredo `PHONE_NUMBER` e deixe o campo vazio.
- Marque a confirmação de autorização.
- Execute e abra a aba **Summary**.

**Não precisa de API key.** Esse fluxo valida o telefone e informa a região, mas não obtém o nome do usuário do WhatsApp. A API oficial do WhatsApp não fornece uma função pública de consulta de perfis arbitrários somente pelo telefone, sem interação autorizada.

**Privacidade:** campos preenchidos no Run workflow não são segredos; pessoas com acesso à execução podem ver metadados. Para testar o próprio número com mais privacidade, prefira o segredo `PHONE_NUMBER`. O relatório não imprime o número completo.

Para verificar o seu nome de perfil, abra **WhatsApp > Configurações > seu perfil** no celular. Isso não requer mensagens ou API.

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
