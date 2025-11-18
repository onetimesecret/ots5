# OneTimeSecret Logo Concepts — Design Index

**Repository**: `claude/secret-sharing-logo-design-01ChfLzmtTevdKsTviPuVaCx`
**Constraint**: Pure SVG vector, <2KB per file, primitives only (circle, rect, line, path)
**Deliverables**: Black-on-white (bw_) and white-on-black (wb_) colorways

---

## Core Visual Metaphors

### 1. The Fading Eye — View-Once Destruction
**ID**: `#A1E9` (v1) • `#A2F0` (v1.1)
**Metaphor**: A viewing eye struck through and dissolving into void
**Evolution**:
- **v1**: Eye with diagonal slash, multiple dissolving particles
- **v1.1**: Refined to minimal—fewer particles, tightened eye shape for favicon clarity

**Files**: `bw_v1.svg` `wb_v1.svg` `bw_v1.1.svg` `wb_v1.1.svg`

---

### 2. The Dissolving Lock — Temporary Security
**ID**: `#B2F8` (v2) • `#B3G1` (v2.1)
**Metaphor**: Security literally melting away after single use
**Evolution**:
- **v2**: Padlock with shackle, 6 drip particles showing dissolution
- **v2.1**: Reduced to 3 deliberate drops, added keyhole detail, shortened body

**Files**: `bw_v2.svg` `wb_v2.svg` `bw_v2.1.svg` `wb_v2.1.svg`

---

### 3. The Vanishing Flame — Burn After Reading
**ID**: `#C3D7` (v3) • `#C4E2` (v3.1)
**Metaphor**: Consuming flame scattering to ash, leaving no trace
**Evolution**:
- **v3**: Flame with rich particle field (10 scatter points)
- **v3.1**: Reduced particle field by 40%, improved symmetry and balance

**Files**: `bw_v3.svg` `wb_v3.svg` `bw_v3.1.svg` `wb_v3.1.svg`

---

### 4. The Expiring Clock — Countdown to Zero
**ID**: `#D5K3`
**Metaphor**: Time running out, arc segments disappearing
**Design**: Clock face with hands at final moment, dashed rings fading in opacity
**Unique trait**: Only concept using stroke-dasharray for temporal decay effect

**Files**: `bw_v4.svg` `wb_v4.svg`

---

### 5. The Dissolving Ripple — Abstract Minimalism
**ID**: `#E6M4`
**Metaphor**: Presence fading to absence through concentric dissolution
**Design**: Solid core with 4 concentric rings at decreasing opacity
**Unique trait**: Most abstract; no literal object—pure visual reduction

**Files**: `bw_v5.svg` `wb_v5.svg`

---

### 6. The Broken Seal — Irreversible Opening
**ID**: `#F7N5`
**Metaphor**: Wax seal shattered, cannot be restored
**Design**: Circle with center chevron (opened state), radiating crack lines
**Unique trait**: Only concept suggesting physical breach rather than fade/decay

**Files**: `bw_v6.svg` `wb_v6.svg`

---

### 7. The Erasing Message — Direct Content Metaphor
**ID**: `#G8P6`
**Metaphor**: Text lines progressively disappearing
**Design**: 7 horizontal bars decreasing in length and opacity (3 at glyph, 5 at lockup, 7 at badge)
**Unique trait**: Most literal representation; uses only rectangles

**Files**: `bw_v7.svg` `wb_v7.svg`

---

## File Size Summary

| Version | Black-on-White | White-on-Black |
|---------|----------------|----------------|
| v1      | 1,707 bytes    | 1,956 bytes    |
| v1.1    | 1,613 bytes    | 1,826 bytes    |
| v2      | 1,970 bytes    | 2,029 bytes    |
| v2.1    | 1,698 bytes    | 1,959 bytes    |
| v3      | 1,862 bytes    | 1,993 bytes    |
| v3.1    | 1,635 bytes    | 1,932 bytes    |
| v4      | 1,997 bytes    | 1,970 bytes    |
| v5      | 1,716 bytes    | 1,881 bytes    |
| v6      | 1,785 bytes    | 1,914 bytes    |
| v7      | 1,636 bytes    | 1,945 bytes    |

**All files**: Under 2KB ✓
**Total variations**: 20 files (10 concepts × 2 colorways)

---

## Conceptual Categories

### Destruction-Based
- Fading Eye (v1, v1.1)
- Vanishing Flame (v3, v3.1)

### Decay/Dissolution
- Dissolving Lock (v2, v2.1)
- Dissolving Ripple (v5)

### Temporal
- Expiring Clock (v4)

### Physical State Change
- Broken Seal (v6)

### Content-Focused
- Erasing Message (v7)

---

## Design Primitives Used

| Primitive | Concepts Using It |
|-----------|-------------------|
| `circle`  | v1, v1.1, v2, v2.1, v3, v3.1, v4, v5, v6 |
| `rect`    | v2, v2.1, v7 |
| `line`    | v1, v1.1 |
| `path`    | v2, v2.1, v3, v3.1, v4, v5, v6 |
| `ellipse` | v1, v1.1 |

**Most minimal**: v7 (rectangles only)
**Most complex**: v4 (uses stroke-dasharray technique)

---

## Iteration Philosophy

Each iteration tested:
1. **Maximum reduction** — Remove elements until meaning is lost
2. **Conceptual clarity** — Can a 16×16 favicon still communicate the metaphor?
3. **Scale consistency** — Does the design work at glyph/lockup/badge sizes?
4. **Visual balance** — Opacity gradients create depth without adding primitives

**Stopping criteria**: Further reduction removes legibility; further addition creates clutter.
