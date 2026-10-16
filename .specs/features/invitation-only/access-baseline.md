# Qualificação inicial do controle de acesso

Data: 2026-10-16. **Resultado: inspeção estática concluída; perímetro Taverna BLOCKED; provas dinâmicas NOT RUN.**

O app fixa SimpleXMQ efaad8e73436d60f5052f07dda6b71151ad5039b (7.0.0.6). O checkout de pesquisa está limpo e dez arquivos receberam hashes SHA-256 no manifesto local. Isso identifica o material inspecionado; não comprova qual versão está em produção ou execução dos testes upstream.

## Evidências por operação

Todos os caminhos da tabela pertencem ao [fonte imutável SimpleXMQ](https://github.com/simplex-chat/simplexmq/tree/efaad8e73436d60f5052f07dda6b71151ad5039b). As conclusões são limitadas aos mecanismos inspecionados, não uma auditoria integral.

| Operação | Evidência no SHA fixado | Resultado da leitura |
| --- | --- | --- |
| Criar fila SMP | src/Simplex/Messaging/Server.hs:1537–1542 | NEW consulta allowNewQueues e newQueueBasicAuth. Esse ramo não implementa associação individual Taverna. |
| Enviar/receber SMP | Server.hs:1257–1278 e 1543–1567 no mesmo diretório | SEND/SUB/GET/ACK usam chaves da parte/fila. Não consultam a senha de criação nesses ramos. Trocar create_password sozinho não implementa revogação de todas as operações existentes. |
| Criar arquivo XFTP | src/Simplex/FileTransfer/Server.hs:467–473 | FNEW consulta allowNewFiles e newFileBasicAuth. |
| Transferir arquivo existente | FileTransfer/Server.hs:443–465 e 474–483 | FPUT/FGET verificam chaves/estado do arquivo; a senha de criação não aparece como autorização dessas operações. |
| Registro de associação | Messaging/Server/QueueStore.hs:37–50; FileTransfer/Server/Store.hs:52–66 | Os registros lidos identificam recursos, chaves e serviços, não o ciclo convidado/dispositivo/revogação aprovado para a Taverna. |
| Certificado de cliente | Messaging/Transport/Client.hs:131; Transport/Server.hs:274–287 | Há primitiva de certificado para investigar reutilização. Ela não equivale a associação ativa, e identidade de serviço não deve ser confundida com participante. |
| Testes de senha existentes | tests/XFTPServerTests.hs:382–404 | Cobrem autenticação da criação e transferência com chaves. Foram lidos; execução NOT RUN. |

A conclusão de engenharia é que a configuração simples de senha compartilhada não satisfaz MEM-02/MEM-05. Isso não significa que criptografia ou autorização de filas do SimpleX estejam quebradas: a Taverna exige uma fronteira administrativa adicional.

## Destinos e grupos

No fork do app, src/Simplex/Chat/Library/Internal.hs:1561/1603 usa shortLinkPresetServers. apps/ios/SimpleXChat/APITypes.swift:267 define fallback de proxy SMP allowProtected. Alterar somente a lista da tela não comprova NET-02/NET-03. Observar tentativas reais em bootstrap, links, configuração, importação e extensões, inclusive na falha dos destinos autorizados.

Messaging/Protocol.hs:590 transporta o corpo de mensagem. O relay não deve precisar ler conteúdo ponta a ponta para administrar a Taverna. As duas alternativas de design precisam de autoridade do proprietário sobre os grupos oficiais; credencial de transporte não prova permissão de criar grupo. Participantes com software próprio podem coordenar comunicação por outros meios; não prometer controle sobre seus dispositivos.

## Matriz de prontidão

| Obrigação | Estado atual | Prova necessária |
| --- | --- | --- |
| Convite de entrada único/atômico e persistente | NOT IMPLEMENTED | Concorrência, repetição idempotente, limites e reinício |
| Revogação em 60 segundos | BLOCKED na configuração simples de senha | Cliente ativo/revogado, sessão nova/aberta e fluxo em andamento em SMP/XFTP |
| Cliente que ignora UI | NOT RUN | Rejeição no serviço sem depender dos botões |
| Grupos oficiais somente pelo proprietário | NOT RUN | Criação/alteração direta por convidado recusadas |
| Servidores próprios sem fallback | NOT RUN | Dois clientes reais e sentinela proibida, com destinos autorizados disponíveis/indisponíveis |
| Criptografia preservada | Restrição ativa | Prova com núcleo/clientes reais; echo e mocks não contam como SMP/XFTP |

Não havia executáveis nativos SMP/XFTP prontos no MacBook. O Docker Desktop já estava ativo; foram qualificados os binários Linux arm64 oficiais da release v7.0.0, exatamente no SHA SimpleXMQ fixado pelo app. Os hashes publicados pelo GitHub conferem e a execução de versão/ajuda confirma v7.0.0.6 / efaad8e. A imagem Ubuntu 24.04 tem digest fixado. Isso evita compilar os daemons e ainda não constitui prova de transporte. O cliente CLI de interoperabilidade é v7.0.0.11, release no SHA e11128ce, distinto do binário iOS do fork.

## Reprodução e limites

Checkout detached do SimpleXMQ no SHA acima, git status --porcelain vazio; pesquisar newQueueBasicAuth, newFileBasicAuth, verifyQueueTransmission e verifyXFTPTransmission e ler seus ramos completos. Conferir também registros e testes citados, sem inferir funcionamento só pela presença de palavras.

Nenhum acesso novo à VPS ou mudança em produção, DNS, firewall, rede administrativa ou serviço externo. Compatibilidade com serviços em uso, capacidade e custo ficam em qualificação operacional separada. Esta inspeção não autoriza uso sensível.
