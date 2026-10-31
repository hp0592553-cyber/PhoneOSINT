# Fontes e legislação para PhoneOSINT
Atualizado em 31/10/2026. Pesquisa informativa, não é parecer jurídico.

## Fontes

| Serviço | O que retorna | O que NÃO retorna |
|---|---|---|
| [Qual Empresa Me Ligou](https://www.qualempresameligou.com.br/) | Razão social e CNPJ associados a certos números empresariais | Nome de pessoa física |
| [Consulta Número da ABR Telecom](https://consultanumero.abrtelecom.com.br/) | Prestadora do número, inclusive após portabilidade | Titular cadastral |
| [Dados Abertos do CNPJ da Receita](https://dadosabertos.rfb.gov.br/CNPJ/) | Telefones declarados por empresas em extrações periódicas | Identidade do usuário atual da linha |
| [Cadastro Pré-Pago](https://cadastropre.com.br/) | Prestadoras com linhas pré-pagas vinculadas ao próprio CPF | Nomes de outros titulares nem números cadastrados |
| [Origem Verificada](https://www.gov.br/anatel/pt-br/regulado/acompanhamento-e-controle/autenticacao-e-identificacao-de-chamadas) | Nome e selo de empresa durante chamadas autenticadas em dispositivos compatíveis | Identidade universal de pessoas físicas |

Aplicativos de identificação de chamadas, como [Truecaller](https://www.truecaller.com/), podem mostrar nomes associados a números; isso não comprova a titularidade registrada pela operadora, está sujeito a erro e aos termos de uso do serviço. O PhoneOSINT não automatiza consultas ao Truecaller nem faz scraping dos sites acima.

## Bases legais e limitações

**LGPD (Lei 13.709/2018)**: dados pessoais continuam protegidos mesmo quando estão publicamente acessíveis. O tratamento de nomes e telefones exige finalidade e base legal adequadas, além de respeito aos direitos dos titulares. Ter uma base legal de tratamento não obriga a operadora a fornecer cadastros privados a qualquer interessado.
- [ANPD: perguntas e respostas sobre LGPD](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes)
- [ANPD: guia do legítimo interesse](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-lanca-guia-orientativo-sobre-legitimo-interesse)

**Medida Provisória 1.396/2026**, publicada em 13/10/2026:
- Art. 5º prevê base centralizada de recursos de numeração e seus titulares, sob supervisão da Anatel.
- Art. 4º exige identificação de **pessoas jurídicas** nas chamadas autenticadas, com nome empresarial e logotipo, quando houver.
- Art. 5º, §6º: dados protegidos nos termos da legislação específica.
- Art. 8º: funcionamento e exigências dependem de regulamentação e prazos.
- **Não cria consulta pública irrestrita aos nomes de titulares pessoas físicas.** Não há API pública dessa base integrada neste projeto.
- [Texto da MP na Câmara](https://www2.camara.leg.br/legin/fed/medpro/2026/medidaprovisoria-1396-9-outubro-2026-800052-publicacaooriginal-181590-pe.html)
- [Acompanhamento no Congresso](https://www.congressonacional.leg.br/pt_BR/materias/medidas-provisorias/-/mpv/175932)
- [Agenda regulatória da Anatel, outubro de 2026](https://www.gov.br/anatel/pt-br/regulado/agenda-regulatoria/2025-2026/agenda-regulatoria-2025-2026-item-41)

## Como exibir resultados com responsabilidade

- **Empresa identificada em base pública:** mostrar nome empresarial, CNPJ, fonte e data, mas não declarar quem usa o WhatsApp ou é titular atual.
- **Nome comunitário em aplicativo:** não confirmado; não afirmar identidade.
- **Posse confirmada voluntariamente por SMS:** prova apenas acesso ao número naquele momento, NÃO titularidade do cadastro.
- **Sem evidência verificável:** retornar 'Titular não identificado'.

**Uso proibido neste projeto:** vazamentos, bots que vendem CPF, acesso à sessão do WhatsApp de terceiros, burlar autenticação, mineração irrestrita de números e divulgação de dados pessoais sem base legal.

## Documentação complementar
- [Anatel — chamadas abusivas](https://www.gov.br/anatel/pt-br/consumidor/chamadas-abusivas)
- [Anatel — FAQ numeração](https://www.gov.br/anatel/pt-br/regulado/numeracao/perguntas-frequentes)
- [Anatel — Cadastro Pré](https://www.gov.br/anatel/pt-br/dados/utilidade-publica/cadastro-pre-pago/)
- [Truecaller — Privacy FAQ](https://www.truecaller.com/privacy/privacy-faq)
