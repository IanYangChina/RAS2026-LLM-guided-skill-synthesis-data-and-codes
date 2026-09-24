## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.7130 | 0.83 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 1 | 0.4142 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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

## Current Skill (Q=0.713) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.06
    - 0.05
    tolerance: 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
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
  subtask_id: contact
- id: push_1
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
      distance: 0.2
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_stroke:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.05], tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.713
- **task_score** (E): 0.826
- **fitness_score**: 0.706  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1729 |
| contact_1 | 0.67 | 1.00 | 0.1083 |
| push_1 | 1.00 | 1.00 | 0.1927 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.153, 0.136) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.553 | 3.526 |
| contact_1 | contact | 0.67 / force_exceeded | (0.513, 0.153, 0.136)→(0.500, 0.105, 0.041) | (0.503, 0.080, 0.034)→(0.504, 0.076, 0.035) | 0.160→0.156 | 1.00 / 1.667 | 9.770 | 14.172 |
| push_1 | push | 1.00 / step_budget | (0.500, 0.105, 0.041)→(0.501, -0.087, 0.032) | (0.504, 0.076, 0.035)→(0.511, -0.129, 0.026) | 0.156→0.061 | 1.00 / 3.333 | 228.061 | 497.470 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.087, 0.032)→(0.498, -0.087, 0.112) | (0.511, -0.129, 0.026)→(0.524, -0.154, 0.018) | 0.061→0.088 | 1.00 / 1.000 | 0.660 | 117.430 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.875
- phase_score: 0.666
- phase_breakdown.contact_score: 0.873
- phase_breakdown.approach_score: 0.129
- phase_breakdown.push_score: 0.776

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.765
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.695
- **K-run variance**: 0.0094
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97931,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.33114,"push_1.push_stroke":0.24382},"optimized_scores":{"best_composite_score":0.83977,"best_fitness_score":0.74977,"best_task_score":0.87508},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":211.0,"contact_point_centroid":[0.52586,-0.10001,0.06493],"force_p95":364.06214,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":432.67211,"mean_force":237.17629,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49253,-0.08397,0.03123]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":106.0,"contact_point_centroid":[0.50079,-0.10004,0.06274],"force_p95":254.81657,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.38596,"mean_force":205.02809,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49371,-0.08793,0.03198]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":871.0,"contact_point_centroid":[0.52831,-0.02321,0.026],"force_p95":195.91589,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":214.97602,"mean_force":86.44138,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48954,-0.01648,0.0317]},{"body_a":"attachment","body_b":"peg","contact_count":899.0,"contact_point_centroid":[0.4992,-0.01451,0.03287],"force_p95":178.55225,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":192.44248,"mean_force":89.0629,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48958,-0.01125,0.03192]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":79.0,"contact_point_centroid":[0.52798,-0.09088,0.02981],"force_p95":82.3806,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":121.24188,"mean_force":36.17994,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48939,-0.08671,0.04223]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":87.0,"contact_point_centroid":[0.47499,-0.01709,0.03253],"force_p95":106.94335,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.55441,"mean_force":80.91169,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48667,-0.0171,0.02982]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50125,-0.10001,0.065],"force_p95":91.9891,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.9891,"mean_force":91.9891,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4933,-0.08769,0.03249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.51192,-0.01819,0.00968],"force_p95":64.08677,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.42393,"mean_force":37.42871,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48938,-0.00284,0.03216]},{"body_a":"attachment","body_b":"peg","contact_count":65.0,"contact_point_centroid":[0.50016,-0.08699,0.03779],"force_p95":82.35123,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.62588,"mean_force":41.88252,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4896,-0.08676,0.04016]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5298,-0.10001,0.06493],"force_p95":79.94458,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.08407,"mean_force":72.01229,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49333,-0.08765,0.03251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":213.0,"contact_point_centroid":[0.49916,-0.06973,0.00867],"force_p95":9.03725,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.75729,"mean_force":2.1398,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4896,-0.08695,0.0764]},{"body_a":"peg","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.50961,-0.02965,0.06925],"force_p95":4.31404,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.01674,"mean_force":3.38633,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48705,-0.00018,0.03106]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.51563,-0.10025,0.02577],"force_p95":18.52767,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.89321,"mean_force":6.46129,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49008,-0.07701,0.02955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.49656,0.11628,0.00949],"force_p95":0.79739,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.53588,"mean_force":0.84102,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4893,0.16226,0.08668]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.49424,0.13376,0.05035],"force_p95":10.40344,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.53318,"mean_force":4.97281,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49137,0.1455,0.04677]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":39.0,"contact_point_centroid":[0.4749,-0.07771,0.02471],"force_p95":9.66191,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.26246,"mean_force":3.78542,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48996,-0.08711,0.09425]}],"total_contact_groups":18},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49383,-0.07415,0.0248],"final_tcp_position":[0.49023,-0.08719,0.11292],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":432.67211,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11908,0.03394],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19921,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51947,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":148.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48993,0.18311,0.13944],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":536.0,"n_steps_budget":720.0,"object_pos_end":[0.49872,0.11382,0.0354],"object_pos_start":[0.49606,0.11908,0.03394],"object_to_goal_dist_end":0.19388,"object_to_goal_dist_start":0.19921,"object_z_max":0.03612,"peak_contact_force":14.53588,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":562.0,"raw_peak_contact_force":14.53588,"subtask_id":"contact","tcp_end":[0.49173,0.14283,0.04021],"tcp_start":[0.48993,0.18311,0.13944],"tcp_to_object_dist_end":0.03022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.51774,-0.0725,0.02724],"object_pos_start":[0.49872,0.11382,0.0354],"object_to_goal_dist_end":0.0231,"object_to_goal_dist_start":0.19388,"object_z_max":0.04074,"peak_contact_force":322.28247,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2981.0,"raw_peak_contact_force":432.67211,"subtask_id":"push","tcp_end":[0.4933,-0.08769,0.03249],"tcp_start":[0.49173,0.14283,0.04021],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":254.0,"n_steps_budget":630.0,"object_pos_end":[0.49383,-0.07415,0.0248],"object_pos_start":[0.51774,-0.0725,0.02724],"object_to_goal_dist_end":0.01742,"object_to_goal_dist_start":0.0231,"object_z_max":0.02984,"peak_contact_force":0.63647,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":400.0,"raw_peak_contact_force":121.24188,"tcp_end":[0.49023,-0.08719,0.11292],"tcp_start":[0.4933,-0.08769,0.03249],"tcp_to_object_dist_end":0.08915,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97842,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":15.07478,"push_1.push_stroke":0.18715},"optimized_scores":{"best_composite_score":0.60457,"best_fitness_score":0.76457,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.51322,-0.10022,0.065],"force_p95":742.93697,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":842.69232,"mean_force":322.57656,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.506,-0.08814,0.0317]},{"body_a":"channel_base_body","body_b":"link7","contact_count":130.0,"contact_point_centroid":[0.54109,-0.1,0.06496],"force_p95":654.55391,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":766.2557,"mean_force":251.24403,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50575,-0.08727,0.03156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.50351,-0.10947,0.03665],"force_p95":204.55498,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":233.00953,"mean_force":83.23051,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50358,-0.07336,0.03054]},{"body_a":"attachment","body_b":"peg","contact_count":400.0,"contact_point_centroid":[0.50499,-0.02815,0.04255],"force_p95":191.99322,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":207.01466,"mean_force":42.93286,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50194,-0.01673,0.03109]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51347,-0.10004,0.065],"force_p95":158.34191,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.81617,"mean_force":91.07352,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50615,-0.08755,0.03184]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54214,-0.1,0.06496],"force_p95":148.53433,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.40535,"mean_force":86.54346,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50614,-0.0875,0.03188]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":67.0,"contact_point_centroid":[0.47456,-0.10448,0.05691],"force_p95":74.25516,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.17098,"mean_force":38.03205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50415,-0.07774,0.0307]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":277.0,"contact_point_centroid":[0.52519,-0.02717,0.02893],"force_p95":56.19388,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.31315,"mean_force":15.44411,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5018,0.00178,0.03149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.50312,-0.03615,0.00981],"force_p95":24.06531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.20433,"mean_force":7.22565,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50155,0.00551,0.03151]},{"body_a":"peg","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.50675,-0.10571,0.06985],"force_p95":37.4487,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.13518,"mean_force":30.75016,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50227,-0.07631,0.02962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":511.0,"contact_point_centroid":[0.50569,0.0611,0.00942],"force_p95":0.67199,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.72468,"mean_force":0.86477,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51102,0.11246,0.08193]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50601,0.07845,0.0488],"force_p95":13.11015,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.41964,"mean_force":6.65545,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50439,0.09033,0.04283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":136.0,"contact_point_centroid":[0.50488,0.06281,0.00928],"force_p95":0.98618,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.64602,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51276,0.16669,0.20736]},{"body_a":"peg","body_b":"world","contact_count":96.0,"contact_point_centroid":[0.51406,-0.17612,-0.00165],"force_p95":2.31907,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.35351,"mean_force":0.75828,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50605,-0.08791,0.03173]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50177,0.19675,0.28998]},{"body_a":"peg","body_b":"world","contact_count":246.0,"contact_point_centroid":[0.52142,-0.18214,-0.00196],"force_p95":0.7179,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81546,"mean_force":0.60463,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50341,-0.08708,0.07128]}],"total_contact_groups":17},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52577,-0.18088,0.01411],"final_tcp_position":[0.50305,-0.0871,0.1122],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":842.69232,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54659,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":170.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52224,0.14046,0.13528],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":517.0,"n_steps_budget":750.0,"object_pos_end":[0.50698,0.05633,0.03502],"object_pos_start":[0.50595,0.06302,0.0338],"object_to_goal_dist_end":0.1366,"object_to_goal_dist_start":0.14328,"object_z_max":0.03522,"peak_contact_force":0.51711,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":565.0,"raw_peak_contact_force":13.72468,"subtask_id":"contact","tcp_end":[0.50321,0.08651,0.03598],"tcp_start":[0.52224,0.14046,0.13528],"tcp_to_object_dist_end":0.03042,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.5176,-0.1832,0.01385],"object_pos_start":[0.50698,0.05633,0.03502],"object_to_goal_dist_end":0.10791,"object_to_goal_dist_start":0.1366,"object_z_max":0.04016,"peak_contact_force":242.68237,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1446.0,"raw_peak_contact_force":842.69232,"subtask_id":"push","tcp_end":[0.50615,-0.08758,0.03185],"tcp_start":[0.50321,0.08651,0.03598],"tcp_to_object_dist_end":0.09798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":246.0,"n_steps_budget":660.0,"object_pos_end":[0.52577,-0.18088,0.01411],"object_pos_start":[0.5176,-0.1832,0.01385],"object_to_goal_dist_end":0.10729,"object_to_goal_dist_start":0.10791,"object_z_max":0.01426,"peak_contact_force":0.71783,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":252.0,"raw_peak_contact_force":165.81617,"tcp_end":[0.50305,-0.0871,0.1122],"tcp_start":[0.50615,-0.08758,0.03185],"tcp_to_object_dist_end":0.1376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9771,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.69604,"push_1.push_stroke":0.16225},"optimized_scores":{"best_composite_score":0.69468,"best_fitness_score":0.60468,"best_task_score":0.60382},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.53493,-0.10001,0.06495],"force_p95":207.07594,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.04572,"mean_force":128.70775,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50361,-0.081,0.03058]},{"body_a":"attachment","body_b":"peg","contact_count":550.0,"contact_point_centroid":[0.50598,-0.01563,0.0387],"force_p95":102.60684,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":158.61717,"mean_force":57.16725,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50455,-0.00444,0.03746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.50462,-0.1048,0.04449],"force_p95":86.47608,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.85862,"mean_force":54.39548,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50401,-0.05775,0.03246]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.50618,-0.02882,0.00972],"force_p95":70.53561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.34282,"mean_force":45.85204,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50488,0.00646,0.0387]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53986,-0.1,0.06499],"force_p95":65.12048,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.23099,"mean_force":64.12587,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50484,-0.0862,0.03138]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.52503,-0.05592,0.05198],"force_p95":19.25047,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.41787,"mean_force":10.33298,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50471,-0.01778,0.03667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.50607,0.05662,0.00937],"force_p95":0.60094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.25585,"mean_force":0.58112,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51505,0.10988,0.08676]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50614,0.07453,0.04685],"force_p95":13.24537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.82836,"mean_force":7.99847,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50613,0.0865,0.04682]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.4749,-0.11509,0.05911],"force_p95":5.23175,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.04099,"mean_force":1.58615,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50388,-0.08182,0.03081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":138.0,"contact_point_centroid":[0.50515,0.05652,0.00929],"force_p95":1.04272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.66196,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5158,0.16376,0.20654]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50231,0.19598,0.28861]},{"body_a":"peg","body_b":"world","contact_count":219.0,"contact_point_centroid":[0.52392,-0.18716,-0.00148],"force_p95":1.45489,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.58737,"mean_force":0.65213,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5019,-0.08578,0.07419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50249,-0.11816,0.01255],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50458,-0.08636,0.03183]}],"total_contact_groups":13},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.55157,-0.20654,0.01397],"final_tcp_position":[0.50173,-0.08569,0.11176],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":217.04572,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05665,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.59388,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":175.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.5276,0.13546,0.13457],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":445.0,"n_steps_budget":750.0,"object_pos_end":[0.50613,0.05647,0.03377],"object_pos_start":[0.50611,0.05665,0.03377],"object_to_goal_dist_end":0.13675,"object_to_goal_dist_start":0.13693,"object_z_max":0.03378,"peak_contact_force":14.25585,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":447.0,"raw_peak_contact_force":14.25585,"subtask_id":"contact","tcp_end":[0.50607,0.08635,0.04654],"tcp_start":[0.5276,0.13546,0.13457],"tcp_to_object_dist_end":0.03249,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.49887,-0.13188,0.03725],"object_pos_start":[0.50613,0.05647,0.03377],"object_to_goal_dist_end":0.05196,"object_to_goal_dist_start":0.13675,"object_z_max":0.04026,"peak_contact_force":119.21904,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1347.0,"raw_peak_contact_force":217.04572,"subtask_id":"push","tcp_end":[0.50482,-0.08615,0.03137],"tcp_start":[0.50607,0.08635,0.04654],"tcp_to_object_dist_end":0.04649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.55157,-0.20654,0.01397],"object_pos_start":[0.49887,-0.13188,0.03725],"object_to_goal_dist_end":0.1391,"object_to_goal_dist_start":0.05196,"object_z_max":0.03725,"peak_contact_force":0.62636,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":230.0,"raw_peak_contact_force":65.23099,"tcp_end":[0.50173,-0.08569,0.11176],"tcp_start":[0.50482,-0.08615,0.03137],"tcp_to_object_dist_end":0.16325,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```