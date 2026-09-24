## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3413 | 0.23 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2818 | 0.24 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 1 | 0.2091 | 0.33 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 1 | 0.4497 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.341) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: grasp_1
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
  subtask_id: grasp_1
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: transport_arc
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.341
- **task_score** (E): 0.227
- **fitness_score**: 0.591  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2662 |
| descend_1 | 1.00 | 1.00 | 0.0017 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 0.67 | 0.67 | 0.1230 |
| transport_arc | 0.33 | 1.00 | 0.2858 |
| descend_place | 1.00 | 1.00 | 0.2413 |
| release_1 | 1.00 | 1.00 | 0.0203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.038) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.038)→(0.506, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.038)→(0.498, 0.002, 0.030) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.147 | 0.212 |
| lift_1 | lift | 0.67 / step_budget | (0.498, 0.002, 0.030)→(0.494, 0.002, 0.153) | (0.511, 0.002, 0.026)→(0.507, 0.005, 0.127) | 0.246→0.216 | 0.67 / 15.000 | 0.076 | 0.674 |
| transport_arc | approach | 0.33 / step_budget | (0.494, 0.002, 0.153)→(0.593, 0.139, 0.380) | (0.507, 0.005, 0.127)→(0.507, 0.031, 0.016) | 0.216→0.231 | 1.00 / 8.667 | 182009.639 | 1.876 |
| descend_place | descend | 1.00 / step_budget | (0.593, 0.139, 0.380)→(0.620, 0.178, 0.144) | (0.507, 0.031, 0.016)→(0.507, 0.031, 0.016) | 0.231→0.231 | 1.00 / 8.333 | 91002.752 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.178, 0.144)→(0.614, 0.176, 0.163) | (0.507, 0.031, 0.016)→(0.507, 0.031, 0.016) | 0.231→0.231 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.342
- phase_score: 0.353
- phase_breakdown.release_1_score: 0.538
- phase_breakdown.descend_1_score: 0.766
- phase_breakdown.transport_arc_score: 0.009
- phase_breakdown.approach_1_score: 0.819
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.647

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.647
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.342
- **Median Q (composite search score)**: 0.318
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.231


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71689,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11629,"transport_arc.arc_height":0.47644},"optimized_scores":{"best_composite_score":0.30896,"best_fitness_score":0.55896,"best_task_score":0.15809},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2720.0,"contact_point_centroid":[0.47435,0.00169,-0.0024],"force_p95":0.12472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89741,"mean_force":0.14007,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51653,0.06883,0.30458]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.45563,-0.02366,-0.0012],"force_p95":0.48599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70955,"mean_force":0.0783,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44606,-0.02468,0.03343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11433.0,"contact_point_centroid":[0.44558,-0.04347,0.07917],"force_p95":0.09979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30569,"mean_force":0.06005,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44366,-0.02458,0.07767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1981.0,"contact_point_centroid":[0.4529,0.00148,0.16754],"force_p95":0.18507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27683,"mean_force":0.11153,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.44711,-0.01702,0.1679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10600.0,"contact_point_centroid":[0.44554,-0.00558,0.07994],"force_p95":0.10461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27247,"mean_force":0.06365,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44369,-0.02458,0.07793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2411.0,"contact_point_centroid":[0.45314,-0.03494,0.1678],"force_p95":0.15635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26252,"mean_force":0.0965,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.44734,-0.01675,0.16871]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45861,-0.02609,-0.00214],"force_p95":0.16345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2389,"mean_force":0.13356,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44855,-0.02477,0.03255]},{"body_a":"world","body_b":"grasp_target","contact_count":3172.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47724,-0.01234,0.16848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5256.0,"contact_point_centroid":[0.44681,-0.00548,0.03288],"force_p95":0.06889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12752,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44746,-0.02473,0.03151]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45536,-0.02487,0.03859]},{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.47426,0.00172,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60125,0.17513,0.23411]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47426,0.00172,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61789,0.20152,0.11849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5471.0,"contact_point_centroid":[0.44689,-0.04406,0.03279],"force_p95":0.06861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08396,"mean_force":0.04137,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44747,-0.02473,0.03151]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2680.0,"contact_point_centroid":[0.52064,0.07356,0.31212],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0191,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52039,0.07356,0.30984]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3017.0,"contact_point_centroid":[0.60167,0.17505,0.23674],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60118,0.17504,0.23449]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.6216,0.20271,0.1175],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62098,0.20269,0.11505]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.47426,0.00172,0.01602],"final_tcp_position":[0.62298,0.20322,0.11897],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273012.6964,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3172.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45654,-0.0248,0.03961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45465,-0.02496,0.03838],"tcp_start":[0.45654,-0.0248,0.03961],"tcp_to_object_dist_end":0.01304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02497,0.02549],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15768,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12527.0,"raw_peak_contact_force":0.2389,"subtask_id":"grasp_1","tcp_end":[0.44743,-0.02473,0.03148],"tcp_start":[0.45465,-0.02496,0.03838],"tcp_to_object_dist_end":0.01256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45899,-0.02457,0.12182],"object_pos_start":[0.45847,-0.02497,0.02549],"object_to_goal_dist_end":0.28903,"object_to_goal_dist_start":0.30281,"object_z_max":0.12171,"peak_contact_force":0.11376,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22164.0,"raw_peak_contact_force":0.70955,"tcp_end":[0.44368,-0.02456,0.13686],"tcp_start":[0.44743,-0.02473,0.03148],"tcp_to_object_dist_end":0.02147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47426,0.00172,0.01602],"object_pos_start":[0.45899,-0.02457,0.12182],"object_to_goal_dist_end":0.27669,"object_to_goal_dist_start":0.28903,"object_z_max":0.1813,"peak_contact_force":273012.6964,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9792.0,"raw_peak_contact_force":1.89741,"subtask_id":"transport_arc","tcp_end":[0.58094,0.14783,0.35365],"tcp_start":[0.44368,-0.02456,0.13686],"tcp_to_object_dist_end":0.38304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.47426,0.00172,0.01602],"object_pos_start":[0.47426,0.00172,0.01602],"object_to_goal_dist_end":0.27669,"object_to_goal_dist_start":0.27669,"object_z_max":0.01602,"peak_contact_force":273008.012,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5857.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62298,0.20322,0.11897],"tcp_start":[0.58094,0.14783,0.35365],"tcp_to_object_dist_end":0.27077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47426,0.00172,0.01602],"object_pos_start":[0.47426,0.00172,0.01602],"object_to_goal_dist_end":0.27669,"object_to_goal_dist_start":0.27669,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61602,0.20081,0.13782],"tcp_start":[0.62298,0.20322,0.11897],"tcp_to_object_dist_end":0.27307,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75785,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.27235,"transport_arc.arc_height":0.23276},"optimized_scores":{"best_composite_score":0.31765,"best_fitness_score":0.56765,"best_task_score":0.18211},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3773.0,"contact_point_centroid":[0.52452,0.01864,-0.00225],"force_p95":0.12417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79077,"mean_force":0.13493,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53544,0.01501,0.34293]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.54113,0.00074,-0.00111],"force_p95":0.47889,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66362,"mean_force":0.0924,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52807,0.00083,0.03031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11856.0,"contact_point_centroid":[0.52911,-0.01787,0.09538],"force_p95":0.1352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33728,"mean_force":0.08078,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52544,0.00079,0.09461]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12563.0,"contact_point_centroid":[0.52925,0.01936,0.0964],"force_p95":0.13226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3185,"mean_force":0.07825,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52549,0.00079,0.09579]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15816,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53097,0.00089,0.0301]},{"body_a":"world","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51757,0.0005,0.16671]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53687,0.00098,0.03671]},{"body_a":"world","body_b":"grasp_target","contact_count":2668.0,"contact_point_centroid":[0.52444,0.01866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62318,0.12781,0.31801]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52444,0.01866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6375,0.1526,0.19666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53077,-0.01834,0.03134],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11516,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52971,0.00087,0.02865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53071,0.01994,0.03046],"force_p95":0.06816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09124,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52971,0.00087,0.02865]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3803.0,"contact_point_centroid":[0.53696,0.01642,0.35276],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5366,0.01642,0.35051]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2865.0,"contact_point_centroid":[0.62379,0.12781,0.32029],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62317,0.1278,0.31804]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.64024,0.15339,0.19577],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01105,"mean_force":0.01017,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63993,0.15337,0.19338]}],"total_contact_groups":14},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.52444,0.01866,0.01602],"final_tcp_position":[0.64158,0.15365,0.19752],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273016.0987,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53728,0.00099,0.03696],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":460.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.538,0.00101,0.03829],"tcp_start":[0.53728,0.00099,0.03696],"tcp_to_object_dist_end":0.01379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13006,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15816,"subtask_id":"grasp_1","tcp_end":[0.52968,0.00086,0.02862],"tcp_start":[0.538,0.00101,0.03829],"tcp_to_object_dist_end":0.01474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5349,0.00932,0.1412],"object_pos_start":[0.54417,0.00074,0.02588],"object_to_goal_dist_end":0.1932,"object_to_goal_dist_start":0.25052,"object_z_max":0.16055,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24559.0,"raw_peak_contact_force":0.66362,"tcp_end":[0.52591,0.0008,0.19041],"tcp_start":[0.52968,0.00086,0.02862],"tcp_to_object_dist_end":0.05074,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52444,0.01866,0.01602],"object_pos_start":[0.5349,0.00932,0.1412],"object_to_goal_dist_end":0.25547,"object_to_goal_dist_start":0.1932,"object_z_max":0.1412,"peak_contact_force":273016.0987,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7576.0,"raw_peak_contact_force":1.79077,"subtask_id":"transport_arc","tcp_end":[0.60532,0.10301,0.44022],"tcp_start":[0.52591,0.0008,0.19041],"tcp_to_object_dist_end":0.44,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.52444,0.01866,0.01602],"object_pos_start":[0.52444,0.01866,0.01602],"object_to_goal_dist_end":0.25547,"object_to_goal_dist_start":0.25547,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5533.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.64158,0.15365,0.19752],"tcp_start":[0.60532,0.10301,0.44022],"tcp_to_object_dist_end":0.25473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52444,0.01866,0.01602],"object_pos_start":[0.52444,0.01866,0.01602],"object_to_goal_dist_end":0.25547,"object_to_goal_dist_start":0.25547,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63608,0.15214,0.21585],"tcp_start":[0.64158,0.15365,0.19752],"tcp_to_object_dist_end":0.26498,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74038,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11413,"transport_arc.arc_height":0.49979},"optimized_scores":{"best_composite_score":0.39742,"best_fitness_score":0.64742,"best_task_score":0.34153},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2422.0,"contact_point_centroid":[0.52386,0.07168,-0.00241],"force_p95":0.13227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93842,"mean_force":0.14212,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55405,0.10279,0.28956]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.52745,0.02834,-0.0012],"force_p95":0.48131,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64978,"mean_force":0.0914,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51451,0.02927,0.03095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8724.0,"contact_point_centroid":[0.51538,0.0103,0.07593],"force_p95":0.10986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32932,"mean_force":0.07329,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51192,0.0291,0.07396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9138.0,"contact_point_centroid":[0.5154,0.04788,0.0745],"force_p95":0.10642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3282,"mean_force":0.07104,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51196,0.02911,0.07269]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1997.0,"contact_point_centroid":[0.51815,0.05307,0.15901],"force_p95":0.17716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32217,"mean_force":0.11743,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51272,0.03486,0.16139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.51792,0.01578,0.15589],"force_p95":0.17039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28544,"mean_force":0.10906,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5123,0.03403,0.15785]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0305,-0.00213],"force_p95":0.16074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23973,"mean_force":0.13272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51739,0.02947,0.03052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.51714,0.01018,0.03188],"force_p95":0.08071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14615,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51615,0.02939,0.02914]},{"body_a":"world","body_b":"grasp_target","contact_count":3352.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51103,0.01445,0.16713]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52348,0.02942,0.03702]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.52373,0.07163,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5945,0.17118,0.23024]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52373,0.07163,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59157,0.17479,0.11666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4997.0,"contact_point_centroid":[0.51706,0.04854,0.03093],"force_p95":0.07331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08691,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51616,0.02939,0.02914]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2397.0,"contact_point_centroid":[0.55668,0.10633,0.29659],"force_p95":0.01144,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55622,0.10631,0.29435]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2581.0,"contact_point_centroid":[0.59495,0.17117,0.23305],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59449,0.17115,0.23081]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.59521,0.17582,0.11504],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01017,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59463,0.17579,0.11257]}],"total_contact_groups":16},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.52373,0.07163,0.01602],"final_tcp_position":[0.59672,0.1764,0.11628],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.93842,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52425,0.02897,0.03757],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":81.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":324.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52424,0.02992,0.03829],"tcp_start":[0.52425,0.02897,0.03757],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02943,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18471,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15272,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.23973,"subtask_id":"grasp_1","tcp_end":[0.51612,0.02938,0.0291],"tcp_start":[0.52424,0.02992,0.03829],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52796,0.02931,0.11661],"object_pos_start":[0.5304,0.02943,0.02557],"object_to_goal_dist_end":0.16663,"object_to_goal_dist_start":0.18471,"object_z_max":0.1165,"peak_contact_force":0.11393,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18005.0,"raw_peak_contact_force":0.64978,"tcp_end":[0.51201,0.02912,0.13087],"tcp_start":[0.51612,0.02938,0.0291],"tcp_to_object_dist_end":0.02139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.52373,0.07163,0.01602],"object_pos_start":[0.52796,0.02931,0.11661],"object_to_goal_dist_end":0.16115,"object_to_goal_dist_start":0.16663,"object_z_max":0.16916,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8800.0,"raw_peak_contact_force":1.93842,"subtask_id":"transport_arc","tcp_end":[0.59336,0.16652,0.34475],"tcp_start":[0.51201,0.02912,0.13087],"tcp_to_object_dist_end":0.34916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.52373,0.07163,0.01602],"object_pos_start":[0.52373,0.07163,0.01602],"object_to_goal_dist_end":0.16115,"object_to_goal_dist_start":0.16115,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4993.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59672,0.1764,0.11628],"tcp_start":[0.59336,0.16652,0.34475],"tcp_to_object_dist_end":0.16235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52373,0.07163,0.01602],"object_pos_start":[0.52373,0.07163,0.01602],"object_to_goal_dist_end":0.16115,"object_to_goal_dist_start":0.16115,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58971,0.17417,0.13643],"tcp_start":[0.59672,0.1764,0.11628],"tcp_to_object_dist_end":0.17137,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```