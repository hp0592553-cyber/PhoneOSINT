# Nome de perfil do WhatsApp — integração oficial

Esta integração lida com o **nome de perfil informado no webhook de uma mensagem recebida** na sua conta da **WhatsApp Business Platform (Cloud API)**.

Ela **não** permite digitar um telefone qualquer e revelar o nome do usuário do WhatsApp. Não há integração oficial pública para esse tipo de consulta irrestrita. O campo de nome é escolhido pelo próprio usuário, pode mudar e **não comprova titularidade cadastral**.

## Consulta manual pelo GitHub Actions (sem enviar mensagem)

Em **Actions > PhoneOSINT - Consultar numero WhatsApp > Run workflow**, o GitHub mostra um campo de texto **Seu telefone brasileiro com DDD**. Digite o seu número e execute. Na aba **Summary** da execução, você verá se o número é válido, o tipo de linha e a região.

**Limitação:** apenas informar o telefone não permite obter o nome de perfil pelo WhatsApp oficial. O resumo informa "Nome do perfil do WhatsApp: não disponível por consulta de número". Nenhuma mensagem é enviada.

**Privacidade:** campos de `workflow_dispatch` não são segredos. Mesmo com repositório privado, pessoas autorizadas a acessar as execuções podem ter acesso ao valor do input ou aos metadados do evento; o programa não imprime o número, mas **não considere o campo confidencial**. Evite inserir dados de terceiros sem autorização.

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
