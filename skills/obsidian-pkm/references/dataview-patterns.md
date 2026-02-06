# Dataview Query Patterns

Common Dataview DQL queries for Obsidian PKM workflows.

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [Project Management](#project-management)
3. [Literature & Reading](#literature--reading)
4. [Daily/Periodic Notes](#dailyperiodic-notes)
5. [Tags & Metadata](#tags--metadata)
6. [Advanced Patterns](#advanced-patterns)

---

## Basic Queries

### List All Notes in a Folder

```dataview
LIST
FROM "Projects"
```

### Table with Metadata

```dataview
TABLE title, date-created, tags
FROM #permanent-note
```

### Sorted by Date

```dataview
LIST
FROM #daily-note
SORT date DESC
```

### Limit Results

```dataview
LIST
FROM #project
SORT priority ASC
LIMIT 10
```

---

## Project Management

### Active Projects

```dataview
TABLE status, priority, due as "Due Date"
FROM #project
WHERE status = "active"
SORT priority ASC
```

### Projects by Priority

```dataview
TABLE status, due
FROM #project
WHERE status != "completed"
GROUP BY priority
```

### Overdue Projects

```dataview
TABLE status, due
FROM #project
WHERE due < date(today) AND status != "completed"
SORT due ASC
```

### Recently Completed

```dataview
LIST
FROM #project
WHERE status = "completed"
SORT file.mtime DESC
LIMIT 10
```

---

## Literature & Reading

### Books to Read

```dataview
TABLE author, rating
FROM #book
WHERE status = "to-read"
SORT rating DESC
```

### Currently Reading

```dataview
TABLE author, started
FROM #book
WHERE status = "reading"
```

### Books by Rating

```dataview
TABLE author, status
FROM #book
WHERE rating >= 8
SORT rating DESC
```

### Articles to Process

```dataview
TABLE source, date-read
FROM #article
WHERE status = "to-process"
SORT date-read ASC
```

---

## Daily/Periodic Notes

### Recent Daily Notes

```dataview
LIST
FROM #daily-note
SORT date DESC
LIMIT 7
```

### This Week's Notes

```dataview
LIST
FROM #daily-note
WHERE date >= date(today) - dur(7 days)
SORT date ASC
```

### Notes with Tasks

```dataview
TASK
FROM #daily-note
WHERE !completed
GROUP BY file.name
```

---

## Tags & Metadata

### Notes Without Tags

```dataview
LIST
FROM !#moc AND !#daily-note
WHERE length(tags) = 0 OR !tags
```

### Notes Without Backlinks

```dataview
LIST
FROM !#moc
WHERE length(file.inlinks) = 0
```

### Orphan Notes (no links in or out)

```dataview
LIST
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
```

### Notes by Tag Count

```dataview
TABLE length(tags) as "Tag Count"
FROM #permanent-note
SORT length(tags) DESC
```

---

## Advanced Patterns

### Map of Content Dynamic List

```dataview
TABLE date-created as Created, file.mtime as Modified
FROM #topic-tag AND !#moc
SORT file.mtime DESC
```

### Recently Modified

```dataview
LIST
SORT file.mtime DESC
LIMIT 20
```

### Long Notes (by word count)

```dataview
TABLE length(file.content) as Words
SORT length(file.content) DESC
LIMIT 10
```

### Created This Month

```dataview
LIST
WHERE file.cday >= date(today) - dur(30 days)
SORT file.cday DESC
```

### Notes by Creation Date

```dataview
LIST
GROUP BY file.cday
```

### All Tasks Across Vault

```dataview
TASK
WHERE !completed
GROUP BY file.name
```

### Tasks Due Soon

```dataview
TASK
WHERE !completed AND due <= date(today) + dur(7 days)
GROUP BY due
```

---

## Query Syntax Reference

### Field Types

| Field | Description | Example |
|-------|-------------|---------|
| `file.name` | Filename without extension | `My Note` |
| `file.path` | Full path from vault root | `Projects/Active/My Note` |
| `file.link` | Link to file | `[[My Note]]` |
| `file.size` | Size in bytes | `1024` |
| `file.ctime` | Created timestamp | `2024-01-15 10:30` |
| `file.cday` | Created date | `2024-01-15` |
| `file.mtime` | Modified timestamp | `2024-01-20 14:45` |
| `file.mday` | Modified date | `2024-01-20` |
| `file.tags` | All tags in file | `[#tag1, #tag2]` |
| `file.inlinks` | Notes linking to this | `[Note A, Note B]` |
| `file.outlinks` | Notes this links to | `[Note C, Note D]` |

### Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=` | Equal | `status = "active"` |
| `!=` | Not equal | `status != "completed"` |
| `<` | Less than | `rating < 5` |
| `>` | Greater than | `due > date(today)` |
| `<=` | Less or equal | `priority <= 2` |
| `>=` | Greater or equal | `rating >= 8` |

### Functions

| Function | Description | Example |
|----------|-------------|---------|
| `date()` | Parse date | `date(2024-01-15)` |
| `dur()` | Duration | `dur(7 days)` |
| `length()` | Array/string length | `length(tags)` |
| `contains()` | Check if contains | `contains(tags, #project)` |
| `regexmatch()` | Regex match | `regexmatch("^Project", file.name)` |

---

*For more advanced patterns, see the full Dataview documentation at blacksmithgu.github.io/obsidian-dataview*
