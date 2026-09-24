## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3858 | 0.16 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5282 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4531 | 0.15 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.4782 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.3825 | 0.14 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.386) — your mutation base

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

- **Composite score**: -0.386
- **task_score** (E): 0.156
- **fitness_score**: 0.169  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 0.00 | 1.00 | 0.1618 |
| descend_to_grasp | 1.00 | 1.00 | 0.0002 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.0054 |
| approach_goal | 0.00 | 1.00 | 0.1196 |
| descend_place | 0.00 | 1.00 | 0.0062 |
| release | 1.00 | 1.00 | 0.0265 |
| retract | 0.00 | 1.00 | 0.0023 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.428, 0.012, 0.158) | (0.511, 0.022, 0.030)→(0.482, 0.021, 0.019) | 0.271→0.288 | 1.00 / 4.667 | 160.361 | 1410.099 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.428, 0.012, 0.158)→(0.428, 0.012, 0.158) | (0.482, 0.021, 0.019)→(0.482, 0.021, 0.019) | 0.288→0.288 | 1.00 / 4.667 | 3440.760 | 54.956 |
| grasp | grasp | 1.00 / step_budget | (0.428, 0.012, 0.157)→(0.428, 0.012, 0.157) | (0.482, 0.021, 0.019)→(0.482, 0.021, 0.019) | 0.288→0.288 | 1.00 / 9.000 | 74.393 | 94.704 |
| lift | lift | 1.00 / step_budget | (0.458, 0.024, 0.193)→(0.458, 0.023, 0.193) | (0.482, 0.021, 0.019)→(0.482, 0.021, 0.019) | 0.288→0.288 | 1.00 / 8.333 | 137.672 | 465.541 |
| approach_goal | approach | 0.00 / step_budget | (0.458, 0.023, 0.193)→(0.508, 0.104, 0.264) | (0.482, 0.021, 0.019)→(0.482, 0.021, 0.019) | 0.288→0.288 | 1.00 / 8.333 | 85.496 | 250.890 |
| descend_place | descend | 0.00 / step_budget | (0.508, 0.104, 0.264)→(0.510, 0.109, 0.268) | (0.482, 0.021, 0.019)→(0.482, 0.021, 0.019) | 0.288→0.288 | 1.00 / 9.000 | 266.245 | 265.609 |
| release | release | 1.00 / step_budget | (0.510, 0.109, 0.268)→(0.510, 0.118, 0.290) | (0.482, 0.021, 0.019)→(0.482, 0.021, 0.019) | 0.288→0.288 | 1.00 / 4.667 | 99.517 | 163.466 |
| retract | retract | 0.00 / step_budget | (0.510, 0.118, 0.290)→(0.510, 0.119, 0.292) | (0.482, 0.021, 0.019)→(0.482, 0.021, 0.019) | 0.288→0.288 | 1.00 / 4.667 | 130.948 | 141.726 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.237
- phase_score: 0.155
- phase_breakdown.approach_object_score: 0.164
- phase_breakdown.grasp_object_score: 0.049
- phase_breakdown.lift_object_score: 0.444
- phase_breakdown.place_at_goal_score: 0.025
- grasp_place_fitness: 0.201

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.201
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.237
- **Median Q (composite search score)**: -0.392
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":219.0,"average_failure_rate":0.70645,"average_mean_iterations":144.60323,"average_solve_count":310.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.09618,"approach_pre_grasp.speed":0.0793,"descend_place.speed":0.0407,"descend_to_grasp.force_threshold":5.33138,"descend_to_grasp.speed":0.02907,"grasp.grasp_duration":0.85486,"lift.lift_height":0.13756,"lift.speed":0.04839,"release.release_duration":0.67878,"retract.speed":0.07699},"optimized_scores":{"best_composite_score":-0.35401,"best_fitness_score":0.20099,"best_task_score":0.23731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.6432,0.01252,-0.00044],"force_p95":208.83799,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1330.93236,"mean_force":203.51256,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40685,0.01194,0.12942]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53514,0.01135,-0.00301],"force_p95":266.03137,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1260.11459,"mean_force":65.54553,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38368,0.0065,0.04688]},{"body_a":"world","body_b":"link6","contact_count":157.0,"contact_point_centroid":[0.65698,0.0223,-6e-05],"force_p95":591.69795,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":801.28799,"mean_force":283.12966,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45285,0.02297,0.18262]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.52742,-0.02299,0.18094],"force_p95":531.36203,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":532.95424,"mean_force":469.51707,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.47684,0.06378,0.18147]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.52828,-0.01055,0.18374],"force_p95":275.7617,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.75676,"mean_force":222.39503,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.47652,0.07549,0.18646]},{"body_a":"link5","body_b":"hand","contact_count":11.0,"contact_point_centroid":[0.53264,0.00921,0.19845],"force_p95":271.05609,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.42109,"mean_force":241.11111,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47681,0.0926,0.20313]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63788,0.01963,-0.00013],"force_p95":76.77023,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.75568,"mean_force":71.42647,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42496,0.01997,0.17078]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63704,0.01965,-0.00022],"force_p95":76.33461,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.33461,"mean_force":76.33461,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42464,0.02,0.17125]},{"body_a":"grasp_target","body_b":"link7","contact_count":675.0,"contact_point_centroid":[0.50196,0.02638,0.04661],"force_p95":0.78977,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.7294,"mean_force":0.30133,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40299,0.01019,0.11838]},{"body_a":"grasp_target","body_b":"hand","contact_count":402.0,"contact_point_centroid":[0.49607,0.02279,0.05611],"force_p95":1.66838,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.88793,"mean_force":0.39238,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39804,0.0082,0.10265]},{"body_a":"world","body_b":"grasp_target","contact_count":2569.0,"contact_point_centroid":[0.49819,0.04309,-0.00339],"force_p95":0.37898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56047,"mean_force":0.2327,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.42463,0.01151,0.146]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50502,0.04072,-0.00199],"force_p95":0.12339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12349,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42464,0.02,0.17125]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50502,0.04072,-0.00199],"force_p95":0.12269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12346,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42496,0.01997,0.17078]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.50502,0.04072,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4555,0.02436,0.18046]},{"body_a":"world","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.50502,0.04072,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47445,0.05343,0.17635]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.50502,0.04072,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.4765,0.06219,0.18065]}],"total_contact_groups":23},"final_pose_error":0.21951,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50502,0.04072,0.02602],"final_tcp_position":[0.47711,0.09499,0.20525],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1330.93236,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50499,0.04074,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":201.61,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4557.0,"raw_peak_contact_force":1330.93236,"subtask_id":"approach_object","tcp_end":[0.42464,0.02,0.17125],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16727,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50499,0.04074,0.02602],"object_pos_start":[0.50499,0.04074,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":76.33461,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":76.33461,"subtask_id":"grasp_object","tcp_end":[0.42465,0.02001,0.17121],"tcp_start":[0.42464,0.02,0.17125],"tcp_to_object_dist_end":0.16723,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50502,0.04072,0.02602],"object_pos_start":[0.50499,0.04074,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":69.74288,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3497.0,"raw_peak_contact_force":82.75568,"tcp_end":[0.42501,0.01994,0.17066],"tcp_start":[0.42501,0.01994,0.17066],"tcp_to_object_dist_end":0.1666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.50502,0.04072,0.02602],"object_pos_start":[0.50502,0.04072,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1957.0,"raw_peak_contact_force":801.28799,"subtask_id":"lift_object","tcp_end":[0.47348,0.0495,0.17424],"tcp_start":[0.47205,0.04355,0.17133],"tcp_to_object_dist_end":0.1518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.50502,0.04072,0.02602],"object_pos_start":[0.50502,0.04072,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":100.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47592,0.05939,0.1793],"tcp_start":[0.47348,0.0495,0.17424],"tcp_to_object_dist_end":0.15713,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.50502,0.04072,0.02602],"object_pos_start":[0.50502,0.04072,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":524.33337,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":532.95424,"subtask_id":"place_at_goal","tcp_end":[0.4773,0.06549,0.18292],"tcp_start":[0.47592,0.05939,0.1793],"tcp_to_object_dist_end":0.16125,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50502,0.04072,0.02602],"object_pos_start":[0.50502,0.04072,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":224.15148,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1226.0,"raw_peak_contact_force":281.75676,"tcp_end":[0.47655,0.09134,0.2022],"tcp_start":[0.4773,0.06549,0.18292],"tcp_to_object_dist_end":0.1855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50502,0.04072,0.02602],"object_pos_start":[0.50502,0.04072,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":239.35925,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":55.0,"raw_peak_contact_force":271.42109,"tcp_end":[0.47711,0.09499,0.20525],"tcp_start":[0.47655,0.09134,0.2022],"tcp_to_object_dist_end":0.18933,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":148.0,"average_failure_rate":0.48366,"average_mean_iterations":99.20588,"average_solve_count":306.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.08043,"approach_pre_grasp.speed":0.05002,"descend_place.speed":0.02366,"descend_to_grasp.force_threshold":5.50559,"descend_to_grasp.speed":0.0294,"grasp.grasp_duration":1.01482,"lift.lift_height":0.24441,"lift.speed":0.0861,"release.release_duration":0.56713,"retract.speed":0.10031},"optimized_scores":{"best_composite_score":-0.39221,"best_fitness_score":0.16279,"best_task_score":0.12446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63433,0.01126,-0.00046],"force_p95":200.44016,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1377.70028,"mean_force":203.82723,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39021,0.01056,0.11707]},{"body_a":"link5","body_b":"hand","contact_count":211.0,"contact_point_centroid":[0.54838,0.07436,0.30191],"force_p95":376.71837,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":450.07699,"mean_force":297.52699,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51668,0.14992,0.34202]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.54227,0.09849,0.27983],"force_p95":262.71489,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.75051,"mean_force":242.00122,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52534,0.1659,0.34767]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54209,0.09897,0.27961],"force_p95":206.94081,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.51859,"mean_force":137.58003,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52757,0.16455,0.35095]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.54333,0.09816,0.29756],"force_p95":149.97491,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.63498,"mean_force":117.0343,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52812,0.16443,0.37062]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.63075,0.01625,-0.0001],"force_p95":74.8213,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.57174,"mean_force":25.01272,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.39671,0.01611,0.14057]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62975,0.01632,-0.00025],"force_p95":88.41105,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.41105,"mean_force":88.41105,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39616,0.01617,0.14102]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63059,0.01627,-0.00013],"force_p95":81.80649,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.07684,"mean_force":71.73445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.39659,0.0161,0.14057]},{"body_a":"grasp_target","body_b":"hand","contact_count":46.0,"contact_point_centroid":[0.46062,0.03968,0.03988],"force_p95":3.97676,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.26668,"mean_force":1.72168,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38308,0.0065,0.05492]},{"body_a":"grasp_target","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.48772,0.0301,0.01186],"force_p95":0.85192,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.09889,"mean_force":0.47467,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37551,0.00644,0.0544]},{"body_a":"world","body_b":"grasp_target","contact_count":3894.0,"contact_point_centroid":[0.44754,0.04933,-0.00216],"force_p95":0.13834,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03395,"mean_force":0.14137,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40254,0.01,0.12772]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.44226,0.04938,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39616,0.01617,0.14102]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44226,0.04938,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.39659,0.0161,0.14057]},{"body_a":"world","body_b":"grasp_target","contact_count":1600.0,"contact_point_centroid":[0.44226,0.04938,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.41765,0.03255,0.1958]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.44226,0.04938,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49149,0.11815,0.30525]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.44226,0.04938,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52534,0.1659,0.34767]}],"total_contact_groups":24},"final_pose_error":0.10294,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44226,0.04938,0.01602],"final_tcp_position":[0.52807,0.16458,0.37071],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1377.70028,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":198.14251,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4880.0,"raw_peak_contact_force":1377.70028,"subtask_id":"approach_object","tcp_end":[0.39616,0.01617,0.14102],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13731,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.44226,0.04938,0.01602],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.31257,"object_z_max":0.01602,"peak_contact_force":144.20361,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":88.41105,"subtask_id":"grasp_object","tcp_end":[0.39616,0.01617,0.14101],"tcp_start":[0.39616,0.01617,0.14102],"tcp_to_object_dist_end":0.13729,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.44226,0.04938,0.01602],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.31257,"object_z_max":0.01602,"peak_contact_force":68.32987,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3496.0,"raw_peak_contact_force":85.07684,"tcp_end":[0.39668,0.01607,0.14041],"tcp_start":[0.39668,0.01607,0.14042],"tcp_to_object_dist_end":0.1366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":400.0,"n_steps_budget":960.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.44226,0.04938,0.01602],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.31257,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3282.0,"raw_peak_contact_force":90.57174,"subtask_id":"lift_object","tcp_end":[0.43672,0.04667,0.24416],"tcp_start":[0.43634,0.04624,0.24332],"tcp_to_object_dist_end":0.22823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.44226,0.04938,0.01602],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.31257,"object_z_max":0.01602,"peak_contact_force":256.24139,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4545.0,"raw_peak_contact_force":450.07699,"tcp_end":[0.52498,0.16608,0.34703],"tcp_start":[0.43672,0.04667,0.24416],"tcp_to_object_dist_end":0.3606,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.44226,0.04938,0.01602],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.31257,"object_z_max":0.01602,"peak_contact_force":274.27936,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":47.0,"raw_peak_contact_force":263.75051,"subtask_id":"place_at_goal","tcp_end":[0.52575,0.16584,0.34816],"tcp_start":[0.52498,0.16608,0.34703],"tcp_to_object_dist_end":0.36173,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.44226,0.04938,0.01602],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.31257,"object_z_max":0.01602,"peak_contact_force":74.27731,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1226.0,"raw_peak_contact_force":208.51859,"tcp_end":[0.52813,0.16443,0.37052],"tcp_start":[0.52575,0.16584,0.34816],"tcp_to_object_dist_end":0.38247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":660.0,"object_pos_end":[0.44226,0.04938,0.01602],"object_pos_start":[0.44226,0.04938,0.01602],"object_to_goal_dist_end":0.31257,"object_to_goal_dist_start":0.31257,"object_z_max":0.01602,"peak_contact_force":153.36209,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":10.0,"raw_peak_contact_force":153.63498,"tcp_end":[0.52807,0.16458,0.37071],"tcp_start":[0.52813,0.16443,0.37052],"tcp_to_object_dist_end":0.38268,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":217.0,"average_failure_rate":0.65758,"average_mean_iterations":135.01515,"average_solve_count":330.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.09357,"approach_pre_grasp.speed":0.12342,"descend_place.speed":0.02949,"descend_to_grasp.force_threshold":6.5565,"descend_to_grasp.speed":0.02798,"grasp.grasp_duration":1.09258,"lift.lift_height":0.1335,"lift.speed":0.03671,"release.release_duration":0.58439,"retract.speed":0.09272},"optimized_scores":{"best_composite_score":-0.41113,"best_fitness_score":0.14387,"best_task_score":0.10607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":859.0,"contact_point_centroid":[0.65237,-0.00816,-0.00044],"force_p95":464.34301,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1521.66424,"mean_force":236.66424,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.43018,-0.00867,0.15217]},{"body_a":"world","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.6859,-0.02824,-0.00012],"force_p95":495.61059,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":504.76304,"mean_force":355.57418,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46395,-0.00954,0.16191]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.68781,-0.05055,-0.00023],"force_p95":285.23432,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.47118,"mean_force":197.5405,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46389,-0.02779,0.16192]},{"body_a":"link5","body_b":"hand","contact_count":93.0,"contact_point_centroid":[0.5361,-0.02873,0.21113],"force_p95":257.35776,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.4258,"mean_force":218.7929,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51267,0.06398,0.24038]},{"body_a":"world","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.68869,-0.01713,-0.00013],"force_p95":71.08427,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.28015,"mean_force":67.40219,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46363,2e-05,0.16151]},{"body_a":"grasp_target","body_b":"link7","contact_count":175.0,"contact_point_centroid":[0.51212,-0.02531,0.03852],"force_p95":4.15933,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.59262,"mean_force":0.8853,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40166,-0.00448,0.09142]},{"body_a":"grasp_target","body_b":"hand","contact_count":158.0,"contact_point_centroid":[0.50467,-0.0305,0.0509],"force_p95":2.3738,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53405,"mean_force":0.88844,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40073,-0.00443,0.08879]},{"body_a":"world","body_b":"grasp_target","contact_count":3636.0,"contact_point_centroid":[0.50652,-0.02515,-0.00235],"force_p95":0.31409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44223,"mean_force":0.16115,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.44291,-0.00852,0.16423]},{"body_a":"grasp_target","body_b":"link6","contact_count":115.0,"contact_point_centroid":[0.54876,-0.0292,0.02208],"force_p95":0.63397,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68178,"mean_force":0.31764,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39761,-0.00439,0.0882]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.49912,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46373,-0.00147,0.16252]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49912,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46363,1e-05,0.16151]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.49912,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46402,-0.01093,0.16213]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.49912,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49174,0.02556,0.20598]},{"body_a":"world","body_b":"grasp_target","contact_count":32.0,"contact_point_centroid":[0.49912,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52526,0.09078,0.27012]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49912,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52486,0.09898,0.27783]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.49912,-0.02577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52503,0.09893,0.29865]}],"total_contact_groups":22},"final_pose_error":0.18828,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49912,-0.02577,0.01602],"final_tcp_position":[0.52542,0.09864,0.29984],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":10101.74218,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":81.32979,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4966.0,"raw_peak_contact_force":1521.66424,"subtask_id":"approach_object","tcp_end":[0.46373,-0.00163,0.16251],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15262,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.49912,-0.02577,0.01602],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.33656,"object_z_max":0.01602,"peak_contact_force":10101.74218,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.46374,-0.00104,0.16249],"tcp_start":[0.46373,-0.00163,0.16251],"tcp_to_object_dist_end":0.1527,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.49912,-0.02577,0.01602],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.33656,"object_z_max":0.01602,"peak_contact_force":85.10628,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3558.0,"raw_peak_contact_force":116.28015,"tcp_end":[0.46362,-3e-05,0.16141],"tcp_start":[0.46362,-3e-05,0.16141],"tcp_to_object_dist_end":0.15186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":36.0,"n_steps_budget":780.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.49912,-0.02577,0.01602],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.33656,"object_z_max":0.01602,"peak_contact_force":412.77173,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":329.0,"raw_peak_contact_force":504.76304,"subtask_id":"lift_object","tcp_end":[0.46382,-0.02664,0.16167],"tcp_start":[0.46423,-0.01836,0.16288],"tcp_to_object_dist_end":0.14987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.49912,-0.02577,0.01602],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.33656,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2951.0,"raw_peak_contact_force":302.47118,"tcp_end":[0.52454,0.08725,0.26717],"tcp_start":[0.46382,-0.02664,0.16167],"tcp_to_object_dist_end":0.27658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.49912,-0.02577,0.01602],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.33656,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":66.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.52588,0.09479,0.27366],"tcp_start":[0.52454,0.08725,0.26717],"tcp_to_object_dist_end":0.28571,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.49912,-0.02577,0.01602],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.33656,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5249,0.09899,0.29808],"tcp_start":[0.52588,0.09479,0.27366],"tcp_to_object_dist_end":0.3095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.49912,-0.02577,0.01602],"object_pos_start":[0.49912,-0.02577,0.01602],"object_to_goal_dist_end":0.33656,"object_to_goal_dist_start":0.33656,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":20.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52542,0.09864,0.29984],"tcp_start":[0.5249,0.09899,0.29808],"tcp_to_object_dist_end":0.31101,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```