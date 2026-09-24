## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17  | -0.0764 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | -0.1713 | 0.18 | ❌ rejected |
| 5 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1730 | 0.17 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1694 | 0.19 | ✅ accepted |
| 3 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.3721 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=-0.372) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.2
- id: lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place
  weight: 0.3
phases:
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_grasp
- id: descend_to_grasp
  type: descend
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
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp
- id: grasp_action
  type: grasp
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_max_width:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: guards.check_grasp.threshold
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.04
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    lift_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: lift
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    transport_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place
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
    release_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_action** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_max_width: status=consumed; consumers=guards.check_grasp.threshold (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.04
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.372
- **task_score** (E): 0.314
- **fitness_score**: 0.628  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.0863 |
| descend_to_grasp | 1.00 | 1.00 | 0.1691 |
| grasp_action | 1.00 | 1.00 | 0.0118 |
| lift_object | 0.00 | 1.00 | 0.0986 |
| transport_to_goal | 0.33 | 0.33 | 0.1758 |
| release_object | 1.00 | 1.00 | 0.0231 |
| retract_after_place | 0.33 | 1.00 | 0.0577 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.501, 0.006, 0.216) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.130 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.501, 0.006, 0.216)→(0.493, 0.001, 0.048) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.129 |
| grasp_action | grasp | 1.00 / step_budget | (0.493, 0.001, 0.048)→(0.485, 0.001, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.025) | 0.265→0.266 | 1.00 / 43.333 | 0.160 | 0.232 |
| lift_object | lift | 0.00 / step_budget | (0.485, 0.001, 0.040)→(0.492, 0.001, 0.138) | (0.497, 0.001, 0.025)→(0.508, 0.001, 0.123) | 0.266→0.216 | 1.00 / 33.667 | 80.304 | 0.517 |
| transport_to_goal | approach | 0.33 / step_budget | (0.492, 0.001, 0.138)→(0.565, 0.143, 0.194) | (0.508, 0.001, 0.123)→(0.591, 0.147, 0.136) | 0.216→0.074 | 0.33 / 7.667 | 0.039 | 0.235 |
| release_object | release | 1.00 / step_budget | (0.565, 0.143, 0.194)→(0.560, 0.143, 0.217) | (0.591, 0.147, 0.136)→(0.604, 0.174, 0.013) | 0.074→0.179 | 1.00 / 4.000 | 0.141 | 1.861 |
| retract_after_place | retract | 0.33 / step_budget | (0.560, 0.143, 0.217)→(0.573, 0.167, 0.267) | (0.604, 0.174, 0.013)→(0.605, 0.173, 0.016) | 0.179→0.177 | 1.00 / 4.000 | 0.125 | 0.137 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.391
- phase_score: 0.504
- phase_breakdown.lift_score: 0.127
- phase_breakdown.place_score: 0.352
- phase_breakdown.pre_grasp_score: 0.762
- phase_breakdown.grasp_score: 0.722
- grasp_place_fitness: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.391
- **Median Q (composite search score)**: -0.372
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.grasp_offset_z
- **Final σ (mean)**: 0.330


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79775,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14223,"approach_object.approach_speed":0.12729,"approach_object.approach_tolerance":0.09123,"descend_to_grasp.descend_speed":0.11617,"descend_to_grasp.descend_tolerance":0.01381,"descend_to_grasp.grasp_offset_z":0.01,"grasp_action.grasp_max_width":0.05516,"lift_object.lift_height":0.1787,"lift_object.lift_speed":0.15004,"lift_object.lift_tolerance":0.0596,"release_object.release_time":0.80242,"retract_after_place.retract_height":0.13519,"retract_after_place.retract_speed":0.05545,"retract_after_place.retract_tolerance":0.06129,"transport_to_goal.transport_speed":0.08913,"transport_to_goal.transport_tolerance":0.06402,"transport_to_goal.transport_z_offset":0.04802},"optimized_scores":{"best_composite_score":-0.40927,"best_fitness_score":0.59073,"best_task_score":0.24193},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.54914,0.09591,-0.00899],"force_p95":1.67473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01268,"mean_force":0.56849,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53811,0.10422,0.24766]},{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.51046,-0.02164,-0.00162],"force_p95":0.48023,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51102,"mean_force":0.24182,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49885,-0.02138,0.04094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.54662,0.12441,0.22964],"force_p95":0.1984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35584,"mean_force":0.08333,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54142,0.10562,0.22827]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1911.0,"contact_point_centroid":[0.50236,-0.0022,0.08629],"force_p95":0.15719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33957,"mean_force":0.07462,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50137,-0.02141,0.08351]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.50234,-0.04053,0.08513],"force_p95":0.14511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3133,"mean_force":0.06923,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50132,-0.02141,0.0831]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51374,-0.0228,-0.00214],"force_p95":0.16133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22449,"mean_force":0.1329,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50183,-0.02146,0.04115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":730.0,"contact_point_centroid":[0.54663,0.08689,0.23026],"force_p95":0.11039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21639,"mean_force":0.0696,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54138,0.10557,0.22821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1761.0,"contact_point_centroid":[0.52816,0.01485,0.18486],"force_p95":0.12211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20715,"mean_force":0.08694,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52355,0.03345,0.18314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.52817,0.05244,0.18586],"force_p95":0.11819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17998,"mean_force":0.08787,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52361,0.03367,0.18329]},{"body_a":"world","body_b":"grasp_target","contact_count":268.0,"contact_point_centroid":[0.55231,0.09727,-0.00233],"force_p95":0.13172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16443,"mean_force":0.10184,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54099,0.11339,0.2717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.50112,-0.00221,0.04266],"force_p95":0.08112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14994,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50067,-0.02143,0.03988]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.5137,-0.02302,-0.00096],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12042,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50338,-0.00219,0.28669]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13606,"mean_force":0.12303,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50718,-0.01453,0.145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5011.0,"contact_point_centroid":[0.50121,-0.04058,0.04173],"force_p95":0.07329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07711,"mean_force":0.04444,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50068,-0.02143,0.03989]}],"total_contact_groups":14},"final_pose_error":0.06063,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55233,0.09717,0.01623],"final_tcp_position":[0.54677,0.12839,0.30167],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":240.72894,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.0264],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26533,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.1365,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":124.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50796,-0.00652,0.26027],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23452,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.0264],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26533,"object_z_max":0.0264,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.13606,"subtask_id":"grasp","tcp_end":[0.50891,-0.02158,0.04908],"tcp_start":[0.50796,-0.00652,0.26027],"tcp_to_object_dist_end":0.0236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51364,-0.02169,0.02553],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.2651,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15436,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10890.0,"raw_peak_contact_force":0.22449,"tcp_end":[0.50065,-0.02143,0.03985],"tcp_start":[0.50891,-0.02158,0.04908],"tcp_to_object_dist_end":0.01934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":108.0,"n_steps_budget":690.0,"object_pos_end":[0.52608,-0.02173,0.13056],"object_pos_start":[0.51364,-0.02169,0.02553],"object_to_goal_dist_end":0.198,"object_to_goal_dist_start":0.2651,"object_z_max":0.12948,"peak_contact_force":240.72894,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4109.0,"raw_peak_contact_force":0.51102,"subtask_id":"lift","tcp_end":[0.5084,-0.02154,0.14551],"tcp_start":[0.50065,-0.02143,0.03985],"tcp_to_object_dist_end":0.02316,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.55974,0.10322,0.21152],"object_pos_start":[0.52608,-0.02173,0.13056],"object_to_goal_dist_end":0.04987,"object_to_goal_dist_start":0.198,"object_z_max":0.21088,"peak_contact_force":0.11557,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3357.0,"raw_peak_contact_force":0.20715,"subtask_id":"place","tcp_end":[0.54233,0.10348,0.2296],"tcp_start":[0.5084,-0.02154,0.14551],"tcp_to_object_dist_end":0.0251,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55053,0.10104,0.00824],"object_pos_start":[0.55974,0.10322,0.21152],"object_to_goal_dist_end":0.21969,"object_to_goal_dist_start":0.04987,"object_z_max":0.21328,"peak_contact_force":0.17581,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1640.0,"raw_peak_contact_force":2.01268,"tcp_end":[0.53807,0.10422,0.25366],"tcp_start":[0.54233,0.10348,0.2296],"tcp_to_object_dist_end":0.24576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.55233,0.09717,0.01623],"object_pos_start":[0.55053,0.10104,0.00824],"object_to_goal_dist_end":0.21286,"object_to_goal_dist_start":0.21969,"object_z_max":0.0168,"peak_contact_force":0.12976,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":268.0,"raw_peak_contact_force":0.16443,"tcp_end":[0.54677,0.12839,0.30167],"tcp_start":[0.53807,0.10422,0.25366],"tcp_to_object_dist_end":0.2872,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.05239,"approach_object.approach_speed":0.14449,"approach_object.approach_tolerance":0.05545,"descend_to_grasp.descend_speed":0.14806,"descend_to_grasp.descend_tolerance":0.01093,"descend_to_grasp.grasp_offset_z":0.0131,"grasp_action.grasp_max_width":0.05079,"lift_object.lift_height":0.15265,"lift_object.lift_speed":0.07663,"lift_object.lift_tolerance":0.05114,"release_object.release_time":1.30924,"retract_after_place.retract_height":0.10517,"retract_after_place.retract_speed":0.03342,"retract_after_place.retract_tolerance":0.04049,"transport_to_goal.transport_speed":0.17538,"transport_to_goal.transport_tolerance":0.05486,"transport_to_goal.transport_z_offset":0.01854},"optimized_scores":{"best_composite_score":-0.33474,"best_fitness_score":0.66526,"best_task_score":0.39085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":561.0,"contact_point_centroid":[0.60728,0.27409,-0.00349],"force_p95":0.73537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34942,"mean_force":0.19701,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54241,0.19525,0.15479]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.49977,0.0429,-0.00178],"force_p95":0.44026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49627,"mean_force":0.16976,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48765,0.04197,0.04107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2134.0,"contact_point_centroid":[0.49052,0.06122,0.07929],"force_p95":0.12053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31281,"mean_force":0.06584,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48992,0.04201,0.07724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.51947,0.07893,0.13838],"force_p95":0.1652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2776,"mean_force":0.10036,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51457,0.09774,0.13588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2002.0,"contact_point_centroid":[0.49017,0.02283,0.07786],"force_p95":0.11325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26171,"mean_force":0.0673,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48971,0.042,0.07509]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.04478,-0.00225],"force_p95":0.19033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25869,"mean_force":0.14054,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48995,0.04219,0.04117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1833.0,"contact_point_centroid":[0.52197,0.12313,0.13822],"force_p95":0.14001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24832,"mean_force":0.08263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5169,0.10473,0.13685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4783.0,"contact_point_centroid":[0.48896,0.02285,0.04275],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13943,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48881,0.04208,0.03994]},{"body_a":"world","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.50118,0.04505,-0.00177],"force_p95":0.13794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12351,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50135,0.01526,0.22221]},{"body_a":"world","body_b":"grasp_target","contact_count":416.0,"contact_point_centroid":[0.6078,0.2745,-0.00199],"force_p95":0.12279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12318,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54692,0.20822,0.19089]},{"body_a":"world","body_b":"grasp_target","contact_count":944.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49736,0.03776,0.08854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5409.0,"contact_point_centroid":[0.48873,0.0615,0.0422],"force_p95":0.07696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08144,"mean_force":0.04239,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48882,0.04208,0.03996]}],"total_contact_groups":12},"final_pose_error":0.04034,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.6078,0.2745,0.01602],"final_tcp_position":[0.55487,0.22648,0.21733],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.34942,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":552.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50128,0.03263,0.13546],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11014,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":944.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp","tcp_end":[0.49682,0.04275,0.04862],"tcp_start":[0.50128,0.03263,0.13546],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50117,0.04289,0.02515],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24411,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.18037,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11992.0,"raw_peak_contact_force":0.25869,"tcp_end":[0.48878,0.04208,0.03991],"tcp_start":[0.49682,0.04275,0.04862],"tcp_to_object_dist_end":0.01929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.51013,0.0428,0.1116],"object_pos_start":[0.50117,0.04289,0.02515],"object_to_goal_dist_end":0.21217,"object_to_goal_dist_start":0.24411,"object_z_max":0.1107,"peak_contact_force":0.09637,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4204.0,"raw_peak_contact_force":0.49627,"subtask_id":"lift","tcp_end":[0.49488,0.04228,0.12714],"tcp_start":[0.48878,0.04208,0.03991],"tcp_to_object_dist_end":0.02177,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.5727,0.19908,0.12125],"object_pos_start":[0.51013,0.0428,0.1116],"object_to_goal_dist_end":0.05307,"object_to_goal_dist_start":0.21217,"object_z_max":0.12697,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3277.0,"raw_peak_contact_force":0.2776,"subtask_id":"place","tcp_end":[0.54778,0.19555,0.15037],"tcp_start":[0.49488,0.04228,0.12714],"tcp_to_object_dist_end":0.03848,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6078,0.27449,0.016],"object_pos_start":[0.5727,0.19908,0.12125],"object_to_goal_dist_end":0.14093,"object_to_goal_dist_start":0.05307,"object_z_max":0.12125,"peak_contact_force":0.12322,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":561.0,"raw_peak_contact_force":1.34942,"tcp_end":[0.54186,0.19508,0.17289],"tcp_start":[0.54778,0.19555,0.15037],"tcp_to_object_dist_end":0.1878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.6078,0.2745,0.01602],"object_pos_start":[0.6078,0.27449,0.016],"object_to_goal_dist_end":0.14092,"object_to_goal_dist_start":0.14093,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":416.0,"raw_peak_contact_force":0.12318,"tcp_end":[0.55487,0.22648,0.21733],"tcp_start":[0.54186,0.19508,0.17289],"tcp_to_object_dist_end":0.21362,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.15931,"approach_object.approach_speed":0.0721,"approach_object.approach_tolerance":0.06842,"descend_to_grasp.descend_speed":0.07078,"descend_to_grasp.descend_tolerance":0.01011,"descend_to_grasp.grasp_offset_z":0.01159,"grasp_action.grasp_max_width":0.0391,"lift_object.lift_height":0.18277,"lift_object.lift_speed":0.11877,"lift_object.lift_tolerance":0.06762,"release_object.release_time":1.72588,"retract_after_place.retract_height":0.16274,"retract_after_place.retract_speed":0.10403,"retract_after_place.retract_tolerance":0.07429,"transport_to_goal.transport_speed":0.10666,"transport_to_goal.transport_tolerance":0.04444,"transport_to_goal.transport_z_offset":0.0331},"optimized_scores":{"best_composite_score":-0.37228,"best_fitness_score":0.62772,"best_task_score":0.30964},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":695.0,"contact_point_centroid":[0.65491,0.14761,-0.00338],"force_p95":0.76274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2198,"mean_force":0.20042,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60073,0.13015,0.20453]},{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.47342,-0.01917,-0.0016],"force_p95":0.49259,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54275,"mean_force":0.28169,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46365,-0.01906,0.03998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1973.0,"contact_point_centroid":[0.46547,-0.03831,0.08392],"force_p95":0.14974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31102,"mean_force":0.06613,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46534,-0.01908,0.08202]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1873.0,"contact_point_centroid":[0.46523,0.00014,0.08229],"force_p95":0.1564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28626,"mean_force":0.06879,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46514,-0.01907,0.08004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2449.0,"contact_point_centroid":[0.51997,0.0484,0.16427],"force_p95":0.12846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21956,"mean_force":0.07977,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51561,0.02961,0.16215]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02006,-0.00209],"force_p95":0.14897,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21173,"mean_force":0.12975,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46624,-0.01912,0.04005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2400.0,"contact_point_centroid":[0.51687,0.00737,0.16266],"force_p95":0.1321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19976,"mean_force":0.08329,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51251,0.02606,0.16084]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.47616,-0.02015,-0.00126],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12427,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49748,-0.0028,0.28361]},{"body_a":"world","body_b":"grasp_target","contact_count":2496.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12911,"mean_force":0.1227,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48101,-0.01373,0.1455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.46496,0.0001,0.04059],"force_p95":0.07005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1248,"mean_force":0.04326,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46515,-0.01909,0.03895]},{"body_a":"world","body_b":"grasp_target","contact_count":236.0,"contact_point_centroid":[0.65379,0.14696,-0.00199],"force_p95":0.12282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12292,"mean_force":0.12261,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60645,0.13563,0.24687]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.46535,-0.03835,0.04084],"force_p95":0.07145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07826,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46515,-0.01909,0.03896]}],"total_contact_groups":12},"final_pose_error":0.07345,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.65379,0.14696,0.01602],"final_tcp_position":[0.61725,0.14465,0.28216],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.2198,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":46.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02592],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28844,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12957,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":180.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.49246,-0.00793,0.25367],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22866,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02592],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28844,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2496.0,"raw_peak_contact_force":0.12911,"subtask_id":"grasp","tcp_end":[0.47287,-0.01925,0.04678],"tcp_start":[0.49246,-0.00793,0.25367],"tcp_to_object_dist_end":0.02104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01937,0.02566],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28815,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14629,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11752.0,"raw_peak_contact_force":0.21173,"tcp_end":[0.46512,-0.01909,0.03893],"tcp_start":[0.47287,-0.01925,0.04678],"tcp_to_object_dist_end":0.01721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":95.0,"n_steps_budget":900.0,"object_pos_end":[0.48652,-0.01926,0.12752],"object_pos_start":[0.47608,-0.01937,0.02566],"object_to_goal_dist_end":0.23821,"object_to_goal_dist_start":0.28815,"object_z_max":0.12628,"peak_contact_force":0.08673,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3906.0,"raw_peak_contact_force":0.54275,"subtask_id":"lift","tcp_end":[0.47169,-0.01918,0.14119],"tcp_start":[0.46512,-0.01909,0.03893],"tcp_to_object_dist_end":0.02017,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.64177,0.13976,0.07431],"object_pos_start":[0.48652,-0.01926,0.12752],"object_to_goal_dist_end":0.11778,"object_to_goal_dist_start":0.23821,"object_z_max":0.16662,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4849.0,"raw_peak_contact_force":0.21956,"subtask_id":"place","tcp_end":[0.60463,0.13026,0.20265],"tcp_start":[0.47169,-0.01918,0.14119],"tcp_to_object_dist_end":0.13395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65379,0.14697,0.01602],"object_pos_start":[0.64177,0.13976,0.07431],"object_to_goal_dist_end":0.17585,"object_to_goal_dist_start":0.11778,"object_z_max":0.07431,"peak_contact_force":0.12294,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":695.0,"raw_peak_contact_force":2.2198,"tcp_end":[0.5997,0.12983,0.22369],"tcp_start":[0.60463,0.13026,0.20265],"tcp_to_object_dist_end":0.21529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":59.0,"n_steps_budget":840.0,"object_pos_end":[0.65379,0.14696,0.01602],"object_pos_start":[0.65379,0.14697,0.01602],"object_to_goal_dist_end":0.17585,"object_to_goal_dist_start":0.17585,"object_z_max":0.01602,"peak_contact_force":0.12266,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":236.0,"raw_peak_contact_force":0.12292,"tcp_end":[0.61725,0.14465,0.28216],"tcp_start":[0.5997,0.12983,0.22369],"tcp_to_object_dist_end":0.26865,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```