# PKM System Architecture and Design Patterns

## Research Summary: Leading-Edge Personal Knowledge Management Systems

**Date Researched:** February 2026  
**Focus Areas:** Input/Process/Output flows, CODE methodology, Progressive Summarization, JIT vs JIC, Actionability, Second Brain Architecture

---

## Table of Contents

1. [Input → Process → Output Flows](#1-input--process--output-flows)
2. [Capture, Clarify, Organize, Reflect, Engage (CCORE)](#2-capture-clarify-organize-reflect-engage-ccore)
3. [Progressive Summarization](#3-progressive-summarization)
4. [Just-in-Time vs Just-in-Case](#4-just-in-time-vs-just-in-case)
5. [Actionability in Note Systems](#5-actionability-in-note-systems)
6. [Building a Second Brain Architecture](#6-building-a-second-brain-architecture)
7. [Architectural Patterns Summary](#7-architectural-patterns-summary)

---

## 1. Input → Process → Output Flows

### The Fundamental PKM Pipeline

At its core, every PKM system follows a three-stage pipeline that mirrors creative and cognitive processes:

```
┌─────────┐    ┌──────────┐    ┌─────────┐
│  INPUT  │ →  │ PROCESS  │ →  │ OUTPUT  │
└─────────┘    └──────────┘    └─────────┘
```

#### Stage 1: Input (Capture)

The input stage is where external information enters the system. Key characteristics:

- **Multi-modal ingestion**: Text, audio, video, images, conversations, thoughts
- **Friction reduction**: The best systems minimize capture friction—if it's hard to capture, it won't be captured
- **Universal capture**: Ideas can come from anywhere (books, articles, podcasts, conversations, shower thoughts)
- **Immediate capture**: Don't rely on memory; capture immediately to preserve context

**Input Sources:**
- Reading (articles, books, research papers)
- Listening (podcasts, lectures, conversations)
- Watching (videos, presentations, demonstrations)
- Thinking (reflections, insights, ideas)
- Experiencing (meetings, events, experiments)

#### Stage 2: Process (Transform)

The process stage is where raw input becomes useful knowledge:

- **Clarification**: Understanding what was captured
- **Contextualization**: Adding metadata (source, date, tags, links)
- **Connection**: Linking to existing knowledge
- **Distillation**: Extracting essence from noise
- **Synthesis**: Combining multiple sources into new insights

**Processing Patterns:**
1. **Immediate processing**: Handle items as they arrive (GTD-style)
2. **Batch processing**: Set aside dedicated time for processing (daily/weekly)
3. **Progressive processing**: Multiple passes with increasing depth

#### Stage 3: Output (Express)

The output stage is where knowledge becomes action or creation:

- **Action**: Tasks, projects, decisions
- **Creation**: Writing, presentations, products
- **Sharing**: Teaching, collaboration, publication
- **Retrieval**: Finding information when needed

**Output Types:**
| Output Type | Description | Example |
|-------------|-------------|---------|
| Immediate Action | Tasks to do now | Add to todo list |
| Project Material | Content for ongoing work | Draft document section |
| Reference | Information for future use | Saved to knowledge base |
| Archive | Completed/outdated items | Move to cold storage |

### The Extended Pipeline: CODE Methodology

Tiago Forte's CODE framework extends the basic pipeline:

```
CAPTURE → ORGANIZE → DISTILL → EXPRESS
   ↓         ↓          ↓         ↓
  Input   Structure   Refine    Create
```

**Key Insight**: The pipeline is not linear—it's iterative. Output often becomes new input (feedback loops).

---

## 2. Capture, Clarify, Organize, Reflect, Engage (CCORE)

### The Five-Stage Knowledge Workflow

This framework synthesizes GTD (Getting Things Done) principles with PKM practices:

#### Stage 1: Capture

**Principle**: Get everything out of your head and into a trusted system.

**Capture Heuristics:**
- Capture what **resonates**—not everything
- Capture when **emotionally resonant**—interest is highest
- Capture the **source**—preserve provenance
- Capture **quickly**—minimize friction

**Capture Tools & Methods:**
| Method | Best For | Friction Level |
|--------|----------|----------------|
| Quick capture apps | Fleeting thoughts | Very Low |
| Read-later services | Articles to process | Low |
| Voice memos | Ideas on-the-go | Low |
| Highlighting | Key passages | Medium |
| Full notes | Deep reading | High |

#### Stage 2: Clarify

**Principle**: Process captured material to understand what it means to you.

**Clarification Questions:**
1. What is this?
2. Is it actionable?
3. What's the desired outcome?
4. What's the next action?
5. Does it connect to existing knowledge?

**The Clarification Decision Tree:**
```
                    [Captured Item]
                         │
                    Is it actionable?
                   /                \
                 YES                 NO
                /                      \
       [Can it be done    Is it reference
        in 2 minutes?]    material?
            /    \           /        \
          YES    NO        YES         NO
           |      |         |          |
       [Do it] [Add to    [File in    [Delete or
               task list]  system]    archive]
```

#### Stage 3: Organize

**Principle**: Structure information by actionability, not by topic.

**PARA Organization System:**

| Category | Definition | Example |
|----------|------------|---------|
| **P**rojects | Short-term efforts with deadlines | "Launch website by March" |
| **A**reas | Long-term responsibilities without deadlines | "Health", "Finances", "Career" |
| **R**esources | Topics of ongoing interest | "Machine Learning", "Recipes" |
| **A**rchives | Inactive items from other categories | Completed projects, old resources |

**Why PARA Works:**
- **Actionability-first**: Organization supports doing, not just knowing
- **Flexible**: Works across tools (files, notes, tasks, bookmarks)
- **Scalable**: Handles growth without restructuring
- **Universal**: Applies to all digital information

#### Stage 4: Reflect

**Principle**: Regular review transforms collection into understanding.

**Review Cadences:**

| Review Type | Frequency | Purpose |
|-------------|-----------|---------|
| Daily | Daily | Process inbox, plan day |
| Weekly | Weekly | Review projects, plan week |
| Monthly | Monthly | Review areas, check progress |
| Quarterly | Quarterly | Review resources, archive old |
| Yearly | Yearly | Full system review, goals |

**Reflection Practices:**
- **Random walks**: Browse your knowledge base to spark connections
- **Backlink exploration**: Follow links to rediscover related ideas
- **Graph visualization**: See note relationships visually
- **Search rediscovery**: Search for forgotten insights

#### Stage 5: Engage

**Principle**: Knowledge work culminates in action and creation.

**Engagement Patterns:**
1. **Retrieval**: Finding information when needed
2. **Synthesis**: Combining notes into new ideas
3. **Creation**: Producing outputs (writing, presentations)
4. **Teaching**: Explaining concepts to others
5. **Decision-making**: Using knowledge to make choices

---

## 3. Progressive Summarization

### The Layered Approach to Note-Taking

Progressive Summarization is a technique for creating "compressed" notes that remain useful over time. Instead of summarizing everything immediately, you create multiple layers of summarization that can be accessed as needed.

#### The Five Layers

```
Layer 5: The Remix          → Your own creation based on the source
Layer 4: The Summary        → Executive summary in your own words
Layer 3: The Highlights     → Key passages highlighted/quoted
Layer 2: The Notes          → Your annotations and thoughts
Layer 1: The Capture        → Full text or source saved
```

#### Layer Details

**Layer 1: Capture**
- Save the full article, book notes, or transcript
- Preserve the complete source
- Add basic metadata (title, author, date, URL)
- *Effort*: Minimal—just capture

**Layer 2: Notes**
- Add your own annotations
- Highlight key passages
- Write marginalia
- Make initial connections
- *Effort*: Light—while reading or shortly after

**Layer 3: Highlights**
- Extract the most important passages
- Bold or format key sentences
- Create a "highlights only" view
- *Effort*: Medium—requires judgment

**Layer 4: Summary**
- Write a 2-3 paragraph summary
- Use your own words
- Capture the main argument or insight
- *Effort*: Significant—requires synthesis

**Layer 5: Remix**
- Create something new from the source
- Use it in a project, article, or presentation
- Transform it into your own intellectual output
- *Effort*: Highest—creative work

#### Progressive Summarization Principles

1. **Don't summarize everything**: Only layers that prove useful
2. **Let use guide depth**: Frequently accessed notes get deeper layers
3. **Preserve the source**: Always keep Layer 1 for context
4. **Make it discoverable**: Good titles and links are essential
5. **Iterate over time**: Return to notes to add deeper layers

#### Implementation Strategy

**First Pass (Capture):**
- Save to read-later or note-taking app
- Add basic tags
- No immediate processing required

**Second Pass (if returning to note):**
- Read and highlight key passages
- Add brief annotations
- Create connections to other notes

**Third Pass (if note proves valuable):**
- Bold most important highlights
- Write a brief summary
- Consider how it applies to current projects

**Fourth Pass (when using for creation):**
- Write full summary
- Create new content from the source
- Publish or share insights

---

## 4. Just-in-Time vs Just-in-Case

### The Knowledge Acquisition Spectrum

This framework addresses a fundamental tension in knowledge work: should you learn things before you need them (just-in-case) or when you need them (just-in-time)?

#### Just-in-Case (JIC) Learning

**Definition**: Learning things that might be useful in the future, without a specific immediate need.

**Characteristics:**
- **Proactive**: Learning ahead of anticipated needs
- **Broad**: Covers wide range of topics
- **Theoretical**: Often abstract, not immediately applicable
- **Storage-oriented**: Emphasis on retention and recall

**When JIC is Valuable:**
- Foundational knowledge (math, language basics)
- Rarely needed but critical skills (emergency procedures)
- Building mental models for pattern recognition
- Exploration and curiosity-driven learning
- Preparing for known future challenges

**Risks of Pure JIC:**
- Information overload
- Low retention without application
- Wasted effort on unused knowledge
- Difficulty distinguishing signal from noise

#### Just-in-Time (JIT) Learning

**Definition**: Learning exactly what you need, exactly when you need it.

**Characteristics:**
- **Reactive**: Learning in response to immediate needs
- **Targeted**: Narrowly focused on specific problems
- **Applied**: Immediately put into practice
- **Retrieval-oriented**: Emphasis on finding, not memorizing

**When JIT is Valuable:**
- Solving specific problems
- Learning tools and technologies
- Research for projects
- Adapting to new situations
- Maximizing learning efficiency

**Risks of Pure JIT:**
- Gaps in foundational knowledge
- Inability to recognize patterns across domains
- Reactive rather than strategic thinking
- Missing opportunities due to lack of preparation

#### The Integrated Approach

**The 80/20 JIT/JIC Balance:**

```
┌─────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE                    │
├─────────────────────────────────────────────────────┤
│  ACTIVE PROJECTS (JIT)  │  REFERENCE MATERIAL (JIC) │
│  ┌─────────────────┐   │  ┌─────────────────────┐  │
│  │ Immediate needs │   │  │ Just-in-case        │  │
│  │ Targeted search │   │  │ Exploratory reading │  │
│  │ Problem-solving │   │  │ Curiosity-driven    │  │
│  │ Applied learning│   │  │ Long-term storage   │  │
│  └─────────────────┘   │  └─────────────────────┘  │
│         ↑↓                    ↑↓                    │
│    High retrieval          Serendipity             │
│    Specific use            Pattern building        │
└─────────────────────────────────────────────────────┘
```

**Practical Implementation:**

1. **Default to JIT for skills**: Learn tools and techniques when you need them
2. **Default to JIC for principles**: Build mental models and frameworks proactively
3. **Use progressive summarization**: JIC captured knowledge becomes JIT accessible
4. **Maintain a curiosity fund**: 10-20% of learning time for pure exploration
5. **Trust your PKM system**: Good organization makes JIC knowledge JIT accessible

**The JIT-JIC Conversion Cycle:**

```
1. CAPTURE (JIC) → Save interesting but not immediately needed information
         ↓
2. ORGANIZE → Structure for future retrieval
         ↓
3. DISCOVER (Serendipity) → Stumble upon during unrelated search
         ↓
4. APPLY (JIT) → Use when specific need arises
         ↓
5. CREATE → Transform into output
         ↓
6. SHARE → Teach others (reinforces learning)
```

---

## 5. Actionability in Note Systems

### From Information to Action

The ultimate purpose of PKM is not to collect information but to facilitate action. Actionability ensures your system serves your goals, not just your curiosity.

#### The Actionability Continuum

```
PURE INFORMATION ←──────────────────────→ PURE ACTION
     ↓                                         ↓
  Reference                               Next Actions
  Resources                               Projects
  Reading lists                           Task lists
  General notes                           Meeting outcomes
```

#### Making Information Actionable

**The GTD Actionability Filter:**

For any captured item, ask:

1. **Is it actionable?**
   - NO → Trash, incubate, or reference
   - YES → Continue to question 2

2. **What's the next action?**
   - Single action → Add to task list
   - Multiple actions → Create project

3. **Will it take < 2 minutes?**
   - YES → Do it now
   - NO → Delegate or defer

**The PKM Actionability Enhancement:**

Beyond GTD's binary actionability, PKM adds layers:

| Level | Type | Characteristics |
|-------|------|-----------------|
| 0 | Raw Information | No immediate use |
| 1 | Potential Action | Might lead to action |
| 2 | Project Support | Useful for current project |
| 3 | Direct Action | Is an action item |
| 4 | Completed Action | Already acted upon |

#### PARA and Actionability

The PARA method is built on actionability as the primary organizing principle:

**Projects (Most Actionable):**
- Have deadlines or target dates
- Require multiple actions
- Clear outcome defined
- Active work happening

**Areas (Moderately Actionable):**
- Ongoing responsibilities
- Standards to maintain
- No specific deadline
- Regular attention needed

**Resources (Low Actionability):**
- Reference material
- Topics of interest
- Used when needed
- No immediate application

**Archives (Not Actionable):**
- Completed or inactive
- Preserved for reference
- No current relevance
- Available if needed

#### Actionability Patterns

**Pattern 1: The Project-Note Link**
- Every project has associated notes
- Notes link to specific project actions
- Context is always available

**Pattern 2: The Action-Reference Bridge**
- Actions reference source notes
- Notes contain actionable insights
- Bidirectional linking maintains context

**Pattern 3: The Output-First Approach**
- Start with desired output
- Gather only relevant information
- Organize around creation

#### Implementation Strategies

**Strategy 1: Action-First Tagging**
```
#action-required     → Needs immediate attention
#project-support     → Relevant to active projects
#someday-maybe       → Potential future action
#reference-only      → No action needed
```

**Strategy 2: Inbox Processing Rules**
1. Process inbox daily
2. Convert notes to actions when applicable
3. Link actions to supporting notes
4. Archive or delete non-actionable items

**Strategy 3: Weekly Action Review**
- Review all active projects
- Identify notes that need action
- Update action lists
- Archive completed items

---

## 6. Building a Second Brain Architecture

### The External Knowledge System

A "Second Brain" is an external, integrated digital system for saving and retrieving information, enabling creative output. The architecture combines multiple methodologies into a unified system.

#### Core Architecture Components

```
┌────────────────────────────────────────────────────────────┐
│                    SECOND BRAIN ARCHITECTURE                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   CAPTURE   │→│   PROCESS   │→│   CREATE    │        │
│  │   LAYER     │  │   LAYER     │  │   LAYER     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         ↓                ↓                ↓               │
│    ┌─────────┐     ┌─────────┐     ┌─────────┐           │
│    │Inboxes  │     │PARA     │     │Projects │           │
│    │Sources  │     │Links    │     │Outputs  │           │
│    │Quick    │     │Tags     │     │Publish  │           │
│    │Capture  │     │Notes    │     │Share    │           │
│    └─────────┘     └─────────┘     └─────────┘           │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              STORAGE & RETRIEVAL LAYER               │  │
│  │     (Notes, Files, Tasks, Bookmarks, Media)         │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### The CODE Framework in Detail

**C - Capture: Keep What Resonates**

*Principles:*
- Capture quickly, process later
- Don't filter during capture
- Use the quickest possible method
- Centralize in inboxes

*Capture Methods by Context:*
| Context | Method | Tool Examples |
|---------|--------|---------------|
| Reading articles | Read-later + highlighting | Pocket, Instapaper |
| Reading books | Highlights + notes | Kindle, physical + photo |
| Meetings | Quick notes + voice | Note apps, voice memos |
| Ideas | Instant capture | Quick-add widgets |
| Browsing | Bookmarks + clips | Browser extensions |

**O - Organize: Save for Actionability**

*The PARA Structure:*

```
Second Brain/
├── 00 Inbox/              ← Temporary holding
├── 01 Projects/           ← Active, deadline-driven work
│   ├── Website Redesign/
│   ├── Q1 Planning/
│   └── Vacation Planning/
├── 02 Areas/              ← Ongoing responsibilities
│   ├── Health/
│   ├── Finances/
│   ├── Career/
│   └── Relationships/
├── 03 Resources/          ← Reference topics
│   ├── Productivity/
│   ├── Programming/
│   ├── Recipes/
│   └── Travel/
└── 04 Archives/           ← Inactive from above
    ├── Completed Projects/
    ├── Previous Years Areas/
    └── Old Resources/
```

*Why PARA Works:*
- Mirrors how we naturally think about work
- Separates actionable from reference
- Grows organically without restructuring
- Works across any tool or platform

**D - Distill: Find the Essence**

*Progressive Summarization in Practice:*

1. **Bold** the best parts of what you've highlighted
2. **Summarize** sections in your own words at the top
3. **Extract** the key insight as a standalone note
4. **Connect** to existing knowledge with links

*The Executive Summary Method:*
Every note should answer:
- What's the main idea?
- Why does it matter?
- How can I use this?

**E - Express: Show Your Work**

*The Output Flywheel:*

```
     ┌──────────────┐
     │   CAPTURE    │
     │   Ideas      │
     └──────┬───────┘
            ↓
     ┌──────────────┐
     │  ORGANIZE    │
     │  Structure   │
     └──────┬───────┘
            ↓
     ┌──────────────┐
     │   DISTILL    │
     │   Refine     │
     └──────┬───────┘
            ↓
     ┌──────────────┐
     │   EXPRESS    │
     │   Create     │
     └──────┬───────┘
            │
            └────────→ Output feeds back as new capture
```

#### The Linking Architecture

**Why Links Matter:**
- Connections = Understanding
- Links create unexpected pathways
- Bidirectional links show context
- Network effects amplify value

**Types of Links:**

| Link Type | Purpose | Example |
|-----------|---------|---------|
| Reference | Cite source | "From [[Article Title]]" |
| Conceptual | Connect ideas | "Related to [[Concept]]" |
| Hierarchical | Show structure | "Part of [[Project]]" |
| Sequential | Show flow | "Next: [[Following Step]]" |
| Oppositional | Contrast | "Contrast with [[Opposite View]]" |

**Linking Best Practices:**
1. Link at point of relevance
2. Use descriptive link text
3. Create landing pages for key concepts
4. Maintain backlinks (automatic or manual)
5. Review link graph periodically

#### The Retrieval System

**Search vs. Browse vs. Serendipity:**

| Method | When to Use | PKM Pattern |
|--------|-------------|-------------|
| Search | Know what you need | Good titles, tags |
| Browse | Exploring a topic | Hierarchical folders |
| Serendipity | Open discovery | Links, graph view |

**Optimizing for Retrieval:**
- Descriptive, unique note titles
- Consistent tagging taxonomy
- Regular review and maintenance
- Multiple entry points (links, tags, search)

---

## 7. Architectural Patterns Summary

### Design Patterns for PKM Systems

Based on the research, here are the key architectural patterns for leading-edge PKM systems:

#### Pattern 1: The Pipeline Pattern

```
[Capture] → [Process] → [Distill] → [Express]
    ↓           ↓           ↓           ↓
  Inboxes    PARA org   Progressive   Output
            Structure   Summarization Creation
```

*Use when:* Building a comprehensive PKM system from scratch

#### Pattern 2: The Hub-and-Spoke Model

```
         ┌─────────────┐
         │   PROJECT   │ ← The hub (active work)
         └──────┬──────┘
                │
    ┌───────────┼───────────┐
    ↓           ↓           ↓
┌───────┐   ┌───────┐   ┌───────┐
│ Notes │   │ Tasks │   │Files  │ ← The spokes
└───────┘   └───────┘   └───────┘
```

*Use when:* Organizing around project-based work

#### Pattern 3: The Garden Pattern (Evergreen)

```
Seedlings → Saplings → Evergreens
 (new)     (developing) (mature)
    ↓          ↓           ↓
 Fleeting   Literature   Permanent
  notes      notes        notes
```

*Use when:* Building a long-term knowledge base (Zettelkasten-style)

#### Pattern 4: The Layered Architecture

```
┌─────────────────────────────────────┐
│  Layer 4: Output/Expression         │ ← Creation
├─────────────────────────────────────┤
│  Layer 3: Distilled Knowledge       │ ← Summarized notes
├─────────────────────────────────────┤
│  Layer 2: Processed Notes           │ ← Organized & linked
├─────────────────────────────────────┤
│  Layer 1: Raw Captures              │ ← Sources & clips
└─────────────────────────────────────┘
```

*Use when:* Progressive summarization is primary method

#### Pattern 5: The Network Model

```
    [Note A] ←──────→ [Note B]
       ↑    \         /    ↑
       |     \       /     |
    [Note C] ←──────→ [Note D]
       ↑                /    ↑
       |               /     |
    [Note E] ←─────────→ [Note F]
```

*Use when:* Emphasizing connections and emergent insights

### Tool Selection Matrix

| Pattern | Primary Tool Type | Secondary Tools |
|---------|------------------|-----------------|
| Pipeline | All-in-one PKM | Specialized capture apps |
| Hub-and-Spoke | Project management | Note storage |
| Garden | Linked note app | Citation manager |
| Layered | Hierarchical notes | Read-later service |
| Network | Graph-based PKM | Visualization tools |

### Implementation Roadmap

**Phase 1: Foundation (Weeks 1-2)**
- Choose primary tool
- Set up PARA structure
- Establish capture habits

**Phase 2: Integration (Weeks 3-4)**
- Migrate existing notes
- Create initial links
- Establish daily/weekly reviews

**Phase 3: Optimization (Month 2)**
- Add progressive summarization
- Refine organization
- Build output habits

**Phase 4: Evolution (Ongoing)**
- Regular reviews and pruning
- System refinement
- Advanced linking and synthesis

### Key Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Capture friction | < 30 seconds | Time from idea to capture |
| Retrieval success | > 80% | Finding what you need |
| Output frequency | Weekly | Creating from notes |
| Note connections | 3+ per note | Average links per note |
| Review completion | > 90% | Weekly review adherence |

---

## References & Further Reading

### Primary Sources
- Forte, Tiago. *Building a Second Brain* (2022)
- Forte, Tiago. *The PARA Method* (2023)
- Ahrens, Sönke. *How to Take Smart Notes* (2017)
- Allen, David. *Getting Things Done* (2001)

### Influential Thinkers
- **Tiago Forte**: CODE methodology, PARA, Building a Second Brain
- **Sönke Ahrens**: Zettelkasten methodology, Smart Notes
- **Andy Matuschak**: Evergreen notes, networked knowledge
- **David Allen**: GTD, actionability
- **Niklas Luhmann**: Original Zettelkasten system

### Key Concepts
- SECI Model (Nonaka & Takeuchi) - Knowledge creation theory
- Extended Mind thesis - External cognition
- Distributed cognition - Offloading to tools
- Spaced repetition - For retention (Matuschak)

---

## Conclusion

Leading-edge PKM systems share common architectural principles:

1. **Flow-oriented design**: Information moves through capture → process → output
2. **Actionability as organizing principle**: Structure supports doing, not just knowing
3. **Progressive refinement**: Knowledge deepens through multiple passes
4. **Strategic JIT/JIC balance**: Learn when needed, capture for serendipity
5. **Networked connections**: Links create emergent value
6. **Regular review cycles**: Maintenance transforms collection into understanding

The most effective PKM architecture is one that you'll actually use—prioritize low friction, clear organization, and regular output over theoretical perfection.

---

*Document compiled from research on PKM methodologies, February 2026.*
