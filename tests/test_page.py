import pytest
from htrc.torchlite.ef.volume import Volume
from htrc.torchlite.ef.page import Page


@pytest.fixture
def volume():
    v = Volume("uc1.32106011187561")
    return v


def test_tokens(volume):
    page = volume.pages[10]
    assert page.tokens['und'] == 4
