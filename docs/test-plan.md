# Test plan

Every test case the library commits to covering, and the test function that covers it. The library is
built test-first: cases are agreed here, tests are written against them, then the implementation is
written to pass. The **Test function** column is the auditable trail — it is filled in as each test is
written, so an empty cell means the case is agreed but not yet covered.

Case IDs are stable and referenceable. Do not renumber; retire an ID rather than reuse it. Every test
function carries its case ID as its docstring, so the trail reads in both directions.

All test functions live in `src/evennia_survival/tests.py`.

Behaviour is agreed here first, before any test or code — see
[test-first-process.md](../../../design/test-first-process.md).

| Prefix | Covers |
|---|---|
| `SC` | The scaffold — the library is installed and the runner reaches it |
| `ST` | `SurvivalStage` — the base class a consumer subclasses to declare a meter's stages |

## Fixtures

The fake objects the suite needs, named and purposed.

| Fixture | Purpose |
|---|---|
| `HungerStageStub` | A consumer's stage enum as the library expects to receive one — several members with consecutive values, every one declared the same way: a value and both message strings. Declared in `tests.py`, since a consumer declares theirs in their own module |
| `GappedStageStub` | The same with a hole in its values. Nothing in `ST` uses it: consecutive values are a boot requirement, so this is the negative fixture for the `CF` case that refuses a set boot cannot work with |

## Cases

One section per function or surface, each with its own prefix and its own table.

### SC — the scaffold

Not behaviour of the library, but a check that there is a library to test. These fail when the editable
install is missing, when the test settings do not name the app, or when the runner cannot find the test
module — each of which otherwise looks like "no tests ran".

| ID | Case | Test function |
|---|---|---|
| SC-01 | The package is importable and carries its version | test_sc_01_the_package_is_importable_and_versioned |
| SC-02 | A log call outside an Evennia engine is a silent no-op rather than an error | test_sc_02_the_log_shim_is_a_no_op_outside_evennia |

### ST — the stage base class

A meter's stages are declared by the consumer as an enum subclassing `SurvivalStage`. The library ships
the base class, so what a stage is comes from inheritance rather than from a documented shape the
library has to inspect.

The base is int-backed. That is what makes a member comparable, so a consumer's tick hook can write
`if hunger <= HungerStage.FAMISHED` instead of matching on names — and it is what would silently break
if the base were ever changed to a plain `Enum`.

A member also steps to its neighbours, so code holding a stage can ask for the one above or below
without holding the list as well. `shifted(-1)` is one stage worse, `shifted(+3)` restores three.

**Stepping is arithmetic on the value, not a walk along the declaration.** Boot requires consecutive
values, so the member one worse is the member whose value is one lower — which means the library never
reads the order the consumer wrote their members in, and they are free to lay the file out whichever
way reads best to them.

**Lower value means a worse stage.** This is the one rule with no enforcement behind it: a set numbered
the other way round is consecutive and unique and passes every boot check, and produces a meter where
eating makes you hungrier. It is stated in the docs and shown in the example because that is the only
place it can be caught.

**Judging whether a declared set is workable is not this class's job.** A member cannot refuse the
company it is declared in, and a refusal belongs with every other configuration refusal — so duplicate
values, non-consecutive values, an empty set and anything else about the set as a whole are checked at
boot and land in the `CF` cases.

| ID | Case | Test function |
|---|---|---|
| ST-01 | A member declared with a value and two message strings carries all three | test_st_01_a_member_carries_its_value_and_both_messages |
| ST-02 | A member declared without both message strings is refused, so every stage is written the same way | test_st_02_a_member_missing_its_messages_is_refused |
| ST-03 | Members compare in value order, so a worse stage is less than a better one | test_st_03_members_compare_in_value_order |
| ST-04 | Shifting returns the member that many values away, in either direction | test_st_04_shifting_returns_the_member_that_many_values_away |
| ST-05 | Shifting past the lowest value returns the lowest member rather than raising | test_st_05_shifting_past_the_lowest_value_clamps |
| ST-06 | Shifting past the highest value returns the highest member rather than raising | test_st_06_shifting_past_the_highest_value_clamps |

## Open decisions

Questions still open, listed so they are not forgotten, and deliberately without cases. A case is a
commitment, so nothing becomes one until it has been decided. The planned shape for most of what
follows is in [design.md](design.md).

- **[TBD — needs discussion: what a meter is.** Stages, their ordering, the thresholds that change
  behaviour, and how a consumer names them.]
- **[TBD — needs discussion: the tick.** What walks the meters, how often, which characters it reaches,
  and how it behaves when the game runs as more than one process.]
- **[TBD — needs discussion: the regeneration pipeline.** How several meters combine into one
  heal/stall/bleed decision, and how the outcome is handed back to the consumer.]
- **[TBD — needs discussion: the container primitive.** Whether a refillable drink container is library
  mechanism or consumer content.]
- **[TBD — needs discussion: settings and their defaults**, and which of them have no safe default and
  so are refused at boot.]
