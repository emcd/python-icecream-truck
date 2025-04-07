# TODOs for ictruck

## Polish
- Deeper validation: `active_flavors` contents (int/str), `trace_levels` values
  (int) in `install`.
- Printer factory validation: Check `TextIOBase` or callable output in
  `install`.

## Ideas
- Debugger Stats: Track hits in `_debuggers`, expose via `Truck.stats()`.
- Custom Context: `include_context` as callable for custom frame info.
- Flavor Aliases: Define in `Vehicle`/`Module` (e.g., `verbose` → `TRACE3`).
- Disable Switch: `ICTRUCK_DISABLE` or `install( enabled=False )`.
- CLI Recipes: Docs for `argparse`, `click`, `typer`, `tyro`.

## Notes for Future Conversations
- **Performance**: Profile `printer_factory` and `_debuggers` caching—ensure no
  bottlenecks in production use.
