## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1243 | 0.45 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2455 | 0.46 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2493 | 0.46 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1512 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2125 | 0.47 | ❌ rejected |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.124) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
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
      mode: keep_current
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
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
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
  subtask_id: grasp_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
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
  subtask_id: lift_object
- id: transport_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
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
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.124
- **task_score** (E): 0.453
- **fitness_score**: 0.704  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1575 |
| descend_1 | 1.00 | 1.00 | 0.1142 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1784 |
| transport_1 | 0.67 | 0.67 | 0.2224 |
| descend_2 | 0.00 | 1.00 | 0.0014 |
| release_1 | 1.00 | 1.00 | 0.0533 |
| retract_1 | 0.67 | 1.00 | 0.1907 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.506, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.034)→(0.497, 0.001, 0.025) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.140 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.025)→(0.507, 0.001, 0.203) | (0.511, 0.001, 0.026)→(0.521, 0.002, 0.197) | 0.246→0.221 | 1.00 / 33.667 | 0.093 | 0.647 |
| transport_1 | approach | 0.67 / step_budget | (0.507, 0.001, 0.203)→(0.612, 0.163, 0.303) | (0.521, 0.002, 0.197)→(0.623, 0.161, 0.277) | 0.221→0.142 | 0.67 / 17.667 | 0.083 | 0.208 |
| descend_2 | descend | 0.00 / step_budget | (0.525, 0.096, 0.207)→(0.525, 0.095, 0.206) | (0.623, 0.161, 0.277)→(0.625, 0.161, 0.221) | 0.142→0.105 | 1.00 / 18.000 | 667.057 | 1015.481 |
| release_1 | release | 1.00 / step_budget | (0.525, 0.095, 0.206)→(0.536, 0.063, 0.241) | (0.625, 0.161, 0.218)→(0.620, 0.169, 0.002) | 0.107→0.137 | 1.00 / 4.000 | 0.608 | 459.592 |
| retract_1 | retract | 0.67 / step_budget | (0.536, 0.063, 0.241)→(0.611, 0.164, 0.194) | (0.620, 0.169, 0.002)→(0.621, 0.170, 0.016) | 0.137→0.123 | 1.00 / 4.000 | 0.123 | 0.572 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.507
- phase_breakdown.place_at_goal_score: 0.255
- phase_breakdown.transport_to_goal_score: 0.437
- phase_breakdown.reach_object_score: 0.672
- phase_breakdown.grasp_object_score: 0.748
- phase_breakdown.lift_object_score: 0.587
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.154
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":106.0,"average_failure_rate":0.20623,"average_mean_iterations":44.33268,"average_solve_count":514.0,"average_success_count":408.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03582,"descend_1.speed":0.04733,"descend_2.speed":0.01008,"lift_1.lift_height":0.13424,"lift_1.speed":0.05827,"retract_1.speed":0.05737,"transport_1.speed":0.07175,"transport_1.transport_height":0.22578},"optimized_scores":{"best_composite_score":0.15372,"best_fitness_score":0.73372,"best_task_score":0.50709},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.31028,-0.11512,-0.00193],"force_p95":2992.2729,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3046.44364,"mean_force":2517.36696,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.34695,-0.02205,0.01825]},{"body_a":"world","body_b":"hand","contact_count":56.0,"contact_point_centroid":[0.28913,-0.14914,-0.00185],"force_p95":646.48277,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1374.52737,"mean_force":178.41513,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.37257,-0.09659,0.03726]},{"body_a":"world","body_b":"grasp_target","contact_count":655.0,"contact_point_centroid":[0.61843,0.18175,-0.00472],"force_p95":0.97559,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.40104,"mean_force":0.23439,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.38242,-0.12137,0.05749]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45612,-0.02536,-0.00136],"force_p95":0.6348,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71481,"mean_force":0.20109,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44598,-0.02564,0.02286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13180.0,"contact_point_centroid":[0.52643,0.05096,0.21621],"force_p95":0.1182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31688,"mean_force":0.07852,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52274,0.06949,0.21619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12527.0,"contact_point_centroid":[0.52662,0.08853,0.21659],"force_p95":0.12874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28932,"mean_force":0.08073,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52303,0.06988,0.21651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8350.0,"contact_point_centroid":[0.44852,-0.04465,0.08089],"force_p95":0.07482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2716,"mean_force":0.05038,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44847,-0.02552,0.07921]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7721.0,"contact_point_centroid":[0.44845,-0.00634,0.07954],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27085,"mean_force":0.0537,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44833,-0.02552,0.0773]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02613,-0.00205],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19153,"mean_force":0.12707,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44792,-0.02571,0.02259]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48081,-0.01069,0.22671]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.61804,0.1836,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12351,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49,0.02524,0.11194]},{"body_a":"world","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45613,-0.02417,0.0861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.44683,-0.00646,0.0239],"force_p95":0.06771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09288,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44682,-0.02567,0.02156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44668,-0.04491,0.02339],"force_p95":0.06647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08655,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44682,-0.02567,0.02157]},{"body_a":"left_finger","body_b":"right_finger","contact_count":21.0,"contact_point_centroid":[0.38384,-0.12527,0.04848],"force_p95":0.01622,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.0093,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.38426,-0.12359,0.04823]}],"total_contact_groups":15},"final_pose_error":0.05994,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61804,0.1836,0.01602],"final_tcp_position":[0.59407,0.16395,0.14588],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":3046.44364,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4613,-0.02245,0.14922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.4543,-0.02594,0.0286],"tcp_start":[0.4613,-0.02245,0.14922],"tcp_to_object_dist_end":0.00499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02566,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13565,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11783.0,"raw_peak_contact_force":0.19153,"subtask_id":"grasp_object","tcp_end":[0.44679,-0.02567,0.02154],"tcp_start":[0.4543,-0.02594,0.0286],"tcp_to_object_dist_end":0.01239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.4699,-0.02532,0.14172],"object_pos_start":[0.45842,-0.02566,0.02582],"object_to_goal_dist_end":0.28456,"object_to_goal_dist_start":0.30328,"object_z_max":0.14145,"peak_contact_force":0.09768,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16151.0,"raw_peak_contact_force":0.71481,"subtask_id":"lift_object","tcp_end":[0.45336,-0.02549,0.14077],"tcp_start":[0.44679,-0.02567,0.02154],"tcp_to_object_dist_end":0.01657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6179,0.16993,0.26175],"object_pos_start":[0.4699,-0.02532,0.14172],"object_to_goal_dist_end":0.15301,"object_to_goal_dist_start":0.28456,"object_z_max":0.27743,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25707.0,"raw_peak_contact_force":0.31688,"subtask_id":"transport_to_goal","tcp_end":[0.60389,0.17573,0.30445],"tcp_start":[0.45336,-0.02549,0.14077],"tcp_to_object_dist_end":0.04531,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":73.0,"n_steps_budget":1000.0,"object_pos_end":[0.62306,0.17003,0.09249],"object_pos_start":[0.6179,0.16993,0.26175],"object_to_goal_dist_end":0.04445,"object_to_goal_dist_start":0.15301,"object_z_max":0.26175,"peak_contact_force":2000.92101,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":3046.44364,"subtask_id":"place_at_goal","tcp_end":[0.3414,-0.02959,0.01482],"tcp_start":[0.34314,-0.02609,0.01599],"tcp_to_object_dist_end":0.35385,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61803,0.18357,0.01603],"object_pos_start":[0.6232,0.17003,0.08485],"object_to_goal_dist_end":0.10186,"object_to_goal_dist_start":0.0486,"object_z_max":0.08485,"peak_contact_force":0.12355,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":732.0,"raw_peak_contact_force":1374.52737,"subtask_id":"place_at_goal","tcp_end":[0.38205,-0.12268,0.07819],"tcp_start":[0.3414,-0.02959,0.01482],"tcp_to_object_dist_end":0.39159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61804,0.1836,0.01602],"object_pos_start":[0.61803,0.18357,0.01603],"object_to_goal_dist_end":0.10186,"object_to_goal_dist_start":0.10186,"object_z_max":0.01603,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12351,"subtask_id":"place_at_goal","tcp_end":[0.59407,0.16395,0.14588],"tcp_start":[0.38205,-0.12268,0.07819],"tcp_to_object_dist_end":0.13351,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":120.0,"average_failure_rate":0.25,"average_mean_iterations":52.33333,"average_solve_count":480.0,"average_success_count":360.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06773,"descend_1.speed":0.09255,"descend_2.speed":0.02771,"lift_1.lift_height":0.25698,"lift_1.speed":0.03571,"retract_1.speed":0.05695,"transport_1.speed":0.04645,"transport_1.transport_height":0.20933},"optimized_scores":{"best_composite_score":0.05172,"best_fitness_score":0.63172,"best_task_score":0.31032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":34.0,"contact_point_centroid":[0.64524,0.1451,-0.00876],"force_p95":2.20502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32747,"mean_force":1.51194,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64028,0.14867,0.4012]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.65123,0.14604,-0.00349],"force_p95":0.35953,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18788,"mean_force":0.14301,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.64237,0.1519,0.33446]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.54006,0.00072,-0.00143],"force_p95":0.55592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59105,"mean_force":0.20978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52842,0.00083,0.02778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16278.0,"contact_point_centroid":[0.53388,-0.01836,0.14762],"force_p95":0.07888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28378,"mean_force":0.05588,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53293,0.00073,0.14536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.53361,0.0198,0.14378],"force_p95":0.07819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27301,"mean_force":0.0551,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53271,0.00073,0.14163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1153.0,"contact_point_centroid":[0.64217,0.16845,0.38026],"force_p95":0.07724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1808,"mean_force":0.047,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6407,0.14924,0.38022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1177.0,"contact_point_centroid":[0.64222,0.1303,0.38047],"force_p95":0.07329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16661,"mean_force":0.04466,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64071,0.14924,0.38025]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15903,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53071,0.00088,0.02826]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51605,0.00045,0.22489]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53517,0.00096,0.07896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53061,-0.01834,0.02949],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11312,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52945,0.00086,0.02681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13508.0,"contact_point_centroid":[0.58931,0.0918,0.32004],"force_p95":0.08701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10885,"mean_force":0.05732,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58815,0.07268,0.31909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15645.0,"contact_point_centroid":[0.59057,0.05617,0.32158],"force_p95":0.07453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09663,"mean_force":0.05014,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58984,0.07511,0.32117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53053,0.01994,0.02861],"force_p95":0.06812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09627,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52946,0.00086,0.02681]}],"total_contact_groups":14},"final_pose_error":0.0195,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65111,0.14615,0.01602],"final_tcp_position":[0.64437,0.15574,0.26019],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":2.32747,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1264.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53474,0.00093,0.14731],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53786,0.00101,0.03655],"tcp_start":[0.53474,0.00093,0.14731],"tcp_to_object_dist_end":0.01234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12987,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15903,"subtask_id":"grasp_object","tcp_end":[0.52942,0.00086,0.02678],"tcp_start":[0.53786,0.00101,0.03655],"tcp_to_object_dist_end":0.01477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.55182,0.00069,0.25332],"object_pos_start":[0.54416,0.00073,0.02588],"object_to_goal_dist_end":0.19448,"object_to_goal_dist_start":0.25053,"object_z_max":0.25307,"peak_contact_force":0.08106,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32988.0,"raw_peak_contact_force":0.59105,"subtask_id":"lift_object","tcp_end":[0.54065,0.00068,0.2632],"tcp_start":[0.52942,0.00086,0.02678],"tcp_to_object_dist_end":0.01492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.64909,0.14939,0.36836],"object_pos_start":[0.55182,0.00069,0.25332],"object_to_goal_dist_end":0.17747,"object_to_goal_dist_start":0.19448,"object_z_max":0.36824,"peak_contact_force":0.09245,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29153.0,"raw_peak_contact_force":0.10885,"subtask_id":"transport_to_goal","tcp_end":[0.64119,0.14905,0.38386],"tcp_start":[0.54065,0.00068,0.2632],"tcp_to_object_dist_end":0.0174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.64909,0.14939,0.36836],"object_pos_start":[0.64909,0.14939,0.36836],"object_to_goal_dist_end":0.17747,"object_to_goal_dist_start":0.17747,"peak_contact_force":0.0927,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.64119,0.14905,0.38386],"tcp_start":[0.64119,0.14905,0.38386],"tcp_to_object_dist_end":0.0174,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64882,0.1478,-0.00836],"object_pos_start":[0.64909,0.14939,0.36836],"object_to_goal_dist_end":0.19973,"object_to_goal_dist_start":0.17747,"object_z_max":0.36836,"peak_contact_force":1.26601,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2364.0,"raw_peak_contact_force":2.32747,"subtask_id":"place_at_goal","tcp_end":[0.64027,0.14867,0.40278],"tcp_start":[0.64119,0.14905,0.38386],"tcp_to_object_dist_end":0.41123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.65111,0.14615,0.01602],"object_pos_start":[0.64882,0.1478,-0.00836],"object_to_goal_dist_end":0.17552,"object_to_goal_dist_start":0.19973,"object_z_max":0.01703,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1008.0,"raw_peak_contact_force":1.18788,"subtask_id":"place_at_goal","tcp_end":[0.64437,0.15574,0.26019],"tcp_start":[0.64027,0.14867,0.40278],"tcp_to_object_dist_end":0.24445,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":59.0,"average_failure_rate":0.19218,"average_mean_iterations":41.0684,"average_solve_count":307.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0531,"descend_1.speed":0.08006,"descend_2.speed":0.03965,"lift_1.lift_height":0.19997,"lift_1.speed":0.06193,"retract_1.speed":0.05991,"transport_1.speed":0.06317,"transport_1.transport_height":0.12243},"optimized_scores":{"best_composite_score":0.16742,"best_fitness_score":0.74742,"best_task_score":0.54018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.59241,0.17116,-0.01261],"force_p95":1.61873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92079,"mean_force":0.97397,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58708,0.16335,0.23604]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.52746,0.0287,-0.00147],"force_p95":0.52836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63566,"mean_force":0.14335,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51518,0.02921,0.02876]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.59472,0.18127,-0.00267],"force_p95":0.18946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40531,"mean_force":0.12053,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59015,0.16762,0.2107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10828.0,"contact_point_centroid":[0.52077,0.04792,0.10866],"force_p95":0.10125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31156,"mean_force":0.06279,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51847,0.02905,0.10718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":825.0,"contact_point_centroid":[0.59342,0.18276,0.21292],"force_p95":0.23857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30742,"mean_force":0.09218,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59,0.16447,0.21639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10157.0,"contact_point_centroid":[0.52088,0.01009,0.11319],"force_p95":0.10569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3014,"mean_force":0.06606,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51877,0.02905,0.11135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":640.0,"contact_point_centroid":[0.59258,0.14637,0.21351],"force_p95":0.22762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28496,"mean_force":0.096,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59022,0.16457,0.2168]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03047,-0.00213],"force_p95":0.16258,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24474,"mean_force":0.13327,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51752,0.02939,0.02886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5733.0,"contact_point_centroid":[0.56081,0.07587,0.21057],"force_p95":0.11897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19716,"mean_force":0.07978,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55672,0.09448,0.21088]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5689.0,"contact_point_centroid":[0.56173,0.11346,0.21096],"force_p95":0.11397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.185,"mean_force":0.07944,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5569,0.0949,0.21088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4056.0,"contact_point_centroid":[0.51724,0.01011,0.03023],"force_p95":0.08105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14773,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51629,0.02931,0.02748]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51026,0.01263,0.22525]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52244,0.02841,0.07756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5006.0,"contact_point_centroid":[0.51716,0.04848,0.02927],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08622,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5163,0.02931,0.02749]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59464,0.18107,0.016],"final_tcp_position":[0.59422,0.17297,0.1758],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.92079,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5228,0.02629,0.14779],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52456,0.02985,0.03681],"tcp_start":[0.5228,0.02629,0.14779],"tcp_to_object_dist_end":0.01235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02933,0.02555],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15399,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10862.0,"raw_peak_contact_force":0.24474,"subtask_id":"grasp_object","tcp_end":[0.51626,0.0293,0.02745],"tcp_start":[0.52456,0.02985,0.03681],"tcp_to_object_dist_end":0.01426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.54234,0.02913,0.19503],"object_pos_start":[0.53039,0.02933,0.02555],"object_to_goal_dist_end":0.18275,"object_to_goal_dist_start":0.1848,"object_z_max":0.19479,"peak_contact_force":0.10057,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21074.0,"raw_peak_contact_force":0.63566,"subtask_id":"lift_object","tcp_end":[0.52608,0.02909,0.20618],"tcp_start":[0.51626,0.0293,0.02745],"tcp_to_object_dist_end":0.01971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.60261,0.1645,0.20109],"object_pos_start":[0.54234,0.02913,0.19503],"object_to_goal_dist_end":0.09406,"object_to_goal_dist_start":0.18275,"object_z_max":0.20108,"peak_contact_force":0.15789,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11422.0,"raw_peak_contact_force":0.19716,"subtask_id":"transport_to_goal","tcp_end":[0.59189,0.16449,0.2204],"tcp_start":[0.52608,0.02909,0.20618],"tcp_to_object_dist_end":0.02209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.60261,0.1645,0.20109],"object_pos_start":[0.60261,0.1645,0.20109],"object_to_goal_dist_end":0.09406,"object_to_goal_dist_start":0.09406,"peak_contact_force":0.15804,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.59189,0.16449,0.2204],"tcp_start":[0.59189,0.16449,0.2204],"tcp_to_object_dist_end":0.02209,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59232,0.17463,-0.00069],"object_pos_start":[0.60261,0.1645,0.20109],"object_to_goal_dist_end":0.10924,"object_to_goal_dist_start":0.09406,"object_z_max":0.20109,"peak_contact_force":0.43383,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1538.0,"raw_peak_contact_force":1.92079,"subtask_id":"place_at_goal","tcp_end":[0.58705,0.16334,0.24116],"tcp_start":[0.59189,0.16449,0.2204],"tcp_to_object_dist_end":0.24217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":131.0,"n_steps_budget":900.0,"object_pos_end":[0.59464,0.18107,0.016],"object_pos_start":[0.59232,0.17463,-0.00069],"object_to_goal_dist_end":0.09238,"object_to_goal_dist_start":0.10924,"object_z_max":0.017,"peak_contact_force":0.12324,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":524.0,"raw_peak_contact_force":0.40531,"subtask_id":"place_at_goal","tcp_end":[0.59422,0.17297,0.1758],"tcp_start":[0.58705,0.16334,0.24116],"tcp_to_object_dist_end":0.16,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```