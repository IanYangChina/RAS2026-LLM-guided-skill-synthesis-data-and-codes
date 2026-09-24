## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2436 | 0.55 | ❌ rejected |
| 12 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1766 | 0.63 | ❌ rejected |
| 11 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.0716 | 0.59 | ❌ rejected |
| 10 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.2820 | 0.70 | ✅ accepted |
| 9 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0732 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.55 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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

## Current Skill (Q=0.244) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align_to_entry
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.15
    - 0.04
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_peg
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
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.07
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
    - 0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.04
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_threshold:
      type: scalar
      range:
      - 20.0
      - 38.0
      default: 30.0
      binds_to:
      - path: guards.push_contact.threshold
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
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_contact
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_entry** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.15, 0.04]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_threshold: status=consumed; consumers=guards.push_contact.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_contact, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.244
- **task_score** (E): 0.547
- **fitness_score**: 0.481  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_entry | 1.00 | 1.00 | 0.2619 |
| approach_peg | 1.00 | 1.00 | 0.0134 |
| contact_peg | 0.67 | 1.00 | 0.0358 |
| push_through | 1.00 | 1.00 | 0.1287 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_entry | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.159, 0.042) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.522 | 2.732 |
| approach_peg | approach | 1.00 / step_budget | (0.496, 0.159, 0.042)→(0.498, 0.149, 0.036) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.552 | 0.579 |
| contact_peg | contact | 0.67 / force_exceeded | (0.498, 0.149, 0.036)→(0.497, 0.114, 0.029) | (0.502, 0.098, 0.034)→(0.504, 0.085, 0.035) | 0.178→0.165 | 1.00 / 2.333 | 1306.473 | 3.319 |
| push_through | push | 1.00 / time_limit | (0.497, 0.114, 0.029)→(0.495, -0.014, 0.032) | (0.504, 0.085, 0.035)→(0.507, -0.042, 0.036) | 0.165→0.039 | 1.00 / 2.000 | 0.892 | 25.310 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.899
- alignment_error: None
- force_efficiency: 0.755
- terminal_score: 0.899
- phase_score: 0.420
- phase_breakdown.approach_score: 0.726
- phase_breakdown.contact_score: 0.721
- phase_breakdown.push_score: 0.217

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.612
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.899
- **Median Q (composite search score)**: 0.288
- **K-run variance**: 0.0472
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.321


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14685,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.07157,"align_to_entry.speed":0.11307,"approach_peg.approach_tolerance":0.01771,"approach_peg.speed":0.05475,"contact_peg.contact_force":2.80824,"contact_peg.speed":0.01964,"push_through.push_max_time":8.69528,"push_through.push_speed":0.07999},"optimized_scores":{"best_composite_score":0.48505,"best_fitness_score":0.61171,"best_task_score":0.89946},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":822.0,"contact_point_centroid":[0.5014,0.05048,0.04057],"force_p95":8.28429,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.23843,"mean_force":2.88849,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49553,0.0618,0.02851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":585.0,"contact_point_centroid":[0.50674,0.01614,0.00996],"force_p95":7.97507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.91502,"mean_force":4.07452,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49557,0.06088,0.0286]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":670.0,"contact_point_centroid":[0.52505,0.02785,0.02695],"force_p95":3.34921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.25967,"mean_force":1.08534,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49557,0.05552,0.02885]},{"body_a":"attachment","body_b":"peg","contact_count":476.0,"contact_point_centroid":[0.50194,0.12193,0.04247],"force_p95":2.26731,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.86432,"mean_force":1.57527,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4974,0.1336,0.03039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":931.0,"contact_point_centroid":[0.50498,0.09975,0.00968],"force_p95":2.35069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.74758,"mean_force":1.21592,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49604,0.14163,0.03141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":947.0,"contact_point_centroid":[0.50362,0.11163,0.00939],"force_p95":0.60232,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55234,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49772,0.21955,0.16414]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":133.0,"contact_point_centroid":[0.52506,0.09927,0.02922],"force_p95":1.14807,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61195,"mean_force":0.82409,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49846,0.12803,0.02982]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50465,0.11219,0.00946],"force_p95":0.57626,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59862,"mean_force":0.54195,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49611,0.15898,0.03928]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49997,0.19987,0.29908]}],"total_contact_groups":9},"final_pose_error":0.07631,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50708,-0.03214,0.03616],"final_tcp_position":[0.49576,-0.00425,0.03173],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":12.23843,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11175,0.03395],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50278,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":963.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49628,0.15923,0.04044],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11179,0.0339],"object_pos_start":[0.50373,0.11175,0.03395],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19188,"object_z_max":0.03395,"peak_contact_force":0.57508,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.59862,"subtask_id":"approach","tcp_end":[0.49641,0.15993,0.03778],"tcp_start":[0.49628,0.15923,0.04044],"tcp_to_object_dist_end":0.04885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.50721,0.09692,0.03559],"object_pos_start":[0.50371,0.11179,0.0339],"object_to_goal_dist_end":0.17712,"object_to_goal_dist_start":0.19192,"object_z_max":0.03568,"peak_contact_force":2.86432,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1540.0,"raw_peak_contact_force":2.86432,"subtask_id":"contact","tcp_end":[0.49886,0.12593,0.0296],"tcp_start":[0.49641,0.15993,0.03778],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50708,-0.03214,0.03616],"object_pos_start":[0.50721,0.09692,0.03559],"object_to_goal_dist_end":0.04854,"object_to_goal_dist_start":0.17712,"object_z_max":0.03623,"peak_contact_force":1.43689,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2077.0,"raw_peak_contact_force":12.23843,"subtask_id":"push","tcp_end":[0.49576,-0.00425,0.03173],"tcp_start":[0.49886,0.12593,0.0296],"tcp_to_object_dist_end":0.03042,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21088,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.04351,"align_to_entry.speed":0.10969,"approach_peg.approach_tolerance":0.02879,"approach_peg.speed":0.09225,"contact_peg.contact_force":3.30371,"contact_peg.speed":0.01624,"push_through.push_max_time":6.35048,"push_through.push_speed":0.07819},"optimized_scores":{"best_composite_score":-0.04185,"best_fitness_score":0.41815,"best_task_score":0.4032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":825.0,"contact_point_centroid":[0.49829,0.05593,0.03951],"force_p95":11.31818,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.61126,"mean_force":4.65141,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49078,0.06639,0.0285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":687.0,"contact_point_centroid":[0.50688,0.02872,0.00993],"force_p95":9.65382,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.15829,"mean_force":4.99837,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49067,0.07059,0.02834]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":738.0,"contact_point_centroid":[0.52514,0.02835,0.03359],"force_p95":8.31049,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.32669,"mean_force":2.92638,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49107,0.05411,0.02894]},{"body_a":"peg","body_b":"link7","contact_count":173.0,"contact_point_centroid":[0.52024,0.08393,0.0624],"force_p95":6.81787,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.90911,"mean_force":3.97329,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48944,0.09959,0.02679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":956.0,"contact_point_centroid":[0.4959,0.09888,0.00984],"force_p95":2.22563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.2348,"mean_force":1.51915,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49207,0.14287,0.0329]},{"body_a":"attachment","body_b":"peg","contact_count":748.0,"contact_point_centroid":[0.49477,0.12761,0.04011],"force_p95":1.95169,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.89069,"mean_force":1.46311,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49198,0.13947,0.03191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":831.0,"contact_point_centroid":[0.4962,0.11903,0.00942],"force_p95":0.61155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55041,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49768,0.20299,0.16717]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49988,0.19985,0.29776]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49446,0.12,0.00944],"force_p95":0.57399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58221,"mean_force":0.53914,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49584,0.15806,0.04327]}],"total_contact_groups":9},"final_pose_error":0.08288,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50717,-0.02472,0.03648],"final_tcp_position":[0.49308,0.00215,0.03152],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":16.61126,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11922,0.03389],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19935,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52098,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":855.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.49633,0.15798,0.0447],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11903,0.03391],"object_pos_start":[0.49602,0.11922,0.03389],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19935,"object_z_max":0.03391,"peak_contact_force":0.53369,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.58221,"subtask_id":"approach","tcp_end":[0.49546,0.15986,0.04134],"tcp_start":[0.49633,0.15798,0.0447],"tcp_to_object_dist_end":0.0415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.49806,0.10042,0.03537],"object_pos_start":[0.49602,0.11903,0.03391],"object_to_goal_dist_end":0.18049,"object_to_goal_dist_start":0.19917,"object_z_max":0.03538,"peak_contact_force":1.49527,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1704.0,"raw_peak_contact_force":3.2348,"subtask_id":"contact","tcp_end":[0.49214,0.12994,0.02963],"tcp_start":[0.49546,0.15986,0.04134],"tcp_to_object_dist_end":0.03066,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50717,-0.02472,0.03648],"object_pos_start":[0.49806,0.10042,0.03537],"object_to_goal_dist_end":0.05586,"object_to_goal_dist_start":0.18049,"object_z_max":0.03696,"peak_contact_force":0.92954,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2423.0,"raw_peak_contact_force":16.61126,"subtask_id":"push","tcp_end":[0.49308,0.00215,0.03152],"tcp_start":[0.49214,0.12994,0.02963],"tcp_to_object_dist_end":0.03074,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.07678,"align_to_entry.speed":0.1213,"approach_peg.approach_tolerance":0.00813,"approach_peg.speed":0.0725,"contact_peg.contact_force":3.81113,"contact_peg.speed":0.02639,"push_through.push_max_time":8.60948,"push_through.push_speed":0.07973},"optimized_scores":{"best_composite_score":0.28764,"best_fitness_score":0.4143,"best_task_score":0.33966},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.53567,0.07516,0.05999],"force_p95":40.41921,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.07993,"mean_force":30.50617,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49779,0.07529,0.02584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.50639,-0.0181,0.00993],"force_p95":8.06911,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.62032,"mean_force":3.71419,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49688,0.02722,0.02829]},{"body_a":"attachment","body_b":"peg","contact_count":803.0,"contact_point_centroid":[0.50228,0.01086,0.04171],"force_p95":8.10608,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.35838,"mean_force":2.59332,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49679,0.02238,0.02855]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":520.0,"contact_point_centroid":[0.52505,-0.00689,0.02132],"force_p95":2.93033,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.008,"mean_force":0.90435,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49673,0.02099,0.02859]},{"body_a":"peg","body_b":"channel_base_body","contact_count":939.0,"contact_point_centroid":[0.50586,0.06301,0.00937],"force_p95":0.55524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56097,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49772,0.22263,0.16224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":827.0,"contact_point_centroid":[0.50597,0.06031,0.00945],"force_p95":2.19025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.85794,"mean_force":0.73395,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.499,0.10587,0.02687]},{"body_a":"attachment","body_b":"peg","contact_count":116.0,"contact_point_centroid":[0.50435,0.07831,0.04243],"force_p95":2.63266,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.41836,"mean_force":1.57262,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50034,0.09015,0.02781]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.50025,0.19998,0.2969]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52501,0.05915,0.02701],"force_p95":0.82076,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32204,"mean_force":0.5976,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50052,0.08844,0.02796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.50599,0.06297,0.00938],"force_p95":0.55256,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.5466,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49755,0.14223,0.03319]}],"total_contact_groups":10},"final_pose_error":0.04049,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.06876,0.03605],"final_tcp_position":[0.49631,-0.04035,0.03266],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3915.06039,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54232,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":973.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49629,0.15913,0.03968],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09685,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.50601,0.06295,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54734,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":230.0,"raw_peak_contact_force":0.55532,"subtask_id":"approach","tcp_end":[0.50067,0.1275,0.02984],"tcp_start":[0.49629,0.15913,0.03968],"tcp_to_object_dist_end":0.06489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":838.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,0.05808,0.03542],"object_pos_start":[0.50601,0.06295,0.03381],"object_to_goal_dist_end":0.13833,"object_to_goal_dist_start":0.14321,"object_z_max":0.03547,"peak_contact_force":3915.06039,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":968.0,"raw_peak_contact_force":3.85794,"subtask_id":"contact","tcp_end":[0.50059,0.08762,0.02801],"tcp_start":[0.50067,0.1275,0.02984],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,-0.06876,0.03605],"object_pos_start":[0.507,0.05808,0.03542],"object_to_goal_dist_end":0.01377,"object_to_goal_dist_start":0.13833,"object_z_max":0.0362,"peak_contact_force":0.31006,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1995.0,"raw_peak_contact_force":47.07993,"subtask_id":"push","tcp_end":[0.49631,-0.04035,0.03266],"tcp_start":[0.50059,0.08762,0.02801],"tcp_to_object_dist_end":0.03052,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```