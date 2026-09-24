# Refinement trajectory exports

Cell-, task-, arm-, and method-level anytime/retention summaries regenerated
from the distributed run logs. `retained_best` uses exact winner semantics: it
is true only when the terminal candidate score exactly equals the selected-best
canonical score. The numerical reporting tolerance is not used for this
categorical statistic. `retained_best_changes.json` records the affected cells
and aggregate manuscript values from correcting the earlier tolerance rule.
`manuscript_retention_updates.json` gives file/line red-removal and green-addition
instructions for the manuscript writer, including full-precision method
aggregates. It does not modify the manuscript.
