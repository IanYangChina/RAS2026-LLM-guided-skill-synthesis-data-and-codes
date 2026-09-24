## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2378 | 0.42 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0520 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1883 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.238) — your mutation base

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

- **Composite score**: 0.238
- **task_score** (E): 0.417
- **fitness_score**: 0.348  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1810 |
| descend_1 | 1.00 | 1.00 | 0.0839 |
| push_1 | 0.67 | 1.00 | 0.1703 |
| retract_1 | 1.00 | 1.00 | 0.0879 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.107, 0.147) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 23.027 | 23.027 |
| descend_1 | descend | 1.00 / force_exceeded | (0.495, 0.107, 0.147)→(0.495, 0.101, 0.063) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.667 | 289.890 | 311.398 |
| push_1 | push | 0.67 / step_budget | (0.495, 0.101, 0.063)→(0.501, -0.068, 0.039) | (0.500, 0.081, 0.034)→(0.500, 0.006, 0.024) | 0.161→0.088 | 1.00 / 1.000 | 0.324 | 98.688 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.068, 0.039)→(0.497, -0.077, 0.124) | (0.500, 0.006, 0.024)→(0.501, 0.005, 0.024) | 0.088→0.087 | 1.00 / 1.000 | 0.541 | 2.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.473
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.473
- phase_score: 0.328
- phase_breakdown.reach_contact_score: 0.580
- phase_breakdown.reach_goal_score: 0.220

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.386
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.473
- **Median Q (composite search score)**: 0.245
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16996,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06762,"descend_1.force_threshold":8.468,"descend_1.speed":0.03561,"push_1.push_distance":0.21698,"push_1.speed":0.01495,"retract_1.speed":0.08245},"optimized_scores":{"best_composite_score":0.24523,"best_fitness_score":0.35523,"best_task_score":0.46163},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":536.0,"contact_point_centroid":[0.54488,-0.10001,0.06494],"force_p95":320.08573,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.29602,"mean_force":254.30637,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50182,-0.07932,0.03931]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":506.0,"contact_point_centroid":[0.52504,-0.07985,0.05998],"force_p95":215.70155,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.93031,"mean_force":154.78758,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5019,-0.07954,0.03939]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52502,-0.08104,0.05999],"force_p95":131.36377,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.8299,"mean_force":41.80474,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50164,-0.08091,0.04055]},{"body_a":"attachment","body_b":"peg","contact_count":377.0,"contact_point_centroid":[0.51245,0.02888,0.05442],"force_p95":130.51056,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.49054,"mean_force":88.97095,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50341,0.02595,0.05686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50217,0.00048,0.00837],"force_p95":128.55692,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.19133,"mean_force":34.32945,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50232,-0.03755,0.04612]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54546,-0.10001,0.06494],"force_p95":91.17591,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.86232,"mean_force":69.75159,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50164,-0.08091,0.04055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.50376,0.06164,0.00938],"force_p95":0.55166,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.73519,"mean_force":0.59409,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50249,0.08525,0.10339]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51072,0.07816,0.0587],"force_p95":21.26088,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.26088,"mean_force":21.26088,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50035,0.08207,0.06322]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":59.0,"contact_point_centroid":[0.52502,0.01492,0.05752],"force_p95":19.04542,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.61246,"mean_force":15.30315,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50656,0.00366,0.05648]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50418,-0.01318,0.00808],"force_p95":0.71296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.22505,"mean_force":0.70097,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49739,-0.08005,0.08471]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.525,-0.03769,0.02419],"force_p95":7.87683,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.88402,"mean_force":4.06552,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49686,-0.0798,0.11002]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47496,0.00911,0.0245],"force_p95":7.59644,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.80163,"mean_force":2.5231,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49969,-0.06641,0.03889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":631.0,"contact_point_centroid":[0.50367,0.06157,0.00935],"force_p95":0.5949,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55928,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50276,0.14274,0.21896]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19888,0.29869]}],"total_contact_groups":14},"final_pose_error":0.01079,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50516,-0.01527,0.02441],"final_tcp_position":[0.49674,-0.07966,0.12972],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":336.29602,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":21.73519,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":448.0,"raw_peak_contact_force":21.73519,"subtask_id":"reach_contact","tcp_end":[0.50707,0.0888,0.14545],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06155,0.03378],"object_pos_start":[0.50373,0.06157,0.03378],"object_to_goal_dist_end":0.14174,"object_to_goal_dist_start":0.14176,"object_z_max":0.03379,"peak_contact_force":310.90801,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2482.0,"raw_peak_contact_force":336.29602,"subtask_id":"reach_contact","tcp_end":[0.50035,0.08207,0.06305],"tcp_start":[0.50707,0.0888,0.14545],"tcp_to_object_dist_end":0.03591,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,-0.01364,0.02413],"object_pos_start":[0.50378,0.06155,0.03378],"object_to_goal_dist_end":0.06824,"object_to_goal_dist_start":0.14174,"object_z_max":0.03921,"peak_contact_force":0.33882,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":706.0,"raw_peak_contact_force":151.8299,"subtask_id":"reach_goal","tcp_end":[0.50164,-0.08081,0.04051],"tcp_start":[0.50035,0.08207,0.06305],"tcp_to_object_dist_end":0.06915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":680.0,"n_steps_budget":780.0,"object_pos_end":[0.50516,-0.01527,0.02441],"object_pos_start":[0.50097,-0.01364,0.02413],"object_to_goal_dist_end":0.06678,"object_to_goal_dist_start":0.06824,"object_z_max":0.02444,"peak_contact_force":0.53982,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":650.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_goal","tcp_end":[0.49674,-0.07966,0.12972],"tcp_start":[0.50164,-0.08081,0.04051],"tcp_to_object_dist_end":0.12372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76271,"average_solve_count":354.0,"average_success_count":354.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02874,"descend_1.force_threshold":5.395,"descend_1.speed":0.07413,"push_1.push_distance":0.20816,"push_1.speed":0.03522,"retract_1.speed":0.02173},"optimized_scores":{"best_composite_score":0.27614,"best_fitness_score":0.38614,"best_task_score":0.47343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":272.0,"contact_point_centroid":[0.54477,-0.03821,0.05996],"force_p95":220.58001,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.91581,"mean_force":169.16343,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50029,-0.0384,0.03654]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":215.0,"contact_point_centroid":[0.52505,-0.04092,0.05998],"force_p95":210.99358,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":219.72835,"mean_force":172.74689,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50071,-0.04081,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":751.0,"contact_point_centroid":[0.50264,0.06066,0.00845],"force_p95":130.46198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.95064,"mean_force":44.45459,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49976,0.02484,0.04705]},{"body_a":"attachment","body_b":"peg","contact_count":369.0,"contact_point_centroid":[0.50893,0.08454,0.05454],"force_p95":131.01148,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.43782,"mean_force":89.37111,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49993,0.08131,0.05695]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52503,-0.04138,0.05998],"force_p95":67.20638,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.89591,"mean_force":18.49249,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50061,-0.04121,0.03669]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.54503,-0.0479,0.05995],"force_p95":46.96555,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.11764,"mean_force":37.67991,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50061,-0.04121,0.03669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":437.0,"contact_point_centroid":[0.50091,0.11593,0.00941],"force_p95":0.61432,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.97856,"mean_force":0.61298,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49601,0.1378,0.10429]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5074,0.133,0.05871],"force_p95":30.49019,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.49019,"mean_force":30.49019,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49668,0.13577,0.06328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50497,0.04189,0.00809],"force_p95":0.71336,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.43704,"mean_force":0.71501,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49673,-0.05734,0.0757]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.525,0.01796,0.02433],"force_p95":7.93211,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.08033,"mean_force":3.27897,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49657,-0.05558,0.07081]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47496,0.0657,0.02494],"force_p95":6.66394,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.76344,"mean_force":1.97267,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49701,-0.00441,0.03974]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50096,0.11603,0.00938],"force_p95":0.60792,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55866,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49807,0.16982,0.22216]}],"total_contact_groups":12},"final_pose_error":0.02618,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50547,0.04029,0.02429],"final_tcp_position":[0.49659,-0.0722,0.11524],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":239.91581,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.501,0.11608,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":30.97856,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":438.0,"raw_peak_contact_force":30.97856,"subtask_id":"reach_contact","tcp_end":[0.49782,0.14051,0.14824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":437.0,"n_steps_budget":810.0,"object_pos_end":[0.50096,0.11613,0.03383],"object_pos_start":[0.501,0.11608,0.03389],"object_to_goal_dist_end":0.19623,"object_to_goal_dist_start":0.19618,"object_z_max":0.03401,"peak_contact_force":210.92568,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1615.0,"raw_peak_contact_force":239.91581,"subtask_id":"reach_contact","tcp_end":[0.4967,0.13577,0.06309],"tcp_start":[0.49782,0.14051,0.14824],"tcp_to_object_dist_end":0.0355,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":756.0,"n_steps_budget":1000.0,"object_pos_end":[0.5025,0.04282,0.02414],"object_pos_start":[0.50096,0.11613,0.03383],"object_to_goal_dist_end":0.12386,"object_to_goal_dist_start":0.19623,"object_z_max":0.03895,"peak_contact_force":0.61025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1054.0,"raw_peak_contact_force":76.89591,"subtask_id":"reach_goal","tcp_end":[0.50062,-0.04122,0.03667],"tcp_start":[0.4967,0.13577,0.06309],"tcp_to_object_dist_end":0.08499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,0.04029,0.02429],"object_pos_start":[0.5025,0.04282,0.02414],"object_to_goal_dist_end":0.12143,"object_to_goal_dist_start":0.12386,"object_z_max":0.02456,"peak_contact_force":0.54172,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":542.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_goal","tcp_end":[0.49659,-0.0722,0.11524],"tcp_start":[0.50062,-0.04122,0.03667],"tcp_to_object_dist_end":0.14493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24681,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08413,"descend_1.force_threshold":13.69869,"descend_1.speed":0.03925,"push_1.push_distance":0.19499,"push_1.speed":0.01767,"retract_1.speed":0.10399},"optimized_scores":{"best_composite_score":0.1921,"best_fitness_score":0.3021,"best_task_score":0.31569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.54028,-0.10001,0.06494],"force_p95":350.55601,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.98263,"mean_force":263.45872,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49758,-0.07636,0.03827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":849.0,"contact_point_centroid":[0.4971,0.00581,0.00829],"force_p95":140.65943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.2886,"mean_force":42.29201,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49503,-0.02834,0.04656]},{"body_a":"attachment","body_b":"peg","contact_count":364.0,"contact_point_centroid":[0.50222,0.03324,0.05444],"force_p95":141.8497,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":143.76277,"mean_force":96.70183,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49286,0.03072,0.05717]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53575,-0.06196,0.05994],"force_p95":59.64697,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.91516,"mean_force":18.20457,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49072,-0.06521,0.03718]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54328,-0.10001,0.06494],"force_p95":67.28432,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.33837,"mean_force":60.18918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50062,-0.08055,0.03867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":584.0,"contact_point_centroid":[0.49504,0.06398,0.0094],"force_p95":0.55079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.36741,"mean_force":0.57242,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48271,0.08761,0.10254]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49917,0.08159,0.05894],"force_p95":15.80155,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.80155,"mean_force":15.80155,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48867,0.08458,0.06389]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.47492,0.02353,0.02355],"force_p95":14.10038,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.59509,"mean_force":9.77969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49519,-0.02812,0.04893]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49452,-0.01014,0.00803],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.75781,"mean_force":0.66797,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,-0.0799,0.08279]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.475,0.01495,0.02433],"force_p95":9.11361,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.25652,"mean_force":3.76536,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49668,-0.07967,0.12254]},{"body_a":"peg","body_b":"channel_base_body","contact_count":581.0,"contact_point_centroid":[0.4955,0.06388,0.00937],"force_p95":0.57899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56019,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48849,0.14376,0.21907]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.19821,0.29744]}],"total_contact_groups":12},"final_pose_error":0.01211,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49337,-0.00939,0.02447],"final_tcp_position":[0.49675,-0.07965,0.12833],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":357.98263,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.49507,0.06409,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1443,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":16.36741,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":585.0,"raw_peak_contact_force":16.36741,"subtask_id":"reach_contact","tcp_end":[0.4792,0.09131,0.1464],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.49483,0.06398,0.03402],"object_pos_start":[0.49507,0.06409,0.03395],"object_to_goal_dist_end":0.1442,"object_to_goal_dist_start":0.1443,"object_z_max":0.03402,"peak_contact_force":347.83541,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1665.0,"raw_peak_contact_force":357.98263,"subtask_id":"reach_contact","tcp_end":[0.4887,0.08458,0.06377],"tcp_start":[0.4792,0.09131,0.1464],"tcp_to_object_dist_end":0.0367,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.49509,-0.01005,0.0241],"object_pos_start":[0.49483,0.06398,0.03402],"object_to_goal_dist_end":0.0719,"object_to_goal_dist_start":0.1442,"object_z_max":0.03882,"peak_contact_force":0.023,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":557.0,"raw_peak_contact_force":67.33837,"subtask_id":"reach_goal","tcp_end":[0.50062,-0.08056,0.03862],"tcp_start":[0.4887,0.08458,0.06377],"tcp_to_object_dist_end":0.0722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49337,-0.00939,0.02447],"object_pos_start":[0.49509,-0.01005,0.0241],"object_to_goal_dist_end":0.0726,"object_to_goal_dist_start":0.0719,"object_z_max":0.02456,"peak_contact_force":0.5402,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":609.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_goal","tcp_end":[0.49675,-0.07965,0.12833],"tcp_start":[0.50062,-0.08056,0.03862],"tcp_to_object_dist_end":0.12544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```