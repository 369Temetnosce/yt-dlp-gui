# Feature Request Template

## FEATURE

**Name:** [Feature Name]

**Description:** [Clear description of what you're building]

**User Story:** As a user, I want to [action] so that [benefit].

---

## LAYER IMPACT

Which layers need changes?

- [ ] **UI Layer** (main_window.py) - New widgets, layouts, signals
- [ ] **Logic Layer** (download_manager.py) - Business logic, threading
- [ ] **Wrapper Layer** (ytdlp_wrapper.py) - yt-dlp commands
- [ ] **Config** (config_manager.py) - Settings persistence

---

## EXAMPLES

**Patterns to Follow:**
- `@examples/python/qthread-worker.py` - Threading pattern
- `@examples/testing/mock-subprocess.py` - Test patterns
- `@.windsurfrules.md` - Project standards

---

## ACCEPTANCE CRITERIA

- [ ] Feature works as described
- [ ] UI remains responsive during operation
- [ ] Error cases handled with user-friendly messages
- [ ] Unit tests written and passing
- [ ] No regressions in existing functionality

---

## NOTES

[Any additional context, edge cases, or considerations]
