## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3701 | 0.47 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3732 | 0.48 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3285 | 0.39 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2857 | 0.30 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2712 | 0.28 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.370) — your mutation base

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
    threshold: 0.3
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
    tolerance: 0.015
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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_held_after
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.3
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: descend_to_place
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
    - 0.0
    tolerance: 0.02
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
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.3
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_held_after, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.3
  - retries: max_attempts=1, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
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

- **Composite score**: 0.370
- **task_score** (E): 0.473
- **fitness_score**: 0.700  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
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
| lift | 1.00 | 1.00 | 0.1037 |
| transport_to_goal | 1.00 | 1.00 | 0.2268 |
| descend_to_place | 1.00 | 0.67 | 0.0691 |
| release | 1.00 | 1.00 | 0.0195 |
| retract | 1.00 | 1.00 | 0.0847 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.054) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.054)→(0.497, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.142 | 0.189 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.045)→(0.494, 0.002, 0.149) | (0.511, 0.002, 0.026)→(0.507, 0.002, 0.124) | 0.246→0.223 | 1.00 / 25.333 | 0.064 | 0.426 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.002, 0.149)→(0.617, 0.171, 0.225) | (0.507, 0.002, 0.124)→(0.622, 0.171, 0.192) | 0.223→0.056 | 1.00 / 17.333 | 0.131 | 0.170 |
| descend_to_place | descend | 1.00 / step_budget | (0.617, 0.171, 0.225)→(0.620, 0.177, 0.156) | (0.622, 0.171, 0.192)→(0.627, 0.174, 0.104) | 0.056→0.035 | 0.67 / 11.667 | 0.099 | 0.273 |
| release | release | 1.00 / step_budget | (0.620, 0.177, 0.156)→(0.614, 0.175, 0.174) | (0.627, 0.174, 0.104)→(0.618, 0.176, 0.023) | 0.035→0.117 | 1.00 / 4.000 | 0.145 | 1.353 |
| retract | retract | 1.00 / step_budget | (0.614, 0.175, 0.174)→(0.611, 0.174, 0.259) | (0.618, 0.176, 0.023)→(0.618, 0.176, 0.023) | 0.117→0.118 | 1.00 / 4.000 | 0.123 | 0.149 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.569
- phase_score: 0.817
- phase_breakdown.approach_objective_score: 0.820
- phase_breakdown.placement_objective_score: 0.816
- grasp_place_fitness: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.569
- **Median Q (composite search score)**: 0.403
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.512


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82727,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.11628,"transport_to_goal.transport_height":0.08952,"transport_to_goal.transport_speed":0.07112},"optimized_scores":{"best_composite_score":0.40329,"best_fitness_score":0.73329,"best_task_score":0.54293},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.60971,0.19986,-0.00405],"force_p95":0.83577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01266,"mean_force":0.25109,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61604,0.20088,0.13776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":595.0,"contact_point_centroid":[0.62544,0.22105,0.12131],"force_p95":0.13222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40278,"mean_force":0.08867,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62026,0.20249,0.1256]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.4564,-0.02473,-0.00126],"force_p95":0.34133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39457,"mean_force":0.06414,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44575,-0.02531,0.04934]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":651.0,"contact_point_centroid":[0.6253,0.18413,0.1216],"force_p95":0.12145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36492,"mean_force":0.08103,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6203,0.2025,0.12565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7130.0,"contact_point_centroid":[0.44511,-0.00616,0.09461],"force_p95":0.10492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28676,"mean_force":0.06461,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44339,-0.0252,0.09386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1007.0,"contact_point_centroid":[0.62587,0.18172,0.15862],"force_p95":0.16991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26755,"mean_force":0.11092,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62048,0.19994,0.16245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7926.0,"contact_point_centroid":[0.44491,-0.04417,0.09448],"force_p95":0.09802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26449,"mean_force":0.05926,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4434,-0.0252,0.09364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":982.0,"contact_point_centroid":[0.62599,0.21807,0.1595],"force_p95":0.16867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26362,"mean_force":0.11424,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62041,0.19984,0.16347]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02624,-0.00208],"force_p95":0.14598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19694,"mean_force":0.12868,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44798,-0.02539,0.04873]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.60578,0.202,-0.00198],"force_p95":0.1314,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17114,"mean_force":0.12267,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61271,0.19966,0.18917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10014.0,"contact_point_centroid":[0.53102,0.06289,0.16771],"force_p95":0.12211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16528,"mean_force":0.08171,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52582,0.08129,0.16844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9335.0,"contact_point_centroid":[0.52946,0.09797,0.16698],"force_p95":0.13085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16081,"mean_force":0.08729,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52434,0.07944,0.16805]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4779,-0.01207,0.19433]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45512,-0.025,0.0725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4350.0,"contact_point_centroid":[0.4471,-0.00611,0.04881],"force_p95":0.0731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10647,"mean_force":0.04975,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.02535,0.04771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.44632,-0.04451,0.04877],"force_p95":0.06576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0692,"mean_force":0.04078,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.02535,0.04771]}],"total_contact_groups":16},"final_pose_error":0.01587,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60577,0.202,0.02602],"final_tcp_position":[0.61295,0.19969,0.23378],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.01266,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.45734,-0.02446,0.08964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":500.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45432,-0.02562,0.05496],"tcp_start":[0.45734,-0.02446,0.08964],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02561,0.02571],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14391,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11569.0,"raw_peak_contact_force":0.19694,"tcp_end":[0.4469,-0.02535,0.04768],"tcp_start":[0.45432,-0.02562,0.05496],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":436.0,"n_steps_budget":750.0,"object_pos_end":[0.45617,-0.0255,0.1231],"object_pos_start":[0.45851,-0.02561,0.02571],"object_to_goal_dist_end":0.29149,"object_to_goal_dist_start":0.30322,"object_z_max":0.12292,"peak_contact_force":0.10464,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15146.0,"raw_peak_contact_force":0.39457,"tcp_end":[0.4433,-0.02519,0.14947],"tcp_start":[0.4469,-0.02535,0.04768],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":887.0,"n_steps_budget":1000.0,"object_pos_end":[0.62375,0.1961,0.15756],"object_pos_start":[0.45617,-0.0255,0.1231],"object_to_goal_dist_end":0.04554,"object_to_goal_dist_start":0.29149,"object_z_max":0.15753,"peak_contact_force":0.11601,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19349.0,"raw_peak_contact_force":0.16528,"tcp_end":[0.61853,0.19662,0.19245],"tcp_start":[0.4433,-0.02519,0.14947],"tcp_to_object_dist_end":0.03528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":111.0,"n_steps_budget":1000.0,"object_pos_end":[0.62815,0.20286,0.09548],"object_pos_start":[0.62375,0.1961,0.15756],"object_to_goal_dist_end":0.01949,"object_to_goal_dist_start":0.04554,"object_z_max":0.15756,"peak_contact_force":0.12427,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1989.0,"raw_peak_contact_force":0.26755,"subtask_id":"placement_objective","tcp_end":[0.62308,0.2033,0.1316],"tcp_start":[0.61853,0.19662,0.19245],"tcp_to_object_dist_end":0.03648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60634,0.20204,0.02644],"object_pos_start":[0.62815,0.20286,0.09548],"object_to_goal_dist_end":0.09105,"object_to_goal_dist_start":0.01949,"object_z_max":0.09548,"peak_contact_force":0.16608,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1526.0,"raw_peak_contact_force":1.01266,"tcp_end":[0.61593,0.20084,0.14932],"tcp_start":[0.62308,0.2033,0.1316],"tcp_to_object_dist_end":0.12326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.60577,0.202,0.02602],"object_pos_start":[0.60634,0.20204,0.02644],"object_to_goal_dist_end":0.09162,"object_to_goal_dist_start":0.09105,"object_z_max":0.02645,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.17114,"tcp_end":[0.61295,0.19969,0.23378],"tcp_start":[0.61593,0.20084,0.14932],"tcp_to_object_dist_end":0.2079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33865,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.10517,"transport_to_goal.transport_height":0.07574,"transport_to_goal.transport_speed":0.03404},"optimized_scores":{"best_composite_score":0.2889,"best_fitness_score":0.6189,"best_task_score":0.30876},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.66689,0.15155,-0.00388],"force_p95":0.81827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9553,"mean_force":0.2077,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63708,0.1526,0.20851]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.5413,0.0008,-0.00121],"force_p95":0.32897,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44053,"mean_force":0.07705,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52802,0.00083,0.04492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6448.0,"contact_point_centroid":[0.52845,-0.01805,0.08601],"force_p95":0.109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31062,"mean_force":0.07331,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52527,0.00079,0.08388]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.64531,0.16844,0.24346],"force_p95":0.22248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30097,"mean_force":0.15499,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63921,0.1502,0.24747]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6766.0,"contact_point_centroid":[0.52857,0.01957,0.08455],"force_p95":0.10678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28827,"mean_force":0.07072,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52532,0.00079,0.08268]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":306.0,"contact_point_centroid":[0.64523,0.13353,0.2408],"force_p95":0.16967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26939,"mean_force":0.0871,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63938,0.15047,0.24469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10181.0,"contact_point_centroid":[0.58584,0.09308,0.19074],"force_p95":0.11303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17959,"mean_force":0.07744,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57962,0.07436,0.1896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10942.0,"contact_point_centroid":[0.58672,0.05694,0.19154],"force_p95":0.09535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17386,"mean_force":0.07246,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58058,0.07555,0.1906]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15387,"mean_force":0.12543,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53057,0.00088,0.04482]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,0.00049,0.19253]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.667,0.15148,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1229,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63396,0.15163,0.26683]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53672,0.00099,0.07033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.53054,-0.01834,0.04607],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11847,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00086,0.04339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53046,0.01994,0.04518],"force_p95":0.06833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09378,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00086,0.04339]}],"total_contact_groups":14},"final_pose_error":0.0159,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.667,0.15148,0.01602],"final_tcp_position":[0.63434,0.15168,0.31143],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.9553,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.5373,0.00099,0.08712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":464.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53775,0.00101,0.05343],"tcp_start":[0.5373,0.00099,0.08712],"tcp_to_object_dist_end":0.02819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13058,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15387,"tcp_end":[0.52933,0.00086,0.04335],"tcp_start":[0.53775,0.00101,0.05343],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":459.0,"n_steps_budget":690.0,"object_pos_end":[0.53873,0.0008,0.1107],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.20751,"object_to_goal_dist_start":0.25049,"object_z_max":0.11055,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13314.0,"raw_peak_contact_force":0.44053,"tcp_end":[0.52518,0.0008,0.13418],"tcp_start":[0.52933,0.00086,0.04335],"tcp_to_object_dist_end":0.0271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.64446,0.1496,0.22055],"object_pos_start":[0.53873,0.0008,0.1107],"object_to_goal_dist_end":0.03081,"object_to_goal_dist_start":0.20751,"object_z_max":0.22044,"peak_contact_force":0.1493,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21123.0,"raw_peak_contact_force":0.17959,"tcp_end":[0.63887,0.14946,0.25109],"tcp_start":[0.52518,0.0008,0.13418],"tcp_to_object_dist_end":0.03104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.65794,0.14522,0.12304],"object_pos_start":[0.64446,0.1496,0.22055],"object_to_goal_dist_end":0.07003,"object_to_goal_dist_start":0.03081,"object_z_max":0.22057,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":464.0,"raw_peak_contact_force":0.30097,"subtask_id":"placement_objective","tcp_end":[0.64178,0.15385,0.20974],"tcp_start":[0.63887,0.14946,0.25109],"tcp_to_object_dist_end":0.08861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.667,0.15148,0.01601],"object_pos_start":[0.65794,0.14522,0.12304],"object_to_goal_dist_end":0.17629,"object_to_goal_dist_start":0.07003,"object_z_max":0.12304,"peak_contact_force":0.12292,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":660.0,"raw_peak_contact_force":1.9553,"tcp_end":[0.6363,0.15234,0.2272],"tcp_start":[0.64178,0.15385,0.20974],"tcp_to_object_dist_end":0.21341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.667,0.15148,0.01602],"object_pos_start":[0.667,0.15148,0.01601],"object_to_goal_dist_end":0.17628,"object_to_goal_dist_start":0.17629,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.1229,"tcp_end":[0.63434,0.15168,0.31143],"tcp_start":[0.6363,0.15234,0.2272],"tcp_to_object_dist_end":0.29721,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80311,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.13257,"transport_to_goal.transport_height":0.13602,"transport_to_goal.transport_speed":0.07803},"optimized_scores":{"best_composite_score":0.41805,"best_fitness_score":0.74805,"best_task_score":0.56865},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.58205,0.17383,-0.00367],"force_p95":0.76344,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08987,"mean_force":0.21597,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58884,0.17278,0.13398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":501.0,"contact_point_centroid":[0.59788,0.19254,0.11674],"force_p95":0.16502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46337,"mean_force":0.10408,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59297,0.17417,0.12087]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.52816,0.02869,-0.00129],"force_p95":0.33865,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44383,"mean_force":0.06263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5147,0.02922,0.04588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":597.0,"contact_point_centroid":[0.59751,0.15609,0.11743],"force_p95":0.14552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40966,"mean_force":0.08725,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59307,0.1742,0.12101]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8958.0,"contact_point_centroid":[0.51591,0.04797,0.10114],"force_p95":0.10375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29989,"mean_force":0.06741,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51211,0.02905,0.0989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8815.0,"contact_point_centroid":[0.51572,0.0102,0.09966],"force_p95":0.10107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27531,"mean_force":0.0681,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51212,0.02905,0.0972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1694.0,"contact_point_centroid":[0.59893,0.18856,0.17733],"force_p95":0.17397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25121,"mean_force":0.10781,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5936,0.17086,0.18038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1501.0,"contact_point_centroid":[0.59875,0.15276,0.17634],"force_p95":0.1826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23522,"mean_force":0.12148,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59368,0.17097,0.17909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03066,-0.00212],"force_p95":0.1556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21741,"mean_force":0.13167,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02939,0.04555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6652.0,"contact_point_centroid":[0.5536,0.11093,0.19071],"force_p95":0.12367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16499,"mean_force":0.07974,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5475,0.09237,0.19128]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6516.0,"contact_point_centroid":[0.55438,0.07523,0.19133],"force_p95":0.12296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15815,"mean_force":0.08112,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54834,0.09382,0.19199]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.58122,0.17397,-0.00198],"force_p95":0.12655,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15182,"mean_force":0.12267,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58543,0.17169,0.18638]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51101,0.0142,0.19279]},{"body_a":"world","body_b":"grasp_target","contact_count":468.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52355,0.0292,0.07075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4890.0,"contact_point_centroid":[0.51712,0.01015,0.04698],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10968,"mean_force":0.04414,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51609,0.02932,0.04419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4994.0,"contact_point_centroid":[0.51702,0.04861,0.04597],"force_p95":0.07309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07492,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51609,0.02932,0.04419]}],"total_contact_groups":16},"final_pose_error":0.01506,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58122,0.17397,0.02602],"final_tcp_position":[0.58563,0.17172,0.23105],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.08987,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.52437,0.02866,0.08754],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":468.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52431,0.02985,0.05377],"tcp_start":[0.52437,0.02866,0.08754],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02981,0.02556],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18438,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1511,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11684.0,"raw_peak_contact_force":0.21741,"tcp_end":[0.51606,0.02932,0.04415],"tcp_start":[0.52431,0.02985,0.05377],"tcp_to_object_dist_end":0.02352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":580.0,"n_steps_budget":840.0,"object_pos_end":[0.52606,0.02926,0.1372],"object_pos_start":[0.53046,0.02981,0.02556],"object_to_goal_dist_end":0.16983,"object_to_goal_dist_start":0.18438,"object_z_max":0.13704,"peak_contact_force":0.08809,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17875.0,"raw_peak_contact_force":0.44383,"tcp_end":[0.51223,0.02907,0.16235],"tcp_start":[0.51606,0.02932,0.04415],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.59799,0.16722,0.19931],"object_pos_start":[0.52606,0.02926,0.1372],"object_to_goal_dist_end":0.09199,"object_to_goal_dist_start":0.16983,"object_z_max":0.19921,"peak_contact_force":0.12674,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13168.0,"raw_peak_contact_force":0.16499,"tcp_end":[0.59246,0.16733,0.2304],"tcp_start":[0.51223,0.02907,0.16235],"tcp_to_object_dist_end":0.03158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.59629,0.17442,0.09257],"object_pos_start":[0.59799,0.16722,0.19931],"object_to_goal_dist_end":0.0169,"object_to_goal_dist_start":0.09199,"object_z_max":0.19932,"peak_contact_force":0.17356,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3195.0,"raw_peak_contact_force":0.25121,"subtask_id":"placement_objective","tcp_end":[0.59587,0.17495,0.1264],"tcp_start":[0.59246,0.16733,0.2304],"tcp_to_object_dist_end":0.03384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58126,0.17387,0.02648],"object_pos_start":[0.59629,0.17442,0.09257],"object_to_goal_dist_end":0.08422,"object_to_goal_dist_start":0.0169,"object_z_max":0.09257,"peak_contact_force":0.14743,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1418.0,"raw_peak_contact_force":1.08987,"tcp_end":[0.58872,0.17275,0.14576],"tcp_start":[0.59587,0.17495,0.1264],"tcp_to_object_dist_end":0.11952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.58122,0.17397,0.02602],"object_pos_start":[0.58126,0.17387,0.02648],"object_to_goal_dist_end":0.08467,"object_to_goal_dist_start":0.08422,"object_z_max":0.02648,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.15182,"tcp_end":[0.58563,0.17172,0.23105],"tcp_start":[0.58872,0.17275,0.14576],"tcp_to_object_dist_end":0.20509,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```