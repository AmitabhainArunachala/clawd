# Front Matter and Metadata in PKM

A comprehensive research report on YAML front matter, metadata schemas, and data management patterns in Personal Knowledge Management systems.

**Research Date:** 2026-02-06  
**Scope:** YAML front matter best practices, metadata schemas, organizational patterns, and Dataview query techniques

---

## Table of Contents

1. [YAML Front Matter Best Practices](#1-yaml-front-matter-best-practices)
2. [Metadata Schemas for Notes](#2-metadata-schemas-for-notes)
3. [Tags vs Links vs Properties](#3-tags-vs-links-vs-properties)
4. [Dynamic Note Generation from Front Matter](#4-dynamic-note-generation-from-front-matter)
5. [Querying Notes by Metadata](#5-querying-notes-by-metadata)
6. [Obsidian Dataview Plugin Patterns](#6-obsidian-dataview-plugin-patterns)

---

## 1. YAML Front Matter Best Practices

### What is YAML Front Matter?

YAML (YAML Ain't Markup Language) front matter is a metadata section placed at the very beginning of a markdown file, enclosed by triple dashes (`---`). It provides structured, machine-readable data about the note.

```yaml
---
title: "My Note Title"
tags: [note, idea, project]
created: 2025-03-30
author: "John Doe"
---
```

### Core Best Practices

#### 1.1 Position and Format
- **Must be first**: Front matter must be the absolute first thing in the file
- **Triple dashes**: Use `---` to open and close the block
- **Valid YAML**: Ensure proper YAML syntax (colons, spacing, quotes)

#### 1.2 Naming Conventions
- Use **lowercase** property names for consistency
- Use **kebab-case** or **snake_case** for multi-word keys
- Examples: `created-date`, `last_reviewed`, `project_status`

#### 1.3 Consistency Across Notes
- Define a **standard set of fields** for all notes
- Use **templates** to enforce consistency
- Avoid mixing `created` vs `date-created` vs `created_date`

#### 1.4 Data Types Matter

| Type | YAML Example | Use Case |
|------|--------------|----------|
| Text | `title: "My Title"` | Names, descriptions |
| Number | `rating: 8` | Ratings, counts, priorities |
| Boolean | `published: true` | Flags, status checks |
| Date | `due: 2025-03-30` | Deadlines, created dates |
| List | `tags: [a, b, c]` | Categories, multiple values |
| Object | `author: {name: "John", email: "john@example.com"}` | Nested data |

#### 1.5 Avoid These Common Mistakes

❌ **Inconsistent tag naming**: Mixing `#todo`, `#to-do`, `#task`
❌ **Creating tags for every note title**: Leads to tag clutter
❌ **Unquoted special characters**: Can break YAML parsing
❌ **Missing quotes around links**: `parent: [[Page]]` should be `parent: "[[Page]]"`

#### 1.6 Template Protection Hack

When using Templater, prevent template front matter from being indexed:

```markdown
<% ---
type: flashcard
subType: language-learning
--- %>
```

Using `<%` and `%>` instead of `---` prevents Obsidian from recognizing the template's front matter as actual metadata. Templater removes these markers when creating the actual note.

---

## 2. Metadata Schemas for Notes

### 2.1 Property Types in Obsidian

Obsidian Properties (introduced in v1.4.0) provide typed metadata fields:

| Type | Description | Example |
|------|-------------|---------|
| **Text** | Simple string values | `status: in-progress` |
| **List** | Multiple text entries | `tags: [work, urgent]` |
| **Number** | Integer or decimal values | `priority: 3` |
| **Checkbox** | Boolean true/false | `completed: true` |
| **Date** | Calendar date | `due: 2025-03-30` |
| **Date & Time** | Timestamp | `meeting: 2025-03-30T14:00` |

### 2.2 Recommended Schema Patterns

#### Basic Schema (Universal Fields)
```yaml
---
title: "Note Title"
created: 2025-02-06
modified: 2025-02-06
tags: [topic, status]
aliases: ["Alt Name", "Another Name"]
---
```

#### Project Schema
```yaml
---
title: "Project Alpha"
type: project
status: in-progress  # planning, active, paused, completed
priority: high       # low, medium, high, critical
due: 2025-06-30
owner: "[[John Doe]]"
stakeholders: ["[[Jane Smith]]", "[[Bob Wilson]]"]
tags: [project, work, q2-2025]
---
```

#### Literature/Source Schema
```yaml
---
title: "The Art of Doing Science"
author: "Richard Hamming"
published: 1996
type: book
rating: 9
status: reading      # to-read, reading, completed, reference
tags: [science, research, philosophy]
source: "https://example.com/book"
---
```

#### Meeting Notes Schema
```yaml
---
title: "Weekly Team Sync"
date: 2025-02-06
type: meeting
attendees: ["[[Alice]]", "[[Bob]]", "[[Charlie]]"]
location: "Conference Room A"
project: "[[Project Alpha]]"
tags: [meeting, work, team]
---
```

### 2.3 Schema Design Principles

1. **Start Simple**: Begin with 3-5 core fields, expand as needed
2. **Use Standard Keys**: Stick to common names (title, date, tags, status)
3. **Type Consistency**: Don't mix types for the same property across notes
4. **Meaningful Values**: Use clear, actionable status values
5. **Document Your Schema**: Create a reference note explaining your metadata conventions

### 2.4 Nested/Complex Schemas

YAML supports nested objects for complex metadata:

```yaml
---
book:
  title: "Deep Work"
  author: "Cal Newport"
  year: 2016
  rating: 9
  notes:
    key_insight: "Deep work is valuable"
    action_item: "Schedule focus blocks"
---
```

Query nested fields with dot notation: `book.rating`, `book.notes.key_insight`

---

## 3. Tags vs Links vs Properties

### 3.1 Understanding the Distinction

| Feature | Tags | Links | Properties |
|---------|------|-------|------------|
| **Syntax** | `#tag` or `#category/sub` | `[[Note Name]]` | `key: value` in YAML |
| **Purpose** | Categorization | Relationships | Structured metadata |
| **Visualization** | Tag pane, search | Graph view, backlinks | Properties panel |
| **Best For** | Broad buckets, status | Specific connections | Data, filtering, queries |

### 3.2 When to Use Tags

Use tags for:
- **Broad categories**: `#work`, `#personal`, `#research`
- **Status indicators**: `#todo`, `#in-progress`, `#done`
- **Temporal markers**: `#2025`, `#q1`, `#week-06`
- **Cross-cutting concerns**: Notes that span multiple areas

Examples:
```markdown
#journal #mood/happy
#project/obsidian-series
#status/waiting-for-review
```

### 3.3 When to Use Links

Use links for:
- **Explicit relationships**: Connecting specific notes
- **Topic hubs**: `[[Project Alpha]]`, `[[Python]]`
- **People**: `[[John Doe]]`, `[[Jane Smith]]`
- **Contextual connections**: Referencing related ideas

Examples:
```markdown
This project is related to [[Project Alpha]] and [[Q2 Goals]].
Meeting with [[John Doe]] about [[Product Launch]].
```

### 3.4 When to Use Properties

Use properties for:
- **Structured data**: Dates, numbers, status values
- **Filtering criteria**: Properties you want to query
- **Automation triggers**: Data for templates and scripts
- **Sortable information**: Priority, rating, progress

### 3.5 The Analogy

> "Think of tags as **broad buckets** and links as **roadways between notes**."
> 
> — Planet Tash

- **Tags** organize notes by category (what type is this?)
- **Links** build meaningful relationships (how does this connect?)
- **Properties** store structured data (what are the facts?)

### 3.6 Combined Workflow Example

```yaml
---
type: meeting
date: 2025-02-06
status: completed
tags: [work, team-sync]
---
```

```markdown
# Weekly Team Sync

Attendees: [[Alice]], [[Bob]], [[Charlie]]
Project: [[Project Alpha]]

## Agenda
- Review #milestones for [[Q2 Goals]]
- Discuss #blockers
```

### 3.7 Common Mistakes to Avoid

❌ Using tags like links: Creating `#Note Title` for every note  
❌ Over-linking: Linking every word creates noisy navigation  
❌ Ignoring one entirely: Using only folders and missing linked thinking  
❌ Inconsistent naming: Mixing `#todo`, `#to-do`, `#task`  
❌ Too many tags: Leads to fragmentation and difficulty finding notes

---

## 4. Dynamic Note Generation from Front Matter

### 4.1 Using Templater

Templater is the primary plugin for dynamic note generation in Obsidian.

#### Basic Dynamic Insertion

```markdown
---
title: "<% tp.file.title %>"
created: "<% tp.date.now('YYYY-MM-DD') %>"
time: "<% tp.date.now('HH:mm') %>"
---
```

#### Conditional Content

```markdown
---
project: "<%* tR += await tp.system.suggester(
    ['Project Alpha', 'Project Beta', 'Project Gamma'], 
    ['alpha', 'beta', 'gamma']
) %>"
priority: "<%* tR += await tp.system.suggester(
    ['Low', 'Medium', 'High', 'Critical'], 
    ['low', 'medium', 'high', 'critical']
) %>"
---
```

#### Accessing Front Matter in Templates

```markdown
---
number: 10
---
The number is: <% tp.frontmatter.number %>
```

### 4.2 Metatemplates Plugin

The Metatemplates plugin takes front-matter-driven templating further:

```yaml
---
type: article
destFolder: "Articles"
nameFormat: "{{date}} - {{title}}"
---
```

Features:
- **type**: Identifies the template type
- **nameFormat**: Dynamic renaming based on front matter fields
- **destFolder**: Auto-placement in specified folder
- **<<date>>** and **<<time>>**: Replacement for Templater syntax

### 4.3 Front Matter Generator Plugin

Automates front matter creation on file save:

- Define templates using JSON or JavaScript expressions
- Dynamically generate metadata based on file properties
- Auto-populate tags based on folder location
- Add timestamps automatically

### 4.4 Practical Dynamic Generation Patterns

#### Daily Note Template
```markdown
---
date: "<% tp.date.now('YYYY-MM-DD') %>"
day: "<% tp.date.now('dddd') %>"
week: "<% tp.date.now('WW') %>"
mood: 
energy: 
tags: [daily-note]
---

# <% tp.date.now('YYYY-MM-DD') %>

## Morning Reflection

## Tasks
- [ ] 

## Notes
```

#### Meeting Template with Prompts
```markdown
---
title: "<%* tR += await tp.system.prompt('Meeting Title') %>"
date: "<% tp.date.now('YYYY-MM-DD') %>"
type: meeting
attendees: 
project: "<%* tR += await tp.system.suggester(
    ['Project A', 'Project B', 'Other'],
    ['[[Project A]]', '[[Project B]]', '']
) %>"
tags: [meeting]
---

# <% tp.frontmatter.title %>

## Attendees
<% tp.frontmatter.attendees %>

## Agenda

## Notes

## Action Items
- [ ] 
```

---

## 5. Querying Notes by Metadata

### 5.1 Dataview Overview

Dataview is a live index and query engine that treats your vault as a database. It operates on:
- **YAML Frontmatter** fields
- **Inline Fields** (`key:: value` syntax)
- **Implicit Fields** (file metadata like creation date, tags, links)

### 5.2 Query Structure

```dataview
<QUERY-TYPE> <fields>
FROM <source>
<DATA-COMMAND> <expression>
```

Only the **Query Type** is mandatory.

### 5.3 Query Types

#### LIST
```dataview
LIST
FROM #project
WHERE status = "active"
```

#### TABLE
```dataview
TABLE title, due, priority
FROM "Projects"
WHERE !completed
SORT priority DESC
```

#### TASK
```dataview
TASK
WHERE !completed AND contains(tags, "#urgent")
GROUP BY file.link
```

#### CALENDAR
```dataview
CALENDAR due
WHERE typeof(due) = "date"
```

### 5.4 Data Commands

| Command | Purpose | Example |
|---------|---------|---------|
| **FROM** | Restrict source | `FROM #tag OR "Folder"` |
| **WHERE** | Filter results | `WHERE status = "open"` |
| **SORT** | Order results | `SORT created DESC` |
| **GROUP BY** | Bundle results | `GROUP BY type` |
| **LIMIT** | Restrict count | `LIMIT 10` |
| **FLATTEN** | Split results | `FLATTEN tags AS tag` |

### 5.5 Querying Front Matter

#### Basic Field Access
```dataview
TABLE title, author, rating
FROM #book
WHERE rating >= 8
```

#### Nested Fields
```dataview
TABLE book.author, book.year
WHERE book.rating > 7
```

#### List Fields
```dataview
TABLE tags, file.etags
FROM #project
WHERE contains(tags, "active")
```

#### Date Comparisons
```dataview
LIST
WHERE due AND due < date(today)
```

### 5.6 Implicit Fields Reference

| Field | Type | Description |
|-------|------|-------------|
| `file.name` | Text | Filename |
| `file.folder` | Text | Folder path |
| `file.path` | Text | Full file path |
| `file.link` | Link | Link to file |
| `file.size` | Number | File size in bytes |
| `file.ctime` | DateTime | Creation time |
| `file.cday` | Date | Creation date |
| `file.mtime` | DateTime | Modification time |
| `file.mday` | Date | Modification date |
| `file.tags` | List | All tags (including subtag levels) |
| `file.etags` | List | Explicit tags only |
| `file.inlinks` | List | Incoming links |
| `file.outlinks` | List | Outgoing links |
| `file.aliases` | List | Aliases from front matter |
| `file.tasks` | List | Tasks in file |
| `file.lists` | List | List items |
| `file.frontmatter` | Object | Raw front matter |

### 5.7 Advanced Query Patterns

#### Recently Modified Files
```dataview
LIST
SORT file.mtime DESC
LIMIT 10
```

#### Orphan Notes (No Links)
```dataview
LIST
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
```

#### Notes by Creation Week
```dataview
TABLE file.cday AS "Created"
GROUP BY dateformat(file.cday, "yyyy-MM") AS Month
```

#### Query All Front Matter Keys
```dataview
TABLE file.frontmatter
WHERE file.frontmatter
```

---

## 6. Obsidian Dataview Plugin Patterns

### 6.1 Dashboard Patterns

#### Project Dashboard
```dataview
TABLE status, due, priority
FROM #project
WHERE status != "completed"
SORT priority DESC, due ASC
```

#### Task Overview
```dataview
TASK
WHERE !completed
GROUP BY file.link
SORT rows.file.ctime ASC
```

#### Reading List
```dataview
TABLE author, rating, status
FROM #book
WHERE status = "to-read" OR status = "reading"
SORT rating DESC
```

### 6.2 Dynamic Date Patterns

#### This Week's Notes
```dataview
LIST
WHERE file.cday >= date(today) - dur(7 days)
SORT file.cday DESC
```

#### Upcoming Deadlines
```dataview
TABLE due, project
FROM #task
WHERE due AND due > date(today) AND due <= date(today) + dur(14 days)
SORT due ASC
```

#### Birthdays This Month
```dataview
LIST birthday
WHERE birthday.month = date(now).month
```

### 6.3 Aggregation Patterns

#### Count by Tag
```dataview
TABLE length(rows) AS Count
FROM #project
GROUP BY type
```

#### Average Rating by Genre
```dataview
TABLE average(rating) AS "Avg Rating", length(rows) AS Count
FROM #book
GROUP BY genre
```

#### Time Tracking Summary
```dataview
TABLE sum(hours) AS "Total Hours", average(hours) AS "Average"
FROM #log
GROUP BY project
```

### 6.4 Table Customization

#### Custom Column Headers
```dataview
TABLE 
  author AS "Author",
  published AS "Published",
  default(finished, date(today)) - started AS "Days Reading"
FROM #book
```

#### TABLE WITHOUT ID
```dataview
TABLE WITHOUT ID
  file.link AS "Book",
  rating AS "★"
FROM #book
SORT rating DESC
```

### 6.5 Task Management Patterns

#### Tasks by Project
```dataview
TASK
FROM #project
WHERE !completed
GROUP BY file.link
```

#### Overdue Tasks
```dataview
TASK
WHERE !completed AND due AND due < date(today)
SORT due ASC
```

#### Tasks with Metadata
```dataview
TASK
WHERE !completed AND contains(tags, "#urgent")
GROUP BY file.link
```

### 6.6 Inline Queries

Display single values anywhere in notes:

```markdown
Total books read this year: `= length(filter([[]], (b) => b.status = "completed"))`

Days until deadline: `= this.due - date(today)`

Average project rating: `= average(map(this.file.inlinks, (f) => f.rating))`
```

### 6.7 JavaScript Queries (DataviewJS)

For complex logic beyond DQL:

```dataviewjs
const pages = dv.pages("#project")
  .where(p => p.status === "active")
  .sort(p => p.priority, 'desc');

dv.table(
  ["Project", "Priority", "Progress"],
  pages.map(p => [
    p.file.link,
    p.priority,
    p.progress + "%"
  ])
);
```

### 6.8 Best Practices for Dataview

1. **Always use FROM**: Restrict queries to specific folders/tags for performance
2. **Type checking**: Use `typeof(field) = "date"` to avoid errors
3. **Default values**: Use `default(field, fallback)` for missing data
4. **Sanitize keys**: Use lowercase-kebab-case for property names
5. **Test incrementally**: Build queries step by step
6. **Document queries**: Comment complex queries with purpose

---

## Summary and Recommendations

### Quick Start Checklist

1. **Define your core schema** (3-5 fields):
   - `type` (note type)
   - `created` (date)
   - `tags` (categories)
   - `status` (workflow state)

2. **Choose your organizational approach**:
   - Tags for categories and status
   - Links for relationships and topics
   - Properties for structured data

3. **Create templates** with Templater:
   - Dynamic date insertion
   - Prompts for key metadata
   - Consistent structure

4. **Build dashboards** with Dataview:
   - Project overview tables
   - Task lists
   - Recent notes

5. **Iterate and refine**:
   - Start simple
   - Add fields as needed
   - Document your conventions

### Key Takeaways

- **Consistency is king**: Use standard field names across all notes
- **Type safety matters**: Proper typing enables powerful queries
- **Combine approaches**: Tags, links, and properties work best together
- **Automate where possible**: Use templates and plugins to reduce friction
- **Query for insight**: Dataview transforms your vault into a queryable database

---

## References

- [Dataview Documentation](https://blacksmithgu.github.io/obsidian-dataview/)
- [Obsidian Properties Help](https://help.obsidian.md/properties)
- [Templater Documentation](https://silentvoid13.github.io/Templater/)
- [Obsidian Rocks - Properties Guide](https://obsidian.rocks/an-introduction-to-obsidian-properties/)
- [Planet Tash - Tags vs Links](https://planettash.com/2025/05/28/obsidian-tags-vs-links-which-should-you-use/)
- [Ithy - Frontmatter in Obsidian](https://ithy.com/article/frontmatter-in-obsidian-qxhwc37n)
- [TfTHacker - Frontmatter and Templater](https://medium.com/obsidian-observer/hacking-obsidian-frontmatter-and-templater-f4912a689cdc)

---

*This report was generated as part of a deep research initiative on PKM metadata management.*
