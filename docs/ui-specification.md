# Desktop interface specification

Source: `source-requirements.md` §§8–11 and 31. Phase 0 contains only a startup window. Phase 2 product interaction is locked.

## Planned workflow

The user should enter a scenario, see which values were entered or derived, lock appropriate inputs, receive explicit consistency and underdetermination messages, inspect payment and cost outputs, and save or reopen local history. Scenario names and colors, duplication, comparison entry points, and single-scenario charts belong to the authorized later phases. Never silently overwrite an entered value. Explain inferred values and reject invalid submissions. Unknown future rates must remain labeled assumptions.

## Interaction and accessibility tests

Test keyboard navigation, readable labels, error focus, invalid and conflicting inputs, recalculation after edits, locked inputs, window startup, responsive long operations, and offline use. Confirm saved data is not lost on navigation or validation failure. Charts need numeric alternatives and explicit units; exact visual treatment awaits owner review.

## Owner decisions before implementation

Approve the Phase 2 workflow, default language and localization path, validation presentation, charts, and persistence/deletion behavior. The Phase 0 window establishes no product UI decision beyond PySide6 startup feasibility.
