**Primeira versão de 64 bits do Unknown Horizons para Windows, com o código de 2026.** O último
instalador oficial é o 2019.1, de 32 bits. Pacote portátil feito pelo [Gameplay RTS](https://gameplayrts.com.br):
extraia e jogue, sem instalar nada.

## Como jogar

1. Baixe `UnknownHorizons-win-v1-win64.zip` e extraia numa pasta sua (Documentos, Área de Trabalho,
   Jogos). Não use "Arquivos de Programas": o jogo grava na própria pasta.
2. Dê dois cliques em **Jogar Unknown Horizons.bat**.
3. Na primeira vez, aparece a janela "Generating atlases!" por cerca de um minuto, enquanto o jogo
   prepara as texturas. Só acontece uma vez.

O jogo abre no idioma do Windows. Saves e configurações ficam em `Documentos\My Games\unknown-horizons`.

## O que vem no pacote

- O Unknown Horizons do ramo `master` oficial de novembro de 2026 (motor FIFE 0.5 com SDL3), mais as
  correções abaixo.
- Python 3.13 embutido, com Tcl/Tk e as bibliotecas do jogo. Não usa nem altera nenhum Python que
  você já tenha.
- Traduções compiladas para 46 idiomas, com o português do Brasil completo.

## Correções nossas

- **Tutorial em português do Brasil.** Antes, com o Windows em pt-BR, a interface saía em pt-BR mas o
  tutorial e o idioma pré-selecionado nos cenários eram o português de Portugal.
- **"Português Br." inteiro na lista de idiomas** dos cenários; antes ele aparecia cortado e igual a
  "Português".
- **O jogo abre sem janela de console** (pelo `pythonw.exe`); antes ele fechava sozinho, sem mensagem.

## Limitações

- **Sem multiplayer** nesta versão: a biblioteca de rede `pyenet` ainda não existe pronta para
  Python 3.13 no Windows.
- O Windows pode avisar que o arquivo `.bat` veio da internet. Ele só chama o Python que vem dentro da
  pasta; o conteúdo dele tem uma linha e pode ser conferido no Bloco de Notas.

## Verificação

Confira o download com o arquivo `.sha256` desta release:

```powershell
Get-FileHash .\UnknownHorizons-win-v1-win64.zip -Algorithm SHA256
```

Este pacote foi montado e testado pela pipeline do fork: motor compilado do código, testes unitários,
pacote extraído numa pasta limpa e jogo aberto até terminar 300 ciclos de um mapa aleatório.

## Código-fonte e licenças

- Fonte exato deste pacote: tag `win-v1` deste repositório (ramo `gameplayrts`).
- Jogo: GPL-2.0 ou posterior; arte e áudio próprios em CC BY-SA 3.0.
- Motor FIFE: LGPL-2.1 ou posterior. O wheel usado vai anexado nesta release e foi compilado do commit
  [`580e17d82`](https://github.com/fifengine/fifengine/commit/580e17d82d05097a4d6002f75b840681f17426ed)
  do FIFE, com a fifechan no commit
  [`b1a4b63ee`](https://github.com/fifengine/fifechan/commit/b1a4b63ee8eaaaf16188c48916522fd2f445258e).
- Detalhes de cada componente no `LICENCAS.txt` dentro do zip.

---

**English:** portable 64-bit Windows build of the current Unknown Horizons code (FIFE 0.5, Python 3.13
embedded). Extract and run `Jogar Unknown Horizons.bat`. Includes fixes for the system locale region
(pt_BR players got the European Portuguese tutorial), the scenario language list width and starting
under `pythonw.exe`. No multiplayer yet (`pyenet` has no Python 3.13 Windows build).
