# Execução da prova mínima

## Passo 1: fornecedores e ambiente

Concluído localmente em 2026-10-16. Docker Desktop já ativo, sem alterações no daemon ou em containers de outros projetos. Servidores oficiais v7.0.0.6/efaad8e e XFTP CLI recebidos da release v7.0.0, com SHA-256 igual aos digests publicados. Cliente CLI oficial v7.0.0.11/e11128ce separado do fonte iOS. Manifesto: tools/taverna/access_proof/inputs.json.

Imagem Ubuntu fixada por digest; ferramentas de suporte instaladas somente nessa imagem. Binários executaram versão/ajuda em container sem rede, rootfs somente leitura, usuário sem privilégios, capabilities removidas e no-new-privileges. SMP e XFTP inicializaram configuração fictícia em .build/access-qualification/run-a, somente no worktree. Nenhum segredo real ou configuração local do sistema criada.

Gates: hashes exatos, versão/ajuda e inicialização oficial; regressões Foundation e validação estrita da spec. Conteúdo dos logs permanece local. Esses gates provam fornecedores e preparação, não associação, revogação ou integração do app.

Próximo passo: ponte TLS mínima e driver de integração, conforme access-proof-plan.md. Os 34 critérios do produto permanecem Pending.

## Passo 2: ponte e integração real

Concluído localmente em 2026-10-16. Componente experimental em tools/taverna/access_proof/gateway.py: TLS com certificado por dispositivo, dois backends administrativos fixos, lista local de associações e consulta periódica para encerrar conexões. Não implementa emissão de convites ou um serviço administrativo de produção.

A rodada run-b usou credenciais e bancos novos. O comando TAVERNA_PROOF_RUN=b python3.12 tools/taverna/access_proof/test_boundary.py passou 11/11 testes, zero skips, em 11,888 segundos na execução final. Controles positivos trocaram texto em ambos os sentidos no SMP e compararam o arquivo recebido byte a byte no XFTP. O cliente de prova desconhecido possui certificado da mesma CA, mas não está na lista, distinguindo autenticação TLS de associação ativa.

A retirada da associação e a falta/invalidez da política fecharam os dois fluxos de controle em menos do limite observado de quatro segundos, dentro do critério de 60 segundos. Esses fluxos já tinham recebido resposta TLS do backend real; os clientes oficiais também mantinham conexões do controle positivo. Não foi feito ensaio de um download grande revogado a meio; esse caso e a semântica completa do app continuam pendentes.

### Adequação dos checks

| Obrigação do experimento | Asserção localizada | Resultado esperado |
| --- | --- | --- |
| AP-01, protocolo real | test_boundary.py:67, assertIn do conteúdo recebido; :86, assertEqual(received.read_bytes(), payload) | Texto exato nos dois sentidos e arquivo idêntico |
| AP-02, negar acesso | test_boundary.py:24, assertEqual(result, {allowed_bytes: False}); casos :88/92 | Nenhum byte de backend para ausente/desconhecido |
| AP-03, retirar associação | test_boundary.py:41/42, closed True e seconds menor que 60; :96; :126/127 | Sessões cortadas, novos acessos negados e nenhum arquivo baixado pelo revogado |
| AP-04, fechar na falha | test_boundary.py:102/108 chamam assert_closed e assert_denied para política ausente e oito formas inválidas | Falha não abre acesso novo ou existente |
| AP-05, destinos fixados | test_boundary.py:160/162/165, sentinela responde ao controle direto e contador continua 1 após CONNECT pela ponte | Destino fornecido pelo cliente não é seguido pela ponte |
| AP-06, isolamento | test_boundary.py:135/138/140/146, redes internas, portas não publicadas, rootfs somente leitura e bypass direto recusado | Fixture sem exposição e relays fora da rede do cliente |

Asserções novas se limitam a AP-01 a AP-06; AP-07 é documentação/origem/revisão. As provas existentes da fundação continuam 70/70, sem mudança de asserções. Nenhum controle echo substitui SMP/XFTP. Scripts de prova não entram automaticamente na CI, que continua sem segredos e sem containers de aplicação.

Próximo passo: relatório delimitado, Verifier independente e CI antes da integração da issue #12. Os critérios completos do app permanecem Pending.
