# Spatial Glass — plan and decisions

The working rules live in `frontend/src/index.css`; `CLAUDE.md` points at it.
This file is the thing that was missing: the phase plan, the decisions behind
it, and the audit findings the remaining phases exist to close.

Written 2026-11-12, from an audit of the repo at `ade75ed`.

## Why this file exists

Phases 2 and 3 are labelled in commit messages (`3be0ba7`, `7825063`). Nothing
else is. There is no commit labelled phase 1, there was no plan document, and
what phases 4–6 were meant to cover was recorded nowhere — it had to be
re-derived by reading `index.css` and the diffs. That is the gap this file
closes. **Decision 5: the plan lives in the repo.** Future phases update this
file in the same commit that does the work.

## History as the git log actually records it

| Commit | Label in the message | Scope |
|---|---|---|
| `35efb07` | *none* | `.glass-strong` on Modal, called a "scoped prototype" |
| `35440df` | *none* | `.glass` on Dropdown, skeletons, focus rings, shadow tokens |
| `3be0ba7` | **phase 2** | Token layer + Card + Button; ground `#0B1120` → `#05070D` |
| `7825063` | **phase 3** | Ambient fields behind the logged-in shell |
| `73c7d2a` | *visibility pass* | `--field-strength` 0.14 → 0.20; 17 CTA migrations; 3 Dashboard panels to real blur |
| `3d5ad52` | *leaderboard* | New page, built to the rules |

The two unlabelled September commits are the de-facto phase 1 — they introduced
`.glass`/`.glass-strong` — but the repo never called them that, and `73c7d2a`
is a fourth Spatial Glass commit that carries no number at all. Phases below
are numbered 4+ to continue the labelled sequence, not because 1–3 map cleanly
onto three commits.

## Decisions

### 1. The budget is overlap, not count

`index.css:1131-1135` is authoritative:

> Budget: at most TWO blurred layers overlapping at any point on screen.

At most **two overlapping blurred layers per point**. A page may carry more than
two `.glass-surface` elements as long as no point on screen composites more than
two `backdrop-filter`s. Dashboard's three blurred panels (`Dashboard.tsx:252`,
`387`, `439`) are therefore compliant: they stack vertically and never overlap
each other.

`.glass-flat` stays the default for anything list-rendered. That part is not a
budget question — it is a flat prohibition, and `Card`'s `default`,
`interactive` and `elevated` variants all resolve to a non-blurred form.

### 2. LessonDetail, DuelArena and LessonHeader stay dense tool chrome

These three are **not** converting to glass surfaces. They are dense working
chrome where translucency costs legibility and buys nothing.

They are still in scope for the *systemic* phases: the RTL sweep (phase 6) and
the blur-budget work (phase 7) both touch them, because their raw
`backdrop-blur-*` utilities count against the budget and their physical
utilities break under `dir="rtl"` regardless of what surface treatment they use.
Not converting is not the same as not maintaining.

### 3. Landing: standalone bugs now, convergence later

Landing runs its own `hero-glow`/`hero-grid` system and is deliberately outside
the logged-in shell the ambient fields sit behind. Its *bugs* — the nested
`backdrop-blur-xl` at `Landing.tsx:358/359`, the `text-left` instances, the
reduced-motion stagger — get fixed in the early systemic phases. Whether Landing
*converges* onto Spatial Glass is a separate, later question and a design call,
not a cleanup.

### 4. Phase 5 deletes the dead utilities and fixes Button properly

Where a caller passes a background or border utility to a glass `Card`, the
utility is dead (see finding F3). Phase 5 **deletes** those utilities rather
than making them win — the glass surface is the intended paint, and the dead
classes are misleading to every future reader.

`Button`'s `secondary` variant (`Button.tsx:54`) is the exception: its
`hover:`/`active:` backgrounds are dead for the same reason (F4) but they are
*wanted* behaviour, not decoration. That one gets a real fix — the hover and
active states move into the glass class layer so they actually paint — not a
deletion.

### 5. The plan lives in the repo

This file. Updated by the phase that changes it.

## Findings

From the audit. `F6` is confirmed in-browser; the rest are from reading.

| # | Finding | Evidence | Phase |
|---|---|---|---|
| F1 | Modal stack exceeds the budget: header `backdrop-blur-xl` + overlay `backdrop-blur-sm` + panel `.glass-strong` blur(20px) = 3 overlapping | `Layout.tsx:134`, `Overlay.tsx:271`, `Overlay.tsx:278` | 7 |
| F2 | Landing code window nests `backdrop-blur-xl` directly inside `backdrop-blur-xl`; + the fixed header = 3 | `Landing.tsx:358`, `359`, `106` | 7 |
| F3 | Background/border utilities passed to glass `Card`s are dead — unlayered `.glass-*` beats `@layer utilities`, and `twMerge` keeps both | `Dashboard.tsx:308`, `487`, `513`; `Login.tsx:73`; `Register.tsx:154`; `ResetPassword.tsx:59`; `ForgotPassword.tsx:50`; `Landing.tsx:464` | 5 |
| F4 | `Button` `secondary` has dead `hover:`/`active:` backgrounds for the same reason; in dark mode `--glass-base` is `transparent`, so there is no hover feedback at all | `Button.tsx:54` | 5 |
| F5 | Physical utilities where logical belong | `Layout.tsx:85`, `195`, `338`; `Dropdown.tsx:214`; `Feedback.tsx:282`; `AchievementToast.tsx:65`; `XpToast.tsx:47`; `NotificationBell.tsx:80`; `LessonDetail.tsx:350`, `391`; `Landing.tsx:222`, `372`, `530` | 6 |
| F6 | **`.bg-grid-pattern` sets `opacity` on the element, and two sites put it on a content container — the whole canvas subtree renders at 0.05** | `CircuitCanvas.tsx:120`, `VisualProgramming.tsx:611`; class at `index.css:1018-1024` | **4** |
| F7 | `bg-grid-pattern-opacity` is never defined anywhere — 8 dead usages | `CourseDetail.tsx:137`; `Profile.tsx:261`, `294`, `360`; `ProjectDetail.tsx:239`; `VisualProgramming.tsx:425`, `466`; `Landing.tsx:465` | 9 |
| F8 | Reduced motion: the global block overrides `animation-duration` but not `animation-delay`, and `.animate-fade-in` is `both` fill — delayed entrances hold at `opacity: 0` | `index.css:1408-1415`, `581`, `605`; `Landing.tsx:268`, `415`, `447` | 8 |
| F9 | `--glass-tint-strength` is defined in both themes with a long justification and consumed by nothing | `index.css:273`, `423` | 8 |
| F10 | Two parallel glass systems: `.glass`/`.glass-strong` are hardcoded blur, not token-driven, and blur in light mode too | `index.css:1236`, `1241`; used at `Overlay.tsx:278`, `Dropdown.tsx:160`, `CodyBubble.tsx:166`, `OnboardingTour.tsx:197` | 7 |
| F11 | `text-quaternary` on glass is the tightest text in the system and was never measured — every phase measured `text-tertiary` instead | `index.css:42`; `StatusBadge.tsx:220` | 8 |
| F12 | Dead code: 7 unrouted `Test*.tsx` pages, `.animate-slide-in-right`/`-out-right`, `ar.json`'s `common.or_continue_with` | `pages/Test*.tsx`; `index.css:596-602`; `locales/ar.json` | 9 |
| F13 | Landing's "Create Free Account" CTA is `variant="secondary"` with `bg-gradient-to-r from-accent-700 to-accent-800`. Dead for the F3 reason, so the CTA renders as dark glass, not orange — measured `backgroundImage: linear-gradient(rgba(255,255,255,0.07), …)`. Unlike F3 the intent here is clearly a coloured CTA, so deleting the utility is the wrong fix | `Landing.tsx:482` | 5b — **done** |
| F14 | `Courses` passes conditional paint to an `interactive` Card: `isCompleted && 'border-success-500/30 bg-success-500/5'` and `!isStarted && !isLocked && 'border-border-primary/50'`. Both dead. The completed-course green tint therefore never renders, so a real state signal is silently missing | `Courses.tsx:203`, `205` | 5b — **done** |

Not findings, recorded so they are not re-investigated: reduced motion is
otherwise handled correctly (`App.tsx:158` `<MotionConfig reducedMotion="user">`
covers all 7 framer-motion sites; `HeroGraph.tsx:170-269` has its own
`matchMedia` gate); locales are at full parity (EN/FR/AR all 832 keys, 0
missing); RTL has real e2e cover (`i18n.spec.ts`, `i18n-stability.spec.ts`).

## Phases

### Phase 4 — Circuit Lab guard and the grid-opacity bug *(this branch)*

Split `.no-glass`. The class bundles three concerns behind one `!important`
block, and only one of them — `backdrop-filter: none` — is the anti-translucency
invariant. The other two (forced opaque `background-color`, `background-image:
none`) are what made it unusable on the Circuit Lab canvas, whose grid lives in
`background-image` and whose `bg-bg-code/50` alpha is deliberate. `3be0ba7` left
that hole open on purpose and said "the Circuit Lab phase should" close it.

- add `.no-blur` — `backdrop-filter: none !important` only
- keep `.no-glass` as the composed opaque version for code surfaces
- apply `.no-blur` to `CircuitCanvas`'s root
- fix F6: move `.bg-grid-pattern` onto a childless `aria-hidden` overlay in both
  `CircuitCanvas.tsx` and `VisualProgramming.tsx`

Verify: `tsc -b`, `npm test`, `vite build`; browser before/after on both
canvases in EN and AR RTL; `e2e/visual-programming.spec.ts`.
Risk: low. `.no-glass` has two call sites, both in `CodeEditor.tsx`.

### Phase 5 — close the unlayered-override holes (F3, F4) — **done**

Deleted the dead background/border utilities at the 8 sites; fixed `Button`'s
`secondary` hover/active with `.glass-interactive` (decision 4).

Every site was measured in Chromium before deleting — computed style with the
utility present and removed, **in both themes**, with a forced style flush, a
320ms settle past Card's `transition-all`, and a per-element control
(removing the glass class itself, which must change the paint). All 8 were
dead in dark *and* light, so nothing was kept on light's account.

Two things were deliberately **not** deleted:

- `backdrop-blur-xl` on the four auth cards. It measured **live** in both
  themes — `.glass-raised-flat` sets no `backdrop-filter` (only
  `.glass-raised` does), so that utility is the only thing blurring them.
- F13 and F14 (below), found by the phase-5 sweep. Both are dead by the same
  mechanism, but in both the caller's intent is a *visible* colour, so
  deleting the utility would make the loss permanent instead of fixing it.

`.glass-interactive` beats `.glass-flat`'s resting background on specificity
alone — no `!important`, and no change to how `index.css` is layered.
`.glass-interactive:hover:not(:disabled)` is **(0,3,0)**: one class, plus
`:hover`, plus `:not(:disabled)`, which takes the specificity of its
argument. `.glass-flat` is (0,1,0). Both are unlayered, so specificity
decides.

Dark's hover/press fills are translucent white rather than the opaque
`--color-bg-quaternary` / `--color-bg-tertiary` the Button variant originally
named: an opaque fill would stop the surface reading as glass under the
pointer. A deliberate deviation from the variant's declared intent, recorded
here rather than buried.

**Press always reads at least as strong as hover.** Light's fills first
shipped inverted, because they were taken straight from the variant's own
`hover:bg-bg-quaternary active:bg-bg-tertiary` — and on the light ramp
tertiary (`#E4EAF3`) is *lighter* than quaternary (`#D6E0EC`), so pressing
made the surface lighter than hovering and the press read as a release.
Light is now `#FFFFFF -> #E4EAF3 -> #D6E0EC`, matching dark (0.10 -> 0.14
white) and the `outline`/`ghost` variants, which always had this order. A
test pins the ordering in both themes, and was confirmed to fail on the
inverted values rather than merely pass on the correct ones.

Verified: deleting the utilities is visually inert — login and register are
pixel-identical before/after in both themes (0 differing pixels); dashboard
differs by 2 and 27 pixels out of 1,440,000. Landing dark differs by 0.595%,
but a self-diff of two runs on *identical* code differs by 0.440% with the
same max delta, so that is the drifting hero glows, not the change.

### Phase 5b — state paint for F13 and F14 — **done**

**F13.** Landing's "Create Free Account" CTA is now the design system's
primary gradient button, and the dead accent utility is gone. It was
`variant="secondary"` painting its own orange: secondary resolves to
`.glass-flat`, which sets background-color unlayered, so the gradient never
rendered. Measured before and after, both themes:

                before (dark)              before (light)        after (both)
  background    rgba(0, 0, 0, 0)           rgb(255, 255, 255)    rgb(37, 99, 235)
  image         glass fill 0.07 -> 0.02    none                  gradient 600 -> 800
  label         #F8FAFC                    #101828               #FFFFFF

So in dark it read as a dark glass button and in light as a plain white one
with dark text -- in neither case a call to action. Label contrast after is
5.50:1 at the gradient's lightest point, 8.17:1 at its darkest. Contrast was
never the defect; identity was.

**F14.** The completed course is now `data-state="completed"` plus
`.glass-flat[data-state="completed"]` in index.css, painting from two new
tokens declared in both themes. (0,2,0) against `.glass-flat`'s (0,1,0),
both unlayered -- no `!important`, no `@layer`, no global change, and no
`backdrop-filter`, so a completed card stays a non-blurred list card.

Seen, not inferred: a completed course was seeded in the local dev DB and
measured in Chromium in dark and light, en and ar, each against a control
that strips the attribute and must revert to the plain card. It does.

The dark tint is 6%, not the 10% first written. At 10% the card body's
`--color-text-tertiary` measured **4.68:1** -- 0.18 above the floor and the
tightest value in the system. 6% puts it at **4.99:1** at rest and **5.00:1**
with every ambient field pinned at its 50% keyframe, which is better than the
4.83:1 the Dashboard already carries. success-500 is far lighter than the
near-black ground, so a green tint *lifts* the composite and eats headroom --
the opposite of the intuition. Light is 7% mixed into the opaque surface
(a translucent tint there would make the card see-through); its tertiary
reads 4.92:1 against 5.19:1 on a plain card.

Seeding note: the first seed picked a course whose prerequisite was unmet, so
the card rendered "Locked" *and* completed at once. Re-seeded on a course with
no prerequisite before measuring.

### Phase 6 — RTL sweep (F5)

The 13 physical→logical swaps. Leave `dir="ltr"` code containers alone; leave
symmetric `left-0 right-0` pairs and `left-1/2` centring alone.

Verify: AR RTL pass over Dashboard, Profile settings, Leaderboard, the
LessonDetail navigator, toasts, notification badge. Add a grep-based test so
they do not come back — nothing currently catches them.
Risk: low.

### Phase 7 — blur budget (F1, F2, F10)

Migrate `.glass`/`.glass-strong` onto the token system and delete them, which
closes the modal stack and the light-mode blur leak together. Unnest
`Landing.tsx:358/359`. Add the test that does not exist: assert the count of
overlapping `backdrop-filter`s per page.

Verify: per-page blur census at several scroll positions, both themes.
Risk: medium — `Overlay` and `Dropdown` are app-wide.

### Phase 8 — reduced motion and contrast (F8, F9, F11)

Neutralise `animation-delay` under `prefers-reduced-motion`; either consume
`--glass-tint-strength` or delete it with its comment; measure `text-quaternary`
composited on glass and adjust the token if it fails.

Verify: browser with reduced motion forced, on Landing — content present
immediately, not staggered. Composited-pixel contrast the way `73c7d2a` did it.
Add the first reduced-motion e2e assertion.
Risk: low.

### Phase 9 — trilingual audit and cleanup (F7, F12)

Locales are already at parity, so this is small: drop `ar.json`'s dead
`common.or_continue_with`, review the 42 FR values identical to EN (mostly true
cognates — `Description`, `Modules`, `Mission` — and interpolation-only strings),
AR render pass on the recent pages. Fold in the dead-code deletions: the 8
`bg-grid-pattern-opacity` usages, the 7 unrouted `Test*.tsx` pages, the two
unused `animate-slide-*-right` classes.

### Later — Landing convergence

Per decision 3. A design call, not cleanup: does marketing converge onto Spatial
Glass or stay deliberately distinct?

## Ordering

4 first: self-contained, already scoped by `3be0ba7`, and it carries the one
confirmed user-visible bug. 5 before 7 because both touch background paint and
interleaving them makes the diffs unreadable. 6 is independent and can land any
time. 9 last — it is almost entirely deletion.
