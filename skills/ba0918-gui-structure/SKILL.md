---
name: ba0918-gui-structure
description: "GUI screen structure — how a screen is split into components, who owns each piece of state, which way data and events flow, where dialogs and focus are decided, what gets redrawn, and how those rules are enforced and tested. Use when designing, implementing, changing or reviewing GUI code: adding or changing a screen, region, dialog or keyboard shortcut, deciding or moving where state lives, or fixing a whole-window redraw or sluggish input. 日本語キーワード: GUI 画面 画面構成 部品 コンポーネント 状態管理 状態の持ち主 イベント ダイアログ フォーカス キーボード操作 描き直し 再描画 表示用データ デスクトップアプリ"
metadata:
  ba0918-routing: required:gui
---

# GUI Screen Structure

## Scope

Applies to code that builds the screens of an application with a graphical user interface —
desktop, web or mobile: how a screen is divided into components, where each piece of state is
held, how data reaches a component and how a user's action leaves it, how dialogs and focus are
decided, what is redrawn when something changes, and how these rules are enforced and tested.

These rules are independent of any GUI framework. How they are realised in a particular framework
— which construct is the top-level component, how events are declared, how redraws are requested —
and the application's own specifics, such as its list of regions and the priority order of its
dialogs, belong in the project's own documentation, not here.

It does not cover visual design (colour, layout dimensions, animation) or accessibility. The
general design principles these rules apply — one-way layering, a pure domain layer, dependency
injection, immutability, type-level verification — are the skill `ba0918-design`; this skill
states only how they take shape in a GUI. How tests are written in general is the skill
`ba0918-testing`, and the test-first procedure is the skill `ba0918-tdd`.

Terms used below:

- **Top-level component** — the single component at the root of a window; every other component
  sits beneath it.
- **Region** — one area of the screen with its own component: a list, a detail pane, a status
  bar, a search box.
- **Application state** — the state the domain layer owns: everything that is saved, and
  everything that more than one region depends on.
- **View data** — the read-only value the top-level component hands a component, holding exactly
  what that component needs to draw.

## Rules

### Composition

- Build a screen from one top-level component and one component per region beneath it.
- Give every component its own drawing. The top-level component does not draw another
  component's contents.

### State ownership

- Give every piece of state exactly one owner.
- Let the application state, owned by the domain layer, be the only owner of saved state and of
  state shared by more than one region. Within the UI, only the top-level component holds it.
- Keep state that is not saved and is used inside one region only — a scroll position, the
  selected row, the text in a search box — in that region's component.

### Data flows down

- Hand each component read-only view data holding only what it needs to draw.
- Draw the view data as received. Do not derive a decision from the application state inside a
  component.

### Events flow up

- Report a user's action to the top-level component as an event. Do not change another component
  or the application state directly.
- Mediate between components only in the top-level component.
- For keyboard input, use the framework's child-to-parent propagation where it exists. Do not
  build a second dispatch mechanism on top of it.

### Dialogs

- Allow at most one open dialog at a time, and hold which one is open as a single piece of state
  in the top-level component.
- Show dialogs the user opens and dialogs the application state demands (an error, a
  confirmation) in the same layer.
- Write the priority between competing dialogs in one place.

### Redraw

- Redraw by component: only a component whose view data changed, or that asked to be redrawn
  itself, is redrawn.
- Do not hand a component view data equal to what it already has.

### Drawing is read-only

- Do not change any state while drawing, including global settings such as a theme, a font or a
  style.

### Focus

- Decide focus moves between regions in the top-level component.
- Move focus only within itself from inside a component.

### Enforcement

- Enforce every rule a machine can check with types, visibility or a quality gate: restrict the
  modules that can reach the application state to the top-level component's, make each
  component's state private, and do not add behaviour to the top-level component's type from
  outside its module.
- Check every rule a machine cannot check in review, rule by rule.

### Tests

- Test each component by constructing it from view data, asserting what it draws and the events
  its interactions emit.
- Keep integration tests that go through the top-level component as well.

## Judgment

**Composition: a screen that draws itself in one place changes in one place for every reason.**
Each region has its own reasons to change. When they share one drawing function, a change to the
list touches the code of the detail pane and the status bar, and none of them can be tested
alone.

**State ownership: two owners of one fact drift apart.** When the selected item lives both in the
top-level component and in the list, one copy is updated and the other is not, and the screen
shows two truths. The split by "saved or shared" versus "local to one region" keeps the top-level
component from collecting every scroll position and cursor in the window: local state is where it
is used, and only what really crosses regions rises to the top.

**Data down: a component that sees only its view data can only draw it.** Given the whole
application state, a component starts deciding — whether an item may be edited, which label a
status gets — and the same decision is soon made differently in two places. Computing such
decisions before the view data is built keeps them in the domain layer, where the skill
`ba0918-design` puts them and where they are tested as pure functions. Formatting for display (a
date format, digit grouping) may stay in the component; a decision may not.

**Events up: the top-level component is the only place that knows every component.** When
components change each other directly, every pair of components is a dependency, and a change to
one breaks others in ways no single test sees. Routing every action through the top-level
component makes the interactions one list that can be read and tested. Keyboard input is the
exception to building this by hand: a framework that propagates key events from child to parent
already is that route, and a second dispatch table beside it lets the same key be handled twice or
not at all.

**Dialogs: one state makes two dialogs at once impossible to represent.** A separate "is open"
flag per dialog allows an error and a confirmation to open together, and no one decided which
wins. With one state naming the open dialog, and one place stating which demand overrides which,
the conflict is resolved once. A confirmation inside a dialog — discard changes in a settings
dialog — is one more value of that state, not a second dialog stacked on the first.

**Redraw: the whole window redrawn on every change is where sluggish input comes from.** When the
top-level component rebuilds and re-hands every component's view data after any change, every
component redraws on every keystroke. Handing a component its view data only when that data
changed confines the cost to the region that changed. Where the framework redraws the whole
screen on every frame and the application cannot choose the unit, the project's documentation
states how this rule applies there — for example, not rebuilding view data that has not changed.

**Drawing is read-only: drawing runs when the framework decides.** A state change inside drawing
happens as often as the framework redraws, in an order the application does not control, and
a global setting changed there leaks into everything drawn afterwards. Drawing that only reads
can be repeated any number of times with the same result. This is the pure-boundary principle of
the skill `ba0918-design`, applied to drawing.

**Focus: moving between regions is a decision about the whole screen.** Which region comes next
depends on which regions are showing and what the user is doing, which only the top-level
component knows. A component that moves focus into another region depends on that region
existing.

**Enforcement: a rule the compiler checks cannot be broken by accident.** A comment saying "do not
touch the application state from a component" does not stop the next change; visibility that
makes the state unreachable from a component's module does. Review is for what remains — whether
view data carries decisions, whether drawing writes — and is done rule by rule against this list,
not from general impressions.

**Tests: view data in, drawing and events out, is the whole contract of a component.** A
component built from view data alone can be tested without the rest of the application, so each
region is tested fast and in isolation. The integration tests through the top-level component
are what check the mediation that the component tests cannot see.

## Examples

Composition — one function draws every region, and each region draws itself:

```
// Bad: the top-level component draws the contents of every region
topLevel.draw() { drawListRows(state.items); drawDetailFields(state.selected); drawStatus(state.message) }

// Good: each region's component draws itself from its view data
topLevel.draw() { list.draw(); detail.draw(); statusBar.draw() }
```

State ownership — one fact with two owners, and local state carried by the top level:

```
// Bad: the selection is held twice and drifts; the top level holds the list's scroll position
topLevel.selectedId; list.selectedId; topLevel.listScrollOffset

// Good: the shared selection is application state; the scroll position is the list's own
appState.selectedId; list.scrollOffset   // private to the list
```

Data down — a component deciding from the application state, and one drawing its view data:

```
// Bad: the component receives all state and decides whether editing is allowed
detail.draw(appState) { editButton.enabled = appState.user.role == ADMIN && !appState.item.locked }

// Good: the decision arrives computed in the view data
detail.draw(view) { editButton.enabled = view.canEdit }
```

Events up — a component changing its neighbour, and one reporting an event:

```
// Bad: the list reaches into the detail pane
list.onRowClicked(row) { detail.item = row.item }

// Good: the list reports; the top level updates the application state and the views
list.onRowClicked(row) { emit(RowSelected(row.id)) }
```

Keyboard — a hand-built dispatch table beside the framework's propagation:

```
// Bad: the top level routes every key itself, in parallel with the framework
topLevel.keyTable = { "ctrl+f": searchBox, "down": list, ... }

// Good: the focused component handles its keys; unhandled keys propagate to the parent
list.onKey(key) { if key == DOWN { moveCursor(); return HANDLED } return UNHANDLED }
```

Dialogs — one flag per dialog, and one state with its priority in one place:

```
// Bad: an error and a confirmation can both be open; nothing decides which wins
topLevel.showError = true; topLevel.showConfirm = true

// Good: one state, one place that orders competing demands
topLevel.dialog = nextDialog(topLevel.dialog, demand)   // None | Error(..) | Confirm(..)
```

Redraw — every component re-handed new view data, and only the changed one:

```
// Bad: any change rebuilds and re-hands all view data, so the whole window redraws
onChange() { for c in components { c.setView(buildView(c, appState)) } }

// Good: a component receives new view data only when its data differs
onChange() { for c in components { v = buildView(c, appState); if v != c.view { c.setView(v) } } }
```

Drawing is read-only — writing inside drawing, and preparing before it:

```
// Bad: drawing flips an initialisation flag and changes a global style
list.draw() { if !initialised { initialised = true; loadIcons() }; setGlobalFont(BOLD) }

// Good: set up outside drawing; pass styles to the call that uses them
list.init() { loadIcons() }
list.draw() { drawText(row.label, font: BOLD) }
```

Focus — a component moving focus into another region, and one reporting instead:

```
// Bad: the list jumps into the detail pane's input field
list.onKey(DOWN) { if atLastRow { detail.nameField.focus() } }

// Good: the list reports that it reached its edge; the top level decides where focus goes
list.onKey(DOWN) { if atLastRow { emit(FocusLeftRegion(DOWN)) } }
```

Enforcement — a rule kept by a comment, and the same rule kept by visibility:

```
// Bad: the application state is public; only a comment asks components not to write it
public appState   // do not modify from components

// Good: only the top-level component's module can reach it
module topLevel { private appState }   // a component that names it fails to compile
```

Tests — every component test starting the whole application, and a component tested alone:

```
// Bad: to check one list, the test starts the application and navigates to the screen
app = startApp(); app.open(MAIN); assert(app.find("list").rows == 3)

// Good: the component is built from view data; drawing and emitted events are asserted
list = List(view: ListView(rows: [a, b, c])); assert(list.drawnRows == 3)
list.click(row: 1); assert(list.emitted == [RowSelected(b.id)])
```

## Evidence

Show these outputs rather than asserting the screen follows these rules.

- **State reach**: a search for uses of the application state outside the top-level component's
  module returning no matches, or the build output showing a component that names it fails to
  compile.
- **Private component state**: the type checker or compiler run, exit code 0, with each
  component's state declared non-public in the diff.
- **Component isolation**: a component test run that constructs each changed component from view
  data alone — no application state, no top-level component — with 0 failures, asserting both
  what it draws and the events it emits.
- **Mediation**: an integration test run through the top-level component covering each
  interaction the change adds or alters, with 0 failures.
- **Redraw scope**: for a change to redraw behaviour, a test or a redraw count showing that a
  change in one region redraws that region's component only.
- **Review coverage**: for the rules a machine cannot check, the review record listing each rule
  in this skill with the site that satisfies it or the finding against it.
