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
| F1 | Modal stack exceeds the budget: header `backdrop-blur-xl` + overlay `backdrop-blur-sm` + panel `.glass-strong` blur(20px) = 3 overlapping | `Layout.tsx:134`, `Overlay.tsx:271`, `Overlay.tsx:278` | 7 — **done** |
| F2 | Landing code window nests `backdrop-blur-xl` directly inside `backdrop-blur-xl`; + the fixed header = 3 | `Landing.tsx:358`, `359`, `106` | 8b — **fixed**, inner blur dropped, swept 3 → 2 |
| F3 | Background/border utilities passed to glass `Card`s are dead — unlayered `.glass-*` beats `@layer utilities`, and `twMerge` keeps both | `Dashboard.tsx:308`, `487`, `513`; `Login.tsx:73`; `Register.tsx:154`; `ResetPassword.tsx:59`; `ForgotPassword.tsx:50`; `Landing.tsx:464` | 5 |
| F4 | `Button` `secondary` has dead `hover:`/`active:` backgrounds for the same reason; in dark mode `--glass-base` is `transparent`, so there is no hover feedback at all | `Button.tsx:54` | 5 |
| F5 | Physical utilities where logical belong (done in 6; the recorded list was 13 sites, the sweep found 29) | `Layout.tsx:85`, `195`, `338`; `Dropdown.tsx:214`; `Feedback.tsx:282`; `AchievementToast.tsx:65`; `XpToast.tsx:47`; `NotificationBell.tsx:80`; `LessonDetail.tsx:350`, `391`; `Landing.tsx:222`, `372`, `530` | 6 |
| F6 | **`.bg-grid-pattern` sets `opacity` on the element, and two sites put it on a content container — the whole canvas subtree renders at 0.05** | `CircuitCanvas.tsx:120`, `VisualProgramming.tsx:611`; class at `index.css:1018-1024` | **4** |
| F7 | `bg-grid-pattern-opacity` is never defined anywhere — 8 dead usages | `CourseDetail.tsx:137`; `Profile.tsx:261`, `294`, `360`; `ProjectDetail.tsx:239`; `VisualProgramming.tsx:425`, `466`; `Landing.tsx:465` | 9 |
| F8 | Reduced motion: the global block overrides `animation-duration` but not `animation-delay`, and `.animate-fade-in` is `both` fill — delayed entrances hold at `opacity: 0` | `index.css` reduced-motion block, `581`, `605`; `Landing.tsx:268`, `415`, `447` | 8 — **done, and see F17** |
| F9 | `--glass-tint-strength` is defined in both themes with a long justification and consumed by nothing | `index.css` | 8 — **done, removed** |
| F10 | Two parallel glass systems: `.glass`/`.glass-strong` are hardcoded blur, not token-driven, and blur in light mode too | `index.css:1236`, `1241`; used at `Overlay.tsx:278`, `Dropdown.tsx:160`, `CodyBubble.tsx:166`, `OnboardingTour.tsx:197` | 7 — **done** |
| F11 | `text-quaternary` on glass is the tightest text in the system and was never measured — every phase measured `text-tertiary` instead | `index.css:42`; `StatusBadge.tsx:220` | 8b — **closed as wrong as written**; the real defect it pointed at became F19 |
| F12 | Dead code: 7 unrouted `Test*.tsx` pages, `.animate-slide-in-right`/`-out-right`, `ar.json`'s `common.or_continue_with` | `pages/Test*.tsx`; `index.css:596-602`; `locales/ar.json` | 9 |
| F13 | Landing's "Create Free Account" CTA is `variant="secondary"` with `bg-gradient-to-r from-accent-700 to-accent-800`. Dead for the F3 reason, so the CTA renders as dark glass, not orange — measured `backgroundImage: linear-gradient(rgba(255,255,255,0.07), …)`. Unlike F3 the intent here is clearly a coloured CTA, so deleting the utility is the wrong fix | `Landing.tsx:482` | 5b — **done** |
| F14 | `Courses` passes conditional paint to an `interactive` Card: `isCompleted && 'border-success-500/30 bg-success-500/5'` and `!isStarted && !isLocked && 'border-border-primary/50'`. Both dead. The completed-course green tint therefore never renders, so a real state signal is silently missing | `Courses.tsx:203`, `205` | 5b — **done** |
| F15 | ~20 directional icons (arrows, chevrons) do not mirror under `dir="rtl"`. Eight sites already flip via an `isRTL` ternary (`ExercisePanel`, `MicroQuestLesson`, `LessonDetail`); the rest point the wrong way in Arabic | `Dashboard.tsx` (6), `Landing.tsx`, `Courses.tsx`, `CourseDetail.tsx`, `QuestClear.tsx`, `LegalLayout.tsx`, `LessonHeader.tsx`, `DuelArena.tsx`, `ForgotPassword.tsx`, `QuestNode.tsx`, `DebugTracePanel.tsx` | 6b — **done** |
| F16 | Two icons carry a direction but not a *navigation* direction: `Send` (paper plane) and `ExternalLink`. Both are metaphors, and mirroring them is a product call rather than a correctness fix, so both were left and allowlisted | `CodyChatPanel.tsx:110`, `ProjectDetail.tsx:413` | **open — your call** |
| F17 | Every `.animate-*` entrance was inert. `animation: fadeIn var(--transition-normal) var(--animate-ease) both` carried two easing functions, because `--transition-normal` is `200ms cubic-bezier(...)` — duration *and* easing — so the shorthand was invalid and the declaration dropped. Measured `animation-name: none` on all 14 Landing elements, in both motion modes | `index.css` `.animate-fade-in` and five siblings | 8 — **fixed** |
| F18 | Five of six `StatusBadge` variants failed contrast in light: the styles were dark-mode ramp recipes (`bg-success-900/30 text-success-400`) reused unchanged. Measured completed 1.58:1 (1.02 in situ), current/available 2.30, in progress 2.38, pending 1.52. Only `locked` passed — the one variant already built from semantic tokens | `StatusBadge.tsx` `statusStyles` | 8 — **fixed** |
| F19 | `--color-text-quaternary` failed in dark on the surfaces it actually renders on: 4.46:1 on `--color-bg-elevated` and 4.07:1 on `--color-bg-tertiary`. Its own comment only ever claimed 5.1:1 against `--color-bg-primary` | `index.css` dark block | 8 — **fixed** |
| F20 | The dark text ramp is inverted after F19: `text-quaternary` #8695AE (luminance 0.2962) is now LIGHTER than `text-tertiary` #7C8CA5 (0.2576). Separately, `text-tertiary` already fails on `--color-bg-tertiary` at 4.41:1 — the pair `StatusBadge` `locked` actually uses (`bg-bg-tertiary text-text-tertiary`) | `index.css` dark block | 8b — **fixed**, option A applied (`#8FA0BA`) |
| F21 | Fixing the inert animations (F17) makes them fire on remount. `CodeEditor.tsx:259/262` mounts its output/error div conditionally, so the fade now replays on every code run, inside an `aria-live="polite"` region. 59 live sites across four classes; the page-level wrappers are once-per-navigation and fine | `CodeEditor.tsx:259`, `262`; `Feedback.tsx:341`, `441`; `ExerciseAnswer.tsx:17`; `Dropdown.tsx:154`; `Overlay.tsx:263/277/285`; `MicroQuestLesson.tsx:170/190/231` | 8b — **judged**: `CodeEditor` fixed, the rest kept |
| F22 | A dropdown over the scrolled app shell composites **3** blurred layers: the menu panel opens at y=57 and the fixed header ends at y=65, so an 8px band stacks `glass-menu` + header blur + a card scrolled under the header. 310 of 324 points sampled in that band were over budget. Phase 7 recorded this state at 2 because its census only sampled scroll 0 | `Dropdown.tsx` position calc; `Layout.tsx` header | 8b — **fixed**, panel now clears its pinned ancestor |
| F23 | `text-tertiary` fails in **light** on two surfaces it really renders on: `--color-bg-tertiary` at 4.29:1 (the `locked` StatusBadge pill and every `disabled:` input — `Input.tsx:78` `disabled:bg-bg-tertiary disabled:text-text-tertiary`), and the code surfaces at 2.82:1 on `--color-bg-code-light` — measured in place at **2.63:1** on Landing's code frame, whose `main.py` label is `text-text-tertiary`. (The earlier 1.87:1 composited `bg-code/80` straight onto `bg-primary`; the real ground is four layers — the title bar's own `bg-bg-code-light/80` over `bg-bg-code/80` over the section's `bg-bg-secondary/50` over `bg-bg-primary` — which renders a flat `rgb(36,46,63)`, darker than the one-layer estimate.) `bg-code` is dark in BOTH themes, so light's dark-on-light tertiary lands on a dark surface. `text-quaternary` also fails light on `--color-bg-secondary` (4.30:1) | `index.css` `:root`; `Landing.tsx:366`; `Input.tsx:78`; `CodeEditor.tsx:265` | **open — 9**, light ramp was out of 8b's brief |
| F24 | The e2e harness hardcoded port 8000 in eleven places — the vite proxy target plus ten in-page `fetch('http://localhost:8000/...')` calls. Any other local service holding 8000 404s the whole suite. The in-page calls are now relative `/api/...` through the proxy, which `lesson-locking.spec.ts:19` already documented as the right pattern, and the proxy target reads `ATLASCODE_API_ORIGIN` | `vite.config.ts`; `e2e/*.spec.ts`; `e2e/helpers.ts` | 8b — **fixed** |

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


### Phase 6 — RTL sweep (F5) — **done**

29 physical->logical swaps across 14 files. F5 recorded 13 sites; a full sweep
found 29, and one of the 13 (`Landing.tsx:372`) turned out to be correct as
written -- it is inside a `dir="ltr"` <pre>, so it was left alone.

Swapped: `ml`/`pl` -> `ms`/`ps`, `text-left` -> `text-start`, `right-N` ->
`end-N`, `border-r` -> `border-e`, `rounded-tl`/`rounded-tr` ->
`rounded-ss`/`rounded-se`. Beyond the F5 list this also caught the lesson
sidebar dividers, the Cody chat bubble tails, the project panel indent and
badge, the Overlay/DuelLobby/VisualProgramming row labels, three Dashboard
`ml-auto` arrows, and four Landing hero decorations.

Verified in a real RTL render rather than by reading. Each utility was
measured for which physical edge it resolves to under `dir="rtl"`:

  ml-6   -> ms-6        margin-left 24px   -> margin-right 24px
  border-r -> border-e  border-right 1px   -> border-left 1px
  rounded-tr -> rounded-se  top-right 6px  -> top-left 6px
  -right-1 -> -end-1    right -4px         -> left -4px
  right-4  -> end-4     right 16px         -> left 16px
  text-left -> text-start  text-align left -> start

A first pass of that measurement was misleading: Tailwind v4 only generates
classes it finds in source, so probing `ms-6`/`border-e`/`rounded-se` before
they existed returned no styles at all. Re-measured after the swap.

EN is unchanged, as it must be -- logical and physical are identical in LTR.
Pixel-diffed against main: lesson, duels, usermenu and cody are byte-identical;
projects 2px; dashboard 531px and landing 3.13%, both of which a self-diff on
*identical* code reproduces (826px and 3.08%), i.e. the hero canvas animation
and run-to-run variance, not the change.

Left physical on purpose, each with a reason in the guard's allowlist: code
inside `dir="ltr"`; `left-1/2` centring and `left-0 right-0` pairs; the
named-direction placement APIs in `Dropdown`/`Feedback`/`Overlay`; the logo
mark's accent dot; `DuelArena`'s `text-right`, which pairs with
`flex-row-reverse` and needs a live duel to verify; the Landing blobs coupled
to a `translate-x` (Tailwind has no logical translate); and the Circuit Lab /
Visual Programming node internals, which sit in a JS-positioned coordinate
space where mirroring the markup would move a port away from the wire that
attaches to it.

Guarded by `components/__tests__/rtlLogicalUtilities.test.ts`: a brace-aware
scanner that reads whole `className` values (including multi-line `cn(...)`
expressions a regex would miss) and fails on any physical utility without an
allowlist reason. Confirmed to fail on a reintroduced `ml-6` before being
trusted, and it found five sites the manual sweep had missed.

### Phase 6b — directional icons (F15) — **done**

23 icons gained `rtl:-scale-x-100`, and three horizontal hover nudges were
paired `ltr:`/`rtl:` so the arrow slides toward the reader in both
directions rather than away in one.

**Mechanism: `rtl:-scale-x-100`,** chosen over the `isRTL` pattern. The repo
had no single convention to follow -- it already mirrors by component swap
(`isRTL ? <ChevronRight/> : <ChevronLeft/>`, 8 sites) *and* by rotation
(`isRTL && 'rotate-180'`, 5 sites). The CSS variant needs no hook threaded
into the ~15 components that lack `useTranslation`, works on icons passed as
`leftIcon`/`rightIcon` props without touching `Button`, and is the same idiom
as the hover-translate fix, so one mechanism covers both. The 13
already-mirrored sites were left as they are; the guard accepts all three.

Verified in the browser before building on it: `rtl:-scale-x-100` resolves to
`scale: -1 1` under `dir="rtl"` and to `scale: none` under `ltr`, so EN is
untouched by construction. Tailwind v4 emits `scale` as its own property, not
inside `transform` -- reading `transform` showed `none` and briefly looked
like the variant did nothing.

Measured across six surfaces: **AR 40 of 40 declared icons flipped, EN 0 of
40.** `ChevronDown` stayed unflipped throughout, which is the check that the
change is not over-reaching.

EN unchanged: courses and projects 0px, coursedetail and lesson 2px of
1,440,000. Landing (0.77%) and dashboard (1163px) both sit at their
self-diff noise floor (0.60% and 190px, same regions), i.e. the hero canvas
and the same right-edge run-variance phase 6 saw.

Out of scope and untouched, as intended: media controls, checkmarks, close,
plus/minus, brand marks, vertical chevrons, and anything inside `dir="ltr"`.
`LogOut` is an exit metaphor rather than a next/back affordance and is
allowlisted. `Send` and `ExternalLink` are F16, left for a decision.

Guarded by `components/__tests__/rtlDirectionalIcons.test.ts`: a brace-aware
scanner (icons sit inside `{...}` props and ternaries, where a `<Icon[^>]*>`
regex reads the wrong text), accepting any of the three mirroring mechanisms,
plus a second assertion that no horizontal hover translate is left
unqualified. Both were confirmed to fail on a reintroduced regression before
being trusted -- and the hover assertion caught a false positive in its own
first regex, where `(?:group-)?` let the match start inside an
already-correct `ltr:group-hover:…`.

### Phase 7 — blur budget (F1, F10) — **done**

Measured first, in a real browser, before changing anything. The budget is a
per-POINT limit, so the census samples a grid and at each point counts how
many elements under it have a computed `backdrop-filter`, via
`elementsFromPoint` (which returns the whole hit stack, ancestors included).

                        before   after
  dashboard                  1       1
  courses                    1       1
  lesson                     1       1
  landing                    1       1
  dashboard + modal          3       2     <- over budget
  dashboard + dropdown       2       2
  dashboard + cody           2       2
  onboarding tour            2       2

**F1 confirmed, with a correction.** Three layers is right -- 504 of 3240
sampled points -- but not the trio F1 named. The two distinct 3-stacks were

  div.backdrop-blur-sm | header.backdrop-blur-xl | div.glass-surface
  div.glass-strong     | div.backdrop-blur-sm    | div.glass-surface

so the third layer is a dashboard card, and the overlay scrim is the common
term in both, not the header-plus-panel pair F1 described. One change fixes
both: the scrim no longer carries `backdrop-blur-sm`. It still dims; the
panel above it is still glass, which is where the frosting reads. That is a
deliberate, visible change in dark (10.1% of the modal view) -- the budget
cannot be met while a full-viewport blurred scrim sits over an already
blurred header.

Only that one state was over budget, so nothing else was touched.

**F10 corrected as well.** Its description -- "not token-driven" -- was only
half right: the backgrounds were already per-theme tokens. The real defect
was narrower, that the BLUR was hardcoded in the rule (`blur(14px)`,
`blur(20px)`) and so fired in light too, against the dark-only decision.
`.glass` and `.glass-strong` are now `.glass-menu` and `.glass-panel`, taking
their blur from `--glass-menu-blur` / `--glass-panel-blur`, `none` in light.
Dark values are unchanged, deliberately: migrating them onto
`.glass-surface`/`.glass-raised` would have repainted every dropdown and
modal.

Dark is pixel-identical across the F10 migration. dashboard and cody 0px,
courses 0px, dropdown 7px of 1,296,000; lesson, landing and the tour each
match their own self-diff noise floor exactly (132 vs 129, 8614 vs 8614,
197 vs 204). The only real dark change is the modal scrim.

Light now composites **1** blurred layer in every state, down from 2 with a
modal or dropdown open -- the F10 defect, gone. Visually that is nearly
nothing (dropdown 0px, cody 0.27%), because blurring a near-uniform light
background looks much like not blurring it; the cost was a real compositing
layer rather than a visible one. AR dark matches EN dark at 2 everywhere.

Kept as `e2e/blur-budget.spec.ts`, which uses only surfaces a brand-new
account can reach -- no locked lessons. Getting it to actually catch the bug
took three corrections, each worth recording: it first passed against the
known-bad code because Playwright's default viewport is 1280x720, where the
dashboard reflows and the overlap never forms; then because it never set a
theme, so it ran in light where glass does not blur at all; and the worst
case needs a scroll, since at scroll 0 the cards sit below the fixed header.
It now pins 1440x900 and dark, scrolls first, and asserts the modal composites
at least two layers before asserting it composites at most two -- so it cannot
pass vacuously. Verified against main: "dashboard + modal: 3 overlapping
blurred layers at (52,4)".

A source guard in `glass.test.tsx` fails if `.glass`/`.glass-strong` returns,
in the stylesheet or in any className, and if either replacement hardcodes a
blur. Confirmed to fail on a reintroduced class. Its first version had a
false positive -- the word "glass" in a comment inside a `cn(...)` call -- so
the shared scanner now reads only string literals, not every word in the
expression.

### Phase 8 — reduced motion and contrast (F8, F9, F11) — **done**

Measured first, in a browser, before editing anything. Three of the four
things this phase set out to fix turned out to be different from the finding
that described them.

**Reduced motion (F8) — the premise was hiding a bigger bug.** F8 predicted a
staggered entrance holding at `opacity: 0`. It does not happen, because the
animations never ran at all: `.animate-fade-in` and its five siblings were
written as `animation: fadeIn var(--transition-normal) var(--animate-ease)
both`, and `--transition-normal` is `200ms cubic-bezier(...)` — duration *and*
easing — so the shorthand carried two easing functions, was invalid, and the
declaration was dropped. All 14 Landing elements computed
`animation-name: none` in both motion modes (F17).

Dropping the redundant `var(--animate-ease)` makes them real, which makes F8
reachable, and `animation-delay: 0s` in the existing reduced-motion block
fixes it. Measured under emulated reduce afterwards: every element reports
`animation-name: fadeIn`, `animation-delay: 0s` (the inline 500ms included)
and `opacity: 1`. Without the preference the designed stagger survives.

**`--glass-tint-strength` (F9) — dead.** Two declarations, zero consumers
anywhere in the frontend. Removed.

**Contrast (F11) — the finding was aimed at the wrong place.** F11 assumed
`text-quaternary` sits on glass. Its only glass call site is `StatusBadge`'s
unearned branch, and both callers pass `earned={true}`, so it never renders
there. Where it does render is code and canvas surfaces — and it failed
there, on the surfaces its own comment never checked (F19):

                       before   after
  bg-elevated           4.46     5.43     <- the FALSE label on a circuit node
  bg-tertiary           4.07     4.96
  bg-primary            5.46     6.64
  #7686A0 -> #8695AE, worst surface 4.96:1

The real contrast failure was somewhere else entirely. `StatusBadge` painted
dark-mode ramp recipes and reused them in light (F18), where five of six
variants failed:

                 light before   light after   dark (unchanged)
  completed         1.58           6.64          11.34
                   (1.02 in situ over the tinted card)
  current           2.30           8.04           7.77
  available         2.30           8.04           7.77
  in progress       2.38           8.63           8.75
  pending           1.52           6.61          11.81
  locked            4.83           4.83           5.79

`locked` passing was the tell: it was the only variant already built from
semantic tokens. So the fix is per-theme `--badge-{hue}-bg/-fg` tokens, not a
one-off class. Dark keeps its exact previous values and measures identically.

Everything else re-measured after the token change, so one failure was not
traded for another: `text-tertiary` on the completed tint is unchanged at
5.14 dark / 4.92 light, and light `text-quaternary` is untouched at 4.83 on
white and 4.58 on the page ground.

Guards: `e2e/reduced-motion.spec.ts` (pins viewport and theme, asserts the
animations exist, that something is still staggered, and that the emulation
is actually on — that last precondition caught a nested
`test.use({ reducedMotion })` doing nothing) and
`src/components/__tests__/contrastTokens.test.ts`, which computes real WCAG
ratios in vitest from the declared values. Every pair it asserts is opaque on
both sides, so no renderer is needed; dark's translucent pills are measured
in a browser instead and recorded above. Both guards were confirmed to fail
on their bug before being trusted.

**F2 is still open, and phase 7 under-measured it.** Phase 7's census reported
Landing at 1 because it only sampled at scroll 0. Scanning the header strip
across the whole scroll range finds **3 overlapping blurred layers** at
scrollY 1560 — `header.backdrop-blur-xl | div.backdrop-blur-xl |
div.backdrop-blur-xl`, the nested code window passing under the fixed header.
Left unfixed here: it is a Landing bug under decision 3 and was not in this
phase's brief. One line (drop the inner blur at `Landing.tsx:359`) should
close it. **Closed in 8b**, and the re-run there found a second over-budget
state this scan missed — see F22.

### Phase 8b — the ramp and the nested blur (F2, F20, F21) — **done**

Measured first, in a browser, before editing anything. Two of the three items
came back different from the finding that described them, and the census that
was re-run to check one of them found a second bug.

**The census under-measured because it sampled one scroll position.** Phase 7
counted overlapping blurred layers at scroll 0 only. Re-run as a *sweep* —
scrollY 0 to the page bottom in steps of viewport/4, sampling the header strip
and a grid at each step, worst taken across the whole sweep — two states phase
7 recorded as within budget are not:

                       phase 7   swept before   swept after
  landing                  1          3              2        <- F2
  dashboard                1          1              1
  courses                  1          1              1
  course detail            -          1              1
  lesson                   1          2              2
  dashboard + modal        2          2              2
  dashboard + dropdown     2          3              2        <- F22
  dashboard + cody         2          2              2
  onboarding tour          2          2              2

**F2, the Landing nested blur — fixed.** Confirmed at 3 overlapping layers,
scrollY 1350, point (52,52): `header.backdrop-blur-xl | div.backdrop-blur-xl |
div.backdrop-blur-xl` — the nested code window passing under the fixed header.
The inner `backdrop-blur-xl` at `Landing.tsx:359` is gone; the outer frame at
`358` keeps its blur and is the one that reads. Swept after: 2.

**F22, the dropdown over a scrolled shell — fixed, and it was not in the
brief.** The sweep found `glass-menu | header.backdrop-blur-xl |
glass-surface` at scrollY 450. The cause is 8px of geometry: the menu panel
opens at y=57 and the fixed header ends at y=65, so wherever a card has
scrolled under the header, three blurs stack in that band — 310 of 324 points
sampled inside it were over budget. Fixed in the `Dropdown.tsx` position calc
rather than at the three header call sites: a bottom-placed panel now clears
the bottom edge of its nearest fixed/sticky ancestor, which fixes
notifications, the user menu and the language switcher at once and stays
correct if the header height changes. Overlap after: 0px, 0 points over.

`e2e/blur-budget.spec.ts` gained the sweep for Landing, Courses, Dashboard and
lesson 1, and was confirmed to FAIL on main at the Landing pair before the fix
("landing, swept: 3 overlapping blurred layers at scrollY 1350"). One
compromise worth recording: the brief asked every swept surface to assert
`scrollHeight > 1.5 x innerHeight` so the sweep cannot pass vacuously, and at
1440x900 on a brand-new account only Landing is reliably that tall (4.65).
Dashboard measured 1.60 and 1.20 on two runs — content height moves with what
has rendered — and courses 1.03, lesson 1 1.08. Pinning 1.5 on those three
would assert a false fact about the app, so Landing carries the real ratio and
the others assert that the sweep left scroll 0 and that the sampler found real
glass. The reasoning is in the spec's own comments.

**F20, the inverted dark ramp — option A applied.** `--color-text-tertiary`
#7C8CA5 -> #8FA0BA. Every surface it renders on was enumerated first, in the
browser, then measured: opaque pairs by token maths (exact), translucent ones
from rendered pixels with the text itself made transparent for the capture, so
the number is the real composite over the live ambient field rather than a
prediction.

                                    before   after
  OPAQUE (token maths)
    bg-primary                       5.90     7.58
    bg-secondary                     4.98     6.40
    bg-tertiary                      4.41     5.66   <- FAIL before
    bg-elevated                      4.82     6.20
    bg-code                          5.91     7.59
    bg-code-light                    5.55     7.13
  COMPOSITED (rendered pixels)
    glass-surface / -flat / -raised  5.57     7.16
    completed tint                   5.19     6.67
    bg-secondary/50                  5.57     7.16
    bg-secondary/80 + blur-xl        5.33     6.85
    bg-secondary/30 + blur-sm        5.76     7.40
    bg-code/80                       5.95     7.65
  IN SITU (worst observed)
    locked badge / disabled input    4.41     5.66
    page ground under the field      4.84     6.22
    footer                           4.98     6.40
  worst case overall                 4.41     5.66

`bg-quaternary` is deliberately absent: it is only Button's `active:` fill,
under `text-primary`/`text-secondary`, so tertiary never lands on it. Included,
it would read 4.33 after and pin a pair that does not exist.

Ordering, checked in both themes. Raw luminance is the wrong test — in dark a
quieter token is darker, in light it is lighter — so the guard compares
contrast against the theme's own page ground, which says the same thing once
and means the same thing in both:

              secondary   tertiary   quaternary
  dark before    9.58       5.90        6.64     <- inverted
  dark after     9.58       7.58        6.64     ok
  light          7.30       4.92        4.58     ok (unchanged)

The secondary-tertiary luminance gap narrows from 0.1916 to 0.1039, still
roughly twice the tertiary-quaternary step (0.0491), and the hierarchy reads
in all twelve review screenshots (Dashboard, Courses, lesson 1 x dark/light x
EN/AR). Light is untouched by this change and measures identically.

**F23, which this uncovered: light fails where dark now passes.** Measuring
light alongside dark found `text-tertiary` under the floor on surfaces it
really renders on — `bg-tertiary` at 4.29 (the same `locked` pill and every
`disabled:` input), and the code surfaces, where it is worst: `bg-code` is
dark in BOTH themes, so light's dark tertiary lands on a dark ground and
Landing's `main.py` label measures **1.87:1** composited. `text-quaternary`
also fails light on `bg-secondary` at 4.30. Left for phase 9: the light ramp
was outside this brief, and Landing is a decision-3 surface.

`contrastTokens.test.ts` grew three groups: ramp ordering in both themes, all
five dark surfaces for tertiary as well as quaternary, and the locked badge
pair by name. Confirmed to fail on the old `#7C8CA5` in exactly the three ways
it should — inverted ordering, `bg-tertiary` 4.41, locked badge 4.41 — before
being trusted.

**F21, remount-fired entrances — judged, one fix.** `CodeEditor.tsx:259/262`
was the one that mattered and is fixed: sampled per animation frame across a
real Python run, the output div mounted at **opacity 0.000** and did not reach
1.0 until 474ms after the output arrived, inside an `aria-live="polite"`
region. The two `animate-fade-in` classes are gone; re-measured, both divs
report `animation-name: none` and opacity **1.000 on their first frame**,
which is also what they did before phase 8 repaired the animations.

`MicroQuestLesson.tsx:170/190/231` does **not** stack three animations, which
is how the finding reads. The three are mutually exclusive stage branches
(`stage === hook | blueprint | quest`), so exactly one is ever mounted.
Sampled across a real hook -> blueprint change: one element, `fadeIn 0.2s`,
fully visible at **237ms** — under the 300ms bar, so it was left alone. The
intended entrances (toasts, dropdowns, modals, page wrappers) were not
touched.

**A harness fix that had to come first (F24).** The suite hardcoded port 8000
in eleven places. The in-page `fetch` calls are now relative `/api/...` through
the dev proxy — the pattern `lesson-locking.spec.ts:19` already documented and
explained — and the proxy target reads `ATLASCODE_API_ORIGIN`, defaulting to
8000. No behaviour change when 8000 is free.


### Phase 9 — trilingual audit and cleanup (F7, F12, F23)

Carries F23 from 8b: the LIGHT ramp. `text-tertiary` is 4.29 on
`--color-bg-tertiary` (the `locked` pill, every `disabled:` input) and
**2.63** in place on Landing's code frame, because `--color-bg-code` is dark
in both themes and light's dark tertiary lands on it; `text-quaternary` is
4.30 on `--color-bg-secondary`. The code-surface case may want a theme-neutral
"on code" token rather than another ramp nudge, since the surface itself does
not change between themes. Numbers and sites are in the 8b section.

Locales are already at parity, so the rest is small: drop `ar.json`'s dead
`common.or_continue_with`, review the 42 FR values identical to EN (mostly true
cognates — `Description`, `Modules`, `Mission` — and interpolation-only strings),
AR render pass on the recent pages. Fold in the dead-code deletions: the 8
`bg-grid-pattern-opacity` usages, the 7 unrouted `Test*.tsx` pages, the two
unused `animate-slide-*-right` classes.

**Two Dropdowns, and an `export *` that picks the wrong halves.** Found while
restricting the panel clearance (`1d4ad99`); cleanup, so it lands here.

`Overlay.tsx:12` exports a second component also called `Dropdown` — an older
one, `content`-prop API, physical `left-0`/`right-0` placement, no clearance
and no RTL handling. Nothing imports it. The one every call site gets is
`ui/Dropdown.tsx`, because `ui/index.ts` lists `export { Dropdown } from
'./Dropdown'` explicitly and an explicit named export wins over the
`export * from './Overlay'` below it.

`DropdownItem` and `DropdownSeparator` are the halves that go wrong.
`ui/index.ts` does *not* re-export them from `./Dropdown`, so `export * from
'./Overlay'` is the only thing that provides those names — and `Layout.tsx:14`
and `NotificationBell.tsx:6` both import them from `./ui`. Checked by identity
rather than by reading: `index.Dropdown === Dropdown.tsx`'s is true, while
`index.DropdownItem` and `index.DropdownSeparator` are both Overlay's. So the
call sites get **Overlay's** items paired with `Dropdown.tsx`'s root, so every
`child.type === DropdownItem` test inside `DropdownRoot` compares against a
different component identity and is permanently false. Harmless today only
because both call sites nest their items inside a wrapper `<div>` rather than
passing them as direct children — the trigger is still found by the
"first non-item child" rule, by luck rather than design.

Fix is a deletion plus one line: drop `Overlay.tsx`'s `Dropdown`,
`DropdownItem` and `DropdownSeparator`, and re-export all three names from
`./Dropdown` in `ui/index.ts`. Do it with the `Dropdown.tsx` item-identity
checks under test, since they have never actually run against the items they
are written for.

### Later — Landing convergence

Per decision 3. A design call, not cleanup: does marketing converge onto Spatial
Glass or stay deliberately distinct?

## Ordering

4 first: self-contained, already scoped by `3be0ba7`, and it carries the one
confirmed user-visible bug. 5 before 7 because both touch background paint and
interleaving them makes the diffs unreadable. 6 is independent and can land any
time. 9 last — it is almost entirely deletion.
