## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | lift → approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.3585 | 0.20 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3645 | 0.13 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2398 | 0.16 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3479 | 0.13 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3633 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.4761612134249316, -0.02015088565858767, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.4761612134249316, -0.02015088565858767, 0.03]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.359) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  weight: 0.3
- id: place_goal
  metric: goal_progress
  weight: 0.5
phases:
- id: raise_tcp
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    raise_height:
      type: scalar
      range:
      - 0.2
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset.z
        mode: replace
    raise_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    descend_force_thresh:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: grasp_contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_contact
- id: grasp_action
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.025
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - -0.02
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    place_force_thresh:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **raise_tcp** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - raise_height: status=consumed; consumers=target.offset.z (replace)
    - raise_speed: status=consumed; consumers=generator.speed (replace)
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - descend_force_thresh: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=grasp_contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **grasp_action** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.025
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.02], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_force_thresh: status=consumed; consumers=termination.force_threshold (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.359
- **task_score** (E): 0.198
- **fitness_score**: 0.171  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| raise_tcp | 1.00 | 1.00 | 0.2907 |
| approach_object | 0.00 | 1.00 | 0.3854 |
| descend_grasp | 1.00 | 1.00 | 0.0001 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.0331 |
| transport_to_goal | 0.33 | 1.00 | 0.2982 |
| descend_place | 1.00 | 1.00 | 0.0026 |
| release_object | 1.00 | 1.00 | 0.0290 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| raise_tcp | lift | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.501, -0.000, 0.592) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| approach_object | approach | 0.00 / step_budget | (0.501, -0.000, 0.592)→(0.431, -0.009, 0.214) | (0.493, -0.015, 0.026)→(0.492, -0.015, 0.020) | 0.281→0.286 | 1.00 / 4.667 | 343.460 | 1339.701 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.431, -0.009, 0.214)→(0.431, -0.009, 0.214) | (0.492, -0.015, 0.020)→(0.492, -0.015, 0.020) | 0.286→0.286 | 1.00 / 4.667 | 475.399 | 112.662 |
| grasp_action | grasp | 1.00 / step_budget | (0.430, -0.009, 0.213)→(0.430, -0.009, 0.213) | (0.492, -0.015, 0.020)→(0.482, -0.015, 0.025) | 0.286→0.287 | 1.00 / 8.000 | 3302.344 | 91.044 |
| lift_object | lift | 0.67 / step_budget | (0.486, -0.046, 0.244)→(0.494, -0.040, 0.240) | (0.481, -0.015, 0.025)→(0.492, -0.015, 0.023) | 0.287→0.284 | 1.00 / 9.000 | 561.401 | 716.467 |
| transport_to_goal | approach | 0.33 / step_budget | (0.494, -0.040, 0.240)→(0.515, 0.223, 0.222) | (0.492, -0.015, 0.023)→(0.512, 0.025, 0.019) | 0.284→0.247 | 1.00 / 9.000 | 91031.677 | 742.825 |
| descend_place | descend | 1.00 / force_exceeded | (0.515, 0.223, 0.222)→(0.516, 0.225, 0.222) | (0.512, 0.025, 0.019)→(0.512, 0.025, 0.019) | 0.247→0.247 | 1.00 / 8.667 | 94282.683 | 34.499 |
| release_object | release | 1.00 / step_budget | (0.516, 0.225, 0.222)→(0.513, 0.239, 0.243) | (0.512, 0.025, 0.019)→(0.512, 0.025, 0.019) | 0.247→0.247 | 1.00 / 4.333 | 26.250 | 26.970 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.258
- phase_score: 0.336
- phase_breakdown.grasp_contact_score: 0.101
- phase_breakdown.approach_object_score: 0.703
- phase_breakdown.place_goal_score: 0.332
- grasp_place_fitness: 0.244

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.244
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.258
- **Median Q (composite search score)**: -0.381
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.293


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63142,0.15919,0.19002]},{"name":"goal","value":[0.47616,-0.02015,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.07207,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.17663,"approach_object.approach_speed":0.34551,"descend_grasp.descend_force_thresh":10.91045,"descend_place.place_force_thresh":5.01175,"lift_object.lift_height":0.20718,"lift_object.lift_speed":0.11991,"raise_tcp.raise_height":0.32776,"raise_tcp.raise_speed":0.22511,"release_object.release_duration":1.30686,"transport_to_goal.transport_arc_height":0.08614,"transport_to_goal.transport_speed":0.27046,"transport_to_goal.transport_z":0.11132},"optimized_scores":{"best_composite_score":-0.40919,"best_fitness_score":0.12081,"best_task_score":0.14212},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.57984,-0.00318,-0.00233],"force_p95":704.14866,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1604.8281,"mean_force":380.33671,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41899,-0.00814,0.20865]},{"body_a":"world","body_b":"link6","contact_count":760.0,"contact_point_centroid":[0.59016,0.02168,-0.00012],"force_p95":617.43085,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1185.60549,"mean_force":252.01409,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.40415,0.02161,0.20157]},{"body_a":"world","body_b":"link6","contact_count":455.0,"contact_point_centroid":[0.57252,-0.019,-0.00015],"force_p95":791.15799,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.36644,"mean_force":611.52982,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.42703,-0.01634,0.24036]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.51253,-0.00309,-0.00033],"force_p95":211.05448,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.05448,"mean_force":211.05448,"phase_index":2.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39849,-0.01196,0.26262]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.51392,-0.00305,-0.00016],"force_p95":125.02664,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.0568,"mean_force":89.3406,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39789,-0.01189,0.26209]},{"body_a":"grasp_target","body_b":"link6","contact_count":262.0,"contact_point_centroid":[0.48442,-0.0165,0.04578],"force_p95":1.25746,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.00152,"mean_force":0.78768,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39357,-0.01055,0.2807]},{"body_a":"grasp_target","body_b":"link7","contact_count":223.0,"contact_point_centroid":[0.48418,-0.01547,0.05369],"force_p95":0.23742,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.8325,"mean_force":0.18531,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.36919,-0.01127,0.1664]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47591,-0.02027,-0.00274],"force_p95":0.4469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5845,"mean_force":0.1739,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42982,-0.00586,0.28269]},{"body_a":"grasp_target","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.46771,-0.01862,0.05034],"force_p95":0.58259,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58259,"mean_force":0.58259,"phase_index":2.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39849,-0.01196,0.26262]},{"body_a":"grasp_target","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.46923,-0.0193,0.04015],"force_p95":0.44664,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51991,"mean_force":0.19145,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39789,-0.01189,0.26209]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47525,-0.02095,-0.00478],"force_p95":0.50115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5062,"mean_force":0.27498,"phase_index":2.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39849,-0.01196,0.26262]},{"body_a":"world","body_b":"grasp_target","contact_count":3908.0,"contact_point_centroid":[0.46856,-0.02022,-0.00216],"force_p95":0.21468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5028,"mean_force":0.13438,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.41285,0.04263,0.19686]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.45672,-0.02118,-0.00526],"force_p95":0.45782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48719,"mean_force":0.31813,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.3979,-0.0119,0.26211]},{"body_a":"world","body_b":"grasp_target","contact_count":1621.0,"contact_point_centroid":[0.46725,-0.02106,-0.00229],"force_p95":0.24012,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30208,"mean_force":0.14024,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4306,-0.01689,0.23737]},{"body_a":"world","body_b":"grasp_target","contact_count":3280.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"raise_tcp","phase_type":"lift","tcp_position_centroid":[0.49959,-4e-05,0.45312]},{"body_a":"grasp_target","body_b":"link6","contact_count":114.0,"contact_point_centroid":[0.47286,-0.01845,0.05601],"force_p95":0.10602,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13784,"mean_force":0.06695,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40707,-0.01322,0.25785]}],"total_contact_groups":24},"final_pose_error":0.31086,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.46869,-0.02047,0.02602],"final_tcp_position":[0.47278,0.41572,0.09481],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273015.69014,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":821.0,"n_steps_budget":930.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"raise_tcp","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3280.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50151,-7e-05,0.60875],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.58363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46517,-0.02053,0.01869],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":512.60391,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4372.0,"raw_peak_contact_force":1604.8281,"subtask_id":"approach_object","tcp_end":[0.39849,-0.01196,0.26262],"tcp_start":[0.50151,-7e-05,0.60875],"tcp_to_object_dist_end":0.25302,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46512,-0.02053,0.01873],"object_pos_start":[0.46517,-0.02053,0.01869],"object_to_goal_dist_end":0.29882,"object_to_goal_dist_start":0.29882,"object_z_max":0.01869,"peak_contact_force":544.8545,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":211.05448,"subtask_id":"grasp_contact","tcp_end":[0.39849,-0.01195,0.26259],"tcp_start":[0.39849,-0.01196,0.26262],"tcp_to_object_dist_end":0.25294,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45414,-0.02066,0.02667],"object_pos_start":[0.46512,-0.02053,0.01873],"object_to_goal_dist_end":0.30076,"object_to_goal_dist_start":0.29882,"object_z_max":0.02697,"peak_contact_force":83.34222,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3041.0,"raw_peak_contact_force":146.0568,"tcp_end":[0.3979,-0.01189,0.26204],"tcp_start":[0.39789,-0.01189,0.26204],"tcp_to_object_dist_end":0.24216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.46992,-0.02099,0.02602],"object_pos_start":[0.45312,-0.02072,0.02697],"object_to_goal_dist_end":0.2923,"object_to_goal_dist_start":0.30124,"object_z_max":0.02764,"peak_contact_force":317.23802,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4182.0,"raw_peak_contact_force":911.36644,"tcp_end":[0.45482,-0.02049,0.20876],"tcp_start":[0.4337,-0.0177,0.23742],"tcp_to_object_dist_end":0.18337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46869,-0.02047,0.02602],"object_pos_start":[0.46996,-0.021,0.02602],"object_to_goal_dist_end":0.29266,"object_to_goal_dist_start":0.29229,"object_z_max":0.02613,"peak_contact_force":273015.69014,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9184.0,"raw_peak_contact_force":1185.60549,"subtask_id":"place_goal","tcp_end":[0.47214,0.41067,0.09276],"tcp_start":[0.45482,-0.02049,0.20876],"tcp_to_object_dist_end":0.43628,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46869,-0.02047,0.02602],"object_pos_start":[0.46869,-0.02047,0.02602],"object_to_goal_dist_end":0.29266,"object_to_goal_dist_start":0.29266,"object_z_max":0.02602,"peak_contact_force":9748.82241,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47278,0.41572,0.09481],"tcp_start":[0.47214,0.41067,0.09276],"tcp_to_object_dist_end":0.4416,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46869,-0.02047,0.02602],"object_pos_start":[0.46869,-0.02047,0.02602],"object_to_goal_dist_end":0.29266,"object_to_goal_dist_start":0.29266,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.46558,0.45748,0.12348],"tcp_start":[0.47278,0.41572,0.09481],"tcp_to_object_dist_end":0.48779,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63013,0.20822,0.11412]},{"name":"goal","value":[0.45856,-0.02632,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.49587,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.26185,"approach_object.approach_speed":0.23907,"descend_grasp.descend_force_thresh":5.94447,"descend_place.place_force_thresh":10.34093,"lift_object.lift_height":0.22468,"lift_object.lift_speed":0.09455,"raise_tcp.raise_height":0.34533,"raise_tcp.raise_speed":0.20319,"release_object.release_duration":1.56896,"transport_to_goal.transport_arc_height":0.18603,"transport_to_goal.transport_speed":0.16546,"transport_to_goal.transport_z":0.18807},"optimized_scores":{"best_composite_score":-0.28587,"best_fitness_score":0.24413,"best_task_score":0.2584},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":29.0,"contact_point_centroid":[0.69534,0.00307,-0.00717],"force_p95":1292.10958,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1624.42771,"mean_force":324.56979,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44934,0.00139,0.10421]},{"body_a":"link5","body_b":"hand","contact_count":696.0,"contact_point_centroid":[0.55822,0.04542,0.22701],"force_p95":158.43017,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":501.79286,"mean_force":90.03104,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43437,0.07434,0.21118]},{"body_a":"world","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47488,-0.04779,-0.00019],"force_p95":327.7606,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.6882,"mean_force":292.5454,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43383,0.03565,0.12803]},{"body_a":"link5","body_b":"hand","contact_count":404.0,"contact_point_centroid":[0.54151,-0.01953,0.16974],"force_p95":141.81699,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.52328,"mean_force":99.58616,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49468,-0.10584,0.23334]},{"body_a":"world","body_b":"link6","contact_count":114.0,"contact_point_centroid":[0.56543,-0.16167,-0.00036],"force_p95":259.32649,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.74941,"mean_force":169.126,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43438,0.03333,0.1383]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.56554,0.10783,0.23715],"force_p95":103.25194,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.25194,"mean_force":103.25194,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43608,0.1196,0.21296]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.56392,0.10854,0.23725],"force_p95":78.48589,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.66484,"mean_force":63.24542,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43421,0.1201,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":3620.0,"contact_point_centroid":[0.53059,0.03068,-0.00257],"force_p95":0.58359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.10494,"mean_force":0.18869,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43935,0.05917,0.20613]},{"body_a":"grasp_target","body_b":"hand","contact_count":147.0,"contact_point_centroid":[0.47401,-0.01135,0.03737],"force_p95":1.75733,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.95394,"mean_force":1.07034,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43589,0.03123,0.13896]},{"body_a":"grasp_target","body_b":"link7","contact_count":110.0,"contact_point_centroid":[0.49759,-0.02099,0.02004],"force_p95":1.43256,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.54369,"mean_force":0.88906,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43289,0.0349,0.13629]},{"body_a":"world","body_b":"grasp_target","contact_count":3520.0,"contact_point_centroid":[0.45856,-0.02632,-0.00196],"force_p95":0.12599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"raise_tcp","phase_type":"lift","tcp_position_centroid":[0.49967,-4e-05,0.46177]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.46579,-0.00326,0.18918]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45801,-0.01609,0.14435]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45757,-0.01621,0.14237]},{"body_a":"world","body_b":"grasp_target","contact_count":4804.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49039,-0.08713,0.23761]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.55438,0.04746,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43608,0.1196,0.21296]}],"total_contact_groups":22},"final_pose_error":0.24411,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.55438,0.04746,0.01602],"final_tcp_position":[0.43607,0.11974,0.21289],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9749.19034,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"raise_tcp","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3520.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50198,-7e-05,0.62657],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.60269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4029.0,"raw_peak_contact_force":1624.42771,"subtask_id":"approach_object","tcp_end":[0.45801,-0.01609,0.14435],"tcp_start":[0.50198,-7e-05,0.62657],"tcp_to_object_dist_end":0.11877,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":491.6074,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.45807,-0.01613,0.14441],"tcp_start":[0.45801,-0.01609,0.14435],"tcp_to_object_dist_end":0.11883,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":9749.19034,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2975.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45753,-0.01622,0.14215],"tcp_start":[0.45753,-0.01622,0.14215],"tcp_to_object_dist_end":0.11657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1201.0,"n_steps_budget":750.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10382.0,"raw_peak_contact_force":274.52328,"tcp_end":[0.49522,-0.0849,0.27661],"tcp_start":[0.51032,-0.11786,0.26148],"tcp_to_object_dist_end":0.25994,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55438,0.04746,0.01602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.20298,"object_to_goal_dist_start":0.30365,"object_z_max":0.03287,"peak_contact_force":79.21883,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8898.0,"raw_peak_contact_force":501.79286,"subtask_id":"place_goal","tcp_end":[0.43608,0.1196,0.21296],"tcp_start":[0.49522,-0.0849,0.27661],"tcp_to_object_dist_end":0.24081,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55438,0.04746,0.01602],"object_pos_start":[0.55438,0.04746,0.01602],"object_to_goal_dist_end":0.20298,"object_to_goal_dist_start":0.20298,"object_z_max":0.01602,"peak_contact_force":62.09897,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":103.25194,"tcp_end":[0.43607,0.11974,0.21289],"tcp_start":[0.43608,0.1196,0.21296],"tcp_to_object_dist_end":0.24079,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55438,0.04746,0.01602],"object_pos_start":[0.55438,0.04746,0.01602],"object_to_goal_dist_end":0.20298,"object_to_goal_dist_start":0.20298,"object_z_max":0.01602,"peak_contact_force":78.50486,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1216.0,"raw_peak_contact_force":80.66484,"tcp_end":[0.43337,0.12049,0.22827],"tcp_start":[0.43607,0.11974,0.21289],"tcp_to_object_dist_end":0.25501,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.64762,0.15808,0.1911]},{"name":"goal","value":[0.54431,0.00113,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.00935,"average_mean_iterations":7.97196,"average_solve_count":107.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.24185,"approach_object.approach_speed":0.25127,"descend_grasp.descend_force_thresh":8.09438,"descend_place.place_force_thresh":9.29962,"lift_object.lift_height":0.21185,"lift_object.lift_speed":0.13123,"raise_tcp.raise_height":0.2596,"raise_tcp.raise_speed":0.25328,"release_object.release_duration":1.10259,"transport_to_goal.transport_arc_height":0.11863,"transport_to_goal.transport_speed":0.33648,"transport_to_goal.transport_z":0.15524},"optimized_scores":{"best_composite_score":-0.38054,"best_fitness_score":0.14946,"best_task_score":0.19452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":417.0,"contact_point_centroid":[0.65042,-0.03297,-0.00017],"force_p95":718.86704,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":963.51072,"mean_force":404.98485,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48407,0.00012,0.2149]},{"body_a":"world","body_b":"link6","contact_count":204.0,"contact_point_centroid":[0.56736,-0.00748,-0.00036],"force_p95":721.88619,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":789.84657,"mean_force":454.84718,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42416,0.00059,0.24229]},{"body_a":"link5","body_b":"hand","contact_count":210.0,"contact_point_centroid":[0.52292,-0.08578,0.18647],"force_p95":660.83572,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":745.80606,"mean_force":377.23942,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52053,-0.00816,0.23149]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.63448,-0.1025,-0.00017],"force_p95":538.05246,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.07774,"mean_force":402.2168,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53474,-0.02207,0.24214]},{"body_a":"link5","body_b":"hand","contact_count":95.0,"contact_point_centroid":[0.48361,-0.10768,0.2042],"force_p95":270.72441,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.26409,"mean_force":231.17157,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52235,-0.04849,0.27175]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.59114,-0.00858,-0.00014],"force_p95":79.41911,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.95117,"mean_force":75.64701,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.435,0.00049,0.23456]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58947,-0.0084,-0.00016],"force_p95":126.80975,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.80975,"mean_force":126.80975,"phase_index":2.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.43536,0.00057,0.23585]},{"body_a":"grasp_target","body_b":"link6","contact_count":575.0,"contact_point_centroid":[0.55293,-0.0002,0.03428],"force_p95":1.54432,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.4356,"mean_force":0.86215,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41428,0.00047,0.26207]},{"body_a":"grasp_target","body_b":"link6","contact_count":136.0,"contact_point_centroid":[0.5458,-0.00458,0.03797],"force_p95":1.162,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.76776,"mean_force":0.67236,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51548,-0.04694,0.30434]},{"body_a":"grasp_target","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.55197,-0.00147,0.04979],"force_p95":0.59256,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.1575,"mean_force":0.27111,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44421,0.00053,0.22523]},{"body_a":"world","body_b":"grasp_target","contact_count":3539.0,"contact_point_centroid":[0.5428,0.00111,-0.00416],"force_p95":0.72403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09181,"mean_force":0.27459,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41402,0.00036,0.29995]},{"body_a":"world","body_b":"grasp_target","contact_count":1931.0,"contact_point_centroid":[0.51819,0.03505,-0.00272],"force_p95":0.64729,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81089,"mean_force":0.18458,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56487,0.02692,0.35381]},{"body_a":"grasp_target","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55827,-0.00614,0.03491],"force_p95":0.78742,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.78742,"mean_force":0.78742,"phase_index":2.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.43536,0.00057,0.23585]},{"body_a":"grasp_target","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.55307,0.00244,0.038],"force_p95":0.7206,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.77827,"mean_force":0.52756,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.435,0.00049,0.23456]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.53214,0.00279,-0.00764],"force_p95":0.61193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64057,"mean_force":0.48612,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.435,0.00049,0.23456]},{"body_a":"world","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.54283,0.00183,-0.01021],"force_p95":0.62737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63149,"mean_force":0.59033,"phase_index":2.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.43536,0.00057,0.23585]}],"total_contact_groups":25},"final_pose_error":0.18798,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.51415,0.04926,0.01602],"final_tcp_position":[0.63787,0.14084,0.35803],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273037.1284,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":590.0,"n_steps_budget":660.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"raise_tcp","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2356.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50052,-5e-05,0.53947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.51531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.552,0.00059,0.01442],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25527,"object_to_goal_dist_start":0.25012,"object_z_max":0.02929,"peak_contact_force":517.65463,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4318.0,"raw_peak_contact_force":789.84657,"subtask_id":"approach_object","tcp_end":[0.43536,0.00057,0.23585],"tcp_start":[0.50052,-5e-05,0.53947],"tcp_to_object_dist_end":0.25028,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.552,0.00059,0.01447],"object_pos_start":[0.552,0.00059,0.01442],"object_to_goal_dist_end":0.25524,"object_to_goal_dist_start":0.25527,"object_z_max":0.01442,"peak_contact_force":389.73625,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":126.80975,"subtask_id":"grasp_contact","tcp_end":[0.43532,0.00057,0.2357],"tcp_start":[0.43536,0.00057,0.23585],"tcp_to_object_dist_end":0.25012,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.53435,0.00198,0.02159],"object_pos_start":[0.552,0.00059,0.01447],"object_to_goal_dist_end":0.25678,"object_to_goal_dist_start":0.25524,"object_z_max":0.02219,"peak_contact_force":74.4983,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2961.0,"raw_peak_contact_force":126.95117,"tcp_end":[0.43502,0.00045,0.2345],"tcp_start":[0.43502,0.00046,0.2345],"tcp_to_object_dist_end":0.23494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":497.0,"n_steps_budget":600.0,"object_pos_end":[0.54696,0.00166,0.01602],"object_pos_start":[0.53178,0.00233,0.02218],"object_to_goal_dist_end":0.25546,"object_to_goal_dist_start":0.25732,"object_z_max":0.02218,"peak_contact_force":1366.84211,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4698.0,"raw_peak_contact_force":963.51072,"tcp_end":[0.53326,-0.01574,0.23442],"tcp_start":[0.51251,-0.0029,0.23348],"tcp_to_object_dist_end":0.21952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.51415,0.04926,0.01602],"object_pos_start":[0.54696,0.00166,0.01602],"object_to_goal_dist_end":0.24559,"object_to_goal_dist_start":0.25546,"object_z_max":0.02547,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4635.0,"raw_peak_contact_force":541.07774,"subtask_id":"place_goal","tcp_end":[0.63794,0.13984,0.36006],"tcp_start":[0.53326,-0.01574,0.23442],"tcp_to_object_dist_end":0.37668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.51415,0.04926,0.01602],"object_pos_start":[0.51415,0.04926,0.01602],"object_to_goal_dist_end":0.24559,"object_to_goal_dist_start":0.24559,"object_z_max":0.01602,"peak_contact_force":273037.1284,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63787,0.14084,0.35803],"tcp_start":[0.63794,0.13984,0.36006],"tcp_to_object_dist_end":0.37506,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51415,0.04926,0.01602],"object_pos_start":[0.51415,0.04926,0.01602],"object_to_goal_dist_end":0.24559,"object_to_goal_dist_start":0.24559,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63887,0.14015,0.3781],"tcp_start":[0.63787,0.14084,0.35803],"tcp_to_object_dist_end":0.39359,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```