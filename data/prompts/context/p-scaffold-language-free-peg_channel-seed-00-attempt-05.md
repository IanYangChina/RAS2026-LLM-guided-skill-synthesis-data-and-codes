## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0554 | 0.77 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2295 | 0.81 | ❌ rejected |
| 3 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 10 | -0.5097 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 12 | -0.5676 | 0.01 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2471 | 0.78 | ❌ rejected |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.833, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
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

## Current Skill (Q=-0.055) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.055
- **task_score** (E): 0.768
- **fitness_score**: 0.385  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1148 |
| approach_1 | 1.00 | 1.00 | 0.1700 |
| contact_1 | 0.00 | 1.00 | 0.0319 |
| push_1 | 0.00 | 1.00 | 0.0666 |
| retract_1 | 1.00 | 1.00 | 0.1007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.501, 0.118, 0.221) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.566 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.501, 0.118, 0.221)→(0.496, 0.100, 0.052) | (0.500, 0.081, 0.034)→(0.501, 0.071, 0.040) | 0.161→0.151 | 1.00 / 1.000 | 0.336 | 16.150 |
| contact_1 | contact | 0.00 / step_budget | (0.496, 0.100, 0.052)→(0.497, 0.073, 0.036) | (0.501, 0.071, 0.040)→(0.497, 0.036, 0.025) | 0.151→0.117 | 1.00 / 1.667 | 0.792 | 8.094 |
| push_1 | push | 0.00 / step_budget | (0.497, 0.073, 0.036)→(0.534, 0.048, 0.084) | (0.497, 0.036, 0.025)→(0.500, -0.064, 0.031) | 0.117→0.021 | 1.00 / 2.667 | 425.340 | 2279.271 |
| retract_1 | retract | 1.00 / step_budget | (0.534, 0.048, 0.084)→(0.515, -0.035, 0.131) | (0.500, -0.064, 0.031)→(0.499, -0.064, 0.031) | 0.021→0.021 | 1.00 / 1.000 | 0.554 | 401.698 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.101
- phase_breakdown.reach_peg_score: 0.124
- phase_breakdown.reach_goal_score: 0.091

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.461
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.064
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.263


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.505,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00589,"approach_1.approach_arc_height":0.08916,"contact_1.contact_force_threshold":13.60272,"push_1.push_distance":0.09047,"push_1.push_speed":0.05178,"retract_1.retract_height":0.09,"retract_1.retract_speed":0.04698},"optimized_scores":{"best_composite_score":-0.064,"best_fitness_score":0.376,"best_task_score":0.72828},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":953.0,"contact_point_centroid":[0.53321,0.09467,0.05991],"force_p95":441.32913,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2301.06875,"mean_force":395.79182,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53279,0.02865,0.09809]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52609,0.03732,0.05977],"force_p95":2171.08456,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2213.56793,"mean_force":954.0941,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50862,0.0314,0.03114]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.5381,0.09235,0.05995],"force_p95":79.11115,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.54394,"mean_force":60.13138,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54317,0.02551,0.10071]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50355,0.03834,0.03494],"force_p95":22.25181,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.36583,"mean_force":14.11047,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50386,0.05014,0.03409]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47488,-0.00983,0.02541],"force_p95":17.88058,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.90093,"mean_force":17.69744,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50342,0.05073,0.0343]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.50391,0.06075,0.00939],"force_p95":0.58146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.31897,"mean_force":0.65392,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50525,0.13109,0.12865]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50218,0.07859,0.05635],"force_p95":16.43051,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.13484,"mean_force":12.99208,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50043,0.0904,0.05213]},{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.50475,-0.07243,0.00816],"force_p95":0.80487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.84335,"mean_force":0.74451,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53333,0.02899,0.09903]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.49809,0.0224,0.00843],"force_p95":0.79263,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.53314,"mean_force":0.62513,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49926,0.06522,0.0407]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.52512,-0.06475,0.02843],"force_p95":9.02162,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.45919,"mean_force":1.47657,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51766,0.02843,0.08151]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47499,-0.00734,0.02419],"force_p95":7.35119,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0835,"mean_force":2.11044,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49991,0.05829,0.03742]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50114,0.04231,0.0404],"force_p95":2.3012,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.66726,"mean_force":0.74498,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5005,0.05425,0.03581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":102.0,"contact_point_centroid":[0.50296,0.06152,0.0092],"force_p95":1.02314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.62549,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50655,0.14561,0.25318]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.51402,-0.10051,0.02367],"force_p95":1.33386,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73261,"mean_force":0.35219,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51861,0.02887,0.08626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.50313,-0.07389,0.00807],"force_p95":0.64358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64358,"mean_force":0.60592,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53354,0.00133,0.11078]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50013,0.19726,0.29774]}],"total_contact_groups":17},"final_pose_error":0.04951,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50295,-0.07387,0.02415],"final_tcp_position":[0.51976,-0.03538,0.12166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":2301.06875,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.0616,0.03377],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.57925,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":121.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.51175,0.10194,0.21731],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.50482,0.0523,0.03958],"object_pos_start":[0.50378,0.0616,0.03377],"object_to_goal_dist_end":0.13239,"object_to_goal_dist_start":0.14178,"object_z_max":0.03943,"peak_contact_force":0.35886,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":17.31897,"subtask_id":"reach_peg","tcp_end":[0.50039,0.08102,0.05092],"tcp_start":[0.51175,0.10194,0.21731],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":431.0,"n_steps_budget":600.0,"object_pos_end":[0.49342,0.0173,0.02426],"object_pos_start":[0.50482,0.0523,0.03958],"object_to_goal_dist_end":0.09878,"object_to_goal_dist_start":0.13239,"object_z_max":0.04078,"peak_contact_force":0.43766,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":430.0,"raw_peak_contact_force":9.53314,"subtask_id":"reach_peg","tcp_end":[0.50052,0.05415,0.03577],"tcp_start":[0.50039,0.08102,0.05092],"tcp_to_object_dist_end":0.03926,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50331,-0.07388,0.02415],"object_pos_start":[0.49342,0.0173,0.02426],"object_to_goal_dist_end":0.01731,"object_to_goal_dist_start":0.09878,"object_z_max":0.03344,"peak_contact_force":344.38891,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2038.0,"raw_peak_contact_force":2301.06875,"subtask_id":"reach_goal","tcp_end":[0.54317,0.02559,0.10064],"tcp_start":[0.50052,0.05415,0.03577],"tcp_to_object_dist_end":0.13165,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.50295,-0.07387,0.02415],"object_pos_start":[0.50331,-0.07388,0.02415],"object_to_goal_dist_end":0.01724,"object_to_goal_dist_start":0.01731,"object_z_max":0.02415,"peak_contact_force":0.56826,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":90.0,"raw_peak_contact_force":86.54394,"subtask_id":"reach_goal","tcp_end":[0.51976,-0.03538,0.12166],"tcp_start":[0.54317,0.02559,0.10064],"tcp_to_object_dist_end":0.10617,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.705,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00361,"approach_1.approach_arc_height":0.09396,"contact_1.contact_force_threshold":10.41296,"push_1.push_distance":0.13565,"push_1.push_speed":0.03359,"retract_1.retract_height":0.13275,"retract_1.retract_speed":0.0683},"optimized_scores":{"best_composite_score":0.0207,"best_fitness_score":0.4607,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":213.0,"contact_point_centroid":[0.53438,0.11977,0.05997],"force_p95":607.00064,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2226.8861,"mean_force":412.25456,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51084,0.08054,0.05506]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":692.0,"contact_point_centroid":[0.52514,0.08315,0.05163],"force_p95":373.73267,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2101.53471,"mean_force":354.28872,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51312,0.08112,0.05051]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":156.0,"contact_point_centroid":[0.47498,0.11996,0.05957],"force_p95":760.25621,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1013.32595,"mean_force":276.49369,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51443,0.08168,0.06056]},{"body_a":"world","body_b":"link7","contact_count":725.0,"contact_point_centroid":[0.5073,0.14131,-5e-05],"force_p95":297.1615,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":664.50518,"mean_force":186.58832,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51307,0.08082,0.05023]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":98.0,"contact_point_centroid":[0.52504,0.08584,0.05537],"force_p95":481.27756,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":601.92701,"mean_force":246.13804,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51327,0.08385,0.05524]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":735.0,"contact_point_centroid":[0.47494,0.1199,0.05338],"force_p95":553.04755,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":565.49593,"mean_force":452.97478,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.0808,0.05025]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5034,0.14329,-2e-05],"force_p95":249.13858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.17082,"mean_force":195.27493,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51328,0.0825,0.04975]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52507,0.11979,0.05988],"force_p95":176.46403,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":180.05484,"mean_force":154.36963,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51629,0.06092,0.08765]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50299,0.09117,0.03704],"force_p95":23.22458,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.52953,"mean_force":12.05235,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5021,0.10303,0.03426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.50238,-0.04603,0.00953],"force_p95":0.75765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.71975,"mean_force":0.62566,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51253,0.08092,0.05147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":467.0,"contact_point_centroid":[0.50091,0.11515,0.00942],"force_p95":0.61461,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.89704,"mean_force":0.65355,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49966,0.18421,0.13696]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49926,0.13284,0.05662],"force_p95":17.34158,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.62701,"mean_force":11.28821,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49762,0.14453,0.05352]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.49764,0.07375,0.00825],"force_p95":0.85575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.97119,"mean_force":0.67035,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49666,0.11842,0.04118]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47499,0.09428,0.02426],"force_p95":7.43433,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.67714,"mean_force":2.12535,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49618,0.11942,0.04119]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49961,0.09632,0.04125],"force_p95":3.57684,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.67628,"mean_force":1.02908,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49785,0.10822,0.03668]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52518,-0.03808,0.05212],"force_p95":1.82645,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.77413,"mean_force":0.51728,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51024,0.08164,0.05171]}],"total_contact_groups":19},"final_pose_error":0.04936,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50142,-0.04726,0.0347],"final_tcp_position":[0.50535,-0.03594,0.15115],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":2226.8861,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":870.0,"object_pos_end":[0.50099,0.11606,0.0338],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55967,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":71.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.50302,0.1482,0.22802],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.50234,0.10525,0.03999],"object_pos_start":[0.50099,0.11606,0.0338],"object_to_goal_dist_end":0.18526,"object_to_goal_dist_start":0.19616,"object_z_max":0.03982,"peak_contact_force":0.31159,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":472.0,"raw_peak_contact_force":17.89704,"subtask_id":"reach_peg","tcp_end":[0.49761,0.13539,0.05187],"tcp_start":[0.50302,0.1482,0.22802],"tcp_to_object_dist_end":0.03274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":600.0,"object_pos_end":[0.49546,0.06943,0.02512],"object_pos_start":[0.50234,0.10525,0.03999],"object_to_goal_dist_end":0.15023,"object_to_goal_dist_start":0.18526,"object_z_max":0.04072,"peak_contact_force":0.53056,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":446.0,"raw_peak_contact_force":7.97119,"subtask_id":"reach_peg","tcp_end":[0.49806,0.10686,0.03615],"tcp_start":[0.49761,0.13539,0.05187],"tcp_to_object_dist_end":0.03911,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5028,-0.04564,0.03484],"object_pos_start":[0.49546,0.06943,0.02512],"object_to_goal_dist_end":0.03486,"object_to_goal_dist_start":0.15023,"object_z_max":0.04192,"peak_contact_force":529.28884,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3353.0,"raw_peak_contact_force":2226.8861,"subtask_id":"reach_goal","tcp_end":[0.51329,0.08251,0.04971],"tcp_start":[0.49806,0.10686,0.03615],"tcp_to_object_dist_end":0.12943,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,-0.04726,0.0347],"object_pos_start":[0.5028,-0.04564,0.03484],"object_to_goal_dist_end":0.0332,"object_to_goal_dist_start":0.03486,"object_z_max":0.03484,"peak_contact_force":0.54168,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":598.0,"raw_peak_contact_force":1013.32595,"subtask_id":"reach_goal","tcp_end":[0.50535,-0.03594,0.15115],"tcp_start":[0.51329,0.08251,0.04971],"tcp_to_object_dist_end":0.11706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6129,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00094,"approach_1.approach_arc_height":0.10247,"contact_1.contact_force_threshold":15.25207,"push_1.push_distance":0.15811,"push_1.push_speed":0.07767,"retract_1.retract_height":0.08484,"retract_1.retract_speed":0.05658},"optimized_scores":{"best_composite_score":-0.12276,"best_fitness_score":0.31724,"best_task_score":0.57686},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":962.0,"contact_point_centroid":[0.52961,0.10409,0.05987],"force_p95":462.07852,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2309.85824,"mean_force":402.42771,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53176,0.03758,0.09556]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52528,0.03848,0.05995],"force_p95":2121.12499,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2143.88778,"mean_force":1377.76142,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.507,0.03044,0.02664]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53224,0.1032,0.05993],"force_p95":96.98814,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.22441,"mean_force":70.98821,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54441,0.03625,0.10038]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52521,-0.06418,0.0472],"force_p95":52.79458,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.68903,"mean_force":6.7135,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50926,0.03769,0.06592]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49954,0.04081,0.04181],"force_p95":74.22701,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.49253,"mean_force":40.73738,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49609,0.05221,0.03387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":880.0,"contact_point_centroid":[0.49457,-0.06969,0.00941],"force_p95":0.84626,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.89754,"mean_force":0.75773,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53366,0.03804,0.09867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.49536,0.06284,0.00939],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.23418,"mean_force":0.62525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48892,0.12801,0.1314]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49302,0.08091,0.05843],"force_p95":12.15953,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.69309,"mean_force":6.21845,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49122,0.0925,0.0564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.5004,0.02375,0.00842],"force_p95":0.853,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.77873,"mean_force":0.64585,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49084,0.06762,0.04204]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47486,0.0409,0.02427],"force_p95":6.18171,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.72527,"mean_force":1.52436,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48978,0.07283,0.04467]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.49618,-0.10107,0.05191],"force_p95":2.76325,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.52429,"mean_force":0.69079,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50601,0.03434,0.05077]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":130.0,"contact_point_centroid":[0.47462,-0.07089,0.04628],"force_p95":1.15101,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.60507,"mean_force":0.38889,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52234,0.03789,0.09325]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49581,0.04484,0.04214],"force_p95":2.35418,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.60353,"mean_force":0.9045,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49252,0.05664,0.03589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.49704,0.06445,0.00926],"force_p95":1.19927,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.63374,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49288,0.14484,0.25196]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52503,0.00441,0.03386],"force_p95":1.78417,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84637,"mean_force":0.98943,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49052,0.07015,0.04357]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49897,0.19425,0.29488]}],"total_contact_groups":17},"final_pose_error":0.04998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49358,-0.07145,0.03387],"final_tcp_position":[0.51922,-0.03418,0.11943],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":2309.85824,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":122.0,"n_steps_budget":1000.0,"object_pos_end":[0.49495,0.06385,0.03387],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14407,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55872,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":123.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.48755,0.10378,0.21785],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.49688,0.05468,0.03922],"object_pos_start":[0.49495,0.06385,0.03387],"object_to_goal_dist_end":0.13472,"object_to_goal_dist_start":0.14407,"object_z_max":0.03904,"peak_contact_force":0.33839,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":429.0,"raw_peak_contact_force":13.23418,"subtask_id":"reach_peg","tcp_end":[0.49132,0.08341,0.05391],"tcp_start":[0.48755,0.10378,0.21785],"tcp_to_object_dist_end":0.03274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":432.0,"n_steps_budget":600.0,"object_pos_end":[0.50258,0.02055,0.02436],"object_pos_start":[0.49688,0.05468,0.03922],"object_to_goal_dist_end":0.10179,"object_to_goal_dist_start":0.13472,"object_z_max":0.04078,"peak_contact_force":1.40756,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":442.0,"raw_peak_contact_force":6.77873,"subtask_id":"reach_peg","tcp_end":[0.49254,0.05652,0.03583],"tcp_start":[0.49132,0.08341,0.05391],"tcp_to_object_dist_end":0.03907,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49348,-0.07159,0.03387],"object_pos_start":[0.50258,0.02055,0.02436],"object_to_goal_dist_end":0.01228,"object_to_goal_dist_start":0.10179,"object_z_max":0.06512,"peak_contact_force":402.34213,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2055.0,"raw_peak_contact_force":2309.85824,"subtask_id":"reach_goal","tcp_end":[0.5444,0.03631,0.1003],"tcp_start":[0.49254,0.05652,0.03583],"tcp_to_object_dist_end":0.13656,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.49358,-0.07145,0.03387],"object_pos_start":[0.49348,-0.07159,0.03387],"object_to_goal_dist_end":0.01232,"object_to_goal_dist_start":0.01228,"object_z_max":0.03387,"peak_contact_force":0.55166,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":95.0,"raw_peak_contact_force":105.22441,"subtask_id":"reach_goal","tcp_end":[0.51922,-0.03418,0.11943],"tcp_start":[0.5444,0.03631,0.1003],"tcp_to_object_dist_end":0.09678,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```