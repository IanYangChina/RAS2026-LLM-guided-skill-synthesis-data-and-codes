## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4371 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0099 | 0.32 | ✅ accepted |
| 4 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.5365 | 0.17 | ❌ rejected |
| 2 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5125095466604667, 0.039721380096957554, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5125095466604667, 0.039721380096957554, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | approach/contact targets near object start |
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

## Current Skill (Q=-0.437) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
phases:
- id: approach_pre_grasp
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_success
    when: during_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: continue
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.1
      - 2.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
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
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: lift_object
- id: approach_goal
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
    - 0.2
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release
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
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_success, when=during_phase, predicate=pose_within_tolerance, on_failure=continue, threshold=0.02
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=reduce_speed
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.437
- **task_score** (E): 0.187
- **fitness_score**: 0.193  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 0.00 | 1.00 | 0.1650 |
| descend_to_grasp | 0.00 | 1.00 | 0.0286 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 0.33 | 1.00 | 0.0319 |
| approach_goal | 1.00 | 1.00 | 0.1999 |
| descend_place | 0.33 | 1.00 | 0.0735 |
| release | 1.00 | 1.00 | 0.0264 |
| retract | 1.00 | 1.00 | 0.0589 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.415, 0.005, 0.160) | (0.511, 0.022, 0.030)→(0.482, 0.023, 0.019) | 0.271→0.288 | 1.00 / 5.000 | 194.018 | 1380.749 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.415, 0.005, 0.160)→(0.439, 0.007, 0.149) | (0.482, 0.023, 0.019)→(0.483, 0.022, 0.019) | 0.288→0.288 | 1.00 / 5.000 | 260.806 | 544.040 |
| grasp | grasp | 1.00 / step_budget | (0.439, 0.007, 0.149)→(0.439, 0.007, 0.149) | (0.483, 0.022, 0.019)→(0.483, 0.022, 0.019) | 0.288→0.288 | 1.00 / 9.333 | 91046.297 | 135.606 |
| lift | lift | 0.33 / step_budget | (0.499, 0.030, 0.240)→(0.512, 0.053, 0.256) | (0.483, 0.022, 0.019)→(0.483, 0.022, 0.019) | 0.288→0.288 | 1.00 / 10.667 | 56211.420 | 671.605 |
| approach_goal | approach | 1.00 / step_budget | (0.512, 0.053, 0.256)→(0.590, 0.179, 0.363) | (0.480, 0.027, 0.019)→(0.478, 0.070, 0.018) | 0.285→0.263 | 1.00 / 7.333 | 0.211 | 325.845 |
| descend_place | descend | 0.33 / step_budget | (0.590, 0.179, 0.363)→(0.602, 0.198, 0.294) | (0.478, 0.070, 0.018)→(0.480, 0.068, 0.016) | 0.263→0.263 | 1.00 / 9.667 | 91552.979 | 569.123 |
| release | release | 1.00 / step_budget | (0.602, 0.198, 0.294)→(0.602, 0.197, 0.320) | (0.480, 0.068, 0.016)→(0.479, 0.068, 0.016) | 0.263→0.263 | 1.00 / 4.000 | 0.123 | 95.529 |
| retract | retract | 1.00 / step_budget | (0.602, 0.197, 0.320)→(0.606, 0.205, 0.376) | (0.479, 0.068, 0.016)→(0.479, 0.068, 0.016) | 0.263→0.263 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.296
- phase_score: 0.095
- phase_breakdown.approach_object_score: 0.125
- phase_breakdown.grasp_object_score: 0.067
- phase_breakdown.lift_object_score: 0.111
- phase_breakdown.place_at_goal_score: 0.072
- grasp_place_fitness: 0.239

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.239
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.296
- **Median Q (composite search score)**: -0.443
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.264


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
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.74667,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.08586,"approach_pre_grasp.speed":0.05678,"descend_place.speed":0.02973,"descend_to_grasp.speed":0.02345,"grasp.grasp_duration":1.10965,"lift.lift_height":0.12923,"lift.speed":0.05981,"release.release_duration":0.45574,"retract.speed":0.13567},"optimized_scores":{"best_composite_score":-0.39135,"best_fitness_score":0.23865,"best_task_score":0.29615},"replay_outcomes":[{"contacts":{"omitted_contact_groups":15,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64081,0.0106,-0.00046],"force_p95":200.57581,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1455.25837,"mean_force":201.44903,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40145,0.01008,0.12514]},{"body_a":"world","body_b":"link6","contact_count":1640.0,"contact_point_centroid":[0.59853,0.01482,-0.00025],"force_p95":575.52331,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":731.68619,"mean_force":330.65226,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4764,0.0384,0.23472]},{"body_a":"world","body_b":"link6","contact_count":901.0,"contact_point_centroid":[0.60062,0.13865,-0.00033],"force_p95":404.71962,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":593.69919,"mean_force":315.69979,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61155,0.14635,0.29343]},{"body_a":"link5","body_b":"hand","contact_count":936.0,"contact_point_centroid":[0.46512,-0.04824,0.23482],"force_p95":247.86297,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":562.74998,"mean_force":207.31355,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50676,0.02158,0.28232]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.5339,0.01101,-0.0033],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":380.58705,"mean_force":16.54726,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38136,0.006,0.04807]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.64736,0.01735,-0.00029],"force_p95":269.55857,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.4839,"mean_force":248.60193,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4293,0.01773,0.16385]},{"body_a":"link5","body_b":"hand","contact_count":8.0,"contact_point_centroid":[0.47715,-0.0496,0.23507],"force_p95":297.02897,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.70755,"mean_force":216.38214,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52299,0.02451,0.2898]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.57783,0.01305,-0.00018],"force_p95":209.97399,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.33679,"mean_force":178.31124,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52289,0.02512,0.28869]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.6057,0.14643,-0.00017],"force_p95":95.65606,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.09673,"mean_force":65.04505,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61434,0.14945,0.294]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.65928,0.01935,-0.00013],"force_p95":76.79784,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.07785,"mean_force":70.51778,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.43859,0.01945,0.16062]},{"body_a":"grasp_target","body_b":"link7","contact_count":738.0,"contact_point_centroid":[0.49833,0.02358,0.04727],"force_p95":0.79688,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.86165,"mean_force":0.27134,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40047,0.00961,0.12078]},{"body_a":"grasp_target","body_b":"hand","contact_count":440.0,"contact_point_centroid":[0.49203,0.02335,0.05644],"force_p95":1.37386,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.80616,"mean_force":0.3576,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39574,0.00754,0.10488]},{"body_a":"world","body_b":"grasp_target","contact_count":2228.0,"contact_point_centroid":[0.49624,0.04435,-0.00405],"force_p95":0.36981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.51868,"mean_force":0.27628,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.42085,0.00896,0.13988]},{"body_a":"grasp_target","body_b":"link6","contact_count":626.0,"contact_point_centroid":[0.50038,0.02038,0.03957],"force_p95":0.28575,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.17399,"mean_force":0.16944,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50887,0.00944,0.29132]},{"body_a":"grasp_target","body_b":"link6","contact_count":154.0,"contact_point_centroid":[0.51452,0.0571,0.04521],"force_p95":0.71247,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.01216,"mean_force":0.41632,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55925,0.07498,0.3049]},{"body_a":"world","body_b":"grasp_target","contact_count":5908.0,"contact_point_centroid":[0.5035,0.04265,-0.00247],"force_p95":0.38621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94462,"mean_force":0.15528,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4723,0.04435,0.22624]}],"total_contact_groups":31},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51911,0.10243,0.01602],"final_tcp_position":[0.62246,0.16197,0.32904],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50174,0.04442,0.02588],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21549,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":195.19694,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4316.0,"raw_peak_contact_force":1455.25837,"subtask_id":"approach_object","tcp_end":[0.41359,0.01583,0.15903],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16223,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50685,0.04075,0.02602],"object_pos_start":[0.50174,0.04442,0.02588],"object_to_goal_dist_end":0.2147,"object_to_goal_dist_start":0.21549,"object_z_max":0.02605,"peak_contact_force":268.52996,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4989.0,"raw_peak_contact_force":355.4839,"subtask_id":"grasp_object","tcp_end":[0.43828,0.01946,0.16098],"tcp_start":[0.41359,0.01583,0.15903],"tcp_to_object_dist_end":0.15287,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50685,0.04075,0.02602],"object_pos_start":[0.50685,0.04075,0.02602],"object_to_goal_dist_end":0.2147,"object_to_goal_dist_start":0.2147,"object_z_max":0.02602,"peak_contact_force":68.4381,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3509.0,"raw_peak_contact_force":82.07785,"tcp_end":[0.43863,0.01942,0.16049],"tcp_start":[0.43863,0.01942,0.1605],"tcp_to_object_dist_end":0.15229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1703.0,"n_steps_budget":750.0,"object_pos_end":[0.50669,0.04091,0.02602],"object_pos_start":[0.50685,0.04075,0.02602],"object_to_goal_dist_end":0.2147,"object_to_goal_dist_start":0.2147,"object_z_max":0.02625,"peak_contact_force":167951.73011,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16558.0,"raw_peak_contact_force":731.68619,"subtask_id":"lift_object","tcp_end":[0.52282,0.02528,0.28842],"tcp_start":[0.51624,0.01048,0.28574],"tcp_to_object_dist_end":0.26336,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.5155,0.10609,0.02103],"object_pos_start":[0.50464,0.04742,0.0255],"object_to_goal_dist_end":0.17986,"object_to_goal_dist_start":0.21224,"object_z_max":0.02657,"peak_contact_force":0.38661,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1197.0,"raw_peak_contact_force":301.70755,"subtask_id":"place_at_goal","tcp_end":[0.60227,0.13613,0.32353],"tcp_start":[0.52282,0.02528,0.28842],"tcp_to_object_dist_end":0.31613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52059,0.10287,0.01482],"object_pos_start":[0.5155,0.10609,0.02103],"object_to_goal_dist_end":0.18234,"object_to_goal_dist_start":0.17986,"object_z_max":0.0234,"peak_contact_force":1366.84211,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9888.0,"raw_peak_contact_force":593.69919,"subtask_id":"place_at_goal","tcp_end":[0.61433,0.14976,0.29369],"tcp_start":[0.60227,0.13613,0.32353],"tcp_to_object_dist_end":0.29792,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51907,0.10242,0.01603],"object_pos_start":[0.52059,0.10287,0.01482],"object_to_goal_dist_end":0.18256,"object_to_goal_dist_start":0.18234,"object_z_max":0.01605,"peak_contact_force":0.12353,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1229.0,"raw_peak_contact_force":96.09673,"tcp_end":[0.61457,0.14922,0.32014],"tcp_start":[0.61433,0.14976,0.29369],"tcp_to_object_dist_end":0.32217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":66.0,"n_steps_budget":600.0,"object_pos_end":[0.51911,0.10243,0.01602],"object_pos_start":[0.51907,0.10242,0.01603],"object_to_goal_dist_end":0.18253,"object_to_goal_dist_start":0.18256,"object_z_max":0.01603,"peak_contact_force":0.12268,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":264.0,"raw_peak_contact_force":0.12348,"tcp_end":[0.62246,0.16197,0.32904],"tcp_start":[0.61457,0.14922,0.32014],"tcp_to_object_dist_end":0.33498,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.75261,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.10944,"approach_pre_grasp.speed":0.02615,"descend_place.speed":0.02881,"descend_to_grasp.speed":0.02751,"grasp.grasp_duration":1.44173,"lift.lift_height":0.11324,"lift.speed":0.04503,"release.release_duration":0.55576,"retract.speed":0.06979},"optimized_scores":{"best_composite_score":-0.4432,"best_fitness_score":0.1868,"best_task_score":0.1366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52774,0.01039,-0.00306],"force_p95":460.37242,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1200.09023,"mean_force":76.57694,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37362,0.00529,0.04934]},{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63351,0.00829,-0.00046],"force_p95":195.88611,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1159.83475,"mean_force":200.12493,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38683,0.00783,0.11227]},{"body_a":"world","body_b":"link6","contact_count":707.0,"contact_point_centroid":[0.57003,0.21624,-0.00033],"force_p95":426.7164,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":594.43501,"mean_force":327.30305,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57944,0.22633,0.29338]},{"body_a":"world","body_b":"link6","contact_count":971.0,"contact_point_centroid":[0.64153,0.03466,-0.00023],"force_p95":283.44554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.76637,"mean_force":245.56496,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4303,0.1083,0.14609]},{"body_a":"world","body_b":"link6","contact_count":146.0,"contact_point_centroid":[0.55307,0.06935,-8e-05],"force_p95":408.9592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.11824,"mean_force":343.05833,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50914,0.12516,0.2716]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.64463,0.01381,-0.00031],"force_p95":305.18057,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.25416,"mean_force":286.99863,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4046,0.01463,0.12953]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.57103,0.22412,-0.00017],"force_p95":97.04498,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.5827,"mean_force":65.53852,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58105,0.22764,0.29395]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.65965,0.01712,-0.00013],"force_p95":81.2504,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.97852,"mean_force":69.71759,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41449,0.01793,0.12008]},{"body_a":"grasp_target","body_b":"hand","contact_count":47.0,"contact_point_centroid":[0.45998,0.03743,0.03982],"force_p95":3.90042,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.25848,"mean_force":1.69057,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38187,0.00537,0.0554]},{"body_a":"grasp_target","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.48683,0.03018,0.01275],"force_p95":0.82306,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.1837,"mean_force":0.47676,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37438,0.00532,0.05429]},{"body_a":"world","body_b":"grasp_target","contact_count":3894.0,"contact_point_centroid":[0.44765,0.04909,-0.00215],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03363,"mean_force":0.14151,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39943,0.00745,0.12327]},{"body_a":"grasp_target","body_b":"link6","contact_count":124.0,"contact_point_centroid":[0.46445,0.05442,0.03836],"force_p95":1.26396,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.5182,"mean_force":0.46549,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52416,0.1277,0.29387]},{"body_a":"world","body_b":"grasp_target","contact_count":1267.0,"contact_point_centroid":[0.43789,0.06363,-0.00257],"force_p95":0.52527,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71041,"mean_force":0.17374,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52104,0.15134,0.29728]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43428,0.08262,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12366,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57672,0.22409,0.30775]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44239,0.04909,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4046,0.01463,0.12953]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44239,0.04909,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41449,0.01793,0.12008]}],"total_contact_groups":24},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.43428,0.08262,0.01602],"final_tcp_position":[0.58291,0.22796,0.4107],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273024.07828,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44239,0.04909,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31268,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":193.50779,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4880.0,"raw_peak_contact_force":1200.09023,"subtask_id":"approach_object","tcp_end":[0.38977,0.011,0.13043],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13156,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44239,0.04909,0.01602],"object_pos_start":[0.44239,0.04909,0.01602],"object_to_goal_dist_end":0.31268,"object_to_goal_dist_start":0.31268,"object_z_max":0.01602,"peak_contact_force":274.81118,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":411.25416,"subtask_id":"grasp_object","tcp_end":[0.41398,0.01796,0.12061],"tcp_start":[0.38977,0.011,0.13043],"tcp_to_object_dist_end":0.11276,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44239,0.04909,0.01602],"object_pos_start":[0.44239,0.04909,0.01602],"object_to_goal_dist_end":0.31268,"object_to_goal_dist_start":0.31268,"object_z_max":0.01602,"peak_contact_force":66.3309,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3511.0,"raw_peak_contact_force":85.97852,"tcp_end":[0.41458,0.0179,0.11991],"tcp_start":[0.41458,0.01791,0.11991],"tcp_to_object_dist_end":0.11198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":977.0,"n_steps_budget":630.0,"object_pos_end":[0.44239,0.04909,0.01602],"object_pos_start":[0.44239,0.04909,0.01602],"object_to_goal_dist_end":0.31268,"object_to_goal_dist_start":0.31268,"object_z_max":0.01602,"peak_contact_force":234.76584,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8974.0,"raw_peak_contact_force":498.76637,"subtask_id":"lift_object","tcp_end":[0.45759,0.15026,0.19471],"tcp_start":[0.4263,0.10695,0.14974],"tcp_to_object_dist_end":0.20591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.43429,0.08259,0.01602],"object_pos_start":[0.44239,0.04909,0.01602],"object_to_goal_dist_end":0.29861,"object_to_goal_dist_start":0.31268,"object_z_max":0.01604,"peak_contact_force":0.12372,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3090.0,"raw_peak_contact_force":446.11824,"subtask_id":"place_at_goal","tcp_end":[0.56506,0.21512,0.38632],"tcp_start":[0.45759,0.15026,0.19471],"tcp_to_object_dist_end":0.41448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43428,0.08262,0.01602],"object_pos_start":[0.43429,0.08259,0.01602],"object_to_goal_dist_end":0.2986,"object_to_goal_dist_start":0.29861,"object_z_max":0.01602,"peak_contact_force":273005.31993,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8994.0,"raw_peak_contact_force":594.43501,"subtask_id":"place_at_goal","tcp_end":[0.58099,0.22795,0.29363],"tcp_start":[0.56506,0.21512,0.38632],"tcp_to_object_dist_end":0.34599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43428,0.08262,0.01602],"object_pos_start":[0.43428,0.08262,0.01602],"object_to_goal_dist_end":0.2986,"object_to_goal_dist_start":0.2986,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1108.0,"raw_peak_contact_force":97.5827,"tcp_end":[0.58132,0.2274,0.32028],"tcp_start":[0.58099,0.22795,0.29363],"tcp_to_object_dist_end":0.36763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":990.0,"object_pos_end":[0.43428,0.08262,0.01602],"object_pos_start":[0.43428,0.08262,0.01602],"object_to_goal_dist_end":0.2986,"object_to_goal_dist_start":0.2986,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58291,0.22796,0.4107],"tcp_start":[0.58132,0.2274,0.32028],"tcp_to_object_dist_end":0.44608,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17606,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.09321,"approach_pre_grasp.speed":0.08008,"descend_place.speed":0.02825,"descend_to_grasp.speed":0.0427,"grasp.grasp_duration":1.07348,"lift.lift_height":0.08883,"lift.speed":0.05074,"release.release_duration":0.60921,"retract.speed":0.07612},"optimized_scores":{"best_composite_score":-0.47661,"best_fitness_score":0.15339,"best_task_score":0.12737},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64632,-0.00674,-0.00045],"force_p95":208.05107,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1486.8991,"mean_force":199.82653,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.4166,-0.00668,0.13974]},{"body_a":"world","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.65898,-0.0083,-0.00025],"force_p95":350.88289,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":865.38226,"mean_force":273.99079,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4583,-0.01288,0.19038]},{"body_a":"world","body_b":"link6","contact_count":2100.0,"contact_point_centroid":[0.58274,-0.05419,-0.00027],"force_p95":566.45285,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":784.36198,"mean_force":406.73869,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53655,-0.02529,0.28374]},{"body_a":"world","body_b":"link6","contact_count":732.0,"contact_point_centroid":[0.59962,0.20205,-0.00031],"force_p95":371.81307,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":519.23527,"mean_force":293.67715,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60976,0.21228,0.29338]},{"body_a":"link5","body_b":"hand","contact_count":1874.0,"contact_point_centroid":[0.50539,-0.12002,0.24119],"force_p95":303.67802,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":492.70434,"mean_force":174.5705,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54089,-0.02698,0.28838]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54038,-0.00049,-0.00351],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":396.32607,"mean_force":17.23157,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38747,-0.00382,0.04674]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68753,-0.00303,-0.00012],"force_p95":70.68354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.76197,"mean_force":67.39683,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46501,-0.01615,0.16536]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.60004,-0.05572,-0.00017],"force_p95":225.228,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.70868,"mean_force":199.08749,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55645,-0.01591,0.28619]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.59927,0.21181,-0.00017],"force_p95":92.41284,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.9069,"mean_force":63.28466,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61087,0.21494,0.2939]},{"body_a":"grasp_target","body_b":"link7","contact_count":274.0,"contact_point_centroid":[0.51856,-0.01776,0.0343],"force_p95":1.89009,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.2622,"mean_force":0.57717,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40133,-0.00422,0.09835]},{"body_a":"grasp_target","body_b":"hand","contact_count":150.0,"contact_point_centroid":[0.50162,-0.02979,0.0487],"force_p95":2.18334,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.40803,"mean_force":0.88,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39755,-0.00395,0.08384]},{"body_a":"world","body_b":"grasp_target","contact_count":3672.0,"contact_point_centroid":[0.50761,-0.02434,-0.00238],"force_p95":0.33057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.3481,"mean_force":0.16239,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.42865,-0.00638,0.15144]},{"body_a":"grasp_target","body_b":"link6","contact_count":861.0,"contact_point_centroid":[0.52502,-0.0297,0.03628],"force_p95":0.39568,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.6217,"mean_force":0.26412,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53811,-0.03569,0.29257]},{"body_a":"grasp_target","body_b":"link6","contact_count":61.0,"contact_point_centroid":[0.51847,-0.00245,0.04078],"force_p95":0.69186,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81134,"mean_force":0.27023,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56701,0.01909,0.30174]},{"body_a":"grasp_target","body_b":"link6","contact_count":122.0,"contact_point_centroid":[0.54745,-0.0308,0.02328],"force_p95":0.68132,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72222,"mean_force":0.30892,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39518,-0.00394,0.08534]},{"body_a":"world","body_b":"grasp_target","contact_count":8720.0,"contact_point_centroid":[0.4974,-0.02091,-0.00217],"force_p95":0.28114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62185,"mean_force":0.14142,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53514,-0.02471,0.28198]}],"total_contact_groups":28},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.4849,0.01996,0.01602],"final_tcp_position":[0.61129,0.22545,0.38778],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.12061,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50099,-0.02473,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33516,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":193.3493,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5128.0,"raw_peak_contact_force":1486.8991,"subtask_id":"approach_object","tcp_end":[0.44203,-0.01154,0.19037],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18452,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50099,-0.02473,0.01602],"object_pos_start":[0.50099,-0.02473,0.01602],"object_to_goal_dist_end":0.33516,"object_to_goal_dist_start":0.33516,"object_z_max":0.01602,"peak_contact_force":239.07714,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4996.0,"raw_peak_contact_force":865.38226,"subtask_id":"grasp_object","tcp_end":[0.46511,-0.01569,0.16633],"tcp_start":[0.44203,-0.01154,0.19037],"tcp_to_object_dist_end":0.15479,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50099,-0.02473,0.01602],"object_pos_start":[0.50099,-0.02473,0.01602],"object_to_goal_dist_end":0.33516,"object_to_goal_dist_start":0.33516,"object_z_max":0.01602,"peak_contact_force":273004.12061,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3525.0,"raw_peak_contact_force":238.76197,"tcp_end":[0.46499,-0.0162,0.16524],"tcp_start":[0.46499,-0.01619,0.16524],"tcp_to_object_dist_end":0.15374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":2190.0,"n_steps_budget":870.0,"object_pos_end":[0.50099,-0.02473,0.01602],"object_pos_start":[0.50099,-0.02473,0.01602],"object_to_goal_dist_end":0.33516,"object_to_goal_dist_start":0.33516,"object_z_max":0.01606,"peak_contact_force":447.76292,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23284.0,"raw_peak_contact_force":784.36198,"subtask_id":"lift_object","tcp_end":[0.5554,-0.01656,0.28468],"tcp_start":[0.55475,-0.02613,0.28454],"tcp_to_object_dist_end":0.27424,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.4849,0.01995,0.01602],"object_pos_start":[0.49375,-0.01544,0.01602],"object_to_goal_dist_end":0.3091,"object_to_goal_dist_start":0.3307,"object_z_max":0.02049,"peak_contact_force":0.12288,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2090.0,"raw_peak_contact_force":229.70868,"subtask_id":"place_at_goal","tcp_end":[0.60348,0.18715,0.37949],"tcp_start":[0.5554,-0.01656,0.28468],"tcp_to_object_dist_end":0.41728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4849,0.01996,0.01602],"object_pos_start":[0.4849,0.01995,0.01602],"object_to_goal_dist_end":0.3091,"object_to_goal_dist_start":0.3091,"object_z_max":0.01602,"peak_contact_force":286.77646,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9025.0,"raw_peak_contact_force":519.23527,"subtask_id":"place_at_goal","tcp_end":[0.61081,0.21527,0.29361],"tcp_start":[0.60348,0.18715,0.37949],"tcp_to_object_dist_end":0.36202,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4849,0.01996,0.01602],"object_pos_start":[0.4849,0.01996,0.01602],"object_to_goal_dist_end":0.3091,"object_to_goal_dist_start":0.3091,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1111.0,"raw_peak_contact_force":92.9069,"tcp_end":[0.61111,0.21481,0.3197],"tcp_start":[0.61081,0.21527,0.29361],"tcp_to_object_dist_end":0.38225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":750.0,"object_pos_end":[0.4849,0.01996,0.01602],"object_pos_start":[0.4849,0.01996,0.01602],"object_to_goal_dist_end":0.3091,"object_to_goal_dist_start":0.3091,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61129,0.22545,0.38778],"tcp_start":[0.61111,0.21481,0.3197],"tcp_to_object_dist_end":0.44318,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```