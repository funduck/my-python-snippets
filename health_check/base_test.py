from testfixtures import compare
import json
import pytest
from health_check.base import BaseHealthCheck


class TestBaseHealthCheck:
    def test_should_report_healthy_if_no_components(self):
        check = BaseHealthCheck()
        healthy, descr = check.get_status()
        assert healthy

    def test_should_set_healthy_without_msg(self):
        BaseHealthCheck().set_healthy("any")

    def test_should_set_healthy_with_msg(self):
        BaseHealthCheck().set_healthy("any", "msg")

    def test_should_fail_set_not_healthy_without_msg(self):
        with pytest.raises(Exception):
            BaseHealthCheck().set_not_healthy("any")

    def test_should_set_not_healthy_with_msg(self):
        BaseHealthCheck().set_not_healthy("any", "msg")

class TestBaseHealthCheckOneComponent:
    def test_should_report_healthy_if_component_is_healthy(self):
        check = BaseHealthCheck()
        check.set_healthy("any")
        healthy, descr = check.get_status()
        assert healthy

    def test_should_report_not_healthy_and_return_some_description_if_component_not_healthy(self):
        check = BaseHealthCheck()
        check.set_not_healthy("any","msg")
        healthy, descr = check.get_status()
        assert not healthy
        assert descr

    def test_should_report_healthy_if_component_was_not_healthy_but_recovered(self):
        check = BaseHealthCheck()
        check.set_not_healthy("any", "achoo")
        check.set_healthy("any")
        healthy, descr = check.get_status()
        assert healthy

class TestBaseHealthCheckManyComponents:
    def test_should_report_healthy_if_all_components_are_healthy(self):
        check = BaseHealthCheck()
        for comp in ["A", "B", "C", "a", "bb", "c0"]:
            check.set_healthy(comp)
        healthy, descr = check.get_status()
        assert healthy

    def test_should_report_not_healthy_and_return_some_description_if_any_of_components_is_not_healthy(self):
        for sick in ["A", "B", "C", "a", "bb", "c0"]:
            check = BaseHealthCheck()
            for comp in ["A", "B", "C", "a", "bb", "c0"]:
                if comp == sick:
                    check.set_not_healthy(comp, "is sick")
                else:
                    check.set_healthy(comp)
        
            healthy, descr = check.get_status()
            assert not healthy
            assert descr
    
    def test_should_return_list_of_healthy_and_not_healthy_components_and_their_messages(self):
        check = BaseHealthCheck()
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
