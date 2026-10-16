# Controle de acesso: alternativas para a prova

**Spec:** [spec.md](spec.md). **Status: rota A escolhida para a prova isolada em 2026-10-16.** O proprietário orientou usar a solução mais simples e aproveitar o piloto SimpleX já realizado. Arquitetura de produção e integração iOS ainda dependem do resultado.

O proprietário aprovou os requisitos e a prova isolada. A [qualificação inicial](access-baseline.md) mostra por que senha de criação SMP/XFTP não basta para a retirada individual. Ambas as rotas abaixo precisam atender aos mesmos critérios aprovados; viabilidade depende do experimento.

## Architecture Overview

Recomendação para a primeira prova: **A, camada de acesso separada**, mantendo protocolo e criptografia de mensagens no núcleo SimpleX. A hipótese é reduzir alterações mantidas nos dois daemons enquanto testamos a fronteira de entrada. Não é uma promessa de que um proxy genérico resolva a integração iOS ou a revogação.

| Aspecto | A: camada de acesso separada | B: autorização dentro dos servidores |
| --- | --- | --- |
| Fronteira | Credencial por dispositivo autentica acesso ao transporte dos relays; acesso direto aos daemons precisa estar fechado | SMP/XFTP verificam associação individual em seus próprios caminhos de transporte/comandos |
| Revogação | Negar reconexões e encerrar sessões/fluxos dentro de 60 segundos | Verificar associação em comandos, entregas assíncronas e fluxos, cumprindo os mesmos 60 segundos |
| App | Adaptar e comprovar o caminho de rede do núcleo/app/extensões, preservando a validação TLS interna do relay | Adaptar núcleo/app para as credenciais e mecanismos aceitos pelos servidores modificados |
| Manutenção | Serviço adicional; menor divergência potencial nos daemons | Alterações coordenadas nos servidores e cliente, com risco maior nas atualizações upstream |
| Conteúdo | Não precisa ler o conteúdo das conversas | Mantém conteúdo ponta a ponta criptografado |
| Risco principal | Porta direta, sessão antiga ou caminho alternativo contorna a barreira | Operação esquecida, incompatibilidade de versão e manutenção de outro fork |
| Grupos oficiais | Autoridade do proprietário precisa ser validada além da UI; autenticação de transporte sozinha não basta | A mesma obrigação; não assumir que o relay interpreta o conteúdo dos grupos |
| Reversibilidade | Descartar protótipo isolado, sem alterar produção | Descartar patch experimental, sem alterar produção |

Certificado individual de cliente é um candidato a autenticação; ainda não existe decisão sobre credencial, emissão ou arquitetura final. Não criar protocolo criptográfico novo ou embutir segredo global no app público.

## Critérios do experimento autorizado

Começar em loopback e estado exclusivo do worktree, com dados fictícios. Após a escolha, detalhar componentes e tarefas para qualificar a rota selecionada. Usar núcleo/clientes/daemons fixados, dois convidados fictícios e destinos sob controle do experimento. Um serviço echo pode ajudar diagnóstico de transporte, mas não comprova mensagens SMP ou transferências XFTP.

Provar controle positivo ativo e negativos sem credencial/revogado; sessões novas e abertas; fluxo de arquivo em andamento; indisponibilidade da autorização; consumo único de convite; repetição; reinício; grupos oficiais; e ausência de tentativas a destino sentinela externo no cliente oficial. Distinguir transporte, admissão, protocolo real, iOS e VPS em resultados separados.

## Risks & Concerns

| Concern | Location | Impact | Mitigation |
| --- | --- | --- | --- |
| Senha só na criação | SimpleXMQ Messaging/Server.hs:1537–1542; FileTransfer/Server.hs:467–483 | Retirada aparente sem impedir operações existentes | Credencial individual e provas de sessões/fluxos existentes |
| Certificado confundido com membro ativo | Transport/Client.hs:131; Transport/Server.hs:274–287 | Chave válida sem associação autoriza acesso | Vínculo durável e consulta efetiva de estado, com prova de posse |
| Destinos herdados | Library/Internal.hs:1561/1603; APITypes.swift:267 | Tráfego fora da instância | Observação de tentativas em todos os caminhos; falha dos relays sem fallback |
| Grupo inferido do ciphertext | Messaging/Protocol.hs:590 | Promessa incompatível com privacidade do conteúdo | Autoridade dos grupos oficiais sem descriptografar conversas; declarar limites de software modificado |
| Biblioteca confundida com servidor | Artefatos ios-first-build | Prova sintética declarada real | Executáveis/cliente reais antes de declarar SMP/XFTP provados |

O proprietário autorizou a rota mais simples após a comparação A/B; adotamos A somente para o experimento delimitado abaixo. Não repetir o piloto inteiro do SimpleX. Nenhum deploy, DNS, credencial real, Mac mini, Tailscale ou Alfred será alterado por esse experimento.

## Desenho mínimo do experimento

Relays oficiais sem patches, executados somente em rede Docker interna. Uma ponte TLS de teste autentica certificado fictício por dispositivo, consulta uma lista local de associações e encaminha bytes ao único backend fixado para SMP ou XFTP. A lista é estado local do experimento, não um serviço de convites pronto. Rejeitar associação ausente e encerrar sessões quando a lista retirar o dispositivo ou ficar ilegível, dentro do limite aprovado de 60 segundos.

Os clientes de prova ficam em outra rede interna, sem acesso direto à rede dos relays. A ponte conecta as duas redes; não publica portas no MacBook. Um adaptador local de teste encapsula o transporte do cliente oficial, preservando TLS interno e conteúdo SimpleX. Isso qualifica o limite de transporte; não comprova que o app iOS e suas extensões já usam esse caminho.

Arquivos da ponte e do driver pertencem a tools/taverna/access_proof. Certificados, binários, listas, bancos e logs pertencem a .build/access-qualification, ignorado pelo Git. O binário de servidor vem da release v7.0.0 no mesmo SHA SimpleXMQ fixado no app. O cliente CLI oficial vem da release v7.0.0, SHA e11128ce; é cliente de interoperabilidade, não o binário iOS do fork.

A aprovação para esta prova cobre escolhas locais reversíveis de ferramenta e fixture. Critérios, mensagens reais de usuários, produção e configurações existentes não mudam.
