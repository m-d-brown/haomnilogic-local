# OmniLogic Local Testing Architecture

This document describes the testing strategy and architecture for the `haomnilogic-local` integration.

## Testing Philosophy

We follow a tiered testing strategy to balance execution speed, reliability, and fidelity.

### Tier 1: Unit Tests
- **Location**: `tests/models/` (Future)
- **Scope**: Testing individual data models and constants within the integration.
- **Mocking**: No external dependencies or Home Assistant core needed.

### Tier 2: Component Integration (Standard)
- **Location**: `tests/test_sensor.py`, `tests/test_switch.py`, etc.
- **Fixture**: `init_integration`
- **Mocking**: Patches the `OmniLogicAPI` at the library level using `unittest.mock.AsyncMock`.
- **Purpose**: Verifies that Home Assistant correctly translates OmniLogic state into entities and that services (like `turn_on`) call the correct library methods.

### Tier 3: Protocol Integration (High Fidelity)
- **Location**: `tests/test_coordinator.py`
- **Fixture**: `omni_server`
- **Mocking**: A real UDP mock server (`MockOmniLogicServer` in `conftest.py`) that implements the Hayward XML/UDP protocol.
- **Purpose**: Verifies the end-to-end communication stack, including the `pyomnilogic-local` library's ability to parse fragmented UDP packets and XML responses.

---

## Fixture Management

### Static Fixtures
Located in `tests/fixtures/`, these are XML files captured from real OmniLogic controllers. They provide high-fidelity "snapshots" of complex real-world systems.
- Example: `issue-144-mspconfig.xml`

### Programmatic Fixtures (The Generator)
For targeted testing of specific equipment combinations, we use the `OmniLogicFixtureGenerator` (found in `tests/generator.py`).

**Example Usage**:
```python
from .generator import OmniLogicFixtureGenerator

def test_custom_scenario(hass):
    gen = OmniLogicFixtureGenerator()
    gen.add_pool("My Pool")
    gen.add_filter_pump("Main Pump")
    
    msp_xml = gen.dump_msp_config()
    telemetry_xml = gen.dump_telemetry()
    # Use these XMLs with the init_integration fixture
```

---

## Running Tests

Ensure you have the environment set up with Poetry:

```bash
# Run all tests
PYTHONPATH=. .venv/bin/pytest

# Run with coverage
PYTHONPATH=. .venv/bin/pytest --cov=custom_components.omnilogic_local
```

## Best Practices
1. **Prefer `init_integration`**: Use the patched API fixture for platform tests unless you are specifically testing UDP communication.
2. **Use the Generator**: For new tests, use the generator to create the minimum viable XML configuration. Only add static fixtures for complex reported bugs.
3. **Verify Service Calls**: Always verify that service calls result in a call to the underlying `omni_api` with the expected parameters.
