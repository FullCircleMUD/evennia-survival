# SPDX-License-Identifier: BSD-3-Clause
"""Unit tests for evennia-survival. Run via ``python runtests.py``.

Every test carries its case ID from docs/test-plan.md as its docstring, so
the coverage trail reads in both directions.
"""

from unittest import TestCase

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase as DjangoTestCase
from django.test import override_settings

import evennia_survival
from evennia_survival.config import (
    PROBLEM_PREFIX,
    SETTING_HUNGER_STAGES,
    SETTING_METER_INTERVAL,
    SETTING_REGEN_INTERVAL,
    SETTING_THIRST_STAGES,
    check_settings,
)
from evennia_survival.log import survival_log
from evennia_survival.services import survival_tick
from evennia_survival.stages import SurvivalStage
from tests.stage_stubs import HungerStageStub


HUNGER_STAGES = "tests.stage_stubs.HungerStageStub"
GAPPED_STAGES = "tests.stage_stubs.GappedStageStub"
DUPLICATE_STAGES = "tests.stage_stubs.DuplicateStageStub"
EMPTY_STAGES = "tests.stage_stubs.EmptyStageStub"
NOT_A_STAGE = "tests.stage_stubs.NotAStage"
MISSING_MODULE = "tests.stage_stubs.NoSuchStageEnum"
RAISING_MODULE = "tests.raising_stage_module.HungerStage"


class ScaffoldTests(TestCase):
    """SC — the library is installed and the runner reaches it."""

    def test_sc_01_the_package_is_importable_and_versioned(self):
        """SC-01"""
        self.assertTrue(evennia_survival.__version__)

    def test_sc_02_the_log_shim_is_a_no_op_outside_evennia(self):
        """SC-02"""
        self.assertIsNone(survival_log("scaffold check"))


class SurvivalStageTests(TestCase):
    """ST — the stage base class."""

    def test_st_01_a_member_carries_its_value_and_both_messages(self):
        """ST-01"""
        stage = HungerStageStub.HUNGRY

        self.assertEqual(stage.value, 3)
        self.assertEqual(stage.first_person, "You are hungry.")
        self.assertEqual(stage.third_person, "$You() $conj(look) hungry.")

    def test_st_02_a_member_missing_its_messages_is_refused(self):
        """ST-02"""
        with self.assertRaises(TypeError):

            class BareStageStub(SurvivalStage):
                FULL = 5

    def test_st_03_members_compare_in_value_order(self):
        """ST-03"""
        self.assertLess(HungerStageStub.STARVING, HungerStageStub.HUNGRY)
        self.assertGreater(HungerStageStub.FULL, HungerStageStub.PECKISH)
        self.assertLessEqual(HungerStageStub.FAMISHED, HungerStageStub.FAMISHED)

    def test_st_04_shifting_returns_the_member_that_many_values_away(self):
        """ST-04"""
        self.assertIs(HungerStageStub.HUNGRY.shifted(-1), HungerStageStub.FAMISHED)
        self.assertIs(HungerStageStub.HUNGRY.shifted(2), HungerStageStub.FULL)

    def test_st_05_shifting_past_the_lowest_value_clamps(self):
        """ST-05"""
        self.assertIs(HungerStageStub.FAMISHED.shifted(-5), HungerStageStub.STARVING)

    def test_st_06_shifting_past_the_highest_value_clamps(self):
        """ST-06"""
        self.assertIs(HungerStageStub.PECKISH.shifted(9), HungerStageStub.FULL)


class CheckSettingsTests(TestCase):
    """CF — settings and boot validation.

    ``tests/test_settings.py`` declares both settings, because ``ready()``
    validates them during ``django.setup()`` and the suite has to boot. A case
    wanting one absent overrides it to ``None``: the check reads
    ``getattr(settings, name, None)``, so undeclared and ``None`` are the same
    path rather than merely similar ones.
    """

    def _refuses(self, **overrides):
        """Run the boot check and hand back what it refused with."""
        with override_settings(**overrides):
            with self.assertRaises(ImproperlyConfigured) as caught:
                check_settings()
        return str(caught.exception)

    def test_cf_01_a_valid_configuration_raises_nothing(self):
        """CF-01"""
        with override_settings(
            **{
                SETTING_HUNGER_STAGES: HUNGER_STAGES,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        ):
            check_settings()

    def test_cf_02_an_undeclared_setting_is_refused(self):
        """CF-02"""
        self._refuses(
            **{
                SETTING_HUNGER_STAGES: None,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        )

    def test_cf_03_a_path_that_does_not_resolve_is_refused(self):
        """CF-03"""
        self._refuses(
            **{
                SETTING_HUNGER_STAGES: MISSING_MODULE,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        )

    def test_cf_04_something_that_is_not_a_stage_enum_is_refused(self):
        """CF-04"""
        self._refuses(
            **{
                SETTING_HUNGER_STAGES: NOT_A_STAGE,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        )

    def test_cf_05_a_stage_enum_with_no_members_is_refused(self):
        """CF-05"""
        self._refuses(
            **{
                SETTING_HUNGER_STAGES: EMPTY_STAGES,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        )

    def test_cf_06_two_members_sharing_a_value_are_refused(self):
        """CF-06"""
        self._refuses(
            **{
                SETTING_HUNGER_STAGES: DUPLICATE_STAGES,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        )

    def test_cf_07_non_consecutive_values_are_refused(self):
        """CF-07"""
        self._refuses(
            **{
                SETTING_HUNGER_STAGES: GAPPED_STAGES,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        )

    def test_cf_08_two_problems_produce_one_raise_carrying_both(self):
        """CF-08"""
        # Hunger undeclared, thirst pointed at a class that is not a stage
        # enum: one problem each, and neither cascades into a second.
        message = self._refuses(
            **{
                SETTING_HUNGER_STAGES: None,
                SETTING_THIRST_STAGES: NOT_A_STAGE,
            }
        )

        self.assertEqual(message.count(PROBLEM_PREFIX), 2)

    def test_cf_09_a_problem_in_the_thirst_setting_alone_is_reported(self):
        """CF-09"""
        self._refuses(
            **{
                SETTING_HUNGER_STAGES: HUNGER_STAGES,
                SETTING_THIRST_STAGES: GAPPED_STAGES,
            }
        )

    def test_cf_10_a_stage_module_that_raises_on_import_is_refused(self):
        """CF-10"""
        with override_settings(
            **{
                SETTING_HUNGER_STAGES: RAISING_MODULE,
                SETTING_THIRST_STAGES: HUNGER_STAGES,
            }
        ):
            with self.assertRaises(ImproperlyConfigured) as caught:
                check_settings()

        self.assertIsNotNone(caught.exception.__cause__)

    def test_cf_11_app_ready_runs_the_boot_check(self):
        """CF-11"""
        from django.apps import apps

        app_config = apps.get_app_config("evennia_survival")

        with override_settings(**{SETTING_HUNGER_STAGES: None}):
            with self.assertRaises(ImproperlyConfigured):
                app_config.ready()

    def test_cf_12_an_interval_that_is_not_set_is_refused(self):
        """CF-12"""
        self._refuses(**{SETTING_METER_INTERVAL: None})

    def test_cf_13_an_interval_that_is_not_an_integer_is_refused(self):
        """CF-13"""
        self._refuses(**{SETTING_METER_INTERVAL: "1200"})

    def test_cf_14_an_interval_of_zero_or_less_is_refused(self):
        """CF-14"""
        self._refuses(**{SETTING_METER_INTERVAL: 0})

    def test_cf_15_a_problem_in_the_regen_interval_alone_is_reported(self):
        """CF-15"""
        self._refuses(**{SETTING_REGEN_INTERVAL: 0})


class SurvivalMixinTests(DjangoTestCase):
    """MX — the meters an object carries.

    These need a real Evennia object, because ``AttributeProperty`` reads and
    writes through an attribute handler.
    """

    def setUp(self):
        from evennia import create_object

        from tests.stage_stubs import HungerStageStub

        self.stages = HungerStageStub
        self.best = HungerStageStub.FULL
        self.worst = HungerStageStub.STARVING
        self.obj = create_object(
            "tests.game_typeclasses.SurvivalObjectStub", key="meter carrier"
        )

    def test_mx_01_a_new_object_starts_at_the_best_stage(self):
        """MX-01"""
        self.assertIs(self.obj.hunger_level, self.best)
        self.assertIs(self.obj.thirst_level, self.best)
        self.assertFalse(self.obj.hunger_free_pass_tick)
        self.assertFalse(self.obj.thirst_free_pass_tick)

    def test_mx_02_a_meter_reads_back_as_the_stage_it_was_set_to(self):
        """MX-02"""
        self.obj.hunger_level = self.stages.HUNGRY

        self.assertIs(self.obj.hunger_level, self.stages.HUNGRY)

    def test_mx_03_restoring_moves_the_meter_up(self):
        """MX-03"""
        self.obj.hunger_level = self.stages.STARVING

        self.obj.restore_hunger(2)

        self.assertIs(self.obj.hunger_level, self.stages.HUNGRY)

    def test_mx_04_increasing_moves_the_meter_down(self):
        """MX-04"""
        self.obj.increase_hunger(2)

        self.assertIs(self.obj.hunger_level, self.stages.HUNGRY)

    def test_mx_05_restoring_past_the_best_stage_stops_there(self):
        """MX-05"""
        self.obj.hunger_level = self.stages.HUNGRY

        self.obj.restore_hunger(99)

        self.assertIs(self.obj.hunger_level, self.best)

    def test_mx_06_increasing_past_the_worst_stage_stops_there(self):
        """MX-06"""
        self.obj.increase_hunger(99)

        self.assertIs(self.obj.hunger_level, self.worst)

    def test_mx_07_moving_one_meter_leaves_the_other_alone(self):
        """MX-07"""
        self.obj.increase_thirst(2)

        self.assertIs(self.obj.thirst_level, self.stages.HUNGRY)
        self.assertIs(self.obj.hunger_level, self.best)

    def test_mx_08_restoring_with_a_free_pass_sets_the_flag(self):
        """MX-08"""
        self.obj.hunger_level = self.stages.HUNGRY

        self.obj.restore_hunger(1, free_pass=True)

        self.assertTrue(self.obj.hunger_free_pass_tick)
        self.assertFalse(self.obj.thirst_free_pass_tick)

    def test_mx_09_restoring_without_asking_leaves_the_flag_alone(self):
        """MX-09"""
        self.obj.hunger_level = self.stages.HUNGRY

        self.obj.restore_hunger(1)

        self.assertFalse(self.obj.hunger_free_pass_tick)

    def test_mx_10_resetting_puts_both_meters_back(self):
        """MX-10"""
        self.obj.increase_hunger(3)
        self.obj.increase_thirst(3)

        self.obj.reset_survival_meters()

        self.assertIs(self.obj.hunger_level, self.best)
        self.assertIs(self.obj.thirst_level, self.best)

    def test_mx_11_a_survival_tick_steps_both_meters_down(self):
        """MX-11"""
        survival_tick(self.obj)

        self.assertIs(self.obj.hunger_level, self.best.shifted(-1))
        self.assertIs(self.obj.thirst_level, self.best.shifted(-1))

    def test_mx_12_a_free_pass_is_spent_instead_of_stepping(self):
        """MX-12"""
        self.obj.hunger_level = self.stages.HUNGRY
        self.obj.restore_hunger(1, free_pass=True)

        survival_tick(self.obj)

        # Hunger held where the pass was granted; thirst has no pass and moved.
        self.assertIs(self.obj.hunger_level, self.stages.PECKISH)
        self.assertFalse(self.obj.hunger_free_pass_tick)
        self.assertIs(self.obj.thirst_level, self.best.shifted(-1))

    def test_mx_13_a_pre_tick_hook_returning_false_cancels(self):
        """MX-13"""
        from evennia import create_object

        guarded = create_object(
            "tests.game_typeclasses.GuardedSurvivalStub", key="refuser"
        )

        survival_tick(guarded)

        self.assertIs(guarded.hunger_level, self.best)
        self.assertIs(guarded.thirst_level, self.best)

    def test_mx_14_the_post_tick_hook_sees_the_new_stages(self):
        """MX-14"""
        from evennia import create_object

        recorder = create_object(
            "tests.game_typeclasses.RecordingSurvivalStub", key="recorder"
        )

        survival_tick(recorder)

        self.assertEqual(
            recorder.ndb.post_tick_saw,
            (self.best.shifted(-1), self.best.shifted(-1)),
        )

    def test_mx_15_the_regeneration_hook_defaults_to_doing_nothing(self):
        """MX-15"""
        # The library never calls this — a consumer's clock does, once there
        # is one. What is ours is that it exists with both meters in its
        # signature, so a holder overriding nothing is ticked rather than
        # raising.
        result = self.obj.at_regeneration_tick(
            self.obj.hunger_level, self.obj.thirst_level
        )

        self.assertIsNone(result)
        self.assertIs(self.obj.hunger_level, self.best)
        self.assertIs(self.obj.thirst_level, self.best)
