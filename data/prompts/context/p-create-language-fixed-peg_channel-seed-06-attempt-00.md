## Search State

- **Seed**: 6
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3693 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.369) — your mutation base

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
    entity: peg
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: channel_axis
      mode: add_to_offset
      sign: positive
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
    probe_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - probe_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.369
- **task_score** (E): 0.234
- **fitness_score**: 0.266  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2487 |
| contact_1 | 1.00 | 1.00 | 0.0141 |
| push_1 | 0.00 | 1.00 | 0.0445 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.143, 0.059) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.551 | 2.127 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.143, 0.059)→(0.494, 0.131, 0.055) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 11.652 | 11.652 |
| push_1 | push | 0.00 / step_budget | (0.494, 0.131, 0.055)→(0.503, 0.087, 0.053) | (0.501, 0.099, 0.034)→(0.502, 0.049, 0.027) | 0.180→0.129 | 1.00 / 2.667 | 272.228 | 475.380 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.492
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.404
- phase_score: 0.286
- phase_breakdown.push_score: 0.039
- phase_breakdown.approach_score: 0.676
- phase_breakdown.contact_score: 0.638

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.333
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.404
- **Median Q (composite search score)**: 0.376
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42647,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06549,"contact_1.contact_force":9.81084,"contact_1.probe_speed":0.04271,"push_1.push_speed":0.06141},"optimized_scores":{"best_composite_score":0.29517,"best_fitness_score":0.19184,"best_task_score":0.06474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":818.0,"contact_point_centroid":[0.46807,0.11991,0.05853],"force_p95":343.54293,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":555.10752,"mean_force":253.50723,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50181,0.08309,0.05267]},{"body_a":"world","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.49741,0.14943,-1e-05],"force_p95":234.21818,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":414.11256,"mean_force":124.10247,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50135,0.0865,0.05296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50233,0.0584,0.00941],"force_p95":0.57759,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.30158,"mean_force":0.64277,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50126,0.08495,0.05286]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50269,0.08432,0.05574],"force_p95":33.39651,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.99503,"mean_force":4.89177,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49945,0.08407,0.05349]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49885,0.16926,-1e-05],"force_p95":18.83869,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.83869,"mean_force":18.83869,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49751,0.1074,0.05447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.5031,0.06744,0.00934],"force_p95":0.55564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5627,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49543,0.16577,0.17901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.50219,0.06759,0.00938],"force_p95":0.55063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54668,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49826,0.11044,0.05554]}],"total_contact_groups":7},"final_pose_error":0.16661,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50266,0.0571,0.0341],"final_tcp_position":[0.50376,0.08609,0.05264],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":555.10752,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54693,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.50007,0.11427,0.05849],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":58.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":18.83869,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":59.0,"raw_peak_contact_force":18.83869,"tcp_end":[0.4975,0.10731,0.05446],"tcp_start":[0.50007,0.11427,0.05849],"tcp_to_object_dist_end":0.04519,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50266,0.0571,0.0341],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.13726,"object_to_goal_dist_start":0.14766,"object_z_max":0.03686,"peak_contact_force":278.14971,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2376.0,"raw_peak_contact_force":555.10752,"subtask_id":"push","tcp_end":[0.50376,0.08609,0.05264],"tcp_start":[0.4975,0.10731,0.05446],"tcp_to_object_dist_end":0.03442,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00541,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04453,"contact_1.contact_force":5.00851,"contact_1.probe_speed":0.04609,"push_1.push_speed":0.02477},"optimized_scores":{"best_composite_score":0.43664,"best_fitness_score":0.33331,"best_task_score":0.40424},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":371.0,"contact_point_centroid":[0.47445,0.11994,0.06],"force_p95":310.45421,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.99921,"mean_force":242.04272,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50585,0.08121,0.05281]},{"body_a":"world","body_b":"link7","contact_count":902.0,"contact_point_centroid":[0.50492,0.15873,-2e-05],"force_p95":179.4715,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.70439,"mean_force":126.94067,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50491,0.09581,0.05324]},{"body_a":"attachment","body_b":"peg","contact_count":540.0,"contact_point_centroid":[0.5016,0.09362,0.04204],"force_p95":37.08468,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.44143,"mean_force":5.16692,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50471,0.09345,0.05332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":979.0,"contact_point_centroid":[0.50176,0.07235,0.00982],"force_p95":7.25682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.99311,"mean_force":3.30718,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50488,0.09662,0.05327]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50498,0.20954,-1e-05],"force_p95":14.13499,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.13499,"mean_force":14.13499,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5037,0.14775,0.05457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":531.0,"contact_point_centroid":[0.50353,0.11169,0.00937],"force_p95":0.61767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55953,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4982,0.18395,0.18107]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52502,0.03997,0.05524],"force_p95":0.70323,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74618,"mean_force":0.26834,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50614,0.08158,0.05267]},{"body_a":"peg","body_b":"channel_base_body","contact_count":61.0,"contact_point_centroid":[0.50389,0.11171,0.00942],"force_p95":0.59445,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61994,"mean_force":0.54207,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50438,0.15069,0.0557]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50378,0.20566,0.29959]}],"total_contact_groups":9},"final_pose_error":0.16266,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50109,0.03309,0.02391],"final_tcp_position":[0.50637,0.08205,0.0526],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":373.99921,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11176,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52516,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":547.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50637,0.15457,0.05902],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11172,0.03388],"object_pos_start":[0.50373,0.11176,0.03381],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.1919,"object_z_max":0.03389,"peak_contact_force":14.13499,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":62.0,"raw_peak_contact_force":14.13499,"tcp_end":[0.50369,0.14769,0.05456],"tcp_start":[0.50637,0.15457,0.05902],"tcp_to_object_dist_end":0.04149,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50109,0.03309,0.02391],"object_pos_start":[0.50377,0.11172,0.03388],"object_to_goal_dist_end":0.11424,"object_to_goal_dist_start":0.19185,"object_z_max":0.04078,"peak_contact_force":235.74913,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2801.0,"raw_peak_contact_force":373.99921,"subtask_id":"push","tcp_end":[0.50637,0.08205,0.0526],"tcp_start":[0.50369,0.14769,0.05456],"tcp_to_object_dist_end":0.05699,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02726,"contact_1.contact_force":1.76359,"contact_1.probe_speed":0.03657,"push_1.push_speed":0.09375},"optimized_scores":{"best_composite_score":0.37616,"best_fitness_score":0.27283,"best_task_score":0.23422},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":668.0,"contact_point_centroid":[0.47286,0.1199,0.05457],"force_p95":272.08559,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.03445,"mean_force":227.05857,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48462,0.12127,0.05305]},{"body_a":"world","body_b":"link7","contact_count":658.0,"contact_point_centroid":[0.47912,0.17886,-4e-05],"force_p95":319.20102,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.5662,"mean_force":201.8228,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48775,0.11638,0.05289]},{"body_a":"attachment","body_b":"peg","contact_count":724.0,"contact_point_centroid":[0.49192,0.12253,0.04384],"force_p95":3.59836,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.82198,"mean_force":1.23273,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48466,0.12151,0.05312]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.49907,0.091,0.00978],"force_p95":3.43235,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.67582,"mean_force":1.30363,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48652,0.11801,0.05305]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47488,0.09429,0.05713],"force_p95":5.0541,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.73082,"mean_force":1.42763,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48568,0.12199,0.05384]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52538,0.09116,0.04549],"force_p95":6.60209,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.68296,"mean_force":1.48505,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49213,0.10857,0.05266]},{"body_a":"peg","body_b":"channel_base_body","contact_count":521.0,"contact_point_centroid":[0.49619,0.11909,0.00942],"force_p95":0.62006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55504,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48855,0.18661,0.18049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":332.0,"contact_point_centroid":[0.49608,0.11892,0.00944],"force_p95":0.59935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98155,"mean_force":0.54556,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48205,0.1472,0.05526]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49373,0.13695,0.05397],"force_p95":1.3062,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.59248,"mean_force":0.43033,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48177,0.13695,0.05487]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50462,0.21211,0.29582]}],"total_contact_groups":10},"final_pose_error":0.17473,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50163,0.05572,0.02432],"final_tcp_position":[0.49811,0.09427,0.05248],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":497.03445,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.4961,0.11909,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19922,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5806,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":545.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48488,0.16113,0.05979],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.1189,0.03398],"object_pos_start":[0.4961,0.11909,0.03383],"object_to_goal_dist_end":0.19904,"object_to_goal_dist_start":0.19922,"object_z_max":0.03413,"peak_contact_force":1.98155,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":337.0,"raw_peak_contact_force":1.98155,"tcp_end":[0.48177,0.13663,0.05488],"tcp_start":[0.48488,0.16113,0.05979],"tcp_to_object_dist_end":0.03088,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50163,0.05572,0.02432],"object_pos_start":[0.49601,0.1189,0.03398],"object_to_goal_dist_end":0.13663,"object_to_goal_dist_start":0.19904,"object_z_max":0.04077,"peak_contact_force":302.78373,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3058.0,"raw_peak_contact_force":497.03445,"subtask_id":"push","tcp_end":[0.49811,0.09427,0.05248],"tcp_start":[0.48177,0.13663,0.05488],"tcp_to_object_dist_end":0.04787,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```