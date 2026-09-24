## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0682 | 0.30 | ❌ rejected |
| 1 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0773 | 0.32 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.3457 | 0.14 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.068) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.4
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_object
- id: descend_1
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
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
    orientation:
      mode: keep_current
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: lift_1
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
    - 0.2
    tolerance: 0.02
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
  subtask_id: lift_object
- id: transport_1
  type: push
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
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    transport_xy_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    transport_xy_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    transport_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  guards:
  - id: object_held
    when: during_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: abort
  subtask_id: approach_goal
- id: release_1
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
    orientation:
      mode: keep_current
  parameters:
    place_delay:
      type: scalar
      range:
      - 0.0
      - 0.5
      default: 0.1
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: place_at_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.03
      - 0.2
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)
    - transport_z_offset: status=consumed; consumers=target.offset.z (add)
  - guards:
    - id=object_held, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.01
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_delay: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.068
- **task_score** (E): 0.295
- **fitness_score**: 0.618  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0768 |
| descend_1 | 1.00 | 1.00 | 0.1896 |
| grasp_1 | 1.00 | 1.00 | 0.0138 |
| lift_1 | 1.00 | 1.00 | 0.1463 |
| transport_1 | 0.67 | 1.00 | 0.2111 |
| release_1 | 1.00 | 1.00 | 0.0205 |
| retract_1 | 1.00 | 1.00 | 0.1009 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.002, 0.237) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.515, -0.002, 0.237)→(0.517, -0.001, 0.048) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.048)→(0.507, -0.001, 0.037) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 42.000 | 0.160 | 0.215 |
| lift_1 | lift | 1.00 / step_budget | (0.507, -0.001, 0.037)→(0.517, -0.001, 0.183) | (0.522, -0.001, 0.025)→(0.533, -0.001, 0.163) | 0.290→0.226 | 1.00 / 21.667 | 0.116 | 0.485 |
| transport_1 | approach | 0.67 / step_budget | (0.517, -0.001, 0.183)→(0.599, 0.192, 0.186) | (0.533, -0.001, 0.163)→(0.610, 0.200, 0.106) | 0.226→0.104 | 1.00 / 12.667 | 0.132 | 0.779 |
| release_1 | release | 1.00 / step_budget | (0.599, 0.190, 0.186)→(0.594, 0.188, 0.205) | (0.603, 0.190, 0.151)→(0.589, 0.188, 0.023) | 0.060→0.183 | 1.00 / 3.000 | 0.217 | 1.506 |
| retract_1 | retract | 1.00 / step_budget | (0.594, 0.188, 0.205)→(0.592, 0.188, 0.306) | (0.589, 0.188, 0.023)→(0.579, 0.187, 0.026) | 0.183→0.182 | 1.00 / 4.000 | 0.123 | 0.224 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.366
- phase_score: 0.589
- phase_breakdown.approach_goal_score: 0.575
- phase_breakdown.reach_above_object_score: 0.053
- phase_breakdown.reach_object_score: 0.726
- phase_breakdown.lift_object_score: 0.644
- phase_breakdown.place_at_goal_score: 0.768
- grasp_place_fitness: 0.655

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.655
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.366
- **Median Q (composite search score)**: 0.055
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.436


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98788,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23865,"descend_1.grasp_offset_z":0.00031,"lift_1.lift_height":0.21951,"release_1.place_delay":0.15119,"retract_1.retract_height":0.12407,"transport_1.transport_speed":0.17924,"transport_1.transport_xy_offset_x":-0.02323,"transport_1.transport_xy_offset_y":0.00703},"optimized_scores":{"best_composite_score":0.04464,"best_fitness_score":0.59464,"best_task_score":0.24237},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.53136,0.21407,-0.00919],"force_p95":1.42901,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79501,"mean_force":0.47359,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54233,0.21663,0.22931]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.48079,0.04541,-0.00154],"force_p95":0.44717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50776,"mean_force":0.09961,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46911,0.04567,0.03814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8249.0,"contact_point_centroid":[0.47408,0.06511,0.12173],"force_p95":0.11351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28831,"mean_force":0.07455,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47194,0.04591,0.11935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6468.0,"contact_point_centroid":[0.52912,0.18064,0.22016],"force_p95":0.12252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26981,"mean_force":0.09538,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52496,0.1618,0.22072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10512.0,"contact_point_centroid":[0.47546,0.02734,0.11919],"force_p95":0.10114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26324,"mean_force":0.06075,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47186,0.0459,0.11819]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48285,0.04861,-0.00226],"force_p95":0.1923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25671,"mean_force":0.14158,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47146,0.0459,0.03748]},{"body_a":"world","body_b":"grasp_target","contact_count":1415.0,"contact_point_centroid":[0.52746,0.21221,-0.00212],"force_p95":0.20543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25018,"mean_force":0.12663,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54055,0.21575,0.29095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7247.0,"contact_point_centroid":[0.5285,0.1362,0.219],"force_p95":0.13033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2447,"mean_force":0.08767,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52182,0.15408,0.22093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5223.0,"contact_point_centroid":[0.47166,0.02682,0.03749],"force_p95":0.06544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20402,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47029,0.04579,0.03629]},{"body_a":"world","body_b":"grasp_target","contact_count":364.0,"contact_point_centroid":[0.4827,0.04873,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12406,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49362,0.01393,0.28859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":483.0,"contact_point_centroid":[0.54939,0.19992,0.20696],"force_p95":0.13654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13754,"mean_force":0.0993,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54526,0.21801,0.21157]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48223,0.03852,0.16119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.5476,0.23634,0.20725],"force_p95":0.11198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11533,"mean_force":0.07932,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5453,0.21803,0.21165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4102.0,"contact_point_centroid":[0.4702,0.06521,0.03855],"force_p95":0.09189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09761,"mean_force":0.05443,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4703,0.04579,0.0363]}],"total_contact_groups":14},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52612,0.21209,0.02602],"final_tcp_position":[0.54101,0.21585,0.34051],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.79501,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.026],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28999,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12212,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.48698,0.03069,0.27574],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.026],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28999,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.47902,0.04657,0.04547],"tcp_start":[0.48698,0.03069,0.27574],"tcp_to_object_dist_end":0.01991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48282,0.04692,0.0251],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29171,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18611,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11125.0,"raw_peak_contact_force":0.25671,"subtask_id":"reach_object","tcp_end":[0.47026,0.04579,0.03626],"tcp_start":[0.47902,0.04657,0.04547],"tcp_to_object_dist_end":0.01684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.49415,0.04801,0.20373],"object_pos_start":[0.48282,0.04692,0.0251],"object_to_goal_dist_end":0.20277,"object_to_goal_dist_start":0.29171,"object_z_max":0.20348,"peak_contact_force":0.12029,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18845.0,"raw_peak_contact_force":0.50776,"subtask_id":"lift_object","tcp_end":[0.47898,0.04653,0.22519],"tcp_start":[0.47026,0.04579,0.03626],"tcp_to_object_dist_end":0.02633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.5503,0.21938,0.1799],"object_pos_start":[0.49415,0.04801,0.20373],"object_to_goal_dist_end":0.06038,"object_to_goal_dist_start":0.20277,"object_z_max":0.20394,"peak_contact_force":0.13645,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13715.0,"raw_peak_contact_force":0.26981,"subtask_id":"approach_goal","tcp_end":[0.54673,0.21862,0.21504],"tcp_start":[0.47898,0.04653,0.22519],"tcp_to_object_dist_end":0.03533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53955,0.21827,0.02025],"object_pos_start":[0.5503,0.21938,0.1799],"object_to_goal_dist_end":0.21472,"object_to_goal_dist_start":0.06038,"object_z_max":0.1799,"peak_contact_force":0.25745,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1243.0,"raw_peak_contact_force":1.79501,"subtask_id":"place_at_goal","tcp_end":[0.5423,0.21662,0.23637],"tcp_start":[0.54673,0.21862,0.21504],"tcp_to_object_dist_end":0.21614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":780.0,"object_pos_end":[0.52612,0.21209,0.02602],"object_pos_start":[0.53955,0.21827,0.02025],"object_to_goal_dist_end":0.21259,"object_to_goal_dist_start":0.21472,"object_z_max":0.02888,"peak_contact_force":0.12267,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1415.0,"raw_peak_contact_force":0.25018,"tcp_end":[0.54101,0.21585,0.34051],"tcp_start":[0.5423,0.21662,0.23637],"tcp_to_object_dist_end":0.31486,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06306,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11202,"descend_1.grasp_offset_z":0.008,"lift_1.lift_height":0.15935,"release_1.place_delay":0.24081,"retract_1.retract_height":0.13643,"transport_1.transport_speed":0.35985,"transport_1.transport_xy_offset_x":0.00232,"transport_1.transport_xy_offset_y":-0.00521},"optimized_scores":{"best_composite_score":0.05503,"best_fitness_score":0.60503,"best_task_score":0.27798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1553.0,"contact_point_centroid":[0.62405,0.22037,-0.00269],"force_p95":0.29205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67851,"mean_force":0.15365,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59871,0.19676,0.1872]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5351,-0.02086,-0.00135],"force_p95":0.38,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42411,"mean_force":0.09053,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52088,-0.02053,0.04305]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4714.0,"contact_point_centroid":[0.56679,0.05639,0.17625],"force_p95":0.14878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3771,"mean_force":0.09591,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56102,0.07516,0.17613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5590.0,"contact_point_centroid":[0.52775,-0.03971,0.09901],"force_p95":0.11303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2819,"mean_force":0.07897,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52434,-0.02069,0.09668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6687.0,"contact_point_centroid":[0.52809,-0.00209,0.0967],"force_p95":0.10672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27154,"mean_force":0.06896,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52422,-0.02069,0.09538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5549.0,"contact_point_centroid":[0.56624,0.08932,0.1745],"force_p95":0.12751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22489,"mean_force":0.08341,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55975,0.07121,0.17558]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02133,-0.00206],"force_p95":0.14063,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17627,"mean_force":0.12752,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5232,-0.02056,0.04315]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51299,-0.00873,0.23083]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52866,-0.01936,0.10653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5304.0,"contact_point_centroid":[0.52305,-0.0015,0.04412],"force_p95":0.06685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10838,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52197,-0.02054,0.04173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4179.0,"contact_point_centroid":[0.52302,-0.03984,0.04441],"force_p95":0.08059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0813,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52197,-0.02054,0.04173]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1407.0,"contact_point_centroid":[0.59922,0.19658,0.18884],"force_p95":0.01203,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01515,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59849,0.19655,0.18659]}],"total_contact_groups":12},"final_pose_error":0.0297,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62415,0.22046,0.01602],"final_tcp_position":[0.60198,0.19774,0.19502],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.67851,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52821,-0.01813,0.15935],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53105,-0.02064,0.05258],"tcp_start":[0.52821,-0.01813,0.15935],"tcp_to_object_dist_end":0.02723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02104,0.02576],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31666,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13982,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11283.0,"raw_peak_contact_force":0.17627,"subtask_id":"reach_object","tcp_end":[0.52194,-0.02054,0.04169],"tcp_start":[0.53105,-0.02064,0.05258],"tcp_to_object_dist_end":0.0219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":432.0,"n_steps_budget":900.0,"object_pos_end":[0.547,-0.02174,0.14259],"object_pos_start":[0.53695,-0.02104,0.02576],"object_to_goal_dist_end":0.26544,"object_to_goal_dist_start":0.31666,"object_z_max":0.14235,"peak_contact_force":0.11957,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12357.0,"raw_peak_contact_force":0.42411,"subtask_id":"lift_object","tcp_end":[0.53181,-0.02094,0.16591],"tcp_start":[0.52194,-0.02054,0.04169],"tcp_to_object_dist_end":0.02784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.62415,0.22046,0.01602],"object_pos_start":[0.547,-0.02174,0.14259],"object_to_goal_dist_end":0.19203,"object_to_goal_dist_start":0.26544,"object_z_max":0.15476,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13223.0,"raw_peak_contact_force":1.67851,"subtask_id":"approach_goal","tcp_end":[0.59838,0.19646,0.18631],"tcp_start":[0.53181,-0.02094,0.16591],"tcp_to_object_dist_end":0.1739,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95918,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24183,"descend_1.grasp_offset_z":0.00033,"lift_1.lift_height":0.15228,"release_1.place_delay":0.12652,"retract_1.retract_height":0.11755,"transport_1.transport_speed":0.49865,"transport_1.transport_xy_offset_x":0.03269,"transport_1.transport_xy_offset_y":0.01061},"optimized_scores":{"best_composite_score":0.10503,"best_fitness_score":0.65503,"best_task_score":0.36554},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.64059,0.15915,-0.00625],"force_p95":1.04218,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21727,"mean_force":0.35058,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64482,0.16002,0.16379]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.54366,-0.02766,-0.00139],"force_p95":0.42535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52204,"mean_force":0.09483,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52912,-0.02795,0.03555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7297.0,"contact_point_centroid":[0.61615,0.07395,0.16045],"force_p95":0.13443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3885,"mean_force":0.09729,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61138,0.0927,0.16007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5385.0,"contact_point_centroid":[0.53665,-0.04715,0.09319],"force_p95":0.11302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33853,"mean_force":0.08245,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5329,-0.02814,0.09093]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8671.0,"contact_point_centroid":[0.61678,0.10883,0.15914],"force_p95":0.13164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28842,"mean_force":0.08511,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.6102,0.09079,0.15997]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6467.0,"contact_point_centroid":[0.53694,-0.00965,0.08918],"force_p95":0.11003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28108,"mean_force":0.07152,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5326,-0.02813,0.08807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54568,-0.02924,-0.00211],"force_p95":0.15487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21188,"mean_force":0.13111,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53146,-0.028,0.0355]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.63212,0.16085,-0.00198],"force_p95":0.15931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19761,"mean_force":0.12349,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.64216,0.15921,0.22294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4796.0,"contact_point_centroid":[0.53213,-0.00908,0.03542],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15925,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53021,-0.02797,0.03405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":515.0,"contact_point_centroid":[0.65429,0.17905,0.14647],"force_p95":0.13676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1392,"mean_force":0.09331,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64881,0.16119,0.1516]},{"body_a":"world","body_b":"grasp_target","contact_count":424.0,"contact_point_centroid":[0.5456,-0.02923,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1238,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51354,-0.00924,0.28828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":481.0,"contact_point_centroid":[0.65325,0.1429,0.14825],"force_p95":0.13374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13485,"mean_force":0.09682,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64892,0.16122,0.15182]},{"body_a":"world","body_b":"grasp_target","contact_count":1716.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53319,-0.02387,0.16109]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4055.0,"contact_point_centroid":[0.53152,-0.04723,0.0371],"force_p95":0.0908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09505,"mean_force":0.05574,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53021,-0.02797,0.03405]}],"total_contact_groups":14},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63194,0.16099,0.02602],"final_tcp_position":[0.64254,0.15926,0.27197],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.21727,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12236,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52884,-0.01969,0.27577],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1716.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.53951,-0.02817,0.04522],"tcp_start":[0.52884,-0.01969,0.27577],"tcp_to_object_dist_end":0.02018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54567,-0.0286,0.0256],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26067,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15356,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10651.0,"raw_peak_contact_force":0.21188,"subtask_id":"reach_object","tcp_end":[0.53018,-0.02797,0.03401],"tcp_start":[0.53951,-0.02817,0.04522],"tcp_to_object_dist_end":0.01764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":436.0,"n_steps_budget":900.0,"object_pos_end":[0.55775,-0.02907,0.14134],"object_pos_start":[0.54567,-0.0286,0.0256],"object_to_goal_dist_end":0.21104,"object_to_goal_dist_start":0.26067,"object_z_max":0.14111,"peak_contact_force":0.10753,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11935.0,"raw_peak_contact_force":0.52204,"subtask_id":"lift_object","tcp_end":[0.54039,-0.02845,0.15863],"tcp_start":[0.53018,-0.02797,0.03401],"tcp_to_object_dist_end":0.0245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.65523,0.16148,0.12155],"object_pos_start":[0.55775,-0.02907,0.14134],"object_to_goal_dist_end":0.05983,"object_to_goal_dist_start":0.21104,"object_z_max":0.14157,"peak_contact_force":0.13618,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15968.0,"raw_peak_contact_force":0.3885,"subtask_id":"approach_goal","tcp_end":[0.6508,0.16174,0.15615],"tcp_start":[0.54039,-0.02845,0.15863],"tcp_to_object_dist_end":0.03489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63821,0.15858,0.02662],"object_pos_start":[0.65523,0.16148,0.12155],"object_to_goal_dist_end":0.15053,"object_to_goal_dist_start":0.05983,"object_z_max":0.12155,"peak_contact_force":0.17679,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1190.0,"raw_peak_contact_force":1.21727,"subtask_id":"place_at_goal","tcp_end":[0.64477,0.16,0.17425],"tcp_start":[0.6508,0.16174,0.15615],"tcp_to_object_dist_end":0.14778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":750.0,"object_pos_end":[0.63194,0.16099,0.02602],"object_pos_start":[0.63821,0.15858,0.02662],"object_to_goal_dist_end":0.15096,"object_to_goal_dist_start":0.15053,"object_z_max":0.02679,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.19761,"tcp_end":[0.64254,0.15926,0.27197],"tcp_start":[0.64477,0.16,0.17425],"tcp_to_object_dist_end":0.24618,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```