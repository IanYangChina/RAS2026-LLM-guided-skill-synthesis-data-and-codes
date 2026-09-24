## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2538 | 0.22 | ✅ accepted |
| 2 | approach → approach → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2165 | 0.18 | ❌ rejected |
| 1 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.0205 | 0.07 | ❌ rejected |
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2439 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=0.254) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.05
  weight: 0.3
- id: reach_goal
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
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.05
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_approach
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
      distance: 0.05
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 2.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_goal
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
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
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
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.05], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.254
- **task_score** (E): 0.223
- **fitness_score**: 0.262  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2112 |
| contact_1 | 0.67 | 1.00 | 0.0398 |
| push_1 | 0.00 | 1.00 | 0.0740 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.105, 0.115) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.557 | 2.857 |
| contact_1 | contact | 0.67 / force_exceeded | (0.481, 0.105, 0.115)→(0.479, 0.065, 0.110) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 9.894 | 9.896 |
| push_1 | push | 0.00 / step_budget | (0.479, 0.065, 0.110)→(0.484, -0.008, 0.105) | (0.497, 0.079, 0.034)→(0.497, 0.036, 0.028) | 0.160→0.117 | 1.00 / 2.667 | 235.857 | 275.089 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.345
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.345
- phase_score: 0.261
- phase_breakdown.reach_goal_score: 0.035
- phase_breakdown.reach_approach_score: 0.788

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.295
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.345
- **Median Q (composite search score)**: 0.394
- **K-run variance**: 0.0404
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.174


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1371,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05233,"contact_1.contact_force":6.27385,"push_1.push_distance":0.16599,"push_1.push_speed":0.02686},"optimized_scores":{"best_composite_score":0.39796,"best_fitness_score":0.29463,"best_task_score":0.34497},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":943.0,"contact_point_centroid":[0.52502,0.11993,0.05997],"force_p95":188.25731,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.99595,"mean_force":181.97955,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49388,0.07714,0.09634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50246,0.06374,0.00826],"force_p95":27.12207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.59673,"mean_force":3.55855,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49394,0.07769,0.09632]},{"body_a":"peg","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.50174,0.12606,0.06042],"force_p95":62.36897,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.17193,"mean_force":49.68074,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49503,0.08634,0.09573]},{"body_a":"peg","body_b":"channel_base_body","contact_count":494.0,"contact_point_centroid":[0.50081,0.11602,0.00942],"force_p95":0.61291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.08912,"mean_force":0.57404,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4956,0.11446,0.0967]},{"body_a":"peg","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50184,0.13385,0.05888],"force_p95":8.98852,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.58296,"mean_force":5.24063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49532,0.09292,0.09636]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52511,0.08326,0.02432],"force_p95":7.91792,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.22004,"mean_force":2.57369,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49414,0.07709,0.09587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.50096,0.11601,0.00939],"force_p95":0.61996,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55545,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49532,0.17522,0.19797]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47491,0.06271,0.05424],"force_p95":1.2514,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28746,"mean_force":0.93371,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4944,0.07683,0.09573]}],"total_contact_groups":8},"final_pose_error":0.15079,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50167,0.06084,0.02412],"final_tcp_position":[0.49331,0.07733,0.0969],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":199.99595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11626,0.03391],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19636,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.57667,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":655.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_approach","tcp_end":[0.49822,0.13872,0.10127],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":494.0,"n_steps_budget":600.0,"object_pos_end":[0.50082,0.11574,0.03385],"object_pos_start":[0.50096,0.11626,0.03391],"object_to_goal_dist_end":0.19584,"object_to_goal_dist_start":0.19636,"object_z_max":0.03397,"peak_contact_force":10.08912,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":497.0,"raw_peak_contact_force":10.08912,"subtask_id":"reach_goal","tcp_end":[0.49532,0.09254,0.09636],"tcp_start":[0.49822,0.13872,0.10127],"tcp_to_object_dist_end":0.0669,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50167,0.06084,0.02412],"object_pos_start":[0.50082,0.11574,0.03385],"object_to_goal_dist_end":0.14174,"object_to_goal_dist_start":0.19584,"object_z_max":0.04072,"peak_contact_force":181.75616,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2004.0,"raw_peak_contact_force":199.99595,"subtask_id":"reach_goal","tcp_end":[0.49331,0.07733,0.0969],"tcp_start":[0.49532,0.09254,0.09636],"tcp_to_object_dist_end":0.07508,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98718,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07071,"contact_1.contact_force":4.20695,"push_1.push_distance":0.14709,"push_1.push_speed":0.01937},"optimized_scores":{"best_composite_score":0.39381,"best_fitness_score":0.29048,"best_task_score":0.31801},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":333.0,"contact_point_centroid":[0.52503,0.11999,0.05992],"force_p95":344.66543,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.55176,"mean_force":308.57226,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47851,-0.02284,0.11411]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":501.0,"contact_point_centroid":[0.47498,0.11433,0.05997],"force_p95":213.06994,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.05111,"mean_force":175.44371,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47816,0.05778,0.11377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.49673,0.03616,0.00907],"force_p95":89.45592,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.45941,"mean_force":13.48038,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47837,0.02374,0.11393]},{"body_a":"peg","body_b":"link7","contact_count":178.0,"contact_point_centroid":[0.49296,0.05168,0.06273],"force_p95":94.02121,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.00415,"mean_force":71.73521,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47854,0.00231,0.11415]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11999,0.05999],"force_p95":19.0453,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.0453,"mean_force":19.0453,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47699,0.06517,0.11398]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47499,-0.00513,0.02443],"force_p95":9.35535,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.45448,"mean_force":3.8175,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47879,-0.02335,0.1138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":684.0,"contact_point_centroid":[0.49536,0.06379,0.00938],"force_p95":0.56617,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.558,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48663,0.1514,0.20481]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50415,0.21543,0.29305]},{"body_a":"peg","body_b":"channel_base_body","contact_count":251.0,"contact_point_centroid":[0.49492,0.06389,0.0094],"force_p95":0.55037,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54533,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47746,0.07666,0.1147]}],"total_contact_groups":9},"final_pose_error":0.0585,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49334,-0.00982,0.02433],"final_tcp_position":[0.47891,-0.02354,0.1137],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":345.55176,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.49533,0.06394,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54933,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":712.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_approach","tcp_end":[0.47967,0.08998,0.11836],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":251.0,"n_steps_budget":600.0,"object_pos_end":[0.49535,0.06376,0.03401],"object_pos_start":[0.49533,0.06394,0.03397],"object_to_goal_dist_end":0.14396,"object_to_goal_dist_start":0.14414,"object_z_max":0.03401,"peak_contact_force":19.0453,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":252.0,"raw_peak_contact_force":19.0453,"subtask_id":"reach_goal","tcp_end":[0.47699,0.06509,0.11398],"tcp_start":[0.47967,0.08998,0.11836],"tcp_to_object_dist_end":0.08207,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49334,-0.00982,0.02433],"object_pos_start":[0.49535,0.06376,0.03401],"object_to_goal_dist_end":0.07222,"object_to_goal_dist_start":0.14396,"object_z_max":0.04029,"peak_contact_force":344.05382,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2018.0,"raw_peak_contact_force":345.55176,"subtask_id":"reach_goal","tcp_end":[0.47891,-0.02354,0.1137],"tcp_start":[0.47699,0.06509,0.11398],"tcp_to_object_dist_end":0.09156,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07101,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07734,"contact_1.contact_force":7.78927,"push_1.push_distance":0.16801,"push_1.push_speed":0.02381},"optimized_scores":{"best_composite_score":-0.03044,"best_fitness_score":0.19956,"best_task_score":0.00522},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":605.0,"contact_point_centroid":[0.52501,0.10953,0.05996],"force_p95":232.54384,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.71864,"mean_force":192.08834,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47275,-0.06664,0.11289]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":745.0,"contact_point_centroid":[0.47473,0.00283,0.05999],"force_p95":168.25679,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.0018,"mean_force":108.55671,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47043,-0.05362,0.11503]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49723,0.05841,0.00947],"force_p95":10.16531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.34049,"mean_force":2.49169,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46976,-0.04665,0.11542]},{"body_a":"peg","body_b":"link6","contact_count":195.0,"contact_point_centroid":[0.50596,0.06601,0.05934],"force_p95":12.37712,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.13406,"mean_force":10.05823,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47738,-0.07525,0.10597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":682.0,"contact_point_centroid":[0.49436,0.05903,0.00936],"force_p95":0.56012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56764,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48047,0.149,0.20759]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50268,0.22086,0.2877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":507.0,"contact_point_centroid":[0.49402,0.05876,0.00939],"force_p95":0.55019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54583,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46423,0.0606,0.1209]}],"total_contact_groups":7},"final_pose_error":0.05647,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49559,0.05621,0.03472],"final_tcp_position":[0.47868,-0.07777,0.10416],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":279.71864,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.49399,0.059,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54364,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":717.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_approach","tcp_end":[0.46659,0.08533,0.12468],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":507.0,"n_steps_budget":600.0,"object_pos_end":[0.49433,0.05889,0.03396],"object_pos_start":[0.49399,0.059,0.03389],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13926,"object_z_max":0.03396,"peak_contact_force":0.5468,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":507.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_goal","tcp_end":[0.46398,0.03824,0.12059],"tcp_start":[0.46659,0.08533,0.12468],"tcp_to_object_dist_end":0.09409,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49559,0.05621,0.03472],"object_pos_start":[0.49433,0.05889,0.03396],"object_to_goal_dist_end":0.13638,"object_to_goal_dist_start":0.13913,"object_z_max":0.03491,"peak_contact_force":181.76146,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2545.0,"raw_peak_contact_force":279.71864,"subtask_id":"reach_goal","tcp_end":[0.47868,-0.07777,0.10416],"tcp_start":[0.46398,0.03824,0.12059],"tcp_to_object_dist_end":0.15185,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```