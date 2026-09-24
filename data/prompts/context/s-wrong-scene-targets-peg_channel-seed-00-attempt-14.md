## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1552 | 0.73 | ❌ rejected |
| 13 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1451 | 0.00 | ❌ rejected |
| 12 | approach → descend → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0212 | 0.17 | ❌ rejected |
| 11 | approach → push → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1074 | 0.00 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 7 | -0.1885 | 0.08 | ❌ rejected |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5109569349857164, -0.09841706289889038, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, -0.09841706289889038, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5109569349857164, 0.061582937101109625, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5109569349857164, 0.061582937101109625, 0.04]
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
  frozen_object_starts: {'peg': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.749, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5109569349857164, -0.09841706289889038, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=0.155) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.155
- **task_score** (E): 0.731
- **fitness_score**: 0.525  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 1.00 | 1.00 | 0.1420 |
| retract_1 | 0.00 | 1.00 | 0.1123 |
| lift_1 | 0.00 | 1.00 | 0.1546 |
| insert_2 | 0.00 | 1.00 | 0.1663 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 1.00 / step_budget | (0.497, 0.119, 0.043)→(0.498, -0.023, 0.037) | (0.500, 0.084, 0.033)→(0.504, -0.054, 0.037) | 0.165→0.031 | 1.00 / 3.000 | 36.766 | 123.621 |
| retract_1 | retract | 0.00 / step_budget | (0.498, -0.023, 0.037)→(0.495, 0.010, 0.143) | (0.504, -0.054, 0.037)→(0.501, -0.056, 0.035) | 0.031→0.027 | 1.00 / 1.333 | 0.511 | 69.824 |
| lift_1 | lift | 0.00 / step_budget | (0.495, 0.010, 0.143)→(0.409, -0.043, 0.259) | (0.501, -0.056, 0.035)→(0.501, -0.056, 0.034) | 0.027→0.027 | 1.00 / 1.333 | 0.507 | 0.536 |
| insert_2 | insert | 0.00 / step_budget | (0.409, -0.043, 0.259)→(0.468, -0.068, 0.105) | (0.501, -0.056, 0.034)→(0.501, -0.056, 0.034) | 0.027→0.027 | 1.00 / 1.333 | 0.506 | 0.564 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.871
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.871
- phase_score: 0.533
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.628
- phase_breakdown.approach_score: 0.783

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.668
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.871
- **Median Q (composite search score)**: 0.143
- **K-run variance**: 0.0126
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.298


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
{"anchors":[{"name":"object","value":[0.51096,-0.09842,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,-0.09842,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51373,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.03964,"push_1.push_distance":0.1644,"push_1.push_speed":0.08339,"retract_1.retract_height":0.15672,"retract_1.speed":0.05847},"optimized_scores":{"best_composite_score":0.29828,"best_fitness_score":0.66828,"best_task_score":0.87083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":338.0,"contact_point_centroid":[0.54153,-0.01222,0.06],"force_p95":63.13324,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.0497,"mean_force":47.84431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49672,-0.01047,0.03699]},{"body_a":"attachment","body_b":"peg","contact_count":781.0,"contact_point_centroid":[0.5026,-0.00393,0.04265],"force_p95":42.60881,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.38072,"mean_force":9.76522,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49651,0.00744,0.03709]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54265,-0.05333,0.05998],"force_p95":76.88466,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.37551,"mean_force":59.13946,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.498,-0.0571,0.03661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.50701,-0.10071,0.05841],"force_p95":76.95529,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.94147,"mean_force":36.48862,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4975,-0.05393,0.03671]},{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.50448,-0.06413,0.05578],"force_p95":16.85495,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.1148,"mean_force":5.34047,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4959,-0.05243,0.04034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.50551,-0.10077,0.05921],"force_p95":16.84798,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.20503,"mean_force":7.81907,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4965,-0.05408,0.03858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":584.0,"contact_point_centroid":[0.50613,-0.02141,0.00985],"force_p95":14.79515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.74116,"mean_force":6.53122,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49649,0.02085,0.03735]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":487.0,"contact_point_centroid":[0.52506,-0.01609,0.02654],"force_p95":6.59163,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.40979,"mean_force":2.41229,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49643,0.01059,0.03707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":942.0,"contact_point_centroid":[0.50619,-0.07854,0.00942],"force_p95":0.55545,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.55484,"mean_force":0.55556,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49469,-0.02846,0.08362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5061,-0.07769,0.00938],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55597,"mean_force":0.54658,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45342,-0.02901,0.18364]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50608,-0.0777,0.00938],"force_p95":0.54997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55171,"mean_force":0.54657,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44252,-0.05921,0.16649]}],"total_contact_groups":14},"final_pose_error":0.05742,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5061,-0.07775,0.03379],"final_tcp_position":[0.47352,-0.07103,0.09016],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":100.0497,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50575,-0.08515,0.03573],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00882,"object_to_goal_dist_start":0.14177,"object_z_max":0.03787,"peak_contact_force":66.89879,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2290.0,"raw_peak_contact_force":100.0497,"tcp_end":[0.498,-0.05706,0.0366],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,-0.0777,0.03379],"object_pos_start":[0.50575,-0.08515,0.03573],"object_to_goal_dist_end":0.00898,"object_to_goal_dist_start":0.00882,"object_z_max":0.03767,"peak_contact_force":0.54981,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1090.0,"raw_peak_contact_force":80.37551,"tcp_end":[0.4953,-0.01032,0.12765],"tcp_start":[0.498,-0.05706,0.0366],"tcp_to_object_dist_end":0.11605,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,-0.07773,0.03379],"object_pos_start":[0.50606,-0.0777,0.03379],"object_to_goal_dist_end":0.00898,"object_to_goal_dist_start":0.00898,"object_z_max":0.03379,"peak_contact_force":0.5447,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55597,"tcp_end":[0.41431,-0.04783,0.2443],"tcp_start":[0.4953,-0.01032,0.12765],"tcp_to_object_dist_end":0.23158,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,-0.07775,0.03379],"object_pos_start":[0.50608,-0.07773,0.03379],"object_to_goal_dist_end":0.00899,"object_to_goal_dist_start":0.00898,"object_z_max":0.03379,"peak_contact_force":0.54691,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55171,"tcp_end":[0.47352,-0.07103,0.09016],"tcp_start":[0.41431,-0.04783,0.2443],"tcp_to_object_dist_end":0.06545,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,-0.04396,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,-0.04396,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80328,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06293,"push_1.push_distance":0.12792,"push_1.push_speed":0.0792,"retract_1.retract_height":0.12413,"retract_1.speed":0.08206},"optimized_scores":{"best_composite_score":0.14327,"best_fitness_score":0.51327,"best_task_score":0.85588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":813.0,"contact_point_centroid":[0.50053,0.06455,0.00843],"force_p95":187.51591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.48853,"mean_force":71.38002,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50116,0.09568,0.0434]},{"body_a":"attachment","body_b":"peg","contact_count":712.0,"contact_point_centroid":[0.50427,0.09555,0.04499],"force_p95":187.55792,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":191.03382,"mean_force":87.66413,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50184,0.10511,0.04439]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52502,0.1059,0.05999],"force_p95":83.87487,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.70638,"mean_force":57.22019,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50684,0.10589,0.04779]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":343.0,"contact_point_centroid":[0.47401,0.05387,0.03831],"force_p95":72.00619,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.34706,"mean_force":18.71487,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50069,0.08016,0.04138]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5425,0.00532,0.05999],"force_p95":76.48736,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.45167,"mean_force":60.87873,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49761,0.00928,0.03704]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":173.0,"contact_point_centroid":[0.54207,0.03097,0.06],"force_p95":60.90622,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.11151,"mean_force":48.48401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49708,0.03359,0.03706]},{"body_a":"peg","body_b":"world","contact_count":127.0,"contact_point_centroid":[0.50198,0.12553,-0.00018],"force_p95":20.38732,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.14613,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50043,0.15431,0.04499]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49897,-0.02097,0.0094],"force_p95":0.56546,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8676,"mean_force":0.54696,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49487,0.02473,0.10282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49923,-0.02086,0.00938],"force_p95":0.55141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55625,"mean_force":0.5467,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44566,-0.00593,0.22619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49921,-0.0209,0.00938],"force_p95":0.5494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55057,"mean_force":0.54674,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.42613,-0.05336,0.2078]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49851,-0.00191,0.04497],"force_p95":0.24376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25547,"mean_force":0.16419,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49641,0.01004,0.03897]}],"total_contact_groups":15},"final_pose_error":0.10215,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49924,-0.0209,0.03379],"final_tcp_position":[0.457,-0.06494,0.13143],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":191.48853,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.50033,-0.02132,0.03496],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.0589,"object_to_goal_dist_start":0.20832,"object_z_max":0.03719,"peak_contact_force":43.40021,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2174.0,"raw_peak_contact_force":191.48853,"tcp_end":[0.49762,0.00937,0.03704],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4992,-0.02083,0.03383],"object_pos_start":[0.50033,-0.02132,0.03496],"object_to_goal_dist_end":0.05949,"object_to_goal_dist_start":0.0589,"object_z_max":0.03496,"peak_contact_force":0.54769,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1009.0,"raw_peak_contact_force":78.45167,"tcp_end":[0.49584,0.03022,0.17158],"tcp_start":[0.49762,0.00937,0.03704],"tcp_to_object_dist_end":0.14695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49925,-0.0209,0.03379],"object_pos_start":[0.4992,-0.02083,0.03383],"object_to_goal_dist_end":0.05943,"object_to_goal_dist_start":0.05949,"object_z_max":0.03383,"peak_contact_force":0.54698,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55625,"tcp_end":[0.3978,-0.04218,0.28549],"tcp_start":[0.49584,0.03022,0.17158],"tcp_to_object_dist_end":0.27221,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49924,-0.0209,0.03379],"object_pos_start":[0.49925,-0.0209,0.03379],"object_to_goal_dist_end":0.05943,"object_to_goal_dist_start":0.05943,"object_z_max":0.03379,"peak_contact_force":0.54717,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55057,"tcp_end":[0.457,-0.06494,0.13143],"tcp_start":[0.3978,-0.04218,0.28549],"tcp_to_object_dist_end":0.11514,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,-0.09612,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.09612,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44082,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.05696,"push_1.push_distance":0.09507,"push_1.push_speed":0.06809,"retract_1.retract_height":0.12352,"retract_1.speed":0.04992},"optimized_scores":{"best_composite_score":0.02403,"best_fitness_score":0.39403,"best_task_score":0.46739},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":347.0,"contact_point_centroid":[0.53844,0.01713,0.06],"force_p95":65.47237,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.32531,"mean_force":48.5731,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49331,0.02046,0.03747]},{"body_a":"attachment","body_b":"peg","contact_count":880.0,"contact_point_centroid":[0.49963,0.01982,0.03609],"force_p95":48.40414,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.23604,"mean_force":29.10326,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49269,0.02883,0.03755]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54179,-0.02699,0.05999],"force_p95":50.09177,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.64509,"mean_force":45.11193,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49711,-0.02134,0.03698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":926.0,"contact_point_centroid":[0.50688,-0.00138,0.0098],"force_p95":30.31611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.88916,"mean_force":16.47433,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49253,0.03217,0.03769]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":774.0,"contact_point_centroid":[0.52539,0.00161,0.02398],"force_p95":32.53472,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.05609,"mean_force":22.11482,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49317,0.02213,0.03749]},{"body_a":"peg","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.5201,0.02412,0.06814],"force_p95":4.78144,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.50962,"mean_force":4.04821,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4908,0.04953,0.03768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.5012,-0.05495,0.00999],"force_p95":0.58037,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.56722,"mean_force":0.45223,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49409,-0.00169,0.0828]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50251,-0.03119,0.0345],"force_p95":4.30477,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.72135,"mean_force":0.83658,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49687,-0.02126,0.03714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":859.0,"contact_point_centroid":[0.49947,-0.10002,0.03278],"force_p95":0.36912,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.58825,"mean_force":0.20537,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49401,0.00047,0.08835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":594.0,"contact_point_centroid":[0.475,-0.08852,0.04578],"force_p95":0.16273,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86826,"mean_force":0.09371,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49395,-0.0006,0.08501]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49942,0.19831,0.29814]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.5251,-0.04516,0.02467],"force_p95":0.65624,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66819,"mean_force":0.40818,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49694,-0.0213,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50154,-0.05208,0.00999],"force_p95":0.44892,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5902,"mean_force":0.39839,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44152,-0.0528,0.16905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.49494,0.06368,0.0094],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54515,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49304,0.08732,0.11116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50112,-0.05358,0.00999],"force_p95":0.43847,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49578,"mean_force":0.39877,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45281,-0.01346,0.18553]}],"total_contact_groups":20},"final_pose_error":0.06174,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49768,-0.0707,0.03328],"final_tcp_position":[0.47209,-0.06784,0.09371],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":79.32531,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.50731,-0.057,0.04061],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02415,"object_to_goal_dist_start":0.14379,"object_z_max":0.04068,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3002.0,"raw_peak_contact_force":79.32531,"tcp_end":[0.49712,-0.02126,0.037],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49757,-0.06963,0.03643],"object_pos_start":[0.50731,-0.057,0.04061],"object_to_goal_dist_end":0.01123,"object_to_goal_dist_start":0.02415,"object_z_max":0.04082,"peak_contact_force":0.4353,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2468.0,"raw_peak_contact_force":50.64509,"tcp_end":[0.49477,0.01128,0.12973],"tcp_start":[0.49712,-0.02126,0.037],"tcp_to_object_dist_end":0.12353,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49763,-0.06995,0.03541],"object_pos_start":[0.49757,-0.06963,0.03643],"object_to_goal_dist_end":0.0113,"object_to_goal_dist_start":0.01123,"object_z_max":0.03643,"peak_contact_force":0.42857,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2676.0,"raw_peak_contact_force":0.49578,"tcp_end":[0.41372,-0.03822,0.24586],"tcp_start":[0.49477,0.01128,0.12973],"tcp_to_object_dist_end":0.22878,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49768,-0.0707,0.03328],"object_pos_start":[0.49763,-0.06995,0.03541],"object_to_goal_dist_end":0.01171,"object_to_goal_dist_start":0.0113,"object_z_max":0.03541,"peak_contact_force":0.42366,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2588.0,"raw_peak_contact_force":0.5902,"tcp_end":[0.47209,-0.06784,0.09371],"tcp_start":[0.41372,-0.03822,0.24586],"tcp_to_object_dist_end":0.06569,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```