## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → push → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2800 | 0.00 | ❌ rejected |
| 5 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2556 | 0.59 | ❌ rejected |
| 4 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3057 | 0.59 | ✅ accepted |
| 3 | approach → descend | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 3 | 0.4357 | 0.59 | ✅ accepted |
| 2 | approach → descend | arc_cartesian | linear_cartesian | impedance_control | position_control | pose_tolerance | pose_tolerance | 4 | -0.1344 | 0.07 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: obstacle_reach
- Frozen realised-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`
- Frozen task target: [0.6826972276605561, 0.048727684333792556, 0.15]
- Goal object position: (0.6826972276605561, 0.048727684333792556, 0.15)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.35, 0.0, 0.32)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.35, 0, 0.32]
objects:
  - name: obstacle_block
    role: obstacle
    dynamics: static
    geometry: box
    dimensions_m: [0.08, 0.3, 0.3]
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_task_target: [0.6827, 0.0487, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.6826972276605561, 0.048727684333792556, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683

## Current Skill (Q=-0.280) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.3
    - 0.2
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_1
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
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.3, 0.2], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.280
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 0.33 | 0.2478 |
| push_1 | 0.33 | 0.67 | 0.1415 |
| descend_1 | 0.00 | 1.00 | 0.0483 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.350, -0.000, 0.321)→(0.547, 0.140, 0.336) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.738→0.738 | 0.33 / 0.333 | 95.032 | 1720.387 | link6 ↔ obstacle_block/obstacle_block_geom |
| push_1 | push | 0.33 / step_budget | (0.547, 0.140, 0.336)→(0.660, 0.084, 0.377) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.738→0.738 | 0.67 / 0.667 | 175.152 | 594.008 | link7 ↔ obstacle_block/obstacle_block_geom |
| descend_1 | descend | 0.00 / step_budget | (0.660, 0.084, 0.377)→(0.666, 0.082, 0.351) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.738→0.738 | 1.00 / 1.333 | 265.332 | 595.224 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.971
- path_efficiency: 0.450
- arc_smoothness: 0.969
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 1755.085 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.249
- min_tcp_distance: 0.213
- tcp_proximity_score: 0.190
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link6
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.280
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.295


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `153111e21f17c0d331b561f1147684993204f9f696925b5b61ee34d65508a2ad`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `09a48f578e6b1d8164588605561432222dd1ada27be56833f7098561f0a0705c`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.6827,0.04873,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.6827,0.04873,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":46.0,"average_failure_rate":0.37398,"average_mean_iterations":79.21951,"average_solve_count":123.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.12528,"approach_1.speed":0.17242,"descend_1.speed":0.10174,"descend_1.tolerance":0.02686,"push_1.speed":0.13923},"optimized_scores":{"best_composite_score":-0.28,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":812.0,"contact_point_centroid":[0.51708,0.05733,0.29978],"force_p95":391.88811,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1755.08465,"mean_force":294.25373,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40543,0.03841,0.38419]},{"body_a":"obstacle_block","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.53869,0.14979,0.29995],"force_p95":386.91379,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":691.1404,"mean_force":201.50369,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51989,0.16196,0.35433]},{"body_a":"obstacle_block","body_b":"link5","contact_count":193.0,"contact_point_centroid":[0.48809,0.14996,0.28204],"force_p95":425.48411,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":645.70603,"mean_force":305.96478,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.62766,0.18738,0.35261]},{"body_a":"obstacle_block","body_b":"link5","contact_count":392.0,"contact_point_centroid":[0.49748,0.14978,0.29955],"force_p95":317.12401,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":496.93052,"mean_force":199.08225,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.60213,0.12959,0.36135]},{"body_a":"obstacle_block","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53251,0.14995,0.2998],"force_p95":282.30561,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":285.09598,"mean_force":248.94306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50168,0.1683,0.35933]}],"total_contact_groups":5},"final_pose_error":0.24887,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.62115,0.21344,0.32613],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1755.08465,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":285.09598,"phase_name":"approach_1","phase_peak_obstacle_force":1755.08465,"phase_type":"approach","raw_contact_event_count":815.0,"raw_peak_contact_force":1755.08465,"tcp_end":[0.50209,0.16945,0.35882],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.63997,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":677.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":215.85737,"phase_name":"push_1","phase_peak_obstacle_force":691.1404,"phase_type":"push","raw_contact_event_count":430.0,"raw_peak_contact_force":691.1404,"tcp_end":[0.62822,0.17806,0.37418],"tcp_start":[0.50209,0.16945,0.35882],"tcp_to_object_dist_end":0.75258,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":202.4298,"phase_name":"descend_1","phase_peak_obstacle_force":645.70603,"phase_type":"descend","raw_contact_event_count":193.0,"raw_peak_contact_force":645.70603,"tcp_end":[0.62115,0.21344,0.32613],"tcp_start":[0.62822,0.17806,0.37418],"tcp_to_object_dist_end":0.73331,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e48c638882a658e374f83b9ad4d96930956de0db1e88d759e02d159e310d1b19`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.73702,-0.02132,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.73702,-0.02132,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":66.0,"average_failure_rate":0.53659,"average_mean_iterations":111.09756,"average_solve_count":123.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.14109,"approach_1.speed":0.176,"descend_1.speed":0.09297,"descend_1.tolerance":0.02789,"push_1.speed":0.23151},"optimized_scores":{"best_composite_score":-0.28,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":722.0,"contact_point_centroid":[0.51565,0.03642,0.29978],"force_p95":388.47954,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1732.29547,"mean_force":282.35942,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40169,0.02401,0.37759]},{"body_a":"obstacle_block","body_b":"link5","contact_count":32.0,"contact_point_centroid":[0.5118,-0.00834,0.29941],"force_p95":725.46896,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1090.88256,"mean_force":365.9803,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.6249,0.09101,0.36897]},{"body_a":"obstacle_block","body_b":"link5","contact_count":89.0,"contact_point_centroid":[0.51207,-0.00453,0.29987],"force_p95":402.36184,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":712.74489,"mean_force":335.69035,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.6303,0.07046,0.39687]},{"body_a":"obstacle_block","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54,0.14926,0.29999],"force_p95":143.99261,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":154.95806,"mean_force":99.0872,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52966,0.149,0.3529]},{"body_a":"obstacle_block","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5399,0.14997,0.29996],"force_p95":146.69746,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":150.27207,"mean_force":114.52594,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54445,0.15564,0.34408]}],"total_contact_groups":5},"final_pose_error":0.28299,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.63153,0.0593,0.39991],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1732.29547,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":1732.29547,"phase_type":"approach","raw_contact_event_count":734.0,"raw_peak_contact_force":1732.29547,"tcp_end":[0.54189,0.15568,0.34608],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.66155,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":311.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":309.59935,"phase_name":"push_1","phase_peak_obstacle_force":1090.88256,"phase_type":"push","raw_contact_event_count":34.0,"raw_peak_contact_force":1090.88256,"tcp_end":[0.62808,0.08386,0.38192],"tcp_start":[0.54189,0.15568,0.34608],"tcp_to_object_dist_end":0.73986,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":346.43025,"phase_name":"descend_1","phase_peak_obstacle_force":712.74489,"phase_type":"descend","raw_contact_event_count":89.0,"raw_peak_contact_force":712.74489,"tcp_end":[0.63153,0.0593,0.39991],"tcp_start":[0.62808,0.08386,0.38192],"tcp_to_object_dist_end":0.74985,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7c770227bfbc61ad3e08c75d3630762494b918d2814b704b39c653a43064979c`; realized-scene SHA-256: `61ec300895503e484321052c14122005b6d825b54245a4a918a581ea2f04a59f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7456,-0.02923,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7456,-0.02923,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.17699,"average_mean_iterations":41.07965,"average_solve_count":113.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.17317,"approach_1.speed":0.2322,"descend_1.speed":0.08414,"descend_1.tolerance":0.03077,"push_1.speed":0.21564},"optimized_scores":{"best_composite_score":-0.28,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":473.0,"contact_point_centroid":[0.50179,0.01877,0.29973],"force_p95":370.58022,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1673.78107,"mean_force":285.68187,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38261,0.00994,0.36535]},{"body_a":"obstacle_block","body_b":"link7","contact_count":142.0,"contact_point_centroid":[0.53836,0.14958,0.29735],"force_p95":576.50684,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1034.52086,"mean_force":291.38021,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55026,0.13122,0.29509]},{"body_a":"obstacle_block","body_b":"link5","contact_count":722.0,"contact_point_centroid":[0.53996,0.10167,0.29991],"force_p95":247.42824,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":427.22225,"mean_force":149.50892,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.73812,-0.01678,0.30653]}],"total_contact_groups":3},"final_pose_error":0.17817,"key_states":{"actual_goal_position":[0.7456,-0.02923,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.74392,-0.02642,0.32814],"realised_goal_position":[0.7456,-0.02923,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1673.78107,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":1673.78107,"phase_type":"approach","raw_contact_event_count":615.0,"raw_peak_contact_force":1673.78107,"tcp_end":[0.59623,0.09589,0.30329],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.67577,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":401.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.7227,-0.00913,0.37479],"tcp_start":[0.59623,0.09589,0.30329],"tcp_to_object_dist_end":0.81415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":247.13531,"phase_name":"descend_1","phase_peak_obstacle_force":427.22225,"phase_type":"descend","raw_contact_event_count":722.0,"raw_peak_contact_force":427.22225,"tcp_end":[0.74392,-0.02642,0.32814],"tcp_start":[0.7227,-0.00913,0.37479],"tcp_to_object_dist_end":0.81351,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```