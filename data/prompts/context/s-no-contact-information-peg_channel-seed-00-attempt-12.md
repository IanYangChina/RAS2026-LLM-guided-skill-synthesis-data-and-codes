## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1505 | 0.74 | ❌ rejected |
| 11 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1512 | 0.70 | ❌ rejected |
| 10 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1772 | 0.74 | ❌ rejected |
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1778 | 0.72 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2755 | 0.04 | ❌ rejected |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.150) — your mutation base

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

- **Composite score**: 0.150
- **task_score** (E): 0.736
- **fitness_score**: 0.520  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| insert_1 | 0.00 | 0.1730 |
| approach_1 | 1.00 | 0.1465 |
| push_1 | 0.33 | 0.1398 |
| retract_1 | 0.00 | 0.1266 |
| lift_1 | 0.00 | 0.1598 |
| insert_2 | 0.00 | 0.1659 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 |
| push_1 | push | 0.33 / step_budget | (0.497, 0.119, 0.043)→(0.497, -0.021, 0.037) | (0.500, 0.084, 0.033)→(0.507, -0.051, 0.038) | 0.165→0.033 |
| retract_1 | retract | 0.00 / step_budget | (0.497, -0.021, 0.037)→(0.495, 0.016, 0.158) | (0.507, -0.051, 0.038)→(0.503, -0.057, 0.031) | 0.033→0.030 |
| lift_1 | lift | 0.00 / step_budget | (0.495, 0.016, 0.158)→(0.403, -0.043, 0.273) | (0.503, -0.057, 0.031)→(0.504, -0.056, 0.031) | 0.030→0.030 |
| insert_2 | insert | 0.00 / step_budget | (0.403, -0.043, 0.273)→(0.462, -0.067, 0.120) | (0.504, -0.056, 0.031)→(0.503, -0.056, 0.031) | 0.030→0.030 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.888
- alignment_error: None
- terminal_score: 0.883
- phase_score: 0.510
- phase_breakdown.approach_score: 0.783
- phase_breakdown.push_score: 0.589

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.659
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.883
- **Median Q (composite search score)**: 0.127
- **K-run variance**: 0.0110
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55762,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04496,"push_1.push_distance":0.17841,"push_1.push_speed":0.06606,"retract_1.retract_height":0.1061,"retract_1.speed":0.0933},"optimized_scores":{"best_composite_score":0.28892,"best_fitness_score":0.65892,"best_task_score":0.8826},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54199,-0.04992,0.06],"force_p95":72.07578,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.95419,"mean_force":64.17004,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49731,-0.05386,0.03673]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":326.0,"contact_point_centroid":[0.54134,-0.00619,0.06],"force_p95":54.35588,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.7163,"mean_force":43.35099,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4965,-0.00384,0.03704]},{"body_a":"attachment","body_b":"peg","contact_count":723.0,"contact_point_centroid":[0.50244,-0.00182,0.04252],"force_p95":17.07595,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.09655,"mean_force":5.82519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49637,0.00962,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":49.0,"contact_point_centroid":[0.50682,-0.10039,0.06004],"force_p95":38.25759,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.75945,"mean_force":21.89126,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49713,-0.05267,0.03676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50633,-0.10035,0.06084],"force_p95":6.6232,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.1563,"mean_force":1.7719,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49656,-0.05286,0.03769]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50556,-0.06426,0.05589],"force_p95":3.35954,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.69803,"mean_force":1.46806,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49636,-0.05241,0.03807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":611.0,"contact_point_centroid":[0.50588,-0.02458,0.00983],"force_p95":13.21785,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.15913,"mean_force":5.4581,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49644,0.01793,0.03732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":339.0,"contact_point_centroid":[0.52506,-0.00907,0.02158],"force_p95":5.58464,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.48805,"mean_force":1.31849,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49627,0.0173,0.03711]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,-0.08301,0.06],"force_p95":3.924,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.98107,"mean_force":2.79729,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49732,-0.05386,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":974.0,"contact_point_centroid":[0.50576,-0.08052,0.00939],"force_p95":0.55341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92212,"mean_force":0.54946,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49466,-0.01824,0.10757]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50586,-0.0804,0.00938],"force_p95":0.55124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55819,"mean_force":0.5466,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44504,-0.0245,0.23348]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5058,-0.08047,0.00938],"force_p95":0.55121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55816,"mean_force":0.54662,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.42467,-0.06023,0.21253]}],"total_contact_groups":15},"final_pose_error":0.10647,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50584,-0.08043,0.03378],"final_tcp_position":[0.45541,-0.06856,0.136],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,-0.08232,0.03632],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00809,"object_to_goal_dist_start":0.14177,"object_z_max":0.03803,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49731,-0.05385,0.03673],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.03002,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50581,-0.08042,0.03379],"object_pos_start":[0.50682,-0.08232,0.03632],"object_to_goal_dist_end":0.00852,"object_to_goal_dist_start":0.00809,"object_z_max":0.03664,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49586,0.00303,0.18124],"tcp_start":[0.49731,-0.05385,0.03673],"tcp_to_object_dist_end":0.16973,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,-0.08046,0.03379],"object_pos_start":[0.50581,-0.08042,0.03379],"object_to_goal_dist_end":0.00854,"object_to_goal_dist_start":0.00852,"object_z_max":0.03379,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.39638,-0.05225,0.29049],"tcp_start":[0.49586,0.00303,0.18124],"tcp_to_object_dist_end":0.28049,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,-0.08043,0.03378],"object_pos_start":[0.50584,-0.08046,0.03379],"object_to_goal_dist_end":0.00854,"object_to_goal_dist_start":0.00854,"object_z_max":0.03379,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.45541,-0.06856,0.136],"tcp_start":[0.39638,-0.05225,0.29049],"tcp_to_object_dist_end":0.1146,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56506,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.01026,"push_1.push_distance":0.1956,"push_1.push_speed":0.06321,"retract_1.retract_height":0.08699,"retract_1.speed":0.07007},"optimized_scores":{"best_composite_score":0.12723,"best_fitness_score":0.49723,"best_task_score":0.82244},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":779.0,"contact_point_centroid":[0.50378,0.07057,0.00854],"force_p95":183.32884,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":186.33166,"mean_force":72.84249,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.1038,0.04349]},{"body_a":"attachment","body_b":"peg","contact_count":811.0,"contact_point_centroid":[0.50521,0.08968,0.04508],"force_p95":182.65141,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.85538,"mean_force":72.79373,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50032,0.0994,0.04321]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54167,0.00765,0.06],"force_p95":81.14666,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.84836,"mean_force":65.83133,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49671,0.0115,0.03716]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":143.0,"contact_point_centroid":[0.47384,0.08044,0.0425],"force_p95":55.04694,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.9722,"mean_force":20.3388,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50168,0.10722,0.04356]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.54149,0.02492,0.06],"force_p95":46.96082,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.91392,"mean_force":37.80903,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49647,0.02786,0.03716]},{"body_a":"peg","body_b":"world","contact_count":131.0,"contact_point_centroid":[0.50198,0.12554,-0.00016],"force_p95":20.52317,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.65446,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50041,0.1544,0.04504]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":199.0,"contact_point_centroid":[0.52513,0.02274,0.01967],"force_p95":7.11579,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.49073,"mean_force":2.02048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49627,0.0492,0.03725]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.5061,-0.01678,0.00941],"force_p95":0.55356,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18234,"mean_force":0.54762,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49401,0.02573,0.0945]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.50468,0.00097,0.05662],"force_p95":0.53204,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.6091,"mean_force":0.14603,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4952,0.01266,0.03965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50609,-0.01643,0.0094],"force_p95":0.55077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55519,"mean_force":0.5458,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45095,-0.00017,0.20536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50609,-0.01644,0.0094],"force_p95":0.55068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55512,"mean_force":0.5458,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43629,-0.04771,0.18622]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52508,-0.01442,0.01268],"force_p95":0.30599,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30628,"mean_force":0.29924,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49672,0.01149,0.03716]}],"total_contact_groups":16},"final_pose_error":0.08082,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50611,-0.01663,0.03394],"final_tcp_position":[0.46582,-0.06348,0.11135],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,-0.01681,0.03732],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.06361,"object_to_goal_dist_start":0.20832,"object_z_max":0.03779,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49672,0.0116,0.03716],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03017,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,-0.01663,0.03394],"object_pos_start":[0.50684,-0.01681,0.03732],"object_to_goal_dist_end":0.06395,"object_to_goal_dist_start":0.06361,"object_z_max":0.03732,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49506,0.03197,0.15278],"tcp_start":[0.49672,0.0116,0.03716],"tcp_to_object_dist_end":0.12887,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,-0.01663,0.03394],"object_pos_start":[0.5061,-0.01663,0.03394],"object_to_goal_dist_end":0.06395,"object_to_goal_dist_start":0.06395,"object_z_max":0.03394,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.40937,-0.03236,0.26265],"tcp_start":[0.49506,0.03197,0.15278],"tcp_to_object_dist_end":0.24883,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,-0.01663,0.03394],"object_pos_start":[0.50611,-0.01663,0.03394],"object_to_goal_dist_end":0.06395,"object_to_goal_dist_start":0.06395,"object_z_max":0.03394,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.46582,-0.06348,0.11135],"tcp_start":[0.40937,-0.03236,0.26265],"tcp_to_object_dist_end":0.09905,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8296,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.07135,"push_1.push_distance":0.09842,"push_1.push_speed":0.0996,"retract_1.retract_height":0.15388,"retract_1.speed":0.06205},"optimized_scores":{"best_composite_score":0.03533,"best_fitness_score":0.40533,"best_task_score":0.50255},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.53785,0.02059,0.06],"force_p95":79.90256,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.53323,"mean_force":56.19756,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49267,0.02375,0.03754]},{"body_a":"attachment","body_b":"peg","contact_count":668.0,"contact_point_centroid":[0.49944,0.02314,0.03662],"force_p95":79.04968,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.29877,"mean_force":47.18802,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49217,0.03161,0.03763]},{"body_a":"peg","body_b":"channel_base_body","contact_count":715.0,"contact_point_centroid":[0.50714,0.00339,0.00973],"force_p95":50.96723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.40037,"mean_force":26.79309,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.492,0.03567,0.0378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":585.0,"contact_point_centroid":[0.52561,0.00607,0.02417],"force_p95":51.12304,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.90703,"mean_force":35.64344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49261,0.02487,0.03755]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54123,-0.02576,0.05999],"force_p95":54.03532,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.62453,"mean_force":48.73245,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4965,-0.02014,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":976.0,"contact_point_centroid":[0.50033,-0.05596,0.00952],"force_p95":0.65315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.84501,"mean_force":0.48099,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4937,0.00045,0.08744]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50194,-0.02885,0.03511],"force_p95":3.96553,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.74822,"mean_force":1.16045,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49581,-0.01967,0.03782]},{"body_a":"peg","body_b":"link7","contact_count":99.0,"contact_point_centroid":[0.52004,0.02243,0.06817],"force_p95":6.37133,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.725,"mean_force":5.33678,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49077,0.04786,0.0377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4978,-0.07186,0.00805],"force_p95":0.70973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.76138,"mean_force":0.61781,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43155,-0.05588,0.18925]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49906,-0.07232,0.00808],"force_p95":0.73787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.72381,"mean_force":0.62711,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44717,-0.01553,0.20057]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.475,-0.09394,0.02419],"force_p95":6.53936,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.56056,"mean_force":2.15142,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43561,-0.05741,0.17902]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,-0.09446,0.02413],"force_p95":6.48468,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.51278,"mean_force":3.41989,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45708,-0.009,0.18536]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52501,-0.05048,0.02435],"force_p95":5.07526,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.22876,"mean_force":1.55761,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42711,-0.0285,0.23006]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52517,-0.04034,0.02314],"force_p95":2.9431,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.3803,"mean_force":0.72255,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,-0.01979,0.03768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_base_body","contact_count":587.0,"contact_point_centroid":[0.50753,-0.10002,0.0248],"force_p95":0.35114,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59407,"mean_force":0.24286,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49339,-0.00045,0.08141]}],"total_contact_groups":20},"final_pose_error":0.08259,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49641,-0.07188,0.02413],"final_tcp_position":[0.46339,-0.06759,0.11299],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":748.0,"n_steps_budget":870.0,"object_pos_end":[0.50776,-0.05425,0.04012],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.0269,"object_to_goal_dist_start":0.14379,"object_z_max":0.04038,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49651,-0.02002,0.0371],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.03615,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49681,-0.07247,0.02419],"object_pos_start":[0.50776,-0.05425,0.04012],"object_to_goal_dist_end":0.0178,"object_to_goal_dist_start":0.0269,"object_z_max":0.04077,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49461,0.01345,0.13894],"tcp_start":[0.49651,-0.02002,0.0371],"tcp_to_object_dist_end":0.14337,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50081,-0.07221,0.02414],"object_pos_start":[0.49681,-0.07247,0.02419],"object_to_goal_dist_end":0.01769,"object_to_goal_dist_start":0.0178,"object_z_max":0.02457,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.40238,-0.04459,0.26686],"tcp_start":[0.49461,0.01345,0.13894],"tcp_to_object_dist_end":0.26337,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49641,-0.07188,0.02413],"object_pos_start":[0.50081,-0.07221,0.02414],"object_to_goal_dist_end":0.01818,"object_to_goal_dist_start":0.01769,"object_z_max":0.02431,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.46339,-0.06759,0.11299],"tcp_start":[0.40238,-0.04459,0.26686],"tcp_to_object_dist_end":0.09489,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```