# Ambiente do app no MacBook

Todos os clones, worktrees e estados do projeto ficam sob Projects. Cada sessão tem branch, responsável, harness, escopo e integrador identificados. O clone principal não é checkout compartilhado de desenvolvimento. Use Git nativo conforme [CONTRIBUTING](../../CONTRIBUTING.md).

O [guia do build iOS](ios-build.md) contém o procedimento comprovado, entradas fixadas, comandos e limites. A primeira prova usa MacBook arm64, Python 3.12, Xcode 27.1, SDK Simulator 27.1 e runtime 27.0/iPhone 17. Nix 2.34.9 foi autorizado como exceção de sistema, com store APFS/daemon fora de Projects. Dependências/compiladores imutáveis da store podem ser reutilizados; DerivedData, SourcePackages, caches, produtos e dados graváveis não são compartilhados.

## Sessão iOS

O executor versionado seleciona DEVELOPER_DIR por comando, preservando xcode-select global. Define CFFIXED_USER_HOME, temporários, módulos, XDG, CACHE_ROOT, precompilados, estatísticas de SDK e CAS dentro do worktree, sem redefinir HOME. Os ajustes efetivos dos targets são conferidos antes do build. Estado que escape por alias/symlink é recusado.

Conforme [APP-004](decisions/README.md), o simulador exclusivo recebe registro no índice padrão do SDK. Seus dados/logs físicos ficam em .build/SimulatorDevices e .build/SimulatorLogs, com aliases por UDID no índice do Xcode. O preflight prova a correspondência física e o destino efetivamente selecionado pelo executor. Um device set privado não foi aceito pelo Xcode instalado; criar um dispositivo apenas nele não comprova seleção/execução.

Use ios_session.py create/guard/control e ios_proof.py conforme o guia. Em sessões paralelas, registrem ambos os UDIDs antes de qualquer teste. Não apagar, resetar ou desligar dispositivos de outra sessão. App já instalado com dados exige novo UDID próprio; preserve o anterior e seus receipts. O encerramento desliga somente o destino próprio.

O processo real do app comprova negação de IP remoto antes do main e loopback permitido em cada lançamento. Serviços do sistema iOS ficam fora dessa contenção. Não há alteração de VPN/firewall global. Perfil, conversa, conta Apple, assinatura em aparelho e distribuição não fazem parte da primeira prova.

## Preflight da fundação

```bash
python3.12 tools/taverna/preflight.py
```

O preflight F0 continua sendo inventário de ferramentas e caminhos. Usa Python stdlib, não consulta credenciais e conserva gates BLOCKED enquanto não houver sua própria prova de núcleo/assinatura. Seu probe de set privado é histórico de F0; não é o executor de F1 e não consome os receipts da prova iOS. foundation_tools aprovado não equivale a build ou teste iOS. A prova F1 usa ios_session.py e ios_proof.py, com artefatos e estados separados.

Não executar scripts/ios/download-libs.sh ou prepare.sh automaticamente: usam Downloads compartilhado e substituem diretórios. O procedimento versionado qualifica hashes, origem, plataforma e payload, mantendo tentativas distintas. Bibliotecas de fornecedor e núcleo construído localmente são identificados separadamente.

Desenvolvimento local, integração com dados fictícios e produção existente permanecem separados. Este preparo não configura instâncias, DNS, APNs ou distribuição. Signing em aparelho terá responsável e uso serializado próprios. Antes de remover um worktree, confira conflitos, commits não integrados, arquivos locais e aliases do SDK. Pendências exigem reconciliação; não usar limpeza forçada.
