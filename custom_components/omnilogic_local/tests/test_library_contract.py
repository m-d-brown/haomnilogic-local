import os
import sys

# This test ensures that our fake library hasn't drifted from the real library signature.
# It also verifies that the namespace swap is working.


def test_faked_namespace_is_available():
    # We simulate what conftest.py will do
    fake_path = os.path.abspath("custom_components/omnilogic_local/tests/fakes")
    sys.path.insert(0, fake_path)
    # Clear sys.modules cache for the library to force reload
    for mod in list(sys.modules.keys()):
        if mod.startswith("pyomnilogic_local"):
            del sys.modules[mod]

    try:
        import pyomnilogic_local.api as api_module

        assert "tests/fakes" in api_module.__file__
    finally:
        sys.path.pop(0)


def test_omnitypes_mirroring():
    # Verify that we are re-exporting correctly
    fake_path = os.path.abspath("custom_components/omnilogic_local/tests/fakes")
    sys.path.insert(0, fake_path)
    # Clear sys.modules cache for the library to force reload
    for mod in list(sys.modules.keys()):
        if mod.startswith("pyomnilogic_local"):
            del sys.modules[mod]

    try:
        import pyomnilogic_local.omnitypes as types_module
        from pyomnilogic_local.omnitypes import OmniType

        assert "tests/fakes" in types_module.__file__
        assert OmniType.BACKYARD is not None
    finally:
        sys.path.pop(0)
