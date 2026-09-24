## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0809 | 0.60 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3150 | 0.68 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1157 | 0.53 | ❌ rejected |
| 8 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1538 | 0.61 | ❌ rejected |
| 7 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0682 | 0.45 | ❌ rejected |

**Proposal policy**: task_score is 0.60 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.081) — your mutation base

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

- **Composite score**: 0.081
- **task_score** (E): 0.596
- **fitness_score**: 0.461  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 1.00 | 1.00 | 0.2492 |
| engage_peg | 1.00 | 1.00 | 0.0340 |
| push_through_channel | 1.00 | 1.00 | 0.0994 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.491, 0.144, 0.059) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.531 | 2.127 |
| engage_peg | align | 1.00 / step_budget | (0.491, 0.144, 0.059)→(0.503, 0.125, 0.035) | (0.501, 0.099, 0.034)→(0.501, 0.095, 0.035) | 0.180→0.175 | 1.00 / 2.000 | 2.058 | 10.668 |
| push_through_channel | push | 1.00 / time_limit | (0.503, 0.125, 0.035)→(0.499, 0.026, 0.031) | (0.501, 0.095, 0.035)→(0.503, -0.004, 0.035) | 0.175→0.076 | 1.00 / 1.667 | 2.361 | 5.802 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.641
- alignment_error: None
- force_efficiency: 0.724
- terminal_score: 0.641
- phase_score: 0.436
- phase_breakdown.push_score: 0.223
- phase_breakdown.approach_score: 0.655
- phase_breakdown.contact_score: 0.855

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.518
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.641
- **Median Q (composite search score)**: 0.090
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.384


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51562,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.08474,"approach_behind_peg.lateral_offset":-0.00547,"engage_peg.align_lateral":0.00741,"engage_peg.align_speed":0.03511,"push_through_channel.push_distance":0.20502,"push_through_channel.push_speed":0.0597,"push_through_channel.push_time":15.03055},"optimized_scores":{"best_composite_score":0.13762,"best_fitness_score":0.51762,"best_task_score":0.64062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.50377,0.06514,0.00943],"force_p95":1.52504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.82444,"mean_force":0.95456,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.49737,0.10472,0.04597]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.50304,0.08351,0.04322],"force_p95":12.77061,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.57796,"mean_force":3.82579,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.50194,0.0954,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":883.0,"contact_point_centroid":[0.49886,0.00597,0.00992],"force_p95":4.1794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.57204,"mean_force":1.29726,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49918,0.04537,0.03086]},{"body_a":"attachment","body_b":"peg","contact_count":814.0,"contact_point_centroid":[0.49971,0.03087,0.03433],"force_p95":3.79698,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.20256,"mean_force":1.01536,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49913,0.04282,0.03081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":488.0,"contact_point_centroid":[0.50304,0.06751,0.00933],"force_p95":0.55986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56427,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49632,0.15833,0.17767]}],"total_contact_groups":5},"final_pose_error":0.10599,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50484,-0.03504,0.0354],"final_tcp_position":[0.49904,-0.00549,0.03074],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":13.82444,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54374,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":488.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49462,0.11474,0.05796],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":146.0,"n_steps_budget":720.0,"object_pos_end":[0.50314,0.06392,0.03499],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14405,"object_to_goal_dist_start":0.14762,"object_z_max":0.03544,"peak_contact_force":0.57756,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":155.0,"raw_peak_contact_force":13.82444,"subtask_id":"contact","tcp_end":[0.50288,0.09371,0.03525],"tcp_start":[0.49462,0.11474,0.05796],"tcp_to_object_dist_end":0.02979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50484,-0.03504,0.0354],"object_pos_start":[0.50314,0.06392,0.03499],"object_to_goal_dist_end":0.04546,"object_to_goal_dist_start":0.14405,"object_z_max":0.03541,"peak_contact_force":3.19811,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1697.0,"raw_peak_contact_force":5.57204,"subtask_id":"push","tcp_end":[0.49904,-0.00549,0.03074],"tcp_start":[0.50288,0.09371,0.03525],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.1478,"approach_behind_peg.lateral_offset":-0.00054,"engage_peg.align_lateral":0.00726,"engage_peg.align_speed":0.0283,"push_through_channel.push_distance":0.20562,"push_through_channel.push_speed":0.05997,"push_through_channel.push_time":6.46841},"optimized_scores":{"best_composite_score":0.09017,"best_fitness_score":0.47017,"best_task_score":0.63892},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":103.0,"contact_point_centroid":[0.50307,0.11019,0.00942],"force_p95":1.63971,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.14703,"mean_force":0.85543,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.50467,0.1475,0.04783]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50486,0.12882,0.03999],"force_p95":10.29618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.58409,"mean_force":4.97429,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.50534,0.14077,0.03989]},{"body_a":"attachment","body_b":"peg","contact_count":841.0,"contact_point_centroid":[0.50485,0.07527,0.04264],"force_p95":5.81949,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.68479,"mean_force":2.70954,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5019,0.08712,0.03333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":711.0,"contact_point_centroid":[0.50583,0.04256,0.00995],"force_p95":6.06438,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.18026,"mean_force":3.48193,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50198,0.08894,0.03342]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":432.0,"contact_point_centroid":[0.52502,0.05578,0.02433],"force_p95":1.81729,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.25268,"mean_force":0.76483,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50188,0.08517,0.03331]},{"body_a":"peg","body_b":"channel_base_body","contact_count":427.0,"contact_point_centroid":[0.50364,0.11166,0.00935],"force_p95":0.61803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56342,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50205,0.17751,0.17504]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49975,0.19977,0.29815]}],"total_contact_groups":7},"final_pose_error":0.10596,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50684,0.00955,0.0353],"final_tcp_position":[0.50177,0.03915,0.03327],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":12.14703,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11175,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54936,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":443.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50561,0.15526,0.05906],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":103.0,"n_steps_budget":780.0,"object_pos_end":[0.50499,0.10919,0.03466],"object_pos_start":[0.50369,0.11175,0.03383],"object_to_goal_dist_end":0.18933,"object_to_goal_dist_start":0.19188,"object_z_max":0.03454,"peak_contact_force":4.51143,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":110.0,"raw_peak_contact_force":12.14703,"subtask_id":"contact","tcp_end":[0.50564,0.13898,0.03787],"tcp_start":[0.50561,0.15526,0.05906],"tcp_to_object_dist_end":0.02997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,0.00955,0.0353],"object_pos_start":[0.50499,0.10919,0.03466],"object_to_goal_dist_end":0.08993,"object_to_goal_dist_start":0.18933,"object_z_max":0.03557,"peak_contact_force":3.3144,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1984.0,"raw_peak_contact_force":7.68479,"subtask_id":"push","tcp_end":[0.50177,0.03915,0.03327],"tcp_start":[0.50564,0.13898,0.03787],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69318,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.12694,"approach_behind_peg.lateral_offset":-0.01253,"engage_peg.align_lateral":0.01457,"engage_peg.align_speed":0.01057,"push_through_channel.push_distance":0.17947,"push_through_channel.push_speed":0.05903,"push_through_channel.push_time":16.71387},"optimized_scores":{"best_composite_score":0.01502,"best_fitness_score":0.39502,"best_task_score":0.50857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.49771,0.11355,0.00954],"force_p95":2.83035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.03229,"mean_force":0.78418,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.48516,0.15169,0.04492]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.49647,0.13387,0.04766],"force_p95":3.92926,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.88778,"mean_force":1.41945,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.49437,0.1457,0.03771]},{"body_a":"attachment","body_b":"peg","contact_count":835.0,"contact_point_centroid":[0.49656,0.07769,0.02874],"force_p95":1.06161,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.14829,"mean_force":0.56705,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49714,0.08963,0.02842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":899.0,"contact_point_centroid":[0.49513,0.05376,0.00994],"force_p95":1.48687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77705,"mean_force":0.84991,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49722,0.09142,0.0285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.49636,0.11906,0.00939],"force_p95":0.61014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56014,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.48563,0.17996,0.17373]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47483,0.10602,0.03515],"force_p95":0.90113,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2515,"mean_force":0.40496,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49847,0.13556,0.02984]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49924,0.19958,0.2962]}],"total_contact_groups":7},"final_pose_error":0.08099,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49646,0.01289,0.03495],"final_tcp_position":[0.49703,0.04293,0.0284],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":6.03229,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11907,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50067,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":452.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.47323,0.16174,0.05941],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.49555,0.1124,0.03471],"object_pos_start":[0.496,0.11907,0.03393],"object_to_goal_dist_end":0.19252,"object_to_goal_dist_start":0.1992,"object_z_max":0.03534,"peak_contact_force":1.08471,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":318.0,"raw_peak_contact_force":6.03229,"subtask_id":"contact","tcp_end":[0.50096,0.14164,0.033],"tcp_start":[0.47323,0.16174,0.05941],"tcp_to_object_dist_end":0.02978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49646,0.01289,0.03495],"object_pos_start":[0.49555,0.1124,0.03471],"object_to_goal_dist_end":0.09309,"object_to_goal_dist_start":0.19252,"object_z_max":0.03567,"peak_contact_force":0.569,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1796.0,"raw_peak_contact_force":4.14829,"subtask_id":"push","tcp_end":[0.49703,0.04293,0.0284],"tcp_start":[0.50096,0.14164,0.033],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```