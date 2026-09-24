## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1875 | 0.10 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1580 | 0.29 | ❌ rejected |
| 10 | descend → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1612 | 0.43 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0476 | 0.00 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0242 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.188) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: push_complete
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: pre_contact
- id: push_1
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
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.09
      - 0.18
      default: 0.16
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
  subtask_id: push_complete
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.188
- **task_score** (E): 0.095
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2007 |
| descend_1 | 1.00 | 1.00 | 0.0877 |
| push_1 | 0.67 | 1.00 | 0.0561 |
| retract_1 | 1.00 | 1.00 | 0.1387 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.105, 0.127) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.540 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.105, 0.127)→(0.503, 0.101, 0.041) | (0.503, 0.080, 0.034)→(0.498, 0.077, 0.033) | 0.160→0.157 | 1.00 / 1.000 | 0.523 | 294.209 |
| push_1 | push | 0.67 / force_exceeded | (0.503, 0.101, 0.041)→(0.499, 0.045, 0.037) | (0.498, 0.077, 0.033)→(0.498, 0.029, 0.023) | 0.157→0.111 | 1.00 / 2.333 | 2612.557 | 6.942 |
| retract_1 | retract | 1.00 / step_budget | (0.499, 0.045, 0.037)→(0.497, 0.045, 0.175) | (0.498, 0.029, 0.023)→(0.510, 0.028, 0.021) | 0.111→0.112 | 1.00 / 1.000 | 0.612 | 18.060 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.783
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.206
- phase_score: 0.766
- phase_breakdown.pre_contact_score: 0.651
- phase_breakdown.push_complete_score: 0.815

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.542
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.206
- **Median Q (composite search score)**: 0.097
- **K-run variance**: 0.0455
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.460


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81176,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14016,"descend_1.descend_speed":0.11103,"push_1.force_threshold":23.57191,"push_1.push_distance":0.12437,"push_1.push_speed":0.04361},"optimized_scores":{"best_composite_score":0.09747,"best_fitness_score":0.15747,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":845.0,"contact_point_centroid":[0.51114,0.15902,-0.00192],"force_p95":0.68378,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.01865,"mean_force":0.70739,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48651,0.13553,0.10207]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50074,0.13608,0.03272],"force_p95":26.34181,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.09219,"mean_force":4.64495,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48887,0.13593,0.03438]},{"body_a":"peg","body_b":"world","contact_count":294.0,"contact_point_centroid":[0.49702,0.15708,-0.00174],"force_p95":0.89354,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.89638,"mean_force":0.6209,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48854,0.13983,0.06053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":502.0,"contact_point_centroid":[0.49634,0.11916,0.0094],"force_p95":0.61689,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55739,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49122,0.17028,0.21051]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4995,0.19895,0.29759]},{"body_a":"peg","body_b":"world","contact_count":26.0,"contact_point_centroid":[0.49957,0.15808,-0.00199],"force_p95":0.72585,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72585,"mean_force":0.61182,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49042,0.1379,0.03463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.49541,0.11993,0.00942],"force_p95":0.59702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60051,"mean_force":0.51994,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48404,0.14142,0.10648]}],"total_contact_groups":7},"final_pose_error":0.0118,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5344,0.15821,0.01412],"final_tcp_position":[0.48682,0.13564,0.17223],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3921.01344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":870.0,"object_pos_end":[0.49601,0.11987,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.2,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52047,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":526.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48429,0.14276,0.12904],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.49932,0.15997,0.01409],"object_pos_start":[0.49601,0.11987,0.03385],"object_to_goal_dist_end":0.24136,"object_to_goal_dist_start":0.2,"object_z_max":0.03386,"peak_contact_force":0.49899,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":518.0,"raw_peak_contact_force":2.89638,"subtask_id":"pre_contact","tcp_end":[0.49133,0.13901,0.03574],"tcp_start":[0.48429,0.14276,0.12904],"tcp_to_object_dist_end":0.03118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.49996,0.15995,0.01409],"object_pos_start":[0.49932,0.15997,0.01409],"object_to_goal_dist_end":0.24135,"object_to_goal_dist_start":0.24136,"object_z_max":0.01409,"peak_contact_force":3921.01344,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":0.72585,"subtask_id":"push_complete","tcp_end":[0.48962,0.13639,0.03367],"tcp_start":[0.49133,0.13901,0.03574],"tcp_to_object_dist_end":0.03233,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.5344,0.15821,0.01412],"object_pos_start":[0.49996,0.15995,0.01409],"object_to_goal_dist_end":0.24207,"object_to_goal_dist_start":0.24135,"object_z_max":0.01607,"peak_contact_force":0.68378,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":864.0,"raw_peak_contact_force":42.01865,"tcp_end":[0.48682,0.13564,0.17223],"tcp_start":[0.48962,0.13639,0.03367],"tcp_to_object_dist_end":0.16666,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07339,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.21682,"descend_1.descend_speed":0.08966,"push_1.force_threshold":29.66196,"push_1.push_distance":0.13449,"push_1.push_speed":0.07599},"optimized_scores":{"best_composite_score":0.48196,"best_fitness_score":0.54196,"best_task_score":0.20609},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":49.0,"contact_point_centroid":[0.52513,0.08515,0.05998],"force_p95":384.1995,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.67167,"mean_force":255.7952,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5122,0.08525,0.05212]},{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.50899,0.06543,0.00912],"force_p95":133.40595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.28458,"mean_force":31.75097,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51428,0.08619,0.07993]},{"body_a":"attachment","body_b":"peg","contact_count":129.0,"contact_point_centroid":[0.51769,0.07561,0.05515],"force_p95":136.18993,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.77552,"mean_force":104.11812,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51096,0.08492,0.05438]},{"body_a":"attachment","body_b":"peg","contact_count":588.0,"contact_point_centroid":[0.50237,0.00549,0.03894],"force_p95":5.29208,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.25463,"mean_force":1.45087,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50466,0.01723,0.03871]},{"body_a":"peg","body_b":"channel_base_body","contact_count":862.0,"contact_point_centroid":[0.49708,-0.01437,0.00947],"force_p95":3.16081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.06036,"mean_force":1.04288,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50474,0.02821,0.0388]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":164.0,"contact_point_centroid":[0.47497,-0.03434,0.02909],"force_p95":4.80856,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.98296,"mean_force":2.82732,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50488,0.02419,0.03898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":872.0,"contact_point_centroid":[0.50026,-0.0632,0.00814],"force_p95":0.72981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.90144,"mean_force":0.64272,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50145,-0.02593,0.10739]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52501,-0.04261,0.02439],"force_p95":5.63478,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.76037,"mean_force":3.09634,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50112,-0.02591,0.07352]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,-0.08334,0.02517],"force_p95":5.03854,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.59558,"mean_force":2.08272,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50242,-0.02594,0.13553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":559.0,"contact_point_centroid":[0.50577,0.06303,0.00936],"force_p95":0.56528,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57077,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51207,0.14207,0.20731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50009,0.19733,0.29562]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50238,-0.0378,0.03892],"force_p95":1.70754,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.70754,"mean_force":1.70754,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50467,-0.02604,0.03871]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52526,0.04244,0.03441],"force_p95":1.09896,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33671,"mean_force":0.41503,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50653,0.08198,0.04102]}],"total_contact_groups":13},"final_pose_error":0.01159,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49791,-0.06239,0.02434],"final_tcp_position":[0.50179,-0.02591,0.17748],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3914.81606,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":587.0,"n_steps_budget":660.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55105,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":593.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52463,0.08935,0.12557],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":438.0,"n_steps_budget":660.0,"object_pos_end":[0.49814,0.03639,0.04293],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.11644,"object_to_goal_dist_start":0.14321,"object_z_max":0.04282,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":608.0,"raw_peak_contact_force":423.67167,"subtask_id":"pre_contact","tcp_end":[0.50851,0.08488,0.0434],"tcp_start":[0.52463,0.08935,0.12557],"tcp_to_object_dist_end":0.04959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.49745,-0.06229,0.02803],"object_pos_start":[0.49814,0.03639,0.04293],"object_to_goal_dist_end":0.02152,"object_to_goal_dist_start":0.11644,"object_z_max":0.04304,"peak_contact_force":3914.81606,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1637.0,"raw_peak_contact_force":10.25463,"subtask_id":"push_complete","tcp_end":[0.50467,-0.02604,0.03871],"tcp_start":[0.50851,0.08488,0.0434],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.49791,-0.06239,0.02434],"object_pos_start":[0.49745,-0.06229,0.02803],"object_to_goal_dist_end":0.02365,"object_to_goal_dist_start":0.02152,"object_z_max":0.02803,"peak_contact_force":0.54766,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":888.0,"raw_peak_contact_force":5.90144,"tcp_end":[0.50179,-0.02591,0.17748],"tcp_start":[0.50467,-0.02604,0.03871],"tcp_to_object_dist_end":0.15748,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80328,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16536,"descend_1.descend_speed":0.08101,"push_1.force_threshold":15.0035,"push_1.push_distance":0.16298,"push_1.push_speed":0.03023},"optimized_scores":{"best_composite_score":-0.01684,"best_fitness_score":0.29316,"best_task_score":0.08013},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":90.0,"contact_point_centroid":[0.52509,0.07884,0.05999],"force_p95":380.40289,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.05995,"mean_force":284.14652,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51228,0.07891,0.05365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.50878,0.05889,0.00914],"force_p95":113.7809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.31486,"mean_force":29.90902,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51734,0.07992,0.07863]},{"body_a":"attachment","body_b":"peg","contact_count":142.0,"contact_point_centroid":[0.51768,0.06866,0.05556],"force_p95":118.47879,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.20359,"mean_force":92.96443,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51196,0.07869,0.05482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.49723,0.00564,0.00853],"force_p95":1.96347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.84568,"mean_force":0.854,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50426,0.05003,0.03796]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":109.0,"contact_point_centroid":[0.47496,-0.01994,0.02837],"force_p95":5.26612,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.42541,"mean_force":2.20014,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50441,0.04055,0.03816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":844.0,"contact_point_centroid":[0.49948,-0.01212,0.00803],"force_p95":0.77015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.25929,"mean_force":0.61252,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50094,0.02509,0.10634]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52503,0.00914,0.02425],"force_p95":4.72974,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.15124,"mean_force":1.33997,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50076,0.02507,0.05539]},{"body_a":"attachment","body_b":"peg","contact_count":249.0,"contact_point_centroid":[0.50332,0.02425,0.03895],"force_p95":1.90549,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.66548,"mean_force":0.79544,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50413,0.03618,0.03783]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,-0.0331,0.02508],"force_p95":4.3525,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.55689,"mean_force":2.51307,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5026,0.02519,0.09636]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50076,0.01328,0.04058],"force_p95":1.57262,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.4932,"mean_force":0.32094,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50267,0.02509,0.04039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":607.0,"contact_point_centroid":[0.50592,0.05663,0.00936],"force_p95":0.60127,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57271,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51539,0.13898,0.20723]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50017,0.19727,0.29562]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52506,0.0358,0.02714],"force_p95":2.39649,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.56913,"mean_force":0.73124,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50539,0.07424,0.03931]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47483,0.02042,0.05599],"force_p95":1.29546,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30729,"mean_force":1.18899,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50825,0.0786,0.04298]}],"total_contact_groups":14},"final_pose_error":0.01178,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.498,-0.01178,0.02414],"final_tcp_position":[0.50126,0.02513,0.17642],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":456.05995,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":636.0,"n_steps_budget":840.0,"object_pos_end":[0.50613,0.0566,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54763,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":644.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53112,0.08312,0.12501],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":750.0,"object_pos_end":[0.49727,0.03353,0.0407],"object_pos_start":[0.50613,0.0566,0.03379],"object_to_goal_dist_end":0.11356,"object_to_goal_dist_start":0.13688,"object_z_max":0.04087,"peak_contact_force":1.07068,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":683.0,"raw_peak_contact_force":456.05995,"subtask_id":"pre_contact","tcp_end":[0.50806,0.07852,0.04256],"tcp_start":[0.53112,0.08312,0.12501],"tcp_to_object_dist_end":0.0463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49676,-0.01105,0.02598],"object_pos_start":[0.49727,0.03353,0.0407],"object_to_goal_dist_end":0.07043,"object_to_goal_dist_start":0.11356,"object_z_max":0.0407,"peak_contact_force":1.84216,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1352.0,"raw_peak_contact_force":9.84568,"subtask_id":"push_complete","tcp_end":[0.50413,0.02528,0.03784],"tcp_start":[0.50806,0.07852,0.04256],"tcp_to_object_dist_end":0.03892,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":930.0,"object_pos_end":[0.498,-0.01178,0.02414],"object_pos_start":[0.49676,-0.01105,0.02598],"object_to_goal_dist_end":0.07007,"object_to_goal_dist_start":0.07043,"object_z_max":0.02599,"peak_contact_force":0.60398,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":866.0,"raw_peak_contact_force":6.25929,"tcp_end":[0.50126,0.02513,0.17642],"tcp_start":[0.50413,0.02528,0.03784],"tcp_to_object_dist_end":0.15672,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```