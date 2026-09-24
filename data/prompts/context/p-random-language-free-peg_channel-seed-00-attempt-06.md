## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2860 | 0.77 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | -0.0598 | 0.00 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1293 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.2036 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5176 | 0.24 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.774, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.286) — your mutation base

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

- **Composite score**: 0.286
- **task_score** (E): 0.774
- **fitness_score**: 0.582  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.074
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 0.33 | 1.00 | 0.1564 |
| retract_1 | 0.00 | 1.00 | 0.1014 |
| lift_1 | 0.00 | 1.00 | 0.1541 |
| insert_2 | 0.33 | 1.00 | 0.1190 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 0.33 / step_budget | (0.497, 0.119, 0.043)→(0.495, -0.037, 0.037) | (0.500, 0.084, 0.033)→(0.507, -0.060, 0.030) | 0.165→0.030 | 1.00 / 3.667 | 45.370 | 171.576 |
| retract_1 | retract | 0.00 / step_budget | (0.495, -0.037, 0.037)→(0.494, 0.001, 0.130) | (0.507, -0.060, 0.030)→(0.505, -0.057, 0.031) | 0.030→0.028 | 1.00 / 1.000 | 0.587 | 93.288 |
| lift_1 | lift | 0.00 / step_budget | (0.494, 0.001, 0.130)→(0.410, -0.044, 0.251) | (0.505, -0.057, 0.031)→(0.502, -0.058, 0.031) | 0.028→0.028 | 1.00 / 1.000 | 0.604 | 3.681 |
| insert_2 | insert | 0.33 / step_budget | (0.410, -0.044, 0.251)→(0.452, -0.063, 0.141) | (0.502, -0.058, 0.031)→(0.501, -0.058, 0.031) | 0.028→0.029 | 1.00 / 1.333 | 3.732 | 3.735 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.819
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.578
- phase_score: 0.537
- phase_breakdown.approach_score: 0.810
- phase_breakdown.push_score: 0.625
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.669
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.875
- **Median Q (composite search score)**: 0.299
- **K-run variance**: 0.0107
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_distance
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72874,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.07309,"push_1.push_distance":0.15216,"push_1.push_speed":0.0811,"retract_1.retract_height":0.10704,"retract_1.speed":0.04517},"optimized_scores":{"best_composite_score":0.29869,"best_fitness_score":0.66869,"best_task_score":0.87489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":348.0,"contact_point_centroid":[0.54159,-0.01101,0.06],"force_p95":69.27126,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.53534,"mean_force":48.31302,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49679,-0.00917,0.03698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.50685,-0.10067,0.05804],"force_p95":64.43459,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.58049,"mean_force":35.74695,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4976,-0.05403,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":731.0,"contact_point_centroid":[0.50277,-0.00677,0.04336],"force_p95":43.76677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.34876,"mean_force":9.71079,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49661,0.00467,0.03707]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54275,-0.05302,0.06],"force_p95":74.68059,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.4649,"mean_force":58.09972,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49811,-0.0568,0.03663]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.50468,-0.06433,0.05558],"force_p95":27.9794,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.18673,"mean_force":6.19749,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49615,-0.05262,0.03982]},{"body_a":"peg","body_b":"channel_base_body","contact_count":54.0,"contact_point_centroid":[0.50548,-0.10068,0.06084],"force_p95":34.59153,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.94761,"mean_force":8.88483,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49669,-0.05404,0.03834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":610.0,"contact_point_centroid":[0.50584,-0.02641,0.00982],"force_p95":16.08124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.55787,"mean_force":6.36643,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4966,0.01611,0.0373]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":351.0,"contact_point_centroid":[0.52507,-0.01034,0.02274],"force_p95":6.03283,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.36379,"mean_force":1.7946,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49643,0.01617,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":947.0,"contact_point_centroid":[0.50649,-0.079,0.00941],"force_p95":0.5536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.93782,"mean_force":0.57996,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49478,-0.02868,0.08267]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50643,-0.0784,0.00938],"force_p95":0.55018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55018,"mean_force":0.54668,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4488,-0.03145,0.18993]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50643,-0.07835,0.00938],"force_p95":0.55018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55018,"mean_force":0.54669,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43456,-0.06153,0.18047]}],"total_contact_groups":14},"final_pose_error":0.07266,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50647,-0.0784,0.03378],"final_tcp_position":[0.46682,-0.07101,0.10402],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":101.53534,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50566,-0.08495,0.0356],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00871,"object_to_goal_dist_start":0.14177,"object_z_max":0.03811,"peak_contact_force":64.04869,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2135.0,"raw_peak_contact_force":101.53534,"tcp_end":[0.49811,-0.05677,0.03663],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50643,-0.07836,0.03378],"object_pos_start":[0.50566,-0.08495,0.0356],"object_to_goal_dist_end":0.0091,"object_to_goal_dist_start":0.00871,"object_z_max":0.03735,"peak_contact_force":0.5492,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1081.0,"raw_peak_contact_force":77.4649,"tcp_end":[0.49534,-0.01059,0.12624],"tcp_start":[0.49811,-0.05677,0.03663],"tcp_to_object_dist_end":0.11517,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,-0.07837,0.03378],"object_pos_start":[0.50643,-0.07836,0.03378],"object_to_goal_dist_end":0.00912,"object_to_goal_dist_start":0.0091,"object_z_max":0.03378,"peak_contact_force":0.54149,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55018,"tcp_end":[0.40502,-0.05246,0.25831],"tcp_start":[0.49534,-0.01059,0.12624],"tcp_to_object_dist_end":0.24774,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,-0.0784,0.03378],"object_pos_start":[0.50647,-0.07837,0.03378],"object_to_goal_dist_end":0.00911,"object_to_goal_dist_start":0.00912,"object_z_max":0.03378,"peak_contact_force":0.55014,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55018,"tcp_end":[0.46682,-0.07101,0.10402],"tcp_start":[0.40502,-0.05246,0.25831],"tcp_to_object_dist_end":0.08099,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56654,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04215,"push_1.push_distance":0.19974,"push_1.push_speed":0.07191,"retract_1.retract_height":0.15149,"retract_1.speed":0.05967},"optimized_scores":{"best_composite_score":0.15357,"best_fitness_score":0.52357,"best_task_score":0.86812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.50103,0.06592,0.00845],"force_p95":183.95194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.33662,"mean_force":72.13361,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5008,0.09766,0.04359]},{"body_a":"attachment","body_b":"peg","contact_count":749.0,"contact_point_centroid":[0.50435,0.09488,0.04479],"force_p95":184.04355,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.79981,"mean_force":83.34158,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50128,0.10445,0.04426]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5417,0.00071,0.06],"force_p95":73.8775,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.49081,"mean_force":55.3105,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49679,0.00492,0.03714]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":276.0,"contact_point_centroid":[0.47416,0.05803,0.03802],"force_p95":64.17673,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.27232,"mean_force":15.36502,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50001,0.08531,0.04132]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.54152,0.02189,0.06],"force_p95":50.1759,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.08897,"mean_force":38.79186,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49652,0.02499,0.03716]},{"body_a":"peg","body_b":"world","contact_count":137.0,"contact_point_centroid":[0.50194,0.12546,-0.00016],"force_p95":18.87088,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.59452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50034,0.15462,0.04497]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50348,-0.02346,0.0094],"force_p95":0.56907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.67997,"mean_force":0.54637,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49392,0.0196,0.08648]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.50233,-0.00611,0.05067],"force_p95":0.70397,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.28437,"mean_force":0.35198,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49565,0.00577,0.03897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50365,-0.02285,0.00938],"force_p95":0.55275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55408,"mean_force":0.54674,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45276,-0.00152,0.19102]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50369,-0.02288,0.00938],"force_p95":0.55268,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55387,"mean_force":0.54673,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44083,-0.04769,0.1729]}],"total_contact_groups":14},"final_pose_error":0.06661,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50364,-0.02286,0.03378],"final_tcp_position":[0.47077,-0.06502,0.09795],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":187.33662,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50413,-0.02414,0.03461],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.05627,"object_to_goal_dist_start":0.20832,"object_z_max":0.03695,"peak_contact_force":4.7523,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2058.0,"raw_peak_contact_force":187.33662,"tcp_end":[0.4968,0.00504,0.03714],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,-0.02287,0.03378],"object_pos_start":[0.50413,-0.02414,0.03461],"object_to_goal_dist_end":0.05758,"object_to_goal_dist_start":0.05627,"object_z_max":0.03533,"peak_contact_force":0.5444,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1028.0,"raw_peak_contact_force":76.49081,"tcp_end":[0.49475,0.02784,0.1371],"tcp_start":[0.4968,0.00504,0.03714],"tcp_to_object_dist_end":0.11544,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50365,-0.0229,0.03378],"object_pos_start":[0.50367,-0.02287,0.03378],"object_to_goal_dist_end":0.05756,"object_to_goal_dist_start":0.05758,"object_z_max":0.03378,"peak_contact_force":0.54432,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55408,"tcp_end":[0.41358,-0.03082,0.24945],"tcp_start":[0.49475,0.02784,0.1371],"tcp_to_object_dist_end":0.23386,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50364,-0.02286,0.03378],"object_pos_start":[0.50365,-0.0229,0.03378],"object_to_goal_dist_end":0.05759,"object_to_goal_dist_start":0.05756,"object_z_max":0.03378,"peak_contact_force":0.54596,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55387,"tcp_end":[0.47077,-0.06502,0.09795],"tcp_start":[0.41358,-0.03082,0.24945],"tcp_to_object_dist_end":0.08352,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4181,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.02112,"push_1.push_distance":0.19999,"push_1.push_speed":0.09752,"retract_1.retract_height":0.11074,"retract_1.speed":0.01314},"optimized_scores":{"best_composite_score":0.40561,"best_fitness_score":0.55339,"best_task_score":0.57784},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":346.0,"contact_point_centroid":[0.53464,-0.01367,0.05999],"force_p95":165.21423,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.85664,"mean_force":101.01289,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48931,-0.00926,0.03817]},{"body_a":"attachment","body_b":"peg","contact_count":921.0,"contact_point_centroid":[0.49757,0.00811,0.03615],"force_p95":121.31035,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.24667,"mean_force":70.51633,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48924,0.01378,0.03809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50854,-0.00541,0.00939],"force_p95":88.16061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.93555,"mean_force":41.39243,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48924,0.01783,0.03819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50022,-0.06806,0.00817],"force_p95":51.60082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.90937,"mean_force":6.49421,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48867,-0.0338,0.08108]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":843.0,"contact_point_centroid":[0.52619,-0.00643,0.02811],"force_p95":96.75103,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.24934,"mean_force":58.39036,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48931,0.0078,0.03807]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.49847,-0.05763,0.0387],"force_p95":75.17271,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.36909,"mean_force":36.36045,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4882,-0.05732,0.04366]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":148.0,"contact_point_centroid":[0.52563,-0.05369,0.02453],"force_p95":66.67274,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.96182,"mean_force":25.70424,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48813,-0.05692,0.04405]},{"body_a":"peg","body_b":"link7","contact_count":376.0,"contact_point_centroid":[0.52018,0.00944,0.06771],"force_p95":23.89311,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.94712,"mean_force":12.21296,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48935,0.03419,0.03791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":142.0,"contact_point_centroid":[0.49434,-0.07166,0.00801],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.10134,"mean_force":0.86889,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.41413,-0.05063,0.23309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50232,-0.07125,0.00805],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.93775,"mean_force":0.69785,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4496,-0.03114,0.1837]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47497,-0.06634,0.0241],"force_p95":9.68635,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.7252,"mean_force":7.69501,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.41757,-0.052,0.22209]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":56.0,"contact_point_centroid":[0.47494,-0.07449,0.02524],"force_p95":9.0416,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.46871,"mean_force":4.66501,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48806,-0.03655,0.07191]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52501,-0.07568,0.02462],"force_p95":9.3397,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.43975,"mean_force":4.52694,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47636,-0.01831,0.14036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49942,0.19831,0.29814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.49494,0.06368,0.0094],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54515,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49304,0.08732,0.11116]}],"total_contact_groups":18},"final_pose_error":0.20137,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49289,-0.07132,0.02423],"final_tcp_position":[0.41772,-0.05206,0.22166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":225.85664,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51093,-0.07212,0.01843],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02544,"object_to_goal_dist_start":0.14379,"object_z_max":0.03994,"peak_contact_force":67.3104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3462.0,"raw_peak_contact_force":225.85664,"tcp_end":[0.49053,-0.06064,0.03805],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.03055,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50463,-0.07124,0.02414],"object_pos_start":[0.51093,-0.07212,0.01843],"object_to_goal_dist_end":0.0187,"object_to_goal_dist_start":0.02544,"object_z_max":0.02942,"peak_contact_force":0.66721,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1346.0,"raw_peak_contact_force":125.90937,"tcp_end":[0.49049,-0.01305,0.12699],"tcp_start":[0.49053,-0.06064,0.03805],"tcp_to_object_dist_end":0.11901,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49556,-0.07137,0.02409],"object_pos_start":[0.50463,-0.07124,0.02414],"object_to_goal_dist_end":0.01864,"object_to_goal_dist_start":0.0187,"object_z_max":0.02535,"peak_contact_force":0.72551,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1022.0,"raw_peak_contact_force":9.93775,"tcp_end":[0.4116,-0.04933,0.24487],"tcp_start":[0.49049,-0.01305,0.12699],"tcp_to_object_dist_end":0.23722,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.49289,-0.07132,0.02423],"object_pos_start":[0.49556,-0.07137,0.02409],"object_to_goal_dist_end":0.01936,"object_to_goal_dist_start":0.01864,"object_z_max":0.02418,"peak_contact_force":10.10134,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":147.0,"raw_peak_contact_force":10.10134,"tcp_end":[0.41772,-0.05206,0.22166],"tcp_start":[0.4116,-0.04933,0.24487],"tcp_to_object_dist_end":0.21213,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```