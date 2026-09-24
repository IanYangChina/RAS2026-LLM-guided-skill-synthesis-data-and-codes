## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1221 | 0.71 | ❌ rejected |
| 11 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2293 | 0.09 | ❌ rejected |
| 10 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1634 | 0.00 | ❌ rejected |
| 9 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1128 | 0.48 | ❌ rejected |
| 8 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0107 | 0.35 | ❌ rejected |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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

## Current Skill (Q=0.122) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_high
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
    - 0.08
    orientation:
      mode: none
  parameters:
    clearance_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
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
- id: approach_final
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
    - 0.0
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
- id: contact_peg
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
      mode: keep_current
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
- id: push_through
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
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.16
      - 0.25
      default: 0.18
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
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.08]
  - orientation: mode=none
  - parameter_bindings:
    - clearance_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_final** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.122
- **task_score** (E): 0.711
- **fitness_score**: 0.629  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1904 |
| descend | 1.00 | 1.00 | 0.0731 |
| approach_north | 1.00 | 0.67 | 0.0534 |
| contact_side | 1.00 | 1.00 | 0.0118 |
| push_through | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.168, 0.115) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.557 | 2.179 |
| descend | descend | 1.00 / step_budget | (0.494, 0.168, 0.115)→(0.496, 0.161, 0.043) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.533 | 0.575 |
| approach_north | approach | 1.00 / step_budget | (0.496, 0.161, 0.043)→(0.495, 0.109, 0.030) | (0.500, 0.081, 0.034)→(0.500, 0.079, 0.035) | 0.161→0.159 | 0.67 / 1.000 | 1.904 | 12.240 |
| contact_side | contact | 1.00 / force_exceeded | (0.495, 0.109, 0.030)→(0.495, 0.097, 0.029) | (0.500, 0.079, 0.035)→(0.503, 0.068, 0.036) | 0.159→0.148 | 1.00 / 2.333 | 1321.623 | 10.830 |
| push_through | push | 0.00 / guard_failure | (0.494, 0.008, 0.027)→(0.494, 0.008, 0.027) | (0.503, 0.068, 0.036)→(0.507, -0.020, 0.036) | 0.148→0.065 | 1.00 / 3.000 | 105.542 | 111.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.916
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.892
- phase_score: 0.625
- phase_breakdown.push_score: 0.585
- phase_breakdown.contact_score: 0.684
- phase_breakdown.approach_score: 0.684

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.777
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.137
- **K-run variance**: 0.0210
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34694,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.arc_height":0.09076,"approach_high.speed":0.06343,"approach_north.speed":0.0354,"contact_side.contact_force":8.27997,"contact_side.speed":0.03183,"descend.speed":0.04711,"push_through.force_guard_threshold":31.124,"push_through.push_distance":0.1888,"push_through.push_speed":0.06998,"push_through.push_tolerance":0.02261,"push_through.retry_lateral_shift":-0.00376},"optimized_scores":{"best_composite_score":0.2917,"best_fitness_score":0.7317,"best_task_score":0.8921},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":215.0,"contact_point_centroid":[0.50296,0.00103,0.04449],"force_p95":12.75017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.46708,"mean_force":2.46953,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49802,0.01257,0.02717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50582,-0.10091,0.04293],"force_p95":26.89059,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.74973,"mean_force":6.09654,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49986,-0.05279,0.02824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":103.0,"contact_point_centroid":[0.50584,-0.03823,0.0098],"force_p95":17.35754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.26012,"mean_force":4.35461,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49823,0.00512,0.02728]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":99.0,"contact_point_centroid":[0.52524,0.0021,0.02873],"force_p95":5.50562,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.74234,"mean_force":1.43979,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49773,0.03105,0.02718]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.50383,0.06098,0.00938],"force_p95":0.55002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.58244,"mean_force":0.67608,"phase_index":2.0,"phase_name":"approach_north","phase_type":"approach","tcp_position_centroid":[0.49883,0.11565,0.03519]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50252,0.07883,0.04452],"force_p95":8.31624,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.20831,"mean_force":4.52378,"phase_index":2.0,"phase_name":"approach_north","phase_type":"approach","tcp_position_centroid":[0.49943,0.09077,0.03058]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50294,0.03441,0.0099],"force_p95":2.87374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.71768,"mean_force":1.77985,"phase_index":3.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49783,0.07965,0.02826]},{"body_a":"attachment","body_b":"peg","contact_count":289.0,"contact_point_centroid":[0.50181,0.06711,0.04006],"force_p95":2.50291,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.19863,"mean_force":1.44956,"phase_index":3.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.4978,0.07892,0.02822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":974.0,"contact_point_centroid":[0.5037,0.0616,0.00936],"force_p95":0.58195,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55496,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50404,0.22191,0.18583]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49979,0.20082,0.29911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":238.0,"contact_point_centroid":[0.50363,0.06157,0.00938],"force_p95":0.55002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55004,"mean_force":0.54678,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50361,0.14497,0.07906]}],"total_contact_groups":11},"final_pose_error":0.0905,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50542,-0.08505,0.03528],"final_tcp_position":[0.49998,-0.05591,0.0283],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":3919.50456,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06156,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.5457,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":993.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50777,0.14844,0.11355],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06159,0.03378],"object_pos_start":[0.50376,0.06156,0.03378],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14175,"object_z_max":0.03378,"peak_contact_force":0.55002,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":238.0,"raw_peak_contact_force":0.55004,"tcp_end":[0.50085,0.14181,0.04332],"tcp_start":[0.50777,0.14844,0.11355],"tcp_to_object_dist_end":0.08083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.50392,0.0602,0.03516],"object_pos_start":[0.50377,0.06159,0.03378],"object_to_goal_dist_end":0.14034,"object_to_goal_dist_start":0.14178,"object_z_max":0.03496,"peak_contact_force":0.0,"phase_name":"approach_north","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":277.0,"raw_peak_contact_force":9.58244,"subtask_id":"approach","tcp_end":[0.49948,0.08983,0.03044],"tcp_start":[0.50085,0.14181,0.04332],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":340.0,"n_steps_budget":600.0,"object_pos_end":[0.50685,0.04296,0.03576],"object_pos_start":[0.50392,0.0602,0.03516],"object_to_goal_dist_end":0.12322,"object_to_goal_dist_start":0.14034,"object_z_max":0.03575,"peak_contact_force":3919.50456,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":584.0,"raw_peak_contact_force":6.71768,"subtask_id":"contact","tcp_end":[0.49866,0.07208,0.02911],"tcp_start":[0.49948,0.08983,0.03044],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.50542,-0.08495,0.03525],"object_pos_start":[0.50685,0.04296,0.03576],"object_to_goal_dist_end":0.00874,"object_to_goal_dist_start":0.12322,"object_z_max":0.03845,"peak_contact_force":26.12163,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":431.0,"raw_peak_contact_force":31.46708,"subtask_id":"push","tcp_end":[0.49998,-0.05591,0.0283],"tcp_start":[0.49997,-0.0556,0.02831],"tcp_to_object_dist_end":0.03036,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91489,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.arc_height":0.08272,"approach_high.speed":0.03988,"approach_north.speed":0.04426,"contact_side.contact_force":6.16167,"contact_side.speed":0.02877,"descend.speed":0.04934,"push_through.force_guard_threshold":27.76736,"push_through.push_distance":0.19296,"push_through.push_speed":0.06114,"push_through.push_tolerance":0.01822,"push_through.retry_lateral_shift":-0.00711},"optimized_scores":{"best_composite_score":0.13682,"best_fitness_score":0.77682,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53022,0.11026,0.05999],"force_p95":254.64173,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.40662,"mean_force":157.75772,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49357,0.10339,0.02582]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.50154,0.10423,0.04599],"force_p95":21.62416,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.08343,"mean_force":8.81854,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49442,0.11541,0.02703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.50586,0.0765,0.00993],"force_p95":20.98325,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.01842,"mean_force":7.07857,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49483,0.12074,0.02766]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52515,0.08576,0.04279],"force_p95":21.38192,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.6512,"mean_force":9.42499,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49431,0.11376,0.02686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.50093,0.11534,0.00945],"force_p95":0.60276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.41454,"mean_force":0.80984,"phase_index":2.0,"phase_name":"approach_north","phase_type":"approach","tcp_position_centroid":[0.49536,0.16987,0.03486]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49989,0.13323,0.04739],"force_p95":11.2563,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.9401,"mean_force":7.9411,"phase_index":2.0,"phase_name":"approach_north","phase_type":"approach","tcp_position_centroid":[0.49644,0.14511,0.03055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50192,0.08958,0.00991],"force_p95":3.26597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.52684,"mean_force":1.80972,"phase_index":3.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49492,0.13425,0.02812]},{"body_a":"attachment","body_b":"peg","contact_count":258.0,"contact_point_centroid":[0.49998,0.12176,0.04053],"force_p95":2.97275,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.94554,"mean_force":1.5245,"phase_index":3.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49487,0.13329,0.02803]},{"body_a":"peg","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52232,0.09191,0.06233],"force_p95":3.91982,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.92616,"mean_force":2.08013,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49413,0.11069,0.02644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":958.0,"contact_point_centroid":[0.50096,0.11603,0.00939],"force_p95":0.61279,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55206,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49804,0.24783,0.21179]},{"body_a":"peg","body_b":"channel_base_body","contact_count":251.0,"contact_point_centroid":[0.50081,0.11595,0.00943],"force_p95":0.5988,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62076,"mean_force":0.54149,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4964,0.20025,0.08006]}],"total_contact_groups":11},"final_pose_error":0.19811,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50748,0.0744,0.03623],"final_tcp_position":[0.49355,0.10306,0.02582],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":265.40662,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11603,0.03384],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.57392,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":958.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49775,0.20483,0.11658],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11601,0.03399],"object_pos_start":[0.50097,0.11603,0.03384],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19613,"object_z_max":0.03399,"peak_contact_force":0.50354,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":251.0,"raw_peak_contact_force":0.62076,"tcp_end":[0.49683,0.19615,0.0428],"tcp_start":[0.49775,0.20483,0.11658],"tcp_to_object_dist_end":0.08073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":259.0,"n_steps_budget":870.0,"object_pos_end":[0.50121,0.11439,0.03523],"object_pos_start":[0.50095,0.11601,0.03399],"object_to_goal_dist_end":0.19445,"object_to_goal_dist_start":0.1961,"object_z_max":0.03504,"peak_contact_force":0.0,"phase_name":"approach_north","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":268.0,"raw_peak_contact_force":12.41454,"subtask_id":"approach","tcp_end":[0.49652,0.14424,0.03046],"tcp_start":[0.49683,0.19615,0.0428],"tcp_to_object_dist_end":0.03059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.50679,0.09861,0.03595],"object_pos_start":[0.50121,0.11439,0.03523],"object_to_goal_dist_end":0.17879,"object_to_goal_dist_start":0.19445,"object_z_max":0.03602,"peak_contact_force":26.12163,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":531.0,"raw_peak_contact_force":6.52684,"subtask_id":"contact","tcp_end":[0.49571,0.12697,0.02884],"tcp_start":[0.49652,0.14424,0.03046],"tcp_to_object_dist_end":0.03126,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":72.0,"n_steps_budget":1000.0,"object_pos_end":[0.50746,0.07464,0.03625],"object_pos_start":[0.50679,0.09861,0.03595],"object_to_goal_dist_end":0.15486,"object_to_goal_dist_start":0.17879,"object_z_max":0.03686,"peak_contact_force":265.40662,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":140.0,"raw_peak_contact_force":265.40662,"subtask_id":"push","tcp_end":[0.49355,0.10306,0.02582],"tcp_start":[0.49357,0.10324,0.02581],"tcp_to_object_dist_end":0.03332,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30698,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.arc_height":0.10074,"approach_high.speed":0.04749,"approach_north.speed":0.03921,"contact_side.contact_force":11.82513,"contact_side.speed":0.03688,"descend.speed":0.05472,"push_through.force_guard_threshold":28.32006,"push_through.push_distance":0.2301,"push_through.push_speed":0.04324,"push_through.push_tolerance":0.03078,"push_through.retry_lateral_shift":0.0002},"optimized_scores":{"best_composite_score":-0.06208,"best_fitness_score":0.37792,"best_task_score":0.24104},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":114.0,"contact_point_centroid":[0.49505,0.0207,0.05206],"force_p95":16.11026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.16677,"mean_force":2.57864,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48882,0.03174,0.02798]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52561,-0.04386,0.03897],"force_p95":23.35569,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.34967,"mean_force":4.54462,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48918,-0.01773,0.028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":81.0,"contact_point_centroid":[0.49943,0.00256,0.00928],"force_p95":16.44083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.77212,"mean_force":3.68529,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48878,0.04171,0.02807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49289,0.04515,0.00971],"force_p95":19.24403,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.24403,"mean_force":19.24403,"phase_index":3.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49021,0.09197,0.03053]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49334,0.0802,0.044],"force_p95":19.11589,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.11589,"mean_force":19.11589,"phase_index":3.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49021,0.09197,0.03053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":274.0,"contact_point_centroid":[0.49537,0.06313,0.00941],"force_p95":0.55165,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.72287,"mean_force":0.69101,"phase_index":2.0,"phase_name":"approach_north","phase_type":"approach","tcp_position_centroid":[0.48835,0.1177,0.0344]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.4941,0.08127,0.05081],"force_p95":11.01249,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.27356,"mean_force":3.73128,"phase_index":2.0,"phase_name":"approach_north","phase_type":"approach","tcp_position_centroid":[0.49009,0.093,0.03064]},{"body_a":"peg","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.51445,-0.00629,0.06451],"force_p95":1.40006,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.52848,"mean_force":0.587,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48875,0.01489,0.02768]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47494,0.04503,0.05427],"force_p95":3.32571,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.6096,"mean_force":1.14559,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48881,0.07669,0.02865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":961.0,"contact_point_centroid":[0.49528,0.06381,0.00938],"force_p95":0.55727,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55436,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48608,0.22284,0.18756]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49951,0.2014,0.29842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.4952,0.06434,0.0094],"force_p95":0.55077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55315,"mean_force":0.54514,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48224,0.14746,0.07786]}],"total_contact_groups":12},"final_pose_error":0.14528,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5074,-0.04895,0.03503],"final_tcp_position":[0.48921,-0.0227,0.02804],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":38.16677,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.49537,0.06392,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55112,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":989.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47769,0.15128,0.11425],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":277.0,"n_steps_budget":960.0,"object_pos_end":[0.49483,0.06396,0.03402],"object_pos_start":[0.49537,0.06392,0.03401],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.14412,"object_z_max":0.03402,"peak_contact_force":0.54427,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":277.0,"raw_peak_contact_force":0.55315,"tcp_end":[0.48908,0.14404,0.04152],"tcp_start":[0.47769,0.15128,0.11425],"tcp_to_object_dist_end":0.08063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":274.0,"n_steps_budget":990.0,"object_pos_end":[0.49483,0.06263,0.03471],"object_pos_start":[0.49483,0.06396,0.03402],"object_to_goal_dist_end":0.14282,"object_to_goal_dist_start":0.14418,"object_z_max":0.03449,"peak_contact_force":5.71075,"phase_name":"approach_north","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":285.0,"raw_peak_contact_force":14.72287,"subtask_id":"approach","tcp_end":[0.49021,0.09197,0.03053],"tcp_start":[0.48908,0.14404,0.04152],"tcp_to_object_dist_end":0.02999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49476,0.0624,0.03494],"object_pos_start":[0.49483,0.06263,0.03471],"object_to_goal_dist_end":0.14259,"object_to_goal_dist_start":0.14282,"object_z_max":0.03471,"peak_contact_force":19.24403,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":19.24403,"subtask_id":"contact","tcp_end":[0.49021,0.09185,0.03049],"tcp_start":[0.49021,0.09197,0.03053],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.50754,-0.04847,0.03519],"object_pos_start":[0.49476,0.0624,0.03494],"object_to_goal_dist_end":0.03277,"object_to_goal_dist_start":0.14259,"object_z_max":0.03963,"peak_contact_force":25.09903,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":260.0,"raw_peak_contact_force":38.16677,"subtask_id":"push","tcp_end":[0.48921,-0.0227,0.02804],"tcp_start":[0.48924,-0.02222,0.02806],"tcp_to_object_dist_end":0.03242,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```