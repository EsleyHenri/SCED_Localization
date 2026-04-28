#!/usr/bin/env python3
"""
Edite a lista PACKS abaixo para escolher quais expansões traduzir.
  - Remova o '#' para incluir uma expansão
  - Adicione '#' para excluir

Uso:
    python run.py                    # executa todos os passos
    python run.py --step translate   # apenas baixar e preparar
    python run.py --step generate    # apenas renderizar no Strange Eons
    python run.py --step pack        # apenas empacotar decks
    python run.py --step upload      # apenas fazer upload
    python run.py --step update      # apenas atualizar mod

Argumentos extras são repassados diretamente para main.py, por exemplo:
    python run.py --step translate --mod-dir-primary ~/Downloads/ARKHAM/SCED
"""

import subprocess
import sys

# ── Idioma ────────────────────────────────────────────────────────────────────
LANG = 'pt'

# ── Expansões ─────────────────────────────────────────────────────────────────
# Remova o '#' para incluir uma expansão no processamento.
PACKS = [

    # ── Core Set ──────────────────────────────────────────────────────────────
    'core', 'rcore',                    # Core Set / Revised Core Set

    # ── The Dunwich Legacy ────────────────────────────────────────────────────
  # 'dwl',                              # The Dunwich Legacy
  # 'tmm',                              # The Miskatonic Museum
  # 'tece',                             # The Essex County Express
  # 'bota',                             # Blood on the Altar
  # 'uau',                              # Undimensioned and Unseen
  # 'wda',                              # Where Doom Awaits
  # 'litas',                            # Lost in Time and Space

    # ── The Path to Carcosa ───────────────────────────────────────────────────
  # 'ptc',                              # The Path to Carcosa
  # 'eotp',                             # Echoes of the Past
  # 'tuo',                              # The Unspeakable Oath
  # 'apot',                             # A Phantom of Truth
  # 'tpm',                              # The Pallid Mask
  # 'bsr',                              # Black Stars Rise
  # 'dca',                              # Dim Carcosa

    # ── The Forgotten Age ─────────────────────────────────────────────────────
  # 'tfa',                              # The Forgotten Age
  # 'tof',                              # Threads of Fate
  # 'tbb',                              # The Boundary Beyond
  # 'hote',                             # Heart of the Elders
  # 'tcoa',                             # The City of Archives
  # 'tdoy',                             # The Depths of Yoth
  # 'sha',                              # Shattered Aeons

    # ── The Circle Undone ─────────────────────────────────────────────────────
  # 'tcu',                              # The Circle Undone
  # 'tsn',                              # The Secret Name
  # 'wos',                              # The Wages of Sin
  # 'fgg',                              # For the Greater Good
  # 'uad',                              # Union and Disillusion
  # 'icc',                              # In the Clutches of Chaos
  # 'bbt',                              # Before the Black Throne

    # ── The Dream-Eaters ──────────────────────────────────────────────────────
  # 'tde',                              # The Dream-Eaters
  # 'sfk',                              # The Search for Kadath
  # 'tsh',                              # A Thousand Shapes of Horror
  # 'dsm',                              # Dark Side of the Moon
  # 'pnr',                              # Point of No Return
  # 'wgd',                              # Where the Gods Dwell
  # 'woc',                              # Weaver of the Cosmos

    # ── The Innsmouth Conspiracy ──────────────────────────────────────────────
  # 'tic',                              # The Innsmouth Conspiracy
  # 'itd',                              # In Too Deep
  # 'def',                              # Devil Reef
  # 'lif',                              # A Light in the Fog
  # 'hhg',                              # Horror in High Gear
  # 'lod',                              # The Lair of Dagon
  # 'itm',                              # Into the Maelstrom

    # ── Edge of the Earth ─────────────────────────────────────────────────────
  # 'eoec',                             # Campaign Expansion
  # 'eoep',                             # Investigator Expansion

    # ── The Scarlet Keys ──────────────────────────────────────────────────────
  # 'tskc',                             # Campaign Expansion
  # 'tskp',                             # Investigator Expansion

    # ── The Feast of Hemlock Vale ─────────────────────────────────────────────
  # 'fhvc',                             # Campaign Expansion
  # 'fhvp',                             # Investigator Expansion

    # ── The Drowned City ──────────────────────────────────────────────────────
  # 'tdcc',                             # Campaign Expansion
  # 'tdcp',                             # Investigator Expansion

    # ── Return to... ──────────────────────────────────────────────────────────
  # 'rtnotz',                           # Return to the Night of the Zealot
  # 'rtdwl',                            # Return to the Dunwich Legacy
  # 'rtptc',                            # Return to the Path to Carcosa
  # 'rttfa',                            # Return to the Forgotten Age
  # 'rttcu',                            # Return to the Circle Undone

    # ── Investigadores Avulsos ────────────────────────────────────────────────
  # 'nat',                              # Nathaniel Cho
  # 'har',                              # Harvey Walters
  # 'win',                              # Winifred Habbamock
  # 'jac',                              # Jacqueline Fine
  # 'ste',                              # Stella Clark

    # ── Side Stories ──────────────────────────────────────────────────────────
  # 'cotr',                             # Curse of the Rougarou
  # 'coh',                              # Carnevale of Horrors
  # 'guardians',                        # Guardians of the Abyss
  # 'hotel',                            # Murder at the Excelsior Hotel
  # 'blob', 'blbe',                     # The Blob That Ate Everything
  # 'wog',                              # War of the Outer Gods
  # 'lol',                              # The Labyrinths of Lunacy
  # 'fof',                              # Fortune and Folly
  # 'mtt',                              # Machinations Through Time
  # 'tmg',                              # The Midwinter Gala
  # 'film_fatale',                      # Film Fatale

    # ── Cenários Paralelos / Standalone ──────────────────────────────────────
  # 'enc',                              # Enthralling Encore
  # 'rod',                              # Read or Die
  # 'rtr',                              # Red Tide Rising
  # 'aon',                              # All or Nothing
  # 'bad',                              # Bad Blood
  # 'rop',                              # Relics of the Past
  # 'aof',                              # Aura of Faith
  # 'btb',                              # By the Book
  # 'hfa',                              # Hunting for Answers
  # 'ltr',                              # Laid to Rest
  # 'otr',                              # On the Road Again
  # 'pap',                              # Pistols and Pearls
  # 'ptr',                              # Path of the Righteous

    # ── Promocionais ──────────────────────────────────────────────────────────
  # 'hoth',                             # Hour of the Huntress
  # 'iotv',                             # Ire of the Void
  # 'tdg',                              # The Deep Gate
  # 'tdor',                             # The Dirge of Reason
  # 'tftbw',                            # To Fight the Black Wind
  # 'bob',                              # Blood of Baalshandor
  # 'dre',                              # Dark Revelations
  # 'promo',                            # Promo

]
# ─────────────────────────────────────────────────────────────────────────────

if not PACKS:
    print('Nenhuma expansão selecionada. Edite run.py e remova o "#" de pelo menos uma linha.')
    sys.exit(1)

filter_expr = f"card.get('pack_code') in {PACKS!r}"
cmd = [sys.executable, 'main.py', '--lang', LANG, '--filter', filter_expr] + sys.argv[1:]

print(f'Expansões selecionadas: {PACKS}')
print()
subprocess.run(cmd)
