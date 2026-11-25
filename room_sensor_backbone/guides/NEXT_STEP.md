# Next step — visualisation, not another source rewrite

You now have configurable paced generators, raw recordings for offline analysis,
and a bounded selected-series snapshot. The next iteration should use these data
products to make plots; it should not duplicate acquisition or calibration logic.

Start with a finished recording, then consider refreshing a view from
`latest.json`. Read `docs/05_VISUALISATION_NEXT.md` for the interface and failure
states the plot must respect. No browser, plotting dependency, background thread,
or HTTP endpoint is included in this iteration.

The earlier planning note is preserved as `PREVIOUS_GENERATOR_PLAN.md` for context.
Its statement that simulation is not yet assigned belongs to the previous stage.
