## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1293 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.2036 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5176 | 0.24 | ❌ rejected |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.1133 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1871 | 0.75 | ✅ accepted |

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

## Current Skill (Q=0.129) — your mutation base

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

- **Composite score**: 0.129
- **task_score** (E): 0.002
- **fitness_score**: 0.076  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1982 |
| descend_1 | 1.00 | 1.00 | 0.0720 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.093, 0.135) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.539 | 2.179 |
| descend_1 | descend | 1.00 / force_exceeded | (0.495, 0.093, 0.135)→(0.495, 0.084, 0.064) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 29.491 | 29.491 |
| push_1 | push | 0.00 / guard_failure | (0.494, 0.083, 0.063)→(0.494, 0.083, 0.063) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 28.877 | 47.088 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.003
- alignment_error: None
- force_efficiency: 0.090
- terminal_score: 0.002
- phase_score: 0.133
- phase_breakdown.push_to_goal_score: 0.051
- phase_breakdown.reach_pre_contact_score: 0.324

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.080
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: 0.134
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44144,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07491,"descend_1.contact_force_threshold":7.59561,"descend_1.descend_speed":0.0402,"push_1.push_force_guard_threshold":38.16002,"push_1.push_speed":0.04062},"optimized_scores":{"best_composite_score":0.13373,"best_fitness_score":0.08039,"best_task_score":0.00248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49166,0.05142,0.00932],"force_p95":41.49458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.03963,"mean_force":29.38035,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50063,0.06514,0.06309]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51156,0.06535,0.0585],"force_p95":41.04932,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.59263,"mean_force":28.92073,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50063,0.06514,0.06309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50392,0.06163,0.00937],"force_p95":0.61737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.56074,"mean_force":0.63586,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50265,0.07022,0.09742]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51179,0.06548,0.05873],"force_p95":34.08621,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.08621,"mean_force":34.08621,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50085,0.06541,0.06364]},{"body_a":"peg","body_b":"channel_base_body","contact_count":394.0,"contact_point_centroid":[0.50349,0.06162,0.00933],"force_p95":0.63277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56693,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50293,0.13546,0.21241]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49972,0.19852,0.29822]}],"total_contact_groups":6},"final_pose_error":0.14643,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50337,0.06113,0.03379],"final_tcp_position":[0.50046,0.06466,0.06273],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":45.03963,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06158,0.03377],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54199,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":413.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_contact","tcp_end":[0.50695,0.07544,0.13362],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06157,0.03377],"object_pos_start":[0.50378,0.06158,0.03377],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14177,"object_z_max":0.03378,"peak_contact_force":34.56074,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":382.0,"raw_peak_contact_force":34.56074,"subtask_id":"reach_pre_contact","tcp_end":[0.50086,0.06539,0.06348],"tcp_start":[0.50695,0.07544,0.13362],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.5034,0.06122,0.0338],"object_pos_start":[0.50376,0.06157,0.03377],"object_to_goal_dist_end":0.1414,"object_to_goal_dist_start":0.14176,"object_z_max":0.0338,"peak_contact_force":29.37582,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":45.03963,"subtask_id":"push_to_goal","tcp_end":[0.50046,0.06466,0.06273],"tcp_start":[0.50049,0.06473,0.06278],"tcp_to_object_dist_end":0.02928,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18261,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06944,"descend_1.contact_force_threshold":2.58898,"descend_1.descend_speed":0.03417,"push_1.push_force_guard_threshold":38.2724,"push_1.push_speed":0.06593},"optimized_scores":{"best_composite_score":0.12039,"best_fitness_score":0.06706,"best_task_score":0.00298},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49213,0.1079,0.00935],"force_p95":45.61801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.72646,"mean_force":26.80772,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.496,0.11772,0.0632]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50696,0.11808,0.05859],"force_p95":45.09958,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.21236,"mean_force":26.35385,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.496,0.11772,0.0632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.50092,0.11603,0.00944],"force_p95":0.5983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.21806,"mean_force":0.62948,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49583,0.12145,0.09872]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50718,0.11826,0.05886],"force_p95":36.66357,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.66357,"mean_force":36.66357,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49621,0.11805,0.0637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50098,0.11597,0.00935],"force_p95":0.65215,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56811,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49842,0.16205,0.21592]}],"total_contact_groups":5},"final_pose_error":0.19845,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5007,0.11556,0.03382],"final_tcp_position":[0.49584,0.11708,0.06286],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":50.72646,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11604,0.03392],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53316,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":339.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49807,0.12555,0.13698],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11604,0.03389],"object_pos_start":[0.50097,0.11604,0.03392],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19614,"object_z_max":0.034,"peak_contact_force":37.21806,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":416.0,"raw_peak_contact_force":37.21806,"subtask_id":"reach_pre_contact","tcp_end":[0.49622,0.11804,0.06355],"tcp_start":[0.49807,0.12555,0.13698],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50069,0.11567,0.03382],"object_pos_start":[0.50096,0.11604,0.03389],"object_to_goal_dist_end":0.19577,"object_to_goal_dist_start":0.19614,"object_z_max":0.03389,"peak_contact_force":26.84774,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":50.72646,"subtask_id":"push_to_goal","tcp_end":[0.49584,0.11708,0.06286],"tcp_start":[0.49586,0.11719,0.06292],"tcp_to_object_dist_end":0.02947,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1913,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06959,"descend_1.contact_force_threshold":6.49982,"descend_1.descend_speed":0.04006,"push_1.push_force_guard_threshold":38.83598,"push_1.push_speed":0.04975},"optimized_scores":{"best_composite_score":0.1338,"best_fitness_score":0.08046,"best_task_score":0.00194},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.47966,0.06135,0.00938],"force_p95":42.09463,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.49928,"mean_force":30.45451,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48644,0.06717,0.06373]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49721,0.06742,0.05878],"force_p95":41.66323,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.05904,"mean_force":29.97871,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48644,0.06717,0.06373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":485.0,"contact_point_centroid":[0.4953,0.06401,0.0094],"force_p95":0.55033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.69527,"mean_force":0.57886,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48205,0.07212,0.0967]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49734,0.06749,0.05896],"force_p95":16.18992,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.18992,"mean_force":16.18992,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48656,0.06751,0.0642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.49541,0.06384,0.00936],"force_p95":0.611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56728,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48902,0.13593,0.21181]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49917,0.19746,0.29647]}],"total_contact_groups":6},"final_pose_error":0.14901,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49453,0.0634,0.03403],"final_tcp_position":[0.48637,0.06654,0.06336],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":45.49928,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.49519,0.06371,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54244,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":418.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.48011,0.07746,0.13401],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06405,0.034],"object_pos_start":[0.49519,0.06371,0.03393],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14392,"object_z_max":0.034,"peak_contact_force":16.69527,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":486.0,"raw_peak_contact_force":16.69527,"subtask_id":"reach_pre_contact","tcp_end":[0.48658,0.06749,0.06408],"tcp_start":[0.48011,0.07746,0.13401],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.49456,0.06352,0.03405],"object_pos_start":[0.49489,0.06405,0.034],"object_to_goal_dist_end":0.14375,"object_to_goal_dist_start":0.14427,"object_z_max":0.03409,"peak_contact_force":30.40729,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":45.49928,"subtask_id":"push_to_goal","tcp_end":[0.48637,0.06654,0.06336],"tcp_start":[0.48638,0.06663,0.06342],"tcp_to_object_dist_end":0.03058,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```