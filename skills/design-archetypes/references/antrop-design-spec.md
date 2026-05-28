# Persona design — Antrop brand notes

> Hur vi designar persona-kort enligt Antrops visuella språk. Skrivet för att kunna återanvändas
> nästa gång samma fråga kommer (Cooper-style behavioural personas eller liknande).

---

## 1 · Utgångspunkt: vad en persona ÄR i Antrops värld

En persona är inte en marknadssegmenterings-avatar. Den är ett **design-mål** — en sammansatt psykologisk profil som ska kunna hållas i huvudet av strategi-, copy- och tjänsteteamet när beslut fattas. Konsekvenser:

- **Komposit-källan ska vara synlig.** "Composite of IP02 + IP04" är ett trovärdighets-element, inte en fotnot. Sätt det i mono direkt under namnet.
- **Frustrationer väger lika tungt som mål.** Vi designar bort barriärer minst lika ofta som vi designar mot mål.
- **Citat är icke-förhandlingsbara.** Ett ordagrant citat från en intervju är personans röst. Sätt den stort, i Playfair Italic, med intervju-id i mono som attribution.
- **Hierarki ska kodas i layouten, inte bara i en pill.** Primary, Supplemental, Negative, Outlier är fyra olika design-roller. De ska se *visuellt* olika ut — inte bara ha olika tagg.

## 2 · Voice — copy enligt Antrop

- **Svenska som default**, även när underliggande material är på engelska. Citat översätts till svenska om de inte redan är det (och original-språk noteras i mono).
- **Du-tilltal genom hela kortet.** "Vad får henne att röra sig" — inte "Vad motiverar personan".
- **Sentence case** i alla rubriker. ALL CAPS bara i mono-eyebrows (CHECK-IN, FRÅGA, GOALS).
- **Inga emoji.** Inga utropstecken. Inga "✨".
- **Korta meningar.** Antrop skriver som man pratar.
- **Skriv ut tal under tio.** *"två & tre barn"*, inte *"2-3 barn"*.

## 3 · Färgsystem — en accent per kort, inte tre

Antrops grundregel: *en sekundär accent per artefakt*. Det ger varje persona en distinkt "atmosfär" utan att paletten spretar:

| Roll | Bakgrund | Text | Accent | Logik |
|---|---|---|---|---|
| **Primary 1** (Anna-typ — friktion, hushåll) | `--antrop-vinrod` | `--antrop-ljusrosa` | `--antrop-korall` | Aj-det-skaver-paletten. Värme + slitage. |
| **Primary 2** (Maja-typ — ambition under tryck) | `--antrop-morkbla` | `--antrop-ljusbla` | `--antrop-turkos` | Brand-default. Lugn, primärt mål. |
| **Secondary** (också-design-för, ej primary) | Same as Primary 2, men med en `SECONDARY`-pill istället för `PRIMARY` | | | Bryt visuellt mot primary med pill, inte färg. |
| **Supplemental** (Linn-typ — redan där) | `--antrop-morkgron` | `--antrop-ljusgul` | `--antrop-gul` | AI-på-Antrop-paletten. Evidens, klarhet. |
| **Customer** (B2B-köpare ≠ användare) | Ljus surface (samma som primary i light-paletten) med en **mono-banner** överst: `KÖPER · ANVÄNDER INTE` | | Accent: indigo `#3B3B6D` | Kunden-fokus. Köpbeslut, integration, TCO. |
| **Served** (gynnas men interagerar inte) | Ljus surface med banner överst: `GYNNAS · INTERAGERAR INTE` | | Accent: terracotta `#A6502A` | Indirekt mottagare. |
| **Negative** (Bengt-typ — designa förbi) | `--antrop-ljusgul` | `--antrop-morkbla` | `--antrop-morkbla` | *Ljus* yta — markerar att hen inte är target. |
| **Outlier** (n=1, marginalanteckning) | `--antrop-vit` | `--antrop-morkbla` | `--antrop-vinrod` | Vit yta med hårstreck-border. Mindre tyngd. |

Aldrig tre färger samtidigt på ett kort. Vinröd + mörkgrön på samma sida = sluta.

## 4 · Typografi — tre röster

- **TT Norms Black** för persona-namn (96pt på A3, lägre på mindre format). Brutalt stort. Tag-line bredvid i `font-weight: 300` och `opacity: 0.6` för ålder.
- **Playfair Display Italic** är *editorial accent*. Bara två platser per kort: (a) role-taglinjen ("The Caregiver Under Load."), (b) pull-quoten. Aldrig som rubrik. Aldrig på små storlekar.
- **Martian Mono (eller fallback)** för allt som är "label-röst": eyebrow ("PRIMARY · DESIGN TARGET"), composite-from-raden, themes-chips, sidnummer, citat-attribution. Letter-spacing 0.10-0.16em.

## 5 · Illustrationer / foto

### Illustrationer (default)

Antrops 56 handritade stipple-illustrationer är *primär* bildkälla. Välj en som metaforiskt matchar personans psykologi, inte demografin:

- Caregiver under load → laptop-collage, hemarbete (`homework-more-01`)
- Constrained Aspirer → fallskärm med paket (`academy-01`) — *försöker landa under kontroll*
- Integrated Practitioner → person som vinkar lugnt (`academy-02`)
- Continuity Keeper → traditionellt redskap, vattenkanna (`sak-sak-vattenkanna`)
- Outlier (regulatorisk) → valurna (`trend-02`)

Placera dem i en **färgad disc** (`background: rgba(accent, 0.08)`) på 110mm i en A3-landscape, med 5% inset så stippling-strukturen syns.

### Foto (om det krävs)

Råa fotografiska porträtt **krockar** med Antrops illustrations-språk. Om foto används, behandla det:

- Duotone i kortets accent-färg + bakgrund (vinröd+ljusrosa, mörkblå+turkos osv)
- Lägg på halftone/grain overlay för att echo:a stipplingen
- Beskär i en organisk wave-mask, inte en rektangel eller cirkel
- Konsistens-regler för en hel serie: samma beskärning, samma ljus, samma kamera-känsla. Annars känns det som stock.

AI-genererat porträtt: ange "n = 1 · AI-genererat porträtt, inte en riktig person" i sidfoten. För personor som baseras på riktiga intervjusubjekt: stäm av samtycke först.

## 6 · Layout — A3 landskap som canonical format

420 × 297 mm. Yttre marginal 22-26 mm. Inre rutnät:

```
┌──────────────────────────────────────────────────────────────────┐
│ [PILL]                                               [01 / 05]   │ ← topbar
│                                                                  │
│ Anna, 38                                  The Caregiver          │ ← hero
│                                           Under Load.            │
│ COMPOSITE OF IP02 · IP04                                         │ ← mono
│                                                                  │
│ ┌─────────┐ DRIVKRAFTER     SMÄRTOR         BEHOV                │
│ │  ILLU   │ — bullet        — bullet        — bullet             │
│ │  110mm  │ — bullet        — bullet        — bullet             │
│ │  disc   │ — bullet        — bullet        — bullet             │
│ └─────────┘                                 [theme chips]        │
│ sketch.                                                          │
│ ─────────────────────────────────────────────────────────────── │
│ " Pull quote i Playfair italic, max 50em "       — INTERVIEW 02  │ ← quote band
└──────────────────────────────────────────────────────────────────┘
```

**Three Cooper-sections — Drivkrafter, Smärtor, Behov (G9-fix).** The front uses three columns, not two. This maps explicitly to the three Cooper-template sections in `archetypes.md`:

| Card column (svenska) | `archetypes.md` field(s) | Eyebrow label (en-version) |
|---|---|---|
| **Drivkrafter** | `End goals` (primary), with 1 Life goal + 1 Experience goal as smaller-print sub-bullets | `DRIVERS — WHAT MOVES HER` |
| **Smärtor** | `Key pains` | `FRUSTRATIONS — WHAT STOPS HER` |
| **Behov** | `Key needs` | `NEEDS — WHAT WOULD HELP` |

**Goal hierarchy (Cooper, P2-fix).** The Drivkrafter column shows End goals at full weight (3–4 bullets, body type) and reserves *one Life goal + one Experience goal as smaller-print sub-items* under a `LIVS- · UPPLEVELSE-` mono divider. End goals do the design work (Cooper's rule), so they're the visual lead; Life and Experience goals provide context without dominating. The full hierarchy lives in `archetypes.md` for designers/strategists who need it.

The previous two-column layout (`GOALS / FRUSTRATIONS`) collapsed either drivkrafter into behov or behov into drivkrafter — different runs produced different collapses (NV v1 dropped behov, SJ 2026-05-28 dropped drivkrafter, parallel projects had the inverse problem). **All three sections render. Always.** If a section is sparse for a given archetype, leave it short rather than dropping it.

If the analyst genuinely wants a two-column variant (e.g. workshop posters where character count is tight), set `card-front-columns: 2` in `.persona-config.md` and choose which Cooper section moves to the back; the default is 3.

Print-CSS: `@page { size: A3 landscape; margin: 0 }` + `page-break-after: always` per persona. Bleed 3mm om det ska tryckas på pressar; 0 för intern utskrift på A3-skrivare.

## 6b · Beteendevariabel-skala på framsidan

På framsidan, mellan porträttdisken och de tre Cooper-kolumnerna, renderas en kolumn med **3–5 utvalda beteendevariabler som prickskala** — fem cirklar per rad, ifyllda upp till personens position. Detta gör att läsaren på ett ögonblick ser *kontrasten* mellan personor utan att läsa texten.

```
DRIVKRAFTER  ●●●●●        SMÄRTOR        BEHOV
PLANERAR LÅNGSIKTIGT       — bullet       — bullet
●●●●○                      — bullet       — bullet
LITAR PÅ EXPERTRÅD         — bullet       — bullet
●○○○○                                     [theme chips]
TYDLIG EKONOMISK KOLL
```

**Vilka variabler renderas?** Card-renderer:
1. Läser `03-framework/behavioural-variables.xlsx` Sheet 2 (Placements)
2. Beräknar medel per kluster per variabel
3. Identifierar de 3–5 variabler med störst varians **mellan** klustren (de variabler där arketyperna faktiskt skiljer sig åt)
4. Renderar dem i en lodrät kolumn till vänster om Cooper-kolumnerna, med variabelnamn i mono och ändpunktsord (`low_end` / `high_end`) som klisterlapp på kortet

**HTML-struktur:**

```html
<aside class="behavior-scale">
  <div class="scale-row">
    <p class="scale-label">PLANERAR LÅNGSIKTIGT</p>
    <p class="scale-dots" data-position="4">●●●●○</p>
    <p class="scale-ends">SPONTAN ↔ STRUKTURERAD</p>
  </div>
  ...
</aside>
```

Skala-prickarna renderas som unicode (`●` / `○`) i mono-fonten med 0.10em letter-spacing. Variabelnamnet är i mono UPPERCASE 9pt. Ändpunktsorden i mono 7pt med opacity 0.6.

**Kan stängas av** med `behavior-scale: no` i `.persona-config.md` `brand-overrides`. Default `yes`. Stängs av automatiskt om `behavioural-variables.xlsx` saknas eller om alla varianser är ≤1 (då skiljer sig personerna inte tydligt på något skala).

**Bakgrund:** Mönstret med prickskala för beteendevariabler är ett klassiskt sätt att kommunicera kontrast mellan persontyper på ett ögonblick. Det passar Cooper-metoden särskilt bra eftersom variablerna *redan* är behavioural-spine — vi har faktisk data från `behavioural-variables.xlsx` att rendera dem från, inte gissningar.

## 7 · Vågorna — låt dem andas

Vågdekoration ska användas på minst ett kort av två — men aldrig som ram runt innehållet. Place på utsidan, opacity 0.05-0.10, så den känns som att ytan curlar in i sidan snarare än att vara dekorerad.

## 8 · Negative persona — speciell behandling

Bengt-typen behöver tre särdrag som signalerar "designa förbi":

1. **Ljus yta** (ljusgul) — bryter mot resten som är mörka tunga bakgrunder
2. **Strategy-banner** i botten ("Reach him structurally — defaults, price, vocabulary he'll accept") i mono på mörkblå
3. **Pill säger "Design around"** — inte "Design target"

Utan dessa tre läses Bengt som ännu ett primärt mål, vilket är hela poängen att undvika.

## 9 · Saker att aldrig göra

- ❌ Sätt aldrig persona-foton på Antrops mörka ytor utan duotone-behandling
- ❌ Använd aldrig Playfair på små storlekar (under 18pt) — den faller isär
- ❌ Skugga aldrig persona-korten — Antrop är flat
- ❌ Border-radius på själva A3-sidan är 0. Inte 12px, inte 20px. Noll.
- ❌ Använd aldrig "👨" / "👩" / emoji som persona-avatar
- ❌ Räkna inte ut prevalens ("32% av befolkningen är Anna") på det här kortet — det är ett separat kvantitativt arbete
- ❌ Sätt aldrig en negativ persona i samma färgvärld som de primära — då kommunicerar layouten fel

## 10 · Leveransformat

- **A3 landscape PDF** — primärleverans, för print
- **HTML** — för iterativ redigering och digital delning (samma källfil, `window.print()` ger PDFen)
- Filnamn: `Persona Cards.html` på rot, CSS/assets under `antrop/`
- Versionera vid större revideringar: `Persona Cards v1.html`, etc.

---

*Senast uppdaterad: behavioural archetypes för Naturvårdsverket, v1 (2026).*
