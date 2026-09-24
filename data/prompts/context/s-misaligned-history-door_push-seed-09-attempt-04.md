## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 7  | 0.2314 | 0.61 | ✅ accepted |
| 3 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 7  | 0.2704 | 0.49 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 0.1972 | 0.32 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | admittance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | 4  | 0.1972 | 0.32 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | admittance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | 4  | 0.2819 | 0.66 | ✅ accepted |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- Frozen realised-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`
- Frozen initial hinge angle: 0.129 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: 0.1292
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

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

## Current Skill (Q=0.282) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_push_point
  anchor: fixture
  offset:
  - 0.2
  - -0.01
  - 0.35
  weight: 0.3
- id: push_door
  target_entity: hinge
  metric: hinge_angle
phases:
- id: approach_panel
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - 0.2
    - -0.01
    - 0.45
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_push_point
- id: descend_to_panel
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - 0.2
    - -0.01
    - 0.35
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_during_descend
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_push_point
- id: push_open
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - 0.2
    - -0.01
    - 0.35
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_panel** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[0.2, -0.01, 0.45], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_panel** (`descend`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[0.2, -0.01, 0.35], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_during_descend, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_open** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[0.2, -0.01, 0.35], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.282
- **task_score** (E): 0.662
- **fitness_score**: 0.662  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_panel | 0.00 | 1.00 | 0.3413 |
| descend_to_panel | 0.00 | 1.00 | 0.0939 |
| push_open | 1.00 | 1.00 | 0.0927 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_panel | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.312, 0.299, 0.592) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 646.387 | 797.097 |
| descend_to_panel | descend | 0.00 / step_budget | (0.312, 0.299, 0.592)→(0.396, 0.284, 0.560) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 203.277 | 362.425 |
| push_open | push | 1.00 / time_limit | (0.396, 0.284, 0.560)→(0.459, 0.328, 0.529) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 2099.285 | 164.993 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.925
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.925
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.925
- **Median Q (composite search score)**: 0.511
- **K-run variance**: 0.1213
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.306


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d324a70682be50916187e25da5a0a59a7678607fbe49b53fdc39aa246f41ddf9`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d82b7d31aa43f8d3a4479d5f34069ef44e70dc4ca62021414a1e013fa43805ad`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07576,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_panel.approach_arc_height":0.14637,"approach_panel.approach_speed":0.13831,"approach_panel.approach_tolerance":0.03202,"descend_to_panel.descend_speed":0.0271,"descend_to_panel.descend_tolerance":0.0121,"push_open.push_distance":0.22845,"push_open.push_speed":0.04704},"optimized_scores":{"best_composite_score":0.5454,"best_fitness_score":0.9254,"best_task_score":0.9254},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link5","contact_count":182.0,"contact_point_centroid":[0.10063,0.17505,0.75009],"force_p95":741.51641,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":761.74697,"mean_force":711.605,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.31848,0.30544,0.55939]},{"body_a":"door_panel","body_b":"link5","contact_count":354.0,"contact_point_centroid":[0.10703,0.12845,0.69948],"force_p95":603.14194,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":640.08028,"mean_force":382.44772,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.27216,0.33504,0.5307]},{"body_a":"door_frame","body_b":"link5","contact_count":6.0,"contact_point_centroid":[0.10541,0.17503,0.75004],"force_p95":307.04324,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.87901,"mean_force":158.95259,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.34623,0.27696,0.57435]},{"body_a":"door_frame","body_b":"link7","contact_count":481.0,"contact_point_centroid":[0.47506,0.22495,0.60462],"force_p95":300.56074,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.1863,"mean_force":237.0273,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.41589,0.26452,0.55336]},{"body_a":"door_panel","body_b":"link4","contact_count":640.0,"contact_point_centroid":[0.12794,0.05358,0.69955],"force_p95":268.52442,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":289.48155,"mean_force":195.88469,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.40305,0.26217,0.55395]},{"body_a":"door_frame","body_b":"link7","contact_count":67.0,"contact_point_centroid":[0.47501,0.22499,0.59673],"force_p95":92.60555,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.09409,"mean_force":57.41952,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.43465,0.2818,0.54129]},{"body_a":"door_panel","body_b":"link4","contact_count":345.0,"contact_point_centroid":[0.15843,-0.00456,0.65313],"force_p95":70.89023,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.22159,"mean_force":36.40602,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.47207,0.29942,0.51195]},{"body_a":"door_panel","body_b":"link5","contact_count":56.0,"contact_point_centroid":[0.11861,0.07959,0.7],"force_p95":41.30464,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.9135,"mean_force":31.05548,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.36235,0.27333,0.5615]},{"body_a":"world","body_b":"door_panel","contact_count":1012.0,"contact_point_centroid":[0.30461,0.1574,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.21875,0.35401,0.47661]},{"body_a":"world","body_b":"door_panel","contact_count":956.0,"contact_point_centroid":[0.31743,0.11814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.39977,0.26571,0.55498]},{"body_a":"world","body_b":"door_panel","contact_count":904.0,"contact_point_centroid":[0.33393,0.08867,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.47244,0.29958,0.51169]}],"total_contact_groups":11},"final_pose_error":0.2451,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.5154,0.32152,0.47885],"hinge_angle":0.61415,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":761.74697,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":721.48133,"phase_name":"approach_panel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1548.0,"raw_peak_contact_force":761.74697,"subtask_id":"reach_push_point","tcp_end":[0.34571,0.27746,0.57417],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.72538,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":261.00988,"phase_name":"descend_to_panel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2139.0,"raw_peak_contact_force":325.87901,"subtask_id":"reach_push_point","tcp_end":[0.43057,0.27778,0.54683],"tcp_start":[0.34571,0.27746,0.57417],"tcp_to_object_dist_end":0.74938,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.93106,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1316.0,"raw_peak_contact_force":126.09409,"subtask_id":"push_door","tcp_end":[0.5154,0.32152,0.47885],"tcp_start":[0.43057,0.27778,0.54683],"tcp_to_object_dist_end":0.77351,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1fec9e8e5c1fdb9e52be404e6e4e2b90974542a257bfa7ba08d11c8aa9beb00c`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91791,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_panel.approach_arc_height":0.16646,"approach_panel.approach_speed":0.09192,"approach_panel.approach_tolerance":0.03495,"descend_to_panel.descend_speed":0.02778,"descend_to_panel.descend_tolerance":0.01564,"push_open.push_distance":0.3229,"push_open.push_speed":0.07356},"optimized_scores":{"best_composite_score":0.51065,"best_fitness_score":0.89065,"best_task_score":0.89065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link5","contact_count":214.0,"contact_point_centroid":[0.10001,0.17505,0.75011],"force_p95":730.0282,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":787.60951,"mean_force":688.46977,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.30234,0.31866,0.5465]},{"body_a":"door_panel","body_b":"link5","contact_count":278.0,"contact_point_centroid":[0.10916,0.11631,0.69903],"force_p95":415.76277,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":512.69944,"mean_force":203.43196,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.2798,0.33311,0.53768]},{"body_a":"door_panel","body_b":"link4","contact_count":612.0,"contact_point_centroid":[0.12888,0.05288,0.69381],"force_p95":268.00653,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":405.61368,"mean_force":213.93353,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.38841,0.27477,0.53182]},{"body_a":"door_frame","body_b":"link5","contact_count":6.0,"contact_point_centroid":[0.1,0.17503,0.75005],"force_p95":270.93324,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":273.18213,"mean_force":157.46023,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.32704,0.29317,0.55536]},{"body_a":"door_frame","body_b":"link7","contact_count":286.0,"contact_point_centroid":[0.48873,0.22497,0.54016],"force_p95":211.5479,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.84325,"mean_force":113.72085,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.42714,0.27185,0.49801]},{"body_a":"door_panel","body_b":"link4","contact_count":229.0,"contact_point_centroid":[0.17595,-0.01443,0.63401],"force_p95":44.32239,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.90193,"mean_force":24.0025,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.47957,0.30543,0.46101]},{"body_a":"door_frame","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50472,0.22497,0.52721],"force_p95":82.15784,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.40968,"mean_force":38.45519,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.4431,0.27163,0.48542]},{"body_a":"door_panel","body_b":"link5","contact_count":47.0,"contact_point_centroid":[0.11678,0.08549,0.69955],"force_p95":45.61968,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.31118,"mean_force":35.73937,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.34133,0.28944,0.54501]},{"body_a":"world","body_b":"door_panel","contact_count":1036.0,"contact_point_centroid":[0.30514,0.15441,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.20725,0.35973,0.47255]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.31904,0.11555,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.39017,0.27587,0.52707]},{"body_a":"world","body_b":"door_panel","contact_count":788.0,"contact_point_centroid":[0.33906,0.08104,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.48143,0.30716,0.46003]}],"total_contact_groups":11},"final_pose_error":0.25317,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.52639,0.34924,0.43468],"hinge_angle":0.62588,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":787.60951,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":504.89399,"phase_name":"approach_panel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1528.0,"raw_peak_contact_force":787.60951,"subtask_id":"reach_push_point","tcp_end":[0.32653,0.29361,0.55526],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.70792,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":120.18335,"phase_name":"descend_to_panel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1875.0,"raw_peak_contact_force":405.61368,"subtask_id":"reach_push_point","tcp_end":[0.44307,0.27159,0.48547],"tcp_start":[0.32653,0.29361,0.55526],"tcp_to_object_dist_end":0.71116,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.51887,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1020.0,"raw_peak_contact_force":92.90193,"subtask_id":"push_door","tcp_end":[0.52639,0.34924,0.43468],"tcp_start":[0.44307,0.27159,0.48547],"tcp_to_object_dist_end":0.76681,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3715cb43c8f8f3084ca346701c1c33fec8eb1e50d1b8785cdad3bdd48e46f29f`; realized-scene SHA-256: `a85e6d1e7f42d6b7853e30231dc3bdf8d0b19eb5c068167ff162abd11c92b77d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.12965,"panel":{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23853,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_panel.approach_arc_height":0.27476,"approach_panel.approach_speed":0.19999,"approach_panel.approach_tolerance":0.02748,"descend_to_panel.descend_speed":0.01559,"descend_to_panel.descend_tolerance":0.00717,"push_open.push_distance":0.15139,"push_open.push_speed":0.06784},"optimized_scores":{"best_composite_score":-0.2103,"best_fitness_score":0.1697,"best_task_score":0.1697},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link5","contact_count":279.0,"contact_point_centroid":[0.10011,0.17504,0.75001],"force_p95":786.14368,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":841.93569,"mean_force":715.81131,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.25897,0.33568,0.63796]},{"body_a":"door_frame","body_b":"link5","contact_count":763.0,"contact_point_centroid":[0.10007,0.17502,0.75001],"force_p95":317.3792,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.78141,"mean_force":274.51016,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.28529,0.31589,0.63909]},{"body_a":"door_panel","body_b":"link5","contact_count":248.0,"contact_point_centroid":[0.1013,0.23118,0.69996],"force_p95":295.45446,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":309.11842,"mean_force":238.64808,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.30885,0.30154,0.64356]},{"body_a":"door_frame","body_b":"link5","contact_count":587.0,"contact_point_centroid":[0.10001,0.175,0.75],"force_p95":194.68645,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.98446,"mean_force":114.10757,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.32118,0.30763,0.65331]},{"body_a":"door_panel","body_b":"link5","contact_count":1497.0,"contact_point_centroid":[0.10032,0.21403,0.6997],"force_p95":195.99768,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":253.35874,"mean_force":149.5727,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.32571,0.3092,0.65838]},{"body_a":"door_frame","body_b":"link6","contact_count":305.0,"contact_point_centroid":[0.22519,0.22499,0.7567],"force_p95":102.08666,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.8151,"mean_force":44.10297,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.33032,0.31115,0.6648]},{"body_a":"door_frame","body_b":"link6","contact_count":146.0,"contact_point_centroid":[0.22818,0.22496,0.75],"force_p95":92.95902,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.88133,"mean_force":77.3944,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.31097,0.30012,0.64545]},{"body_a":"world","body_b":"door_panel","contact_count":940.0,"contact_point_centroid":[0.29999,0.20981,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_panel","phase_type":"approach","tcp_position_centroid":[0.18276,0.36846,0.53872]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.29992,0.20808,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_panel","phase_type":"descend","tcp_position_centroid":[0.28976,0.3131,0.64053]},{"body_a":"world","body_b":"door_panel","contact_count":1012.0,"contact_point_centroid":[0.29976,0.20068,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.32421,0.30861,0.65662]}],"total_contact_groups":10},"final_pose_error":0.48944,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.33398,0.31347,0.67373],"hinge_angle":-0.04073,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":6269.40606,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":712.78537,"phase_name":"approach_panel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1219.0,"raw_peak_contact_force":841.93569,"subtask_id":"reach_push_point","tcp_end":[0.26441,0.32631,0.64616],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.77066,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":228.63749,"phase_name":"descend_to_panel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2081.0,"raw_peak_contact_force":355.78141,"subtask_id":"reach_push_point","tcp_end":[0.3132,0.30129,0.64669],"tcp_start":[0.26441,0.32631,0.64616],"tcp_to_object_dist_end":0.77915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6269.40606,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3401.0,"raw_peak_contact_force":275.98446,"subtask_id":"push_door","tcp_end":[0.33398,0.31347,0.67373],"tcp_start":[0.3132,0.30129,0.64669],"tcp_to_object_dist_end":0.81469,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```