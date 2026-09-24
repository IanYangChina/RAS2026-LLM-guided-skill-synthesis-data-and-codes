## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1651 | 0.02 | ✅ accepted |
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2051 | 0.01 | ✅ accepted |
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2053 | 0.01 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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

## Current Skill (Q=0.165) — your mutation base

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
    - 0.07
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
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
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
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
    offset_along_axis:
      distance: 0.1
      axis: channel_axis
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.0
      - 0.2
      default: 0.1
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
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.07]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], offset_along_axis={axis=channel_axis, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.165
- **task_score** (E): 0.019
- **fitness_score**: 0.112  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2041 |
| contact_1 | 1.00 | 1.00 | 0.0580 |
| push_1 | 0.67 | 1.00 | 0.0229 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.113, 0.118) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.545 | 3.659 |
| contact_1 | descend | 1.00 / force_exceeded | (0.492, 0.113, 0.118)→(0.491, 0.097, 0.064) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 52.278 | 52.278 |
| push_1 | push | 0.67 / step_budget | (0.491, 0.097, 0.064)→(0.498, 0.080, 0.055) | (0.498, 0.068, 0.034)→(0.500, 0.059, 0.034) | 0.148→0.140 | 1.00 / 3.000 | 203.611 | 466.186 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.136
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.042
- phase_score: 0.178
- phase_breakdown.push_score: 0.041
- phase_breakdown.approach_score: 0.211
- phase_breakdown.contact_score: 0.555

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.123
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.042
- **Median Q (composite search score)**: 0.167
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.244


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40517,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09298,"contact_1.contact_force":13.77616,"contact_1.contact_speed":0.03105,"push_1.push_depth":0.13358,"push_1.push_speed":0.03572},"optimized_scores":{"best_composite_score":0.16654,"best_fitness_score":0.11321,"best_task_score":0.01355},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":388.0,"contact_point_centroid":[0.49101,0.14159,-9e-05],"force_p95":476.88419,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":747.94102,"mean_force":317.65953,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4899,0.08023,0.05488]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":365.0,"contact_point_centroid":[0.47427,0.11997,0.02863],"force_p95":413.14569,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":670.28082,"mean_force":123.57698,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48988,0.08022,0.05486]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47499,0.12,0.05999],"force_p95":121.96309,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.20894,"mean_force":65.09101,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48618,0.09182,0.0643]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.12,0.05999],"force_p95":24.69237,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.69237,"mean_force":24.69237,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.48545,0.09335,0.06596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.49793,0.06013,0.00944],"force_p95":0.65514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.53954,"mean_force":0.67787,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48941,0.08148,0.05586]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49487,0.08079,0.04527],"force_p95":18.57983,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.17862,"mean_force":7.7458,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48795,0.08083,0.05504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.49545,0.06383,0.00937],"force_p95":0.56772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55879,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48635,0.16003,0.20354]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50409,0.21536,0.29293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.4948,0.06411,0.0094],"force_p95":0.55062,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.5454,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.48156,0.10077,0.09108]}],"total_contact_groups":9},"final_pose_error":0.03318,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49768,0.05998,0.03433],"final_tcp_position":[0.49133,0.08103,0.05651],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":747.94102,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":670.0,"n_steps_budget":1000.0,"object_pos_end":[0.4952,0.06407,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14428,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54342,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":671.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.47976,0.10896,0.11828],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.49493,0.06364,0.03401],"object_pos_start":[0.4952,0.06407,0.03396],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14428,"object_z_max":0.03401,"peak_contact_force":24.69237,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":334.0,"raw_peak_contact_force":24.69237,"subtask_id":"contact","tcp_end":[0.48548,0.0933,0.06582],"tcp_start":[0.47976,0.10896,0.11828],"tcp_to_object_dist_end":0.04451,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":467.0,"n_steps_budget":870.0,"object_pos_end":[0.49768,0.05998,0.03433],"object_pos_start":[0.49493,0.06364,0.03401],"object_to_goal_dist_end":0.14011,"object_to_goal_dist_start":0.14386,"object_z_max":0.03582,"peak_contact_force":321.48509,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1241.0,"raw_peak_contact_force":747.94102,"subtask_id":"push","tcp_end":[0.49133,0.08103,0.05651],"tcp_start":[0.48548,0.0933,0.06582],"tcp_to_object_dist_end":0.03123,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.59091,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03726,"contact_1.contact_force":8.81837,"contact_1.contact_speed":0.02361,"push_1.push_depth":0.13452,"push_1.push_speed":0.01148},"optimized_scores":{"best_composite_score":0.15205,"best_fitness_score":0.09871,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":647.0,"contact_point_centroid":[0.49113,0.14266,-6e-05],"force_p95":293.19983,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.2193,"mean_force":229.12928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49077,0.08025,0.05376]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":840.0,"contact_point_centroid":[0.46084,0.11997,0.05406],"force_p95":125.47591,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.04432,"mean_force":102.00315,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4903,0.0802,0.05445]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":132.0,"contact_point_centroid":[0.47498,0.11999,0.05995],"force_p95":168.16159,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.60415,"mean_force":134.54909,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48145,0.08612,0.0696]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.12,0.05997],"force_p95":38.04222,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.04222,"mean_force":38.04222,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.47728,0.0901,0.07186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.49425,0.05899,0.00936],"force_p95":0.55954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56556,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48157,0.15956,0.20928]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50277,0.22095,0.28776]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49418,0.05896,0.0094],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54522,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48897,0.08108,0.05674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.49419,0.05904,0.00939],"force_p95":0.55014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5514,"mean_force":0.54581,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.47095,0.09663,0.09356]}],"total_contact_groups":8},"final_pose_error":0.0304,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49385,0.05908,0.03404],"final_tcp_position":[0.49205,0.08017,0.05424],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":322.2193,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.49407,0.05881,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13907,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54646,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":790.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46662,0.10422,0.1182],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.49394,0.05886,0.03395],"object_pos_start":[0.49407,0.05881,0.03389],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13907,"object_z_max":0.03395,"peak_contact_force":38.04222,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":364.0,"raw_peak_contact_force":38.04222,"subtask_id":"contact","tcp_end":[0.47732,0.09007,0.07176],"tcp_start":[0.46662,0.10422,0.1182],"tcp_to_object_dist_end":0.05177,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49385,0.05908,0.03404],"object_pos_start":[0.49394,0.05886,0.03395],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.13912,"object_z_max":0.03404,"peak_contact_force":289.34742,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2619.0,"raw_peak_contact_force":322.2193,"subtask_id":"push","tcp_end":[0.49205,0.08017,0.05424],"tcp_start":[0.47732,0.09007,0.07176],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78889,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0511,"contact_1.contact_force":12.30968,"contact_1.contact_speed":0.02844,"push_1.push_depth":0.07077,"push_1.push_speed":0.02538},"optimized_scores":{"best_composite_score":0.17665,"best_fitness_score":0.12332,"best_task_score":0.04196},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.525,0.11988,0.06],"force_p95":318.71467,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.39733,"mean_force":236.22879,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50912,0.07923,0.05269]},{"body_a":"world","body_b":"link7","contact_count":974.0,"contact_point_centroid":[0.50962,0.15553,-5e-05],"force_p95":190.20265,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.01634,"mean_force":146.97932,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50927,0.09252,0.05308]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51135,0.16868,-1e-05],"force_p95":94.09812,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.09812,"mean_force":94.09812,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.51019,0.10657,0.05419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":953.0,"contact_point_centroid":[0.50425,0.06732,0.00959],"force_p95":1.8209,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.6937,"mean_force":0.91437,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50928,0.09281,0.05309]},{"body_a":"attachment","body_b":"peg","contact_count":302.0,"contact_point_centroid":[0.50591,0.0896,0.05234],"force_p95":2.63594,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.52751,"mean_force":1.40895,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50912,0.08959,0.05296]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":156.0,"contact_point_centroid":[0.5251,0.06583,0.03154],"force_p95":0.4108,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.21316,"mean_force":0.33963,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50911,0.08516,0.05284]},{"body_a":"peg","body_b":"channel_base_body","contact_count":725.0,"contact_point_centroid":[0.50575,0.08087,0.00936],"force_p95":0.55328,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56781,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50999,0.16843,0.20767]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50302,0.22176,0.28718]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.50598,0.08093,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54678,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.51987,0.1157,0.0858]}],"total_contact_groups":9},"final_pose_error":0.08991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,0.05922,0.03478],"final_tcp_position":[0.50928,0.07928,0.05276],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":328.39733,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":754.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":761.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.53031,0.12488,0.11752],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":94.09812,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":314.0,"raw_peak_contact_force":94.09812,"subtask_id":"contact","tcp_end":[0.51014,0.10653,0.05402],"tcp_start":[0.53031,0.12488,0.11752],"tcp_to_object_dist_end":0.03293,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.05922,0.03478],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.13949,"object_to_goal_dist_start":0.16112,"object_z_max":0.03597,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2462.0,"raw_peak_contact_force":328.39733,"subtask_id":"push","tcp_end":[0.50928,0.07928,0.05276],"tcp_start":[0.51014,0.10653,0.05402],"tcp_to_object_dist_end":0.02704,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```