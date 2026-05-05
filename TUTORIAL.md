# Tutorial — SCED Localization

Guia completo para traduzir cartas do Arkham Horror LCG para uso no Tabletop Simulator (TTS).

---

## Visão Geral do Pipeline

O processo é dividido em 5 etapas sequenciais:

| Etapa | Nome | O que faz |
|-------|------|-----------|
| 1 | `translate` | Baixa dados do ArkhamDB e SCED, corta imagens das cartas e gera CSVs para o Strange Eons |
| 2 | `generate` | Renderiza as imagens das cartas no Strange Eons usando os CSVs |
| 3 | `pack` | Monta as deck sheets (imagens de grade) no formato do TTS |
| 4 | `upload` | Faz upload das deck sheets para o Google Drive |
| 5 | `update` | Atualiza os arquivos do mod SCED com as novas URLs das imagens traduzidas |

---

## Pré-requisitos

### 1. Python (Anaconda)
- Instale o [Anaconda](https://www.anaconda.com/download)
- Ative o ambiente conda antes de rodar qualquer comando:
  ```bash
  conda activate base
  ```

### 2. Dependências Python
Na pasta do projeto, instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

### 3. Strange Eons
- Baixe e instale o [Strange Eons](https://cgjennings.ca/eons/)
- Instale o plugin **Arkham Horror LCG** dentro do Strange Eons
  - Menu: **Toolbox → Manage Plugins → Catalog**
  - Busque por "Arkham Horror" e instale

### 4. Git
- Necessário para clonar automaticamente os repositórios do SCED e ArkhamDB
- Instale via [git-scm.com](https://git-scm.com)

### 5. Google Drive (apenas para etapa de upload)
- Uma conta Google com espaço suficiente
- Uma **Service Account** no Google Cloud com acesso à Drive API
- Um arquivo de credenciais JSON da Service Account
- O ID da pasta no Google Drive onde as imagens serão salvas

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/EsleyHenri/SCED_Localization.git
cd SCED_Localization

# Mude para o branch de desenvolvimento
git checkout claude/arkham-cards-tts-format-yarq4

# Instale dependências
pip install -r requirements.txt
```

---

## Configuração — `run.py`

O arquivo `run.py` é o ponto de entrada principal. Edite-o para escolher o idioma e as expansões a processar.

### Idioma
```python
LANG = 'pt'   # Português
```

Idiomas disponíveis: `pt`, `es`, `de`, `fr`, `it`, `ko`, `pl`, `ru`, `uk`, `zh_TW`, `zh_CN`

### Expansões
Cada expansão está listada como uma linha. Remova o `#` para incluir, adicione `#` para excluir:

```python
PACKS = [
    'core', 'rcore',       # Core Set / Revised Core Set — ATIVO
  # 'dwl',                 # The Dunwich Legacy — INATIVO
  # 'core_2026',           # Core Set 2026 — INATIVO
]
```

---

## Executando o Pipeline

### Rodando todas as etapas de uma vez
```bash
python run.py
```

### Rodando uma etapa específica
```bash
python run.py --step translate   # Etapa 1: baixar dados e gerar CSVs
python run.py --step generate    # Etapa 2: renderizar no Strange Eons
python run.py --step pack        # Etapa 3: montar deck sheets
python run.py --step upload      # Etapa 4: fazer upload para o Google Drive
python run.py --step update      # Etapa 5: atualizar arquivos do mod
```

---

## Etapa 1 — `translate`

**O que acontece:**
1. Clona automaticamente os repositórios `argonui/SCED` e `Chr1Z93/SCED-downloads` (na primeira execução)
2. Baixa os dados de cartas do `Kamalisk/arkhamdb-json-data` e gera `cache/ahdb/pt.json`
3. Para cada carta filtrada pelas expansões selecionadas:
   - Baixa a deck sheet original (imagem JPG) do Google Drive do SCED para `cache/decks/{pack_code}/`
   - Corta a imagem individual da carta para `cache/cards/{pack_code}/`
4. Gera os arquivos CSV em `SE_Generator/data/{pack_code}/` para cada tipo de carta

**Estrutura de saída:**
```
cache/
  ahdb/pt.json              ← dados de todas as cartas em PT
  decks/{pack_code}/*.jpg   ← deck sheets originais baixadas
  cards/{pack_code}/*.png   ← cartas individuais cortadas
SE_Generator/
  data/{pack_code}/*.csv    ← dados para o Strange Eons
```

**Forçar re-download dos dados do ArkhamDB** (quando houver novas traduções):
```bash
# Atualizar o repositório local
git -C repos/arkhamdb-json-data pull

# Deletar o cache para reprocessar
rm cache/ahdb/pt.json
```

---

## Etapa 2 — `generate`

**O que acontece:**
- O Strange Eons é executado em modo headless
- Para cada pack, lê os CSVs de `SE_Generator/data/{pack_code}/`
- Renderiza as imagens das cartas com o texto traduzido
- Salva as imagens em `SE_Generator/images/{pack_code}/`

**Requisito:** Strange Eons instalado com o plugin Arkham Horror LCG.

**Caminhos padrão do Strange Eons:**
- macOS: `/Applications/Strange Eons.app/Contents/Resources/app/bin/eons`
- Windows: `C:\Program Files\Strange Eons\bin\eons.exe`

**Caso o executável esteja em outro local:**
```bash
python run.py --step generate --se-executable "/caminho/para/eons"
```

---

## Etapa 3 — `pack`

**O que acontece:**
- Lê as imagens renderizadas de `SE_Generator/images/{pack_code}/`
- Monta as deck sheets no formato de grade exigido pelo TTS
- Salva as deck sheets traduzidas em `decks/{lang}/{url_id}.jpg`

**Estrutura de saída:**
```
decks/
  pt/
    {url_id}.jpg   ← deck sheets traduzidas prontas para upload
```

---

## Etapa 4 — `upload`

**O que acontece:**
- Faz upload das deck sheets de `decks/{lang}/` para uma pasta no Google Drive
- Registra as novas URLs no arquivo `cache/urls.json`
- Arquivos existentes são sobrescritos mantendo o mesmo link (sem quebrar mods salvos)

**Configuração necessária:**
```bash
python run.py --step upload \
  --gdrive-credentials /caminho/para/credentials.json \
  --gdrive-folder-id ID_DA_PASTA_NO_DRIVE
```

**Para obter o ID da pasta:** abra a pasta no Google Drive no navegador — o ID é a parte final da URL:
```
https://drive.google.com/drive/folders/ESTE_E_O_ID
```

**Forçar novos links** (caso queira URLs novas em vez de sobrescrever):
```bash
python run.py --step upload --new-link ...
```

---

## Etapa 5 — `update`

**O que acontece:**
- Lê os arquivos do mod SCED em `repos/SCED-downloads/decomposed/`
- Substitui as URLs originais dos campos `FaceURL`/`BackURL` pelas URLs traduzidas do `cache/urls.json`
- Salva os arquivos modificados de volta no repositório local do SCED-downloads

Após esta etapa, os arquivos do mod estão prontos para serem carregados no TTS.

---

## Argumentos Avançados

Todos os argumentos podem ser passados via `run.py` e serão repassados ao `main.py`:

```bash
python run.py --step translate --mod-dir-primary ~/meu/SCED
```

| Argumento | Padrão | Descrição |
|-----------|--------|-----------|
| `--lang` | `pt` (definido no run.py) | Idioma de destino |
| `--step` | (todos) | Etapa específica a executar |
| `--filter` | `True` | Filtro Python para selecionar cartas |
| `--cache-dir` | `cache` | Pasta de cache intermediário |
| `--decks-dir` | `decks` | Pasta das deck sheets traduzidas |
| `--repo-dir` | `repos` | Pasta dos repositórios clonados |
| `--ahdb-dir` | `repos/arkhamdb-json-data` | Repositório do ArkhamDB |
| `--mod-dir-primary` | `repos/SCED` | Repositório principal do SCED |
| `--mod-dir-secondary` | `repos/SCED-downloads` | Repositório SCED-downloads |
| `--se-executable` | (detectado) | Caminho do executável do Strange Eons |
| `--gdrive-credentials` | — | Arquivo JSON de credenciais do Google Drive |
| `--gdrive-folder-id` | — | ID da pasta de destino no Google Drive |
| `--new-link` | `false` | Criar novos links no upload |

### Filtro personalizado
Processa apenas uma carta específica pelo código:
```bash
python run.py --step translate --filter "card.get('code') == '01001'"
```

Processa apenas cartas de investigador:
```bash
python run.py --step translate --filter "card.get('type_code') == 'investigator'"
```

---

## Estrutura de Pastas

```
SCED_Localization/
├── run.py                      ← ponto de entrada (configure aqui)
├── main.py                     ← pipeline principal
├── translations/
│   └── pt/                     ← módulos de transformação para PT
├── SE_Generator/
│   ├── data/{pack_code}/*.csv  ← gerado na etapa translate
│   ├── images/{pack_code}/*.png← gerado na etapa generate
│   ├── template/*.eon          ← templates do Strange Eons
│   └── make.js                 ← script de automação do Strange Eons
├── cache/
│   ├── ahdb/pt.json            ← dados combinados do ArkhamDB
│   ├── decks/{pack_code}/*.jpg ← deck sheets originais
│   └── cards/{pack_code}/*.png ← cartas individuais cortadas
├── decks/
│   └── pt/*.jpg                ← deck sheets traduzidas (saída final)
└── repos/
    ├── arkhamdb-json-data/     ← clone do ArkhamDB
    ├── SCED/                   ← clone do mod principal
    └── SCED-downloads/         ← clone do SCED-downloads
```

---

## Atualização do Código

Para baixar as últimas correções e melhorias:

```bash
cd ~/Downloads/ARKHAM/SCED_Localization
git pull origin claude/arkham-cards-tts-format-yarq4
```

---

## Problemas Comuns

### `ModuleNotFoundError`
O Python usado não é o do conda. Ative o ambiente antes de rodar:
```bash
conda activate base
python run.py
```

### `KeyError` em `encounter_map` ou `pack_map`
Uma expansão nova tem conjuntos de encontro ou pack codes não mapeados. Reporte o erro para que o mapeamento seja adicionado.

### `OSError: image file is truncated`
O arquivo de cache de uma deck sheet foi corrompido (download incompleto). O pipeline detecta e re-baixa automaticamente na próxima execução.

### `fatal: refusing to merge unrelated histories`
Você está tentando fazer merge de repositórios sem histórico em comum. Use:
```bash
git merge upstream/master --allow-unrelated-histories
```

### Traduções não atualizadas
O cache do ArkhamDB não é atualizado automaticamente. Para forçar:
```bash
git -C repos/arkhamdb-json-data pull
rm cache/ahdb/pt.json
```
