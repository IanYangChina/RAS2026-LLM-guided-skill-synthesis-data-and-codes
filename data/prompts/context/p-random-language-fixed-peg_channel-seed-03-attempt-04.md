## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.0574 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1946 | 0.11 | ✅ accepted |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1599 | 0.00 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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

## Current Skill (Q=0.057) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
- id: contact
  type: descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5
      binds_to:
      - path: termination.force_threshold
        mode: add
  guards:
  - id: contact_guard
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: contact
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (add)
  - guards:
    - id=contact_guard, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=reduce_speed
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.02, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.057
- **task_score** (E): 0.003
- **fitness_score**: 0.004  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 0.00 | 1.00 | 0.2149 |
| descend | 1.00 | 1.00 | 0.0003 |
| push | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.609, 0.220, 0.165) | (0.509, 0.081, 0.040)→(0.502, 0.080, 0.034) | 0.165→0.160 | 1.00 / 2.000 | 430.501 | 1313.402 |
| descend | descend | 1.00 / force_exceeded | (0.609, 0.220, 0.165)→(0.610, 0.220, 0.164) | (0.502, 0.080, 0.034)→(0.502, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 269.756 | 269.756 |
| push | push | 0.00 / guard_failure | (0.610, 0.220, 0.164)→(0.610, 0.220, 0.165) | (0.502, 0.080, 0.034)→(0.502, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.000 | 281.348 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.021
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.007
- phase_score: 0.004
- phase_breakdown.push_score: 0.002
- phase_breakdown.approach_score: 0.007
- phase_breakdown.contact_score: 0.007

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.005
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.007
- **Median Q (composite search score)**: 0.057
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.288


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.32143,"average_solve_count":28.0,"average_success_count":28.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.19587,"descend.contact_force_threshold":6.91892,"push.push_distance":0.17815,"push.push_force_threshold":13.82396,"push.push_speed":0.0424},"optimized_scores":{"best_composite_score":0.0586,"best_fitness_score":0.00527,"best_task_score":0.00685},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":525.0,"contact_point_centroid":[0.52509,0.10103,0.05972],"force_p95":806.52399,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1320.47632,"mean_force":643.94069,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51715,0.19734,0.24258]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.525,0.08401,0.05998],"force_p95":260.88763,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.88763,"mean_force":260.88763,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.485,0.102,0.28529]},{"body_a":"peg","body_b":"link6","contact_count":69.0,"contact_point_centroid":[0.50416,0.0805,0.05915],"force_p95":123.64601,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.64064,"mean_force":33.17205,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4995,0.12965,0.28173]},{"body_a":"peg","body_b":"channel_base_body","contact_count":596.0,"contact_point_centroid":[0.49659,0.06006,0.00939],"force_p95":29.68761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.26979,"mean_force":4.49962,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50964,0.1968,0.23489]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52502,0.08392,0.0599],"force_p95":127.86598,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":127.86598,"mean_force":127.86598,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48517,0.10218,0.28512]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":51.0,"contact_point_centroid":[0.5253,0.06733,0.0578],"force_p95":8.30449,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.67489,"mean_force":6.97593,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49567,0.12304,0.28325]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":48.0,"contact_point_centroid":[0.46988,0.05749,0.04356],"force_p95":1.13549,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.39541,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49591,0.16936,0.28022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.4978,0.03869,0.00944],"force_p95":0.43101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43101,"mean_force":0.43101,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.485,0.102,0.28529]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49597,0.03844,0.00942],"force_p95":0.42351,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42351,"mean_force":0.42351,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48517,0.10218,0.28512]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.47448,0.11973,0.05912],"force_p95":0.0,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.39394,0.25233,0.12137]}],"total_contact_groups":10},"final_pose_error":0.43593,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49471,0.05551,0.03455],"final_tcp_position":[0.48471,0.10181,0.28542],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1320.47632,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":627.0,"n_steps_budget":780.0,"object_pos_end":[0.49451,0.05522,0.03463],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13544,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":651.70701,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1302.0,"raw_peak_contact_force":1320.47632,"subtask_id":"approach","tcp_end":[0.48517,0.10218,0.28512],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25503,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49461,0.05536,0.03459],"object_pos_start":[0.49451,0.05522,0.03463],"object_to_goal_dist_end":0.13557,"object_to_goal_dist_start":0.13544,"object_z_max":0.03463,"peak_contact_force":127.86598,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":127.86598,"subtask_id":"contact","tcp_end":[0.485,0.102,0.28529],"tcp_start":[0.48517,0.10218,0.28512],"tcp_to_object_dist_end":0.25518,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49471,0.05551,0.03455],"object_pos_start":[0.49461,0.05536,0.03459],"object_to_goal_dist_end":0.13572,"object_to_goal_dist_start":0.13557,"object_z_max":0.03459,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":260.88763,"subtask_id":"push","tcp_end":[0.48471,0.10181,0.28542],"tcp_start":[0.485,0.102,0.28529],"tcp_to_object_dist_end":0.2553,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.16981,"average_mean_iterations":38.45283,"average_solve_count":53.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11282,"descend.contact_force_threshold":7.92047,"push.push_distance":0.0002,"push.push_force_threshold":21.15503,"push.push_speed":0.04741},"optimized_scores":{"best_composite_score":0.05692,"best_fitness_score":0.00359,"best_task_score":0.00157},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":911.0,"contact_point_centroid":[0.5356,0.11969,0.05978],"force_p95":571.54766,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1245.51466,"mean_force":419.73816,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.61837,0.27075,0.16071]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.555,0.11998,0.05992],"force_p95":348.51118,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.51118,"mean_force":348.51118,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.67411,0.27563,0.09524]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.555,0.11999,0.05997],"force_p95":286.95762,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.95762,"mean_force":286.95762,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.67442,0.27566,0.09507]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.50437,0.08126,0.00944],"force_p95":0.66174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.58646,"mean_force":0.81738,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.60778,0.26705,0.16057]},{"body_a":"peg","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.5094,0.09706,0.05963],"force_p95":19.80189,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.17298,"mean_force":7.74164,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.42973,0.27171,0.15466]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52928,0.08045,0.0406],"force_p95":1.08008,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.32944,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5359,0.22366,0.24449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51956,0.0692,0.00943],"force_p95":0.54162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54162,"mean_force":0.54162,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.67411,0.27563,0.09524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51744,0.06702,0.00943],"force_p95":0.54137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54137,"mean_force":0.54137,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.67442,0.27566,0.09507]}],"total_contact_groups":8},"final_pose_error":0.4003,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50603,0.08005,0.03434],"final_tcp_position":[0.67462,0.27577,0.09506],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1245.51466,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.0802,0.03434],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16041,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":313.43382,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1978.0,"raw_peak_contact_force":1245.51466,"subtask_id":"approach","tcp_end":[0.67411,0.27563,0.09524],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.26477,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.08012,0.03434],"object_pos_start":[0.50619,0.0802,0.03434],"object_to_goal_dist_end":0.16033,"object_to_goal_dist_start":0.16041,"object_z_max":0.03434,"peak_contact_force":348.51118,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":348.51118,"subtask_id":"contact","tcp_end":[0.67442,0.27566,0.09507],"tcp_start":[0.67411,0.27563,0.09524],"tcp_to_object_dist_end":0.26505,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.08005,0.03434],"object_pos_start":[0.50611,0.08012,0.03434],"object_to_goal_dist_end":0.16027,"object_to_goal_dist_start":0.16033,"object_z_max":0.03434,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":286.95762,"subtask_id":"push","tcp_end":[0.67462,0.27577,0.09506],"tcp_start":[0.67442,0.27566,0.09507],"tcp_to_object_dist_end":0.26536,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.11321,"average_mean_iterations":26.54717,"average_solve_count":53.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.09744,"descend.contact_force_threshold":6.99004,"push.push_distance":0.07633,"push.push_force_threshold":9.84268,"push.push_speed":0.06888},"optimized_scores":{"best_composite_score":0.05674,"best_fitness_score":0.00341,"best_task_score":0.00069},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":912.0,"contact_point_centroid":[0.54008,0.11963,0.05977],"force_p95":499.87069,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1374.21352,"mean_force":408.09242,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.61689,0.27152,0.1701]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55442,0.11998,0.05992],"force_p95":332.8894,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.8894,"mean_force":332.8894,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.6692,0.28153,0.11318]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55455,0.12,0.05999],"force_p95":296.1985,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.1985,"mean_force":296.1985,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.66954,0.2816,0.11307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50538,0.10511,0.0094],"force_p95":0.63385,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.64147,"mean_force":0.61795,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.60639,0.26774,0.16958]},{"body_a":"peg","body_b":"link6","contact_count":42.0,"contact_point_centroid":[0.51955,0.11514,0.05629],"force_p95":8.49893,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.14476,"mean_force":1.48459,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4353,0.27361,0.15113]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50072,0.19544,0.28299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51008,0.08707,0.00939],"force_p95":0.54684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54684,"mean_force":0.54684,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.66954,0.2816,0.11307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51772,0.09119,0.00939],"force_p95":0.54265,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54265,"mean_force":0.54265,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.6692,0.28153,0.11318]}],"total_contact_groups":8},"final_pose_error":0.47546,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50559,0.10442,0.03385],"final_tcp_position":[0.66978,0.28172,0.11309],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1374.21352,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50568,0.10444,0.03385],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18463,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":326.36286,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1959.0,"raw_peak_contact_force":1374.21352,"subtask_id":"approach","tcp_end":[0.6692,0.28153,0.11318],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25376,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50564,0.10442,0.03385],"object_pos_start":[0.50568,0.10444,0.03385],"object_to_goal_dist_end":0.18461,"object_to_goal_dist_start":0.18463,"object_z_max":0.03385,"peak_contact_force":332.8894,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":332.8894,"subtask_id":"contact","tcp_end":[0.66954,0.2816,0.11307],"tcp_start":[0.6692,0.28153,0.11318],"tcp_to_object_dist_end":0.25404,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50559,0.10442,0.03385],"object_pos_start":[0.50564,0.10442,0.03385],"object_to_goal_dist_end":0.1846,"object_to_goal_dist_start":0.18461,"object_z_max":0.03385,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":296.1985,"subtask_id":"push","tcp_end":[0.66978,0.28172,0.11309],"tcp_start":[0.66954,0.2816,0.11307],"tcp_to_object_dist_end":0.25431,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```