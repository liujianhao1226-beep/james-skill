# Smart hardware test-domain checklist

Use this checklist to expand smart hardware test scope in a reusable way. Not every product needs every branch. Include only branches that match the product architecture.

## 1. Core function and user journey

Check for:
- first-use flow
- normal daily-use flow
- feature modes or scene modes
- entry / exit / interruption / resume logic
- role-specific or permission-specific behavior

Common missing sub-branches:
- default values
- mode mutual exclusion
- restored previous state
- shortcut and alternate entry paths

## 2. Device control and hardware behavior

Check for:
- actuators or output channels: light, motor, fan, heating, speaker, display, lock, pump, valve, etc.
- sensors: light sensor, occupancy, temperature, humidity, microphone, camera, touch, knob, buttons
- control parameters: intensity, speed, angle, color, temperature, timing, thresholds
- calibration, debounce, mis-trigger, drift, and fault indication

Common missing sub-branches:
- per-channel control
- parameter ranges and step size
- local/manual control priority
- power-on defaults and restore behavior
- sensor noise and false positive / false negative cases

## 3. UI and human-machine interaction

Check for:
- boot and startup behavior
- onboarding and guidance
- touch, knob, key, gesture, indicator, display, voice feedback, sound prompts
- page transitions and state refresh
- disabled state, loading state, failure state, empty state

Common missing sub-branches:
- startup protection period
- interaction lock during upgrade or pairing
- stale UI after remote control
- local language / font / truncation issues

## 4. Connectivity and pairing

Check for:
- pairing / provisioning / binding
- wifi, bluetooth, zigbee, matter, thread, lan, hotspot, cellular, or accessory pairing
- credential changes, router changes, hidden SSID, signal weakness, reconnect
- local-only vs cloud-required behavior

Common missing sub-branches:
- timeout and retry flow
- wrong-password and duplicate-device handling
- network switching and recovery
- device reset and re-bind

## 5. App, account, and cloud interaction

Check for:
- device add/remove
- account binding and sharing
- family / member / role permission
- remote control, scene, automation, push, history, and data reporting
- multi-device or multi-home management

Common missing sub-branches:
- state sync delay
- conflict between device-side and app-side control
- stale cache after reconnect
- permission downgrade / revoke flow

## 6. Voice, audio, and ai capabilities

Use this branch only when applicable.

Check for:
- wake-up and recognition
- command understanding and confirmation
- offline vs online behavior
- interruption, barge-in, anti-noise, anti-false-trigger
- tts feedback and audio routing

Common missing sub-branches:
- relative adjustment commands
- ambiguous command handling
- weak network degradation
- wake-up rate, false wake-up rate, latency

## 7. Data, state sync, and cross-end consistency

Check for:
- device state vs app state vs cloud state
- report timing and refresh timing
- conflict handling for simultaneous control
- state persistence across reboot, re-login, reconnect, and upgrade

Common missing sub-branches:
- last-writer-wins ambiguity
- cross-end range mismatch
- stale state after reconnect
- scene / automation execution visibility

## 8. Compatibility

Check for:
- phone OS and app version
- router and network topology
- protocol version
- screen size, locale, region, time zone
- accessory compatibility and mixed firmware versions

Common missing sub-branches:
- hidden SSID and special-character SSID
- ipv4 / ipv6 differences
- old phone / tablet layout issues
- cross-version interoperability

## 9. Performance and resource behavior

Check for:
- startup time
- response latency
- pairing time
- sync delay
- CPU, memory, storage, bandwidth, battery, temperature, and power consumption
- burst commands and long-run load

Common missing sub-branches:
- first-response vs steady-state response
- device-side and cloud-side timing separation
- high-frequency control stress
- long-duration idle or weak-network soak

## 10. Stability, fault tolerance, and recovery

Check for:
- reboot recovery
- power loss recovery
- network interruption recovery
- process crash and watchdog behavior
- corrupted config and safe fallback

Common missing sub-branches:
- partial initialization failure
- repeated reconnect storm
- brownout / unstable power cases
- graceful degradation when dependencies fail

## 11. OTA, diagnostics, and manufacturing support

Check for:
- firmware upgrade and rollback
- version migration and config migration
- factory reset
- log collection, error reporting, health reporting
- production test / calibration / provisioning support

Common missing sub-branches:
- interrupted upgrade
- post-upgrade state migration
- version mismatch across device components
- manufacturing identifiers, mac/sn, and traceability

## 12. Scenario chains

Check for end-to-end flows instead of single functions only.

Common examples:
- first boot → pairing → onboarding → normal use
- local control → app control → cloud sync → scene trigger
- upgrade → reboot → state restore → report verification
- permission change → remote control → device reaction

## 13. Exploratory and abuse-oriented coverage

Check for:
- rapid repeated control
- mixed control from multiple ends
- impossible or contradictory sequences
- extreme boundary combinations
- unexpected unplug / relock / force quit / app backgrounding

## 14. Security, privacy, and compliance

Use this branch when applicable.

Check for:
- microphone / camera / sensor privacy controls
- account and token handling
- local network exposure
- data retention and deletion
- permission prompts and revocation

Common missing sub-branches:
- guest control boundaries
- hidden diagnostic endpoints
- insecure default exposure
- privacy-state UI mismatch

## Cross-cutting dimensions to add under important branches

When a branch is too generic, expand it using these dimensions:
- default values
- boundary values
- exception flow
- state sync
- persistence and restore
- mode priority / mutual exclusion
- permission and role differences
- offline / weak-network behavior
- reboot / reconnect / power-loss recovery
- logging and observability
