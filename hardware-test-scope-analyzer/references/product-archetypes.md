# Product archetypes for smart-hardware test-scope generation

Use this file when there is no existing XMind, or when the provided XMind is too shallow to anchor the structure.

## Selection rule

1. Start with the **universal base skeleton**.
2. Add one or two domain archetypes that best match the product.
3. Remove unsupported branches instead of forcing every archetype into the final tree.
4. For hybrid products, prefer breadth at level 1 and specificity at level 2 or 3.

## Universal base skeleton

Recommended top-level order:
- product overview / version boundary
- feature modules
- local interaction
- pairing / network / connectivity
- app / cloud / account / permissions
- compatibility
- performance
- stability / recovery / observability
- ota / diagnostics / logs
- security / privacy
- scenario chains
- production test / embedded / manufacturing
- exploratory

Use this base when the product combines device, app, and cloud.

## Lighting device archetype

Add or expand these areas:
- light channels / output paths
- modes and scenes
- brightness / illuminance / color temperature / timing parameters
- defaults / memory / restore
- sensors such as ambient light, occupancy, posture, distance
- local controls: touch, rotary knob, remote control, physical keys
- app and voice interaction for mode switching
- special modes: sleep, focus, red light, classroom simulation, adaptive lighting
- thermal, power, long-run stability, and false-trigger recovery

## Voice or audio device archetype

Add or expand these areas:
- wake-up, asr, nlu, tts, dialogue management
- far-field, noise robustness, multi-speaker, interruption, false wake-up
- online vs offline behavior
- microphone / speaker / volume / playback routing
- voice control latency and fallback logic
- privacy controls, mute status, and permission state

## Screen-heavy interactive device archetype

Add or expand these areas:
- boot, animation, landing page, idle state
- gesture, click, long press, rotary, and page transitions
- stateful pages, refresh timing, placeholders, and stale data
- mode display rules, navigation depth, and conflict resolution
- performance: fps-like smoothness, input latency, cpu / memory hot paths

## Sensor or gateway archetype

Add or expand these areas:
- sensor calibration and drift
- false positives / false negatives
- heartbeat, retries, timeout, and reconnect
- multi-device orchestration, topology, role change, and fallback
- data freshness, event ordering, and eventual consistency

## Camera or vision device archetype

Add or expand these areas:
- preview / stream / storage / retrieval
- privacy covers, permission, encryption, account sharing
- network degradation, bitrate adaptation, reconnect, and clock sync
- event detection, false alarm, missed alarm, and retention rules

## Manufacturing-heavy product archetype

Add or expand these areas:
- factory mode, calibration, traceability, sn / mac / version readback
- production diagnostics, hardware self-test, and aging
- board-to-board communication and test-port access
- factory reset, provisioning, and shipment defaults

## Heuristic shortcuts

- Mostly physical behavior + parameters -> combine **lighting** with **screen-heavy** if a local display exists.
- Mostly speech-driven -> combine **voice or audio** with **screen-heavy** if the product also has a UI.
- Mostly data collection / routing -> combine **sensor or gateway** with the **universal base**.
- High manufacturing emphasis -> add **manufacturing-heavy** even if another archetype is primary.
