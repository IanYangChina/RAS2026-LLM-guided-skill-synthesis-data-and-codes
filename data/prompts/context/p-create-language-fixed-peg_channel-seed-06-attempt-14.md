## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0804 | 0.24 | ❌ rejected |
| 13 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3200 | 0.02 | ❌ rejected |
| 12 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1442 | 0.56 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0809 | 0.60 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3150 | 0.68 | ❌ rejected |

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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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

## Current Skill (Q=-0.080) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_behind_peg
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
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: engage_peg
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    lateral_jitter:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **engage_peg** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - lateral_jitter: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.080
- **task_score** (E): 0.242
- **fitness_score**: 0.280  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descent_to_safe_z | 1.00 | 1.00 | 0.1543 |
| lateral_approach_behind | 1.00 | 1.00 | 0.0208 |
| contact_engage | 1.00 | 1.00 | 0.1153 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descent_to_safe_z | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.112, 0.174) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.527 | 2.127 |
| lateral_approach_behind | align | 1.00 / step_budget | (0.498, 0.112, 0.174)→(0.497, 0.126, 0.159) | (0.501, 0.100, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 0.604 |
| contact_engage | contact | 1.00 / step_budget | (0.497, 0.126, 0.159)→(0.504, 0.125, 0.044) | (0.501, 0.099, 0.034)→(0.502, 0.098, 0.031) | 0.180→0.179 | 1.00 / 2.333 | 126.081 | 189.439 |
| push_through_channel | push | 0.00 / guard_failure | (0.503, 0.077, 0.043)→(0.503, 0.077, 0.043) | (0.502, 0.098, 0.031)→(0.500, 0.052, 0.031) | 0.179→0.136 | 1.00 / 3.000 | 81.842 | 101.207 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.941
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.725
- phase_score: 0.559
- phase_breakdown.push_score: 0.606
- phase_breakdown.approach_score: 0.068
- phase_breakdown.contact_score: 0.912

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.626
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.725
- **Median Q (composite search score)**: -0.247
- **K-run variance**: 0.0600
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.282


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83012,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_engage.engage_speed":0.02217,"descent_to_safe_z.descent_speed":0.19168,"lateral_approach_behind.lateral_speed":0.10489,"push_through_channel.lateral_jitter":-0.00343,"push_through_channel.push_distance":0.1791,"push_through_channel.push_speed":0.03358},"optimized_scores":{"best_composite_score":0.26589,"best_fitness_score":0.62589,"best_task_score":0.72548},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":193.0,"contact_point_centroid":[0.51378,0.08171,0.05399],"force_p95":166.09533,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.87162,"mean_force":132.62593,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50617,0.08984,0.05238]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.50648,0.07057,0.009],"force_p95":165.91897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.04176,"mean_force":43.12411,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.5006,0.09237,0.09158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.49287,-0.10063,0.06043],"force_p95":38.06308,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.11606,"mean_force":24.18123,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50288,-0.05328,0.0383]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.4997,0.00271,0.04202],"force_p95":29.69183,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.64441,"mean_force":6.94516,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50311,0.01385,0.03875]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.49601,-0.01426,0.00965],"force_p95":19.84174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.74525,"mean_force":5.24984,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50327,0.02096,0.03897]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":201.0,"contact_point_centroid":[0.47476,-0.0281,0.03351],"force_p95":8.51649,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.88104,"mean_force":1.84367,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50296,0.0,0.03851]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":110.0,"contact_point_centroid":[0.52508,0.06835,0.05644],"force_p95":7.15074,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.10924,"mean_force":2.85398,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50851,0.09018,0.05074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":302.0,"contact_point_centroid":[0.50311,0.0674,0.0093],"force_p95":0.68556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57515,"phase_index":0.0,"phase_name":"descent_to_safe_z","phase_type":"approach","tcp_position_centroid":[0.49974,0.13965,0.23259]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50243,0.06748,0.00938],"force_p95":0.55321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5555,"mean_force":0.54655,"phase_index":1.0,"phase_name":"lateral_approach_behind","phase_type":"align","tcp_position_centroid":[0.49982,0.08706,0.1657]}],"total_contact_groups":9},"final_pose_error":0.03515,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49286,-0.08306,0.03624],"final_tcp_position":[0.50268,-0.05516,0.03804],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":173.87162,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":660.0,"object_pos_end":[0.50301,0.06744,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.1476,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54259,"phase_name":"descent_to_safe_z","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":302.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.50041,0.08281,0.17186],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50301,0.06744,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.1476,"object_z_max":0.0338,"peak_contact_force":0.54833,"phase_name":"lateral_approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":57.0,"raw_peak_contact_force":0.5555,"tcp_end":[0.49976,0.09421,0.15932],"tcp_start":[0.50041,0.08281,0.17186],"tcp_to_object_dist_end":0.12837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.49966,0.05662,0.03621],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.13668,"object_to_goal_dist_start":0.14766,"object_z_max":0.03595,"peak_contact_force":0.35962,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":902.0,"raw_peak_contact_force":173.87162,"subtask_id":"contact","tcp_end":[0.5062,0.08929,0.04285],"tcp_start":[0.49976,0.09421,0.15932],"tcp_to_object_dist_end":0.03397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.49294,-0.0824,0.03661],"object_pos_start":[0.49966,0.05662,0.03621],"object_to_goal_dist_end":0.00819,"object_to_goal_dist_start":0.13668,"object_z_max":0.04014,"peak_contact_force":0.78162,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":609.0,"raw_peak_contact_force":41.11606,"subtask_id":"push","tcp_end":[0.50268,-0.05516,0.03804],"tcp_start":[0.50274,-0.05506,0.03811],"tcp_to_object_dist_end":0.02896,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38636,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_engage.engage_speed":0.05867,"descent_to_safe_z.descent_speed":0.25406,"lateral_approach_behind.lateral_speed":0.14556,"push_through_channel.lateral_jitter":-0.00129,"push_through_channel.push_distance":0.15084,"push_through_channel.push_speed":0.03227},"optimized_scores":{"best_composite_score":-0.24666,"best_fitness_score":0.11334,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":488.0,"contact_point_centroid":[0.50681,0.11386,0.00893],"force_p95":180.95763,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.06009,"mean_force":40.50445,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.5014,0.13614,0.09334]},{"body_a":"attachment","body_b":"peg","contact_count":144.0,"contact_point_centroid":[0.51287,0.12747,0.05252],"force_p95":194.96966,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":199.50789,"mean_force":135.52097,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50481,0.13539,0.05141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50718,0.11915,0.00636],"force_p95":148.35887,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.69212,"mean_force":119.84115,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50863,0.13815,0.04557]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51413,0.12831,0.04818],"force_p95":146.22164,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.28418,"mean_force":118.77302,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50863,0.13815,0.04557]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52505,0.118,0.04259],"force_p95":9.14735,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35191,"mean_force":1.94913,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50837,0.13781,0.04597]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52506,0.11537,0.02988],"force_p95":2.9962,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.52494,"mean_force":0.88123,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50863,0.13815,0.04557]},{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.50353,0.11169,0.00932],"force_p95":0.75912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57729,"phase_index":0.0,"phase_name":"descent_to_safe_z","phase_type":"approach","tcp_position_centroid":[0.50291,0.15979,0.23291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":67.0,"contact_point_centroid":[0.50309,0.11166,0.00944],"force_p95":0.58852,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6335,"mean_force":0.54235,"phase_index":1.0,"phase_name":"lateral_approach_behind","phase_type":"align","tcp_position_centroid":[0.50446,0.12945,0.16719]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"descent_to_safe_z","phase_type":"approach","tcp_position_centroid":[0.49994,0.19864,0.29817]}],"total_contact_groups":9},"final_pose_error":0.15106,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50705,0.11534,0.02922],"final_tcp_position":[0.50873,0.1383,0.04567],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":200.06009,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":265.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11184,0.03389],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19197,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51579,"phase_name":"descent_to_safe_z","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":259.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50635,0.12377,0.17502],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":67.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.11176,0.03385],"object_pos_start":[0.50371,0.11184,0.03389],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19197,"object_z_max":0.03395,"peak_contact_force":0.53432,"phase_name":"lateral_approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":67.0,"raw_peak_contact_force":0.6335,"tcp_end":[0.50281,0.13807,0.15949],"tcp_start":[0.50635,0.12377,0.17502],"tcp_to_object_dist_end":0.12836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.50709,0.11524,0.02912],"object_pos_start":[0.50372,0.11176,0.03385],"object_to_goal_dist_end":0.19567,"object_to_goal_dist_start":0.1919,"object_z_max":0.0341,"peak_contact_force":200.06009,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":646.0,"raw_peak_contact_force":200.06009,"subtask_id":"contact","tcp_end":[0.50857,0.13808,0.04555],"tcp_start":[0.50281,0.13807,0.15949],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50709,0.11526,0.02913],"object_pos_start":[0.50709,0.11524,0.02912],"object_to_goal_dist_end":0.19569,"object_to_goal_dist_start":0.19567,"object_z_max":0.02918,"peak_contact_force":149.69212,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":149.69212,"subtask_id":"push","tcp_end":[0.50873,0.1383,0.04567],"tcp_start":[0.50869,0.13822,0.04561],"tcp_to_object_dist_end":0.02841,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38636,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_engage.engage_speed":0.0584,"descent_to_safe_z.descent_speed":0.20862,"lateral_approach_behind.lateral_speed":0.13077,"push_through_channel.lateral_jitter":-0.00461,"push_through_channel.push_distance":0.18502,"push_through_channel.push_speed":0.034},"optimized_scores":{"best_composite_score":-0.26053,"best_fitness_score":0.09947,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":131.0,"contact_point_centroid":[0.50144,0.13451,0.05127],"force_p95":177.86596,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":194.38675,"mean_force":118.96683,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49499,0.14341,0.05035]},{"body_a":"peg","body_b":"channel_base_body","contact_count":492.0,"contact_point_centroid":[0.498,0.11925,0.00899],"force_p95":135.41196,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.02581,"mean_force":28.58988,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49042,0.14455,0.09497]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50227,0.13684,0.0467],"force_p95":110.14973,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.81395,"mean_force":97.44885,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49863,0.14703,0.04426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.48997,0.11877,0.00701],"force_p95":84.53813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.78094,"mean_force":78.47361,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49863,0.14703,0.04426]},{"body_a":"peg","body_b":"world","contact_count":55.0,"contact_point_centroid":[0.4983,0.13114,-0.00037],"force_p95":49.44444,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.60705,"mean_force":34.54054,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49726,0.14541,0.04605]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.499,0.13046,-0.00063],"force_p95":29.06713,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.4981,"mean_force":22.50667,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49863,0.14703,0.04426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.49636,0.11911,0.0094],"force_p95":0.68908,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57321,"phase_index":0.0,"phase_name":"descent_to_safe_z","phase_type":"approach","tcp_position_centroid":[0.49228,0.16296,0.23292]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"descent_to_safe_z","phase_type":"approach","tcp_position_centroid":[0.49943,0.19781,0.29631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.49632,0.11893,0.00941],"force_p95":0.60284,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6244,"mean_force":0.54285,"phase_index":1.0,"phase_name":"lateral_approach_behind","phase_type":"align","tcp_position_centroid":[0.48746,0.13737,0.16739]}],"total_contact_groups":9},"final_pose_error":0.1853,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49907,0.12338,0.02878],"final_tcp_position":[0.49873,0.14721,0.04433],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":194.38675,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":255.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11932,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19946,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5235,"phase_name":"descent_to_safe_z","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":254.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48616,0.1305,0.17627],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":79.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11904,0.0339],"object_pos_start":[0.49602,0.11932,0.03386],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.0339,"peak_contact_force":0.59728,"phase_name":"lateral_approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":79.0,"raw_peak_contact_force":0.6244,"tcp_end":[0.48983,0.14675,0.1589],"tcp_start":[0.48616,0.1305,0.17627],"tcp_to_object_dist_end":0.12819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.49907,0.12333,0.02871],"object_pos_start":[0.49602,0.11904,0.0339],"object_to_goal_dist_end":0.20364,"object_to_goal_dist_start":0.19917,"object_z_max":0.03412,"peak_contact_force":177.82193,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":678.0,"raw_peak_contact_force":194.38675,"subtask_id":"contact","tcp_end":[0.49861,0.14693,0.04427],"tcp_start":[0.48983,0.14675,0.1589],"tcp_to_object_dist_end":0.02827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49903,0.12334,0.02871],"object_pos_start":[0.49907,0.12333,0.02871],"object_to_goal_dist_end":0.20365,"object_to_goal_dist_start":0.20364,"object_z_max":0.02874,"peak_contact_force":95.05244,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":112.81395,"subtask_id":"push","tcp_end":[0.49873,0.14721,0.04433],"tcp_start":[0.49867,0.14713,0.04428],"tcp_to_object_dist_end":0.02854,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```