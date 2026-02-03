# Validation Findings: Real-World Code Quality Issues

**Purpose**: Documents legitimate code quality issues found by thai-lint in popular open-source
repositories, with authoritative citations explaining why each pattern is problematic.

**Scope**: Representative findings from validation trials against 16 popular repositories
(10 Python, 6 Rust) totaling thousands of source files.

---

## Overview

thai-lint was validated against popular, well-maintained open-source repositories to verify
that detected violations represent real code quality issues. This document presents
representative findings across both Python and Rust codebases, organized by anti-pattern
category. Repository names are omitted out of respect for the maintainers — these are
excellent projects, and every codebase accumulates complexity over time.

All examples shown are true positives: patterns that authoritative sources identify as
harmful to readability, maintainability, or performance.

## Aggregate Results

### Python — 10 Repositories, 11 Rules

| Rule | Total Violations | Repos Affected |
|------|-----------------|----------------|
| Magic Numbers | 25,135 | 10/10 |
| DRY (Duplicate Code) | 12,249 | 10/10 |
| Lazy Ignores | 2,760 | 10/10 |
| Nesting | 2,116 | 10/10 |
| Print Statements | 1,801 | 9/10 |
| Stringly-Typed | 1,776 | 9/10 |
| SRP | 1,108 | 10/10 |
| Stateless Class | 1,045 | 10/10 |
| LBYL | 910 | 10/10 |
| Method Property | 420 | 10/10 |
| Collection Pipeline | 365 | 10/10 |

### Rust — 6 Repositories, 6 Rules

| Rule | Total Violations | Repos Affected |
|------|-----------------|----------------|
| Magic Numbers | 1,151 | 6/6 |
| Unwrap Abuse | 479 | 6/6 |
| Nesting | 248 | 6/6 |
| SRP | 194 | 6/6 |
| Clone Abuse | 159 | 6/6 |
| Blocking-in-Async | 1 | 1/6 |

---

## Selected Findings

| # | Language | Rule | Finding | Key Metric | Primary Source |
|---|----------|------|---------|------------|----------------|
| 1 | Python | SRP | God class in terminal library | 45 methods, 1,752 lines | Martin, *Clean Code* — SRP |
| 2 | Python | SRP | God class in validation library | 1,717 lines | Brown et al., *AntiPatterns* — God Object |
| 3 | Python | Nesting | ANSI parser nested 13 levels deep | Depth 13 | Linux Kernel Coding Style |
| 4 | Python | LBYL | hasattr chain with false confidence | 3 hasattr checks | Python Glossary — EAFP |
| 5 | Python | Stringly-Typed | Same 4 strings validated in 4 files | 4 files, 4 raw strings | Martin, *Clean Code* — G25 |
| 6 | Python | Collection Pipeline | Loop with 3 continue-based filters | 3 filter conditions | Fowler, *Refactoring* |
| 7 | Python | DRY | Identical TypeVar block in 2 modules | 11 duplicate lines | Hunt & Thomas, *Pragmatic Programmer* |
| 8 | Python | LBYL | Dict key check before access | Redundant lookup | Python Glossary — EAFP |
| 9 | Rust | Unwrap Abuse | Unwrap on user-derived URI host | Panic on malformed input | Rust Book, Ch. 9.3 |
| 10 | Rust | Unwrap Abuse | Unwrap in error return path | Panic in sync primitive | Rust Book, Ch. 9.2 |
| 11 | Rust | Clone Abuse | self.clone() inside proxy loop | Full struct clone per iteration | Rust Performance Book |
| 12 | Rust | Clone Abuse | Double clone (key + value) in loop | 2 clones per iteration | Rust API Guidelines — C-CALLER-CONTROL |
| 13 | Rust | Magic Numbers | Unexplained buffer size `58` | Undocumented derivation | Martin, *Clean Code* — G25 |
| 14 | Rust | SRP | 35 methods on a 2-field struct | 35 methods (5x threshold) | Rust API Guidelines — C-NEWTYPE |
| 15 | Rust | Nesting | Async state machine nested 7 deep | Depth 7 | Campbell, *Cognitive Complexity* |

---

## Python Findings

### 1. God Class — 45 Methods, 1,752 Lines

A terminal output library's central class accumulates printing, styling, recording,
HTML export, SVG export, text export, paging, input handling, status display, and
progress bars into a single 1,752-line class with 45 methods.

```python
class Console:
    """A high level console interface."""
    # 45 methods, 1,752 lines
    # Handles: printing, styling, recording, HTML export,
    # SVG export, paging, input, status, progress bars...
```

**Why this matters:**

Robert C. Martin, *Clean Code* (2008) — The Single Responsibility Principle:

> "A class should have only one reason to change."

A class with 45 methods has many reasons to change. Modifications to SVG export risk
breaking progress bar rendering. Testing any one responsibility requires instantiating
the entire object. The Rust API Guidelines similarly advocate for small, focused types
with clear single responsibilities
([C-NEWTYPE](https://rust-lang.github.io/api-guidelines/type-safety.html)).

---

### 2. God Class — Schema Generator, 1,717 Lines

A data validation library's schema generation class spans 1,717 lines. The class handles
type resolution, field processing, validator wiring, JSON schema mapping, and config
management in a single file.

```python
class GenerateSchema:
    """Generate core schema for a Pydantic model, dataclass
    and types like `str`, `datetime`, ... ."""

    __slots__ = (
        '_config_wrapper_stack',
        '_ns_resolver',
        '_typevars_map',
        'field_name_stack',
        'model_type_stack',
        'defs',
    )
    # 1,717 lines follow...
```

**Why this matters:**

Brown et al., *AntiPatterns: Refactoring Software, Architectures, and Projects in Crisis*
(1998) define the "God Object" as an object that knows too much or does too much. God
objects create tight coupling, resist reuse, and become bottlenecks for team collaboration
since many changes touch the same file.

---

### 3. Excessive Nesting Depth — 13 Levels Deep

An ANSI escape code parser nests 13 levels deep: method body, `for` loop, `elif` branch,
`for` loop, `elif` branch, `with` block, `elif` branch, and function call.

```python
def decode_line(self, line: str) -> Text:
    for plain_text, sgr, osc in _ansi_tokenize(line):      # depth 1
        if plain_text:                                       # depth 2
            append(plain_text, self.style or None)
        elif sgr is not None:                                # depth 2
            codes = [...]
            for code in iter_codes:                          # depth 3
                if code == 0:                                # depth 4
                    self.style = _Style.null()
                elif code == 38:                              # depth 4
                    with suppress(StopIteration):             # depth 5
                        color_type = next(iter_codes)
                        if color_type == 5:                   # depth 6
                            self.style += _Style.from_color(
                                from_ansi(next(iter_codes))
                            )
                        elif color_type == 2:                 # depth 6
                            self.style += _Style.from_color(  # depth 7+
                                from_rgb(
                                    next(iter_codes),
                                    next(iter_codes),
                                    next(iter_codes),
                                )
                            )
```

**Why this matters:**

The Linux Kernel Coding Style
([kernel.org](https://www.kernel.org/doc/html/latest/process/coding-style.html)):

> "If you need more than 3 levels of indentation, you're screwed anyway, and should fix
> your program."

G. Ann Campbell, *Cognitive Complexity* (SonarSource, 2021)
([paper](https://www.sonarsource.com/resources/cognitive-complexity/)) demonstrates that
nesting imposes a multiplicative cognitive burden: each additional level requires the
reader to maintain more context in working memory. A doubly-nested `if` is not twice as
hard as a top-level `if` — it is exponentially harder.

---

### 4. Look Before You Leap — hasattr Chain

An HTTP library checks for attributes with `hasattr` before accessing them, rather than
using Python's EAFP (Easier to Ask Forgiveness than Permission) idiom.

```python
def super_len(o):
    total_length = None

    if hasattr(o, "__len__"):
        total_length = len(o)
    elif hasattr(o, "len"):
        total_length = o.len
    elif hasattr(o, "fileno"):
        try:
            fileno = o.fileno()
        except (io.UnsupportedOperation, AttributeError):
            # AttributeError is a surprising exception, seeing
            # as how we've just checked that `hasattr(o, 'fileno')`.
            # It happens for objects obtained via
            # `Tarfile.extractfile()`, per issue 5229.
            pass
```

The code's own comment reveals the flaw: `hasattr` returned `True`, but calling the
attribute still raised `AttributeError`. The LBYL check gave false confidence.

**Why this matters:**

The Python Glossary defines
[EAFP](https://docs.python.org/3/glossary.html#term-EAFP) as the preferred Python style:

> "Easier to ask for forgiveness than permission. This common Python coding style assumes
> the existence of valid keys or attributes and catches exceptions if the assumption proves
> false."

The glossary contrasts this with
[LBYL](https://docs.python.org/3/glossary.html#term-LBYL):

> "Look before you leap... In a multi-threaded environment, the LBYL approach can risk
> introducing a race condition."

---

### 5. Stringly-Typed Parameter — Same 4 Strings in 4 Files

A data analysis library validates an interval boundary parameter against raw strings
in multiple locations across the codebase.

```python
if closed is not None and closed not in {"right", "left", "both", "neither"}:
    raise ValueError("closed must be one of 'right', 'left', 'both', 'neither'")
```

The same set `{"right", "left", "both", "neither"}` appears in 4 separate files. Adding
a new option (e.g., `"half-open"`) requires updating every occurrence.

**Why this matters:**

Robert C. Martin, *Clean Code* (2008), G25 — *Replace Magic Numbers with Named Constants*
extends to string literals: repeated validation of the same string set is a missing enum.

The Python documentation for
[`enum.Enum`](https://docs.python.org/3/library/enum.html) states:

> "An enumeration... can be used to create well-defined symbols for values instead of
> using literal strings or integers."

---

### 6. Embedded Filtering — Loop with 3 Filter Conditions

An HTTP library filters cookies using three sequential `continue` statements inside a
`for` loop, mixing iteration with filtering logic.

```python
def remove_cookie_by_name(cookiejar, name, domain=None, path=None):
    clearables = []
    for cookie in cookiejar:
        if cookie.name != name:
            continue
        if domain is not None and domain != cookie.domain:
            continue
        if path is not None and path != cookie.path:
            continue
        clearables.append((cookie.domain, cookie.path, cookie.name))
```

This could be a single list comprehension with the filter conditions composed together,
separating the "what to select" from the "what to do with it."

**Why this matters:**

Martin Fowler, *Refactoring: Improving the Design of Existing Code* (2018) describes
the Collection Pipeline pattern as replacing loops with chained operations (filter, map,
reduce). The result is more declarative, easier to test, and separates selection logic
from transformation logic.

---

### 7. Duplicate Code — Same 5 TypeVar Declarations in 2 Files

A web framework defines identical `TypeVar` declarations in two separate modules.

```python
# In app.py:
T_shell_context_processor = t.TypeVar(
    "T_shell_context_processor", bound=ft.ShellContextProcessorCallable
)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)

# Identical block in sansio/app.py
```

**Why this matters:**

Andrew Hunt and David Thomas, *The Pragmatic Programmer* (1999) — the DRY principle:

> "Every piece of knowledge must have a single, unambiguous, authoritative representation
> within a system."

Duplicated declarations diverge over time. When one is updated, the other is easily
forgotten, leading to subtle type inconsistencies.

---

### 8. LBYL Dict Key Check

A web framework checks whether a key exists in a dictionary before iterating over the
value, rather than using `.get()` with a default.

```python
for name in names:
    if name in self.template_context_processors:
        for func in self.template_context_processors[name]:
            context.update(self.ensure_sync(func)())
```

The idiomatic alternative is `for func in self.template_context_processors.get(name, [])`,
which eliminates the redundant key lookup and the extra nesting level.

**Why this matters:**

The Python Glossary on
[EAFP](https://docs.python.org/3/glossary.html#term-EAFP) establishes that Python's
design favors direct access with fallback over pre-checking. The `dict.get()` method
exists precisely for this pattern — it performs a single lookup instead of two.

---

## Rust Findings

### 9. Unwrap on User-Derived Input

A web framework's WebSocket client unwraps `uri.host()` without a guard. If a URI passes
scheme validation but lacks a host component, this panics at runtime in code handling
external input.

```rust
if !self.head.headers.contains_key(header::HOST) {
    let hostname = uri.host().unwrap();
    let port = uri.port();
    self.head.headers.insert(
        header::HOST,
        HeaderValue::from_str(&Host { hostname, port }.to_string()).unwrap(),
    );
}
```

**Why this matters:**

The Rust Programming Language, Chapter 9.3 — *To panic! or Not to panic!*
([doc.rust-lang.org](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)):

> "When you choose to return a `Result` value, you give the calling code options. When
> code panics, there's no way to recover."

> "The `unwrap` and `expect` methods are very handy when you're prototyping... They leave
> clear markers in your code for when you're ready to make your program more robust."

Clippy's `unwrap_used` restriction lint reinforces this: "Propagating errors upward with
the `?` operator represents a more sophisticated error-handling approach in production
code."

---

### 10. Unwrap in Error Return Path

An async runtime's oneshot channel uses `.unwrap()` inside an error return path. The value
is logically guaranteed to exist (the sender just wrote it), but a bare unwrap in critical
synchronization code means any invariant violation becomes an unrecoverable panic.

```rust
pub fn send(mut self, t: T) -> Result<(), T> {
    let inner = self.inner.take().unwrap();
    inner.value.with_mut(|ptr| unsafe { *ptr = Some(t) });

    if !inner.complete() {
        return Err(inner.consume_value().unwrap());
    }
    // ...
}
```

**Why this matters:**

The Rust Programming Language, Chapter 9.2 — *Recoverable Errors with Result*
([doc.rust-lang.org](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)):

> "In production-quality code, most Rustaceans choose `expect` rather than `unwrap` and
> give more context about why the operation is expected to always succeed."

At minimum, `.expect("value was just written")` would document the invariant.

---

### 11. Clone-in-Loop — Cloning Self in a Hot Path

An HTTP client clones its entire connector struct inside a proxy-matching loop. Each
matching proxy triggers a full deep copy of the connector, including all its
configuration and connection pool references.

```rust
for prox in self.proxies.iter() {
    if let Some(intercepted) = prox.intercept(&dst) {
        return Box::pin(with_timeout(
            self.clone().connect_via_proxy(dst, intercepted),
            timeout,
        ));
    }
}
```

**Why this matters:**

The Rust Performance Book — *Heap Allocations*
([nnethercote.github.io](https://nnethercote.github.io/perf-book/heap-allocations.html)),
by Nicholas Nethercote (Rust compiler performance engineer):

> "Calling `clone` on a value that contains heap-allocated memory typically involves
> additional allocations... If you see a hot `clone` call that does not seem necessary,
> sometimes it can simply be removed."

The Rust Design Patterns book lists *Clone to satisfy the borrow checker* as an explicit
anti-pattern
([rust-unofficial.github.io](https://rust-unofficial.github.io/patterns/anti_patterns/borrow_clone.html)):

> "Using `.clone()` causes a copy of the data to be made. Any changes between the two
> are not synchronized — as if two completely separate variables exist."

---

### 12. Double Clone in a Loop

A CLI argument parser clones both the key and value on every loop iteration, when
consuming the map with `.drain()` or `.into_iter()` would transfer ownership without
any allocation.

```rust
for (name, matched_arg) in vals_map.iter_mut() {
    self.matches.args.insert(name.clone(), matched_arg.clone());
}
```

**Why this matters:**

The Rust API Guidelines — C-CALLER-CONTROL
([rust-lang.github.io](https://rust-lang.github.io/api-guidelines/flexibility.html)):

> "If a function requires ownership of an argument, it should take ownership of the
> argument rather than borrowing and cloning the argument."

The idiomatic Rust approach is to consume the source collection when ownership is needed,
avoiding redundant allocations.

---

### 13. Magic Number — Unexplained Buffer Size

A serialization library uses `58` as a buffer size in the core deserializer. The value
is carefully calculated (19 characters for the format string plus 39 digits for a max
i128), but no constant or comment explains the derivation.

```rust
fn visit_i128<E>(self, v: i128) -> Result<Self::Value, E>
where
    E: Error,
{
    let mut buf = [0u8; 58];
    let mut writer = crate::format::Buf::new(&mut buf);
    fmt::Write::write_fmt(
        &mut writer,
        format_args!("integer `{}` as i128", v),
    ).unwrap();
```

**Why this matters:**

Robert C. Martin, *Clean Code* (2008), G25 — *Replace Magic Numbers with Named Constants*:

A named constant like `MAX_I128_ERROR_MSG_LEN` would communicate intent. You can search
for the constant name but cannot meaningfully search for `58`. If the format string
changes, a developer must re-derive the buffer size rather than updating a single
constant.

---

### 14. God Struct — 35 Methods on a 2-Field Struct

A web framework's request wrapper has only two fields but exposes 35 methods — 5x the
recommended maximum. It accumulates request parsing, header access, connection info,
path extraction, and application data access into a single type.

```rust
pub struct ServiceRequest {
    req: HttpRequest,
    payload: Payload,
}

impl ServiceRequest {
    // 35 methods follow...
}
```

**Why this matters:**

The Rust API Guidelines — Type Safety
([rust-lang.github.io](https://rust-lang.github.io/api-guidelines/type-safety.html))
advocate for small, focused types:

> "Newtypes can statically distinguish between different interpretations of an underlying
> type... Use a deliberate type to convey interpretation and invariants."

A struct with 35 methods is doing the work of several types. Decomposing into focused
types (e.g., separating header access from path extraction) improves testability and
reduces coupling.

---

### 15. Nesting Depth 7 in Async State Machine

An async runtime's notification primitive reaches nesting depth 7 in a lock-free state
machine: `loop` > `match` > arm > `loop` > `match` > arm > compare-and-swap.

```rust
fn poll_notified(self, waker: Option<&Waker>) -> Poll<()> {
    'outer_loop: loop {                              // depth 1
        match *state {                               // depth 2
            State::Init => {                         // depth 3
                // ...
                loop {                               // depth 4
                    match get_state(curr) {           // depth 5
                        EMPTY => {                    // depth 6
                            let res = notify.state    // depth 7
                                .compare_exchange(/* ... */);
```

**Why this matters:**

G. Ann Campbell, *Cognitive Complexity* (SonarSource, 2021)
([paper](https://www.sonarsource.com/resources/cognitive-complexity/)):

> Each nesting level adds an incremental cognitive penalty. A structure at depth 7
> requires the reader to maintain 7 levels of context simultaneously — which branch
> was taken, which loop iteration, which match arm.

Clippy's `excessive_nesting` lint
([rust-lang.github.io](https://rust-lang.github.io/rust-clippy/master/index.html))
flags blocks nested beyond a configurable threshold (default: 3), noting that deep
nesting "can severely hinder readability."

---

## Authoritative Sources Summary

| Source | Type | Patterns Covered |
|--------|------|------------------|
| Robert C. Martin, *Clean Code* (2008) | Software engineering canon | SRP, magic numbers |
| The Rust Programming Language, Ch. 9 | Official Rust documentation | Unwrap abuse |
| Rust API Guidelines | Official Rust guidelines | Clone abuse, SRP, type safety |
| Rust Performance Book (Nethercote) | Rust compiler engineer | Clone performance |
| Rust Design Patterns Book | Community standard reference | Clone anti-pattern |
| Linux Kernel Coding Style | Industry standard | Nesting depth |
| G. Ann Campbell, *Cognitive Complexity* | Industry-standard metric | Nesting depth |
| Python Glossary (EAFP/LBYL) | Official Python documentation | LBYL anti-pattern |
| Martin Fowler, *Refactoring* (2018) | Software engineering canon | Collection pipelines |
| Hunt & Thomas, *The Pragmatic Programmer* (1999) | Software engineering canon | DRY principle |
| Rust Clippy lints | Official Rust linter | Unwrap, clone, nesting |
