## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2818 | 0.24 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 1 | 0.2091 | 0.33 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 1 | 0.4497 | 0.39 | ✅ accepted |

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

## Current Skill (Q=0.282) — your mutation base

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

- **Composite score**: 0.282
- **task_score** (E): 0.237
- **fitness_score**: 0.582  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1681 |
| descend_1 | 1.00 | 1.00 | 0.0834 |
| grasp_1 | 1.00 | 1.00 | 0.0121 |
| lift_1 | 0.67 | 0.67 | 0.1490 |
| transport_arc | 0.00 | 1.00 | 0.1396 |
| place_approach | 0.00 | 1.00 | 0.0907 |
| release_1 | 1.00 | 1.00 | 0.0268 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.138) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.002, 0.138)→(0.506, 0.002, 0.054) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.054)→(0.498, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.333 | 0.140 | 0.184 |
| lift_1 | lift | 0.67 / step_budget | (0.498, 0.002, 0.045)→(0.505, 0.002, 0.194) | (0.511, 0.002, 0.026)→(0.516, 0.002, 0.160) | 0.246→0.215 | 0.67 / 8.667 | 35.464 | 0.412 |
| transport_arc | approach | 0.00 / step_budget | (0.505, 0.002, 0.194)→(0.507, 0.009, 0.227) | (0.516, 0.002, 0.160)→(0.518, 0.029, 0.019) | 0.215→0.230 | 1.00 / 9.667 | 91539.529 | 1318.738 |
| place_approach | descend | 0.00 / step_budget | (0.507, 0.009, 0.227)→(0.557, 0.050, 0.268) | (0.518, 0.029, 0.019)→(0.519, 0.028, 0.019) | 0.230→0.230 | 1.00 / 9.667 | 368.252 | 656.809 |
| release_1 | release | 1.00 / step_budget | (0.557, 0.050, 0.268)→(0.556, 0.049, 0.295) | (0.519, 0.028, 0.019)→(0.519, 0.028, 0.019) | 0.230→0.230 | 1.00 / 4.000 | 0.124 | 104.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.358
- phase_score: 0.245
- phase_breakdown.release_1_score: 0.004
- phase_breakdown.descend_1_score: 0.869
- phase_breakdown.transport_arc_score: 0.003
- phase_breakdown.approach_1_score: 0.116
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.643

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.643
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.358
- **Median Q (composite search score)**: 0.281
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.250


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.1037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.20821,"place_approach.place_z_offset":0.03262,"transport_arc.arc_height":0.22873},"optimized_scores":{"best_composite_score":0.22177,"best_fitness_score":0.52177,"best_task_score":0.11987},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.51996,-0.02321,-0.00204],"force_p95":865.94399,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1193.51934,"mean_force":258.96343,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.38842,-0.02723,0.02598]},{"body_a":"world","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.62263,0.03314,-0.00022],"force_p95":378.88485,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":810.08092,"mean_force":243.67384,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.42281,0.00575,0.18338]},{"body_a":"world","body_b":"hand","contact_count":17.0,"contact_point_centroid":[0.44468,-0.11579,-0.00209],"force_p95":158.87826,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":794.39131,"mean_force":46.7289,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.3932,-0.02708,0.00404]},{"body_a":"world","body_b":"link6","contact_count":857.0,"contact_point_centroid":[0.61676,-0.00475,-0.00027],"force_p95":239.76789,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":545.33839,"mean_force":218.3214,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.37667,-0.02134,0.06601]},{"body_a":"world","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.62364,0.05898,-0.00015],"force_p95":90.60721,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.71229,"mean_force":75.56254,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45054,0.02668,0.21772]},{"body_a":"world","body_b":"left_finger","contact_count":187.0,"contact_point_centroid":[0.39802,-0.03076,-0.00232],"force_p95":28.82003,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.74999,"mean_force":3.27027,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.39481,-0.02712,0.00347]},{"body_a":"world","body_b":"right_finger","contact_count":179.0,"contact_point_centroid":[0.39754,-0.02272,-0.00228],"force_p95":29.54548,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.707,"mean_force":2.98522,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.3947,-0.02712,0.00325]},{"body_a":"grasp_target","body_b":"hand","contact_count":904.0,"contact_point_centroid":[0.48059,-0.043,0.02927],"force_p95":1.02124,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.06535,"mean_force":0.44147,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.37778,-0.02187,0.06284]},{"body_a":"world","body_b":"grasp_target","contact_count":3525.0,"contact_point_centroid":[0.45061,-0.03737,-0.00361],"force_p95":0.63471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.97991,"mean_force":0.2426,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.37821,-0.0215,0.06386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.47001,-0.03253,0.05988],"force_p95":1.56812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.60394,"mean_force":0.99632,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46912,-0.02974,0.07003]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.45658,-0.0249,-0.00111],"force_p95":0.30045,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39282,"mean_force":0.04408,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4459,-0.0255,0.04968]},{"body_a":"grasp_target","body_b":"link7","contact_count":784.0,"contact_point_centroid":[0.48411,-0.04445,0.0325],"force_p95":0.22381,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34502,"mean_force":0.15544,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.37642,-0.02133,0.06599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13818.0,"contact_point_centroid":[0.45078,-0.00658,0.11571],"force_p95":0.11476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32697,"mean_force":0.07073,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44776,-0.02549,0.11532]},{"body_a":"grasp_target","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.48177,-0.03533,0.03781],"force_p95":0.31249,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31653,"mean_force":0.27612,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.37704,-0.00482,0.09347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15463.0,"contact_point_centroid":[0.45073,-0.04427,0.11682],"force_p95":0.10046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2559,"mean_force":0.06428,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44784,-0.02549,0.11652]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44801,-0.03358,-0.00199],"force_p95":0.1228,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22434,"mean_force":0.12248,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.42291,0.00581,0.18358]}],"total_contact_groups":25},"final_pose_error":0.26514,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.448,-0.03358,0.01602],"final_tcp_position":[0.45062,0.0266,0.21807],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1366.84211,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45846,-0.02397,0.13952],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45447,-0.02582,0.0551],"tcp_start":[0.45846,-0.02397,0.13952],"tcp_to_object_dist_end":0.02937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0258,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30336,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14093,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12037.0,"raw_peak_contact_force":0.18994,"subtask_id":"grasp_1","tcp_end":[0.44704,-0.02555,0.0478],"tcp_start":[0.45447,-0.02582,0.0551],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46396,-0.02972,0.16948],"object_pos_start":[0.4585,-0.0258,0.02575],"object_to_goal_dist_end":0.29545,"object_to_goal_dist_start":0.30336,"object_z_max":0.17374,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29409.0,"raw_peak_contact_force":0.39282,"tcp_end":[0.45385,-0.02562,0.2091],"tcp_start":[0.44704,-0.02555,0.0478],"tcp_to_object_dist_end":0.0411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44724,-0.03143,0.01568],"object_pos_start":[0.46396,-0.02972,0.16948],"object_to_goal_dist_end":0.31713,"object_to_goal_dist_start":0.29545,"object_z_max":0.16948,"peak_contact_force":1366.84211,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10165.0,"raw_peak_contact_force":1193.51934,"subtask_id":"transport_arc","tcp_end":[0.37698,-0.00481,0.09329],"tcp_start":[0.45385,-0.02562,0.2091],"tcp_to_object_dist_end":0.10802,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.448,-0.03358,0.01602],"object_pos_start":[0.44724,-0.03143,0.01568],"object_to_goal_dist_end":0.31821,"object_to_goal_dist_start":0.31713,"object_z_max":0.01613,"peak_contact_force":370.13967,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9287.0,"raw_peak_contact_force":810.08092,"subtask_id":"release_1","tcp_end":[0.45062,0.0266,0.21807],"tcp_start":[0.37698,-0.00481,0.09329],"tcp_to_object_dist_end":0.21084,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.448,-0.03358,0.01602],"object_pos_start":[0.448,-0.03358,0.01602],"object_to_goal_dist_end":0.31821,"object_to_goal_dist_start":0.31821,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1087.0,"raw_peak_contact_force":131.71229,"tcp_end":[0.44913,0.02617,0.24432],"tcp_start":[0.45062,0.0266,0.21807],"tcp_to_object_dist_end":0.23599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13869,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.24999,"place_approach.place_z_offset":0.0338,"transport_arc.arc_height":0.48915},"optimized_scores":{"best_composite_score":0.2806,"best_fitness_score":0.5806,"best_task_score":0.2317},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":17.0,"contact_point_centroid":[0.57094,-0.07771,-0.00378],"force_p95":1102.16321,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1219.76081,"mean_force":170.73467,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47105,-0.11479,0.0526]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.58008,-0.02562,-0.00401],"force_p95":843.04205,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1013.67644,"mean_force":377.33336,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48002,-0.11696,0.06538]},{"body_a":"world","body_b":"link6","contact_count":889.0,"contact_point_centroid":[0.56253,0.10853,-0.00032],"force_p95":366.91256,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":866.61577,"mean_force":293.45138,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.64136,0.00205,0.23771]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.59346,0.10692,-0.00033],"force_p95":587.871,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":736.73885,"mean_force":471.49416,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.60415,0.10124,0.29371]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.62875,0.12794,-0.00016],"force_p95":82.55332,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.74368,"mean_force":59.88874,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63259,0.12111,0.29442]},{"body_a":"grasp_target","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.5619,0.00299,0.02116],"force_p95":3.29409,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.73478,"mean_force":1.1621,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5054,-0.10739,0.09323]},{"body_a":"world","body_b":"grasp_target","contact_count":3323.0,"contact_point_centroid":[0.59232,0.02224,-0.00248],"force_p95":0.29115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.54723,"mean_force":0.16097,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.63705,0.00571,0.23808]},{"body_a":"grasp_target","body_b":"link6","contact_count":42.0,"contact_point_centroid":[0.55607,0.02422,0.02677],"force_p95":1.47528,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.58686,"mean_force":0.81411,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51037,-0.1111,0.10126]},{"body_a":"grasp_target","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.53492,0.00521,0.08139],"force_p95":1.23066,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.23948,"mean_force":1.15122,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49117,-0.05862,0.06173]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54243,0.0008,-0.00111],"force_p95":0.30444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4257,"mean_force":0.06061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52863,0.00084,0.04546]},{"body_a":"grasp_target","body_b":"link5","contact_count":80.0,"contact_point_centroid":[0.57715,0.04188,0.05616],"force_p95":0.06606,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35474,"mean_force":0.0539,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.63076,0.1191,0.29405]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13483.0,"contact_point_centroid":[0.53475,-0.01796,0.11421],"force_p95":0.11781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32422,"mean_force":0.07248,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53045,0.00077,0.11273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13530.0,"contact_point_centroid":[0.53449,0.01956,0.11283],"force_p95":0.12029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28078,"mean_force":0.07233,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53038,0.00078,0.11124]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59627,0.02274,-0.00195],"force_p95":0.19211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21378,"mean_force":0.12194,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6326,0.12117,0.30062]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5959,0.02267,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19748,"mean_force":0.12307,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.60415,0.10124,0.29371]},{"body_a":"grasp_target","body_b":"link5","contact_count":133.0,"contact_point_centroid":[0.58064,0.04204,0.05703],"force_p95":0.15942,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18016,"mean_force":0.07589,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63256,0.12114,0.29595]}],"total_contact_groups":25},"final_pose_error":0.07989,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.59764,0.02257,0.02602],"final_tcp_position":[0.63268,0.12086,0.29399],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1219.76081,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53704,0.00099,0.13661],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53849,0.00103,0.05386],"tcp_start":[0.53704,0.00099,0.13661],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00078,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13032,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10794.0,"raw_peak_contact_force":0.14998,"subtask_id":"grasp_1","tcp_end":[0.53003,0.00088,0.04372],"tcp_start":[0.53849,0.00103,0.05386],"tcp_to_object_dist_end":0.0228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54613,0.00437,0.1687],"object_pos_start":[0.54421,0.00078,0.02587],"object_to_goal_dist_end":0.18556,"object_to_goal_dist_start":0.25048,"object_z_max":0.17235,"peak_contact_force":106.2864,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27159.0,"raw_peak_contact_force":0.4257,"tcp_end":[0.53662,0.00074,0.20481],"tcp_start":[0.53003,0.00088,0.04372],"tcp_to_object_dist_end":0.03752,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5959,0.02267,0.02602],"object_pos_start":[0.54613,0.00437,0.1687],"object_to_goal_dist_end":0.2197,"object_to_goal_dist_start":0.18556,"object_z_max":0.1687,"peak_contact_force":250.94177,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8207.0,"raw_peak_contact_force":1219.76081,"subtask_id":"transport_arc","tcp_end":[0.57376,0.08058,0.29359],"tcp_start":[0.53662,0.00074,0.20481],"tcp_to_object_dist_end":0.27466,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59809,0.02341,0.0257],"object_pos_start":[0.5959,0.02267,0.02602],"object_to_goal_dist_end":0.21897,"object_to_goal_dist_start":0.2197,"object_z_max":0.02607,"peak_contact_force":403.61124,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9306.0,"raw_peak_contact_force":736.73885,"subtask_id":"release_1","tcp_end":[0.63268,0.12086,0.29399],"tcp_start":[0.57376,0.08058,0.29359],"tcp_to_object_dist_end":0.28753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59764,0.02257,0.02602],"object_pos_start":[0.59809,0.02341,0.0257],"object_to_goal_dist_end":0.21935,"object_to_goal_dist_start":0.21897,"object_z_max":0.02628,"peak_contact_force":0.12544,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1239.0,"raw_peak_contact_force":93.74368,"tcp_end":[0.63275,0.12127,0.32052],"tcp_start":[0.63268,0.12086,0.29399],"tcp_to_object_dist_end":0.31258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.55556,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.15573,"place_approach.place_z_offset":0.03263,"transport_arc.arc_height":0.28154},"optimized_scores":{"best_composite_score":0.34299,"best_fitness_score":0.64299,"best_task_score":0.35845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":25.0,"contact_point_centroid":[0.60082,0.11053,-0.00471],"force_p95":1298.92592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1542.93237,"mean_force":460.26294,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50438,0.13778,0.03655]},{"body_a":"world","body_b":"link6","contact_count":897.0,"contact_point_centroid":[0.57472,-0.09521,-0.00032],"force_p95":386.14037,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1328.93876,"mean_force":291.58495,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58522,-0.01945,0.26854]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.56824,-0.04298,-0.00027],"force_p95":396.66087,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.60671,"mean_force":322.75752,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.57889,-0.02714,0.29323]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.58758,-0.02166,-0.00016],"force_p95":86.76001,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.97651,"mean_force":61.98792,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58718,0.00141,0.29325]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.54539,0.06986,0.03265],"force_p95":4.00091,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.4273,"mean_force":1.28913,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50844,0.13246,0.04237]},{"body_a":"world","body_b":"grasp_target","contact_count":3553.0,"contact_point_centroid":[0.51458,0.09134,-0.00264],"force_p95":0.2941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22255,"mean_force":0.16183,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58053,-0.01892,0.26241]},{"body_a":"grasp_target","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.52859,0.03778,0.02714],"force_p95":1.42059,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.50808,"mean_force":1.00485,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50766,0.14229,0.04425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":454.0,"contact_point_centroid":[0.54262,0.01784,0.1532],"force_p95":0.366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50415,"mean_force":0.16827,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53955,0.03772,0.15424]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.529,0.02923,-0.0012],"force_p95":0.27812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41681,"mean_force":0.05484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51547,0.02944,0.04653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":379.0,"contact_point_centroid":[0.54512,0.0525,0.1632],"force_p95":0.30976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38586,"mean_force":0.14952,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53735,0.03505,0.1629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12973.0,"contact_point_centroid":[0.52197,0.04828,0.10094],"force_p95":0.0949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28404,"mean_force":0.06207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51859,0.02945,0.09869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11338.0,"contact_point_centroid":[0.52177,0.01049,0.09906],"force_p95":0.10829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26167,"mean_force":0.06919,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51848,0.02944,0.09753]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.0307,-0.00211],"force_p95":0.15278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21356,"mean_force":0.13085,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51795,0.02962,0.04607]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51092,0.01384,0.21815]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52343,0.02905,0.09554]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51136,0.09446,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.57882,-0.02736,0.29323]}],"total_contact_groups":22},"final_pose_error":0.23387,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.51136,0.09446,0.01602],"final_tcp_position":[0.58719,0.00163,0.29296],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273000.80373,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52426,0.02818,0.13729],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52502,0.03009,0.05435],"tcp_start":[0.52426,0.02818,0.13729],"tcp_to_object_dist_end":0.02886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02995,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18425,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14981,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12053.0,"raw_peak_contact_force":0.21356,"subtask_id":"grasp_1","tcp_end":[0.51674,0.02954,0.04466],"tcp_start":[0.52502,0.03009,0.05435],"tcp_to_object_dist_end":0.02349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.53775,0.03043,0.14155],"object_pos_start":[0.53046,0.02995,0.0256],"object_to_goal_dist_end":0.16473,"object_to_goal_dist_start":0.18425,"object_z_max":0.14143,"peak_contact_force":0.10583,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24462.0,"raw_peak_contact_force":0.41681,"tcp_end":[0.52595,0.02968,0.16869],"tcp_start":[0.51674,0.02954,0.04466],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51136,0.09446,0.01602],"object_pos_start":[0.53775,0.03043,0.14155],"object_to_goal_dist_end":0.15389,"object_to_goal_dist_start":0.16473,"object_z_max":0.14164,"peak_contact_force":273000.80373,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8921.0,"raw_peak_contact_force":1542.93237,"subtask_id":"transport_arc","tcp_end":[0.57065,-0.0481,0.29272],"tcp_start":[0.52595,0.02968,0.16869],"tcp_to_object_dist_end":0.31686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51136,0.09446,0.01602],"object_pos_start":[0.51136,0.09446,0.01602],"object_to_goal_dist_end":0.15389,"object_to_goal_dist_start":0.15389,"object_z_max":0.01602,"peak_contact_force":331.00389,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9415.0,"raw_peak_contact_force":423.60671,"subtask_id":"release_1","tcp_end":[0.58719,0.00163,0.29296],"tcp_start":[0.57065,-0.0481,0.29272],"tcp_to_object_dist_end":0.30177,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51136,0.09446,0.01602],"object_pos_start":[0.51136,0.09446,0.01602],"object_to_goal_dist_end":0.15389,"object_to_goal_dist_start":0.15389,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1109.0,"raw_peak_contact_force":86.97651,"tcp_end":[0.58731,0.00094,0.32052],"tcp_start":[0.58719,0.00163,0.29296],"tcp_to_object_dist_end":0.32746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```