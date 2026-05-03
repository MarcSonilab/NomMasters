# NomsMasters — Especificació de disseny
**Data:** 2026-05-03  
**Tecnologia:** Python 3.11+ · PyQt6 · PyInstaller (executable portable .exe)

---

## Visió general

NomsMasters és una eina d'escriptori per a professionals de postproducció audiovisual que gestionen lliuraments de màsters. Implementa la convenció de nomenclatura de MASTERS.docx en tres funcionalitats: generació de noms, desxifrat de noms, i renombrat per lots.

La finestra principal té tres pestanyes: **① Crear noms**, **② Desxifrar nom**, **③ Renombrar per lots**.

---

## Convenció de nomenclatura

Format canònic:
```
REF-N-TITOL-N-FMT[_TMP[_EPI]]-PRF-IDI-VER-VIS-L-TA_CN-VXX[.ext]
```

| Segment | Descripció | Valors possibles |
|---------|-----------|-----------------|
| `REF` | Codi intern del projecte | Text lliure, ex: `1983`, `C0042` |
| `TITOL` | Títol normalitzat | Text: espais→`_`, tot en majúscules |
| `FMT` | Tipus de referència | `FTR` / `TLR` / `SPT` / `SER` |
| `TMP` | Temporada (només SER) | `S01`…`S99` |
| `EPI` | Episodi (només SER) | `E0001`…`E9999` |
| `PRF` | Perfil / destí | `MASTER` / `BR` / `DCP` / `SD` |
| `IDI` | Idioma | Codi de 2-3 lletres: `ES`, `EN`, `CA`, `EU`, `FR`, `RU`, `ZH`, `JA`, `NO`, `CS`, `XX` |
| `VER` | Versió lingüística | `ORG` (pinnejat) / `ALT` (seleccionat) |
| `VIS` | Estat visual | `XXX` / `GRA` / `INT` / `SBT` / `GRA_INT` / `GRA_SBT` |
| `L` | Longitud | `S` (Short) / `L` (Long) |
| `TA` | Tipus d'àudio | `MIX` / `ME` / `DX` / `XXX` (vídeo) |
| `CN` | Canals | `1` / `2_0` / `5_1` / `7_1_4` |
| `VXX` | Versió del fitxer | `V01`…`V99` |
| `.ext` | Extensió | `.mov` (vídeo) / `.wav` (àudio) |

**Separadors:**
- Entre REF i TITOL: `-N-`
- Entre TITOL i FMT: `-N-`
- Entre la resta de segments: `-`
- FMT_TMP_EPI units amb `_`: ex `SER_S01_E0001`
- TA i CN units amb `_`: ex `MIX_2_0`, `MIX_5_1`

---

## Pestanya ① — Crear noms

### Camps del formulari

#### REF — Referència
- Camp de text lliure (QLineEdit)
- No es normalitza (l'usuari controla el valor exacte)

#### TÍTOL
- Camp de text (QLineEdit)
- **Normalització automàtica en perdre el focus** (`editingFinished`):
  - Elimina espais al principi i final (`.strip()`)
  - Substitueix seqüències d'espais per `_`
  - Converteix tot a majúscules
- Exemple: `"baba yaga y el libro"` → `"BABA_YAGA_Y_EL_LIBRO"`

#### FMT — Tipus de referència
- Selecció única (radio buttons estilitzats com a pills)
- Valors: `FTR` | `TLR` | `SPT` | `SER`
- Per defecte: `FTR`
- Tooltips: FTR=Feature, TLR=Tràiler, SPT=Spot, SER=Sèrie
- Quan s'activa `SER`: s'habiliten els camps TMP i EPI
- Quan s'activa qualsevol altre: s'inhabiliten TMP i EPI (aparença grisada, no editables)

#### TMP / EPI — Temporada i Episodis (mode SER)
- Inline a la mateixa fila que FMT
- **Temporada**: QSpinBox, rang 1–99, mostra com `S01` (zero-padded 2 dígits)
- **Episodi des de**: QSpinBox, rang 1–9999
- **Episodi fins a**: QSpinBox, rang 1–9999, ha de ser ≥ "des de"
- Quan FMT ≠ SER: camps inhabilitats visualment (opacity reduïda)

#### PRF — Perfil / Destí
- Selecció múltiple (pills/checkboxes)
- Valors: `MASTER` | `BR` | `DCP` | `SD`
- Mínim 1 seleccionat per generar noms
- Ample automàtic (no expandeix per omplir la fila)

#### IDI — Idiomes (sistema de 3 estats)
- Botons individuals per idioma: `ES EN CA EU FR RU ZH JA NO CS XX`
- Cada botó té **3 estats** que ciclen amb cada clic:
  1. **Gris** (no seleccionat): no inclòs als noms generats
  2. **Verd** (seleccionat = ALT): inclòs, VER=`ALT`
  3. **Taronja** (pinnejat = ORG): inclòs, VER=`ORG`
- **Restricció:** màxim 2 botons en estat PIN simultàniament
  - Si ja hi ha 2 pins i l'usuari intenta passar a pin un tercer botó (des d'estat verd), va directament a gris
- **VER és automàtic:** no hi ha camp VER al formulari; es deriva de l'estat IDI
- Nota visual: `■ Verd = ALT · ■ Taronja = ORG · Màx. 2 pins`
- Tooltips: nom complet de l'idioma

#### VIS — Estat visual (vídeo)
- Selecció múltiple (pills/checkboxes)
- Valors: `XXX` | `GRA` | `INT` | `SBT` | `GRA_INT` | `GRA_SBT`
- Tooltips descriptius per cada valor
- **Nota:** per a noms d'àudio, VIS sempre és `XXX` automàticament (independent del que l'usuari hagi seleccionat)

#### Longitud (L/S)
- Selecció única: `Short` | `Long` (genera `S` o `L` al nom)
- Per defecte: `Short`

#### Versió de fitxer (VXX)
- QSpinBox, rang 1–99
- Per defecte: 1 (es mostra com `V01`)
- No accepta valors fora del rang (clamp en temps real)
- Format al nom: `V` + zero-padded 2 dígits (`V01`, `V12`, `V99`)

#### TA · CN — Tipus d'àudio × Canals
- **3 blocs independents** amb colors distinctius:
  - **MIX** (fons blau-morat): Mescla completa
  - **ME** (fons verd fosc): Music & Effects
  - **DX** (fons marró): Diàlegs
- Cada bloc té:
  - Botó activador del tipus (pill de color)
  - 4 pills de canals: `1` | `2_0` | `5_1` | `7_1_4`
- **Regles de comportament:**
  - Canals disponibles **només** quan el bloc tipus està actiu
  - En activar un bloc: s'activa el canal per defecte (`2_0` per MIX/ME, `1` per DX)
  - En desactivar un bloc: es netegen tots els canals del bloc
  - En reactivar: torna al canal per defecte
  - **Mínim 1 canal** actiu per cada bloc actiu (no es pot desmarcar l'últim)
  - Selecció múltiple de canals per bloc (genera combinació per cada canal)

#### Sincronització toggle Àudio ↔ Blocs TA
- Toggle **Generar àudios** ON → si cap bloc actiu, activa MIX amb `2_0`
- Toggle **Generar àudios** OFF → desactiva tots els blocs, neteja tots els canals
- Activar qualsevol bloc TA → toggle Àudio s'activa automàticament
- Desactivar tots els blocs TA → toggle Àudio s'apaga automàticament

#### 3 Toggles de generació (horitzontals)
- **Generar vídeos**: ON per defecte. Si OFF, no es generen noms de vídeo.
- **Generar àudios**: sincronitzat amb TA (vegeu secció anterior)
- **Incloure extensió**: OFF per defecte. Si ON, afegeix `.mov` al final dels noms de vídeo i `.wav` als d'àudio.

---

### Algoritme de generació de noms

**Pre-condicions per generar:**
- REF no buit
- TÍTOL no buit
- Almenys 1 PRF seleccionat
- Almenys 1 IDI seleccionat
- Toggle vídeos OR toggle àudios actiu

**Ordre de generació** (primer vídeos, després àudios):

**Noms de VÍDEO** (si toggle vídeos actiu):
```
per cada PRF seleccionat:
  per cada IDI seleccionat (en ordre de botons):
    per cada VIS seleccionat:
      VER = "ORG" si IDI és PIN, "ALT" si és SEL
      genera: REF-N-TITOL-N-FMT-PRF-IDI-VER-VIS-L-XXX-VXX[.mov]
```

**Noms d'ÀUDIO** (si toggle àudios actiu):
```
per cada PRF seleccionat:
  per cada IDI seleccionat (en ordre de botons):
    per cada bloc TA actiu (MIX → ME → DX):
      per cada CN actiu del bloc:
        VER = "ORG" si IDI és PIN, "ALT" si és SEL
        genera: REF-N-TITOL-N-FMT-PRF-IDI-VER-XXX-L-TA_CN-VXX[.wav]
```

**Mode SER** — el segment FMT s'expandeix:
```
FMT → "SER_S{TMP:02d}_E{EPI:04d}"
```
Es genera un conjunt complet de noms per a **cada episodi** de l'interval [des_de .. fins_a].

**Format dels noms:** tot en majúscules, sense espais.

---

### Àrea de resultats

#### Mode FTR / TLR / SPT (film)
- Secció **VÍDEO (.mov)** col·lapsable
- Secció **ÀUDIO (.wav)** col·lapsable
- Cada nom: caixa monospace amb **segments de colors** + botó 📋 (copia el nom)
- Botó **"📋 Copiar tots"** a la capçalera: copia tots els noms un per línia, separats per `\n` (compatible amb Excel)
- Llegenda de colors a la part inferior

#### Mode SER (sèries)
- Un **bloc accordion** per episodi (S01E0001, S01E0002…)
- **Un sol episodi obert a la vegada** (comportament accordion)
- Primer episodi obert per defecte
- Capçalera de l'episodi: codi + badge amb nombre de noms
- Dins cada episodi: subseccions VÍDEO i ÀUDIO (mateixa estructura que mode film)
- Cada fila té **dos botons**:
  - **📋 blau** — copia aquest nom (1 episodi)
  - **📋 daurat** — copia aquest nom de **tots** els episodis (un per línia)
- Botó **"📋 Copiar tots"** global (tots els noms de tots els episodis)

#### Codificació de colors dels segments
| Segment | Fons | Text |
|---------|------|------|
| REF | `#312e81` | `#a5b4fc` |
| TÍTOL | `#7c2d12` | `#fdba74` |
| FMT (inclou TMP·EPI) | `#14532d` | `#86efac` |
| PRF | `#164e63` | `#67e8f9` |
| IDI | `#831843` | `#fbcfe8` |
| VER | `#713f12` | `#fde68a` |
| VIS | `#4c1d95` | `#ddd6fe` |
| L/S | `#1e1b4b` | `#a5b4fc` |
| TA\_CN | `#7f1d1d` | `#fca5a5` |
| VXX | `#1f2937` | `#9ca3af` |
| .ext | `#111827` | `#6b7280` |

---

## Pestanya ② — Desxifrar nom

### Entrada
- **Camp de text** (QLineEdit) per enganxar un nom manualment
- **Drag & drop**: arrossegar un fitxer sobre la zona d'entrada extreu el nom del fitxer (`os.path.basename`) i el col·loca al camp. El fitxer no es modifica.
- El botó **"🔍 Desxifrar nom"** (o auto-parse en canviar el text) processa el nom

### Algoritme de parsing

El parser intenta identificar els segments en ordre:

```
1. Separar extensió: tot el que hi hagi després de l'últim '.' → EXT
2. Separar per "-N-" → [REF, TITOL+resta] o fallback complet
3. A la resta, separar per "-" → llista de segments
4. Identificar FMT: primer segment que sigui FTR/TLR/SPT o comenci per SER
   - Si comença per SER: extreure TMP (S\d+) i EPI (E\d+) del mateix token
5. La resta de segments en ordre: PRF, IDI, VER, VIS, L/S, TA_CN, VXX
6. TA_CN: si el segment conté '_' i la part esquerra és MIX/ME/DX → TA+CN
           si el segment és XXX → TA=XXX (vídeo)
```

Si algun segment no és reconeixible, es marca com a **desconegut** (badge vermell).

**Detecció de tipus d'arxiu:**
- Si TA = `XXX` i EXT = `.mov` → VÍDEO
- Si TA ≠ `XXX` i EXT = `.wav` → ÀUDIO
- Si no hi ha extensió: deduir per TA

### Resultat visual

1. **Nom original amb segments de colors** (mateixa codificació de colors que Tab 1)
2. **Grid de targetes** (3 columnes), una per camp:
   - REF (1 col) + TÍTOL (2 col)
   - FMT + TMP + EPI (3 col, TMP i EPI presents/ocults si SER o no)
   - PRF + IDI + VER
   - VIS + L/S + TA·CN
   - VXX + Extensió + Tipus d'arxiu (VÍDEO/ÀUDIO)
3. Camps no reconeguts: fons vermell amb valor "?" i nota d'error

---

## Pestanya ③ — Renombrar per lots

### Entrada: CSV
- **Selector de fitxer** (QPushButton → QFileDialog) o **drag & drop** del CSV
- Mostra la ruta completa del fitxer seleccionat
- Format CSV esperat: `nom_original,nom_nou` (sense capçalera, o capçalera autodetectada)
- El separador pot ser `,` o `;` (autodetectat)
- Codificació: UTF-8

### Entrada: Carpeta
- **Selector de carpeta** (QPushButton → QFileDialog)
- Mostra la ruta completa
- La cerca de fitxers és **no recursiva** (només fitxers directament dins la carpeta)

### Processament i previsualització

En carregar CSV o canviar carpeta, es recalcula la taula:

```
per cada fila del CSV (nom_original, nom_nou):
  buscar nom_original dins la carpeta seleccionada
  estat = un de:
    - TROBAT: el fitxer existeix i el nom_nou no existeix → llest per renombrar
    - NO_TROBAT: el fitxer no existeix a la carpeta
    - CONFLICTE: el nom_nou ja existeix a la carpeta
```

**Taula de previsualització** (columnes):
- `#` — número de fila
- `Nom original` — en gris
- `→` — fletxa separadora
- `Nom nou` — en blanc (gris si no_trobat)
- `Estat` — badge de color

**Codificació visual dels estats:**
| Estat | Color fons fila | Badge |
|-------|----------------|-------|
| TROBAT | verd molt fosc | `✓ Trobat` (verd) |
| NO_TROBAT | vermell molt fosc | `✗ No trobat` (vermell) |
| CONFLICTE | ambre molt fosc | `⚠ Nom ja existeix` (ambre) |

**Barra d'estadístiques** (sobre la taula):
- Total files al CSV · Trobats · No trobats · Conflictes · "Es renombraran N fitxers"

### Execució

- Botó **"✅ Renombrar N fitxers trobats"** (N = només els TROBAT)
- S'executen **únicament** les files en estat TROBAT
- NO_TROBAT i CONFLICTE s'ignoren silenciosament
- Avís previ: "Aquesta acció no es pot desfer. Continuar?"
- Execució: `os.rename(carpeta/nom_original, carpeta/nom_nou)` per cada fila TROBAT
- Errors individuals (fitxer bloquejat, permisos…) es capturen i mostren per fila sense aturar la resta
- **Botó "📋 Exportar log"**: genera un TXT amb el resultat complet (timestamp, fila, estat, èxit/error)

---

## Aspectes globals

### Tecnologia
- **Python 3.11+** amb **PyQt6**
- Empaquetat amb **PyInstaller** com a `.exe` portable (un sol fitxer, sense instal·lació)
- Sense base de dades ni fitxers de configuració externs

### Estil visual
- Tema fosc (dark mode) inspirat en els mockups HTML
- Font monospace `Consolas` per a noms de fitxer
- Colors d'accent per segments (mateixa paleta a les 3 pestanyes)

### Comportament general
- La finestra és redimensionable; els camps de text i la taula s'expandeixen
- No hi ha persistència de sessió (cada cop que s'obre l'app, comença des de zero)
- Tots els textos de la interfície en català
