## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1068 | 0.23 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3019 | 0.39 | ✅ accepted |

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

## Current Skill (Q=0.107) — your mutation base

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

- **Composite score**: 0.107
- **task_score** (E): 0.230
- **fitness_score**: 0.217  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2120 |
| contact_1 | 1.00 | 1.00 | 0.0480 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 0.00 | 1.00 | 0.0547 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.140, 0.099) | (0.509, 0.098, 0.040)→(0.502, 0.099, 0.034) | 0.179→0.179 | 1.00 / 1.000 | 0.554 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.505, 0.140, 0.099)→(0.500, 0.125, 0.054) | (0.502, 0.099, 0.034)→(0.503, 0.112, 0.027) | 0.179→0.192 | 1.00 / 2.000 | 1354.778 | 48.762 |
| push_1 | push | 0.00 / guard_failure | (0.500, 0.125, 0.054)→(0.500, 0.125, 0.054) | (0.503, 0.112, 0.027)→(0.503, 0.112, 0.027) | 0.192→0.192 | 1.00 / 2.000 | 48.196 | 76.381 |
| retract_1 | retract | 0.00 / step_budget | (0.500, 0.125, 0.054)→(0.513, 0.074, 0.059) | (0.503, 0.112, 0.027)→(0.502, 0.056, 0.029) | 0.192→0.137 | 1.00 / 2.667 | 210.315 | 400.762 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.354
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.354
- phase_score: 0.210
- phase_breakdown.approach_score: 0.306
- phase_breakdown.contact_score: 0.705
- phase_breakdown.push_score: 0.013

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.268
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.354
- **Median Q (composite search score)**: 0.141
- **K-run variance**: 0.0037
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03536,"contact_1.contact_force":15.04608,"contact_1.speed":0.02796,"push_1.push_distance":0.1218,"push_1.push_speed":0.02101,"push_1.push_tolerance":0.03526},"optimized_scores":{"best_composite_score":0.15756,"best_fitness_score":0.26756,"best_task_score":0.35411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":654.0,"contact_point_centroid":[0.47422,0.11994,0.05983],"force_p95":205.36032,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.08428,"mean_force":155.27792,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50735,0.07785,0.06698]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":230.0,"contact_point_centroid":[0.52503,0.07862,0.05999],"force_p95":201.8609,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.00707,"mean_force":174.22772,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51373,0.07541,0.0622]},{"body_a":"world","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.50281,0.19998,-0.0002],"force_p95":108.65564,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.52487,"mean_force":82.55075,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50165,0.13791,0.05386]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50287,0.20029,-0.0002],"force_p95":76.40375,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.18698,"mean_force":66.05364,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50166,0.13823,0.05386]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50289,0.2004,-9e-05],"force_p95":68.67142,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.67142,"mean_force":68.67142,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50168,0.13833,0.05408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":982.0,"contact_point_centroid":[0.50419,0.06689,0.00862],"force_p95":4.19196,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.6922,"mean_force":1.06434,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50483,0.08735,0.06549]},{"body_a":"attachment","body_b":"peg","contact_count":125.0,"contact_point_centroid":[0.5014,0.11151,0.04894],"force_p95":9.63125,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.5609,"mean_force":3.23694,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4988,0.11154,0.06062]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52501,0.03197,0.02447],"force_p95":8.33565,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.38411,"mean_force":3.4483,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51333,0.07546,0.06247]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52504,0.11991,0.05986],"force_p95":2.0955,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.27411,"mean_force":0.34448,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49829,0.07955,0.07429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":749.0,"contact_point_centroid":[0.50364,0.11164,0.00939],"force_p95":0.60993,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55417,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4994,0.18211,0.20198]},{"body_a":"peg","body_b":"channel_base_body","contact_count":238.0,"contact_point_centroid":[0.50363,0.11169,0.00942],"force_p95":0.59631,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61881,"mean_force":0.54211,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50336,0.14574,0.07621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48979,0.10391,0.00942],"force_p95":0.55863,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55956,"mean_force":0.54899,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50166,0.13823,0.05386]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50378,0.20566,0.29959]}],"total_contact_groups":13},"final_pose_error":0.17841,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50593,0.05512,0.02415],"final_tcp_position":[0.5135,0.07395,0.06085],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":308.08428,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11172,0.03379],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56902,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":765.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50662,0.15337,0.09902],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11174,0.03388],"object_pos_start":[0.50369,0.11172,0.03379],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19185,"object_z_max":0.03403,"peak_contact_force":68.67142,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":239.0,"raw_peak_contact_force":68.67142,"subtask_id":"contact","tcp_end":[0.50168,0.13828,0.05392],"tcp_start":[0.50662,0.15337,0.09902],"tcp_to_object_dist_end":0.03333,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11171,0.03387],"object_pos_start":[0.50368,0.11174,0.03388],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19187,"object_z_max":0.03388,"peak_contact_force":51.61918,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":77.18698,"subtask_id":"push","tcp_end":[0.50165,0.13815,0.05375],"tcp_start":[0.50165,0.13818,0.05379],"tcp_to_object_dist_end":0.03314,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.05512,0.02415],"object_pos_start":[0.50373,0.1117,0.03387],"object_to_goal_dist_end":0.13617,"object_to_goal_dist_start":0.19184,"object_z_max":0.04081,"peak_contact_force":205.8159,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2047.0,"raw_peak_contact_force":308.08428,"tcp_end":[0.5135,0.07395,0.06085],"tcp_start":[0.50165,0.13815,0.05375],"tcp_to_object_dist_end":0.04193,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86905,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05941,"contact_1.contact_force":10.56325,"contact_1.speed":0.01928,"push_1.push_distance":0.1623,"push_1.push_speed":0.04955,"push_1.push_tolerance":0.01399},"optimized_scores":{"best_composite_score":0.141,"best_fitness_score":0.251,"best_task_score":0.31102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":534.0,"contact_point_centroid":[0.47498,0.11992,0.05993],"force_p95":228.88532,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":243.23777,"mean_force":186.58269,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50025,0.07458,0.07988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":906.0,"contact_point_centroid":[0.49622,0.085,0.00841],"force_p95":133.359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.65373,"mean_force":37.30265,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49601,0.08883,0.07653]},{"body_a":"peg","body_b":"link7","contact_count":429.0,"contact_point_centroid":[0.48957,0.15923,0.03526],"force_p95":136.70633,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.20381,"mean_force":78.7465,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48934,0.11411,0.0691]},{"body_a":"world","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.48977,0.20871,-8e-05],"force_p95":105.50229,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.34375,"mean_force":83.94775,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48854,0.14665,0.05411]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.48972,0.20891,-5e-05],"force_p95":79.36009,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.30664,"mean_force":65.50558,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48848,0.14685,0.05418]},{"body_a":"peg","body_b":"world","contact_count":260.0,"contact_point_centroid":[0.4978,0.12944,-0.00044],"force_p95":20.97608,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.44091,"mean_force":9.26442,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48793,0.12491,0.06206]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,0.08387,0.02412],"force_p95":7.08372,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.25693,"mean_force":2.35423,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50952,0.07052,0.07191]},{"body_a":"peg","body_b":"world","contact_count":227.0,"contact_point_centroid":[0.4971,0.15609,-0.00168],"force_p95":1.00201,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9666,"mean_force":0.6266,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4859,0.15157,0.07076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":699.0,"contact_point_centroid":[0.49617,0.11928,0.00943],"force_p95":0.59817,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5515,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48924,0.18453,0.19866]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50463,0.21212,0.29586]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.49875,0.16829,-0.00198],"force_p95":0.70949,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72585,"mean_force":0.59568,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48848,0.14685,0.05418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.49668,0.11988,0.00957],"force_p95":0.54469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55337,"mean_force":0.46036,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48376,0.15826,0.09386]}],"total_contact_groups":12},"final_pose_error":0.17025,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49458,0.05993,0.02433],"final_tcp_position":[0.51152,0.06998,0.07026],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3921.01344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.12174,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20187,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54728,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":723.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48451,0.16006,0.09955],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.49863,0.16001,0.01409],"object_pos_start":[0.49604,0.12174,0.03392],"object_to_goal_dist_end":0.24141,"object_to_goal_dist_start":0.20187,"object_z_max":0.03392,"peak_contact_force":3921.01344,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":293.0,"raw_peak_contact_force":2.9666,"subtask_id":"contact","tcp_end":[0.48847,0.1469,0.05425],"tcp_start":[0.48451,0.16006,0.09955],"tcp_to_object_dist_end":0.04345,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49865,0.15998,0.01409],"object_pos_start":[0.49863,0.16001,0.01409],"object_to_goal_dist_end":0.24138,"object_to_goal_dist_start":0.24141,"object_z_max":0.01409,"peak_contact_force":53.36897,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":81.30664,"subtask_id":"push","tcp_end":[0.4885,0.14677,0.05409],"tcp_start":[0.48849,0.14681,0.05412],"tcp_to_object_dist_end":0.04333,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49458,0.05993,0.02433],"object_pos_start":[0.49869,0.1599,0.01409],"object_to_goal_dist_end":0.14091,"object_to_goal_dist_start":0.2413,"object_z_max":0.03933,"peak_contact_force":220.03707,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2139.0,"raw_peak_contact_force":243.23777,"tcp_end":[0.51152,0.06998,0.07026],"tcp_start":[0.4885,0.14677,0.05409],"tcp_to_object_dist_end":0.04998,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48684,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07218,"contact_1.contact_force":6.46608,"contact_1.speed":0.02439,"push_1.push_distance":0.17543,"push_1.push_speed":0.03623,"push_1.push_tolerance":0.03657},"optimized_scores":{"best_composite_score":0.02183,"best_fitness_score":0.13183,"best_task_score":0.02542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":832.0,"contact_point_centroid":[0.47497,0.11995,0.05968],"force_p95":413.89049,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":650.96319,"mean_force":224.19382,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51227,0.0822,0.04715]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":645.0,"contact_point_centroid":[0.52505,0.0837,0.04576],"force_p95":294.93077,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.0524,"mean_force":197.50743,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51319,0.08251,0.04498]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":66.0,"contact_point_centroid":[0.525,0.11982,0.05128],"force_p95":86.15908,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.02849,"mean_force":55.62627,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50735,0.07933,0.05635]},{"body_a":"world","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.5112,0.15287,-0.00019],"force_p95":92.26248,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.95084,"mean_force":70.04958,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51007,0.09077,0.05385]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51149,0.15334,-1e-05],"force_p95":74.64923,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.64923,"mean_force":74.64923,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51032,0.09122,0.05419]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.51139,0.15322,-0.00014],"force_p95":68.34185,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.64949,"mean_force":52.60752,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51022,0.09111,0.05394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50456,0.05298,0.00962],"force_p95":2.36021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.38053,"mean_force":1.00575,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51196,0.08217,0.04776]},{"body_a":"attachment","body_b":"peg","contact_count":349.0,"contact_point_centroid":[0.50766,0.07563,0.05281],"force_p95":5.58348,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.3776,"mean_force":1.52719,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51257,0.08166,0.04565]},{"body_a":"peg","body_b":"channel_base_body","contact_count":754.0,"contact_point_centroid":[0.50578,0.06295,0.00936],"force_p95":0.55668,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56451,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50794,0.15958,0.19692]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50341,0.22023,0.28865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":226.0,"contact_point_centroid":[0.50619,0.06314,0.00938],"force_p95":0.55211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55419,"mean_force":0.54657,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51726,0.09941,0.07581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49774,0.0494,0.00938],"force_p95":0.5498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54647,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51022,0.09111,0.05394]}],"total_contact_groups":12},"final_pose_error":0.18815,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50574,0.05249,0.03759],"final_tcp_position":[0.51382,0.07661,0.04664],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":650.96319,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06303,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54707,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":788.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52495,0.10744,0.09753],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.50595,0.06303,0.0338],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":74.64923,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":227.0,"raw_peak_contact_force":74.64923,"subtask_id":"contact","tcp_end":[0.51027,0.09117,0.05402],"tcp_start":[0.52495,0.10744,0.09753],"tcp_to_object_dist_end":0.03499,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":39.59998,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":70.64949,"subtask_id":"push","tcp_end":[0.51014,0.09102,0.05379],"tcp_start":[0.51017,0.09106,0.05386],"tcp_to_object_dist_end":0.03472,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50574,0.05249,0.03759],"object_pos_start":[0.50593,0.063,0.03381],"object_to_goal_dist_end":0.13264,"object_to_goal_dist_start":0.14326,"object_z_max":0.03758,"peak_contact_force":205.09115,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2900.0,"raw_peak_contact_force":650.96319,"tcp_end":[0.51382,0.07661,0.04664],"tcp_start":[0.51014,0.09102,0.05379],"tcp_to_object_dist_end":0.02699,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```