import pytest

from htrc.torchlite.ef.workset import WorkSet


@pytest.fixture
def workset():
    mini_workset = WorkSet('63f7ae452500006404fc54c7')
    return mini_workset


def test_volumes(workset):
    assert len(workset.volumes) == 4
