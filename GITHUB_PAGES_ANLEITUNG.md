# GitHub Pages – Schritt für Schritt

## 1. GitHub-Konto

Falls noch nicht vorhanden, erstelle ein kostenloses Konto bei GitHub.

## 2. Neues Repository

1. Klicke auf `New repository`.
2. Name: zum Beispiel `willip-wiki`.
3. Sichtbarkeit: `Private` oder `Public`.

Wichtig: Bei kostenlosen GitHub-Konten kann die genaue Pages-Verfügbarkeit für private Repositories je nach aktuellem GitHub-Plan variieren. Wenn die Seite nur für deine Spieler erreichbar sein soll, ist eine andere Hosting-Lösung mit Passwortschutz eventuell sinnvoll.

## 3. Projekt hochladen

Lade den gesamten Inhalt dieses Projektordners in das Repository hoch.

Wichtig:

- `02_Spielleiterwissen` sollte idealerweise gar nicht zu GitHub hochgeladen werden.
- Wenn du GitHub als Build-System nutzt, kann die Action nur Dateien sehen, die im Repository liegen.

## EMPFOHLENE SICHERHEITSARCHITEKTUR

Behalte deine echte Master-Vault lokal.

```text
PRIVATE MASTER VAULT
        |
        | manueller/automatischer Export
        v
GITHUB-EXPORT-REPOSITORY
        |
        v
GitHub Pages
        |
        v
Spieler
```

So gelangen geheime Dateien niemals zu GitHub.

## 4. GitHub Pages aktivieren

Im Repository:

1. `Settings`
2. `Pages`
3. Unter `Build and deployment`
4. Source: `GitHub Actions`

Die Datei `.github/workflows/deploy.yml` übernimmt danach den Rest.

## 5. Erster Build

Sobald du Dateien nach `main` hochlädst:

- GitHub startet automatisch den Workflow.
- Python erzeugt das Wiki.
- Der Ordner `docs/` wird veröffentlicht.

Unter `Actions` kannst du den Fortschritt verfolgen.

## 6. URL

Nach erfolgreicher Veröffentlichung zeigt GitHub dir unter:

`Settings → Pages`

die URL deiner Website.

Typisch:

```text
https://BENUTZERNAME.github.io/REPOSITORYNAME/
```

## 7. Nach einer Session aktualisieren

Beispiel:

Die Spieler erfahren, dass Dr. Kreutz mit dem Sanatorium verbunden ist.

Du öffnest:

`wiki_config.yaml`

und ergänzt:

```yaml
unlocks:
  - dr-kreutz-sanatorium
```

Danach:

1. Änderung zu GitHub hochladen.
2. GitHub Action läuft automatisch.
3. Website aktualisiert sich.

## WICHTIGER SICHERHEITSHINWEIS

Eine GitHub-Pages-Seite ist standardmäßig öffentlich erreichbar.

Deshalb niemals:

- SL-Geheimnisse
- geheime Markdown-Dateien
- deine vollständige Obsidian-Vault

in ein öffentliches Repository laden.

Dieses Projekt ist deshalb als Export-System gedacht.

Die sicherste Struktur:

```text
C:/DND/
├── Willip-SL-Vault/        ← nur lokal
└── Willip-Wiki-Export/     ← wird zu GitHub übertragen
```

Der Export-Ordner enthält ausschließlich freigegebene Daten.
