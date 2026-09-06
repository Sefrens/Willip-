# Willip Wiki Generator

Ein statischer Wiki-Generator für Obsidian-Markdown.

## Grundidee

- Deine Obsidian-Vault bleibt privat.
- Jede Notiz kann Spielerwissen und SL-Wissen enthalten.
- Einzelne Blöcke können über IDs freigeschaltet werden.
- Der Generator exportiert ausschließlich sichtbares Wissen nach `docs/`.
- GitHub Pages veröffentlicht anschließend nur den Inhalt von `docs/`.

## Schnellstart

```bash
python generate_wiki.py
```

Danach:

```text
docs/
├── index.html
├── assets/
└── ...
```

## Beispiel einer Notiz

```markdown
---
title: Dr. Kreutz
type: npc
published: true
---

# Dr. Kreutz

:::player
## Bekanntes Wissen

Dr. Kreutz wird in den Aufzeichnungen eines Alchemisten erwähnt.
:::

:::unlock id=dr-kreutz-sanatorium
## Verbindung zum Sanatorium

Die Gruppe hat erfahren, dass Dr. Kreutz mit einem Sanatorium verbunden ist.
:::

:::gm
## Die Wahrheit

Dr. Kreutz züchtete die Gehirnpilze für den Kult von Lux.
:::
```

## Freischalten

In `wiki_config.yaml`:

```yaml
unlocks:
  - dr-kreutz-sanatorium
```

Nach `python generate_wiki.py` erscheint der entsprechende Block im Spielerwiki.

## Sichtbarkeitsregeln

### `:::player`
Immer sichtbar.

### `:::unlock id=...`
Nur sichtbar, wenn die ID in `wiki_config.yaml` unter `unlocks` steht.

### `:::gm`
Wird niemals exportiert.

### Datei komplett ausblenden

Im Frontmatter:

```yaml
published: false
```

Die Datei wird nicht in das Wiki übernommen.
