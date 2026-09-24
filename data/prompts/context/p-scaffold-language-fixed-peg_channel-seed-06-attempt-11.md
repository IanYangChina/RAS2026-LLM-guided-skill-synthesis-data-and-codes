## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2188 | 0.94 | ✅ accepted |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3681 | 0.42 | ❌ rejected |
| 9 | approach → approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3081 | 0.00 | ❌ rejected |
| 8 | approach → approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3271 | 0.67 | ❌ rejected |
| 7 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4891 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.219) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: align_1
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach
- id: approach_1
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
    - 0.02
    - -0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
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
    push_depth:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_check
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, -0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_check, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.219
- **task_score** (E): 0.938
- **fitness_score**: 0.629  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2005 |
| approach_1 | 1.00 | 1.00 | 0.0861 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.0620 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.145, 0.108) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.145, 0.108)→(0.504, 0.109, 0.032) | (0.501, 0.099, 0.034)→(0.496, 0.049, 0.044) | 0.180→0.129 | 1.00 / 1.000 | 0.390 | 207.107 |
| push_1 | push | 0.00 / guard_failure | (0.497, -0.049, 0.034)→(0.497, -0.049, 0.034) | (0.496, 0.049, 0.044)→(0.504, -0.080, 0.033) | 0.129→0.010 | 1.00 / 3.333 | 3.747 | 46.164 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.049, 0.034)→(0.496, -0.044, 0.096) | (0.504, -0.080, 0.033)→(0.502, -0.079, 0.031) | 0.010→0.012 | 1.00 / 1.333 | 0.592 | 17.548 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.453
- phase_breakdown.push_score: 0.580
- phase_breakdown.approach_score: 0.524
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.672
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.240
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29756,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00439,"approach_1.lateral_offset_y":0.00381,"approach_1.speed":0.03417,"push_1.push_depth":-0.00019,"push_1.speed":0.04493,"retract_1.retract_height":0.10411,"retract_1.speed":0.07286},"optimized_scores":{"best_composite_score":0.24012,"best_fitness_score":0.65012,"best_task_score":0.93397},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.50689,0.06513,0.00873],"force_p95":166.2044,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":173.99278,"mean_force":49.76576,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49875,0.09576,0.06709]},{"body_a":"attachment","body_b":"peg","contact_count":146.0,"contact_point_centroid":[0.50994,0.08063,0.05375],"force_p95":169.95203,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.52437,"mean_force":123.04582,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50063,0.08766,0.05287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50678,-0.10057,0.06045],"force_p95":40.26323,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.61081,"mean_force":14.21473,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49598,-0.05339,0.034]},{"body_a":"attachment","body_b":"peg","contact_count":115.0,"contact_point_centroid":[0.50054,-0.03698,0.04068],"force_p95":21.96663,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.75568,"mean_force":4.04673,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49559,-0.02576,0.03264]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.5048,-0.03356,0.00959],"force_p95":7.12928,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.28315,"mean_force":1.68705,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49527,0.02604,0.03065]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":85.0,"contact_point_centroid":[0.52524,-0.05621,0.03092],"force_p95":9.81265,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.17812,"mean_force":1.98046,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49562,-0.02731,0.03273]},{"body_a":"peg","body_b":"channel_base_body","contact_count":70.0,"contact_point_centroid":[0.50574,-0.10041,0.01767],"force_p95":0.77439,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.40918,"mean_force":0.66,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49425,-0.05159,0.05668]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50244,-0.0665,0.06045],"force_p95":8.00524,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.07505,"mean_force":1.54824,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49542,-0.05497,0.03431]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.50811,-0.07603,0.00977],"force_p95":0.80803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.08283,"mean_force":0.60598,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49425,-0.05139,0.05821]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.5251,-0.08358,0.05975],"force_p95":4.35226,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.03172,"mean_force":1.22426,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49573,-0.05504,0.03395]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50304,0.06739,0.00932],"force_p95":0.61054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56899,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.15735,0.20055]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.05177,0.0574],"force_p95":1.69671,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69671,"mean_force":1.69671,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50427,0.08402,0.04867]}],"total_contact_groups":12},"final_pose_error":0.04923,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50584,-0.08197,0.0345],"final_tcp_position":[0.49457,-0.05022,0.08911],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":173.99278,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54683,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49999,0.1165,0.10729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.50483,-0.00159,0.03776],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.07859,"object_to_goal_dist_start":0.14764,"object_z_max":0.04275,"peak_contact_force":0.326,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":512.0,"raw_peak_contact_force":173.99278,"tcp_end":[0.49747,0.07696,0.03182],"tcp_start":[0.49999,0.1165,0.10729],"tcp_to_object_dist_end":0.07912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.5064,-0.08292,0.03597],"object_pos_start":[0.50483,-0.00159,0.03776],"object_to_goal_dist_end":0.00811,"object_to_goal_dist_start":0.07859,"object_z_max":0.04047,"peak_contact_force":7.42742,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":453.0,"raw_peak_contact_force":40.61081,"subtask_id":"push","tcp_end":[0.49593,-0.05487,0.03398],"tcp_start":[0.49596,-0.0547,0.03402],"tcp_to_object_dist_end":0.03001,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":70.0,"n_steps_budget":900.0,"object_pos_end":[0.50584,-0.08197,0.0345],"object_pos_start":[0.50632,-0.08337,0.03569],"object_to_goal_dist_end":0.00826,"object_to_goal_dist_start":0.00836,"object_z_max":0.03569,"peak_contact_force":0.4528,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":152.0,"raw_peak_contact_force":15.40918,"tcp_end":[0.49457,-0.05022,0.08911],"tcp_start":[0.49593,-0.05487,0.03398],"tcp_to_object_dist_end":0.06416,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13596,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00246,"approach_1.lateral_offset_y":0.00416,"approach_1.speed":0.03739,"push_1.push_depth":-0.0167,"push_1.speed":0.04485,"retract_1.retract_height":0.0951,"retract_1.speed":0.04797},"optimized_scores":{"best_composite_score":0.26178,"best_fitness_score":0.67178,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":366.0,"contact_point_centroid":[0.51808,0.12175,0.05227],"force_p95":209.20873,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":215.46196,"mean_force":162.21695,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50933,0.12903,0.05022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":544.0,"contact_point_centroid":[0.51339,0.1161,0.00832],"force_p95":209.45563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.34674,"mean_force":109.18144,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50708,0.13445,0.06119]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":99.0,"contact_point_centroid":[0.52504,0.11997,0.06],"force_p95":97.83001,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.31026,"mean_force":83.16551,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51437,0.12737,0.04735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50489,-0.1004,0.06038],"force_p95":39.31748,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.71708,"mean_force":25.2752,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49736,-0.05321,0.03371]},{"body_a":"attachment","body_b":"peg","contact_count":213.0,"contact_point_centroid":[0.50023,-0.00105,0.04218],"force_p95":5.1614,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.4744,"mean_force":2.08293,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49866,0.01056,0.03122]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":169.0,"contact_point_centroid":[0.52522,0.10904,0.0554],"force_p95":19.42452,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.14872,"mean_force":8.03079,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51205,0.12749,0.04865]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47455,-0.00859,0.04516],"force_p95":19.96434,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.29698,"mean_force":2.67428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49973,0.038,0.03085]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.50509,-0.10038,0.03441],"force_p95":12.43346,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.45775,"mean_force":1.74623,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49576,-0.0518,0.04322]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50201,-0.06589,0.05561],"force_p95":12.6172,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.75189,"mean_force":9.3271,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49707,-0.05386,0.03357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50125,-0.0035,0.00955],"force_p95":4.1192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.13138,"mean_force":1.49768,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49962,0.04545,0.03019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":64.0,"contact_point_centroid":[0.50371,-0.0807,0.00978],"force_p95":4.66315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.80953,"mean_force":0.98023,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49569,-0.05099,0.05131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50351,0.11176,0.00934],"force_p95":0.6343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56822,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.17712,0.19971]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.4731,0.07932,0.04537],"force_p95":1.57451,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05456,"mean_force":0.57086,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50752,0.12357,0.03627]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.5253,-0.05197,0.02229],"force_p95":1.03505,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27596,"mean_force":0.52393,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49848,-0.01473,0.0327]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19934,0.29835]}],"total_contact_groups":15},"final_pose_error":0.04935,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50553,-0.08186,0.03416],"final_tcp_position":[0.49579,-0.04954,0.07961],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":215.46196,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50616,0.15629,0.10861],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.49185,0.06472,0.04813],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.14518,"object_to_goal_dist_start":0.1919,"object_z_max":0.04951,"peak_contact_force":0.64865,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1211.0,"raw_peak_contact_force":215.46196,"tcp_end":[0.50438,0.12118,0.03142],"tcp_start":[0.50616,0.15629,0.10861],"tcp_to_object_dist_end":0.06019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,-0.08181,0.03617],"object_pos_start":[0.49185,0.06472,0.04813],"object_to_goal_dist_end":0.00741,"object_to_goal_dist_start":0.14518,"object_z_max":0.04813,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":567.0,"raw_peak_contact_force":39.71708,"subtask_id":"push","tcp_end":[0.4973,-0.05366,0.03366],"tcp_start":[0.49734,-0.05349,0.0337],"tcp_to_object_dist_end":0.02959,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.50553,-0.08186,0.03416],"object_pos_start":[0.50582,-0.08241,0.03597],"object_to_goal_dist_end":0.00825,"object_to_goal_dist_start":0.00748,"object_z_max":0.03597,"peak_contact_force":0.55838,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":116.0,"raw_peak_contact_force":14.45775,"tcp_end":[0.49579,-0.04954,0.07961],"tcp_start":[0.4973,-0.05366,0.03366],"tcp_to_object_dist_end":0.05662,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24696,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00587,"approach_1.lateral_offset_y":0.00412,"approach_1.speed":0.03294,"push_1.push_depth":0.0011,"push_1.speed":0.03099,"retract_1.retract_height":0.13367,"retract_1.speed":0.086},"optimized_scores":{"best_composite_score":0.15454,"best_fitness_score":0.56454,"best_task_score":0.88058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":646.0,"contact_point_centroid":[0.50719,0.11909,0.0077],"force_p95":222.33498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":231.86547,"mean_force":111.4888,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50003,0.14156,0.05898]},{"body_a":"attachment","body_b":"peg","contact_count":442.0,"contact_point_centroid":[0.51151,0.12752,0.05009],"force_p95":223.24979,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":231.33158,"mean_force":161.53372,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50568,0.13694,0.04788]},{"body_a":"attachment","body_b":"peg","contact_count":192.0,"contact_point_centroid":[0.50233,0.01587,0.04237],"force_p95":18.28565,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.16266,"mean_force":3.72552,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50233,0.02779,0.03164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50211,-0.10027,0.04463],"force_p95":36.19441,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.65956,"mean_force":9.98002,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49874,-0.03816,0.03402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.49651,0.00202,0.00944],"force_p95":10.93845,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.23876,"mean_force":2.28958,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50341,0.045,0.03125]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":76.0,"contact_point_centroid":[0.5255,0.11912,0.04894],"force_p95":22.20175,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.53571,"mean_force":14.23512,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52046,0.13567,0.04609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.49285,-0.10016,0.04274],"force_p95":19.52552,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.77686,"mean_force":5.23247,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49718,-0.03801,0.03851]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.49872,-0.05063,0.04486],"force_p95":18.73183,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.93239,"mean_force":5.70235,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49773,-0.03901,0.03524]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":69.0,"contact_point_centroid":[0.47465,0.00317,0.03478],"force_p95":12.45209,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.6108,"mean_force":3.41589,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50439,0.05654,0.0313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":94.0,"contact_point_centroid":[0.49609,-0.07966,0.00881],"force_p95":6.94199,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81889,"mean_force":1.20232,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49708,-0.03315,0.07322]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47497,-0.04835,0.02452],"force_p95":8.29595,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.37147,"mean_force":3.17146,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49753,-0.03108,0.10464]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.5255,0.05123,0.0548],"force_p95":1.28075,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92516,"mean_force":0.4618,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50745,0.1109,0.0296]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":18.0,"contact_point_centroid":[0.47315,0.08804,0.04702],"force_p95":2.28885,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73756,"mean_force":0.87792,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51414,0.13048,0.03554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49639,0.11903,0.00939],"force_p95":0.63431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56429,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49175,0.1803,0.19941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.19904,0.2964]}],"total_contact_groups":15},"final_pose_error":0.04986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4937,-0.07244,0.02485],"final_tcp_position":[0.49773,-0.03245,0.11831],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":231.86547,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57183,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48515,0.16278,0.10959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.49009,0.08363,0.0466],"object_pos_start":[0.49602,0.11913,0.03403],"object_to_goal_dist_end":0.16407,"object_to_goal_dist_start":0.19926,"object_z_max":0.04729,"peak_contact_force":0.19413,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1182.0,"raw_peak_contact_force":231.86547,"tcp_end":[0.51114,0.12897,0.03245],"tcp_start":[0.48515,0.16278,0.10959],"tcp_to_object_dist_end":0.05195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.49964,-0.07532,0.02721],"object_pos_start":[0.49009,0.08363,0.0466],"object_to_goal_dist_end":0.01362,"object_to_goal_dist_start":0.16407,"object_z_max":0.0466,"peak_contact_force":3.81381,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":594.0,"raw_peak_contact_force":58.16266,"subtask_id":"push","tcp_end":[0.49865,-0.03933,0.03401],"tcp_start":[0.49868,-0.03916,0.03404],"tcp_to_object_dist_end":0.03664,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":100.0,"n_steps_budget":990.0,"object_pos_end":[0.4937,-0.07244,0.02485],"object_pos_start":[0.49971,-0.07541,0.02715],"object_to_goal_dist_end":0.01806,"object_to_goal_dist_start":0.01365,"object_z_max":0.02891,"peak_contact_force":0.76535,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":138.0,"raw_peak_contact_force":22.77686,"tcp_end":[0.49773,-0.03245,0.11831],"tcp_start":[0.49865,-0.03933,0.03401],"tcp_to_object_dist_end":0.10173,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```