## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4531 | 0.15 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.4782 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.3825 | 0.14 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4371 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0099 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.453) — your mutation base

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

- **Composite score**: -0.453
- **task_score** (E): 0.145
- **fitness_score**: 0.177  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 0.00 | 1.00 | 0.1874 |
| descend_to_grasp | 0.00 | 1.00 | 0.0252 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 0.67 | 1.00 | 0.0019 |
| approach_goal | 0.00 | 1.00 | 0.1295 |
| descend_place | 0.00 | 1.00 | 0.0254 |
| release | 1.00 | 1.00 | 0.0270 |
| retract | 0.00 | 1.00 | 0.0717 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.400, 0.004, 0.142) | (0.511, 0.022, 0.030)→(0.471, 0.025, 0.016) | 0.271→0.295 | 1.00 / 5.000 | 190.882 | 1349.436 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.400, 0.004, 0.142)→(0.424, 0.008, 0.136) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 5.000 | 269.390 | 385.211 |
| grasp | grasp | 1.00 / step_budget | (0.424, 0.008, 0.135)→(0.424, 0.008, 0.135) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 9.000 | 73.235 | 84.865 |
| lift | lift | 0.67 / step_budget | (0.452, 0.025, 0.156)→(0.453, 0.027, 0.156) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 8.667 | 325.097 | 398.772 |
| approach_goal | approach | 0.00 / step_budget | (0.453, 0.027, 0.156)→(0.492, 0.085, 0.257) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 8.333 | 91000.273 | 526.177 |
| descend_place | descend | 0.00 / step_budget | (0.492, 0.085, 0.257)→(0.491, 0.073, 0.278) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 9.000 | 94.506 | 120.805 |
| release | release | 1.00 / step_budget | (0.491, 0.073, 0.278)→(0.490, 0.074, 0.305) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 4.333 | 34.268 | 110.703 |
| retract | retract | 0.00 / step_budget | (0.490, 0.074, 0.305)→(0.504, 0.090, 0.373) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 4.667 | 106.592 | 295.890 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.205
- phase_score: 0.116
- phase_breakdown.approach_object_score: 0.092
- phase_breakdown.grasp_object_score: 0.078
- phase_breakdown.lift_object_score: 0.339
- phase_breakdown.place_at_goal_score: 0.015
- grasp_place_fitness: 0.206

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.206
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.205
- **Median Q (composite search score)**: -0.452
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":287.0,"average_failure_rate":0.60042,"average_mean_iterations":123.25732,"average_solve_count":478.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.06299,"approach_pre_grasp.speed":0.02041,"descend_place.speed":0.03355,"descend_to_grasp.speed":0.02383,"grasp.grasp_duration":0.82195,"lift.lift_height":0.12714,"lift.speed":0.02199,"release.release_duration":0.57135,"retract.speed":0.03998},"optimized_scores":{"best_composite_score":-0.42438,"best_fitness_score":0.20562,"best_task_score":0.2048},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63582,0.00573,-0.00047],"force_p95":195.5268,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1430.78339,"mean_force":199.91035,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39251,0.0054,0.11944]},{"body_a":"link5","body_b":"hand","contact_count":81.0,"contact_point_centroid":[0.53723,0.02319,0.2299],"force_p95":622.61542,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":760.88118,"mean_force":388.74137,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49377,0.09825,0.27801]},{"body_a":"world","body_b":"link6","contact_count":59.0,"contact_point_centroid":[0.67401,0.02238,-5e-05],"force_p95":580.33202,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":627.8177,"mean_force":259.35594,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43628,0.02396,0.13596]},{"body_a":"world","body_b":"link6","contact_count":19.0,"contact_point_centroid":[0.69137,0.07011,-0.00015],"force_p95":365.20218,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.06439,"mean_force":293.264,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4628,0.05369,0.16246]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.64497,0.00987,-0.0003],"force_p95":291.77078,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.05797,"mean_force":266.15869,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41184,0.01058,0.14158]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.70418,0.0496,-7e-05],"force_p95":356.53822,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.16943,"mean_force":305.85732,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.46171,0.04813,0.13489]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.7035,0.04555,-0.0001],"force_p95":286.31806,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.18285,"mean_force":203.92,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46107,0.04639,0.1349]},{"body_a":"world","body_b":"link6","contact_count":125.0,"contact_point_centroid":[0.70217,0.05215,-6e-05],"force_p95":70.57878,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.4272,"mean_force":64.12276,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.46156,0.04812,0.13795]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.65869,0.01246,-0.00013],"force_p95":81.22817,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.46568,"mean_force":70.31044,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42081,0.01317,0.13391]},{"body_a":"grasp_target","body_b":"link7","contact_count":318.0,"contact_point_centroid":[0.49415,0.02262,0.0391],"force_p95":1.41285,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.52632,"mean_force":0.48514,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38879,0.0041,0.09967]},{"body_a":"grasp_target","body_b":"hand","contact_count":288.0,"contact_point_centroid":[0.48479,0.0238,0.0532],"force_p95":2.09007,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.6024,"mean_force":0.46561,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38858,0.00404,0.09788]},{"body_a":"world","body_b":"grasp_target","contact_count":3303.0,"contact_point_centroid":[0.48209,0.0468,-0.0028],"force_p95":0.3856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.40837,"mean_force":0.1903,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.4074,0.00529,0.13342]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47066,0.04877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41184,0.01058,0.14158]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47066,0.04877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42081,0.01317,0.13391]},{"body_a":"world","body_b":"grasp_target","contact_count":616.0,"contact_point_centroid":[0.47066,0.04877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44151,0.0276,0.13631]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.47066,0.04877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46121,0.04663,0.13496]}],"total_contact_groups":25},"final_pose_error":0.16597,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.47066,0.04877,0.01602],"final_tcp_position":[0.49912,0.09705,0.36818],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1430.78339,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":190.94121,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4816.0,"raw_peak_contact_force":1430.78339,"subtask_id":"approach_object","tcp_end":[0.39794,0.00769,0.14236],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15146,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.47066,0.04877,0.01602],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.23786,"object_z_max":0.01602,"peak_contact_force":257.49402,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":373.05797,"subtask_id":"grasp_object","tcp_end":[0.42037,0.0132,0.13434],"tcp_start":[0.39794,0.00769,0.14236],"tcp_to_object_dist_end":0.1334,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.47066,0.04877,0.01602],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.23786,"object_z_max":0.01602,"peak_contact_force":67.11231,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3508.0,"raw_peak_contact_force":85.46568,"tcp_end":[0.42088,0.01314,0.13375],"tcp_start":[0.42088,0.01314,0.13375],"tcp_to_object_dist_end":0.13269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.47066,0.04877,0.01602],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.23786,"object_z_max":0.01602,"peak_contact_force":627.8177,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1321.0,"raw_peak_contact_force":627.8177,"subtask_id":"lift_object","tcp_end":[0.46096,0.04587,0.13498],"tcp_start":[0.4588,0.04214,0.135],"tcp_to_object_dist_end":0.11939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.47066,0.04877,0.01602],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.23786,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":54.0,"raw_peak_contact_force":299.18285,"tcp_end":[0.46168,0.04751,0.13517],"tcp_start":[0.46096,0.04587,0.13498],"tcp_to_object_dist_end":0.11949,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.47066,0.04877,0.01602],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.23786,"object_z_max":0.01602,"peak_contact_force":283.27191,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":43.0,"raw_peak_contact_force":362.16943,"subtask_id":"place_at_goal","tcp_end":[0.46188,0.04821,0.13477],"tcp_start":[0.46168,0.04751,0.13517],"tcp_to_object_dist_end":0.11907,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.47066,0.04877,0.01602],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.23786,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1151.0,"raw_peak_contact_force":229.4272,"tcp_end":[0.45949,0.04804,0.16338],"tcp_start":[0.46188,0.04821,0.13477],"tcp_to_object_dist_end":0.14778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.47066,0.04877,0.01602],"object_pos_start":[0.47066,0.04877,0.01602],"object_to_goal_dist_end":0.23786,"object_to_goal_dist_start":0.23786,"object_z_max":0.01602,"peak_contact_force":197.59336,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":796.0,"raw_peak_contact_force":760.88118,"tcp_end":[0.49912,0.09705,0.36818],"tcp_start":[0.45949,0.04804,0.16338],"tcp_to_object_dist_end":0.3566,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":122.0,"average_failure_rate":0.4311,"average_mean_iterations":89.18375,"average_solve_count":283.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.10954,"approach_pre_grasp.speed":0.03384,"descend_place.speed":0.02933,"descend_to_grasp.speed":0.02882,"grasp.grasp_duration":1.30555,"lift.lift_height":0.17881,"lift.speed":0.0593,"release.release_duration":0.50124,"retract.speed":0.09538},"optimized_scores":{"best_composite_score":-0.45235,"best_fitness_score":0.17765,"best_task_score":0.12441},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63467,0.00784,-0.00046],"force_p95":196.50908,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1301.28998,"mean_force":200.38723,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38906,0.00736,0.1144]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52698,0.0095,-0.00308],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1204.92059,"mean_force":54.76912,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37482,0.00479,0.04913]},{"body_a":"link5","body_b":"hand","contact_count":21.0,"contact_point_centroid":[0.54133,0.06177,0.2431],"force_p95":620.00231,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":663.96358,"mean_force":386.33601,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50106,0.153,0.26268]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.64514,0.01344,-0.00031],"force_p95":301.02734,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":398.27658,"mean_force":282.35503,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.40728,0.01417,0.13348]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.55181,0.06989,0.26742],"force_p95":126.15145,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.66508,"mean_force":95.48074,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50259,0.16349,0.29042]},{"body_a":"link5","body_b":"hand","contact_count":105.0,"contact_point_centroid":[0.55007,0.06727,0.25197],"force_p95":102.44112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.55974,"mean_force":85.51275,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.50171,0.1615,0.27506]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.65992,0.01677,-0.0001],"force_p95":77.64211,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.13817,"mean_force":27.74923,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.41707,0.01757,0.12476]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.65978,0.01674,-0.00013],"force_p95":80.9277,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.62199,"mean_force":69.84637,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41696,0.0175,0.12474]},{"body_a":"grasp_target","body_b":"hand","contact_count":46.0,"contact_point_centroid":[0.46016,0.03855,0.03997],"force_p95":3.94792,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.25168,"mean_force":1.70967,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.3832,0.00486,0.05477]},{"body_a":"world","body_b":"grasp_target","contact_count":3898.0,"contact_point_centroid":[0.44759,0.04919,-0.00215],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60888,"mean_force":0.14092,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40148,0.00699,0.1252]},{"body_a":"grasp_target","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.48784,0.03019,0.01199],"force_p95":0.75726,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.7801,"mean_force":0.39411,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.3752,0.00482,0.05382]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44235,0.04922,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.40728,0.01417,0.13348]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44235,0.04922,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41696,0.0175,0.12474]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.44235,0.04922,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4272,0.03274,0.15425]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.44235,0.04922,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47495,0.10166,0.22644]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.44235,0.04922,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5024,0.15912,0.26595]}],"total_contact_groups":23},"final_pose_error":0.13613,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44235,0.04922,0.01602],"final_tcp_position":[0.50273,0.16364,0.29095],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":272985.22119,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":193.08336,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4881.0,"raw_peak_contact_force":1301.28998,"subtask_id":"approach_object","tcp_end":[0.39332,0.01064,0.13521],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13453,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.44235,0.04922,0.01602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31262,"object_z_max":0.01602,"peak_contact_force":273.2092,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":398.27658,"subtask_id":"grasp_object","tcp_end":[0.41647,0.01753,0.12525],"tcp_start":[0.39332,0.01064,0.13521],"tcp_to_object_dist_end":0.11664,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.44235,0.04922,0.01602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31262,"object_z_max":0.01602,"peak_contact_force":85.1493,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":85.62199,"tcp_end":[0.41704,0.01747,0.12457],"tcp_start":[0.41704,0.01748,0.12458],"tcp_to_object_dist_end":0.1159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":258.0,"n_steps_budget":870.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.44235,0.04922,0.01602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31262,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2122.0,"raw_peak_contact_force":92.13817,"subtask_id":"lift_object","tcp_end":[0.43613,0.04512,0.17902],"tcp_start":[0.43597,0.04445,0.1783],"tcp_to_object_dist_end":0.16317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.44235,0.04922,0.01602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31262,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2627.0,"raw_peak_contact_force":663.96358,"tcp_end":[0.5023,0.15918,0.26573],"tcp_start":[0.43613,0.04512,0.17902],"tcp_to_object_dist_end":0.27935,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.44235,0.04922,0.01602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31262,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.50255,0.15921,0.26651],"tcp_start":[0.5023,0.15918,0.26573],"tcp_to_object_dist_end":0.28013,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.44235,0.04922,0.01602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31262,"object_z_max":0.01602,"peak_contact_force":102.55974,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1129.0,"raw_peak_contact_force":102.55974,"tcp_end":[0.50256,0.16345,0.2902],"tcp_start":[0.50255,0.15921,0.26651],"tcp_to_object_dist_end":0.30307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":900.0,"object_pos_end":[0.44235,0.04922,0.01602],"object_pos_start":[0.44235,0.04922,0.01602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31262,"object_z_max":0.01602,"peak_contact_force":122.05948,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":15.0,"raw_peak_contact_force":126.66508,"tcp_end":[0.50273,0.16364,0.29095],"tcp_start":[0.50256,0.16345,0.2902],"tcp_to_object_dist_end":0.30385,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":207.0,"average_failure_rate":0.65714,"average_mean_iterations":134.68889,"average_solve_count":315.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.06443,"approach_pre_grasp.speed":0.03424,"descend_place.speed":0.03758,"descend_to_grasp.speed":0.02435,"grasp.grasp_duration":1.0781,"lift.lift_height":0.08111,"lift.speed":0.07111,"release.release_duration":0.5313,"retract.speed":0.11011},"optimized_scores":{"best_composite_score":-0.48271,"best_fitness_score":0.14729,"best_task_score":0.10727},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.64283,-0.00376,-0.00045],"force_p95":196.58019,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1316.23492,"mean_force":197.04598,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.4007,-0.00372,0.12053]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53583,0.00099,-0.00308],"force_p95":358.31484,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1232.87295,"mean_force":70.91307,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38321,-0.00263,0.0484]},{"body_a":"world","body_b":"link5","contact_count":103.0,"contact_point_centroid":[0.65505,0.10243,-0.00073],"force_p95":420.50913,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":615.38447,"mean_force":183.75925,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49313,-0.02777,0.17877]},{"body_a":"world","body_b":"link6","contact_count":123.0,"contact_point_centroid":[0.6753,-0.00923,-9e-05],"force_p95":436.94856,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":476.35983,"mean_force":281.26296,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45157,-0.00947,0.15715]},{"body_a":"link5","body_b":"hand","contact_count":112.0,"contact_point_centroid":[0.51912,0.07787,0.13918],"force_p95":305.66399,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":455.72611,"mean_force":174.73227,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48799,-0.02091,0.17877]},{"body_a":"world","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.69302,-0.01314,-8e-05],"force_p95":451.72147,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":454.11395,"mean_force":352.1424,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46356,-0.00999,0.15351]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.65144,-0.00601,-0.00029],"force_p95":278.21638,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.29811,"mean_force":257.897,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42527,-0.0067,0.15248]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.66483,-0.00734,-0.00013],"force_p95":76.47849,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.50655,"mean_force":69.7322,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.43485,-0.00793,0.14705]},{"body_a":"grasp_target","body_b":"link7","contact_count":588.0,"contact_point_centroid":[0.52495,-0.01146,0.03234],"force_p95":0.82819,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.92812,"mean_force":0.31543,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39799,-0.00317,0.10852]},{"body_a":"grasp_target","body_b":"hand","contact_count":138.0,"contact_point_centroid":[0.49684,-0.02811,0.04728],"force_p95":2.19341,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.83041,"mean_force":0.88851,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39206,-0.00266,0.08098]},{"body_a":"world","body_b":"grasp_target","contact_count":3709.0,"contact_point_centroid":[0.50698,-0.02388,-0.00245],"force_p95":0.32477,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21288,"mean_force":0.16722,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.41336,-0.00353,0.13266]},{"body_a":"grasp_target","body_b":"link6","contact_count":119.0,"contact_point_centroid":[0.54377,-0.02641,0.02554],"force_p95":0.77186,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89745,"mean_force":0.35501,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38982,-0.00266,0.08379]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50048,-0.02411,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42527,-0.0067,0.15248]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50048,-0.02411,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.43485,-0.00793,0.14705]},{"body_a":"world","body_b":"grasp_target","contact_count":544.0,"contact_point_centroid":[0.50048,-0.02411,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45214,-0.00953,0.15721]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50048,-0.02411,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50242,0.02242,0.27066]}],"total_contact_groups":24},"final_pose_error":0.26205,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50048,-0.02411,0.01602],"final_tcp_position":[0.50939,0.0093,0.46117],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273000.57509,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":188.62163,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5463.0,"raw_peak_contact_force":1316.23492,"subtask_id":"approach_object","tcp_end":[0.40951,-0.00538,0.1494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16253,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.50048,-0.02411,0.01602],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.33486,"object_z_max":0.01602,"peak_contact_force":277.46824,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":384.29811,"subtask_id":"grasp_object","tcp_end":[0.43448,-0.00787,0.14751],"tcp_start":[0.40951,-0.00538,0.1494],"tcp_to_object_dist_end":0.14802,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.50048,-0.02411,0.01602],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.33486,"object_z_max":0.01602,"peak_contact_force":67.44326,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3497.0,"raw_peak_contact_force":83.50655,"tcp_end":[0.4349,-0.00796,0.14691],"tcp_start":[0.4349,-0.00796,0.14691],"tcp_to_object_dist_end":0.14729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":136.0,"n_steps_budget":750.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.50048,-0.02411,0.01602],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.33486,"object_z_max":0.01602,"peak_contact_force":347.35181,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1244.0,"raw_peak_contact_force":476.35983,"subtask_id":"lift_object","tcp_end":[0.46287,-0.01063,0.15441],"tcp_start":[0.46261,-0.01087,0.15481],"tcp_to_object_dist_end":0.14404,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.50048,-0.02411,0.01602],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.33486,"object_z_max":0.01602,"peak_contact_force":273000.57509,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8580.0,"raw_peak_contact_force":615.38447,"tcp_end":[0.5116,0.04969,0.36961],"tcp_start":[0.46287,-0.01063,0.15441],"tcp_to_object_dist_end":0.36138,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.50048,-0.02411,0.01602],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.33486,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":542.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.50746,0.01017,0.43284],"tcp_start":[0.5116,0.04969,0.36961],"tcp_to_object_dist_end":0.41828,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.50048,-0.02411,0.01602],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.33486,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1043.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5094,0.00929,0.46101],"tcp_start":[0.50746,0.01017,0.43284],"tcp_to_object_dist_end":0.44633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50048,-0.02411,0.01602],"object_pos_start":[0.50048,-0.02411,0.01602],"object_to_goal_dist_end":0.33486,"object_to_goal_dist_start":0.33486,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50939,0.0093,0.46117],"tcp_start":[0.5094,0.00929,0.46101],"tcp_to_object_dist_end":0.44649,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```