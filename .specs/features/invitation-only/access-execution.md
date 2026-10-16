# Execução da prova mínima

## Passo 1: fornecedores e ambiente

Concluído localmente em 2026-10-16. Docker Desktop já ativo, sem alterações no daemon ou em containers de outros projetos. Servidores oficiais v7.0.0.6/efaad8e e XFTP CLI recebidos da release v7.0.0, com SHA-256 igual aos digests publicados. Cliente CLI oficial v7.0.0.11/e11128ce separado do fonte iOS. Manifesto: tools/taverna/access_proof/inputs.json.

Imagem Ubuntu fixada por digest; ferramentas de suporte instaladas somente nessa imagem. Binários executaram versão/ajuda em container sem rede, rootfs somente leitura, usuário sem privilégios, capabilities removidas e no-new-privileges. SMP e XFTP inicializaram configuração fictícia em .build/access-qualification/run-a, somente no worktree. Nenhum segredo real ou configuração local do sistema criada.

Gates: hashes exatos, versão/ajuda e inicialização oficial; regressões Foundation e validação estrita da spec. Conteúdo dos logs permanece local. Esses gates provam fornecedores e preparação, não associação, revogação ou integração do app.

Próximo passo: ponte TLS mínima e driver de integração, conforme access-proof-plan.md. Os 34 critérios do produto permanecem Pending.
