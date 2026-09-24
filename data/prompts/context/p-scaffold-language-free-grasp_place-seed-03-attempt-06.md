## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2493 | 0.46 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1512 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2125 | 0.47 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2215 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.249) — your mutation base

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

- **Composite score**: 0.249
- **task_score** (E): 0.456
- **fitness_score**: 0.706  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1576 |
| descend_1 | 1.00 | 1.00 | 0.1137 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1430 |
| transport_1 | 0.67 | 1.00 | 0.2291 |
| descend_2 | 1.00 | 1.00 | 0.0148 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 27.040 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.506, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.034)→(0.498, 0.002, 0.025) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.141 | 0.210 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.025)→(0.506, 0.001, 0.168) | (0.511, 0.002, 0.026)→(0.522, 0.002, 0.163) | 0.246→0.223 | 1.00 / 28.667 | 0.099 | 0.658 |
| transport_1 | approach | 0.67 / step_budget | (0.506, 0.001, 0.168)→(0.612, 0.163, 0.229) | (0.522, 0.002, 0.163)→(0.621, 0.163, 0.211) | 0.223→0.076 | 1.00 / 22.000 | 0.147 | 0.189 |
| descend_2 | descend | 1.00 / force_exceeded | (0.612, 0.163, 0.229)→(0.611, 0.164, 0.214) | (0.621, 0.163, 0.211)→(0.620, 0.164, 0.195) | 0.076→0.061 | 1.00 / 22.333 | 3296.133 | 0.250 |
| release_1 | release | 1.00 / step_budget | (0.611, 0.164, 0.214)→(0.606, 0.162, 0.234) | (0.620, 0.164, 0.195)→(0.616, 0.174, 0.017) | 0.061→0.122 | 1.00 / 4.000 | 0.104 | 1.775 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.538
- phase_score: 0.466
- phase_breakdown.place_at_goal_score: 0.345
- phase_breakdown.transport_to_goal_score: 0.129
- phase_breakdown.reach_object_score: 0.676
- phase_breakdown.grasp_object_score: 0.736
- phase_breakdown.lift_object_score: 0.546
- grasp_place_fitness: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.538
- **Median Q (composite search score)**: 0.283
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9644,"average_solve_count":309.0,"average_success_count":309.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05558,"descend_1.descend_tolerance":0.01624,"descend_1.speed":0.04752,"descend_2.place_force_threshold":5.00318,"descend_2.speed":0.0321,"lift_1.lift_height":0.16008,"lift_1.speed":0.05913,"transport_1.speed":0.03655,"transport_1.transport_height":0.10149},"optimized_scores":{"best_composite_score":0.28331,"best_fitness_score":0.74046,"best_task_score":0.51823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":262.0,"contact_point_centroid":[0.61713,0.20674,-0.0057],"force_p95":1.19261,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68177,"mean_force":0.30022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61146,0.19451,0.1937]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.45599,-0.02515,-0.00141],"force_p95":0.56837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63568,"mean_force":0.17277,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44616,-0.02544,0.02908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":458.0,"contact_point_centroid":[0.61903,0.21411,0.17521],"force_p95":0.20449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34231,"mean_force":0.10073,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61535,0.19598,0.18056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":810.0,"contact_point_centroid":[0.62074,0.21466,0.19015],"force_p95":0.13555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3209,"mean_force":0.09367,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61756,0.19647,0.1949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":729.0,"contact_point_centroid":[0.62154,0.17828,0.19045],"force_p95":0.13517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31561,"mean_force":0.09915,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61756,0.19647,0.1949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":519.0,"contact_point_centroid":[0.61882,0.17795,0.17528],"force_p95":0.13729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3013,"mean_force":0.08843,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61525,0.19595,0.18034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8913.0,"contact_point_centroid":[0.44908,-0.04444,0.09279],"force_p95":0.09275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27261,"mean_force":0.05474,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44835,-0.02536,0.09127]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8480.0,"contact_point_centroid":[0.44887,-0.00623,0.09191],"force_p95":0.09673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26146,"mean_force":0.05677,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44827,-0.02536,0.08993]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02616,-0.00208],"force_p95":0.14508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22208,"mean_force":0.12876,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44811,-0.02551,0.02886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11039.0,"contact_point_centroid":[0.53608,0.06309,0.18286],"force_p95":0.12302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17784,"mean_force":0.08094,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53185,0.08165,0.18303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11102.0,"contact_point_centroid":[0.53975,0.10512,0.18356],"force_p95":0.12077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17428,"mean_force":0.07962,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53561,0.08662,0.18396]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48087,-0.01074,0.22642]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4567,-0.02402,0.09161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.44647,-0.00622,0.02961],"force_p95":0.06571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10335,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44703,-0.02547,0.02784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5436.0,"contact_point_centroid":[0.44647,-0.04477,0.02946],"force_p95":0.06597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08154,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44703,-0.02547,0.02785]}],"total_contact_groups":15},"final_pose_error":0.10186,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61774,0.20621,0.01632],"final_tcp_position":[0.61702,0.19653,0.18445],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4614,-0.02245,0.14932],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45461,-0.02574,0.03505],"tcp_start":[0.4614,-0.02245,0.14932],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02556,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30321,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14217,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.22208,"subtask_id":"grasp_object","tcp_end":[0.447,-0.02547,0.02782],"tcp_start":[0.45461,-0.02574,0.03505],"tcp_to_object_dist_end":0.01164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.47203,-0.02536,0.15997],"object_pos_start":[0.45845,-0.02556,0.02573],"object_to_goal_dist_end":0.28576,"object_to_goal_dist_start":0.30321,"object_z_max":0.1597,"peak_contact_force":0.11003,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17472.0,"raw_peak_contact_force":0.63568,"subtask_id":"lift_object","tcp_end":[0.45371,-0.02538,0.16638],"tcp_start":[0.447,-0.02547,0.02782],"tcp_to_object_dist_end":0.01941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.62657,0.19597,0.18246],"object_pos_start":[0.47203,-0.02536,0.15997],"object_to_goal_dist_end":0.06952,"object_to_goal_dist_start":0.28576,"object_z_max":0.18244,"peak_contact_force":0.12674,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22141.0,"raw_peak_contact_force":0.17784,"subtask_id":"transport_to_goal","tcp_end":[0.61872,0.19611,0.20451],"tcp_start":[0.45371,-0.02538,0.16638],"tcp_to_object_dist_end":0.02341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":81.0,"n_steps_budget":1000.0,"object_pos_end":[0.62454,0.19646,0.16128],"object_pos_start":[0.62657,0.19597,0.18246],"object_to_goal_dist_end":0.04892,"object_to_goal_dist_start":0.06952,"object_z_max":0.18246,"peak_contact_force":9760.30694,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1539.0,"raw_peak_contact_force":0.3209,"subtask_id":"place_at_goal","tcp_end":[0.61702,0.19653,0.18445],"tcp_start":[0.61872,0.19611,0.20451],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61774,0.20621,0.01632],"object_pos_start":[0.62454,0.19646,0.16128],"object_to_goal_dist_end":0.0986,"object_to_goal_dist_start":0.04892,"object_z_max":0.16128,"peak_contact_force":0.10747,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1239.0,"raw_peak_contact_force":1.68177,"subtask_id":"place_at_goal","tcp_end":[0.61141,0.19449,0.20352],"tcp_start":[0.61702,0.19653,0.18445],"tcp_to_object_dist_end":0.18767,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06324,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05721,"descend_1.descend_tolerance":0.01661,"descend_1.speed":0.0608,"descend_2.place_force_threshold":7.26272,"descend_2.speed":0.05937,"lift_1.lift_height":0.12108,"lift_1.speed":0.06087,"transport_1.speed":0.05241,"transport_1.transport_height":0.1862},"optimized_scores":{"best_composite_score":0.17532,"best_fitness_score":0.63246,"best_task_score":0.31165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":262.0,"contact_point_centroid":[0.63122,0.15331,-0.00916],"force_p95":1.82933,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42243,"mean_force":0.38411,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62424,0.1296,0.3336]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.54165,0.00071,-0.00137],"force_p95":0.56223,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67246,"mean_force":0.149,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52865,0.00083,0.02501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6838.0,"contact_point_centroid":[0.53385,-0.01829,0.07633],"force_p95":0.09455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29954,"mean_force":0.06049,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53214,0.00072,0.07451]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.63184,0.11244,0.31746],"force_p95":0.22691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29788,"mean_force":0.13789,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62658,0.13044,0.32325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7150.0,"contact_point_centroid":[0.53342,0.01972,0.07463],"force_p95":0.09752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29125,"mean_force":0.05836,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53197,0.00073,0.07278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11701.0,"contact_point_centroid":[0.5816,0.04326,0.21822],"force_p95":0.14725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28291,"mean_force":0.08681,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57836,0.06198,0.21873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.62676,0.14762,0.32022],"force_p95":0.19516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25551,"mean_force":0.11043,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62687,0.13024,0.32481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":49.0,"contact_point_centroid":[0.62955,0.11182,0.3199],"force_p95":0.22799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24871,"mean_force":0.13821,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62687,0.13024,0.32481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":217.0,"contact_point_centroid":[0.62788,0.14684,0.31774],"force_p95":0.15778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19824,"mean_force":0.06004,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6264,0.1304,0.32244]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16067,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53087,0.00088,0.02528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13581.0,"contact_point_centroid":[0.58483,0.0844,0.22491],"force_p95":0.10452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14672,"mean_force":0.07325,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58121,0.06603,0.22502]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51605,0.00044,0.22489]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53498,0.00095,0.0895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53071,-0.01834,0.02653],"force_p95":0.07603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11019,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52961,0.00086,0.02385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53064,0.01994,0.02566],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09676,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52961,0.00086,0.02385]}],"total_contact_groups":15},"final_pose_error":0.16684,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63161,0.15334,0.01702],"final_tcp_position":[0.62686,0.13043,0.32432],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":114.62753,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":40.45316,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53475,0.00093,0.1472],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53831,0.00102,0.03391],"tcp_start":[0.53475,0.00093,0.1472],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12965,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16067,"subtask_id":"grasp_object","tcp_end":[0.52958,0.00086,0.02381],"tcp_start":[0.53831,0.00102,0.03391],"tcp_to_object_dist_end":0.01472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.55594,0.00077,0.12485],"object_pos_start":[0.54415,0.00072,0.02588],"object_to_goal_dist_end":0.19376,"object_to_goal_dist_start":0.25053,"object_z_max":0.12462,"peak_contact_force":0.10625,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14076.0,"raw_peak_contact_force":0.67246,"subtask_id":"lift_object","tcp_end":[0.53848,0.00067,0.12804],"tcp_start":[0.52958,0.00086,0.02381],"tcp_to_object_dist_end":0.01774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63531,0.1303,0.30351],"object_pos_start":[0.55594,0.00077,0.12485],"object_to_goal_dist_end":0.11644,"object_to_goal_dist_start":0.19376,"object_z_max":0.30335,"peak_contact_force":0.22391,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25282.0,"raw_peak_contact_force":0.28291,"subtask_id":"transport_to_goal","tcp_end":[0.62685,0.13004,0.32493],"tcp_start":[0.53848,0.00067,0.12804],"tcp_to_object_dist_end":0.02303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.63506,0.13067,0.30272],"object_pos_start":[0.63531,0.1303,0.30351],"object_to_goal_dist_end":0.11562,"object_to_goal_dist_start":0.11644,"object_z_max":0.30355,"peak_contact_force":114.62753,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":119.0,"raw_peak_contact_force":0.25551,"subtask_id":"place_at_goal","tcp_end":[0.62686,0.13043,0.32432],"tcp_start":[0.62685,0.13004,0.32493],"tcp_to_object_dist_end":0.0231,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63161,0.15334,0.01702],"object_pos_start":[0.63506,0.13067,0.30272],"object_to_goal_dist_end":0.17488,"object_to_goal_dist_start":0.11562,"object_z_max":0.30272,"peak_contact_force":0.09877,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":560.0,"raw_peak_contact_force":2.42243,"subtask_id":"place_at_goal","tcp_end":[0.62426,0.1296,0.34357],"tcp_start":[0.62686,0.13043,0.32432],"tcp_to_object_dist_end":0.32749,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3691,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07078,"descend_1.descend_tolerance":0.00972,"descend_1.speed":0.08705,"descend_2.place_force_threshold":6.88959,"descend_2.speed":0.04799,"lift_1.lift_height":0.20363,"lift_1.speed":0.04922,"transport_1.speed":0.06126,"transport_1.transport_height":0.05235},"optimized_scores":{"best_composite_score":0.28914,"best_fitness_score":0.74628,"best_task_score":0.53758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":273.0,"contact_point_centroid":[0.59615,0.16374,-0.00494],"force_p95":1.00299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21978,"mean_force":0.26877,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58214,0.16275,0.1447]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.52619,0.02867,-0.00149],"force_p95":0.63155,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66646,"mean_force":0.21226,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51528,0.02931,0.02582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13229.0,"contact_point_centroid":[0.51952,0.04818,0.11517],"force_p95":0.07926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30221,"mean_force":0.05397,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51896,0.02912,0.11307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12474.0,"contact_point_centroid":[0.51995,0.01,0.1198],"force_p95":0.08186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29266,"mean_force":0.05612,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51928,0.02912,0.1173]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03045,-0.00213],"force_p95":0.16046,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24682,"mean_force":0.1328,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51751,0.02948,0.02595]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1766.0,"contact_point_centroid":[0.59133,0.14498,0.14551],"force_p95":0.09106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17288,"mean_force":0.06528,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58882,0.16382,0.14453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.59125,0.18274,0.14498],"force_p95":0.08924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16264,"mean_force":0.06613,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58883,0.16383,0.14452]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4053.0,"contact_point_centroid":[0.51724,0.0102,0.02734],"force_p95":0.08075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14292,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51628,0.0294,0.02459]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51034,0.01268,0.22496]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":945.0,"contact_point_centroid":[0.5872,0.14504,0.13067],"force_p95":0.08648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13083,"mean_force":0.05552,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58654,0.16413,0.13054]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52242,0.02806,0.08987]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.58758,0.18302,0.13013],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10709,"mean_force":0.04759,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58656,0.16414,0.13059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7240.0,"contact_point_centroid":[0.55794,0.07459,0.18371],"force_p95":0.08876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10607,"mean_force":0.05931,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55612,0.09348,0.18252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6743.0,"contact_point_centroid":[0.55898,0.11435,0.1829],"force_p95":0.08971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10592,"mean_force":0.06271,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55704,0.09537,0.1818]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5000.0,"contact_point_centroid":[0.51716,0.04856,0.02639],"force_p95":0.07313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09068,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51629,0.0294,0.0246]}],"total_contact_groups":15},"final_pose_error":0.05914,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59903,0.16363,0.01623],"final_tcp_position":[0.58849,0.16467,0.13407],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":40.54342,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":40.54342,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5229,0.02634,0.14748],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.5248,0.02996,0.03418],"tcp_start":[0.5229,0.02634,0.14748],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02936,0.02558],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15193,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10853.0,"raw_peak_contact_force":0.24682,"subtask_id":"grasp_object","tcp_end":[0.51626,0.02939,0.02456],"tcp_start":[0.5248,0.02996,0.03418],"tcp_to_object_dist_end":0.01415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.5385,0.02922,0.20401],"object_pos_start":[0.53037,0.02936,0.02558],"object_to_goal_dist_end":0.18837,"object_to_goal_dist_start":0.18477,"object_z_max":0.20376,"peak_contact_force":0.08011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25794.0,"raw_peak_contact_force":0.66646,"subtask_id":"lift_object","tcp_end":[0.52618,0.02913,0.2099],"tcp_start":[0.51626,0.02939,0.02456],"tcp_to_object_dist_end":0.01365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.60213,0.16244,0.14629],"object_pos_start":[0.5385,0.02922,0.20401],"object_to_goal_dist_end":0.04147,"object_to_goal_dist_start":0.18837,"object_z_max":0.20419,"peak_contact_force":0.0892,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13983.0,"raw_peak_contact_force":0.10607,"subtask_id":"transport_to_goal","tcp_end":[0.59037,0.16253,0.15757],"tcp_start":[0.52618,0.02913,0.2099],"tcp_to_object_dist_end":0.0163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.59918,0.16444,0.12155],"object_pos_start":[0.60213,0.16244,0.14629],"object_to_goal_dist_end":0.01966,"object_to_goal_dist_start":0.04147,"object_z_max":0.14629,"peak_contact_force":13.46529,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3570.0,"raw_peak_contact_force":0.17288,"subtask_id":"place_at_goal","tcp_end":[0.58849,0.16467,0.13407],"tcp_start":[0.59037,0.16253,0.15757],"tcp_to_object_dist_end":0.01647,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59903,0.16363,0.01623],"object_pos_start":[0.59918,0.16444,0.12155],"object_to_goal_dist_end":0.0931,"object_to_goal_dist_start":0.01966,"object_z_max":0.12155,"peak_contact_force":0.10646,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2344.0,"raw_peak_contact_force":1.21978,"subtask_id":"place_at_goal","tcp_end":[0.58205,0.16273,0.155],"tcp_start":[0.58849,0.16467,0.13407],"tcp_to_object_dist_end":0.1398,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```