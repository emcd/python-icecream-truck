# TODOs for ictruck

## Environment Variables
- Names: `ICTRUCK_TRACE`, `ICTRUCK_TRACE_MODULES`, `ICTRUCK_FLAVORS`,
  `ICTRUCK_FLAVORS_MODULES`.
- Format: `module:values+module:values` (e.g., `x.y:foo,bar+x.z:baz`).
- Helpers: `_parse_env_trace()`, `_parse_env_flavors()` in `install`.

## Polish
- Deeper validation: `active_flavors` contents (int/str), `trace_levels` values
  (int) in `install`.
- Printer factory validation: Check `TextIOBase` or callable output in
  `install`.
- AOP decorator: Handle nested types (e.g., `Mapping` contents), integrate
  `executing` for context.
- Exceptions: Expand `_attribute_visibility_includes_` in `Omniexception`.

## Ideas
- Logging: Extend `specialists.py` with more factories (e.g., stream-based,
  `rich.console`)?
- Debugger Stats: Track hits in `_debuggers`, expose via `Truck.stats()`.
- Custom Context: `include_context` as callable for custom frame info.
- Flavor Aliases: Define in `Vehicle`/`Module` (e.g., `verbose` → `TRACE3`).
- Disable Switch: `ICTRUCK_DISABLE` or `install( enabled=False )`.
- CLI Recipes: Docs for `argparse`, `click`, `typer`, `tyro`.
- Formatter Enum: Enum for `Null`, `Pretty`, `Rich` with terminal detection.

## Notes for Future Conversations
- **Testing**: Write `pytest` suite—cover `install`, `register_module`,
  `produce_logging_truck`, and flavor handling. Test edge cases like missing
  modules or invalid flavors.
- **Docs**: Expand with a full user guide (e.g., `docs/sphinx/`). Include
  advanced recipes (e.g., `rich` integration) and CLI examples.
- **Performance**: Profile `printer_factory` and `_debuggers` caching—ensure no
  bottlenecks in production use.
- **Logo**: Consider a fun ice cream truck logo for the README (SVG or
  emoji-based?).
- **Release**: Prep for PyPI—double-check `pyproject.toml`, versioning, and
  dependencies.
