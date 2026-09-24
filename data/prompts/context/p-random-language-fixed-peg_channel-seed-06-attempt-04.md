## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2134 | 0.67 | ✅ accepted |
| 3 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.0042 | 0.01 | ✅ accepted |
| 2 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0795 | 0.00 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0828 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.213) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_pre
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
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
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
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.04
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.087
  parameters:
    max_push_time:
      type: scalar
      range:
      - 1.0
      - 4.0
      default: 2.5
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.04
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.087
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.213
- **task_score** (E): 0.668
- **fitness_score**: 0.493  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre | 1.00 | 1.00 | 0.2108 |
| descend_contact | 1.00 | 1.00 | 0.0603 |
| push_channel | 1.00 | 1.00 | 0.1228 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.142, 0.099) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.561 | 2.127 |
| descend_contact | descend | 1.00 / step_budget | (0.497, 0.142, 0.099)→(0.497, 0.123, 0.042) | (0.501, 0.099, 0.034)→(0.503, 0.094, 0.036) | 0.180→0.174 | 1.00 / 1.333 | 5.736 | 31.517 |
| push_channel | push | 1.00 / time_limit | (0.497, 0.123, 0.042)→(0.497, 0.001, 0.033) | (0.503, 0.094, 0.036)→(0.507, -0.027, 0.036) | 0.174→0.054 | 1.00 / 1.667 | 1.082 | 21.787 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.847
- alignment_error: None
- force_efficiency: 0.422
- terminal_score: 0.847
- phase_score: 0.500
- phase_breakdown.push_score: 0.435
- phase_breakdown.contact_score: 0.882
- phase_breakdown.approach_score: 0.313

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.639
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.850
- **Median Q (composite search score)**: 0.260
- **K-run variance**: 0.0201
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90426,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.05546,"descend_contact.descend_speed":0.0208,"push_channel.max_push_time":2.21554,"push_channel.push_distance":0.16204,"push_channel.push_speed":0.07984},"optimized_scores":{"best_composite_score":0.35878,"best_fitness_score":0.63878,"best_task_score":0.84717},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":772.0,"contact_point_centroid":[0.50202,0.01345,0.04277],"force_p95":18.68488,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.9142,"mean_force":4.63756,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49743,0.02487,0.03536]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":746.0,"contact_point_centroid":[0.52513,0.00422,0.02862],"force_p95":14.78996,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.56739,"mean_force":2.36779,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49718,0.0323,0.03555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.50354,0.0638,0.00943],"force_p95":3.20383,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.98553,"mean_force":1.06446,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49806,0.10267,0.07077]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50097,0.08181,0.04831],"force_p95":15.76612,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.81449,"mean_force":6.00095,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49849,0.09355,0.04635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":616.0,"contact_point_centroid":[0.50651,-0.01418,0.00992],"force_p95":11.11922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.54492,"mean_force":4.85592,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49727,0.03048,0.03551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":726.0,"contact_point_centroid":[0.50307,0.06743,0.00935],"force_p95":0.55473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5585,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49888,0.15532,0.19601]}],"total_contact_groups":6},"final_pose_error":0.06093,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50704,-0.06809,0.03561],"final_tcp_position":[0.49989,-0.0388,0.03381],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":28.9142,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54722,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":726.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49955,0.11225,0.09777],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.50576,0.06266,0.0367],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14281,"object_to_goal_dist_start":0.14761,"object_z_max":0.03706,"peak_contact_force":0.14812,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":238.0,"raw_peak_contact_force":15.98553,"subtask_id":"contact","tcp_end":[0.49872,0.09173,0.04149],"tcp_start":[0.49955,0.11225,0.09777],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50704,-0.06809,0.03561],"object_pos_start":[0.50576,0.06266,0.0367],"object_to_goal_dist_end":0.01452,"object_to_goal_dist_start":0.14281,"object_z_max":0.0367,"peak_contact_force":0.34281,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2134.0,"raw_peak_contact_force":28.9142,"subtask_id":"push","tcp_end":[0.49989,-0.0388,0.03381],"tcp_start":[0.49872,0.09173,0.04149],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19444,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.03904,"descend_contact.descend_speed":0.04438,"push_channel.max_push_time":3.49673,"push_channel.push_distance":0.12628,"push_channel.push_speed":0.07983},"optimized_scores":{"best_composite_score":0.26003,"best_fitness_score":0.54003,"best_task_score":0.85039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":201.0,"contact_point_centroid":[0.50428,0.10677,0.00946],"force_p95":16.613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.64796,"mean_force":2.58952,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50251,0.14493,0.07055]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50253,0.12644,0.05005],"force_p95":50.01778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.31273,"mean_force":18.26678,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50102,0.13821,0.05013]},{"body_a":"attachment","body_b":"peg","contact_count":760.0,"contact_point_centroid":[0.50255,0.05535,0.04268],"force_p95":8.69506,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.4368,"mean_force":3.35724,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49842,0.06691,0.03541]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.50645,0.02654,0.00994],"force_p95":8.31851,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.75027,"mean_force":4.29601,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49835,0.07205,0.0356]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":711.0,"contact_point_centroid":[0.52512,0.04438,0.02749],"force_p95":4.02555,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.53449,"mean_force":1.28685,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49825,0.07273,0.03552]},{"body_a":"peg","body_b":"channel_base_body","contact_count":668.0,"contact_point_centroid":[0.50363,0.11162,0.00939],"force_p95":0.61119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55538,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.50219,0.1762,0.19606]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49972,0.19945,0.29915]}],"total_contact_groups":7},"final_pose_error":0.02505,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5069,-0.02429,0.03551],"final_tcp_position":[0.49974,0.00494,0.0332],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":60.64796,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":690.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11176,0.03377],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55681,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":684.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50605,0.15395,0.09874],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":201.0,"n_steps_budget":960.0,"object_pos_end":[0.50391,0.10675,0.03664],"object_pos_start":[0.50368,0.11176,0.03377],"object_to_goal_dist_end":0.18682,"object_to_goal_dist_start":0.19189,"object_z_max":0.03672,"peak_contact_force":16.22288,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":224.0,"raw_peak_contact_force":60.64796,"subtask_id":"contact","tcp_end":[0.50069,0.13576,0.0424],"tcp_start":[0.50605,0.15395,0.09874],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,-0.02429,0.03551],"object_pos_start":[0.50391,0.10675,0.03664],"object_to_goal_dist_end":0.05632,"object_to_goal_dist_start":0.18682,"object_z_max":0.03664,"peak_contact_force":2.16064,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2070.0,"raw_peak_contact_force":24.4368,"subtask_id":"push","tcp_end":[0.49974,0.00494,0.0332],"tcp_start":[0.50069,0.13576,0.0424],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.03632,"descend_contact.descend_speed":0.03292,"push_channel.max_push_time":2.84625,"push_channel.push_distance":0.14521,"push_channel.push_speed":0.06518},"optimized_scores":{"best_composite_score":0.02139,"best_fitness_score":0.30139,"best_task_score":0.30644},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":219.0,"contact_point_centroid":[0.49668,0.11412,0.00953],"force_p95":10.0174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.91754,"mean_force":1.46758,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48577,0.15188,0.07124]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.4926,0.13276,0.05158],"force_p95":17.49765,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.5741,"mean_force":7.23807,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48922,0.14427,0.04742]},{"body_a":"attachment","body_b":"peg","contact_count":744.0,"contact_point_centroid":[0.49624,0.07408,0.04091],"force_p95":8.77467,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.0104,"mean_force":3.7484,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48954,0.08442,0.03476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":704.0,"contact_point_centroid":[0.50526,0.05055,0.00988],"force_p95":7.72503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.3981,"mean_force":3.53893,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48922,0.09196,0.03507]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":526.0,"contact_point_centroid":[0.52515,0.04332,0.03077],"force_p95":5.47724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.44689,"mean_force":2.48317,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49038,0.06776,0.03421]},{"body_a":"peg","body_b":"channel_base_body","contact_count":648.0,"contact_point_centroid":[0.49623,0.11908,0.00944],"force_p95":0.61206,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55126,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49097,0.17956,0.19606]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49948,0.19928,0.29808]}],"total_contact_groups":7},"final_pose_error":0.06891,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50714,0.00996,0.03627],"final_tcp_position":[0.49202,0.03626,0.03305],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":17.91754,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11911,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5801,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":672.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48393,0.16073,0.09954],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.49923,0.11295,0.03473],"object_pos_start":[0.49602,0.11911,0.03393],"object_to_goal_dist_end":0.19303,"object_to_goal_dist_start":0.19924,"object_z_max":0.03662,"peak_contact_force":0.8372,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":248.0,"raw_peak_contact_force":17.91754,"subtask_id":"contact","tcp_end":[0.4903,0.14235,0.04128],"tcp_start":[0.48393,0.16073,0.09954],"tcp_to_object_dist_end":0.03141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50714,0.00996,0.03627],"object_pos_start":[0.49923,0.11295,0.03473],"object_to_goal_dist_end":0.09032,"object_to_goal_dist_start":0.19303,"object_z_max":0.0373,"peak_contact_force":0.7424,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1974.0,"raw_peak_contact_force":12.0104,"subtask_id":"push","tcp_end":[0.49202,0.03626,0.03305],"tcp_start":[0.4903,0.14235,0.04128],"tcp_to_object_dist_end":0.03051,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```