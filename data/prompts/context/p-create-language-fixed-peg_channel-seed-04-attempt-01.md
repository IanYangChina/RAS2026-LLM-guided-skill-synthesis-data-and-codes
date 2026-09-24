## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0426 | 0.00 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2607 | 0.15 | ✅ accepted |

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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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

## Current Skill (Q=-0.043) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
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
    - 0.04
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
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
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.043
- **task_score** (E): 0.000
- **fitness_score**: 0.267  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1933 |
| contact_peg | 0.00 | 1.00 | 0.0500 |
| push_channel | 1.00 | 1.00 | 0.1982 |
| retract_lift | 1.00 | 1.00 | 0.1323 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.141, 0.118) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.545 | 3.242 |
| contact_peg | contact | 0.00 / step_budget | (0.516, 0.141, 0.118)→(0.503, 0.118, 0.076) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.549 | 0.560 |
| push_channel | push | 1.00 / step_budget | (0.503, 0.118, 0.076)→(0.500, -0.080, 0.071) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.547 | 0.559 |
| retract_lift | retract | 1.00 / step_budget | (0.500, -0.080, 0.071)→(0.497, -0.008, 0.182) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.547 | 0.559 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.959
- terminal_score: 0.000
- phase_score: 0.465
- phase_breakdown.contact_score: 0.477
- phase_breakdown.push_score: 0.548
- phase_breakdown.approach_score: 0.203

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.279
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.047
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.316


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88015,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04588,"contact_peg.contact_force":22.66642,"contact_peg.contact_speed":0.01679,"push_channel.push_distance":0.21286,"push_channel.push_speed":0.06068},"optimized_scores":{"best_composite_score":-0.04969,"best_fitness_score":0.26031,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.50558,0.08084,0.00935],"force_p95":0.56435,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.588,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51421,0.16735,0.20318]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50036,0.19815,0.29481]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51695,0.12671,0.09598]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.50598,0.08094,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50336,0.01766,0.07218]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.50597,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49893,-0.04345,0.1254]}],"total_contact_groups":5},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50599,0.08087,0.03378],"final_tcp_position":[0.49765,-0.00812,0.18204],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":4.32595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54626,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":406.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52857,0.13787,0.11713],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54639,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":252.0,"raw_peak_contact_force":0.55014,"subtask_id":"contact","tcp_end":[0.50642,0.11491,0.07652],"tcp_start":[0.52857,0.13787,0.11713],"tcp_to_object_dist_end":0.05463,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":495.0,"raw_peak_contact_force":0.55007,"subtask_id":"push","tcp_end":[0.50306,-0.0792,0.07169],"tcp_start":[0.50642,0.11491,0.07652],"tcp_to_object_dist_end":0.16452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":384.0,"n_steps_budget":960.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":384.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.49765,-0.00812,0.18204],"tcp_start":[0.50306,-0.0792,0.07169],"tcp_to_object_dist_end":0.17311,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91065,"average_solve_count":291.0,"average_success_count":291.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06261,"contact_peg.contact_force":14.85861,"contact_peg.contact_speed":0.01494,"push_channel.push_distance":0.23839,"push_channel.push_speed":0.0311},"optimized_scores":{"best_composite_score":-0.04696,"best_fitness_score":0.26304,"best_task_score":5e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":345.0,"contact_point_centroid":[0.50538,0.10459,0.00936],"force_p95":0.59628,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57913,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50907,0.17836,0.20396]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50022,0.19872,0.29516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.50619,0.10469,0.00939],"force_p95":0.57549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.5463,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5109,0.14888,0.09683]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.50579,0.1047,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57608,"mean_force":0.54636,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50159,0.02842,0.07259]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.50598,0.10448,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57571,"mean_force":0.54631,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49799,-0.04456,0.12568]}],"total_contact_groups":5},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50582,0.10462,0.03384],"final_tcp_position":[0.49748,-0.00833,0.18209],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3.33087,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10472,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54139,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":377.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.5187,0.15905,0.11829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.50589,0.10472,0.03383],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.55211,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":242.0,"raw_peak_contact_force":0.57865,"subtask_id":"contact","tcp_end":[0.50468,0.13825,0.07697],"tcp_start":[0.5187,0.15905,0.11829],"tcp_to_object_dist_end":0.05474,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10467,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54958,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":567.0,"raw_peak_contact_force":0.57608,"subtask_id":"push","tcp_end":[0.50133,-0.08121,0.07217],"tcp_start":[0.50468,0.13825,0.07697],"tcp_to_object_dist_end":0.18986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":384.0,"n_steps_budget":960.0,"object_pos_end":[0.50582,0.10462,0.03384],"object_pos_start":[0.50599,0.10467,0.03384],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"peak_contact_force":0.55006,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":384.0,"raw_peak_contact_force":0.57571,"tcp_end":[0.49748,-0.00833,0.18209],"tcp_start":[0.50133,-0.08121,0.07217],"tcp_to_object_dist_end":0.18656,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64045,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08119,"contact_peg.contact_force":8.24936,"contact_peg.contact_speed":0.03459,"push_channel.push_distance":0.19991,"push_channel.push_speed":0.07},"optimized_scores":{"best_composite_score":-0.03109,"best_fitness_score":0.27891,"best_task_score":6e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.50312,0.06744,0.00932],"force_p95":0.6198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57022,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49951,0.16221,0.20592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.50292,0.06753,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55198,"mean_force":0.54665,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49828,0.11274,0.09408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.50313,0.06747,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55083,"mean_force":0.54664,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49606,0.00976,0.07031]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50305,0.06734,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55068,"mean_force":0.54665,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49493,-0.04409,0.12466]}],"total_contact_groups":4},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50301,0.06745,0.0338],"final_tcp_position":[0.49691,-0.00814,0.18207],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54817,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":365.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49998,0.12594,0.11748],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":960.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.5472,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":320.0,"raw_peak_contact_force":0.55198,"subtask_id":"contact","tcp_end":[0.49902,0.10027,0.07446],"tcp_start":[0.49998,0.12594,0.11748],"tcp_to_object_dist_end":0.05239,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54558,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":452.0,"raw_peak_contact_force":0.55083,"subtask_id":"push","tcp_end":[0.49572,-0.08064,0.06977],"tcp_start":[0.49902,0.10027,0.07446],"tcp_to_object_dist_end":0.15256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":960.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54671,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":390.0,"raw_peak_contact_force":0.55068,"tcp_end":[0.49691,-0.00814,0.18207],"tcp_start":[0.49572,-0.08064,0.06977],"tcp_to_object_dist_end":0.16654,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```