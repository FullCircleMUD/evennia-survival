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
| `CF` | Settings, and the boot check that refuses a configuration the library cannot work with |

## Fixtures

The fake objects the suite needs, named and purposed.

| Fixture | Purpose |
|---|---|
| `tests/stage_stubs.py` | Every stage enum the suite needs, in one module that **imports nothing but `evennia_survival.stages`**. `test_settings.py` points the two settings here, and `ready()` resolves them during `django.setup()` — so anything this module imported would be pulled in while the app registry is still being built |
| `HungerStageStub` | A consumer's stage enum as the library expects to receive one — several members with consecutive values, every one declared the same way: a value and both message strings |
| `GappedStageStub` | The same with a hole in its values. Nothing in `ST` uses it: consecutive values are a boot requirement, so this is the negative fixture for `CF-07` |
| `DuplicateStageStub` | Two members declaring the same value. Python aliases them silently, so this can be declared at module scope — it is only boot that objects. `CF-06` |
| `EmptyStageStub` | A `SurvivalStage` subclass with no members at all. `CF-05` |
| `NotAStage` | A plain class, for a setting pointing at something that is not a stage enum. `CF-04` |
| `tests/raising_stage_module.py` | A consumer's stage module that fails on import. It lives outside `tests.py` because importing it raises, which is the point. `CF-10` |

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

### CF — settings and boot validation

Each meter's stages reach the library as a setting naming a module, per
[library-standards.md](../../../design/library-standards.md) § Consumer-authored config. Neither
setting has a safe default — there is no stage list the library could invent — so both are validated
once in `check_settings()`, called from `AppConfig.ready()`, and the instance does not start without
them. The accessors that read them afterwards do no checking of their own: boot has already guaranteed
the value is there and usable.

**Every problem in one raise.** A consumer installing the library typically has more than one thing to
set, and stopping at the first turns that into fix-restart-fix-restart. Problems are collected and
raised together, one per line behind a module-level prefix constant, which is also what lets a test
count them without pinning any wording.

**A stage module that will not import is refused**, whatever the reason — the module exists because
this library asked for it, so its failure is this library's business to report. The underlying error is
chained rather than swallowed, so the consumer gets both the setting that is wrong and the traceback
saying why.

Cases assert that a refusal happens, not what it says. The exception is `CF-08`, where the count of
problems *is* the behaviour under test.

**The two clock intervals are required too, not defaulted.** The library could invent a cadence, but
the right one is a game-design decision — a default would ship our number in someone's game without
anyone having chosen it. Each must be set, must be an integer, and must be positive.

**An integer, not something that converts to one.** `"1200"` is refused along with `1200.0` — one form
to write and none to guess at. Zero and negatives are refused separately from the type: zero is a
perfectly good integer that gives a meter which never moves, with nothing anywhere to say why.

**The suite boots as a configured instance**, because `ready()` runs the check during `django.setup()`
— so `tests/test_settings.py` declares both settings, and a case wanting one absent overrides it to
`None`. The check reads `getattr(settings, name, None)`, so undeclared and `None` are the same path by
construction rather than by approximation.

| ID | Case | Test function |
|---|---|---|
| CF-01 | A correctly configured pair of settings raises nothing | test_cf_01_a_valid_configuration_raises_nothing |
| CF-02 | A setting that is not declared at all is refused | test_cf_02_an_undeclared_setting_is_refused |
| CF-03 | A setting naming a module path that does not resolve is refused | test_cf_03_a_path_that_does_not_resolve_is_refused |
| CF-04 | A setting naming something that is not a `SurvivalStage` subclass is refused | test_cf_04_something_that_is_not_a_stage_enum_is_refused |
| CF-05 | A stage enum with no members is refused | test_cf_05_a_stage_enum_with_no_members_is_refused |
| CF-06 | Two members sharing a value are refused | test_cf_06_two_members_sharing_a_value_are_refused |
| CF-07 | Values that are not consecutive are refused | test_cf_07_non_consecutive_values_are_refused |
| CF-08 | Two problems at once produce one raise carrying both, not the first alone | test_cf_08_two_problems_produce_one_raise_carrying_both |
| CF-09 | A problem in the thirst setting alone is reported, so both meters are checked | test_cf_09_a_problem_in_the_thirst_setting_alone_is_reported |
| CF-10 | A stage module that raises on import is refused, with the underlying error chained | test_cf_10_a_stage_module_that_raises_on_import_is_refused |
| CF-11 | `AppConfig.ready()` runs the boot check, so a misconfigured instance refuses to start | test_cf_11_app_ready_runs_the_boot_check |
| CF-12 | An interval that is not set is refused | test_cf_12_an_interval_that_is_not_set_is_refused |
| CF-13 | An interval that is not an integer is refused, a numeric string included | test_cf_13_an_interval_that_is_not_an_integer_is_refused |
| CF-14 | An interval of zero or less is refused | test_cf_14_an_interval_of_zero_or_less_is_refused |
| CF-15 | A problem in the regen interval alone is reported, so both intervals are checked | test_cf_15_a_problem_in_the_regen_interval_alone_is_reported |

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
- **[TBD — needs discussion: the clocks themselves.** The two intervals are settled and covered by
  `CF`; what runs on them, and how the walk over characters behaves when the game runs as more than one
  process, is not.]
