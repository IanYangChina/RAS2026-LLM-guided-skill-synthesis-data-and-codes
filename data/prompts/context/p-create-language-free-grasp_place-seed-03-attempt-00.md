## Search State

- **Seed**: 3
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1728 | 0.24 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.173) — your mutation base

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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
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
- id: lift
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    - 0.03
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
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

- **Composite score**: 0.173
- **task_score** (E): 0.242
- **fitness_score**: 0.323  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.667
- **Complexity Penalty**: 0.150

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2168 |
| descend_to_grasp | 1.00 | 1.00 | 0.0241 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.0881 |
| approach_goal | 0.00 | 1.00 | 0.1153 |
| release | 1.00 | 1.00 | 0.0236 |
| retract | 1.00 | 1.00 | 0.0866 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.506, 0.002, 0.064) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.064)→(0.498, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 27.667 | 0.143 | 0.188 |
| lift | lift | 1.00 / step_budget | (0.498, 0.002, 0.055)→(0.494, 0.002, 0.143) | (0.511, 0.002, 0.026)→(0.496, 0.007, 0.076) | 0.246→0.230 | 1.00 / 15.333 | 3249.677 | 0.397 |
| approach_goal | approach | 0.00 / step_budget | (0.494, 0.002, 0.143)→(0.558, 0.095, 0.147) | (0.496, 0.007, 0.076)→(0.514, 0.037, 0.016) | 0.230→0.227 | 1.00 / 8.000 | 0.123 | 0.856 |
| release | release | 1.00 / step_budget | (0.558, 0.095, 0.147)→(0.552, 0.094, 0.170) | (0.514, 0.037, 0.016)→(0.514, 0.037, 0.016) | 0.227→0.227 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.552, 0.094, 0.170)→(0.549, 0.094, 0.256) | (0.514, 0.037, 0.016)→(0.514, 0.037, 0.016) | 0.227→0.227 | 1.00 / 4.000 | 15.263 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.132
- phase_score: 0.246
- phase_breakdown.approach_objective_score: 0.820
- phase_breakdown.placement_objective_score: 0.000
- grasp_place_fitness: 0.265

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.323
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.242
- **Median Q (composite search score)**: 0.173
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: no_parameters
- **Mean generations**: 0.0
- **Final σ (mean)**: 0.000


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75352,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.11544,"best_fitness_score":0.26544,"best_task_score":0.13182},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1545.0,"contact_point_centroid":[0.44191,-0.01204,-0.00221],"force_p95":0.32721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58194,"mean_force":0.13764,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44358,-0.02507,0.11356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1768.0,"contact_point_centroid":[0.44379,-0.00642,0.06428],"force_p95":0.15029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26344,"mean_force":0.09319,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44427,-0.02511,0.06872]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.44399,-0.04355,0.06524],"force_p95":0.12363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26332,"mean_force":0.07951,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44421,-0.02511,0.06949]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4586,-0.02628,-0.00208],"force_p95":0.14686,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19803,"mean_force":0.12866,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44834,-0.02527,0.05866]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4779,-0.01207,0.19433]},{"body_a":"world","body_b":"grasp_target","contact_count":360.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45544,-0.02493,0.07765]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44021,-0.00787,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48722,0.03385,0.14113]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.44021,-0.00787,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52354,0.08409,0.14265]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.44021,-0.00787,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51871,0.08328,0.20581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3148.0,"contact_point_centroid":[0.44541,-0.00633,0.05364],"force_p95":0.08588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09597,"mean_force":0.06634,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44729,-0.02523,0.05763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3474.0,"contact_point_centroid":[0.44572,-0.0441,0.05369],"force_p95":0.08317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08349,"mean_force":0.06102,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4473,-0.02523,0.05763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1118.0,"contact_point_centroid":[0.4436,-0.02507,0.12812],"force_p95":0.01262,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01541,"mean_force":0.01084,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4434,-0.02506,0.1258]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4195.0,"contact_point_centroid":[0.48773,0.0341,0.14338],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01296,"mean_force":0.01061,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48743,0.0341,0.14112]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.52679,0.08463,0.13923],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01015,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52642,0.08463,0.13728]}],"total_contact_groups":14},"final_pose_error":0.01292,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.44021,-0.00787,0.01602],"final_tcp_position":[0.51886,0.08329,0.25084],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.80328,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.45734,-0.02446,0.08964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":360.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45459,-0.02549,0.06492],"tcp_start":[0.45734,-0.02446,0.08964],"tcp_to_object_dist_end":0.03911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45853,-0.02564,0.02571],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14554,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8422.0,"raw_peak_contact_force":0.19803,"tcp_end":[0.44727,-0.02523,0.0576],"tcp_start":[0.45459,-0.02549,0.06492],"tcp_to_object_dist_end":0.03382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.44021,-0.00787,0.01602],"object_pos_start":[0.45853,-0.02564,0.02571],"object_to_goal_dist_end":0.30395,"object_to_goal_dist_start":0.30324,"object_z_max":0.04504,"peak_contact_force":9748.80328,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6491.0,"raw_peak_contact_force":0.58194,"tcp_end":[0.4436,-0.02507,0.1468],"tcp_start":[0.44727,-0.02523,0.0576],"tcp_to_object_dist_end":0.13195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44021,-0.00787,0.01602],"object_pos_start":[0.44021,-0.00787,0.01602],"object_to_goal_dist_end":0.30395,"object_to_goal_dist_start":0.30395,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8195.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.5278,0.08463,0.1394],"tcp_start":[0.4436,-0.02507,0.1468],"tcp_to_object_dist_end":0.17734,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44021,-0.00787,0.01602],"object_pos_start":[0.44021,-0.00787,0.01602],"object_to_goal_dist_end":0.30395,"object_to_goal_dist_start":0.30395,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52184,0.08379,0.1634],"tcp_start":[0.5278,0.08463,0.1394],"tcp_to_object_dist_end":0.1918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.44021,-0.00787,0.01602],"object_pos_start":[0.44021,-0.00787,0.01602],"object_to_goal_dist_end":0.30395,"object_to_goal_dist_start":0.30395,"object_z_max":0.01602,"peak_contact_force":45.54305,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51886,0.08329,0.25084],"tcp_start":[0.52184,0.08379,0.1634],"tcp_to_object_dist_end":0.26389,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73077,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.15926,"best_fitness_score":0.30926,"best_task_score":0.21243},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3285.0,"contact_point_centroid":[0.55885,0.03365,-0.00221],"force_p95":0.12486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25702,"mean_force":0.13371,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55597,0.0452,0.15678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5090.0,"contact_point_centroid":[0.52866,-0.01743,0.08957],"force_p95":0.13786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29345,"mean_force":0.10157,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52527,0.0008,0.09287]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.54136,0.00058,-0.00114],"force_p95":0.2328,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29273,"mean_force":0.05855,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52777,0.00083,0.05497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.52884,0.01905,0.08963],"force_p95":0.1373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28028,"mean_force":0.1001,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52532,0.0008,0.09285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":859.0,"contact_point_centroid":[0.53404,-0.01087,0.13671],"force_p95":0.17148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20226,"mean_force":0.11544,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52811,0.00721,0.14067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":943.0,"contact_point_centroid":[0.53454,0.02596,0.13679],"force_p95":0.13563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17748,"mean_force":0.10307,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52859,0.00814,0.1408]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54432,0.00109,-0.00203],"force_p95":0.13244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15345,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5306,0.00089,0.05479]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,0.00049,0.19253]},{"body_a":"world","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53687,0.00099,0.07551]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55901,0.03363,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57179,0.0701,0.1714]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.55901,0.03363,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56726,0.06944,0.23294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.53066,-0.01788,0.05063],"force_p95":0.09721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09981,"mean_force":0.07619,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,0.00087,0.05336]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2940.0,"contact_point_centroid":[0.53026,0.01955,0.05038],"force_p95":0.09174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09184,"mean_force":0.06993,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,0.00087,0.05336]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3127.0,"contact_point_centroid":[0.55827,0.04773,0.16031],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01067,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55795,0.04773,0.15802]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.57469,0.07054,0.16936],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.00997,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57458,0.07053,0.16687]}],"total_contact_groups":15},"final_pose_error":0.01415,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55901,0.03363,0.01602],"final_tcp_position":[0.56747,0.06945,0.27767],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.25702,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.5373,0.00099,0.08712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":332.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53766,0.00101,0.06343],"tcp_start":[0.5373,0.00099,0.08712],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.00089,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13143,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7412.0,"raw_peak_contact_force":0.15345,"tcp_end":[0.52937,0.00087,0.05332],"tcp_start":[0.53766,0.00101,0.06343],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.53135,0.00077,0.10518],"object_pos_start":[0.54423,0.00089,0.02588],"object_to_goal_dist_end":0.21366,"object_to_goal_dist_start":0.25039,"object_z_max":0.10507,"peak_contact_force":0.11366,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10399.0,"raw_peak_contact_force":0.29345,"tcp_end":[0.52528,0.0008,0.14061],"tcp_start":[0.52937,0.00087,0.05332],"tcp_to_object_dist_end":0.03595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55901,0.03363,0.01602],"object_pos_start":[0.53135,0.00077,0.10518],"object_to_goal_dist_end":0.23237,"object_to_goal_dist_start":0.21366,"object_z_max":0.10523,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8214.0,"raw_peak_contact_force":1.25702,"subtask_id":"placement_objective","tcp_end":[0.57594,0.0706,0.16933],"tcp_start":[0.52528,0.0008,0.14061],"tcp_to_object_dist_end":0.15861,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55901,0.03363,0.01602],"object_pos_start":[0.55901,0.03363,0.01602],"object_to_goal_dist_end":0.23237,"object_to_goal_dist_start":0.23237,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57016,0.06985,0.19156],"tcp_start":[0.57594,0.0706,0.16933],"tcp_to_object_dist_end":0.17958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.55901,0.03363,0.01602],"object_pos_start":[0.55901,0.03363,0.01602],"object_to_goal_dist_end":0.23237,"object_to_goal_dist_start":0.23237,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56747,0.06945,0.27767],"tcp_start":[0.57016,0.06985,0.19156],"tcp_to_object_dist_end":0.26422,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74074,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.24364,"best_fitness_score":0.39364,"best_task_score":0.38305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2674.0,"contact_point_centroid":[0.54129,0.08581,-0.00225],"force_p95":0.12414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18828,"mean_force":0.13461,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55165,0.10138,0.13318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5387.0,"contact_point_centroid":[0.5153,0.01063,0.09095],"force_p95":0.13412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31674,"mean_force":0.09706,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51208,0.02893,0.09444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5358.0,"contact_point_centroid":[0.51531,0.04724,0.09147],"force_p95":0.13703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29355,"mean_force":0.09779,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51211,0.02893,0.09496]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52788,0.02847,-0.00122],"force_p95":0.2267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28705,"mean_force":0.05604,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51456,0.02909,0.05594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2255.0,"contact_point_centroid":[0.52554,0.02893,0.13173],"force_p95":0.14225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27384,"mean_force":0.10853,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52002,0.04722,0.13651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.52557,0.06561,0.13176],"force_p95":0.12243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21694,"mean_force":0.09419,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52022,0.04757,0.13647]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0307,-0.00212],"force_p95":0.15773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21168,"mean_force":0.13108,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51735,0.02927,0.05552]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51101,0.0142,0.19279]},{"body_a":"world","body_b":"grasp_target","contact_count":336.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52372,0.02914,0.07592]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54135,0.08574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56443,0.12926,0.13401]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.54135,0.08574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55942,0.12801,0.19559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2449.0,"contact_point_centroid":[0.51778,0.01051,0.0514],"force_p95":0.10465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11401,"mean_force":0.08158,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51618,0.0292,0.05415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2822.0,"contact_point_centroid":[0.51727,0.04787,0.05084],"force_p95":0.10011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10026,"mean_force":0.0732,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51619,0.0292,0.05416]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2477.0,"contact_point_centroid":[0.55436,0.10528,0.13527],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55398,0.10527,0.13302]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.56807,0.13007,0.13164],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01029,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56744,0.13005,0.12945]}],"total_contact_groups":15},"final_pose_error":0.01423,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.54135,0.08574,0.01602],"final_tcp_position":[0.55959,0.12802,0.24031],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.18828,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.52437,0.02866,0.08754],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":336.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52427,0.02971,0.06376],"tcp_start":[0.52437,0.02866,0.08754],"tcp_to_object_dist_end":0.03826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02975,0.02562],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1844,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15252,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7071.0,"raw_peak_contact_force":0.21168,"tcp_end":[0.51615,0.0292,0.05411],"tcp_start":[0.52427,0.02971,0.06376],"tcp_to_object_dist_end":0.03189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.51781,0.02913,0.10552],"object_pos_start":[0.53047,0.02975,0.02562],"object_to_goal_dist_end":0.17132,"object_to_goal_dist_start":0.1844,"object_z_max":0.1054,"peak_contact_force":0.1142,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10893.0,"raw_peak_contact_force":0.31674,"tcp_end":[0.51213,0.02894,0.14167],"tcp_start":[0.51615,0.0292,0.05411],"tcp_to_object_dist_end":0.03659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54135,0.08574,0.01602],"object_pos_start":[0.51781,0.02913,0.10552],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.17132,"object_z_max":0.10556,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9962.0,"raw_peak_contact_force":1.18828,"subtask_id":"placement_objective","tcp_end":[0.56898,0.13021,0.13197],"tcp_start":[0.51213,0.02894,0.14167],"tcp_to_object_dist_end":0.12722,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54135,0.08574,0.01602],"object_pos_start":[0.54135,0.08574,0.01602],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.14394,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56265,0.12879,0.15419],"tcp_start":[0.56898,0.13021,0.13197],"tcp_to_object_dist_end":0.14628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.54135,0.08574,0.01602],"object_pos_start":[0.54135,0.08574,0.01602],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.14394,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55959,0.12802,0.24031],"tcp_start":[0.56265,0.12879,0.15419],"tcp_to_object_dist_end":0.22897,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```