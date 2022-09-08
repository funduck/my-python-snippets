import json
import pytest
from testfixtures import compare

from health_checking.health_checking import HealthChecking, Checker


class TestChecker:
    def test_should_report_healthy_if_no_components(self):
        check = Checker()
        healthy, descr = check.get_status()
        assert healthy

    def test_should_set_healthy_without_msg(self):
        Checker().set_healthy("any")

    def test_should_set_healthy_with_msg(self):
        Checker().set_healthy("any", "msg")

    def test_should_fail_set_not_healthy_without_msg(self):
        with pytest.raises(Exception):
            Checker().set_not_healthy("any")

    def test_should_set_not_healthy_with_msg(self):
        Checker().set_not_healthy("any", "msg")

class TestCheckerOneComponent:
    def test_should_report_healthy_if_component_is_healthy(self):
        check = Checker()
        check.set_healthy("any")
        healthy, descr = check.get_status()
        assert healthy

    def test_should_report_not_healthy_and_return_some_description_if_component_not_healthy(self):
        check = Checker()
        check.set_not_healthy("any","msg")
        healthy, descr = check.get_status()
        assert not healthy
        assert descr

    def test_should_report_healthy_if_component_was_not_healthy_but_recovered(self):
        check = Checker()
        check.set_not_healthy("any", "achoo")
        check.set_healthy("any")
        healthy, descr = check.get_status()
        assert healthy

class TestCheckerManyComponents:
    def test_should_report_healthy_if_all_components_are_healthy(self):
        check = Checker()
        for comp in ["A", "B", "C", "a", "bb", "c0"]:
            check.set_healthy(comp)
        healthy, descr = check.get_status()
        assert healthy

    def test_should_report_not_healthy_and_return_some_description_if_any_of_components_is_not_healthy(self):
        for sick in ["A", "B", "C", "a", "bb", "c0"]:
            check = Checker()
            for comp in ["A", "B", "C", "a", "bb", "c0"]:
                if comp == sick:
                    check.set_not_healthy(comp, "is sick")
                else:
                    check.set_healthy(comp)
        
            healthy, descr = check.get_status()
            assert not healthy
            assert descr
    
    def test_should_return_list_of_healthy_and_not_healthy_components_and_their_messages(self):
        check = Checker()
        for comp in ["A", "B", "C"]:
            check.set_healthy(comp, "I am ok!")
        check.set_not_healthy("C", "I am sick :(")
        
        healthy, descr = check.get_status()
        assert not healthy
        compare(json.loads(descr), {
            "healthy": {
                "A": "I am ok!",
                "B": "I am ok!"
            },
            "not healthy": {
                "C":"I am sick :("
            }
        })

class TestCheckers:
    def test_should_get_independent_results_from_two_checkers(self):
        check1 = Checker()
        check2 = Checker()
        check1.set_healthy('A')
        check2.set_not_healthy('A', 'sick')
        healthy1,descr1 = check1.get_status()
        healthy2,descr2 = check2.get_status()
        assert healthy1
        assert not healthy2
        compare(json.loads(descr1), {
            "healthy": {
                "A": ""
            },
            "not healthy": {}
        })
        compare(json.loads(descr2), {
            "healthy": {},
            "not healthy": {
                "A": "sick"
            }
        })

class TestHealthChecking:
    def test_should_return_same_instance_without_name(self):
        check1 = HealthChecking.getChecker()
        check2 = HealthChecking.getChecker()
        assert check1 == check2

    def test_should_return_same_instance_with_name(self):
        check1 = HealthChecking.getChecker('A')
        check2 = HealthChecking.getChecker('A')
        assert check1 == check2

    def test_should_return_different_instances(self):
        check1 = HealthChecking.getChecker()
        check2 = HealthChecking.getChecker('A')
        check3 = HealthChecking.getChecker('B')
        assert check1 != check2
        assert check1 != check3
        assert check2 != check3