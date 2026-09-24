## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | descend → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | -0.2841 | 0.17 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.2211 | 0.19 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6  | -0.2211 | 0.19 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6  | -0.2528 | 0.33 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=-0.253) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_grasp_height
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.25
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.25
- id: transport_above
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_target
  weight: 0.1
phases:
- id: descend_approach
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_height:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp_height
- id: grasp_object
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
    tolerance: 0.005
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: reach_grasp_height
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
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_above
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_target
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
    tolerance: 0.005
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
- id: retract_away
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_placed
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: continue

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_approach** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_away** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_placed, when=after_phase, predicate=object_lifted, on_failure=continue, threshold=0.02

## Design Metrics

- **Composite score**: -0.253
- **task_score** (E): 0.330
- **fitness_score**: 0.627  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1434 |
| descend_to_grasp | 1.00 | 1.00 | 0.1072 |
| grasp_object | 1.00 | 1.00 | 0.0121 |
| lift_object | 1.00 | 1.00 | 0.1182 |
| transport_to_goal | 1.00 | 1.00 | 0.2357 |
| descend_to_place | 1.00 | 1.00 | 0.1124 |
| release_object | 1.00 | 1.00 | 0.0201 |
| retract_away | 1.00 | 1.00 | 0.0997 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.163) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.163)→(0.506, 0.022, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.055)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.667 | 0.155 | 0.211 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.021, 0.046)→(0.506, 0.021, 0.164) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.140) | 0.274→0.222 | 1.00 / 37.667 | 0.083 | 0.371 |
| transport_to_goal | approach | 1.00 / step_budget | (0.506, 0.021, 0.164)→(0.592, 0.182, 0.307) | (0.514, 0.022, 0.140)→(0.597, 0.182, 0.277) | 0.222→0.088 | 1.00 / 23.667 | 0.129 | 0.155 |
| descend_to_place | descend | 1.00 / step_budget | (0.592, 0.182, 0.307)→(0.601, 0.204, 0.198) | (0.597, 0.182, 0.277)→(0.607, 0.204, 0.165) | 0.088→0.030 | 1.00 / 18.000 | 0.136 | 0.355 |
| release_object | release | 1.00 / step_budget | (0.601, 0.204, 0.198)→(0.595, 0.202, 0.217) | (0.607, 0.204, 0.165)→(0.593, 0.200, 0.022) | 0.030→0.173 | 1.00 / 2.667 | 0.251 | 1.599 |
| retract_away | retract | 1.00 / step_budget | (0.595, 0.202, 0.217)→(0.604, 0.208, 0.316) | (0.593, 0.200, 0.022)→(0.582, 0.202, 0.026) | 0.173→0.170 | 1.00 / 4.000 | 0.123 | 0.250 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.444
- phase_score: 0.685
- phase_breakdown.reach_grasp_height_score: 0.681
- phase_breakdown.place_target_score: 0.816
- phase_breakdown.lift_clearance_score: 0.750
- phase_breakdown.transport_above_score: 0.677
- phase_breakdown.reach_approach_score: 0.552
- grasp_place_fitness: 0.684

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.684
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.444
- **Median Q (composite search score)**: -0.271
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.299


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79472,"average_solve_count":492.0,"average_success_count":492.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.11077,"descend_approach.approach_speed":0.05189,"descend_to_grasp.descend_speed":0.0401,"descend_to_grasp.grasp_height":0.02078,"descend_to_place.place_speed":0.02494,"descend_to_place.place_z_offset":-0.00566,"lift_object.lift_height":0.16038,"lift_object.lift_speed":0.01823,"release_object.release_duration":1.59681,"retract_away.retract_height":0.14157,"retract_away.retract_speed":0.06474,"transport_to_goal.arc_height":0.11661,"transport_to_goal.transport_height":0.09949,"transport_to_goal.transport_speed":0.03229},"optimized_scores":{"best_composite_score":-0.19598,"best_fitness_score":0.68402,"best_task_score":0.44363},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.60984,0.16636,-0.00603],"force_p95":1.0481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33711,"mean_force":0.33025,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61485,0.16699,0.15996]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2954.0,"contact_point_centroid":[0.62109,0.18212,0.20429],"force_p95":0.10789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48565,"mean_force":0.07447,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61667,0.16373,0.20518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2671.0,"contact_point_centroid":[0.61976,0.14503,0.20423],"force_p95":0.13147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40075,"mean_force":0.0847,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6166,0.16365,0.20607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.62392,0.18654,0.14619],"force_p95":0.10521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37728,"mean_force":0.06767,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61896,0.16833,0.14723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":587.0,"contact_point_centroid":[0.62316,0.14969,0.1446],"force_p95":0.13719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36447,"mean_force":0.08836,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61894,0.16832,0.14722]},{"body_a":"world","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.50971,0.03763,-0.00168],"force_p95":0.30718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34843,"mean_force":0.14226,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49819,0.03785,0.04705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9635.0,"contact_point_centroid":[0.50149,0.05696,0.10368],"force_p95":0.07962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23331,"mean_force":0.0513,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50133,0.03786,0.1018]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.0396,-0.00215],"force_p95":0.16428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22264,"mean_force":0.13358,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50043,0.03804,0.0475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8690.0,"contact_point_centroid":[0.50114,0.01869,0.10599],"force_p95":0.08169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21041,"mean_force":0.0549,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50159,0.03787,0.10471]},{"body_a":"world","body_b":"grasp_target","contact_count":1682.0,"contact_point_centroid":[0.60255,0.16463,-0.00199],"force_p95":0.15837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20313,"mean_force":0.1238,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.61813,0.16872,0.21882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15148.0,"contact_point_centroid":[0.53825,0.09297,0.24401],"force_p95":0.07958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15226,"mean_force":0.05265,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53742,0.07391,0.24328]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14807.0,"contact_point_centroid":[0.53894,0.05664,0.24587],"force_p95":0.08218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1416,"mean_force":0.05381,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53905,0.07573,0.24535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4331.0,"contact_point_centroid":[0.4996,0.0187,0.04783],"force_p95":0.07798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13957,"mean_force":0.04967,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49928,0.03795,0.04622]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50286,0.01605,0.23089]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50589,0.03597,0.10619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5517.0,"contact_point_centroid":[0.50054,0.05713,0.04853],"force_p95":0.07072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07253,"mean_force":0.04035,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03795,0.04623]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60235,0.16447,0.02602],"final_tcp_position":[0.62384,0.17111,0.26705],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.33711,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50736,0.03359,0.15865],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50733,0.03859,0.05525],"tcp_start":[0.50736,0.03359,0.15865],"tcp_to_object_dist_end":0.02971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03845,0.02546],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21334,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16118,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11648.0,"raw_peak_contact_force":0.22264,"subtask_id":"reach_grasp_height","tcp_end":[0.49926,0.03795,0.04619],"tcp_start":[0.50733,0.03859,0.05525],"tcp_to_object_dist_end":0.02459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.51589,0.0386,0.14273],"object_pos_start":[0.51248,0.03845,0.02546],"object_to_goal_dist_end":0.17439,"object_to_goal_dist_start":0.21334,"object_z_max":0.14247,"peak_contact_force":0.08282,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18440.0,"raw_peak_contact_force":0.34843,"subtask_id":"lift_clearance","tcp_end":[0.50757,0.0381,0.16661],"tcp_start":[0.49926,0.03795,0.04619],"tcp_to_object_dist_end":0.02529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.62008,0.16006,0.22365],"object_pos_start":[0.51589,0.0386,0.14273],"object_to_goal_dist_end":0.07996,"object_to_goal_dist_start":0.17439,"object_z_max":0.25403,"peak_contact_force":0.11003,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29955.0,"raw_peak_contact_force":0.15226,"subtask_id":"transport_above","tcp_end":[0.61463,0.15985,0.25234],"tcp_start":[0.50757,0.0381,0.16661],"tcp_to_object_dist_end":0.0292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.62773,0.16946,0.12142],"object_pos_start":[0.62008,0.16006,0.22365],"object_to_goal_dist_end":0.0238,"object_to_goal_dist_start":0.07996,"object_z_max":0.22365,"peak_contact_force":0.13399,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5625.0,"raw_peak_contact_force":0.48565,"subtask_id":"place_target","tcp_end":[0.62132,0.16893,0.15217],"tcp_start":[0.61463,0.15985,0.25234],"tcp_to_object_dist_end":0.03142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60889,0.16753,0.02686],"object_pos_start":[0.62773,0.16946,0.12142],"object_to_goal_dist_end":0.11974,"object_to_goal_dist_start":0.0238,"object_z_max":0.12142,"peak_contact_force":0.19459,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1570.0,"raw_peak_contact_force":1.33711,"tcp_end":[0.61477,0.16696,0.17098],"tcp_start":[0.62132,0.16893,0.15217],"tcp_to_object_dist_end":0.14424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.60235,0.16447,0.02602],"object_pos_start":[0.60889,0.16753,0.02686],"object_to_goal_dist_end":0.12191,"object_to_goal_dist_start":0.11974,"object_z_max":0.02694,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1682.0,"raw_peak_contact_force":0.20313,"tcp_end":[0.62384,0.17111,0.26705],"tcp_start":[0.61477,0.16696,0.17098],"tcp_to_object_dist_end":0.24208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.56021,"average_solve_count":573.0,"average_success_count":573.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.10859,"descend_approach.approach_speed":0.01012,"descend_to_grasp.descend_speed":0.01749,"descend_to_grasp.grasp_height":0.02003,"descend_to_place.place_speed":0.01506,"descend_to_place.place_z_offset":-0.00771,"lift_object.lift_height":0.15451,"lift_object.lift_speed":0.04246,"release_object.release_duration":0.9306,"retract_away.retract_height":0.12231,"retract_away.retract_speed":0.06117,"transport_to_goal.arc_height":0.08869,"transport_to_goal.transport_height":0.11692,"transport_to_goal.transport_speed":0.03573},"optimized_scores":{"best_composite_score":-0.29121,"best_fitness_score":0.58879,"best_task_score":0.25313},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.5693,0.22284,-0.01159],"force_p95":1.56938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92749,"mean_force":0.69344,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57187,0.22091,0.24768]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.47934,0.04616,-0.00156],"force_p95":0.3743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4001,"mean_force":0.13875,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4697,0.04654,0.048]},{"body_a":"world","body_b":"grasp_target","contact_count":1153.0,"contact_point_centroid":[0.55992,0.22293,-0.00234],"force_p95":0.24281,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31504,"mean_force":0.1363,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.57517,0.22409,0.2981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":530.0,"contact_point_centroid":[0.57998,0.24072,0.22591],"force_p95":0.13361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30213,"mean_force":0.09705,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57462,0.22231,0.2305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2650.0,"contact_point_centroid":[0.57442,0.22776,0.29429],"force_p95":0.13279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28848,"mean_force":0.09912,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.569,0.20952,0.29701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":597.0,"contact_point_centroid":[0.57998,0.20407,0.22655],"force_p95":0.11777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27461,"mean_force":0.0836,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57463,0.22231,0.2305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8061.0,"contact_point_centroid":[0.47279,0.06563,0.10326],"force_p95":0.08371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27448,"mean_force":0.05442,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47256,0.04661,0.10192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2499.0,"contact_point_centroid":[0.57448,0.19222,0.28912],"force_p95":0.1227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25722,"mean_force":0.09929,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56948,0.2104,0.29272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6774.0,"contact_point_centroid":[0.47188,0.02743,0.10367],"force_p95":0.08941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24129,"mean_force":0.06177,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4726,0.04662,0.10246]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.0486,-0.00217],"force_p95":0.16872,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22838,"mean_force":0.13476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47168,0.04675,0.04793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16191.0,"contact_point_centroid":[0.49798,0.10035,0.27268],"force_p95":0.09872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16638,"mean_force":0.06168,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4957,0.08164,0.27267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14916.0,"contact_point_centroid":[0.49478,0.05899,0.26967],"force_p95":0.12626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15952,"mean_force":0.06749,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49349,0.07788,0.2702]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49068,0.01953,0.23072]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47869,0.04415,0.10566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.46975,0.0274,0.04856],"force_p95":0.07194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11435,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47058,0.04665,0.04679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5509.0,"contact_point_centroid":[0.47013,0.06594,0.04845],"force_p95":0.07104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07343,"mean_force":0.04077,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47059,0.04665,0.0468]}],"total_contact_groups":16},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5569,0.22271,0.02602],"final_tcp_position":[0.57896,0.22698,0.33312],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.92749,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48201,0.04128,0.15702],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47825,0.04738,0.05483],"tcp_start":[0.48201,0.04128,0.15702],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04736,0.0254],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29127,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16445,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12120.0,"raw_peak_contact_force":0.22838,"subtask_id":"reach_grasp_height","tcp_end":[0.47056,0.04664,0.04676],"tcp_start":[0.47825,0.04738,0.05483],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.48559,0.0473,0.13649],"object_pos_start":[0.48268,0.04736,0.0254],"object_to_goal_dist_end":0.22598,"object_to_goal_dist_start":0.29127,"object_z_max":0.13622,"peak_contact_force":0.08715,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14926.0,"raw_peak_contact_force":0.4001,"subtask_id":"lift_clearance","tcp_end":[0.47789,0.04693,0.16066],"tcp_start":[0.47056,0.04664,0.04676],"tcp_to_object_dist_end":0.02537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57016,0.20046,0.31687],"object_pos_start":[0.48559,0.0473,0.13649],"object_to_goal_dist_end":0.09169,"object_to_goal_dist_start":0.22598,"object_z_max":0.32049,"peak_contact_force":0.12873,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31107.0,"raw_peak_contact_force":0.16638,"subtask_id":"transport_above","tcp_end":[0.56426,0.19953,0.34885],"tcp_start":[0.47789,0.04693,0.16066],"tcp_to_object_dist_end":0.03253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.58186,0.22345,0.20006],"object_pos_start":[0.57016,0.20046,0.31687],"object_to_goal_dist_end":0.0309,"object_to_goal_dist_start":0.09169,"object_z_max":0.31687,"peak_contact_force":0.13329,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5149.0,"raw_peak_contact_force":0.28848,"subtask_id":"place_target","tcp_end":[0.57637,0.22288,0.23506],"tcp_start":[0.56426,0.19953,0.34885],"tcp_to_object_dist_end":0.03544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57347,0.21665,0.01684],"object_pos_start":[0.58186,0.22345,0.20006],"object_to_goal_dist_end":0.21416,"object_to_goal_dist_start":0.0309,"object_z_max":0.20006,"peak_contact_force":0.32628,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1236.0,"raw_peak_contact_force":1.92749,"tcp_end":[0.57184,0.2209,0.25502],"tcp_start":[0.57637,0.22288,0.23506],"tcp_to_object_dist_end":0.23822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.5569,0.22271,0.02602],"object_pos_start":[0.57347,0.21665,0.01684],"object_to_goal_dist_end":0.20608,"object_to_goal_dist_start":0.21416,"object_z_max":0.02993,"peak_contact_force":0.12294,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1153.0,"raw_peak_contact_force":0.31504,"tcp_end":[0.57896,0.22698,0.33312],"tcp_start":[0.57184,0.2209,0.25502],"tcp_to_object_dist_end":0.30792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98495,"average_solve_count":465.0,"average_success_count":465.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.12486,"descend_approach.approach_speed":0.07753,"descend_to_grasp.descend_speed":0.03116,"descend_to_grasp.grasp_height":0.02231,"descend_to_place.place_speed":0.02533,"descend_to_place.place_z_offset":-0.01198,"lift_object.lift_height":0.1594,"lift_object.lift_speed":0.03682,"release_object.release_duration":1.4284,"retract_away.retract_height":0.16114,"retract_away.retract_speed":0.06324,"transport_to_goal.arc_height":0.08022,"transport_to_goal.transport_height":0.10784,"transport_to_goal.transport_speed":0.04882},"optimized_scores":{"best_composite_score":-0.27108,"best_fitness_score":0.60892,"best_task_score":0.29466},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.59089,0.21747,-0.00838],"force_p95":1.33079,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53295,"mean_force":0.44261,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59981,0.21788,0.21807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":488.0,"contact_point_centroid":[0.60778,0.23766,0.19869],"force_p95":0.14515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39253,"mean_force":0.10148,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60293,0.21935,0.20164]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.53347,-0.02065,-0.0015],"force_p95":0.34395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36366,"mean_force":0.13757,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52199,-0.02066,0.04741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.60783,0.2013,0.19809],"force_p95":0.13658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35592,"mean_force":0.09423,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60295,0.21936,0.20168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2813.0,"contact_point_centroid":[0.60373,0.18353,0.2645],"force_p95":0.12598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29163,"mean_force":0.09354,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5994,0.20148,0.26626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2466.0,"contact_point_centroid":[0.60372,0.21866,0.26771],"force_p95":0.13785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28006,"mean_force":0.10501,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59907,0.20038,0.26992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8438.0,"contact_point_centroid":[0.52588,-0.0015,0.10624],"force_p95":0.0805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24425,"mean_force":0.05706,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52555,-0.02067,0.10451]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9431.0,"contact_point_centroid":[0.52585,-0.03975,0.10444],"force_p95":0.07751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24341,"mean_force":0.05213,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52539,-0.02067,0.10277]},{"body_a":"world","body_b":"grasp_target","contact_count":2069.0,"contact_point_centroid":[0.58626,0.21887,-0.00205],"force_p95":0.17199,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23094,"mean_force":0.12452,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.60306,0.22185,0.28857]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02126,-0.00206],"force_p95":0.13999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18107,"mean_force":0.12733,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52418,-0.0207,0.04794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18499.0,"contact_point_centroid":[0.55243,0.02877,0.26704],"force_p95":0.08178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14735,"mean_force":0.05343,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55115,0.04759,0.26679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16109.0,"contact_point_centroid":[0.55192,0.06489,0.26511],"force_p95":0.11442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14269,"mean_force":0.06264,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55058,0.04583,0.26503]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51276,-0.00855,0.23718]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52808,-0.0193,0.11321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4352.0,"contact_point_centroid":[0.52391,-0.00149,0.04822],"force_p95":0.07368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1155,"mean_force":0.04944,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52298,-0.02068,0.04654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.52382,-0.03982,0.04801],"force_p95":0.06974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08812,"mean_force":0.04457,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52298,-0.02068,0.04654]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58553,0.21892,0.02602],"final_tcp_position":[0.60826,0.22626,0.34879],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.53295,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52791,-0.01786,0.17187],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1556.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.53129,-0.02083,0.0564],"tcp_start":[0.52791,-0.01786,0.17187],"tcp_to_object_dist_end":0.03092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02083,0.02577],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3165,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13858,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11056.0,"raw_peak_contact_force":0.18107,"subtask_id":"reach_grasp_height","tcp_end":[0.52295,-0.02068,0.0465],"tcp_start":[0.53129,-0.02083,0.0564],"tcp_to_object_dist_end":0.02502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.54068,-0.02091,0.14181],"object_pos_start":[0.53695,-0.02083,0.02577],"object_to_goal_dist_end":0.26644,"object_to_goal_dist_start":0.3165,"object_z_max":0.14156,"peak_contact_force":0.07783,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17965.0,"raw_peak_contact_force":0.36366,"subtask_id":"lift_clearance","tcp_end":[0.53189,-0.02074,0.16587],"tcp_start":[0.52295,-0.02068,0.0465],"tcp_to_object_dist_end":0.02562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60146,0.18536,0.29041],"object_pos_start":[0.54068,-0.02091,0.14181],"object_to_goal_dist_end":0.09362,"object_to_goal_dist_start":0.26644,"object_z_max":0.29588,"peak_contact_force":0.14735,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34608.0,"raw_peak_contact_force":0.14735,"subtask_id":"transport_above","tcp_end":[0.5959,0.18635,0.3211],"tcp_start":[0.53189,-0.02074,0.16587],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.61038,0.21917,0.17299],"object_pos_start":[0.60146,0.18536,0.29041],"object_to_goal_dist_end":0.03547,"object_to_goal_dist_start":0.09362,"object_z_max":0.29041,"peak_contact_force":0.13963,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5279.0,"raw_peak_contact_force":0.29163,"subtask_id":"place_target","tcp_end":[0.60499,0.21986,0.20668],"tcp_start":[0.5959,0.18635,0.3211],"tcp_to_object_dist_end":0.03412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59811,0.21477,0.02186],"object_pos_start":[0.61038,0.21917,0.17299],"object_to_goal_dist_end":0.18641,"object_to_goal_dist_start":0.03547,"object_z_max":0.17299,"peak_contact_force":0.23186,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1184.0,"raw_peak_contact_force":1.53295,"tcp_end":[0.59978,0.21787,0.22553],"tcp_start":[0.60499,0.21986,0.20668],"tcp_to_object_dist_end":0.2037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.58553,0.21892,0.02602],"object_pos_start":[0.59811,0.21477,0.02186],"object_to_goal_dist_end":0.18329,"object_to_goal_dist_start":0.18641,"object_z_max":0.02817,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2069.0,"raw_peak_contact_force":0.23094,"tcp_end":[0.60826,0.22626,0.34879],"tcp_start":[0.59978,0.21787,0.22553],"tcp_to_object_dist_end":0.32365,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```