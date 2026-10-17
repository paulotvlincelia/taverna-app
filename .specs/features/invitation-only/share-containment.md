# Contenção da fixture Share Extension

2026-10-17. Qualificação de T4, NP-04/07/08. Este documento registra a instrumentação de teste; não altera os critérios aprovados nem declara autorização de produto ou isolamento pelo kernel.

## Execução e limite

A prova abre UIActivityViewController pelo app de controle DEBUG e seleciona a extensão instalada na folha do sistema. O callback de ShareViewController executa no processo SimpleX SE; chamar esse controlador dentro do app não satisfaz o gate. O driver exige processo/PID, recibo anterior ao main, configuração lida do núcleo, protocolos reais, sentinela e resultado XCTest sem falhas ou skips.

O mecanismo do primeiro build permanece inalterado no app principal: host-sandbox aplica a política do kernel antes de exec. Na extensão, essa transição executou o controle anterior ao main, mas invalidou a requisição do serviço UIKit; viewDidLoad não foi alcançado. Repetir a seleção não qualificou o lifecycle. Essas tentativas falharam. Um controle separado sem o trampoline chegou ao callback, registrou somente UI_CONTROL_ONLY e não iniciou o núcleo; o driver corretamente o recusou como PASS.

Para a fixture da extensão, o modo explícito socket-test instrumenta connect, connectx, sendto e sendmsg via interposição dyld. Antes do main, permite Unix/loopback e nega destinos IPv4/IPv6 externos. O recibo identifica test_socket_interposition; não define o marcador de sandbox do kernel. Configuração e seleção pertencem ao checkout e somente existem em DEBUG Simulator; nenhum seletor ou construtor é compilado em aparelho/release.

A instrumentação cobre essas chamadas nos binários fixados; não impede syscalls diretas, descritores herdados ou operações delegadas a serviços do sistema. Não é uma prova de isolamento de toda a sessão iOS, nem substitui autenticação, mTLS, validação interna dos relays ou política SOCKS. Dados, CA, chaves e relays são fictícios e exclusivos da rodada. Não se autoriza conteúdo real com base neste mecanismo.

A sentinela usa um endereço loopback fora das duas rotas autorizadas. O controle positivo a alcança. Como o filtro permite loopback, ele não esconde um fallback direto para esse destino: as tentativas SMP/XFTP pelo núcleo devem falhar e o contador deve permanecer em uma conexão. As provas de componente e do app preservam ainda autenticação por processo, TLS, revogação e indisponibilidade da autoridade.

## Suítes independentes e ordem observável

A qualificação usa o target/scheme Taverna Share Qualification, sem OnlyTestIdentifiers ou SkipTestIdentifiers. O target Tests iOS e seu scheme mantêm os quatro métodos originais; TavernaUITestSession é um único helper compartilhado, extraído sem mudar suas asserções. O driver compila o scheme de qualificação com o comando e bindings do build de base, exige os quatro produtos inalterados e registra também o hash do binário do teste. Não filtra a suíte first-build para obter um PASS Share.

O observer DEBUG Simulator no encoder SEChatCommand.cmdString lê a resposta bruta de /network enquanto o dispatcher real serializa start/activate, antes da chamada C. Não altera comandos nem fornece respostas falsas. A prova exige política gerenciada e socksMode=always bruto nas duas fronteiras, além do readback posterior. Isso detecta configuração aplicada depois do início ou reativação; um readback posterior sozinho não comprovaria a ordem.

## Ordem comprovada pela prova

1. Sem transporte, o modelo não cria controlador; start/activate são recusados e o núcleo permanece parado.
2. Com configuração fictícia, o modelo real inicia; o núcleo devolve a configuração obrigatória, incluindo socksMode=always, sem persistir a capability.
3. Os testes reais SMP/XFTP passam pelo gateway autorizado; destinos sentinela são recusados sem conexão direta.
4. Durante suspensão, uma configuração insegura anterior é inserida como falha controlada. A retomada pelo modelo real deve substituí-la pela política gerenciada.
5. Após stop do núcleo e transporte, start/activate são recusados e o núcleo continua parado.

O build de quatro produtos, as regressões e a repetição limpa são gates adicionais. O Verifier independente deve revisar a adequação desta contenção e executar o sensor de autorização antes de aprovar o recorte Share. T4 inteira permanece aberta até a execução efetiva da NSE; T6 e os oito critérios agregados não recebem PASS parcial.

## Comando da prova

Após build limpo com o guard-manifest qualificado, informar seus caminhos relativos ao worktree:

```sh
TAVERNA_SHARE_SOCKET_TEST=1 TAVERNA_NATIVE_GUARD=.build/attempts/guard-share-b/guard-manifest.json TAVERNA_NATIVE_BUILD=.build/attempts/share-isolated-clean/receipt.json python3.12 tools/taverna/native_access_tests/test_share.py
```

O driver usa fixture nova, compara hashes dos quatro produtos, SHA/estado do checkout e vinte e dois checkpoints, confere os logs autorizados dos dois protocolos e a sentinela. Os recibos e xcresult ficam em .build/access-qualification/run-share-*/ios. O encerramento remove somente o pedido da própria rodada, seu processo de extensão e os containers/redes nomeados; preserva os arquivos de evidência. Um build com allow-dirty serve somente ao desenvolvimento e não comprova o gate final limpo.
