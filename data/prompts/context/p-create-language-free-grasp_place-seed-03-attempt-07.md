## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3120 | 0.36 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.1582 | 0.24 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1127 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1085 | 0.24 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | -0.0692 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605988) | final destination targets |
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

## Current Skill (Q=0.312) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_objective
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: placement_objective
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_objective
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
- id: grasp
  type: grasp
  control: impedance_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
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
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_held
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: placement_objective
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
- id: retract
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_held, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.312
- **task_score** (E): 0.357
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2168 |
| descend_to_grasp | 1.00 | 1.00 | 0.0341 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.1075 |
| transport_to_goal | 0.67 | 1.00 | 0.0018 |
| descend_to_place | 1.00 | 1.00 | 0.1105 |
| release | 1.00 | 1.00 | 0.0200 |
| retract | 1.00 | 1.00 | 0.0846 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.054) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.054)→(0.497, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.142 | 0.189 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.045)→(0.494, 0.002, 0.152) | (0.511, 0.002, 0.026)→(0.505, 0.001, 0.125) | 0.246→0.223 | 1.00 / 23.000 | 0.117 | 0.433 |
| transport_to_goal | approach | 0.67 / step_budget | (0.622, 0.179, 0.257)→(0.623, 0.180, 0.257) | (0.505, 0.001, 0.125)→(0.564, 0.112, 0.015) | 0.223→0.165 | 1.00 / 8.333 | 0.123 | 1.522 |
| descend_to_place | descend | 1.00 / step_budget | (0.623, 0.180, 0.257)→(0.622, 0.180, 0.146) | (0.565, 0.113, 0.016)→(0.565, 0.113, 0.016) | 0.164→0.164 | 1.00 / 8.000 | 6499.270 | 0.123 |
| release | release | 1.00 / step_budget | (0.622, 0.180, 0.146)→(0.616, 0.178, 0.165) | (0.565, 0.113, 0.016)→(0.565, 0.113, 0.016) | 0.164→0.164 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.616, 0.178, 0.165)→(0.613, 0.177, 0.250) | (0.565, 0.113, 0.016)→(0.565, 0.113, 0.016) | 0.164→0.164 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.246
- phase_breakdown.approach_objective_score: 0.820
- phase_breakdown.placement_objective_score: 0.000
- grasp_place_fitness: 0.734

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.734
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.277
- **K-run variance**: 0.0043
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.407


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68473,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.1241,"transport_to_goal.transport_height":0.15493,"transport_to_goal.transport_speed":0.24842},"optimized_scores":{"best_composite_score":0.27737,"best_fitness_score":0.60737,"best_task_score":0.29109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6424.0,"contact_point_centroid":[0.5285,0.08798,-0.00217],"force_p95":0.12458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56677,"mean_force":0.13275,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58507,0.15558,0.23529]},{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.45599,-0.02459,-0.00115],"force_p95":0.33813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39515,"mean_force":0.05357,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44559,-0.0253,0.04951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10090.0,"contact_point_centroid":[0.44548,-0.00625,0.09588],"force_p95":0.13352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28763,"mean_force":0.07186,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44322,-0.0252,0.09588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11480.0,"contact_point_centroid":[0.4455,-0.04391,0.09721],"force_p95":0.10157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26477,"mean_force":0.06165,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44322,-0.0252,0.09682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4257.0,"contact_point_centroid":[0.47162,-0.01168,0.1689],"force_p95":0.15202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23423,"mean_force":0.0982,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46578,0.00647,0.17124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4122.0,"contact_point_centroid":[0.4745,0.02874,0.16921],"force_p95":0.13112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19761,"mean_force":0.09928,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46898,0.01055,0.17299]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02624,-0.00208],"force_p95":0.14598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19694,"mean_force":0.12868,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44798,-0.02539,0.04873]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4779,-0.01207,0.19433]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45512,-0.025,0.0725]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.52854,0.08852,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62561,0.20636,0.19118]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52854,0.08852,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62043,0.20467,0.12177]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.52854,0.08852,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61529,0.20274,0.18075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4350.0,"contact_point_centroid":[0.4471,-0.00611,0.04881],"force_p95":0.0731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10647,"mean_force":0.04975,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.02535,0.04771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.44632,-0.04451,0.04877],"force_p95":0.06576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0692,"mean_force":0.04078,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.02535,0.04771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6839.0,"contact_point_centroid":[0.58644,0.15684,0.23811],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01041,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58607,0.15683,0.23581]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1465.0,"contact_point_centroid":[0.62627,0.20638,0.19384],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62561,0.20635,0.19163]}],"total_contact_groups":17},"final_pose_error":0.016,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52854,0.08852,0.01602],"final_tcp_position":[0.61554,0.20278,0.22535],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.81773,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.45734,-0.02446,0.08964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":500.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45432,-0.02562,0.05496],"tcp_start":[0.45734,-0.02446,0.08964],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02561,0.02571],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14391,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11569.0,"raw_peak_contact_force":0.19694,"tcp_end":[0.4469,-0.02535,0.04768],"tcp_start":[0.45432,-0.02562,0.05496],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.45261,-0.0265,0.12992],"object_pos_start":[0.45851,-0.02561,0.02571],"object_to_goal_dist_end":0.29471,"object_to_goal_dist_start":0.30322,"object_z_max":0.12981,"peak_contact_force":0.14051,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21693.0,"raw_peak_contact_force":0.39515,"tcp_end":[0.4433,-0.02519,0.16064],"tcp_start":[0.4469,-0.02535,0.04768],"tcp_to_object_dist_end":0.03213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2187.0,"n_steps_budget":1000.0,"object_pos_end":[0.52854,0.08852,0.01602],"object_pos_start":[0.45261,-0.0265,0.12992],"object_to_goal_dist_end":0.18512,"object_to_goal_dist_start":0.29471,"object_z_max":0.14906,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21642.0,"raw_peak_contact_force":1.56677,"tcp_end":[0.62705,0.20681,0.25888],"tcp_start":[0.62496,0.20418,0.25837],"tcp_to_object_dist_end":0.28754,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.52854,0.08852,0.01602],"object_pos_start":[0.52854,0.08852,0.01602],"object_to_goal_dist_end":0.18512,"object_to_goal_dist_start":0.18512,"object_z_max":0.01602,"peak_contact_force":9748.81773,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2829.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.62555,0.20652,0.1226],"tcp_start":[0.62705,0.20681,0.25888],"tcp_to_object_dist_end":0.18626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52854,0.08852,0.01602],"object_pos_start":[0.52854,0.08852,0.01602],"object_to_goal_dist_end":0.18512,"object_to_goal_dist_start":0.18512,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61859,0.20397,0.14102],"tcp_start":[0.62555,0.20652,0.1226],"tcp_to_object_dist_end":0.19251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.52854,0.08852,0.01602],"object_pos_start":[0.52854,0.08852,0.01602],"object_to_goal_dist_end":0.18512,"object_to_goal_dist_start":0.18512,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61554,0.20278,0.22535],"tcp_start":[0.61859,0.20397,0.14102],"tcp_to_object_dist_end":0.25386,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56701,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.11124,"transport_to_goal.transport_height":0.12292,"transport_to_goal.transport_speed":0.2828},"optimized_scores":{"best_composite_score":0.25515,"best_fitness_score":0.58515,"best_task_score":0.24127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6824.0,"contact_point_centroid":[0.57015,0.06402,-0.00213],"force_p95":0.12301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45588,"mean_force":0.12981,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62004,0.12578,0.26915]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54166,0.00067,-0.00112],"force_p95":0.30818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45864,"mean_force":0.07027,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52771,0.00083,0.04504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2102.0,"contact_point_centroid":[0.5378,-0.0056,0.15118],"force_p95":0.17587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37191,"mean_force":0.09962,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53198,0.01289,0.15107]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8706.0,"contact_point_centroid":[0.52864,-0.018,0.08881],"force_p95":0.10779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31102,"mean_force":0.07318,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52512,0.00079,0.08678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2464.0,"contact_point_centroid":[0.53905,0.03277,0.15222],"force_p95":0.13038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30243,"mean_force":0.08524,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53307,0.01451,0.15253]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9055.0,"contact_point_centroid":[0.52872,0.01953,0.08729],"force_p95":0.10559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28869,"mean_force":0.07085,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52516,0.00079,0.08544]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15387,"mean_force":0.12543,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53057,0.00088,0.04482]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,0.00049,0.19253]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53672,0.00099,0.07033]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.57018,0.06409,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64435,0.15696,0.2529]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57018,0.06409,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64006,0.15582,0.19912]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.57018,0.06409,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63627,0.15462,0.25777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.53054,-0.01834,0.04607],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11847,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00086,0.04339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53046,0.01994,0.04518],"force_p95":0.06833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09378,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00086,0.04339]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7044.0,"contact_point_centroid":[0.62253,0.12841,0.27418],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01048,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62211,0.1284,0.27191]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1095.0,"contact_point_centroid":[0.64502,0.157,0.25515],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64435,0.15697,0.25293]}],"total_contact_groups":17},"final_pose_error":0.01603,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57018,0.06409,0.01602],"final_tcp_position":[0.63665,0.15467,0.30236],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.87038,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.5373,0.00099,0.08712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":464.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53775,0.00101,0.05343],"tcp_start":[0.5373,0.00099,0.08712],"tcp_to_object_dist_end":0.02819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13058,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15387,"tcp_end":[0.52933,0.00086,0.04335],"tcp_start":[0.53775,0.00101,0.05343],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53718,0.00094,0.11711],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.20583,"object_to_goal_dist_start":0.25049,"object_z_max":0.117,"peak_contact_force":0.10888,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17906.0,"raw_peak_contact_force":0.45864,"tcp_end":[0.52523,0.0008,0.1421],"tcp_start":[0.52933,0.00086,0.04335],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2020.0,"n_steps_budget":1000.0,"object_pos_end":[0.57018,0.06409,0.01602],"object_pos_start":[0.53718,0.00094,0.11711],"object_to_goal_dist_end":0.21328,"object_to_goal_dist_start":0.20583,"object_z_max":0.13761,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18434.0,"raw_peak_contact_force":1.45588,"tcp_end":[0.64533,0.15724,0.3037],"tcp_start":[0.64466,0.15638,0.30316],"tcp_to_object_dist_end":0.31158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.57018,0.06409,0.01602],"object_pos_start":[0.57018,0.06409,0.01602],"object_to_goal_dist_end":0.21328,"object_to_goal_dist_start":0.21328,"object_z_max":0.01602,"peak_contact_force":9748.87038,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2115.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.6441,0.15701,0.20023],"tcp_start":[0.64533,0.15724,0.3037],"tcp_to_object_dist_end":0.21916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57018,0.06409,0.01602],"object_pos_start":[0.57018,0.06409,0.01602],"object_to_goal_dist_end":0.21328,"object_to_goal_dist_start":0.21328,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63867,0.15537,0.21824],"tcp_start":[0.6441,0.15701,0.20023],"tcp_to_object_dist_end":0.2322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.57018,0.06409,0.01602],"object_pos_start":[0.57018,0.06409,0.01602],"object_to_goal_dist_end":0.21328,"object_to_goal_dist_start":0.21328,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63665,0.15467,0.30236],"tcp_start":[0.63867,0.15537,0.21824],"tcp_to_object_dist_end":0.3076,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52308,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.12297,"transport_to_goal.transport_height":0.1091,"transport_to_goal.transport_speed":0.28695},"optimized_scores":{"best_composite_score":0.40358,"best_fitness_score":0.73358,"best_task_score":0.53972},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2961.0,"contact_point_centroid":[0.59544,0.18506,-0.00232],"force_p95":0.12734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54397,"mean_force":0.13745,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59436,0.17242,0.20506]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.52786,0.02885,-0.00123],"force_p95":0.3274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44395,"mean_force":0.07137,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51447,0.0292,0.04597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11169.0,"contact_point_centroid":[0.51548,0.04794,0.09629],"force_p95":0.09736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29995,"mean_force":0.06389,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51195,0.02905,0.09415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10551.0,"contact_point_centroid":[0.51518,0.01015,0.09348],"force_p95":0.10035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2754,"mean_force":0.06689,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51197,0.02905,0.09145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8546.0,"contact_point_centroid":[0.54795,0.06687,0.17085],"force_p95":0.13515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23297,"mean_force":0.09318,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54272,0.08532,0.17244]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03066,-0.00212],"force_p95":0.1556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21741,"mean_force":0.13167,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02939,0.04555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9169.0,"contact_point_centroid":[0.54882,0.1045,0.17108],"force_p95":0.12484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21185,"mean_force":0.08759,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54324,0.0862,0.17277]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51101,0.0142,0.19279]},{"body_a":"world","body_b":"grasp_target","contact_count":468.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52355,0.0292,0.07075]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.59541,0.18512,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59635,0.17684,0.16272]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59541,0.18512,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59147,0.17535,0.11673]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.59541,0.18512,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58623,0.17363,0.17703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4890.0,"contact_point_centroid":[0.51712,0.01015,0.04698],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10968,"mean_force":0.04414,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51609,0.02932,0.04419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4994.0,"contact_point_centroid":[0.51702,0.04861,0.04597],"force_p95":0.07309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07492,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51609,0.02932,0.04419]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2901.0,"contact_point_centroid":[0.59541,0.17343,0.20758],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59489,0.17341,0.20528]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1044.0,"contact_point_centroid":[0.597,0.17688,0.16512],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59634,0.17684,0.16292]}],"total_contact_groups":17},"final_pose_error":0.01515,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59541,0.18512,0.01602],"final_tcp_position":[0.58643,0.17365,0.2217],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.54397,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.52437,0.02866,0.08754],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":468.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52431,0.02985,0.05377],"tcp_start":[0.52437,0.02866,0.08754],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02981,0.02556],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18438,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1511,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11684.0,"raw_peak_contact_force":0.21741,"tcp_end":[0.51606,0.02932,0.04415],"tcp_start":[0.52431,0.02985,0.05377],"tcp_to_object_dist_end":0.02352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.52448,0.02933,0.12895],"object_pos_start":[0.53046,0.02981,0.02556],"object_to_goal_dist_end":0.16925,"object_to_goal_dist_start":0.18438,"object_z_max":0.12883,"peak_contact_force":0.10083,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21864.0,"raw_peak_contact_force":0.44395,"tcp_end":[0.51214,0.02906,0.15475],"tcp_start":[0.51606,0.02932,0.04415],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1694.0,"n_steps_budget":1000.0,"object_pos_end":[0.5938,0.18439,0.01257],"object_pos_start":[0.52448,0.02933,0.12895],"object_to_goal_dist_end":0.09601,"object_to_goal_dist_start":0.16925,"object_z_max":0.15706,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23577.0,"raw_peak_contact_force":1.54397,"tcp_end":[0.59775,0.17726,0.20803],"tcp_start":[0.59746,0.17665,0.20811],"tcp_to_object_dist_end":0.19564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.59541,0.18512,0.01602],"object_pos_start":[0.59541,0.18512,0.01602],"object_to_goal_dist_end":0.0925,"object_to_goal_dist_start":0.0925,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.59662,0.177,0.11644],"tcp_start":[0.59775,0.17726,0.20803],"tcp_to_object_dist_end":0.10075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59541,0.18512,0.01602],"object_pos_start":[0.59541,0.18512,0.01602],"object_to_goal_dist_end":0.0925,"object_to_goal_dist_start":0.0925,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5896,0.17473,0.13647],"tcp_start":[0.59662,0.177,0.11644],"tcp_to_object_dist_end":0.12104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.59541,0.18512,0.01602],"object_pos_start":[0.59541,0.18512,0.01602],"object_to_goal_dist_end":0.0925,"object_to_goal_dist_start":0.0925,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58643,0.17365,0.2217],"tcp_start":[0.5896,0.17473,0.13647],"tcp_to_object_dist_end":0.20619,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```