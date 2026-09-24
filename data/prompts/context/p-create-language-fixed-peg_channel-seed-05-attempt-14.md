## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1596 | 0.18 | ❌ rejected |
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0147 | 0.00 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.4987 | 0.44 | ✅ accepted |
| 11 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 6 | -0.2773 | 0.00 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.1494 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.160) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_height
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
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
  subtask_id: approach
- id: contact_phase
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: none
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_phase
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - -0.01
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_height** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_phase** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_phase** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, -0.01, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.160
- **task_score** (E): 0.180
- **fitness_score**: 0.256  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2502 |
| contact_phase | 1.00 | 1.00 | 0.0232 |
| push_phase | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.140, 0.058) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.561 | 2.488 |
| contact_phase | contact | 1.00 / force_exceeded | (0.508, 0.140, 0.058)→(0.502, 0.122, 0.044) | (0.504, 0.095, 0.034)→(0.503, 0.093, 0.034) | 0.175→0.173 | 1.00 / 2.000 | 8.828 | 8.828 |
| push_phase | push | 0.00 / guard_failure | (0.505, 0.096, 0.040)→(0.505, 0.096, 0.040) | (0.503, 0.093, 0.034)→(0.503, 0.065, 0.035) | 0.173→0.145 | 1.00 / 2.000 | 71.932 | 76.843 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.266
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.266
- phase_score: 0.330
- phase_breakdown.push_score: 0.064
- phase_breakdown.approach_score: 0.675
- phase_breakdown.contact_score: 0.782

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.304
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.266
- **Median Q (composite search score)**: 0.189
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28846,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_tolerance":0.02945,"approach_peg.speed":0.06555,"contact_phase.contact_force":9.92548,"contact_phase.speed":0.03063,"push_phase.force_guard_threshold":22.73672,"push_phase.push_speed":0.04414,"push_phase.push_tolerance":0.0329,"push_phase.retry_x_offset":-7e-05},"optimized_scores":{"best_composite_score":0.08241,"best_fitness_score":0.17908,"best_task_score":0.01329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,0.11997,0.05999],"force_p95":49.53644,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.54749,"mean_force":49.24784,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50912,0.12891,0.04246]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.11999,0.06],"force_p95":14.79907,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.79907,"mean_force":14.79907,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.50916,0.12897,0.04252]},{"body_a":"peg","body_b":"channel_base_body","contact_count":226.0,"contact_point_centroid":[0.50507,0.09924,0.00957],"force_p95":3.50511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.81253,"mean_force":1.00106,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.51209,0.13696,0.04759]},{"body_a":"attachment","body_b":"peg","contact_count":62.0,"contact_point_centroid":[0.50771,0.11942,0.04467],"force_p95":3.83812,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.39701,"mean_force":1.88076,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.50987,0.13117,0.04379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.50551,0.10461,0.00937],"force_p95":0.5786,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57082,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.509,0.17321,0.17381]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50001,0.19877,0.29506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49721,0.08256,0.00982],"force_p95":0.54518,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54787,"mean_force":0.5227,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50912,0.12891,0.04246]}],"total_contact_groups":7},"final_pose_error":0.15509,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50243,0.09967,0.03464],"final_tcp_position":[0.50905,0.12891,0.04239],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":49.54749,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54227,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":494.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51875,0.1487,0.05824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.50247,0.0997,0.0347],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.17979,"object_to_goal_dist_start":0.18492,"object_z_max":0.03518,"peak_contact_force":14.79907,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":289.0,"raw_peak_contact_force":14.79907,"subtask_id":"contact","tcp_end":[0.50914,0.12893,0.0425],"tcp_start":[0.51875,0.1487,0.05824],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50245,0.09967,0.03468],"object_pos_start":[0.50247,0.0997,0.0347],"object_to_goal_dist_end":0.17977,"object_to_goal_dist_start":0.17979,"object_z_max":0.0347,"peak_contact_force":49.43696,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":49.54749,"subtask_id":"push","tcp_end":[0.50905,0.12891,0.04239],"tcp_start":[0.50909,0.1289,0.04243],"tcp_to_object_dist_end":0.03095,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75776,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_tolerance":0.03198,"approach_peg.speed":0.05614,"contact_phase.contact_force":2.56486,"contact_phase.speed":0.0152,"push_phase.force_guard_threshold":37.56861,"push_phase.push_speed":0.04118,"push_phase.push_tolerance":0.02713,"push_phase.retry_x_offset":-0.00442},"optimized_scores":{"best_composite_score":0.20726,"best_fitness_score":0.30393,"best_task_score":0.26555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,0.05835,0.05998],"force_p95":60.66782,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.12999,"mean_force":45.33048,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50184,0.05821,0.03836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":60.0,"contact_point_centroid":[0.50604,0.03859,0.00974],"force_p95":23.3025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.25561,"mean_force":6.60901,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49808,0.08179,0.04118]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.50213,0.06897,0.04406],"force_p95":22.56348,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.05098,"mean_force":6.64327,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49815,0.08036,0.0408]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52523,0.05044,0.03733],"force_p95":13.49282,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.16345,"mean_force":2.4916,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49818,0.0789,0.04037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.50297,0.06711,0.00938],"force_p95":0.55068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.85885,"mean_force":0.56058,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.49639,0.10344,0.04778]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50262,0.08534,0.05679],"force_p95":2.38025,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.47822,"mean_force":1.20121,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.49656,0.0972,0.0443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":499.0,"contact_point_centroid":[0.5031,0.06748,0.00934],"force_p95":0.55959,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56389,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49901,0.15675,0.17636]}],"total_contact_groups":7},"final_pose_error":0.08613,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50205,0.02497,0.03488],"final_tcp_position":[0.50186,0.05771,0.03828],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":62.12999,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54805,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":499.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49935,0.1148,0.05786],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06733,0.03412],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14748,"object_to_goal_dist_start":0.14758,"object_z_max":0.03408,"peak_contact_force":2.85885,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":524.0,"raw_peak_contact_force":2.85885,"subtask_id":"contact","tcp_end":[0.49657,0.09704,0.04422],"tcp_start":[0.49935,0.1148,0.05786],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.50245,0.02563,0.03496],"object_pos_start":[0.50304,0.06733,0.03412],"object_to_goal_dist_end":0.10578,"object_to_goal_dist_start":0.14748,"object_z_max":0.03833,"peak_contact_force":47.50823,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":153.0,"raw_peak_contact_force":62.12999,"subtask_id":"push","tcp_end":[0.50186,0.05771,0.03828],"tcp_start":[0.50186,0.05792,0.03832],"tcp_to_object_dist_end":0.03225,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93082,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_tolerance":0.03098,"approach_peg.speed":0.04664,"contact_phase.contact_force":8.31544,"contact_phase.speed":0.04996,"push_phase.force_guard_threshold":28.34524,"push_phase.push_speed":0.03745,"push_phase.push_tolerance":0.04488,"push_phase.retry_x_offset":-0.00897},"optimized_scores":{"best_composite_score":0.18906,"best_fitness_score":0.28573,"best_task_score":0.26088},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,0.10244,0.05998],"force_p95":118.81014,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.85065,"mean_force":99.08538,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50308,0.10227,0.04009]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.50555,0.08247,0.00978],"force_p95":21.55622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.53303,"mean_force":9.9926,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50132,0.12602,0.043]},{"body_a":"attachment","body_b":"peg","contact_count":72.0,"contact_point_centroid":[0.50403,0.11319,0.04569],"force_p95":20.88504,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.52335,"mean_force":7.0472,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.5013,0.12484,0.04271]},{"body_a":"peg","body_b":"channel_base_body","contact_count":149.0,"contact_point_centroid":[0.5041,0.11019,0.00941],"force_p95":0.61695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.82641,"mean_force":0.71589,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.5023,0.14719,0.05055]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50345,0.12957,0.05109],"force_p95":7.74563,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.58764,"mean_force":3.40655,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.50124,0.14148,0.04644]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52513,0.09326,0.03444],"force_p95":6.73935,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.06722,"mean_force":1.25831,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50123,0.12212,0.04202]},{"body_a":"peg","body_b":"channel_base_body","contact_count":470.0,"contact_point_centroid":[0.50357,0.11172,0.00936],"force_p95":0.63866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56171,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50223,0.17684,0.17568]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49976,0.19947,0.2989]}],"total_contact_groups":8},"final_pose_error":0.1289,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50468,0.06935,0.0338],"final_tcp_position":[0.50309,0.10172,0.04003],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":118.85065,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.50381,0.11173,0.03378],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59338,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":486.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50569,0.15521,0.05882],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":149.0,"n_steps_budget":660.0,"object_pos_end":[0.50379,0.11123,0.03441],"object_pos_start":[0.50381,0.11173,0.03378],"object_to_goal_dist_end":0.19135,"object_to_goal_dist_start":0.19186,"object_z_max":0.03437,"peak_contact_force":8.82641,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":157.0,"raw_peak_contact_force":8.82641,"subtask_id":"contact","tcp_end":[0.50118,0.14075,0.04598],"tcp_start":[0.50569,0.15521,0.05882],"tcp_to_object_dist_end":0.03181,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.50492,0.07014,0.03406],"object_pos_start":[0.50379,0.11123,0.03441],"object_to_goal_dist_end":0.15033,"object_to_goal_dist_start":0.19135,"object_z_max":0.03737,"peak_contact_force":118.85065,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":157.0,"raw_peak_contact_force":118.85065,"subtask_id":"push","tcp_end":[0.50309,0.10172,0.04003],"tcp_start":[0.50309,0.10196,0.04006],"tcp_to_object_dist_end":0.0322,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```