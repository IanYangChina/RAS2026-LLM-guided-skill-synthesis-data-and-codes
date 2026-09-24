## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3553 | 0.42 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2541 | 0.39 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2890 | 0.28 | ❌ rejected |
| 4 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 1 | 0.4518 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3413 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.355) — your mutation base

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
- id: lift_1
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
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
- id: descend_place
  type: descend
  generator: linear_cartesian
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current

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
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.355
- **task_score** (E): 0.415
- **fitness_score**: 0.685  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2662 |
| descend_1 | 1.00 | 1.00 | 0.0017 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.1182 |
| transport_arc | 1.00 | 1.00 | 0.2077 |
| descend_place | 1.00 | 1.00 | 0.0190 |
| release_1 | 1.00 | 1.00 | 0.0206 |
| retract_1 | 1.00 | 1.00 | 0.1303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.038) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.038)→(0.506, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.038)→(0.498, 0.002, 0.030) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.147 | 0.212 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.030)→(0.494, 0.002, 0.148) | (0.511, 0.002, 0.026)→(0.513, 0.002, 0.138) | 0.246→0.217 | 1.00 / 23.000 | 0.114 | 0.646 |
| transport_arc | approach | 1.00 / step_budget | (0.494, 0.002, 0.148)→(0.613, 0.168, 0.138) | (0.513, 0.002, 0.138)→(0.583, 0.139, 0.014) | 0.217→0.142 | 1.00 / 6.667 | 94254.864 | 1.542 |
| descend_place | descend | 1.00 / step_budget | (0.613, 0.168, 0.138)→(0.622, 0.180, 0.149) | (0.583, 0.139, 0.014)→(0.583, 0.141, 0.016) | 0.142→0.139 | 1.00 / 8.333 | 91001.528 | 0.326 |
| release_1 | release | 1.00 / step_budget | (0.622, 0.180, 0.149)→(0.616, 0.178, 0.169) | (0.583, 0.141, 0.016)→(0.583, 0.141, 0.016) | 0.139→0.139 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.616, 0.178, 0.169)→(0.614, 0.177, 0.299) | (0.583, 0.141, 0.016)→(0.583, 0.141, 0.016) | 0.139→0.139 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.719
- phase_breakdown.release_1_score: 0.543
- phase_breakdown.descend_1_score: 0.766
- phase_breakdown.transport_arc_score: 0.673
- phase_breakdown.approach_1_score: 0.819
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.378
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.368


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57848,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.02452,"lift_1.lift_height":0.15349,"transport_arc.arc_height":0.43739},"optimized_scores":{"best_composite_score":0.37754,"best_fitness_score":0.70754,"best_task_score":0.45524},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":544.0,"contact_point_centroid":[0.58862,0.16089,-0.00372],"force_p95":0.98937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71525,"mean_force":0.22547,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60158,0.17579,0.13995]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.4558,-0.02404,-0.00145],"force_p95":0.59948,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63226,"mean_force":0.15264,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44625,-0.02469,0.03299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7157.0,"contact_point_centroid":[0.4456,-0.04359,0.09202],"force_p95":0.10123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30671,"mean_force":0.05992,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44409,-0.02459,0.09031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5110.0,"contact_point_centroid":[0.49918,0.02224,0.18114],"force_p95":0.16581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27963,"mean_force":0.10317,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49382,0.0407,0.18086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6677.0,"contact_point_centroid":[0.44555,-0.00552,0.09294],"force_p95":0.1056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27385,"mean_force":0.06301,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44412,-0.02459,0.09065]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6010.0,"contact_point_centroid":[0.5049,0.06627,0.18081],"force_p95":0.1444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26294,"mean_force":0.09096,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49964,0.04807,0.18117]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45861,-0.02609,-0.00214],"force_p95":0.16345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2389,"mean_force":0.13356,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44855,-0.02477,0.03255]},{"body_a":"world","body_b":"grasp_target","contact_count":3172.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47724,-0.01234,0.16848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5256.0,"contact_point_centroid":[0.44681,-0.00548,0.03288],"force_p95":0.06889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12752,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44746,-0.02473,0.03151]},{"body_a":"world","body_b":"grasp_target","contact_count":3384.0,"contact_point_centroid":[0.58688,0.15882,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1238,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62006,0.20099,0.12214]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45536,-0.02487,0.03859]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58688,0.15882,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62036,0.20426,0.12849]},{"body_a":"world","body_b":"grasp_target","contact_count":2120.0,"contact_point_centroid":[0.58688,0.15882,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61563,0.20245,0.21225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5471.0,"contact_point_centroid":[0.44689,-0.04406,0.03279],"force_p95":0.06861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08396,"mean_force":0.04137,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44747,-0.02473,0.03151]},{"body_a":"left_finger","body_b":"right_finger","contact_count":390.0,"contact_point_centroid":[0.60714,0.18241,0.13627],"force_p95":0.01441,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01113,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60686,0.18241,0.13392]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3592.0,"contact_point_centroid":[0.62053,0.20102,0.12434],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62008,0.20101,0.12216]}],"total_contact_groups":17},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.58688,0.15882,0.01602],"final_tcp_position":[0.61618,0.20257,0.27793],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273014.92694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3172.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45654,-0.0248,0.03961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45465,-0.02496,0.03838],"tcp_start":[0.45654,-0.0248,0.03961],"tcp_to_object_dist_end":0.01304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02497,0.02549],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15768,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12527.0,"raw_peak_contact_force":0.2389,"subtask_id":"grasp_1","tcp_end":[0.44743,-0.02473,0.03148],"tcp_start":[0.45465,-0.02496,0.03838],"tcp_to_object_dist_end":0.01256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":400.0,"n_steps_budget":960.0,"object_pos_end":[0.46219,-0.02471,0.15512],"object_pos_start":[0.45847,-0.02497,0.02549],"object_to_goal_dist_end":0.29007,"object_to_goal_dist_start":0.30281,"object_z_max":0.15484,"peak_contact_force":0.10993,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13908.0,"raw_peak_contact_force":0.63226,"tcp_end":[0.44413,-0.02457,0.16539],"tcp_start":[0.44743,-0.02473,0.03148],"tcp_to_object_dist_end":0.02078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.58688,0.15881,0.016],"object_pos_start":[0.46219,-0.02471,0.15512],"object_to_goal_dist_end":0.11806,"object_to_goal_dist_start":0.29007,"object_z_max":0.17149,"peak_contact_force":273014.92694,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12054.0,"raw_peak_contact_force":1.71525,"subtask_id":"transport_arc","tcp_end":[0.61666,0.19478,0.12028],"tcp_start":[0.44413,-0.02457,0.16539],"tcp_to_object_dist_end":0.11425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.58688,0.15882,0.01602],"object_pos_start":[0.58688,0.15881,0.016],"object_to_goal_dist_end":0.11804,"object_to_goal_dist_start":0.11806,"object_z_max":0.01602,"peak_contact_force":273004.33861,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6976.0,"raw_peak_contact_force":0.1238,"tcp_end":[0.625,0.20592,0.12847],"tcp_start":[0.61666,0.19478,0.12028],"tcp_to_object_dist_end":0.12774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58688,0.15882,0.01602],"object_pos_start":[0.58688,0.15882,0.01602],"object_to_goal_dist_end":0.11804,"object_to_goal_dist_start":0.11804,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61851,0.20356,0.1477],"tcp_start":[0.625,0.20592,0.12847],"tcp_to_object_dist_end":0.14262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":530.0,"n_steps_budget":960.0,"object_pos_end":[0.58688,0.15882,0.01602],"object_pos_start":[0.58688,0.15882,0.01602],"object_to_goal_dist_end":0.11804,"object_to_goal_dist_start":0.11804,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2120.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61618,0.20257,0.27793],"tcp_start":[0.61851,0.20356,0.1477],"tcp_to_object_dist_end":0.26715,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61307,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.02398,"lift_1.lift_height":0.13763,"transport_arc.arc_height":0.49971},"optimized_scores":{"best_composite_score":0.27128,"best_fitness_score":0.60128,"best_task_score":0.24936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1335.0,"contact_point_centroid":[0.56352,0.08311,-0.00279],"force_p95":0.36727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72053,"mean_force":0.16407,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59982,0.1001,0.18396]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.54118,0.00048,-0.00134],"force_p95":0.61426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65751,"mean_force":0.14326,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52842,0.00084,0.02991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5485.0,"contact_point_centroid":[0.52894,-0.01807,0.08304],"force_p95":0.11099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33689,"mean_force":0.075,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52576,0.00079,0.08085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5822.0,"contact_point_centroid":[0.52903,0.01958,0.08133],"force_p95":0.10897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31808,"mean_force":0.0715,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5258,0.00079,0.0794]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1545.0,"contact_point_centroid":[0.54259,0.03612,0.15459],"force_p95":0.21094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27914,"mean_force":0.11277,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53673,0.01787,0.1557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.54102,-0.00308,0.15385],"force_p95":0.21223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27379,"mean_force":0.10626,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53501,0.01538,0.15435]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15816,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53097,0.00089,0.0301]},{"body_a":"world","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51757,0.0005,0.16671]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53687,0.00098,0.03671]},{"body_a":"world","body_b":"grasp_target","contact_count":3384.0,"contact_point_centroid":[0.56293,0.08343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63872,0.15155,0.19345]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56293,0.08343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63995,0.15551,0.20428]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.56293,0.08343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63658,0.15441,0.2877]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53077,-0.01834,0.03134],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11516,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52971,0.00087,0.02865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53071,0.01994,0.03046],"force_p95":0.06816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09124,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52971,0.00087,0.02865]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1218.0,"contact_point_centroid":[0.6052,0.10635,0.1873],"force_p95":0.01243,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01586,"mean_force":0.01073,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60473,0.10634,0.18501]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3584.0,"contact_point_centroid":[0.63924,0.15158,0.19566],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63873,0.15157,0.19349]}],"total_contact_groups":17},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56293,0.08343,0.01602],"final_tcp_position":[0.63733,0.15455,0.35355],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.90277,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53728,0.00099,0.03696],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":460.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.538,0.00101,0.03829],"tcp_start":[0.53728,0.00099,0.03696],"tcp_to_object_dist_end":0.01379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13006,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15816,"subtask_id":"grasp_1","tcp_end":[0.52968,0.00086,0.02862],"tcp_start":[0.538,0.00101,0.03829],"tcp_to_object_dist_end":0.01474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":392.0,"n_steps_budget":870.0,"object_pos_end":[0.54503,0.00073,0.13705],"object_pos_start":[0.54417,0.00074,0.02588],"object_to_goal_dist_end":0.19547,"object_to_goal_dist_start":0.25052,"object_z_max":0.1368,"peak_contact_force":0.12015,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11384.0,"raw_peak_contact_force":0.65751,"tcp_end":[0.52576,0.0008,0.14664],"tcp_start":[0.52968,0.00086,0.02862],"tcp_to_object_dist_end":0.02153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.56293,0.08343,0.01602],"object_pos_start":[0.54503,0.00073,0.13705],"object_to_goal_dist_end":0.20833,"object_to_goal_dist_start":0.19547,"object_z_max":0.14643,"peak_contact_force":9748.90277,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5550.0,"raw_peak_contact_force":1.72053,"subtask_id":"transport_arc","tcp_end":[0.63463,0.14464,0.18432],"tcp_start":[0.52576,0.0008,0.14664],"tcp_to_object_dist_end":0.1929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.56293,0.08343,0.01602],"object_pos_start":[0.56293,0.08343,0.01602],"object_to_goal_dist_end":0.20833,"object_to_goal_dist_start":0.20833,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6968.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64363,0.15657,0.20453],"tcp_start":[0.63463,0.14464,0.18432],"tcp_to_object_dist_end":0.21771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56293,0.08343,0.01602],"object_pos_start":[0.56293,0.08343,0.01602],"object_to_goal_dist_end":0.20833,"object_to_goal_dist_start":0.20833,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63855,0.15507,0.22335],"tcp_start":[0.64363,0.15657,0.20453],"tcp_to_object_dist_end":0.23203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":960.0,"object_pos_end":[0.56293,0.08343,0.01602],"object_pos_start":[0.56293,0.08343,0.01602],"object_to_goal_dist_end":0.20833,"object_to_goal_dist_start":0.20833,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63733,0.15455,0.35355],"tcp_start":[0.63855,0.15507,0.22335],"tcp_to_object_dist_end":0.35287,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54974,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.016,"lift_1.lift_height":0.12172,"transport_arc.arc_height":0.31443},"optimized_scores":{"best_composite_score":0.41719,"best_fitness_score":0.74719,"best_task_score":0.54109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":21.0,"contact_point_centroid":[0.60208,0.16865,-0.00363],"force_p95":1.18646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18934,"mean_force":0.87636,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58853,0.16213,0.11179]},{"body_a":"world","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.59937,0.181,-0.00223],"force_p95":0.12417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73163,"mean_force":0.12836,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5924,0.17138,0.1113]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52744,0.0284,-0.00143],"force_p95":0.6095,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6476,"mean_force":0.13802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5148,0.02929,0.03056]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4846.0,"contact_point_centroid":[0.5152,0.01022,0.07676],"force_p95":0.1102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32825,"mean_force":0.07274,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5123,0.02912,0.07443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5194.0,"contact_point_centroid":[0.51518,0.04797,0.07431],"force_p95":0.10804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32722,"mean_force":0.06935,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51234,0.02912,0.07244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3282.0,"contact_point_centroid":[0.54394,0.05924,0.13541],"force_p95":0.18749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30248,"mean_force":0.11014,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53858,0.07772,0.13508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.54738,0.10161,0.1342],"force_p95":0.15634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29293,"mean_force":0.09573,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54191,0.08351,0.13468]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0305,-0.00213],"force_p95":0.16074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23973,"mean_force":0.13272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51739,0.02947,0.03052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.51714,0.01018,0.03188],"force_p95":0.08071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14615,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51615,0.02939,0.02914]},{"body_a":"world","body_b":"grasp_target","contact_count":3352.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51103,0.01445,0.16713]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52348,0.02942,0.03702]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59937,0.18097,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59164,0.17495,0.11626]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.59937,0.18097,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5867,0.17332,0.20062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4997.0,"contact_point_centroid":[0.51706,0.04854,0.03093],"force_p95":0.07331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08691,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51616,0.02939,0.02914]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2793.0,"contact_point_centroid":[0.59335,0.17208,0.11381],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01567,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59283,0.17205,0.1116]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.59558,0.17602,0.11468],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59485,0.17599,0.11243]}],"total_contact_groups":16},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59937,0.18097,0.01602],"final_tcp_position":[0.58715,0.17341,0.26638],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.18934,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52425,0.02897,0.03757],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":81.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":324.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52424,0.02992,0.03829],"tcp_start":[0.52425,0.02897,0.03757],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02943,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18471,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15272,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.23973,"subtask_id":"grasp_1","tcp_end":[0.51612,0.02938,0.0291],"tcp_start":[0.52424,0.02992,0.03829],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":336.0,"n_steps_budget":780.0,"object_pos_end":[0.53098,0.02932,0.12262],"object_pos_start":[0.5304,0.02943,0.02557],"object_to_goal_dist_end":0.16573,"object_to_goal_dist_start":0.18471,"object_z_max":0.12237,"peak_contact_force":0.11086,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10120.0,"raw_peak_contact_force":0.6476,"tcp_end":[0.51216,0.02912,0.13148],"tcp_start":[0.51612,0.02938,0.0291],"tcp_to_object_dist_end":0.0208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.59913,0.17603,0.00902],"object_pos_start":[0.53098,0.02932,0.12262],"object_to_goal_dist_end":0.09913,"object_to_goal_dist_start":0.16573,"object_z_max":0.12489,"peak_contact_force":0.76207,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7379.0,"raw_peak_contact_force":1.18934,"subtask_id":"transport_arc","tcp_end":[0.58918,0.16331,0.11089],"tcp_start":[0.51216,0.02912,0.13148],"tcp_to_object_dist_end":0.10313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.59937,0.18097,0.01602],"object_pos_start":[0.59913,0.17603,0.00902],"object_to_goal_dist_end":0.09213,"object_to_goal_dist_start":0.09913,"object_z_max":0.01645,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5705.0,"raw_peak_contact_force":0.73163,"tcp_end":[0.59642,0.17645,0.11523],"tcp_start":[0.58918,0.16331,0.11089],"tcp_to_object_dist_end":0.09936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59937,0.18097,0.01602],"object_pos_start":[0.59937,0.18097,0.01602],"object_to_goal_dist_end":0.09213,"object_to_goal_dist_start":0.09213,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58973,0.17433,0.13596],"tcp_start":[0.59642,0.17645,0.11523],"tcp_to_object_dist_end":0.12051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":960.0,"object_pos_end":[0.59937,0.18097,0.01602],"object_pos_start":[0.59937,0.18097,0.01602],"object_to_goal_dist_end":0.09213,"object_to_goal_dist_start":0.09213,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58715,0.17341,0.26638],"tcp_start":[0.58973,0.17433,0.13596],"tcp_to_object_dist_end":0.25077,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```