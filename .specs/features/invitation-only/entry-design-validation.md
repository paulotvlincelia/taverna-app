# Validação independente do desenho de entrada

**Veredicto:** PASS
**Data:** 2026-10-16
**Diff verificado:** `da9136c541dd4ca06da0269dfd12355a360e0d3b..1d203d9c7687e07874c1d419fc02b572ec0a737b`
**Fonte do app:** `da9136c541dd4ca06da0269dfd12355a360e0d3b`
**Fonte SimpleXMQ:** `efaad8e73436d60f5052f07dda6b71151ad5039b`
**Verifier:** agente independente do autor; ownership limitado a este arquivo

## Resultado por critério

| Critério | Evidência | Resultado |
| --- | --- | --- |
| ED-01 | `.specs/features/invitation-only/entry-design.md:3` classifica o documento como proposta não implementada; `entry-design.md:10` preserva convite individual e ausência de telefone/e-mail; `entry-design.md:12` mantém o produto sem comprovação; `.specs/features/invitation-only/spec.md:180` a `spec.md:213` contêm 34 linhas `Pending`, confirmadas por contagem determinística | PASS |
| ED-02 | `entry-design.md:42` a `entry-design.md:54` descrevem o código reutilizado; `entry-design.md:136` a `entry-design.md:147` fixam SHAs, fontes e limites. Leitura direta confirmou app/NSE/Share como controladores separados e a ordem de configuração da Share Extension. No clone fixado, `src/Simplex/Messaging/Client.hs:441`, `src/Simplex/Messaging/Client.hs:452`, `src/Simplex/Messaging/Transport/Client.hs:167`, `src/Simplex/Messaging/Transport/Client.hs:242` e `src/Simplex/FileTransfer/Client.hs:209` sustentam as alegações sobre SOCKS, autenticação, TLS interno e XFTP. Trinta links relativos resolveram; as nove fontes externas responderam HTTP 200 | PASS |
| ED-03 | `entry-design.md:18` a `entry-design.md:25` recomendam A1 e reservam A2 como fallback; `entry-design.md:95` a `entry-design.md:105` põem transporte nativo antes de admissão e UI, sem promover a proposta a arquitetura de produção | PASS |
| ED-04 | `entry-design.md:58` declara que nenhum endpoint existe; `entry-design.md:60` a `entry-design.md:71` delimitam convite, owner mTLS e autoridade; `entry-design.md:75` a `entry-design.md:81` cobrem hash do token, transação, concorrência, repetição e capacidade; `entry-design.md:85` a `entry-design.md:93` cobrem bootstrap autenticado, limites, autoridade SQLite e falha fechada | PASS |
| ED-05 | `entry-design.md:36` e `entry-design.md:101` exigem `DESIGN.md` antes da UI; `entry-design.md:46` a `entry-design.md:50` cobrem app, NSE e Share Extension; `entry-design.md:118` a `entry-design.md:120` exigem contenção nova e proíbem reutilizar o receipt do primeiro build como prova de rede | PASS |
| ED-06 | Diff limitado a `entry-design.md`, `README.md`, `docs/taverna/roadmap.md` e `.specs/STATE.md`; 70/70 regressões, checker Foundation, compileall, `validate_spec.py`, commit checker, links/âncoras e `git diff --check` passaram. Nenhum segredo ou convite completo foi encontrado nos quatro arquivos | PASS |

## Revisão crítica de simplicidade e segurança

- A1 reutiliza o SOCKS existente e mantém A2 como decisão posterior somente se o gate falhar. O desenho não introduz painel web, login social, fila, Redis, protocolo próprio ou alteração simultânea dos daemons (`entry-design.md:14`, `entry-design.md:25`).
- A API, o serviço de admissão e a ponte são propostas. O texto não reclama endpoints, build iOS, execução em aparelho, rede nativa ou produção existentes (`entry-design.md:3`, `entry-design.md:12`, `entry-design.md:58`).
- O adaptador local não confia apenas em loopback ou porta efêmera. A proposta exige usuário/senha SOCKS aleatórios por processo, somente em memória, rejeição sem credencial e rejeição de reuso. O SimpleXMQ fixado realmente converte `SocksAuthUsername` em `SocksCredentials` e usa `socksConnectAuth`; `SocksIsolateByAuth` gera isolamento, mas não um segredo de processo (`entry-design.md:27`, `Messaging/Client.hs:452`, `Transport/Client.hs:223`, `Transport/Client.hs:242`).
- Convite e associação têm estados duráveis e ordem transacional coerente. A repetição com a mesma chave recupera o certificado persistido; uma chave diferente perde a corrida; revogação não reativa membro (`entry-design.md:75` a `entry-design.md:81`).
- A identidade administrativa vem de mTLS validado pelo serviço e papel consultado na autoridade durável. Corpo HTTP e headers de proxy não concedem identidade (`entry-design.md:71`, `entry-design.md:87`).
- A ponte consulta uma única autoridade SQLite com prazo e falha fechada; estado ilegível ou indisponível encerra acesso (`entry-design.md:91` a `entry-design.md:93`).
- O modelo mantém o TLS interno do relay separado do TLS externo da ponte. A prova real dessa composição nos três processos iOS continua corretamente bloqueada pelo primeiro gate (`entry-design.md:54`, `entry-design.md:99`).

## Gates executados

Os gates completos e o sensor rodaram no commit documental `4c7738422`. O commit final `1d203d9c7` alterou somente `entry-design.md`, com quatro inserções e uma substituição. Esse delta recebeu revisão direta, commit checker e `git diff --check`; os gates completos não foram repetidos pelo Verifier.

| Comando/check | Resultado |
| --- | --- |
| `python3.12 -m unittest discover -s tools/taverna/tests -v` | PASS, 70 testes, 0 falhas, 0 skips |
| `python3.12 tools/taverna/check_foundation.py` | PASS; saída limita o resultado à fundação, sem prova de build/release iOS |
| `python3.12 -m compileall -q tools/taverna` | PASS, exit 0 |
| `python3.12 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/invitation-only/spec.md` | PASS, 0 erros, 0 warnings |
| `python3.12 .agents/skills/tlc-spec-driven/scripts/check_commit.py --message "docs(invitation): require authentication at the local adapter"` | PASS no commit final `1d203d9c7` |
| `git diff --check 4c7738422427140606d7633b4bd2bd7ee85a943e..1d203d9c7687e07874c1d419fc02b572ec0a737b` | PASS no delta final |
| Checker local de Markdown para os quatro arquivos alterados | PASS, 30 alvos relativos existentes, 0 âncoras ausentes |
| `curl -L --fail` equivalente por status para as fontes externas de `entry-design.md` | PASS, 9/9 HTTP 200; disponibilidade não prova semântica de runtime |
| Contagem de requisitos e estados | PASS, 34 requisitos e 34 `Pending` |
| Busca de chaves privadas, bearer, secrets e URL HTTPS com fragmento nos quatro arquivos | PASS, zero ocorrência |

`validate_state.py invitation-only` não foi executado. Esse gate representa a feature completa e exigiria `validation.md` com PASS, incompatível com os 34 requisitos de produto ainda `Pending` (`.specs/features/invitation-only/access-proof-validation.md:191`).

## Sensor documental

O sensor usou o scratch `taverna-entry-sensor-verifier-4c773842` sob Projects, destacado no primeiro commit documental. Nenhuma mutação ocorreu no checkout real e nenhum `stash` foi usado. O commit final alterou somente o requisito do adaptador e foi revisto como delta; não modificou os alvos do sensor.

| Mutação | Check que detectou | Resultado |
| --- | --- | --- |
| M1: `spec.md` trocado por `missing-spec.md` no link canônico | Checker local de links Markdown | KILLED: `missing local targets: ['missing-spec.md']` |
| M2: `INV-01` alterado de `Pending` para `Verified` | Contagem exata de estados | KILLED: `pending=33 expected=34` |
| M3: gate nativo alterado para liberar convites/UI/produção | Check semântico de ordem e bloqueio dos três gates | KILLED: `native_gate_does_not_release_invites_ui_prod=False` |

**Sensor:** 3/3 mutações mortas. O scratch foi removido. O porcelain do checkout real coincidiu com o baseline vazio antes de criar este relatório.

## Limites e riscos residuais

- A escolha A1 e a CLI administrativa ainda dependem de confirmação do proprietário (`entry-design.md:69`, `.specs/STATE.md:12`). Isso impede tarefas formais, não invalida o desenho para revisão.
- A frase em `entry-design.md:83` sobre app/browser não registrarem o fragmento é uma obrigação proposta, não garantia atual. O próprio documento identifica que o handler herdado registra a URL e exige interceptação anterior, teste de logs e ausência de analytics (`entry-design.md:50`, `entry-design.md:132`).
- NWListener, Keychain e Associated Domains são primitivas candidatas. As fontes Apple não provam listener loopback, suspensão/retomada, compartilhamento de credencial entre targets ou Universal Link em aparelho (`entry-design.md:18`, `entry-design.md:130`, `entry-design.md:142` a `entry-design.md:144`).
- Dependências HTTP/X.509/CSR, terminação mTLS, serialização de certificado, contenção de rede e operação conjunta sobre SQLite seguem sem qualificação. O documento as mantém como gates, sem adotar versão ou runtime (`entry-design.md:38`, `entry-design.md:71`, `entry-design.md:120`).
- Nenhum Docker, simulador, provider, instalação, build iOS, teste de transporte nativo ou mutação de rede foi executado nesta validação. Este PASS cobre somente a entrega documental no SHA informado.

## Conclusão

**PASS:** o delta documenta uma proposta pequena, rastreável e fail-closed, preserva as decisões aprovadas e os 34 requisitos `Pending`, e impede que a prova CLI anterior seja confundida com integração iOS. Os gates documentais e o sensor passaram. Nenhuma implementação, arquitetura de produção ou capacidade de rede nova foi declarada pronta.
