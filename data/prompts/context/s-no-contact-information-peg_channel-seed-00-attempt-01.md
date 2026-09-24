## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2176 | 0.78 | ✅ accepted |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1861 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.778, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.218) — your mutation base

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

- **Composite score**: 0.218
- **task_score** (E): 0.778
- **fitness_score**: 0.588  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| insert_1 | 0.00 | 0.1730 |
| approach_1 | 1.00 | 0.1465 |
| push_1 | 0.33 | 0.1561 |
| retract_1 | 0.00 | 0.0992 |
| lift_1 | 0.00 | 0.1477 |
| insert_2 | 0.00 | 0.1650 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 |
| push_1 | push | 0.33 / step_budget | (0.497, 0.119, 0.043)→(0.495, -0.037, 0.037) | (0.500, 0.084, 0.033)→(0.506, -0.060, 0.030) | 0.165→0.030 |
| retract_1 | retract | 0.00 / step_budget | (0.495, -0.037, 0.037)→(0.494, 0.001, 0.128) | (0.506, -0.060, 0.030)→(0.502, -0.058, 0.031) | 0.030→0.028 |
| lift_1 | lift | 0.00 / step_budget | (0.494, 0.001, 0.128)→(0.414, -0.042, 0.244) | (0.502, -0.058, 0.031)→(0.501, -0.058, 0.031) | 0.028→0.028 |
| insert_2 | insert | 0.00 / step_budget | (0.414, -0.042, 0.244)→(0.473, -0.069, 0.092) | (0.501, -0.058, 0.031)→(0.501, -0.058, 0.031) | 0.028→0.028 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.881
- alignment_error: None
- terminal_score: 0.881
- phase_score: 0.518
- phase_breakdown.approach_score: 0.783
- phase_breakdown.push_score: 0.603

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.663
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.881
- **Median Q (composite search score)**: 0.207
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.415


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50562,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04855,"push_1.push_distance":0.13884,"push_1.push_speed":0.07192,"retract_1.retract_height":0.09047,"retract_1.speed":0.04182},"optimized_scores":{"best_composite_score":0.29342,"best_fitness_score":0.66342,"best_task_score":0.88128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":352.0,"contact_point_centroid":[0.54163,-0.00852,0.06],"force_p95":62.61163,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.60117,"mean_force":48.13352,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49682,-0.00632,0.03699]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5426,-0.05116,0.05999],"force_p95":65.9844,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.9138,"mean_force":59.83336,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49796,-0.05504,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":750.0,"contact_point_centroid":[0.50253,-0.00196,0.04247],"force_p95":27.21905,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.06663,"mean_force":7.64224,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49662,0.00948,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":69.0,"contact_point_centroid":[0.50648,-0.10044,0.05898],"force_p95":56.48232,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.65535,"mean_force":26.65376,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49765,-0.05303,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.50531,-0.10055,0.06112],"force_p95":13.57147,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.17313,"mean_force":3.44548,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49679,-0.05346,0.03778]},{"body_a":"attachment","body_b":"peg","contact_count":51.0,"contact_point_centroid":[0.50485,-0.06445,0.0546],"force_p95":8.98551,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.08164,"mean_force":2.88706,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49643,-0.05265,0.03849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":623.0,"contact_point_centroid":[0.5057,-0.0248,0.00983],"force_p95":16.31557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.04862,"mean_force":6.44112,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49665,0.01784,0.0373]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":390.0,"contact_point_centroid":[0.52506,-0.00902,0.02253],"force_p95":5.78674,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.80262,"mean_force":1.64027,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49648,0.01756,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":956.0,"contact_point_centroid":[0.50657,-0.07964,0.0094],"force_p95":0.5547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96444,"mean_force":0.54922,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,-0.02765,0.08207]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5067,-0.0794,0.00938],"force_p95":0.54967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55145,"mean_force":0.54657,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45344,-0.02847,0.18232]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5067,-0.07941,0.00938],"force_p95":0.54965,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55142,"mean_force":0.54657,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44265,-0.05893,0.16577]}],"total_contact_groups":14},"final_pose_error":0.05715,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50674,-0.07942,0.03379],"final_tcp_position":[0.47358,-0.07091,0.08985],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50555,-0.08382,0.0362],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00773,"object_to_goal_dist_start":0.14177,"object_z_max":0.03783,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49796,-0.05499,0.03665],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.02981,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,-0.07936,0.03379],"object_pos_start":[0.50555,-0.08382,0.0362],"object_to_goal_dist_end":0.00917,"object_to_goal_dist_start":0.00773,"object_z_max":0.03718,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49523,-0.00962,0.126],"tcp_start":[0.49796,-0.05499,0.03665],"tcp_to_object_dist_end":0.11618,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,-0.07939,0.03379],"object_pos_start":[0.50671,-0.07936,0.03379],"object_to_goal_dist_end":0.00918,"object_to_goal_dist_start":0.00917,"object_z_max":0.03379,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.41452,-0.0474,0.24316],"tcp_start":[0.49523,-0.00962,0.126],"tcp_to_object_dist_end":0.23101,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,-0.07942,0.03379],"object_pos_start":[0.50674,-0.07939,0.03379],"object_to_goal_dist_end":0.00918,"object_to_goal_dist_start":0.00918,"object_z_max":0.03379,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.47358,-0.07091,0.08985],"tcp_start":[0.41452,-0.0474,0.24316],"tcp_to_object_dist_end":0.06569,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50923,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04596,"push_1.push_distance":0.19435,"push_1.push_speed":0.0711,"retract_1.retract_height":0.09918,"retract_1.speed":0.02294},"optimized_scores":{"best_composite_score":0.15208,"best_fitness_score":0.52208,"best_task_score":0.87307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":826.0,"contact_point_centroid":[0.50005,0.06849,0.00844],"force_p95":184.29571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.18813,"mean_force":73.1579,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50089,0.09959,0.0437]},{"body_a":"attachment","body_b":"peg","contact_count":788.0,"contact_point_centroid":[0.50375,0.09353,0.04446],"force_p95":184.00062,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.78432,"mean_force":81.08293,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50114,0.10321,0.04405]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":311.0,"contact_point_centroid":[0.47419,0.05194,0.03525],"force_p95":65.61362,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.85476,"mean_force":15.16169,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49983,0.07903,0.04108]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.54155,0.02351,0.06],"force_p95":51.43559,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.37177,"mean_force":39.58689,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49654,0.02652,0.03715]},{"body_a":"peg","body_b":"world","contact_count":138.0,"contact_point_centroid":[0.50194,0.12552,-0.00016],"force_p95":19.03442,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.15515,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50032,0.15483,0.04494]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5417,0.00345,0.05999],"force_p95":43.94164,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.01303,"mean_force":41.91062,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49677,0.00752,0.03714]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50269,-0.02334,0.00951],"force_p95":0.55495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70787,"mean_force":0.53839,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49388,0.02118,0.08301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50267,-0.023,0.00947],"force_p95":0.54441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54734,"mean_force":0.54019,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44261,-0.04676,0.16737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50254,-0.02283,0.00948],"force_p95":0.5434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54582,"mean_force":0.53941,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45359,9e-05,0.18459]}],"total_contact_groups":13},"final_pose_error":0.06149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50181,-0.02365,0.03465],"final_tcp_position":[0.47256,-0.06519,0.093],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50053,-0.02241,0.03574],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.05775,"object_to_goal_dist_start":0.20832,"object_z_max":0.03602,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49683,0.00776,0.03717],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03043,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50388,-0.02331,0.03487],"object_pos_start":[0.50053,-0.02241,0.03574],"object_to_goal_dist_end":0.05706,"object_to_goal_dist_start":0.05775,"object_z_max":0.03574,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49461,0.02905,0.13033],"tcp_start":[0.49683,0.00776,0.03717],"tcp_to_object_dist_end":0.10927,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50216,-0.02404,0.03471],"object_pos_start":[0.50388,-0.02331,0.03487],"object_to_goal_dist_end":0.05625,"object_to_goal_dist_start":0.05706,"object_z_max":0.03487,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.41541,-0.0288,0.24336],"tcp_start":[0.49461,0.02905,0.13033],"tcp_to_object_dist_end":0.22602,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50181,-0.02365,0.03465],"object_pos_start":[0.50216,-0.02404,0.03471],"object_to_goal_dist_end":0.05663,"object_to_goal_dist_start":0.05625,"object_z_max":0.03471,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.47256,-0.06519,0.093],"tcp_start":[0.41541,-0.0288,0.24336],"tcp_to_object_dist_end":0.07737,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48276,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.01017,"push_1.push_distance":0.19141,"push_1.push_speed":0.09985,"retract_1.retract_height":0.05321,"retract_1.speed":0.02028},"optimized_scores":{"best_composite_score":0.20734,"best_fitness_score":0.57734,"best_task_score":0.57846},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":364.0,"contact_point_centroid":[0.53458,-0.01569,0.05999],"force_p95":175.08643,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.20856,"mean_force":109.68073,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4892,-0.01155,0.03826]},{"body_a":"attachment","body_b":"peg","contact_count":919.0,"contact_point_centroid":[0.49755,0.0066,0.03593],"force_p95":121.51832,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.43248,"mean_force":71.61826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48924,0.01199,0.03813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.50856,-0.0064,0.00938],"force_p95":87.21649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.36316,"mean_force":41.02105,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48925,0.01583,0.03824]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":848.0,"contact_point_centroid":[0.52625,-0.00801,0.02759],"force_p95":97.82483,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.08819,"mean_force":60.06685,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4893,0.00618,0.03812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49744,-0.06835,0.00805],"force_p95":46.89726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.51234,"mean_force":6.07062,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48915,-0.03652,0.08116]},{"body_a":"attachment","body_b":"peg","contact_count":142.0,"contact_point_centroid":[0.49939,-0.06105,0.03878],"force_p95":75.05473,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.4493,"mean_force":34.8234,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48894,-0.0608,0.04389]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":150.0,"contact_point_centroid":[0.52557,-0.06143,0.02372],"force_p95":46.88103,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.58445,"mean_force":20.95213,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48889,-0.06046,0.04421]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53635,-0.06133,0.06],"force_p95":55.63204,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.91239,"mean_force":53.10883,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49102,-0.06457,0.03792]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53425,-0.1,0.06499],"force_p95":44.40686,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.89307,"mean_force":22.97468,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49101,-0.06466,0.03793]},{"body_a":"peg","body_b":"link7","contact_count":348.0,"contact_point_centroid":[0.52006,0.01087,0.06779],"force_p95":23.51135,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.55271,"mean_force":11.77928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48941,0.0357,0.03791]},{"body_a":"peg","body_b":"world","contact_count":13.0,"contact_point_centroid":[0.51103,-0.06254,-0.00023],"force_p95":17.118,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.70908,"mean_force":3.82004,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49049,-0.06188,0.0381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49433,-0.07169,0.00807],"force_p95":0.717,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.89869,"mean_force":0.67439,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44985,-0.0326,0.18374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49328,-0.07134,0.0081],"force_p95":0.68435,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76627,"mean_force":0.76315,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44027,-0.06053,0.16836]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47499,-0.08187,0.02433],"force_p95":9.5276,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.7184,"mean_force":2.91234,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4891,-0.03234,0.08593]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":18.0,"contact_point_centroid":[0.47497,-0.06054,0.02449],"force_p95":9.41502,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.4534,"mean_force":4.17231,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.41857,-0.04708,0.23387]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47498,-0.06865,0.0246],"force_p95":9.11209,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.28095,"mean_force":4.06514,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.4558,-0.06587,0.13083]}],"total_contact_groups":20},"final_pose_error":0.06117,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49347,-0.07106,0.02413],"final_tcp_position":[0.47153,-0.07123,0.09343],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51074,-0.07266,0.01763],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02588,"object_to_goal_dist_start":0.14379,"object_z_max":0.03991,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49105,-0.0642,0.03794],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02952,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49465,-0.07159,0.02413],"object_pos_start":[0.51074,-0.07266,0.01763],"object_to_goal_dist_end":0.01874,"object_to_goal_dist_start":0.02588,"object_z_max":0.02909,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49084,-0.01507,0.12705],"tcp_start":[0.49105,-0.0642,0.03794],"tcp_to_object_dist_end":0.11748,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49318,-0.07126,0.02439],"object_pos_start":[0.49465,-0.07159,0.02413],"object_to_goal_dist_end":0.01914,"object_to_goal_dist_start":0.01874,"object_z_max":0.02508,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.41176,-0.05025,0.24489],"tcp_start":[0.49084,-0.01507,0.12705],"tcp_to_object_dist_end":0.23599,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49347,-0.07106,0.02413],"object_pos_start":[0.49318,-0.07126,0.02439],"object_to_goal_dist_end":0.01935,"object_to_goal_dist_start":0.01914,"object_z_max":0.02522,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.47153,-0.07123,0.09343],"tcp_start":[0.41176,-0.05025,0.24489],"tcp_to_object_dist_end":0.07269,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```