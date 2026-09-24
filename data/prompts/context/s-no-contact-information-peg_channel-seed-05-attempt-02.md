## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2253 | 0.23 | ❌ rejected |
| 1 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2268 | 0.23 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=0.225) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - -0.01
  - 0.0
  weight: 0.2
- id: push_through
  weight: 0.8
phases:
- id: approach_tcp
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - -0.01
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through
- id: retract_away
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_tcp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.01, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_away** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.225
- **task_score** (E): 0.230
- **fitness_score**: 0.405  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_tcp | 1.00 | 0.2695 |
| push_channel | 0.67 | 0.1160 |
| retract_away | 1.00 | 0.0901 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_tcp | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.091, 0.055) | (0.512, 0.095, 0.040)→(0.506, 0.093, 0.032) | 0.175→0.173 |
| push_channel | push | 0.67 / step_budget | (0.514, 0.091, 0.055)→(0.505, -0.024, 0.045) | (0.506, 0.093, 0.032)→(0.502, 0.059, 0.028) | 0.173→0.140 |
| retract_away | retract | 1.00 / step_budget | (0.505, -0.024, 0.045)→(0.502, -0.024, 0.135) | (0.502, 0.059, 0.028)→(0.504, 0.058, 0.027) | 0.140→0.139 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.339
- alignment_error: None
- terminal_score: 0.339
- phase_score: 0.697
- phase_breakdown.approach_peg_score: 0.785
- phase_breakdown.push_through_score: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.554
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.350
- **Median Q (composite search score)**: 0.374
- **K-run variance**: 0.0440
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: approach_tcp.approach_speed
- **Final σ (mean)**: 0.388


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48428,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_tcp.approach_speed":0.06702,"push_channel.push_speed":0.06962,"retract_away.retract_speed":0.06485},"optimized_scores":{"best_composite_score":-0.07146,"best_fitness_score":0.10854,"best_task_score":0.00027},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":145.0,"contact_point_centroid":[0.53227,0.10368,0.05984],"force_p95":452.53688,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.52104,"mean_force":416.91536,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.5204,0.1042,0.06133]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":965.0,"contact_point_centroid":[0.53107,0.06166,0.05996],"force_p95":244.97312,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.41488,"mean_force":200.09886,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51951,0.06402,0.06136]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52931,0.04376,0.05998],"force_p95":108.65558,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.15906,"mean_force":67.02081,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51895,0.04967,0.06124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.51022,0.14377,0.15875]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.49977,0.19856,0.29671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50587,0.10463,0.00939],"force_p95":0.57567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57575,"mean_force":0.54634,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51955,0.06471,0.06137]},{"body_a":"peg","body_b":"channel_base_body","contact_count":837.0,"contact_point_centroid":[0.50595,0.10459,0.00939],"force_p95":0.57559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57564,"mean_force":0.54631,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51576,0.04939,0.10669]}],"total_contact_groups":7},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50585,0.10455,0.03384],"final_tcp_position":[0.51588,0.0494,0.15171],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_tcp","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.52199,0.10413,0.06161],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03205,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.10467,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.51895,0.04963,0.06122],"tcp_start":[0.52199,0.10413,0.06161],"tcp_to_object_dist_end":0.06283,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":837.0,"n_steps_budget":960.0,"object_pos_end":[0.50585,0.10455,0.03384],"object_pos_start":[0.50598,0.10467,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51588,0.0494,0.15171],"tcp_start":[0.51895,0.04963,0.06122],"tcp_to_object_dist_end":0.13053,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55556,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_tcp.approach_speed":0.09988,"push_channel.push_speed":0.05705,"retract_away.retract_speed":0.09536},"optimized_scores":{"best_composite_score":0.3739,"best_fitness_score":0.5539,"best_task_score":0.3392},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":932.0,"contact_point_centroid":[0.50438,0.06691,0.00926],"force_p95":119.48807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.86917,"mean_force":11.23522,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.49909,0.12785,0.16538]},{"body_a":"attachment","body_b":"peg","contact_count":84.0,"contact_point_centroid":[0.51443,0.06584,0.05479],"force_p95":164.70584,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.31525,"mean_force":118.53487,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.50255,0.06669,0.05447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.50566,0.03373,0.00848],"force_p95":137.23933,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.25693,"mean_force":66.3268,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50559,0.00742,0.04736]},{"body_a":"attachment","body_b":"peg","contact_count":222.0,"contact_point_centroid":[0.51427,0.03871,0.05294],"force_p95":137.57839,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.67591,"mean_force":101.31705,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50866,0.03068,0.05131]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":77.0,"contact_point_centroid":[0.52509,0.05647,0.05659],"force_p95":15.40319,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.72315,"mean_force":12.4039,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50913,0.04845,0.05256]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47491,-0.00991,0.02432],"force_p95":8.77126,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.82594,"mean_force":3.57019,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49972,-0.03362,0.03991]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49657,0.01353,0.00802],"force_p95":0.72555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73106,"mean_force":0.60571,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49433,-0.06049,0.08077]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,-0.01048,0.02423],"force_p95":0.38528,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38528,"mean_force":0.38528,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49424,-0.0605,0.05378]}],"total_contact_groups":8},"final_pose_error":0.01143,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50001,0.01319,0.02409],"final_tcp_position":[0.4944,-0.06038,0.12601],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"phases":[{"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.5062,0.06391,0.02942],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14443,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"phase_name":"approach_tcp","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.50619,0.06315,0.05021],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.02081,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.49436,0.01347,0.02412],"object_pos_start":[0.5062,0.06391,0.02942],"object_to_goal_dist_end":0.09498,"object_to_goal_dist_start":0.14443,"object_z_max":0.0396,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.49758,-0.06073,0.03699],"tcp_start":[0.50619,0.06315,0.05021],"tcp_to_object_dist_end":0.07538,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50001,0.01319,0.02409],"object_pos_start":[0.49436,0.01347,0.02412],"object_to_goal_dist_end":0.09454,"object_to_goal_dist_start":0.09498,"object_z_max":0.02417,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.4944,-0.06038,0.12601],"tcp_start":[0.49758,-0.06073,0.03699],"tcp_to_object_dist_end":0.12582,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34595,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_tcp.approach_speed":0.1,"push_channel.push_speed":0.03974,"retract_away.retract_speed":0.06472},"optimized_scores":{"best_composite_score":0.37352,"best_fitness_score":0.55352,"best_task_score":0.34968},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52526,0.10663,0.05997],"force_p95":282.42927,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.32672,"mean_force":199.62865,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.51256,0.10675,0.05224]},{"body_a":"attachment","body_b":"peg","contact_count":74.0,"contact_point_centroid":[0.52131,0.10859,0.0556],"force_p95":153.01278,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.95407,"mean_force":119.87085,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.50932,0.10818,0.0552]},{"body_a":"peg","body_b":"channel_base_body","contact_count":846.0,"contact_point_centroid":[0.50516,0.11121,0.00933],"force_p95":118.69695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":153.59744,"mean_force":10.89383,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.50259,0.14995,0.16534]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.50553,0.0784,0.00852],"force_p95":122.92758,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.10753,"mean_force":50.61945,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50703,0.03675,0.04656]},{"body_a":"attachment","body_b":"peg","contact_count":265.0,"contact_point_centroid":[0.51558,0.09113,0.05401],"force_p95":125.20973,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.63456,"mean_force":96.25349,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51185,0.08133,0.05224]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":144.0,"contact_point_centroid":[0.52505,0.09175,0.05999],"force_p95":122.40802,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.99063,"mean_force":78.84776,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51228,0.09188,0.05294]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":46.0,"contact_point_centroid":[0.52552,0.11064,0.04687],"force_p95":19.78105,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.5071,"mean_force":6.7558,"phase_index":0.0,"phase_name":"approach_tcp","phase_type":"approach","tcp_position_centroid":[0.50763,0.13911,0.13842]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47492,0.08371,0.02769],"force_p95":11.80641,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.44763,"mean_force":2.4206,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.505,0.02335,0.0435]},{"body_a":"peg","body_b":"channel_base_body","contact_count":817.0,"contact_point_centroid":[0.50557,0.05767,0.00813],"force_p95":0.77891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.79733,"mean_force":0.81764,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49448,-0.06012,0.08187]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":55.0,"contact_point_centroid":[0.525,0.03341,0.02451],"force_p95":8.13847,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.34853,"mean_force":3.57086,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4947,-0.06026,0.0716]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52504,0.0609,0.03499],"force_p95":7.72106,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.22186,"mean_force":1.8722,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50322,0.00061,0.04211]}],"total_contact_groups":11},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50481,0.05526,0.02413],"final_tcp_position":[0.49462,-0.06004,0.12714],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"phases":[{"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,0.11028,0.03271],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19049,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"phase_name":"approach_tcp","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.51293,0.10673,0.05205],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.02103,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,0.05976,0.02487],"object_pos_start":[0.50547,0.11028,0.03271],"object_to_goal_dist_end":0.14069,"object_to_goal_dist_start":0.19049,"object_z_max":0.03989,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.49782,-0.06041,0.0366],"tcp_start":[0.51293,0.10673,0.05205],"tcp_to_object_dist_end":0.121,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":817.0,"n_steps_budget":960.0,"object_pos_end":[0.50481,0.05526,0.02413],"object_pos_start":[0.50571,0.05976,0.02487],"object_to_goal_dist_end":0.13627,"object_to_goal_dist_start":0.14069,"object_z_max":0.02489,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49462,-0.06004,0.12714],"tcp_start":[0.49782,-0.06041,0.0366],"tcp_to_object_dist_end":0.15495,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```