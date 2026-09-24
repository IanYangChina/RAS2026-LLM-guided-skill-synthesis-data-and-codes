## Search State

- **Seed**: 7
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3019 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.302) — your mutation base

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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
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
    - 0.15
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.302
- **task_score** (E): 0.394
- **fitness_score**: 0.312  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2474 |
| contact_1 | 1.00 | 1.00 | 0.0003 |
| push_1 | 0.00 | 1.00 | 0.0635 |
| retract_1 | 0.00 | 1.00 | 0.1245 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.504, 0.144, 0.061) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 2.000 | 205.467 | 254.094 |
| contact_1 | contact | 1.00 / force_exceeded | (0.504, 0.144, 0.061)→(0.504, 0.144, 0.061) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 123.163 | 139.430 |
| push_1 | push | 0.00 / step_budget | (0.504, 0.144, 0.061)→(0.506, 0.082, 0.054) | (0.502, 0.098, 0.034)→(0.505, 0.052, 0.031) | 0.178→0.133 | 1.00 / 3.000 | 304.458 | 564.285 |
| retract_1 | retract | 0.00 / step_budget | (0.506, 0.082, 0.054)→(0.507, -0.032, 0.105) | (0.505, 0.052, 0.031)→(0.502, 0.021, 0.024) | 0.133→0.103 | 1.00 / 1.000 | 0.921 | 623.857 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.601
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.601
- phase_score: 0.282
- phase_breakdown.approach_score: 0.723
- phase_breakdown.contact_score: 0.571
- phase_breakdown.push_score: 0.038

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.409
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.601
- **Median Q (composite search score)**: 0.343
- **K-run variance**: 0.0102
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.249


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99291,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08214,"contact_1.contact_force":6.96353,"contact_1.speed":0.02847,"push_1.speed":0.07507},"optimized_scores":{"best_composite_score":0.39936,"best_fitness_score":0.40936,"best_task_score":0.60115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":313.0,"contact_point_centroid":[0.47496,0.1199,0.05807],"force_p95":261.77632,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":603.35159,"mean_force":240.7264,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50715,0.08168,0.05197]},{"body_a":"world","body_b":"link7","contact_count":611.0,"contact_point_centroid":[0.50648,0.17849,-2e-05],"force_p95":175.76067,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":455.17551,"mean_force":130.4533,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50496,0.11556,0.0532]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":818.0,"contact_point_centroid":[0.47357,0.11994,0.05998],"force_p95":292.31034,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":389.8556,"mean_force":155.55879,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51169,0.09194,0.04371]},{"body_a":"world","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.50829,0.21536,-0.00048],"force_p95":278.24819,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.93195,"mean_force":228.09688,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50607,0.15395,0.05401]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":294.0,"contact_point_centroid":[0.52502,0.09665,0.04503],"force_p95":214.77304,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.51798,"mean_force":107.67208,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51361,0.09391,0.04263]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50859,0.21542,-0.00026],"force_p95":135.39454,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.39454,"mean_force":135.39454,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50584,0.15484,0.05534]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.03102,0.06],"force_p95":55.25149,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.42116,"mean_force":53.72449,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51418,0.05492,0.06159]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.50698,0.06495,0.05958],"force_p95":16.90982,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.90422,"mean_force":4.90252,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51386,0.07264,0.05508]},{"body_a":"peg","body_b":"channel_base_body","contact_count":918.0,"contact_point_centroid":[0.50368,0.08011,0.00948],"force_p95":2.55738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.44828,"mean_force":0.98825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50566,0.10657,0.05285]},{"body_a":"attachment","body_b":"peg","contact_count":170.0,"contact_point_centroid":[0.5045,0.10607,0.04966],"force_p95":18.13831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.97056,"mean_force":3.34486,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50505,0.10579,0.05291]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":145.0,"contact_point_centroid":[0.52528,0.07465,0.03759],"force_p95":8.58715,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.2055,"mean_force":1.38113,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5056,0.09406,0.05267]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50657,0.05597,0.00936],"force_p95":0.55177,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.5901,"mean_force":0.65821,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51178,0.0856,0.04693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":831.0,"contact_point_centroid":[0.50363,0.11173,0.00937],"force_p95":0.61587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55466,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49985,0.17963,0.17105]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50378,0.20566,0.29959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51883,0.10199,0.00939],"force_p95":0.52213,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52213,"mean_force":0.52213,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50584,0.15484,0.05534]}],"total_contact_groups":15},"final_pose_error":0.05795,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50632,0.01559,0.02344],"final_tcp_position":[0.50552,-0.03793,0.11052],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":603.35159,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":223.56921,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":881.0,"raw_peak_contact_force":308.93195,"subtask_id":"approach","tcp_end":[0.50584,0.15484,0.05534],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.50373,0.11173,0.03381],"object_pos_start":[0.50376,0.11173,0.03382],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19187,"object_z_max":0.03382,"peak_contact_force":135.39454,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":135.39454,"subtask_id":"contact","tcp_end":[0.50576,0.15478,0.05547],"tcp_start":[0.50584,0.15484,0.05534],"tcp_to_object_dist_end":0.04823,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5067,0.06028,0.03381],"object_pos_start":[0.50373,0.11173,0.03381],"object_to_goal_dist_end":0.14057,"object_to_goal_dist_start":0.19187,"object_z_max":0.03772,"peak_contact_force":246.10594,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2157.0,"raw_peak_contact_force":603.35159,"subtask_id":"push","tcp_end":[0.50821,0.08318,0.05135],"tcp_start":[0.50576,0.15478,0.05547],"tcp_to_object_dist_end":0.02888,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50632,0.01559,0.02344],"object_pos_start":[0.5067,0.06028,0.03381],"object_to_goal_dist_end":0.09722,"object_to_goal_dist_start":0.14057,"object_z_max":0.0408,"peak_contact_force":0.37769,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2131.0,"raw_peak_contact_force":389.8556,"tcp_end":[0.50552,-0.03793,0.11052],"tcp_start":[0.50821,0.08318,0.05135],"tcp_to_object_dist_end":0.10222,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99301,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0799,"contact_1.contact_force":9.29021,"contact_1.speed":0.02273,"push_1.speed":0.07926},"optimized_scores":{"best_composite_score":0.34329,"best_fitness_score":0.35329,"best_task_score":0.45425},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":282.0,"contact_point_centroid":[0.46194,0.11989,0.06],"force_p95":460.98759,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":624.17718,"mean_force":281.07297,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49381,0.08159,0.0522]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":852.0,"contact_point_centroid":[0.46531,0.11995,0.05998],"force_p95":198.14772,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":481.23,"mean_force":147.43616,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50311,0.09164,0.04355]},{"body_a":"world","body_b":"link7","contact_count":829.0,"contact_point_centroid":[0.48888,0.17259,-2e-05],"force_p95":218.08855,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.48166,"mean_force":137.9989,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4891,0.10975,0.05293]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.48488,0.14593,-1e-05],"force_p95":401.20465,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":419.77409,"mean_force":234.07965,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4953,0.08288,0.05208]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.52502,0.07961,0.0572],"force_p95":222.755,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":268.50925,"mean_force":95.32838,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51368,0.07682,0.0545]},{"body_a":"world","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.48616,0.22196,-0.0005],"force_p95":257.77196,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.01496,"mean_force":224.62553,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48397,0.16048,0.05389]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48639,0.22201,-0.0003],"force_p95":134.17427,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.17427,"mean_force":134.17427,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48372,0.16127,0.05511]},{"body_a":"attachment","body_b":"peg","contact_count":593.0,"contact_point_centroid":[0.49661,0.10292,0.04352],"force_p95":39.24434,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.73237,"mean_force":8.45781,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48954,0.10246,0.0528]},{"body_a":"peg","body_b":"channel_base_body","contact_count":987.0,"contact_point_centroid":[0.5016,0.08424,0.00971],"force_p95":28.26552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.94278,"mean_force":5.41937,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48909,0.10979,0.05294]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":132.0,"contact_point_centroid":[0.52503,0.04674,0.05927],"force_p95":13.15302,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.64093,"mean_force":2.30466,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49279,0.08161,0.05238]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49482,0.03653,0.00806],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.66006,"mean_force":0.6395,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50423,0.08413,0.04726]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47498,0.06104,0.02421],"force_p95":9.11143,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.15253,"mean_force":3.27455,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50298,0.09328,0.04285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":821.0,"contact_point_centroid":[0.49616,0.11922,0.00943],"force_p95":0.5997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54975,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48906,0.18271,0.17084]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50466,0.21213,0.29588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51378,0.12,0.00947],"force_p95":0.47577,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47577,"mean_force":0.47577,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48372,0.16127,0.05511]}],"total_contact_groups":15},"final_pose_error":0.05709,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4936,0.03686,0.02417],"final_tcp_position":[0.50416,-0.03863,0.11088],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":624.17718,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11914,0.03396],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19927,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":218.8525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":877.0,"raw_peak_contact_force":262.01496,"subtask_id":"approach","tcp_end":[0.48372,0.16127,0.05511],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.49603,0.11914,0.03397],"object_pos_start":[0.49606,0.11914,0.03396],"object_to_goal_dist_end":0.19927,"object_to_goal_dist_start":0.19927,"object_z_max":0.03396,"peak_contact_force":134.17427,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":134.17427,"subtask_id":"contact","tcp_end":[0.48364,0.16122,0.05524],"tcp_start":[0.48372,0.16127,0.05511],"tcp_to_object_dist_end":0.04875,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50328,0.03649,0.02383],"object_pos_start":[0.49603,0.11914,0.03397],"object_to_goal_dist_end":0.11765,"object_to_goal_dist_start":0.19927,"object_z_max":0.0407,"peak_contact_force":265.32468,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2823.0,"raw_peak_contact_force":624.17718,"subtask_id":"push","tcp_end":[0.49531,0.0829,0.05206],"tcp_start":[0.48364,0.16122,0.05524],"tcp_to_object_dist_end":0.05491,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4936,0.03686,0.02417],"object_pos_start":[0.50328,0.03649,0.02383],"object_to_goal_dist_end":0.1181,"object_to_goal_dist_start":0.11765,"object_z_max":0.02472,"peak_contact_force":0.60595,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1901.0,"raw_peak_contact_force":481.23,"tcp_end":[0.50416,-0.03863,0.11088],"tcp_start":[0.49531,0.0829,0.05206],"tcp_to_object_dist_end":0.11546,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21244,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04088,"contact_1.contact_force":13.79427,"contact_1.speed":0.03859,"push_1.speed":0.04708},"optimized_scores":{"best_composite_score":0.16305,"best_fitness_score":0.17305,"best_task_score":0.12732},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":774.0,"contact_point_centroid":[0.47496,0.11994,0.05997],"force_p95":598.98518,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1000.48503,"mean_force":352.61012,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51326,0.08236,0.05367]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":867.0,"contact_point_centroid":[0.52505,0.08328,0.0546],"force_p95":387.31075,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":687.04345,"mean_force":235.54195,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51333,0.08147,0.05351]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":84.0,"contact_point_centroid":[0.47496,0.11994,0.05994],"force_p95":419.10919,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":465.3276,"mean_force":269.32374,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51311,0.07879,0.05935]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":544.0,"contact_point_centroid":[0.525,0.11994,0.06],"force_p95":289.73658,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":440.8001,"mean_force":171.07447,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51305,0.07918,0.05936]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":930.0,"contact_point_centroid":[0.52502,0.09167,0.05961],"force_p95":213.22603,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.19326,"mean_force":120.77041,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51512,0.09082,0.06332]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":102.0,"contact_point_centroid":[0.52505,0.12,0.05979],"force_p95":176.10256,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.3364,"mean_force":159.12216,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52268,0.11514,0.07149]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.12,0.05997],"force_p95":146.28101,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.72106,"mean_force":124.32049,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52258,0.11518,0.07198]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,0.04396,0.06],"force_p95":23.42348,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.64607,"mean_force":4.78966,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.514,0.07013,0.05607]},{"body_a":"attachment","body_b":"peg","contact_count":285.0,"contact_point_centroid":[0.50776,0.0718,0.058],"force_p95":3.41868,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.94569,"mean_force":1.19455,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51354,0.07938,0.05176]},{"body_a":"peg","body_b":"channel_base_body","contact_count":979.0,"contact_point_centroid":[0.50514,0.05142,0.00964],"force_p95":1.93535,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.26545,"mean_force":0.7997,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51337,0.07956,0.05421]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5066,0.05214,0.00971],"force_p95":1.07461,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.16324,"mean_force":0.72337,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51503,0.09067,0.06325]},{"body_a":"attachment","body_b":"peg","contact_count":534.0,"contact_point_centroid":[0.50534,0.0789,0.05849],"force_p95":1.13454,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.78257,"mean_force":0.50751,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51305,0.0792,0.05934]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50868,0.1581,0.17492]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50343,0.22037,0.28874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49457,0.07097,0.00938],"force_p95":0.55012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55054,"mean_force":0.54726,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52257,0.11518,0.07201]}],"total_contact_groups":15},"final_pose_error":0.08393,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50611,0.01154,0.025],"final_tcp_position":[0.51172,-0.01853,0.09406],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1000.48503,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":173.9792,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1108.0,"raw_peak_contact_force":191.3364,"subtask_id":"approach","tcp_end":[0.52273,0.11528,0.07197],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":870.0,"object_pos_end":[0.50601,0.06303,0.0338],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14323,"object_z_max":0.0338,"peak_contact_force":99.91992,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":148.72106,"subtask_id":"contact","tcp_end":[0.52237,0.11505,0.07192],"tcp_start":[0.52273,0.11528,0.07197],"tcp_to_object_dist_end":0.06653,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,0.0604,0.03503],"object_pos_start":[0.50601,0.06303,0.0338],"object_to_goal_dist_end":0.14062,"object_to_goal_dist_start":0.14329,"object_z_max":0.03577,"peak_contact_force":401.94322,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3092.0,"raw_peak_contact_force":465.3276,"subtask_id":"push","tcp_end":[0.51311,0.07888,0.05927],"tcp_start":[0.52237,0.11505,0.07192],"tcp_to_object_dist_end":0.03128,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.01154,0.025],"object_pos_start":[0.50609,0.0604,0.03503],"object_to_goal_dist_end":0.09296,"object_to_goal_dist_start":0.14062,"object_z_max":0.04084,"peak_contact_force":1.77851,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2913.0,"raw_peak_contact_force":1000.48503,"tcp_end":[0.51172,-0.01853,0.09406],"tcp_start":[0.51311,0.07888,0.05927],"tcp_to_object_dist_end":0.07553,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```