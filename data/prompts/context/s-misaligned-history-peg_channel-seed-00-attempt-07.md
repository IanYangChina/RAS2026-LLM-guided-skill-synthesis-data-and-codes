## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.0255 | 0.20 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7  | -0.0814 | 0.02 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5  | 0.2691 | 0.74 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | -0.1276 | 0.00 | ❌ rejected |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5  | 0.1642 | 0.68 | ❌ rejected |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.164) — your mutation base

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

- **Composite score**: 0.164
- **task_score** (E): 0.680
- **fitness_score**: 0.534  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 0.67 | 1.00 | 0.1534 |
| retract_1 | 0.00 | 1.00 | 0.1241 |
| lift_1 | 0.00 | 1.00 | 0.1520 |
| insert_2 | 0.00 | 1.00 | 0.1661 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 0.67 / step_budget | (0.497, 0.119, 0.043)→(0.497, -0.034, 0.037) | (0.500, 0.084, 0.033)→(0.508, -0.062, 0.037) | 0.165→0.024 | 1.00 / 3.667 | 2115.846 | 146.893 |
| retract_1 | retract | 0.00 / step_budget | (0.497, -0.034, 0.037)→(0.495, 0.006, 0.153) | (0.508, -0.062, 0.037)→(0.506, -0.059, 0.034) | 0.024→0.026 | 1.00 / 1.000 | 0.547 | 66.781 |
| lift_1 | lift | 0.00 / step_budget | (0.495, 0.006, 0.153)→(0.407, -0.045, 0.265) | (0.506, -0.059, 0.034)→(0.506, -0.059, 0.034) | 0.026→0.026 | 1.00 / 1.000 | 0.547 | 0.550 |
| insert_2 | insert | 0.00 / step_budget | (0.407, -0.045, 0.265)→(0.465, -0.068, 0.111) | (0.506, -0.059, 0.034)→(0.506, -0.059, 0.034) | 0.026→0.026 | 1.00 / 1.000 | 0.546 | 0.551 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.894
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.880
- phase_score: 0.509
- phase_breakdown.push_score: 0.588
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.783

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.658
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.880
- **Median Q (composite search score)**: 0.155
- **K-run variance**: 0.0095
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.399


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54982,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.03643,"push_1.push_distance":0.18282,"push_1.push_speed":0.06448,"retract_1.retract_height":0.19403,"retract_1.speed":0.07686},"optimized_scores":{"best_composite_score":0.28773,"best_fitness_score":0.65773,"best_task_score":0.88032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":315.0,"contact_point_centroid":[0.5413,-0.00583,0.06],"force_p95":55.83093,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.03581,"mean_force":42.91627,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49646,-0.00337,0.03704]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54192,-0.04986,0.05999],"force_p95":64.73288,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.493,"mean_force":57.8918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49724,-0.05381,0.03673]},{"body_a":"attachment","body_b":"peg","contact_count":745.0,"contact_point_centroid":[0.50234,-0.00137,0.04226],"force_p95":16.1441,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.32492,"mean_force":5.98788,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49634,0.01005,0.03711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":49.0,"contact_point_centroid":[0.507,-0.10031,0.06082],"force_p95":33.73814,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.48265,"mean_force":18.56906,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49706,-0.0524,0.03676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.50639,-0.10034,0.06157],"force_p95":6.81385,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.7345,"mean_force":1.80754,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49647,-0.05295,0.03747]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50609,-0.065,0.05608],"force_p95":5.41124,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.29041,"mean_force":1.79391,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49664,-0.0532,0.03728]},{"body_a":"peg","body_b":"channel_base_body","contact_count":614.0,"contact_point_centroid":[0.50565,-0.02195,0.00983],"force_p95":13.8314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.90645,"mean_force":5.86534,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49639,0.0204,0.03734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":398.0,"contact_point_centroid":[0.52506,-0.01364,0.02443],"force_p95":5.64314,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.64911,"mean_force":1.68492,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4963,0.01299,0.0371]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,-0.08295,0.06],"force_p95":3.91445,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.01802,"mean_force":2.81277,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49722,-0.05381,0.03675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50565,-0.08131,0.00937],"force_p95":0.55352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42574,"mean_force":0.5524,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49435,-0.02181,0.09575]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50564,-0.08135,0.00938],"force_p95":0.54975,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5531,"mean_force":0.54652,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43388,-0.05846,0.19062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50564,-0.08135,0.00938],"force_p95":0.54947,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54652,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44937,-0.02478,0.21001]}],"total_contact_groups":15},"final_pose_error":0.08251,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50566,-0.0814,0.03381],"final_tcp_position":[0.46457,-0.0689,0.11368],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":69.03581,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,-0.08248,0.03687],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00791,"object_to_goal_dist_start":0.14177,"object_z_max":0.03819,"peak_contact_force":54.30305,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2121.0,"raw_peak_contact_force":69.03581,"tcp_end":[0.49724,-0.05379,0.03673],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.03025,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50565,-0.0814,0.03381],"object_pos_start":[0.50683,-0.08248,0.03687],"object_to_goal_dist_end":0.0085,"object_to_goal_dist_start":0.00791,"object_z_max":0.03707,"peak_contact_force":0.54738,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1020.0,"raw_peak_contact_force":65.493,"tcp_end":[0.49538,-0.00131,0.15582],"tcp_start":[0.49724,-0.05379,0.03673],"tcp_to_object_dist_end":0.14631,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50566,-0.0814,0.03381],"object_pos_start":[0.50565,-0.0814,0.03381],"object_to_goal_dist_end":0.00851,"object_to_goal_dist_start":0.0085,"object_z_max":0.03381,"peak_contact_force":0.54759,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55023,"tcp_end":[0.40583,-0.04843,0.26895],"tcp_start":[0.49538,-0.00131,0.15582],"tcp_to_object_dist_end":0.25758,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50566,-0.0814,0.03381],"object_pos_start":[0.50566,-0.0814,0.03381],"object_to_goal_dist_end":0.0085,"object_to_goal_dist_start":0.00851,"object_z_max":0.03381,"peak_contact_force":0.54693,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.5531,"tcp_end":[0.46457,-0.0689,0.11368],"tcp_start":[0.40583,-0.04843,0.26895],"tcp_to_object_dist_end":0.09068,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63197,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.03783,"push_1.push_distance":0.15472,"push_1.push_speed":0.07934,"retract_1.retract_height":0.10412,"retract_1.speed":0.08561},"optimized_scores":{"best_composite_score":0.15497,"best_fitness_score":0.52497,"best_task_score":0.8644},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":802.0,"contact_point_centroid":[0.50212,0.06239,0.00851],"force_p95":186.64398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.67567,"mean_force":70.78462,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50084,0.09447,0.04328]},{"body_a":"attachment","body_b":"peg","contact_count":765.0,"contact_point_centroid":[0.50481,0.08768,0.0451],"force_p95":186.41677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.28172,"mean_force":79.2181,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50116,0.09733,0.04368]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":232.0,"contact_point_centroid":[0.47388,0.06347,0.03697],"force_p95":68.59771,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.78596,"mean_force":20.96822,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50106,0.08958,0.04203]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54218,-0.00155,0.06],"force_p95":73.37277,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.92318,"mean_force":60.43291,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49731,0.00277,0.03708]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":140.0,"contact_point_centroid":[0.54183,0.02549,0.06],"force_p95":56.59036,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.28805,"mean_force":45.16406,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49684,0.0284,0.0371]},{"body_a":"peg","body_b":"world","contact_count":124.0,"contact_point_centroid":[0.50196,0.12556,-0.00017],"force_p95":20.81847,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.09194,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50038,0.15458,0.04495]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":116.0,"contact_point_centroid":[0.52508,-0.00912,0.02451],"force_p95":6.06544,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.73032,"mean_force":2.06616,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49702,0.01821,0.03712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50607,-0.02428,0.00942],"force_p95":0.55472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8864,"mean_force":0.54098,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4947,0.02023,0.10521]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50377,-0.00726,0.05392],"force_p95":0.60603,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73303,"mean_force":0.29266,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49554,0.0046,0.04066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50607,-0.02324,0.00938],"force_p95":0.54712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54713,"mean_force":0.54674,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44734,-0.00689,0.22779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50609,-0.02324,0.00938],"force_p95":0.54712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54712,"mean_force":0.54674,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.4285,-0.05245,0.20611]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,-0.02871,0.06],"force_p95":0.11153,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.11933,"mean_force":0.0644,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49731,0.00277,0.03708]}],"total_contact_groups":16},"final_pose_error":0.10073,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50609,-0.02323,0.03377],"final_tcp_position":[0.45835,-0.06445,0.13039],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":189.67567,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50666,-0.02592,0.03629],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.05461,"object_to_goal_dist_start":0.20832,"object_z_max":0.03793,"peak_contact_force":0.56368,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2179.0,"raw_peak_contact_force":189.67567,"tcp_end":[0.49732,0.0029,0.03708],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,-0.02324,0.03377],"object_pos_start":[0.50666,-0.02592,0.03629],"object_to_goal_dist_end":0.05742,"object_to_goal_dist_start":0.05461,"object_z_max":0.03629,"peak_contact_force":0.54584,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1036.0,"raw_peak_contact_force":74.92318,"tcp_end":[0.49578,0.02693,0.17702],"tcp_start":[0.49732,0.0029,0.03708],"tcp_to_object_dist_end":0.15212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,-0.02324,0.03377],"object_pos_start":[0.50605,-0.02324,0.03377],"object_to_goal_dist_end":0.05743,"object_to_goal_dist_start":0.05742,"object_z_max":0.03377,"peak_contact_force":0.54585,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.54713,"tcp_end":[0.40113,-0.04084,0.28332],"tcp_start":[0.49578,0.02693,0.17702],"tcp_to_object_dist_end":0.27128,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,-0.02323,0.03377],"object_pos_start":[0.50607,-0.02324,0.03377],"object_to_goal_dist_end":0.05743,"object_to_goal_dist_start":0.05743,"object_z_max":0.03377,"peak_contact_force":0.54585,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.54712,"tcp_end":[0.45835,-0.06445,0.13039],"tcp_start":[0.40113,-0.04084,0.28332],"tcp_to_object_dist_end":0.11538,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48462,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.03283,"push_1.push_distance":0.14772,"push_1.push_speed":0.0999,"retract_1.retract_height":0.10285,"retract_1.speed":0.02875},"optimized_scores":{"best_composite_score":0.04995,"best_fitness_score":0.41995,"best_task_score":0.29604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":332.0,"contact_point_centroid":[0.5379,-0.01002,0.06],"force_p95":119.11539,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.96732,"mean_force":73.65773,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49289,-0.00745,0.03744]},{"body_a":"attachment","body_b":"peg","contact_count":919.0,"contact_point_centroid":[0.49917,0.0039,0.03589],"force_p95":116.02769,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.1196,"mean_force":68.28422,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49178,0.01142,0.03761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.50804,-0.01387,0.00962],"force_p95":72.1033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.37865,"mean_force":38.80753,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49165,0.01582,0.03774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":844.0,"contact_point_centroid":[0.52595,-0.01279,0.02782],"force_p95":72.79748,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.2347,"mean_force":47.83681,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49205,0.00566,0.03756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":144.0,"contact_point_centroid":[0.50962,-0.10086,0.05024],"force_p95":70.13087,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.83824,"mean_force":51.74269,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49577,-0.04552,0.03696]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54183,-0.0483,0.05999],"force_p95":59.61219,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.92754,"mean_force":56.77401,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49713,-0.05227,0.03676]},{"body_a":"attachment","body_b":"peg","contact_count":80.0,"contact_point_centroid":[0.50261,-0.05812,0.04936],"force_p95":13.65043,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.66658,"mean_force":3.87241,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49476,-0.04717,0.04153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50954,-0.10039,0.05813],"force_p95":21.54224,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.55166,"mean_force":12.21692,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49623,-0.05104,0.03745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":987.0,"contact_point_centroid":[0.50667,-0.07369,0.00946],"force_p95":0.57256,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.4365,"mean_force":0.6563,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49406,-0.02624,0.08101]},{"body_a":"peg","body_b":"link7","contact_count":296.0,"contact_point_centroid":[0.52007,0.01224,0.06799],"force_p95":20.58806,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.03079,"mean_force":9.29864,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49015,0.03739,0.03782]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":310.0,"contact_point_centroid":[0.52517,-0.07203,0.05296],"force_p95":11.18296,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.25702,"mean_force":1.18591,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49429,-0.02889,0.07637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49942,0.19831,0.29814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.49494,0.06368,0.0094],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54515,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49304,0.08732,0.11116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50676,-0.07161,0.00938],"force_p95":0.55137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55386,"mean_force":0.54664,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4532,-0.02714,0.18254]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50676,-0.07164,0.00938],"force_p95":0.55137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55386,"mean_force":0.54664,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44262,-0.05837,0.16575]}],"total_contact_groups":18},"final_pose_error":0.05719,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50692,-0.07145,0.03379],"final_tcp_position":[0.47356,-0.07067,0.08985],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":6292.67123,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51027,-0.07663,0.03917],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.01084,"object_to_goal_dist_start":0.14379,"object_z_max":0.04022,"peak_contact_force":6292.67123,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3505.0,"raw_peak_contact_force":181.96732,"tcp_end":[0.49717,-0.05225,0.03679],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,-0.07138,0.03379],"object_pos_start":[0.51027,-0.07663,0.03917],"object_to_goal_dist_end":0.01267,"object_to_goal_dist_start":0.01084,"object_z_max":0.03924,"peak_contact_force":0.54696,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1409.0,"raw_peak_contact_force":59.92754,"tcp_end":[0.49474,-0.00788,0.12654],"tcp_start":[0.49717,-0.05225,0.03679],"tcp_to_object_dist_end":0.11306,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,-0.07142,0.03379],"object_pos_start":[0.5069,-0.07138,0.03379],"object_to_goal_dist_end":0.01264,"object_to_goal_dist_start":0.01267,"object_z_max":0.03379,"peak_contact_force":0.54803,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1265.0,"raw_peak_contact_force":0.55386,"tcp_end":[0.41447,-0.04651,0.24313],"tcp_start":[0.49474,-0.00788,0.12654],"tcp_to_object_dist_end":0.23019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50692,-0.07145,0.03379],"object_pos_start":[0.50691,-0.07142,0.03379],"object_to_goal_dist_end":0.01264,"object_to_goal_dist_start":0.01264,"object_z_max":0.03379,"peak_contact_force":0.54477,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.55386,"tcp_end":[0.47356,-0.07067,0.08985],"tcp_start":[0.41447,-0.04651,0.24313],"tcp_to_object_dist_end":0.06524,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```