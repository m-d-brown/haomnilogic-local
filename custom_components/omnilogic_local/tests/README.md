# OmniLogic Local High-Fidelity Test Infrastructure

This document describes the modern testing strategy for the `haomnilogic-local` integration. We have moved away from brittle XML fixtures and `MagicMock` patching in favor of a **Shadow Library** architecture.

## The Shadow Library Concept

Our testing standard is based on a high-fidelity "Test Double" of the `pyomnilogic-local` library. This fake library lives within the repository at `custom_components/omnilogic_local/tests/fakes/pyomnilogic_local/`.

### How it Works

1.  **Namespace Injection**: In `conftest.py`, we prepend the `fakes/` directory to `sys.path`. This ensures that any `import pyomnilogic_local` in the integration or test suite resolves to our local fake instead of the installed library.
2.  **Model Parity**: Our fake models (`MSPConfig`, `Telemetry`, etc.) mirror the production library's API and data structures exactly, using Pydantic for validation.
3.  **Stateful Fake API**: The `FakeOmniLogicAPI` maintains an internal state dictionary. When the integration calls a service (e.g., `async_set_heater`), the fake API updates its internal state. Tests then assert against this state directly.

## Architecture

### 1. High-Fidelity Models
Located in `tests/fakes/pyomnilogic_local/models/`. These models define exactly how complex equipment like filters, heaters, and chlorinators are represented.

### 2. Fake API
The `OmniLogicAPI` class in `tests/fakes/pyomnilogic_local/api.py` handles all "network" calls. It is completely isolated from real UDP traffic, making tests fast and deterministic.

### 3. Mock Models Factory
[mock_models.py](file:///Users/mdbrown/important/others/haomnilogic-local/custom_components/omnilogic_local/tests/mock_models.py) provides a set of helper functions (`create_mock_filter`, `create_mock_light`, etc.) to easily build complex system scenarios for your tests.

### 4. Integration Fixture
The `init_integration` fixture in `conftest.py` orchestrates the setup of the entire Home Assistant environment, ensuring all entities are discovered and initialized using the shadow library data.

## Why This is Better

-   **Robustness**: Tests are no longer broken by upstream library changes in XML parsing or internal logic.
-   **Parity**: We test against the same object types (`MSPConfig`, `Telemetry`) used in production, ensuring contract fidelity.
-   **Observability**: You can inspect `mock_api.state` to verify exactly what parameters were sent to the "system" during a service call.
-   **Speed**: No XML parsing, no UDP network stack, no complicated `MagicMock` setups.

## Adding a New Test

1.  **Scene Setup**: Use `mock_models.py` helpers to define your equipment in a test.
2.  **Discovery Verification**: Check `hass.states` to ensure your entity was created with the correct unique ID and attributes.
3.  **Service Verification**: Call a Home Assistant service and assert that the `mock_api.state` was updated correctly.

```python
async def test_heater_set_temp(hass, init_integration):
    # Verify entity exists
    state = hass.states.get("water_heater.pool_heater")
    assert state.state == "on"

    # Call service
    await hass.services.async_call(WATER_HEATER_DOMAIN, ...)

    # Verify state in Fake API
    coordinator = hass.data[DOMAIN][...][KEY_COORDINATOR]
    assert coordinator.omni_api.state["set_point_7"] == 86
```

## Maintenance

### Synchronizing with the Library
When the production `pyomnilogic-local` library is updated (e.g., new attributes or equipment types), you **MUST** update the shadow library models in `fakes/` to maintain parity.

### Contract Verification
Use `test_library_contract.py` to verify that our shadow library's API matches the expectation of the integration.

## Running Tests

```bash
PYTHONPATH=. .venv/bin/pytest -vv
```
