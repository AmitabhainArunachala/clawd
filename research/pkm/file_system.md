# File System Organization for Personal Knowledge Management (PKM)

A comprehensive guide to robust file system organization for PKM systems.

---

## Table of Contents

1. [Folder Structure Patterns](#1-folder-structure-patterns)
2. [File Naming Conventions](#2-file-naming-conventions)
3. [Attachment Management](#3-attachment-management)
4. [Version Control for Notes](#4-version-control-for-notes)
5. [Cross-Platform Sync Strategies](#5-cross-platform-sync-strategies)
6. [Backup and Archival Patterns](#6-backup-and-archival-patterns)

---

## 1. Folder Structure Patterns

### 1.1 PARA Method

**Created by:** Tiago Forte  
**Best for:** Action-oriented organization focused on projects and goals

PARA stands for **Projects, Areas, Resources, Archives** — four categories that encompass all information in your life.

#### Structure
```
/
├── 1-Projects/
│   ├── Complete web page design/
│   ├── Buy new computer/
│   ├── Write research report/
│   └── Renovate bathroom/
├── 2-Areas/
│   ├── Health/
│   ├── Finances/
│   ├── Marketing/
│   ├── Direct Reports/
│   └── Home/
├── 3-Resources/
│   ├── Graphic design/
│   ├── Personal productivity/
│   ├── Coffee/
│   ├── Modern architecture/
│   └── Marketing assets/
└── 4-Archives/
    ├── Completed projects/
    ├── Previous roles/
    └── Old interests/
```

#### Key Principles

1. **Organize by actionability, not by topic** — Everything is organized by what you're actively working on
2. **Projects have deadlines/goals; Areas are ongoing** — "Renovate bathroom" (project) vs "Home" (area)
3. **Resources are reference material** — Topics you're interested in but not actively working on
4. **Archives store inactive items** — Completed projects, outdated resources, former responsibilities

#### Pros
- Clear distinction between active and inactive work
- Reduces cognitive load by focusing on current priorities
- Works across all platforms (file system, cloud storage, note apps)

#### Cons
- Can be too project-focused for research-heavy workflows
- Requires regular maintenance to move items to Archives
- May conflict with Zettelkasten-style permanent note storage

#### Variations

**PARA + Inbox**: Add a `0-Inbox` folder at the top level for quick capture:
```
/
├── 0-Inbox/           # Daily notes, quick captures
├── 1-Projects/
├── 2-Areas/
├── 3-Resources/
└── 4-Archives/
```

---

### 1.2 Johnny Decimal System

**Created by:** Johnny Noble  
**Best for:** Large-scale organization requiring precise retrieval

A system that assigns unique numeric IDs to everything, limiting hierarchy to manageable chunks.

#### Structure
```
/
├── 10-19 Life admin/
│   ├── 11 Me/
│   ├── 12 House/
│   ├── 13 Money/
│   ├── 14 Online/
│   └── 15 Travel/
├── 20-29 Work/
│   ├── 21 Projects/
│   ├── 22 Clients/
│   ├── 23 Finances/
│   └── 24 Operations/
├── 30-39 Hobbies/
│   ├── 31 Tennis/
│   └── 32 Photography/
└── 90-99 System/
    ├── 91 Templates/
    └── 92 Archive/
```

#### Key Principles

1. **10 Areas maximum** — Major divisions of your life (numbered 10-19, 20-29, etc.)
2. **10 Categories per Area** — Subdivisions within each area (11, 12, 13...)
3. **100 IDs per Category** — Individual items (11.01, 11.02, 15.23)
4. **Format: XX.YY** — Category.ID (e.g., "15.23 Travel insurance")

#### Numbering System

| Level | Format | Example | Description |
|-------|--------|---------|-------------|
| Area | 10-19, 20-29 | 10-19 Life admin | Top-level divisions |
| Category | 11, 12, 13 | 15 Travel | Subdivisions |
| ID | 15.01, 15.23 | 15.23 Travel insurance | Individual items |

#### Benefits of Numeric IDs

- **Muscle memory**: Numbers stay in place; alphabetical folders shift
- **Easy communication**: "Check 15.23" vs "Check the travel folder then the insurance subfolder"
- **Imposes limits**: Forces you to keep categories focused (max 10 per area)
- **Predictable structure**: Always know where to look

#### Pros
- Extremely scalable for large collections
- Predictable retrieval without searching
- Works across all systems (files, notes, email, physical)

#### Cons
- Steeper learning curve
- Requires maintaining an index
- Can feel rigid for creative workflows

---

### 1.3 Zettelkasten Structure

**Origins:** Niklas Luhmann's slip-box system  
**Best for:** Research, academic work, and knowledge building

A flat structure emphasizing note relationships over folder hierarchy.

#### Structure
```
/
├── 0000000000 Index.md
├── 0000000001 Introduction to topic.md
├── 0000000002 Related concept.md
├── 0000000002a Sub-concept A.md
├── 0000000002b Sub-concept B.md
├── 0000000003 Another topic.md
├── Literature/
│   ├── @Author2023_TitleOfWork.md
│   └── @Smith2022_AnotherWork.md
└── Fleeting/
    ├── Daily notes/
    └── Random thoughts/
```

#### Key Principles

1. **Unique identifiers** — Each note gets a unique ID (timestamp or sequential)
2. **Atomic notes** — One idea per note
3. **Link everything** — Notes connect via `[[links]]`, not folders
4. **Flat hierarchy** — Minimal folder structure; organization through linking

#### ID Formats

| Format | Example | Use Case |
|--------|---------|----------|
| Luhmann | 1, 1a, 1a1 | Traditional branching |
| Timestamp | 20240206113000 | Creation-time based |
| UUID | 8f3a2b1c | Guaranteed uniqueness |

#### Pros
- Emergent organization through linking
- Supports discovery of unexpected connections
- Timeless for research and writing

#### Cons
- Requires discipline to maintain links
- Can become unwieldy without periodic review
- Steep learning curve for beginners

---

### 1.4 Hybrid Approaches

Many practitioners combine systems for optimal results:

#### PARA + Johnny Decimal
```
/
├── 10-19 Projects/
│   ├── 11 Active/
│   │   ├── 11.01 Website redesign/
│   │   └── 11.02 Course creation/
│   └── 12 On-hold/
├── 20-29 Areas/
├── 30-39 Resources/
└── 90-99 Archives/
```

#### PARA + Zettelkasten
```
/
├── 1-Projects/
│   └── Use PARA for project organization
├── 2-Areas/
├── 3-Resources/
│   └── Knowledge/         # Flat Zettelkasten here
│       ├── 0001 Concept.md
│       ├── 0002 Related.md
│       └── 0002a Detail.md
└── 4-Archives/
```

#### Role-Based Structure
```
/
├── 00-Inbox/
├── 01-Personal/
│   ├── Health/
│   ├── Family/
│   └── Hobbies/
├── 02-Work/
│   ├── Projects/
│   ├── Meetings/
│   └── Admin/
├── 03-Learning/
│   ├── Books/
│   ├── Courses/
│   └── Research/
└── 99-Archive/
```

---

## 2. File Naming Conventions

### 2.1 Date-Based Naming (Chronological)

**Format:** `YYYY-MM-DD-Title` or `YYYYMMDD_Title`

#### Examples
```
2024-02-06-Meeting-with-team.md
20240206_project_proposal.pdf
2024-01-15_journal_entry.md
```

#### Pros
- Automatic chronological sorting
- Easy to find by time period
- Works across all operating systems

#### Cons
- Can obscure content without reading full name
- Duplicate titles need distinguishing

#### Variations

| Format | Example | Sorts By |
|--------|---------|----------|
| ISO 8601 | 2024-02-06 | Date |
| Compact | 20240206 | Date |
| With time | 2024-02-06-1130 | Date + time |
| Reverse | 240206 | Date (short) |

---

### 2.2 Zettelkasten Naming

**Format:** `ID Title` or `ID-Title`

#### Examples
```
0000000001 Introduction to PKM.md
0000000002 Folder structures.md
0000000002a PARA method.md
202402061130 Daily reflection.md
```

#### Pros
- Guaranteed unique names
- Supports branching (2 → 2a, 2b)
- Links remain stable forever

#### Cons
- IDs aren't meaningful
- Requires lookup for context

---

### 2.3 Descriptive Naming

**Format:** `Category-Subcategory-Title` or `Context-Action-Outcome`

#### Examples
```
Project-WebsiteRedesign-Requirements.md
Meeting-Engineering-2024-02-06.md
Research-PKM-FolderStructures.md
Book-AtomicHabits-Notes.md
```

#### Pros
- Self-describing
- Easy to scan visually
- No lookup needed

#### Cons
- Longer names
- Alphabetical sorting may split related items

---

### 2.4 Best Practices

#### General Rules

1. **Use hyphens or underscores** — Not spaces (cross-platform compatibility)
2. **Avoid special characters** — `/:?"<>|` cause issues on various systems
3. **Be consistent** — Pick one style and stick to it
4. **Include version numbers when needed** — `document-v1.2.md`
5. **Keep it readable** — Future you needs to understand it

#### File Naming Templates

| Use Case | Template | Example |
|----------|----------|---------|
| Daily notes | `YYYY-MM-DD` | 2024-02-06.md |
| Meeting notes | `YYYY-MM-DD-Meeting-Topic` | 2024-02-06-Meeting-Q1-Planning.md |
| Project files | `ProjectName-DocumentType` | Website-Requirements.md |
| Research | `Topic-Subtopic-Source` | PKM-PARA-Research.md |
| Templates | `Template-Purpose` | Template-Meeting.md |

---

## 3. Attachment Management

### 3.1 Centralized Attachment Folder

**Structure:** Single folder for all attachments

```
/
├── Notes/
│   └── Various markdown files
└── Attachments/
    ├── 2024-02-06-meeting-notes.pdf
    ├── diagram-01.png
    ├── article-screenshot.jpg
    └── spreadsheet.xlsx
```

#### Settings (Obsidian)
- **Default location:** `In the folder specified below`
- **Attachment folder path:** `Attachments`

#### Pros
- Simple to manage
- Easy to back up attachments separately
- No orphaned attachments when notes move

#### Cons
- Can become unwieldy with many files
- Loses context of which note uses which attachment

---

### 3.2 Subfolder by File Type

**Structure:** Organize attachments by type

```
/
├── Notes/
└── Attachments/
    ├── Images/
    │   ├── 2024-02-06-diagram.png
    │   └── screenshot.jpg
    ├── PDFs/
    │   ├── research-paper.pdf
    │   └── invoice-2024-01.pdf
    ├── Documents/
    │   └── spreadsheet.xlsx
    └── Audio/
        └── recording-2024-02-06.mp3
```

#### Pros
- Easy to find by type
- Simplifies bulk operations (resize all images, etc.)

#### Cons
- Multiple folders to manage
- Still loses note context

---

### 3.3 Subfolder Under Current Note

**Structure:** Each note gets its own attachment folder

```
/
└── Projects/
    └── Website Redesign/
        ├── Website Redesign.md
        └── Website Redesign_attachments/
            ├── mockup-01.png
            ├── mockup-02.png
            └── requirements.pdf
```

#### Settings (Obsidian)
- **Default location:** `In subfolder under current file`
- **Subfolder name:** `{{filename}}_attachments`

#### Pros
- Attachments stay with their note
- Easy to move note + attachments together
- Clear context

#### Cons
- Many small folders scattered throughout vault
- Harder to find attachments across notes

---

### 3.4 Hybrid: Type-Based with Note Reference

**Structure:** Type folders with note reference in filename

```
/
├── Notes/
│   └── 2024-02-06-Project-Meeting.md
└── Attachments/
    ├── Images/
    │   ├── 2024-02-06-Project-Meeting-whiteboard.png
    │   └── 2024-02-06-Project-Meeting-diagram.png
    └── PDFs/
        └── 2024-02-06-Project-Meeting-handout.pdf
```

#### Pros
- Best of both worlds
- Maintainable structure
- Easy to locate attachments

#### Cons
- Requires discipline in naming
- Longer filenames

---

### 3.5 Best Practices for Attachments

1. **Use descriptive filenames** — Include date and context
2. **Optimize file sizes** — Compress images, don't store huge files unnecessarily
3. **Consider external storage** — Large files (videos, archives) in cloud storage with links in notes
4. **Regular cleanup** — Remove unused attachments periodically
5. **Version control considerations** — Binary files bloat git repositories

---

## 4. Version Control for Notes

### 4.1 Why Use Git for PKM?

| Benefit | Description |
|---------|-------------|
| Version history | See every change, revert to any point |
| Sync across devices | Pull/push between computers |
| Backup | GitHub/GitLab as remote backup |
| Collaboration | Share notes, work together |
| Audit trail | Track when ideas evolved |

---

### 4.2 Git Setup for Obsidian

#### Basic Repository Structure

```
pkm-vault/
├── .git/                    # Git internals
├── .gitignore              # Files to exclude
├── .obsidian/              # Obsidian settings
│   ├── app.json
│   ├── appearance.json
│   └── ...
├── Daily/                  # Your notes
├── Projects/
├── Areas/
└── Resources/
```

#### .gitignore Template

```gitignore
# Obsidian settings that shouldn't be shared
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# Plugins (optional - include if you want to sync plugins)
# .obsidian/plugins/

# Large files that shouldn't be versioned
*.mp4
*.mov
*.zip
*.dmg

# OS files
.DS_Store
Thumbs.db
```

---

### 4.3 Obsidian Git Plugin

**Plugin:** [obsidian-git](https://github.com/Vinzent03/obsidian-git) by Vinzent

#### Features
- Automatic commit and push
- Visual diff of changes
- Pull/push from within Obsidian
- Backup reminders
- Works on desktop and mobile (with Working Copy on iOS)

#### Configuration

1. Install plugin from Community Plugins
2. Configure backup settings:
   - **Backup interval:** 30 minutes
   - **Auto pull on startup:** Enabled
   - **Auto push after commit:** Enabled
   - **Commit message:** `{{date}} {{hostname}}`

#### Mobile Setup (iOS)

1. Install [Working Copy](https://workingcopyapp.com/) app
2. Clone your repository
3. In Obsidian Git settings:
   - Enable "Working Copy" integration
   - Set repository path

---

### 4.4 Command Line Workflow

#### Initial Setup

```bash
# Navigate to vault
cd ~/Documents/ObsidianVault

# Initialize repository
git init

# Add remote (GitHub/GitLab)
git remote add origin https://github.com/username/pkm-vault.git

# Initial commit
git add .
git commit -m "Initial vault setup"
git push -u origin main
```

#### Daily Workflow

```bash
# Pull latest changes
git pull

# Make changes to notes...

# Stage and commit
git add .
git commit -m "2024-02-06 Daily notes and project updates"

# Push to remote
git push
```

#### Useful Commands

| Command | Purpose |
|---------|---------|
| `git log --oneline` | View commit history |
| `git diff` | See uncommitted changes |
| `git checkout <commit>` | View old version |
| `git revert <commit>` | Undo a commit |
| `git stash` | Temporarily save changes |

---

### 4.5 Alternative: Obsidian Sync Version History

If using official [Obsidian Sync](https://obsidian.md/sync):

- **Standard tier:** 1 month version history
- **Plus tier:** 12 month version history
- Access via: File → Open version history

---

## 5. Cross-Platform Sync Strategies

### 5.1 Comparison Matrix

| Method | Windows | Mac | Linux | iOS | Android | Cost | Ease |
|--------|---------|-----|-------|-----|---------|------|------|
| Obsidian Sync | ✅ | ✅ | ✅ | ✅ | ✅ | $4-8/mo | Easy |
| iCloud | ✅* | ✅ | ❌ | ✅ | ❌ | Free | Easy |
| Dropbox | ✅ | ✅ | ✅ | ✅** | ✅** | Free/Paid | Medium |
| Git | ✅ | ✅ | ✅ | ✅*** | ✅*** | Free | Hard |
| Syncthing | ✅ | ✅ | ✅ | ✅**** | ✅ | Free | Medium |
| Remotely Save | ✅ | ✅ | ✅ | ✅ | ✅ | Free | Medium |

\* Known for duplication issues on Windows  
\** Requires third-party apps (Dropsync, FolderSync)  
\*** Requires Working Copy (iOS) or Git client  
\**** Requires Mobius Sync or SyncTrain on iOS

---

### 5.2 Official Obsidian Sync

**Best for:** Users wanting simplicity and reliability

#### Features
- End-to-end encryption
- Version history
- Selective sync (exclude folders)
- Plugin and settings sync
- Works offline

#### Pricing
- **Standard:** $4/month (1 vault, 1GB, 1 month history)
- **Plus:** $8/month (10 vaults, 10GB, 12 month history)

---

### 5.3 Git-Based Sync

**Best for:** Technical users, developers, version control enthusiasts

#### Setup

1. Create repository on GitHub/GitLab
2. Clone to all devices
3. Use Obsidian Git plugin or command line
4. Commit/push after changes, pull before starting

#### Workflow
```
Device A: Edit → Commit → Push
Device B: Pull → Edit → Commit → Push
Device A: Pull → Continue editing
```

#### Handling Conflicts

Git conflicts in markdown are rare but possible:

1. Open conflicted file
2. Look for `<<<<<<< HEAD` markers
3. Choose which version to keep (or merge manually)
4. Commit the resolution

---

### 5.4 Cloud Storage (Dropbox, iCloud, OneDrive)

**Best for:** Users already paying for cloud storage

#### Desktop Setup
1. Move vault to cloud storage folder
2. Let cloud service sync
3. Open vault from cloud location on each device

#### Mobile Limitations
- iOS restricts file system access
- Cannot directly open vaults in cloud folders
- Requires "Remotely Save" plugin or Obsidian Sync

#### iCloud Specifics
```
On Mac:
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/VaultName

On iOS:
Files app → iCloud Drive → Obsidian → VaultName
```

⚠️ **Warning:** iCloud on Windows has reported issues with file duplication and conflicts.

---

### 5.5 Remotely Save Plugin

**Best for:** Cross-platform free sync with existing cloud storage

#### Supported Services
- Dropbox
- OneDrive
- Amazon S3 / S3-compatible (Cloudflare R2, Wasabi)
- WebDAV
- Google Drive (limited)

#### Setup
1. Install Remotely Save plugin
2. Configure your service credentials
3. Set sync direction (bidirectional recommended)
4. Enable auto-sync or manual trigger

---

### 5.6 Hybrid Approaches

#### Desktop + Mobile Split
- **Desktop:** Vault in Dropbox/iCloud folder
- **Mobile:** Use Remotely Save to sync same Dropbox

#### Work + Personal Split
- **Personal:** Obsidian Sync ($4/month)
- **Work:** Git repository (firewall-friendly, no external services)

---

## 6. Backup and Archival Patterns

### 6.1 The 3-2-1 Backup Rule

| Number | Rule |
|--------|------|
| 3 | Keep 3 copies of important data |
| 2 | Store on 2 different media types |
| 1 | Keep 1 copy offsite |

#### PKM Application

```
Copy 1: Local device (your working vault)
Copy 2: Cloud sync (iCloud/Dropbox/Obsidian Sync)
Copy 3: Remote backup (GitHub, separate cloud)
```

---

### 6.2 Backup Strategies

#### Strategy A: Git as Backup

```
Local → GitHub → (GitHub is your offsite backup)
```

**Pros:** Version history, free, reliable  
**Cons:** Learning curve, binary files don't version well

#### Strategy B: Cloud + Local Archive

```
Working vault: iCloud/Dropbox (synced)
Monthly: Export to external drive
Yearly: Archive to cold storage
```

#### Strategy C: Obsidian Sync + Export

```
Daily: Obsidian Sync
Weekly: Export to PDF/markdown archive
Monthly: Copy to external drive
```

---

### 6.3 Archival Patterns

#### Time-Based Archive

```
/
├── 00-Active/              # Current work
├── 01-This-Year/           # 2024 notes
├── 02-Last-Year/           # 2023 notes
└── 03-Archive/             # Everything older
    ├── 2022/
    ├── 2021/
    └── 2020/
```

#### Project-Based Archive

```
/
├── 1-Projects/
│   └── Active projects here
└── 4-Archives/
    ├── Projects-2024/
    ├── Projects-2023/
    └── Projects-2022/
```

#### Automated Archive (with Git)

```bash
# Tag significant versions
git tag -a v2024-Q1 -m "First quarter 2024 archive"

# Create archive branch
git checkout -b archive/2023

# Or export to separate archive repository
git archive --format=zip -o ~/backups/pkm-2023.zip archive/2023
```

---

### 6.4 Export Formats for Long-Term Storage

| Format | Pros | Cons |
|--------|------|------|
| Markdown | Plain text, future-proof | Needs renderer for viewing |
| PDF | Self-contained, readable | Not editable, larger files |
| HTML | Preserves links, styled | Requires browser |
| JSON | Structured, parseable | Not human-readable |

#### Recommended: Markdown + PDF

1. **Primary:** Keep everything in Markdown (future-proof)
2. **Archive:** Export important notes to PDF annually
3. **Insurance:** Plain text exports ensure you can always read your notes

---

### 6.5 Disaster Recovery Checklist

- [ ] Test restore from backup quarterly
- [ ] Verify GitHub/GitLab repository is accessible
- [ ] Keep offline copy on external drive
- [ ] Document your folder structure (so you can rebuild)
- [ ] Export critical notes to PDF annually
- [ ] Test opening vault on clean device

---

## Summary: Recommended Setup

### For Most Users

```
Folder Structure: PARA + Inbox
File Naming: YYYY-MM-DD-Descriptive-Title
Attachments: Subfolder by type
Sync: Obsidian Sync (or Git for technical users)
Backup: GitHub + external drive
```

### For Researchers/Academics

```
Folder Structure: PARA + Zettelkasten (Resources folder)
File Naming: Timestamp + Title
Attachments: Subfolder under current note
Sync: Git (for version history of ideas)
Backup: GitHub + institutional cloud
```

### For Large Organizations

```
Folder Structure: Johnny Decimal
File Naming: Category-ID-Description
Attachments: Centralized with index
Sync: Self-hosted or enterprise cloud
Backup: Multiple redundant systems
```

---

## Resources

### Tools Mentioned
- [Obsidian](https://obsidian.md/)
- [obsidian-git plugin](https://github.com/Vinzent03/obsidian-git)
- [Remotely Save](https://github.com/remotely-save/remotely-save)
- [Working Copy](https://workingcopyapp.com/) (iOS Git client)
- [Syncthing](https://syncthing.net/)

### Further Reading
- [The PARA Method - Tiago Forte](https://fortelabs.com/blog/para/)
- [Johnny Decimal](https://johnnydecimal.com/)
- [Zettelkasten.de](https://zettelkasten.de/)

---

*Last updated: 2024-02-06*
