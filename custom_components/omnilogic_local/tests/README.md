# OmniLogic Local Testing Architecture

This document describes the testing strategy and architecture for the `haomnilogic-local` integration.

## Testing Philosophy

We follow a tiered testing strategy to balance execution speed, reliability, and fidelity. Our primary goal is to isolate the Home Assistant integration from the underlying `pyomnilogic-local` library's complex XML and Pydantic parsing logic where possible.

### Tier 1: Model-Layer Mocking (Preferred)

- **Location**: `tests/test_light.py`, `tests/test_sensor.py`, etc.
- **Fixture**: `init_integration` (with `mock_omni_data`)
- **Key File**: [mock_models.py](file:///Users/mdbrown/important/others/haomnilogic-local/custom_components/omnilogic_local/tests/mock_models.py)
- **Concept**: Instead of providing raw XML fixtures, we provide fully-attributed MagicMock objects that look like the `pyomnilogic-local` models (`MSPConfig`, `Telemetry`, etc.).
- **Benefits**:
    - **Isolation**: Changes in the library's XML schema or Pydantic validation don't break integration tests.
    - **Control**: Easy to manipulate specific state values (e.g., `telemetry.brightness`) without hand-editing XML.
    - **Performance**: Skips the expensive XML parsing step during test setup.

### Tier 2: Component Integration (Legacy)

- **Purpose**: Verifies that Home Assistant correctly translates OmniLogic state into entities.
- **Mocking**: Patches the `OmniLogicAPI` at the library level.
- **Note**: Most tests are migrating to Tier 1.

### Tier 3: Protocol Integration (High Fidelity)

- **Location**: `tests/test_coordinator.py`
- **Fixture**: `omni_server`
- **Mocking**: A real UDP mock server (`MockOmniLogicServer` in `conftest.py`) that implements the Hayward XML/UDP protocol.
- **Purpose**: Verifies the end-to-end communication stack, including the `pyomnilogic-local` library's ability to handle fragmented UDP packets.

---

## Mocking Architecture

### mock_models.py
This module is the core of our modern testing strategy. It provides helper functions to create "well-behaved" mocks for any OmniLogic equipment:

- `create_mock_light()`
- `create_mock_sensor()`
- `create_mock_backyard()`
- etc.

These helpers ensure that:
1.  **Attributes are consistent**: All expected properties (like `system_id`, `name`, `omni_type`) are present.
2.  **JSON Safety**: All attributes return serializable primitives (integers, strings, enums) or "sanitized" mocks that won't crash Home Assistant's state restoration logic.
3.  **Discovery Compatibility**: The mocks correctly expose properties used by [utils.py](file:///Users/mdbrown/important/others/haomnilogic-local/custom_components/omnilogic_local/utils.py) for entity discovery.

### conftest.py
The `init_integration` fixture in `conftest.py` orchestrates the setup:
1.  It collects all entities from a `mock_omni_data` dictionary.
2.  It patches `MSPConfig.load_xml` and `Telemetry.load_xml` to return specific mock objects.
3.  It patches the `OmniLogicCoordinator` to use the `mock_omni_data` for its internal entity catalog.

---

## Adding a New Test

1.  **Define Equipment**: Add your equipment to the scenario in your test using `mock_models.py` helpers.
2.  **Initialize**: Call `init_integration` which will pick up your mocked equipment.
3.  **Assert**: Check `hass.states` for the expected entities and their attributes.

```python
async def test_my_new_sensor(hass, init_integration):
    # The scenarios are defined in conftest.py or specifically for your test
    state = hass.states.get("sensor.my_mock_sensor")
    assert state.state == "80.0"
```

## Maintenance

> [!IMPORTANT]
> **No more XML fixtures!**
> Do not add new XML files to `tests/fixtures/`. Always prefer adding model helpers to `mock_models.py`.

> [!WARNING]
> **JSON Serialization**
> If you add a new attribute to an entity's `extra_state_attributes`, ensure that the corresponding mock in `mock_models.py` is sanitized using the `sanitize_mock()` utility to avoid `TypeError` during state restoration.

---

## Running Tests

```bash
PYTHONPATH=. .venv/bin/pytest -vv
```
