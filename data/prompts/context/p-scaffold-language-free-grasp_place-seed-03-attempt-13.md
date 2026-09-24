## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4537 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1288 | 0.46 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0774 | 0.47 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.454) — your mutation base

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
  target_entity: object
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
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.454
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1574 |
| descend_1 | 1.00 | 1.00 | 0.1035 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 1.00 | 1.00 | 0.1534 |
| transport_1 | 1.00 | 1.00 | 0.2266 |
| descend_2 | 1.00 | 1.00 | 0.0748 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.045)→(0.498, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.000 | 0.146 | 0.204 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.035)→(0.506, 0.001, 0.188) | (0.511, 0.002, 0.026)→(0.518, 0.001, 0.177) | 0.246→0.226 | 1.00 / 38.000 | 0.082 | 0.481 |
| transport_1 | approach | 1.00 / step_budget | (0.506, 0.001, 0.188)→(0.617, 0.170, 0.235) | (0.518, 0.001, 0.177)→(0.624, 0.169, 0.217) | 0.226→0.081 | 1.00 / 37.667 | 0.077 | 0.106 |
| descend_2 | descend | 1.00 / step_budget | (0.617, 0.170, 0.235)→(0.620, 0.177, 0.161) | (0.624, 0.169, 0.217)→(0.631, 0.176, 0.142) | 0.081→0.010 | 1.00 / 28.333 | 90.280 | 0.178 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.682
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.597
- phase_breakdown.place_at_goal_score: 0.605
- phase_breakdown.transport_to_goal_score: 0.426
- phase_breakdown.reach_object_score: 0.671
- phase_breakdown.grasp_object_score: 0.766
- phase_breakdown.lift_object_score: 0.435
- grasp_place_fitness: 0.975

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.975
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.453
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.278


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02528,"average_solve_count":356.0,"average_success_count":356.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05927,"descend_1.speed":0.05537,"descend_2.place_z_offset":0.00051,"descend_2.speed":0.0291,"lift_1.lift_height":0.2253,"lift_1.speed":0.05573,"transport_1.speed":0.06355,"transport_1.transport_height":0.12048},"optimized_scores":{"best_composite_score":0.45452,"best_fitness_score":0.97452,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.45618,-0.02533,-0.0016],"force_p95":0.4565,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50175,"mean_force":0.21116,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44678,-0.02513,0.03856]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7420.0,"contact_point_centroid":[0.44997,-0.0443,0.12943],"force_p95":0.08006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28266,"mean_force":0.05433,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44974,-0.02515,0.12757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7422.0,"contact_point_centroid":[0.44994,-0.00601,0.12946],"force_p95":0.07682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27408,"mean_force":0.05403,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44974,-0.02515,0.12755]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.0262,-0.0021],"force_p95":0.15138,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21507,"mean_force":0.1303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44868,-0.0252,0.03856]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2323.0,"contact_point_centroid":[0.62186,0.17965,0.18839],"force_p95":0.08781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17032,"mean_force":0.06043,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62003,0.19863,0.18666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2564.0,"contact_point_centroid":[0.62186,0.21772,0.18714],"force_p95":0.08251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16612,"mean_force":0.05736,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62005,0.19865,0.18653]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48082,-0.01075,0.22638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4807.0,"contact_point_centroid":[0.4478,-0.00597,0.03948],"force_p95":0.07147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12663,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44762,-0.02516,0.03756]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45766,-0.02385,0.09827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16505.0,"contact_point_centroid":[0.53897,0.07056,0.22331],"force_p95":0.07223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1063,"mean_force":0.04937,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53891,0.08972,0.22182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16885.0,"contact_point_centroid":[0.54067,0.11127,0.22348],"force_p95":0.07127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09818,"mean_force":0.04782,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54069,0.09213,0.22187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.44783,-0.0444,0.03943],"force_p95":0.0719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07961,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44763,-0.02516,0.03756]}],"total_contact_groups":12},"final_pose_error":0.02462,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63201,0.20305,0.11733],"final_tcp_position":[0.62347,0.20325,0.1378],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":270.62739,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46137,-0.02243,0.1494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":860.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45548,-0.02542,0.04534],"tcp_start":[0.46137,-0.02243,0.1494],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02544,0.02564],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30312,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14762,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11571.0,"raw_peak_contact_force":0.21507,"subtask_id":"grasp_object","tcp_end":[0.4476,-0.02516,0.03753],"tcp_start":[0.45548,-0.02542,0.04534],"tcp_to_object_dist_end":0.01613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.46462,-0.02538,0.20702],"object_pos_start":[0.45848,-0.02544,0.02564],"object_to_goal_dist_end":0.30098,"object_to_goal_dist_start":0.30312,"object_z_max":0.20654,"peak_contact_force":0.07601,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14910.0,"raw_peak_contact_force":0.50175,"subtask_id":"lift_object","tcp_end":[0.45485,-0.02528,0.22145],"tcp_start":[0.4476,-0.02516,0.03753],"tcp_to_object_dist_end":0.01743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.62451,0.19509,0.20603],"object_pos_start":[0.46462,-0.02538,0.20702],"object_to_goal_dist_end":0.09301,"object_to_goal_dist_start":0.30098,"object_z_max":0.2078,"peak_contact_force":0.06679,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33390.0,"raw_peak_contact_force":0.1063,"subtask_id":"transport_to_goal","tcp_end":[0.6183,0.19515,0.22523],"tcp_start":[0.45485,-0.02528,0.22145],"tcp_to_object_dist_end":0.02018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.63201,0.20305,0.11733],"object_pos_start":[0.62451,0.19509,0.20603],"object_to_goal_dist_end":0.00636,"object_to_goal_dist_start":0.09301,"object_z_max":0.20603,"peak_contact_force":270.62739,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4887.0,"raw_peak_contact_force":0.17032,"subtask_id":"place_at_goal","tcp_end":[0.62347,0.20325,0.1378],"tcp_start":[0.6183,0.19515,0.22523],"tcp_to_object_dist_end":0.02219,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97772,"average_solve_count":359.0,"average_success_count":359.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09909,"descend_1.speed":0.06693,"descend_2.place_z_offset":0.00831,"descend_2.speed":0.02352,"lift_1.lift_height":0.14521,"lift_1.speed":0.03796,"transport_1.speed":0.05047,"transport_1.transport_height":0.14227},"optimized_scores":{"best_composite_score":0.45321,"best_fitness_score":0.97321,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.54096,0.00075,-0.00158],"force_p95":0.45038,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4798,"mean_force":0.23798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52827,0.00082,0.03446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4561.0,"contact_point_centroid":[0.53199,-0.01846,0.08517],"force_p95":0.0841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26893,"mean_force":0.05832,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53165,0.00073,0.08238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5118.0,"contact_point_centroid":[0.53202,0.01981,0.08575],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25846,"mean_force":0.05351,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53179,0.00073,0.08365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2201.0,"contact_point_centroid":[0.64611,0.17144,0.27628],"force_p95":0.09195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18868,"mean_force":0.06732,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64199,0.15269,0.27551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.64483,0.1339,0.27658],"force_p95":0.10865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17889,"mean_force":0.07574,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64198,0.15268,0.27586]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15604,"mean_force":0.12542,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53039,0.00087,0.03524]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51632,0.00045,0.2248]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53549,0.00095,0.09657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53043,-0.01835,0.0365],"force_p95":0.07623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11911,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52917,0.00085,0.03384]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17599.0,"contact_point_centroid":[0.58878,0.05606,0.22769],"force_p95":0.08569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09883,"mean_force":0.05602,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58741,0.07509,0.22571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17721.0,"contact_point_centroid":[0.59093,0.09708,0.23085],"force_p95":0.07995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09756,"mean_force":0.05522,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5895,0.07807,0.22923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53033,0.01992,0.03563],"force_p95":0.0683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09547,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52917,0.00085,0.03384]}],"total_contact_groups":12},"final_pose_error":0.02434,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65375,0.15501,0.2032],"final_tcp_position":[0.64356,0.15529,0.22325],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.4798,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53495,0.00093,0.14752],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53812,0.00101,0.04454],"tcp_start":[0.53495,0.00093,0.14752],"tcp_to_object_dist_end":0.01953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00073,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1305,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15604,"subtask_id":"grasp_object","tcp_end":[0.52914,0.00085,0.0338],"tcp_start":[0.53812,0.00101,0.04454],"tcp_to_object_dist_end":0.01701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.55078,0.00054,0.13254],"object_pos_start":[0.54419,0.00073,0.02587],"object_to_goal_dist_end":0.19398,"object_to_goal_dist_start":0.25052,"object_z_max":0.13209,"peak_contact_force":0.08372,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9761.0,"raw_peak_contact_force":0.4798,"subtask_id":"lift_object","tcp_end":[0.53815,0.00068,0.14188],"tcp_start":[0.52914,0.00085,0.0338],"tcp_to_object_dist_end":0.01572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.64874,0.15051,0.29777],"object_pos_start":[0.55078,0.00054,0.13254],"object_to_goal_dist_end":0.10694,"object_to_goal_dist_start":0.19398,"object_z_max":0.29763,"peak_contact_force":0.08698,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35320.0,"raw_peak_contact_force":0.09883,"subtask_id":"transport_to_goal","tcp_end":[0.64123,0.15075,0.31595],"tcp_start":[0.53815,0.00068,0.14188],"tcp_to_object_dist_end":0.01967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.65375,0.15501,0.2032],"object_pos_start":[0.64874,0.15051,0.29777],"object_to_goal_dist_end":0.0139,"object_to_goal_dist_start":0.10694,"object_z_max":0.29779,"peak_contact_force":0.10902,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4105.0,"raw_peak_contact_force":0.18868,"subtask_id":"place_at_goal","tcp_end":[0.64356,0.15529,0.22325],"tcp_start":[0.64123,0.15075,0.31595],"tcp_to_object_dist_end":0.0225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30389,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0679,"descend_1.speed":0.09998,"descend_2.place_z_offset":-0.00938,"descend_2.speed":0.04,"lift_1.lift_height":0.20598,"lift_1.speed":0.02748,"transport_1.speed":0.07209,"transport_1.transport_height":0.05984},"optimized_scores":{"best_composite_score":0.45328,"best_fitness_score":0.97328,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.52752,0.02896,-0.00169],"force_p95":0.44823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46241,"mean_force":0.2376,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51503,0.02897,0.03516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7706.0,"contact_point_centroid":[0.519,0.048,0.11554],"force_p95":0.07952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26389,"mean_force":0.05229,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51895,0.0289,0.11359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6965.0,"contact_point_centroid":[0.519,0.00971,0.11431],"force_p95":0.08216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25268,"mean_force":0.05581,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51879,0.0289,0.11162]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03052,-0.00216],"force_p95":0.16739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2408,"mean_force":0.13434,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51724,0.02913,0.03577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.59393,0.14779,0.14634],"force_p95":0.08497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17379,"mean_force":0.05758,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59171,0.16652,0.1454]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1178.0,"contact_point_centroid":[0.59392,0.18553,0.14725],"force_p95":0.10158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16619,"mean_force":0.06908,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59166,0.16639,0.1461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4066.0,"contact_point_centroid":[0.51708,0.00984,0.03718],"force_p95":0.08176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15357,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51605,0.02905,0.03445]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51029,0.01264,0.22522]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52299,0.02788,0.09679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7784.0,"contact_point_centroid":[0.55791,0.0763,0.18296],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11218,"mean_force":0.05312,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55691,0.09534,0.18078]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7460.0,"contact_point_centroid":[0.55868,0.11607,0.18253],"force_p95":0.07876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09965,"mean_force":0.05517,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5577,0.09699,0.18033]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5030.0,"contact_point_centroid":[0.51699,0.04823,0.03623],"force_p95":0.07468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08176,"mean_force":0.04452,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51606,0.02905,0.03445]}],"total_contact_groups":12},"final_pose_error":0.0246,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60631,0.1713,0.105],"final_tcp_position":[0.59399,0.17101,0.12086],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.46241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52282,0.02627,0.14787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":780.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52484,0.02961,0.0447],"tcp_start":[0.52282,0.02627,0.14787],"tcp_to_object_dist_end":0.01956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02926,0.02548],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15871,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10896.0,"raw_peak_contact_force":0.2408,"subtask_id":"grasp_object","tcp_end":[0.51602,0.02905,0.03441],"tcp_start":[0.52484,0.02961,0.0447],"tcp_to_object_dist_end":0.01695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.53749,0.02899,0.19065],"object_pos_start":[0.53043,0.02926,0.02548],"object_to_goal_dist_end":0.18247,"object_to_goal_dist_start":0.18487,"object_z_max":0.19019,"peak_contact_force":0.08521,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14761.0,"raw_peak_contact_force":0.46241,"subtask_id":"lift_object","tcp_end":[0.52581,0.02901,0.20182],"tcp_start":[0.51602,0.02905,0.03441],"tcp_to_object_dist_end":0.01617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.60007,0.16281,0.14849],"object_pos_start":[0.53749,0.02899,0.19065],"object_to_goal_dist_end":0.04339,"object_to_goal_dist_start":0.18247,"object_z_max":0.19129,"peak_contact_force":0.07857,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15244.0,"raw_peak_contact_force":0.11218,"subtask_id":"transport_to_goal","tcp_end":[0.59053,0.16285,0.16342],"tcp_start":[0.52581,0.02901,0.20182],"tcp_to_object_dist_end":0.01771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":77.0,"n_steps_budget":1000.0,"object_pos_end":[0.60631,0.1713,0.105],"object_pos_start":[0.60007,0.16281,0.14849],"object_to_goal_dist_end":0.00924,"object_to_goal_dist_start":0.04339,"object_z_max":0.14849,"peak_contact_force":0.10423,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2506.0,"raw_peak_contact_force":0.17379,"subtask_id":"place_at_goal","tcp_end":[0.59399,0.17101,0.12086],"tcp_start":[0.59053,0.16285,0.16342],"tcp_to_object_dist_end":0.02009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```