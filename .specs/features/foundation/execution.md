# Execução da fundação pública

Data: 2026-10-16. Autor/integrador: Codex desktop. Base upstream 479548ee53ffb73db73841e77acbeee5a78dbbd5. Nenhuma alteração funcional no mensageiro.

T1: contribuição e checker em 6e6e9ad60. 14 testes aprovados. T2: preflight em aa844213d. Total 26 testes aprovados, zero skips. Comandos: python3.12 -m unittest discover -s tools/taverna/tests -v; python3.12 tools/taverna/check_foundation.py; compileall e git diff --check. Spec strict e tasks: zero erros/avisos.

Adequação: test_foundation.py afirma hashes das duas licenças, origem/SHA, links, redirect, atribuições, bloqueio de release e workflow sem privilégios. test_preflight.py afirma valor dos gates e motivos para cada ferramenta ausente, versões incompatíveis, SDK inválido, timeout e simulador ausente; proíbe comandos de credencial e verifica confinamento/symlink escape. Caminhos macOS comparados após resolve para /var e /private/var.

Preflight real: ferramentas Git/gh/Python e Xcode/SDK disponíveis; simulador, GHC/Cabal, proveniência das bibliotecas e assinatura ainda exigem prova. overall BLOCKED/exit 2; build_proven=false e push_proven=false. Nenhum binário da Taverna produzido. A instalação de ferramentas não comprova build ou notificações.

Duas worktrees nativas com branches e diretórios .build/.venv distintos foram preparadas. Responsabilidade e UDID pertencem ao handoff local; nenhum inventário operacional é publicado aqui. CI e Verifier no último commit ainda necessários para concluir T3.
