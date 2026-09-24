## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1786 | 0.06 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2508 | 0.81 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0554 | 0.77 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2295 | 0.81 | ❌ rejected |
| 3 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 10 | -0.5097 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.179) — your mutation base

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

- **Composite score**: -0.179
- **task_score** (E): 0.058
- **fitness_score**: 0.061  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1816 |
| approach_1 | 1.00 | 1.00 | 0.0922 |
| contact_1 | 1.00 | 1.00 | 0.0027 |
| push_1 | 1.00 | 1.00 | 0.0327 |
| retract_1 | 1.00 | 1.00 | 0.1208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.094, 0.154) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.546 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.499, 0.094, 0.154)→(0.496, 0.082, 0.063) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.567 | 0.580 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.082, 0.063)→(0.495, 0.081, 0.060) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 16.422 | 16.422 |
| push_1 | push | 1.00 / time_limit | (0.495, 0.081, 0.060)→(0.508, 0.078, 0.072) | (0.500, 0.081, 0.034)→(0.497, 0.069, 0.029) | 0.161→0.149 | 1.00 / 2.333 | 230.273 | 706.938 |
| retract_1 | retract | 1.00 / step_budget | (0.508, 0.078, 0.072)→(0.507, 0.078, 0.192) | (0.497, 0.069, 0.029)→(0.496, 0.069, 0.031) | 0.149→0.149 | 1.00 / 1.000 | 0.580 | 129.594 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.119
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.107
- phase_score: 0.064
- phase_breakdown.reach_pre_contact_score: 0.215
- phase_breakdown.reach_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.081
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.107
- **Median Q (composite search score)**: -0.177
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44295,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00165,"approach_1.approach_speed":0.06017,"contact_1.contact_force_threshold":12.72978,"push_1.push_distance":0.13977,"push_1.push_speed":0.04922,"push_1.push_time":4.5358,"retract_1.retract_height":0.11151,"retract_1.retract_speed":0.08617},"optimized_scores":{"best_composite_score":-0.20045,"best_fitness_score":0.03955,"best_task_score":0.00362},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":921.0,"contact_point_centroid":[0.52514,0.11993,0.05993],"force_p95":354.91573,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":767.8436,"mean_force":308.90604,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51869,0.06857,0.09217]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52702,0.06068,0.05945],"force_p95":688.41564,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":761.43826,"mean_force":415.46167,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51935,0.05315,0.06274]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.51531,0.06683,0.05788],"force_p95":347.89912,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":418.33898,"mean_force":161.43581,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51246,0.05865,0.06343]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50026,0.06092,0.00931],"force_p95":1.15395,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":328.38092,"mean_force":8.06483,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51845,0.06765,0.09011]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52672,0.05728,0.05696],"force_p95":122.50969,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.63076,"mean_force":28.80558,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51687,0.05296,0.06064]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52501,0.11995,0.05995],"force_p95":81.69649,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.70673,"mean_force":58.29372,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52151,0.06971,0.09197]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50268,0.05959,0.00938],"force_p95":5.1692,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.74765,"mean_force":1.48984,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50035,0.06304,0.06177]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51184,0.06243,0.05876],"force_p95":13.29526,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.29526,"mean_force":13.29526,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49998,0.06293,0.06053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50355,0.06154,0.00933],"force_p95":0.60639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56907,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50395,0.13563,0.22185]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49989,0.19828,0.2981]},{"body_a":"peg","body_b":"channel_base_body","contact_count":258.0,"contact_point_centroid":[0.49958,0.06085,0.00937],"force_p95":0.60118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60402,"mean_force":0.54661,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52012,0.06958,0.1366]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.50381,0.06167,0.00938],"force_p95":0.55012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55166,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50387,0.06973,0.10773]}],"total_contact_groups":12},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49972,0.06079,0.03379],"final_tcp_position":[0.52004,0.06977,0.18363],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":767.8436,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.06159,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54261,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":378.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_contact","tcp_end":[0.50873,0.07638,0.15271],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06156,0.03378],"object_pos_start":[0.50374,0.06159,0.03378],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14178,"object_z_max":0.03378,"peak_contact_force":0.54565,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":304.0,"raw_peak_contact_force":0.55166,"subtask_id":"reach_pre_contact","tcp_end":[0.50087,0.06321,0.06305],"tcp_start":[0.50873,0.07638,0.15271],"tcp_to_object_dist_end":0.02946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.06158,0.03376],"object_pos_start":[0.50376,0.06156,0.03378],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14175,"object_z_max":0.03378,"peak_contact_force":13.74765,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":13.74765,"tcp_end":[0.49995,0.06292,0.06035],"tcp_start":[0.50087,0.06321,0.06305],"tcp_to_object_dist_end":0.02689,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49969,0.06082,0.03377],"object_pos_start":[0.50375,0.06158,0.03376],"object_to_goal_dist_end":0.14096,"object_to_goal_dist_start":0.14177,"object_z_max":0.03485,"peak_contact_force":293.76557,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2021.0,"raw_peak_contact_force":767.8436,"tcp_end":[0.52152,0.06972,0.09191],"tcp_start":[0.49995,0.06292,0.06035],"tcp_to_object_dist_end":0.06274,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":258.0,"n_steps_budget":810.0,"object_pos_end":[0.49972,0.06079,0.03379],"object_pos_start":[0.49969,0.06082,0.03377],"object_to_goal_dist_end":0.14093,"object_to_goal_dist_start":0.14096,"object_z_max":0.03379,"peak_contact_force":0.55055,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":262.0,"raw_peak_contact_force":85.70673,"tcp_end":[0.52004,0.06977,0.18363],"tcp_start":[0.52152,0.06972,0.09191],"tcp_to_object_dist_end":0.15148,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37736,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00284,"approach_1.approach_speed":0.07905,"contact_1.contact_force_threshold":7.53526,"push_1.push_distance":0.13805,"push_1.push_speed":0.01883,"push_1.push_time":9.66006,"retract_1.retract_height":0.14096,"retract_1.retract_speed":0.08837},"optimized_scores":{"best_composite_score":-0.15857,"best_fitness_score":0.08143,"best_task_score":0.10703},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52737,0.11713,0.05942],"force_p95":755.45534,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":813.07544,"mean_force":430.74981,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51916,0.11032,0.06246]},{"body_a":"attachment","body_b":"peg","contact_count":971.0,"contact_point_centroid":[0.49963,0.09691,0.05266],"force_p95":174.12964,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":416.65875,"mean_force":130.35402,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49966,0.09036,0.06178]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49908,0.09637,0.00757],"force_p95":172.19985,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":347.9646,"mean_force":124.43897,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50028,0.09093,0.06185]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":503.0,"contact_point_centroid":[0.46779,0.11994,0.05845],"force_p95":188.6304,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.65232,"mean_force":138.93791,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49824,0.08031,0.06123]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.4676,0.11996,0.06],"force_p95":164.92646,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.93683,"mean_force":115.10014,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49926,0.08086,0.06142]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52672,0.11232,0.05634],"force_p95":104.05662,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.40322,"mean_force":23.13878,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51753,0.10872,0.06051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.49357,0.09603,0.00929],"force_p95":0.64969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.95301,"mean_force":1.5902,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49772,0.08049,0.12062]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49864,0.08118,0.05506],"force_p95":93.25231,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.5551,"mean_force":11.43833,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49867,0.08097,0.06525]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":449.0,"contact_point_centroid":[0.47412,0.10603,0.02025],"force_p95":49.88679,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.60171,"mean_force":19.42042,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49977,0.09807,0.06223]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.525,0.11981,0.05058],"force_p95":14.05783,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.31419,"mean_force":2.29592,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49709,0.07948,0.06149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.49754,0.11613,0.00939],"force_p95":5.21372,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.73379,"mean_force":1.49259,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49685,0.11647,0.0618]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50835,0.11593,0.05879],"force_p95":13.32354,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.32354,"mean_force":13.32354,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49649,0.11634,0.06053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.50088,0.11599,0.00937],"force_p95":0.70024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56867,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49993,0.16235,0.22531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":297.0,"contact_point_centroid":[0.50098,0.11612,0.00942],"force_p95":0.61016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63629,"mean_force":0.54263,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49818,0.1214,0.10951]}],"total_contact_groups":14},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49377,0.09694,0.03378],"final_tcp_position":[0.49778,0.08072,0.18261],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":813.07544,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11605,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.549,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":294.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.50087,0.12651,0.15634],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":297.0,"n_steps_budget":840.0,"object_pos_end":[0.50088,0.11605,0.03385],"object_pos_start":[0.50092,0.11605,0.03383],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19615,"object_z_max":0.03395,"peak_contact_force":0.61617,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":297.0,"raw_peak_contact_force":0.63629,"subtask_id":"reach_pre_contact","tcp_end":[0.49737,0.11667,0.06312],"tcp_start":[0.50087,0.12651,0.15634],"tcp_to_object_dist_end":0.02949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.50091,0.11607,0.03381],"object_pos_start":[0.50088,0.11605,0.03385],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19615,"object_z_max":0.03385,"peak_contact_force":13.73379,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":13.73379,"tcp_end":[0.49646,0.11633,0.06034],"tcp_start":[0.49737,0.11667,0.06312],"tcp_to_object_dist_end":0.0269,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49384,0.09688,0.03049],"object_pos_start":[0.50091,0.11607,0.03381],"object_to_goal_dist_end":0.17724,"object_to_goal_dist_start":0.19617,"object_z_max":0.03502,"peak_contact_force":180.94142,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3004.0,"raw_peak_contact_force":813.07544,"tcp_end":[0.49926,0.08082,0.0614],"tcp_start":[0.49646,0.11633,0.06034],"tcp_to_object_dist_end":0.03525,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":338.0,"n_steps_budget":990.0,"object_pos_end":[0.49377,0.09694,0.03378],"object_pos_start":[0.49384,0.09688,0.03049],"object_to_goal_dist_end":0.17716,"object_to_goal_dist_start":0.17724,"object_z_max":0.03384,"peak_contact_force":0.54676,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":372.0,"raw_peak_contact_force":169.93683,"tcp_end":[0.49778,0.08072,0.18261],"tcp_start":[0.49926,0.08082,0.0614],"tcp_to_object_dist_end":0.14976,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42211,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00781,"approach_1.approach_speed":0.0325,"contact_1.contact_force_threshold":9.61016,"push_1.push_distance":0.17545,"push_1.push_speed":0.03054,"push_1.push_time":5.17355,"retract_1.retract_height":0.16914,"retract_1.retract_speed":0.0729},"optimized_scores":{"best_composite_score":-0.1767,"best_fitness_score":0.0633,"best_task_score":0.06373},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52605,0.05753,0.05983],"force_p95":532.17116,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":539.8958,"mean_force":320.11287,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51436,0.05631,0.05632]},{"body_a":"attachment","body_b":"peg","contact_count":141.0,"contact_point_centroid":[0.5046,0.08212,0.05284],"force_p95":262.61722,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":358.3678,"mean_force":183.28333,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50615,0.07532,0.0548]},{"body_a":"peg","body_b":"channel_base_body","contact_count":976.0,"contact_point_centroid":[0.50131,0.05105,0.00802],"force_p95":218.72145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":358.22081,"mean_force":25.92351,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50349,0.08112,0.06174]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":870.0,"contact_point_centroid":[0.47008,0.11989,0.05999],"force_p95":250.06033,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.57461,"mean_force":224.03289,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50291,0.08203,0.06236]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.52739,0.11944,0.05987],"force_p95":38.90959,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.23787,"mean_force":10.27629,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50009,0.07951,0.05217]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.46877,0.11996,0.06],"force_p95":128.02657,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.13909,"mean_force":74.77344,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50395,0.08404,0.06139]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":81.0,"contact_point_centroid":[0.47428,0.05907,0.02287],"force_p95":99.42831,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.12743,"mean_force":67.75283,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5057,0.08408,0.05344]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52569,0.06478,0.04021],"force_p95":57.97954,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.5603,"mean_force":11.92872,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50754,0.06661,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.5064,0.06703,0.0094],"force_p95":11.16731,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.7835,"mean_force":2.47634,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49015,0.06507,0.06164]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5017,0.06376,0.05896],"force_p95":21.3032,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.3032,"mean_force":21.3032,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4899,0.06497,0.06071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.49489,0.04904,0.00808],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.27602,"mean_force":0.73652,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50252,0.08384,0.13424]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47499,0.0244,0.02442],"force_p95":8.50422,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.79635,"mean_force":3.83352,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50241,0.08379,0.14962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.49547,0.06399,0.00936],"force_p95":0.62706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56988,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49295,0.13618,0.22138]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49941,0.19704,0.29628]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.49504,0.06372,0.0094],"force_p95":0.55025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54566,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48794,0.07189,0.10783]}],"total_contact_groups":15},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49486,0.04794,0.02415],"final_tcp_position":[0.50267,0.08421,0.21072],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":539.8958,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.49502,0.06371,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5454,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":376.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.48759,0.07865,0.1533],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.49519,0.06366,0.03397],"object_pos_start":[0.49502,0.06371,0.03392],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14392,"object_z_max":0.03397,"peak_contact_force":0.5377,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_pre_contact","tcp_end":[0.49054,0.06522,0.06258],"tcp_start":[0.48759,0.07865,0.1533],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.49502,0.0641,0.03397],"object_pos_start":[0.49519,0.06366,0.03397],"object_to_goal_dist_end":0.14431,"object_to_goal_dist_start":0.14386,"object_z_max":0.03397,"peak_contact_force":21.7835,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12.0,"raw_peak_contact_force":21.7835,"tcp_end":[0.48986,0.06496,0.06053],"tcp_start":[0.49054,0.06522,0.06258],"tcp_to_object_dist_end":0.02707,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49688,0.04916,0.0241],"object_pos_start":[0.49502,0.0641,0.03397],"object_to_goal_dist_end":0.13017,"object_to_goal_dist_start":0.14431,"object_z_max":0.03592,"peak_contact_force":216.11195,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2155.0,"raw_peak_contact_force":539.8958,"tcp_end":[0.50397,0.08401,0.0614],"tcp_start":[0.48986,0.06496,0.06053],"tcp_to_object_dist_end":0.05154,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.49486,0.04794,0.02415],"object_pos_start":[0.49688,0.04916,0.0241],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.13017,"object_z_max":0.02464,"peak_contact_force":0.64352,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":438.0,"raw_peak_contact_force":133.13909,"tcp_end":[0.50267,0.08421,0.21072],"tcp_start":[0.50397,0.08401,0.0614],"tcp_to_object_dist_end":0.19022,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```