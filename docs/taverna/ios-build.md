# Build iOS local da Taverna

Este procedimento compila a base do fork para simulador arm64, com o núcleo SimpleX real. A interface ainda é a herdada do SimpleX. A prova exige produtos reais, a navegação Get started → Your profile, os quatro métodos da suíte no perfil first-build e repetição em outro ambiente. Não cria perfil ou conversa.

Ambiente qualificado nesta entrega: MacBook arm64, Python 3.12, Xcode 27.1 (27A9275), SDK iOS Simulator 27.1, runtime iOS 27.0 (24A434) e iPhone 17. Nix 2.34.9 e o cache assinado foram autorizados em [APP-002/003](decisions/README.md). Nix/store e seus serviços são a exceção de sistema; o estado do projeto permanece em Projects. Outro SDK/macOS exige requalificação, especialmente do guard e das ferramentas nativas.

## Abrir uma sessão

Escolha o commit que será testado. Cada reprodução precisa da mesma revisão e manifesto, mas de branch, worktree, caches e UDID próprios. Não use produtos da primeira sessão para provar a segunda.

```bash
cd "$HOME/Projects/taverna-app"
taverna_revision="$(git rev-parse HEAD)"
git worktree add -b codex/6-ios-proof-author ../taverna-app-worktrees/ios-proof-author "$taverna_revision"
cd ../taverna-app-worktrees/ios-proof-author
```

Registre responsável, harness, branch e escopo no handoff ignorado ou na issue/PR. O integrador controla CI, locks e documentação compartilhada. Nas provas finais o checkout fica limpo; os comandos abaixo escrevem somente no estado ignorado. Licença/primeiro acesso do Xcode e instalação administrativa do Nix pertencem ao proprietário; estes comandos não aceitam contratos ou consultam contas Apple.

## Preparar o núcleo fixado

A referência imutável é o upstream 479548ee53ffb73db73841e77acbeee5a78dbbd5, com seus locks. A avaliação deve produzir a derivação registrada no [manifesto](../../.specs/features/ios-first-build/native-inputs.json). A saída imutável já construída neste MacBook pode ser reutilizada; isso não conta como nova compilação do núcleo. Em uma máquina fria, uma falha ou timeout continua sem aprovação e precisa de nova tentativa preservada.

```bash
python3.12 - <<'PY'
from pathlib import Path
import json, sys
root = Path.cwd(); sys.path.insert(0, str(root / 'tools/taverna'))
import ios_proof as p
m = json.loads((root / '.specs/features/ios-first-build/native-inputs.json').read_text())
a = p.session.new_attempt(root, 'native-source')
nix = '/nix/var/nix/profiles/default/bin/nix'
base = [nix, '--extra-experimental-features', 'nix-command flakes']
ref = 'github:simplex-chat/simplex-chat/' + m['upstream_commit']
attribute = '#packages.aarch64-darwin."aarch64-darwin-ios:lib:simplex-chat".drvPath'
args = base + ['eval', '--raw', '--no-write-lock-file', '--no-update-lock-file', '--keep-failed', '-L', '--option', 'allow-import-from-derivation', 'true', '--option', 'extra-substituters', 'https://cache.iog.io', ref + attribute]
r = p.record_stage(root, a, 'eval', args, 5400); p.validate_stage('eval', r)
drv = (a / 'eval.stdout.log').read_text().strip()
p.require(drv == m['core_derivation'], 'unexpected core derivation')
args = base + ['build', '--no-link', '--json', '--keep-failed', '-L', '--option', 'extra-substituters', 'https://cache.iog.io', '--max-jobs', '1', '--cores', '5', drv + '^out']
r = p.record_stage(root, a, 'realize', args, 5400); p.validate_stage('realize', r)
product = json.loads((a / 'realize.stdout.log').read_text())[0]
p.require(product['drvPath'] == drv, 'native output mismatch')
bundle = Path(product['outputs']['out']) / 'pkg-ios-aarch64-swift-json.zip'
args = [sys.executable, 'tools/taverna/ios_native.py', '--bundle', str(bundle), '--attempt', 'native']
r = p.record_stage(root, a, 'prepare', args, 5400); p.validate_stage('prepare', r)
PY
```

O preparador verifica origem, locks, licença, ZIP, ferramentas e todos os objetos. A conversão usa vtool por membro e libtool determinístico, preservando payload, símbolos, relocações e versões. Não escreve na store. O conjunto final tem cinco arquivos e 4.187 objetos arm64/platform 7; hashes divergentes impedem avançar. Não usar os scripts upstream que baixam versões móveis ou substituem Downloads compartilhado.

## Resolver os sete pacotes SwiftPM

O WebRTC é um binário do fornecedor, com checksum e receita fixados; não foi reconstruído localmente. O download abaixo é limitado, confere o ZIP conhecido e seus caminhos antes de resolver os mesmos pins do projeto. Os artefatos consumidos pelo SwiftPM também precisam bater com o manifesto.

```bash
python3.12 - <<'PY'
from pathlib import Path, PurePosixPath
import json, sys, zipfile, stat, posixpath, shutil
root = Path.cwd(); sys.path.insert(0, str(root / 'tools/taverna'))
import ios_proof as p
m = json.loads((root / '.specs/features/ios-first-build/native-inputs.json').read_text())
a = p.session.new_attempt(root, 'packages')
archive = a / 'WebRTC.zip'
url = 'https://github.com/simplex-chat/WebRTC/releases/download/110.0.0/WebRTC-M110.0.0.xcframework.zip'
args = ['curl', '--fail', '--silent', '--show-error', '--location', '--proto', '=https', '--proto-redir', '=https', '--max-time', '1800', '--max-filesize', '5368709120', '--output', str(archive), url]
r = p.record_stage(root, a, 'download', args, 1800); p.validate_stage('download', r)
p.require(p.sha256(archive) == m['webrtc']['received_sha256'], 'WebRTC checksum mismatch')
with zipfile.ZipFile(archive) as z:
    names = set()
    for entry in z.infolist():
        path = PurePosixPath(entry.filename)
        p.require(not path.is_absolute() and '..' not in path.parts and '\\' not in entry.filename and entry.filename not in names, 'unsafe ZIP path')
        names.add(entry.filename)
        if stat.S_ISLNK(entry.external_attr >> 16):
            target = z.read(entry).decode()
            normalized = posixpath.normpath(str(path.parent / PurePosixPath(target)))
            p.require(not PurePosixPath(target).is_absolute() and normalized != '..' and not normalized.startswith('../'), 'ZIP link escape')
lock = root / p.native.LOCK
before = p.sha256(lock)
p.require(before == m['swiftpm_lock_sha256'], 'changed package pins')
args = ['xcodebuild', '-resolvePackageDependencies', '-project', 'apps/ios/SimpleX.xcodeproj', '-scheme', 'SimpleX (iOS)', '-derivedDataPath', str(root / '.build/DerivedData')] + p.package_args(root) + p.session.build_cache_args(root)
r = p.record_stage(root, a, 'resolve', args, 1800); p.validate_stage('resolve', r)
p.require(p.sha256(lock) == before and len(json.loads(lock.read_text())['pins']) == 7, 'package pins changed')
webrtc = root / '.build/SourcePackages/artifacts/webrtc/WebRTC/WebRTC.xcframework/ios-x86_64_arm64-simulator/WebRTC.framework/WebRTC'
p.require(p.sha256(webrtc) == m['webrtc']['used_binary_sha256'], 'resolved WebRTC differs')
destination = root / 'apps/ios/Libraries/sim'
destination.mkdir(parents=True, exist_ok=True)
p.session.inside(root, destination)
bindings = dict(native_manifest_sha256=p.sha256(root / '.specs/features/ios-first-build/native-inputs.json'), libraries={}, webrtc_binary=str(webrtc))
for library in m['libraries']:
    source = root / '.build/attempts/native/sim' / library['name']
    target = destination / library['name']
    with source.open('rb') as original, target.open('xb') as output:
        shutil.copyfileobj(original, output)
    p.native.validate_library(target, library)
    bindings['libraries'][library['name']] = str(target)
with (root / '.build/native-input-bindings.json').open('x') as output:
    json.dump(bindings, output, indent=2)
PY
```

Downloads de artefatos têm teto de 5 GiB/30 minutos. O ZIP local do núcleo é produto Nix, não download de uma biblioteca oficial pré-compilada. O cache do Nix mantém sua verificação de assinaturas; o comando apenas seleciona o cache já autorizado, sem mudar a configuração global.

## Provar o destino e a contenção

```bash
python3.12 tools/taverna/ios_session.py create --owner Codex-author --runtime com.apple.CoreSimulator.SimRuntime.iOS-27-0 --device-type com.apple.CoreSimulator.SimDeviceType.iPhone-17
python3.12 tools/taverna/ios_session.py guard --attempt guard
python3.12 tools/taverna/ios_session.py control --attempt control --guard-manifest .build/attempts/guard/guard-manifest.json
```

Se duas sessões executarem em paralelo, registrem ambos os UDIDs antes de qualquer teste. O executor recusa novos destinos surgidos durante sua suíte.

O controle UIKit próprio é uma prova do ambiente. A prova da Taverna vem depois. Cada UDID fica registrado no índice padrão do SDK, com dados/logs físicos no worktree e aliases por UDID, conforme [APP-004](decisions/README.md). Não usar um set privado como se o Xcode o selecionasse.

O guard contém IP remoto no processo do app antes do main e permite loopback. Os serviços do iOS ficam fora dessa contenção. Os testes exigem prova de negação IPv4/IPv6 a cada lançamento, sem mudar VPN ou firewall global. Não há envio de formulário, criação de perfil ou conversa.

## Compilar, testar e validar

```bash
python3.12 tools/taverna/ios_proof.py build --attempt build --guard-manifest .build/attempts/guard/guard-manifest.json
python3.12 tools/taverna/ios_proof.py test --build-attempt .build/attempts/build --attempt tests --guard-manifest .build/attempts/guard/guard-manifest.json --ui-profile first-build
python3.12 tools/taverna/ios_proof.py --build-attempt .build/attempts/build --test-attempt .build/attempts/tests --native-attempt .build/attempts/native --attempt proof --require-clean
```

O build usa Debug/arm64 e assinatura ad hoc, com DEVELOPMENT_TEAM vazio. O limite agregado é 90 minutos para build e 60 para a suíte, conforme a revisão operacional registrada no [plano](../../.specs/features/ios-first-build/spec.md). Get started e Your profile mantêm 30 segundos cada. O perfil first-build foi aprovado pelo proprietário: inglês, portrait e light, os três métodos herdados e o novo onboarding, todas as asserções e zero skips. A métrica de lançamento continua executando suas medições. O perfil full-matrix mantém a expansão herdada de configurações e permanece pendente; selecione --ui-profile full-matrix em uma tentativa/simulador novos para executá-lo. As tentativas integrais anteriores venceram o prazo e não foram aprovadas. Não somar suas execuções para alegar conclusão.

A prova lê os executáveis de app, framework, NSE e Share Extension, as assinaturas, símbolos nativos, hashes e resultados reais do xcresult. Registra métodos lógicos e execuções expandidas do console. Comando com exit 0 e suíte vazia/parcial, artefato ausente ou etapa com timeout não aprovam o resultado. `--allow-dirty` serve somente à exploração local; não pode substituir as reproduções limpas.

## Repetir e comparar

O Verifier independente usa outro worktree/branch e UDID do mesmo commit, com a mesma receita e manifesto. Repete todo o procedimento, sem compartilhar DerivedData, SourcePackages, caches graváveis ou dados de simulador. Somente a store imutável Nix pode ser reutilizada.

Depois de obter dois receipts `proof/receipt.json` bem-sucedidos:

```bash
python3.12 tools/taverna/ios_proof.py compare --first /caminho/da/prova-A/.build/attempts/proof/receipt.json --second /caminho/da/prova-B/.build/attempts/proof/receipt.json --attempt comparison
```

Substitua os caminhos pelos dois worktrees reais em Projects. O comparador recusa commits/manifestos/perfis diferentes, fonte sujo, falha, mesmo UDID ou mesmo armazenamento físico. A entrega exige também CI no commit de implementação e o [Verifier TLC](../../.agents/skills/tlc-spec-driven/SKILL.md), com falhas injetadas em cópia isolada. Relatórios posteriores identificam esse SHA, sem substituir a fonte testada.

## Interpretar e retomar

`PASS` local do build/suíte, origem do núcleo e assinatura/push em aparelho são estados separados. O simulador não comprova APNs, distribuição, entrega de mensagens ou segurança ponta a ponta. Identidade Taverna, assets e licença de distribuição continuam com seus [gates próprios](assets.md).

Os receipts, stdout/stderr, dados de simulador, screenshots e xcresult ficam em `.build`, ignorados pelo Git. O relatório público é textual. Nunca publicar arquivos de mensagens, perfis, chaves, screenshots ou URLs temporárias de download.

Uma tentativa existente nunca é sobrescrita. Em falha, preserve o código/saídas e crie outra tentativa ou worktree. Se o app já tiver dados, crie novo UDID próprio; não apague os anteriores para passar no teste. O encerramento desliga apenas o dispositivo da própria tentativa.

Antes de remover um worktree, confira conflitos, commits não integrados, arquivos locais e aliases do SDK que apontam para ele. Pendências exigem reconciliação; não usar limpeza forçada nem remover dispositivos de outra sessão. O preflight F0 continua sendo inventário de ferramentas; a prova F1 vem destes artefatos, não de instalar ferramentas.
