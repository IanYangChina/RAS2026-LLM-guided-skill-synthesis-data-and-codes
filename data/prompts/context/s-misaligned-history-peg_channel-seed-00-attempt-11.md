## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → lift → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.0280 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7  | 0.1778 | 0.72 | ❌ rejected |
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.2024 | 0.72 | ❌ rejected |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.1642 | 0.68 | ❌ rejected |
| 7 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | -0.2392 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.239) — your mutation base

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

- **Composite score**: -0.239
- **task_score** (E): 0.004
- **fitness_score**: 0.051  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1931 |
| descend_to_peg | 1.00 | 1.00 | 0.0724 |
| push_through | 0.00 | 1.00 | 0.0001 |
| lift_off | 1.00 | 1.00 | 0.1016 |
| retract_clear | 1.00 | 1.00 | 0.1804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.111, 0.133) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.536 | 2.179 |
| descend_to_peg | contact | 1.00 / force_exceeded | (0.495, 0.111, 0.133)→(0.495, 0.101, 0.063) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 25.881 | 25.881 |
| push_through | push | 0.00 / guard_failure | (0.495, 0.101, 0.063)→(0.495, 0.101, 0.063) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 24.936 | 34.703 |
| lift_off | lift | 1.00 / step_budget | (0.495, 0.101, 0.063)→(0.496, 0.100, 0.164) | (0.500, 0.080, 0.034)→(0.499, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.531 | 29.136 |
| retract_clear | retract | 1.00 / step_budget | (0.496, 0.100, 0.164)→(0.498, -0.061, 0.245) | (0.499, 0.080, 0.034)→(0.499, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.535 | 0.584 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.004
- alignment_error: None
- force_efficiency: 0.322
- terminal_score: 0.004
- phase_score: 0.084
- phase_breakdown.push_channel_score: 0.001
- phase_breakdown.reach_peg_score: 0.836

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.052
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.004
- **Median Q (composite search score)**: -0.239
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.220


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92453,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_arc_height":0.14232,"approach_peg.approach_speed":0.05875,"descend_to_peg.contact_force_threshold":11.42789,"lift_off.lift_speed":0.09568,"push_through.push_distance":0.09088,"push_through.push_speed":0.03013,"retract_clear.retract_arc_height":0.1555,"retract_clear.retract_speed":0.12022},"optimized_scores":{"best_composite_score":-0.24101,"best_fitness_score":0.04899,"best_task_score":0.00351},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50144,0.06073,0.00944],"force_p95":0.65281,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.65136,"mean_force":0.95307,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49879,0.08032,0.1124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49007,0.0613,0.00933],"force_p95":31.20611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.21723,"mean_force":23.06958,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50031,0.08062,0.06299]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.51013,0.07708,0.05914],"force_p95":31.64435,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.15741,"mean_force":9.33429,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49957,0.08022,0.06349]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.51096,0.07781,0.05851],"force_p95":30.78888,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.81416,"mean_force":22.66074,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50031,0.08062,0.06299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.50378,0.06161,0.00938],"force_p95":0.55518,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.96101,"mean_force":0.63021,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.50374,0.08007,0.0984]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51126,0.07802,0.05876],"force_p95":28.41199,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.41199,"mean_force":28.41199,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.50058,0.08073,0.06352]},{"body_a":"peg","body_b":"channel_base_body","contact_count":504.0,"contact_point_centroid":[0.50358,0.06161,0.00934],"force_p95":0.59035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56254,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5076,0.10609,0.24216]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49961,0.19769,0.29988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":468.0,"contact_point_centroid":[0.50287,0.06103,0.00939],"force_p95":0.55198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55603,"mean_force":0.54628,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.49816,0.0261,0.22361]}],"total_contact_groups":9},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50291,0.06093,0.03381],"final_tcp_position":[0.49809,-0.06048,0.24294],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":32.65136,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.0616,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54711,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":523.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.50929,0.07964,0.13541],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":340.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06161,0.0338],"object_pos_start":[0.50377,0.0616,0.03379],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14179,"object_z_max":0.03379,"peak_contact_force":28.96101,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":341.0,"raw_peak_contact_force":28.96101,"subtask_id":"reach_peg","tcp_end":[0.50057,0.08073,0.06334],"tcp_start":[0.50929,0.07964,0.13541],"tcp_to_object_dist_end":0.03534,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.50339,0.06142,0.03375],"object_pos_start":[0.50379,0.06161,0.0338],"object_to_goal_dist_end":0.1416,"object_to_goal_dist_start":0.14179,"object_z_max":0.0338,"peak_contact_force":24.33104,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":32.21723,"subtask_id":"push_channel","tcp_end":[0.50009,0.08037,0.06267],"tcp_start":[0.50012,0.08042,0.06273],"tcp_to_object_dist_end":0.03473,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":315.0,"n_steps_budget":810.0,"object_pos_end":[0.50305,0.0609,0.03394],"object_pos_start":[0.50332,0.06134,0.03377],"object_to_goal_dist_end":0.14107,"object_to_goal_dist_start":0.14151,"object_z_max":0.03548,"peak_contact_force":0.54509,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":329.0,"raw_peak_contact_force":32.65136,"tcp_end":[0.50012,0.08074,0.16404],"tcp_start":[0.50009,0.08037,0.06267],"tcp_to_object_dist_end":0.13163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":468.0,"n_steps_budget":930.0,"object_pos_end":[0.50291,0.06093,0.03381],"object_pos_start":[0.50305,0.0609,0.03394],"object_to_goal_dist_end":0.14109,"object_to_goal_dist_start":0.14107,"object_z_max":0.03394,"peak_contact_force":0.54242,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":468.0,"raw_peak_contact_force":0.55603,"tcp_end":[0.49809,-0.06048,0.24294],"tcp_start":[0.50012,0.08074,0.16404],"tcp_to_object_dist_end":0.24187,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31452,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_arc_height":0.17788,"approach_peg.approach_speed":0.13023,"descend_to_peg.contact_force_threshold":11.40746,"lift_off.lift_speed":0.08715,"push_through.push_distance":0.10897,"push_through.push_speed":0.03605,"retract_clear.retract_arc_height":0.15551,"retract_clear.retract_speed":0.12653},"optimized_scores":{"best_composite_score":-0.23804,"best_fitness_score":0.05196,"best_task_score":0.00351},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.49898,0.11531,0.00943],"force_p95":0.68749,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.90409,"mean_force":0.93821,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49555,0.13652,0.11216]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50547,0.1323,0.05909],"force_p95":32.38317,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.40463,"mean_force":9.25226,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.4959,0.13822,0.06282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.48811,0.1152,0.0093],"force_p95":31.47295,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.17133,"mean_force":22.52339,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49654,0.13874,0.06237]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50623,0.13301,0.05849],"force_p95":30.99033,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.72682,"mean_force":22.09738,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49654,0.13874,0.06237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.50104,0.11601,0.00942],"force_p95":0.6036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.84091,"mean_force":0.61604,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.49615,0.15131,0.09295]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50638,0.13321,0.05874],"force_p95":25.37886,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.37886,"mean_force":25.37886,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.49673,0.13903,0.06283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":346.0,"contact_point_centroid":[0.50085,0.11603,0.00934],"force_p95":0.65428,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56844,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49849,0.20648,0.20448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":647.0,"contact_point_centroid":[0.50032,0.11548,0.00943],"force_p95":0.611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64421,"mean_force":0.54234,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.49647,0.0607,0.24575]}],"total_contact_groups":8},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50029,0.11548,0.03388],"final_tcp_position":[0.49803,-0.06303,0.25006],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":33.90409,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":900.0,"object_pos_end":[0.50097,0.11623,0.03385],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19633,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.51055,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":346.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49793,0.16438,0.12616],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":347.0,"n_steps_budget":600.0,"object_pos_end":[0.50099,0.11603,0.03376],"object_pos_start":[0.50097,0.11623,0.03385],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19633,"object_z_max":0.03397,"peak_contact_force":25.84091,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":348.0,"raw_peak_contact_force":25.84091,"subtask_id":"reach_peg","tcp_end":[0.49673,0.13897,0.06267],"tcp_start":[0.49793,0.16438,0.12616],"tcp_to_object_dist_end":0.03715,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50065,0.11589,0.0337],"object_pos_start":[0.50099,0.11603,0.03376],"object_to_goal_dist_end":0.19599,"object_to_goal_dist_start":0.19613,"object_z_max":0.03376,"peak_contact_force":24.76148,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":32.17133,"subtask_id":"push_channel","tcp_end":[0.49636,0.13847,0.06208],"tcp_start":[0.49639,0.13852,0.06214],"tcp_to_object_dist_end":0.03652,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":323.0,"n_steps_budget":870.0,"object_pos_end":[0.50029,0.11548,0.03393],"object_pos_start":[0.50058,0.11582,0.03371],"object_to_goal_dist_end":0.19557,"object_to_goal_dist_start":0.19592,"object_z_max":0.03538,"peak_contact_force":0.50201,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":337.0,"raw_peak_contact_force":33.90409,"tcp_end":[0.49732,0.13537,0.16424],"tcp_start":[0.49636,0.13847,0.06208],"tcp_to_object_dist_end":0.13185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50029,0.11548,0.03388],"object_pos_start":[0.50029,0.11548,0.03393],"object_to_goal_dist_end":0.19557,"object_to_goal_dist_start":0.19557,"object_z_max":0.03409,"peak_contact_force":0.51221,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":647.0,"raw_peak_contact_force":0.64421,"tcp_end":[0.49803,-0.06303,0.25006],"tcp_start":[0.49732,0.13537,0.16424],"tcp_to_object_dist_end":0.28036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77119,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_arc_height":0.20631,"approach_peg.approach_speed":0.118,"descend_to_peg.contact_force_threshold":11.56786,"lift_off.lift_speed":0.13037,"push_through.push_distance":0.10061,"push_through.push_speed":0.04401,"retract_clear.retract_arc_height":0.16692,"retract_clear.retract_speed":0.11596},"optimized_scores":{"best_composite_score":-0.23856,"best_fitness_score":0.05144,"best_task_score":0.00448},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49367,0.0509,0.00937],"force_p95":35.72387,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.71907,"mean_force":22.56126,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48888,0.08383,0.06337]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49938,0.08083,0.05868],"force_p95":35.31049,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.31793,"mean_force":22.14434,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48888,0.08383,0.06337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":486.0,"contact_point_centroid":[0.49484,0.06381,0.0094],"force_p95":0.55042,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.83962,"mean_force":0.64508,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.48206,0.08597,0.09866]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49945,0.08079,0.05908],"force_p95":21.70698,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.39224,"mean_force":16.21834,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.48898,0.08395,0.06392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.49372,0.06321,0.00943],"force_p95":0.62121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.85352,"mean_force":0.76082,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48878,0.08289,0.11279]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49873,0.08054,0.05877],"force_p95":19.21354,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.26414,"mean_force":6.60568,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48818,0.08332,0.06347]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.49568,0.06391,0.00936],"force_p95":0.60961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56679,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4838,0.11909,0.23192]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49846,0.19518,0.29835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.49474,0.06289,0.00941],"force_p95":0.55067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55276,"mean_force":0.54507,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.49251,0.02589,0.22278]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47495,0.06271,0.0591],"force_p95":0.00078,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.00103,"mean_force":0.00017,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48742,0.08309,0.06631]}],"total_contact_groups":10},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4945,0.06278,0.03403],"final_tcp_position":[0.49703,-0.06063,0.24226],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":39.71907,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.49504,0.06406,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54985,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":427.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47749,0.0885,0.13878],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":486.0,"n_steps_budget":600.0,"object_pos_end":[0.49526,0.0636,0.03397],"object_pos_start":[0.49504,0.06406,0.03393],"object_to_goal_dist_end":0.14381,"object_to_goal_dist_start":0.14427,"object_z_max":0.034,"peak_contact_force":22.83962,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":489.0,"raw_peak_contact_force":22.83962,"subtask_id":"reach_peg","tcp_end":[0.48909,0.08397,0.06367],"tcp_start":[0.47749,0.0885,0.13878],"tcp_to_object_dist_end":0.03654,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.49495,0.06335,0.03381],"object_pos_start":[0.49526,0.0636,0.03397],"object_to_goal_dist_end":0.14358,"object_to_goal_dist_start":0.14381,"object_z_max":0.03397,"peak_contact_force":25.716,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":39.71907,"subtask_id":"push_channel","tcp_end":[0.48862,0.08351,0.06307],"tcp_start":[0.48867,0.08357,0.06312],"tcp_to_object_dist_end":0.03608,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":300.0,"n_steps_budget":600.0,"object_pos_end":[0.49447,0.06284,0.03403],"object_pos_start":[0.49492,0.06326,0.0338],"object_to_goal_dist_end":0.14307,"object_to_goal_dist_start":0.14348,"object_z_max":0.03491,"peak_contact_force":0.54639,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":316.0,"raw_peak_contact_force":20.85352,"tcp_end":[0.49149,0.08281,0.16437],"tcp_start":[0.48862,0.08351,0.06307],"tcp_to_object_dist_end":0.13189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":960.0,"object_pos_end":[0.4945,0.06278,0.03403],"object_pos_start":[0.49447,0.06284,0.03403],"object_to_goal_dist_end":0.14301,"object_to_goal_dist_start":0.14307,"object_z_max":0.03404,"peak_contact_force":0.54979,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":476.0,"raw_peak_contact_force":0.55276,"tcp_end":[0.49703,-0.06063,0.24226],"tcp_start":[0.49149,0.08281,0.16437],"tcp_to_object_dist_end":0.24206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```