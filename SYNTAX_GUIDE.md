# Syntax-Leitfaden

## Datei-Metadaten

Jede exportierbare Datei beginnt mit:

```yaml
---
title: Name des Eintrags
type: npc
published: true
---
```

Mögliche `type`-Werte:

- npc
- location
- faction
- session
- item
- creature
- phenomenon

## Immer sichtbares Wissen

```markdown
:::player
Dieser Inhalt ist immer sichtbar.
:::
```

## Freischaltbares Wissen

```markdown
:::unlock id=eindeutige-id
Dieser Inhalt wird sichtbar, wenn die ID freigeschaltet ist.
:::
```

Die ID kommt in `wiki_config.yaml`:

```yaml
unlocks:
  - eindeutige-id
```

## Spielleiterwissen

```markdown
:::gm
Dieser Inhalt wird nie exportiert.
:::
```

## Empfehlung für IDs

Verwende:

```text
thema-information
```

Beispiele:

```text
kreutz-sanatorium
mirek-menschenhandel
blackbird-fluch
lux-chimera
```

## Obsidian-Links

Normale Obsidian-Links funktionieren:

```markdown
[[Kult von Lux]]
[[Dr. Kreutz|Doktor Kreutz]]
```

Der Generator versucht, sie in Wiki-Links umzuwandeln.
