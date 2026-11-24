# Unknown Horizons para Windows (fork do Gameplay RTS)

Este fork existe para uma coisa: **entregar o Unknown Horizons atual para quem joga no Windows**, num
pacote que abre com dois cliques, e devolver ao projeto oficial cada correção que aparecer no caminho.

O trabalho é documentado no blog [Gameplay RTS](https://gameplayrts.com.br), no laboratório de jogos de
estratégia de código aberto.

## Por que este fork

- O último instalador oficial para Windows é o **2019.1**, de 12/01/2019, só de 32 bits.
- O projeto ficou parado de dezembro de 2023 a fevereiro de 2026 e voltou com força: mais de 130
  commits em 2026, migração para o motor **FIFE 0.5** (que trocou o SDL2 pelo SDL3) e para o
  **Python 3.13**.
- Esse código novo não tinha nenhuma versão para Windows. Quem quisesse jogar precisava montar Python,
  motor e dependências na mão.

## O que o pacote entrega

Um zip portátil de 64 bits (cerca de 285 MB, 375 MB extraído), sem instalador e sem exigir nada
instalado na máquina:

| Pasta ou arquivo | Conteúdo |
|---|---|
| `Jogar Unknown Horizons.bat` | abre o jogo sem janela de console |
| `Unknown Horizons (depurar).bat` | abre com console e grava log, para relatar problemas |
| `python/` | Python 3.13 embutido, Tcl/Tk e as bibliotecas do jogo (FIFE, Pillow, PyYAML...) |
| `unknown-horizons/` | o jogo, com as traduções já compiladas (46 idiomas, pt-BR 100%) |
| `LEIA-ME.txt`, `LICENCAS.txt` | como jogar e a licença de cada componente |

Na primeira execução o jogo monta os atlas de texturas (um ou dois minutos, com a janela
"Generating atlases!"). Saves e configurações ficam em `Documentos\My Games\unknown-horizons`.

**Ainda não tem multiplayer:** a biblioteca de rede `pyenet` não existe pronta para Python 3.13 no
Windows. O modo de um jogador funciona completo.

## O que mudamos no jogo

Três correções, cada uma num commit próprio, todas testadas com o jogo rodando:

1. **Brasileiro recebia o tutorial em português de Portugal.** Com o idioma em "System default", o jogo
   cortava `pt_BR` para `pt`. Agora mantém a região quando existe tradução para ela (também vale para
   `zh_CN` e `zh_TW`). Com teste unitário. Ramo para o projeto oficial:
   `fix/system-locale-keep-region`.
2. **"Português Br." aparecia cortado** na lista de idiomas dos cenários e ficava igual a "Português".
   A coluna passou de 140 para 170 px. Ramo: `fix/sp-scenario-language-list-width`.
3. **O jogo não abria pelo `pythonw.exe`** (sem console): morria antes de criar a janela, sem mensagem
   nenhuma. Agora abre.

O ramo `gameplayrts` é o `master` oficial mais essas correções, o empacotamento (`packaging/windows/`)
e a pipeline (`.github/workflows/gameplayrts-windows.yml`).

## A pipeline

A cada mudança no ramo `gameplayrts`, o GitHub Actions:

1. **Compila o motor FIFE** a partir do código, num commit fixado do FIFE e da fifechan, e guarda o
   resultado em cache (só recompila quando o commit fixado muda).
2. **Roda os testes unitários** de idioma e traduções no Windows.
3. **Monta o pacote** com `packaging/windows/build_package.py`, o mesmo script usado à mão.
4. **Extrai o pacote numa pasta limpa e abre o jogo**: confere o SHA256, carrega as bibliotecas no
   Python embutido e joga 300 ciclos de um mapa aleatório, com OpenGL por software (Mesa) no runner.
   Um pacote que compila mas não abre não passa.
5. Numa tag `win-v*`, **cria a release em rascunho** com o zip, o SHA256 e o wheel do motor.

## Licenças e código-fonte

O jogo é GPL-2.0 ou posterior (arte e áudio próprios em CC BY-SA 3.0); o motor FIFE é LGPL-2.1 ou
posterior. Cada release aponta para a tag deste repositório com o fonte exato do pacote, e o wheel do
motor vai junto na release com o commit do FIFE de onde saiu.

---

## English summary

This fork ships the current (2026) Unknown Horizons code as a portable 64-bit Windows package: embedded
Python 3.13, FIFE 0.5 built from a pinned commit, translations compiled, no installer. The last
official Windows build was 2019.1 (32-bit). The `gameplayrts` branch is upstream `master` plus three
fixes (system locale region for pt_BR/zh_*, wider scenario language list, starting under
`pythonw.exe`), the packaging script and a CI pipeline that builds the engine, runs unit tests, builds
the package and actually starts the game from it on every change. The locale and layout fixes are on
their own branches, ready to be proposed upstream.
