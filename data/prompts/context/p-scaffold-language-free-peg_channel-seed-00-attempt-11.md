## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.2303 | 0.53 | ❌ rejected |
| 10 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.4864 | 0.00 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1159 | 0.14 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.0625 | 0.26 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1786 | 0.06 | ❌ rejected |

**Proposal policy**: task_score is 0.53 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.230) — your mutation base

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

- **Composite score**: 0.230
- **task_score** (E): 0.533
- **fitness_score**: 0.674  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1707 |
| descend_and_contact | 1.00 | 1.00 | 0.1066 |
| push_along_channel | 0.67 | 1.00 | 0.1617 |
| lift_and_retract | 0.33 | 1.00 | 0.0858 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.129, 0.153) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.539 | 2.179 |
| descend_and_contact | descend | 1.00 / force_exceeded | (0.494, 0.129, 0.153)→(0.491, 0.091, 0.056) | (0.500, 0.081, 0.034)→(0.500, 0.075, 0.035) | 0.161→0.155 | 1.00 / 2.000 | 13.776 | 15.225 |
| push_along_channel | push | 0.67 / step_budget | (0.491, 0.091, 0.056)→(0.500, -0.069, 0.039) | (0.500, 0.075, 0.035)→(0.502, -0.025, 0.028) | 0.155→0.057 | 1.00 / 3.000 | 312.496 | 392.193 |
| lift_and_retract | retract | 0.33 / step_budget | (0.500, -0.069, 0.039)→(0.497, -0.059, 0.124) | (0.502, -0.025, 0.028)→(0.500, -0.025, 0.027) | 0.057→0.058 | 1.00 / 1.000 | 0.631 | 90.265 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.372
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.359
- phase_score: 0.843
- phase_breakdown.push_channel_score: 0.969
- phase_breakdown.reach_peg_score: 0.551

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.763
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.248
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.365


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29148,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.14354,"approach_peg.approach_speed":0.03719,"approach_peg.arc_height":0.08553,"descend_and_contact.contact_force":5.9218,"descend_and_contact.descend_speed":0.05159,"descend_and_contact.lateral_offset_x":-0.00769,"lift_and_retract.retract_height":0.1753,"lift_and_retract.speed":0.06874,"push_along_channel.pose_tolerance":0.01898,"push_along_channel.push_distance":0.18213,"push_along_channel.push_speed":0.08052},"optimized_scores":{"best_composite_score":0.2897,"best_fitness_score":0.6497,"best_task_score":0.35931},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":268.0,"contact_point_centroid":[0.54432,-0.10001,0.06493],"force_p95":370.11531,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":409.63645,"mean_force":278.2637,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50142,-0.07783,0.03881]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":208.0,"contact_point_centroid":[0.52503,-0.07888,0.05999],"force_p95":197.08993,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.44095,"mean_force":141.27867,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5018,-0.07862,0.03901]},{"body_a":"attachment","body_b":"peg","contact_count":271.0,"contact_point_centroid":[0.50724,0.03223,0.05529],"force_p95":119.22195,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.95648,"mean_force":80.64693,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49852,0.02783,0.05788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.50534,0.0145,0.00855],"force_p95":116.71361,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.63758,"mean_force":33.50872,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49954,-0.02897,0.04719]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,-0.07971,0.05999],"force_p95":105.34572,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.81201,"mean_force":32.29552,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.50155,-0.0796,0.04005]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54521,-0.10001,0.06493],"force_p95":71.58805,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.26585,"mean_force":55.47731,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.50155,-0.0796,0.04008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50376,0.06158,0.00938],"force_p95":0.55527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.49733,"mean_force":0.57888,"phase_index":1.0,"phase_name":"descend_and_contact","phase_type":"descend","tcp_position_centroid":[0.50091,0.08714,0.12523]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50595,0.07065,0.05876],"force_p95":22.07411,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.07411,"mean_force":22.07411,"phase_index":1.0,"phase_name":"descend_and_contact","phase_type":"descend","tcp_position_centroid":[0.49507,0.07048,0.06378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.52501,0.02959,0.05885],"force_p95":17.72572,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.21878,"mean_force":14.43029,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50074,0.01844,0.0581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":794.0,"contact_point_centroid":[0.50367,0.06157,0.00935],"force_p95":0.58457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55681,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50643,0.13112,0.27224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50586,0.00201,0.00802],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81489,"mean_force":0.60589,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.49805,-0.066,0.0956]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49958,0.19864,0.3]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.02693,0.02418],"force_p95":0.37083,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37083,"mean_force":0.37083,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.49825,-0.07447,0.04883]}],"total_contact_groups":13},"final_pose_error":0.06451,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50528,0.00212,0.02409],"final_tcp_position":[0.4983,-0.06387,0.15282],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":409.63645,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.06157,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54805,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":813.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.50908,0.10377,0.18938],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.06156,0.03379],"object_pos_start":[0.50373,0.06157,0.03379],"object_to_goal_dist_end":0.14174,"object_to_goal_dist_start":0.14176,"object_z_max":0.03379,"peak_contact_force":22.49733,"phase_name":"descend_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":681.0,"raw_peak_contact_force":22.49733,"subtask_id":"reach_peg","tcp_end":[0.49507,0.07044,0.06361],"tcp_start":[0.50908,0.10377,0.18938],"tcp_to_object_dist_end":0.0323,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.5059,0.00207,0.02415],"object_pos_start":[0.50373,0.06156,0.03379],"object_to_goal_dist_end":0.0838,"object_to_goal_dist_start":0.14174,"object_z_max":0.03936,"peak_contact_force":340.21576,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1450.0,"raw_peak_contact_force":409.63645,"subtask_id":"push_channel","tcp_end":[0.50152,-0.07953,0.04002],"tcp_start":[0.49507,0.07044,0.06361],"tcp_to_object_dist_end":0.08324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50528,0.00212,0.02409],"object_pos_start":[0.5059,0.00207,0.02415],"object_to_goal_dist_end":0.08382,"object_to_goal_dist_start":0.0838,"object_z_max":0.02421,"peak_contact_force":0.72551,"phase_name":"lift_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1010.0,"raw_peak_contact_force":122.81201,"tcp_end":[0.4983,-0.06387,0.15282],"tcp_start":[0.50152,-0.07953,0.04002],"tcp_to_object_dist_end":0.14482,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80882,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.05017,"approach_peg.approach_speed":0.05027,"approach_peg.arc_height":0.05605,"descend_and_contact.contact_force":13.94762,"descend_and_contact.descend_speed":0.01011,"descend_and_contact.lateral_offset_x":-0.0028,"lift_and_retract.retract_height":0.05654,"lift_and_retract.speed":0.03756,"push_along_channel.pose_tolerance":0.01846,"push_along_channel.push_distance":0.1987,"push_along_channel.push_speed":0.08524},"optimized_scores":{"best_composite_score":0.15327,"best_fitness_score":0.76327,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":615.0,"contact_point_centroid":[0.5437,-0.01273,0.05997],"force_p95":257.08661,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":417.36363,"mean_force":149.13488,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49891,-0.01338,0.03691]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":329.0,"contact_point_centroid":[0.52503,-0.04738,0.05999],"force_p95":172.13265,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.8981,"mean_force":137.37925,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5006,-0.04726,0.03679]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52504,-0.04945,0.05998],"force_p95":59.4084,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.2112,"mean_force":13.20187,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.50039,-0.04901,0.03753]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.54512,-0.05647,0.05995],"force_p95":50.98428,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.02072,"mean_force":44.90229,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.50039,-0.04901,0.03753]},{"body_a":"attachment","body_b":"peg","contact_count":584.0,"contact_point_centroid":[0.50083,-0.00846,0.03876],"force_p95":26.25803,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.60051,"mean_force":4.89214,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49802,0.00303,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":673.0,"contact_point_centroid":[0.50196,-0.04682,0.00978],"force_p95":25.41549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.47011,"mean_force":4.15901,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49842,-0.00332,0.03702]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":258.0,"contact_point_centroid":[0.52523,0.02189,0.03293],"force_p95":15.37209,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.11537,"mean_force":3.64354,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49554,0.04951,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50262,0.09994,0.00976],"force_p95":4.79496,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.36113,"mean_force":1.78332,"phase_index":1.0,"phase_name":"descend_and_contact","phase_type":"descend","tcp_position_centroid":[0.49403,0.14289,0.05588]},{"body_a":"attachment","body_b":"peg","contact_count":586.0,"contact_point_centroid":[0.49755,0.12151,0.04563],"force_p95":4.85402,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.00004,"mean_force":2.30678,"phase_index":1.0,"phase_name":"descend_and_contact","phase_type":"descend","tcp_position_centroid":[0.4939,0.13294,0.046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":809.0,"contact_point_centroid":[0.50095,0.11602,0.00939],"force_p95":0.60733,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55337,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49786,0.21909,0.1898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.49944,-0.07877,0.00941],"force_p95":0.56141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66834,"mean_force":0.54792,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.49681,-0.04485,0.06141]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50008,-0.06069,0.03882],"force_p95":1.11628,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.383,"mean_force":0.35666,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.50007,-0.04871,0.03806]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49948,-0.07856,0.03378],"final_tcp_position":[0.49658,-0.04742,0.085],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":417.36363,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.11603,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52905,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":809.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49736,0.1752,0.09105],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50278,0.0991,0.03664],"object_pos_start":[0.50094,0.11603,0.03387],"object_to_goal_dist_end":0.17916,"object_to_goal_dist_start":0.19613,"object_z_max":0.03712,"peak_contact_force":2.01581,"phase_name":"descend_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1586.0,"raw_peak_contact_force":6.36113,"subtask_id":"reach_peg","tcp_end":[0.49391,0.12748,0.04071],"tcp_start":[0.49736,0.1752,0.09105],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.49945,-0.07896,0.03534],"object_pos_start":[0.50278,0.0991,0.03664],"object_to_goal_dist_end":0.0048,"object_to_goal_dist_start":0.17916,"object_z_max":0.04003,"peak_contact_force":247.71954,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2459.0,"raw_peak_contact_force":417.36363,"subtask_id":"push_channel","tcp_end":[0.50036,-0.04905,0.0375],"tcp_start":[0.49391,0.12748,0.04071],"tcp_to_object_dist_end":0.03,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":960.0,"object_pos_end":[0.49948,-0.07856,0.03378],"object_pos_start":[0.49945,-0.07896,0.03534],"object_to_goal_dist_end":0.00641,"object_to_goal_dist_start":0.0048,"object_z_max":0.03535,"peak_contact_force":0.54873,"phase_name":"lift_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":541.0,"raw_peak_contact_force":79.2112,"tcp_end":[0.49658,-0.04742,0.085],"tcp_start":[0.50036,-0.04905,0.0375],"tcp_to_object_dist_end":0.06002,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97778,"average_solve_count":270.0,"average_success_count":270.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.13351,"approach_peg.approach_speed":0.04434,"approach_peg.arc_height":0.09526,"descend_and_contact.contact_force":15.85809,"descend_and_contact.descend_speed":0.02453,"descend_and_contact.lateral_offset_x":-0.00433,"lift_and_retract.retract_height":0.15822,"lift_and_retract.speed":0.05034,"push_along_channel.pose_tolerance":0.01337,"push_along_channel.push_distance":0.16649,"push_along_channel.push_speed":0.06365},"optimized_scores":{"best_composite_score":0.24791,"best_fitness_score":0.60791,"best_task_score":0.23879},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":278.0,"contact_point_centroid":[0.53787,-0.10001,0.06495],"force_p95":342.81551,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.58039,"mean_force":231.69538,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49515,-0.07302,0.03792]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.534,-0.0586,0.05999],"force_p95":126.68924,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.82401,"mean_force":82.80615,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48894,-0.06205,0.03739]},{"body_a":"peg","body_b":"channel_base_body","contact_count":867.0,"contact_point_centroid":[0.49969,0.01576,0.00851],"force_p95":122.14013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.72569,"mean_force":38.9255,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49023,-0.01935,0.04767]},{"body_a":"attachment","body_b":"peg","contact_count":416.0,"contact_point_centroid":[0.49685,0.03173,0.05434],"force_p95":123.23774,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.16228,"mean_force":80.00974,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48771,0.02844,0.05731]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54209,-0.10002,0.06492],"force_p95":66.50137,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.7711,"mean_force":55.31677,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.49942,-0.07958,0.03847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":807.0,"contact_point_centroid":[0.49501,0.06397,0.0094],"force_p95":0.55076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.81569,"mean_force":0.56535,"phase_index":1.0,"phase_name":"descend_and_contact","phase_type":"descend","tcp_position_centroid":[0.47885,0.0899,0.1191]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49427,0.07395,0.05898],"force_p95":16.29534,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.29534,"mean_force":16.29534,"phase_index":1.0,"phase_name":"descend_and_contact","phase_type":"descend","tcp_position_centroid":[0.48351,0.07382,0.06423]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49532,0.00121,0.00806],"force_p95":0.69709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.00697,"mean_force":0.62953,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.49587,-0.06736,0.08542]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47499,-0.02272,0.02436],"force_p95":8.4476,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.60461,"mean_force":3.36113,"phase_index":3.0,"phase_name":"lift_and_retract","phase_type":"retract","tcp_position_centroid":[0.49549,-0.0706,0.05916]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52503,0.02504,0.02427],"force_p95":5.84774,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.1468,"mean_force":1.47438,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4936,-0.0706,0.03771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.49541,0.06387,0.00938],"force_p95":0.56441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55679,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48231,0.12878,0.26297]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49887,0.19763,0.29981]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,-0.01899,0.03468],"force_p95":0.78612,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79144,"mean_force":0.7383,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48746,-0.02962,0.04392]}],"total_contact_groups":13},"final_pose_error":0.06538,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4959,0.00098,0.02414],"final_tcp_position":[0.49601,-0.06464,0.1331],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":349.58039,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,0.06412,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14433,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.53925,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47669,0.10673,0.17885],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.49479,0.06383,0.03403],"object_pos_start":[0.4951,0.06412,0.03398],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14433,"object_z_max":0.03404,"peak_contact_force":16.81569,"phase_name":"descend_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":808.0,"raw_peak_contact_force":16.81569,"subtask_id":"reach_peg","tcp_end":[0.48353,0.07379,0.06412],"tcp_start":[0.47669,0.10673,0.17885],"tcp_to_object_dist_end":0.03363,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.50018,0.00125,0.02413],"object_pos_start":[0.49479,0.06383,0.03403],"object_to_goal_dist_end":0.08279,"object_to_goal_dist_start":0.14404,"object_z_max":0.03944,"peak_contact_force":349.5533,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1598.0,"raw_peak_contact_force":349.58039,"subtask_id":"push_channel","tcp_end":[0.4994,-0.07961,0.03844],"tcp_start":[0.48353,0.07379,0.06412],"tcp_to_object_dist_end":0.08212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4959,0.00098,0.02414],"object_pos_start":[0.50018,0.00125,0.02413],"object_to_goal_dist_end":0.08262,"object_to_goal_dist_start":0.08279,"object_z_max":0.02456,"peak_contact_force":0.61749,"phase_name":"lift_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1013.0,"raw_peak_contact_force":68.7711,"tcp_end":[0.49601,-0.06464,0.1331],"tcp_start":[0.4994,-0.07961,0.03844],"tcp_to_object_dist_end":0.12719,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```