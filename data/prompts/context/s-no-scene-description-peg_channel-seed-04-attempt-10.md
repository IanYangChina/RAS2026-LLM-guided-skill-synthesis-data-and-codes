## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3049 | 0.61 | ❌ rejected |
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.3000 | 0.00 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.61 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.60 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3035 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.305) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.305
- **task_score** (E): 0.606
- **fitness_score**: 0.332  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1931 |
| align_1 | 1.00 | 1.00 | 0.1061 |
| release_1 | 1.00 | 1.00 | 0.1734 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.089, 0.142) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.545 | 3.242 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.089, 0.142)→(0.502, 0.121, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.596 | 62.351 |
| release_1 | release | 1.00 / step_budget | (0.502, 0.121, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.034)→(0.506, -0.082, 0.036) | 0.162→0.010 | 1.00 / 4.000 | 86.493 | 96.963 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.082, 0.036)→(0.506, -0.082, 0.036) | 0.010→0.010 | 1.00 / 4.000 | 92.823 | 92.823 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.970
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.970
- phase_score: 0.188
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.885
- phase_breakdown.push_score: 0.018

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.501
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.970
- **Median Q (composite search score)**: 0.277
- **K-run variance**: 0.0165
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.352


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89286,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00133,"align_1.lateral_offset_y":0.00163,"insert_1.insertion_depth":0.14925,"insert_1.insertion_force":9.016,"push_1.push_distance":0.0594,"push_1.push_speed":0.08275},"optimized_scores":{"best_composite_score":0.1634,"best_fitness_score":0.19007,"best_task_score":0.30895},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":525.0,"contact_point_centroid":[0.54248,-0.00739,0.05999],"force_p95":76.13229,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.82988,"mean_force":57.38258,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49771,-0.00682,0.03685]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54275,-0.04922,0.05998],"force_p95":81.74766,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.74766,"mean_force":81.74766,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4981,-0.05322,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":884.0,"contact_point_centroid":[0.50373,-0.00097,0.04449],"force_p95":17.8881,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.67976,"mean_force":6.71866,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49764,0.01062,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.50689,-0.10038,0.05816],"force_p95":21.50076,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.97734,"mean_force":14.514,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49801,-0.05309,0.03666]},{"body_a":"peg","body_b":"channel_base_body","contact_count":618.0,"contact_point_centroid":[0.50636,-0.01597,0.00985],"force_p95":15.6667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.56937,"mean_force":5.89509,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49767,0.02764,0.03711]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50698,-0.06503,0.05542],"force_p95":12.68965,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.68965,"mean_force":12.68965,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4981,-0.05322,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50688,-0.10037,0.06045],"force_p95":12.58542,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.58542,"mean_force":12.58542,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4981,-0.05322,0.03664]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":443.0,"contact_point_centroid":[0.52504,-0.02016,0.02584],"force_p95":5.31991,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.19204,"mean_force":1.12217,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49764,0.00733,0.0369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49734,0.14386,0.21482]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49934,0.19834,0.2973]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.50607,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49764,0.10402,0.09015]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52502,-0.0826,0.01057],"force_p95":0.02784,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.02784,"mean_force":0.02784,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4981,-0.05322,0.03664]}],"total_contact_groups":12},"final_pose_error":0.02705,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50695,-0.08267,0.03549],"final_tcp_position":[0.49811,-0.05322,0.03664],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":84.82988,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49665,0.09258,0.13979],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10706,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":340.0,"n_steps_budget":720.0,"object_pos_end":[0.50595,0.08087,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":340.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50091,0.11668,0.04119],"tcp_start":[0.49665,0.09258,0.13979],"tcp_to_object_dist_end":0.03692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.08267,0.0355],"object_pos_start":[0.50595,0.08087,0.03378],"object_to_goal_dist_end":0.0087,"object_to_goal_dist_start":0.1611,"object_z_max":0.0375,"peak_contact_force":73.20891,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2641.0,"raw_peak_contact_force":84.82988,"tcp_end":[0.4981,-0.05322,0.03664],"tcp_start":[0.50091,0.11668,0.04119],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50695,-0.08267,0.03549],"object_pos_start":[0.50696,-0.08267,0.0355],"object_to_goal_dist_end":0.00871,"object_to_goal_dist_start":0.0087,"object_z_max":0.0355,"peak_contact_force":81.74766,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":81.74766,"tcp_end":[0.49811,-0.05322,0.03664],"tcp_start":[0.4981,-0.05322,0.03664],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88991,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00458,"align_1.lateral_offset_y":0.00805,"insert_1.insertion_depth":0.1165,"insert_1.insertion_force":4.64898,"push_1.push_distance":0.07351,"push_1.push_speed":0.09941},"optimized_scores":{"best_composite_score":0.27693,"best_fitness_score":0.30359,"best_task_score":0.53832},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":104.0,"contact_point_centroid":[0.51224,0.12779,0.05465],"force_p95":160.23355,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.95277,"mean_force":111.61731,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50343,0.13351,0.05631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.50731,0.10843,0.00914],"force_p95":145.855,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":176.47596,"mean_force":30.57756,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49898,0.11649,0.08337]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54271,-0.04069,0.05998],"force_p95":78.75451,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.75451,"mean_force":78.75451,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04512,0.03669]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.54281,-0.02909,0.05998],"force_p95":77.19684,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.54584,"mean_force":59.80864,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49814,-0.02951,0.03679]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":88.0,"contact_point_centroid":[0.52514,0.11159,0.05291],"force_p95":31.81304,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.48909,"mean_force":13.06109,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5045,0.13559,0.05462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.50604,-0.01825,0.00987],"force_p95":14.81929,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.20357,"mean_force":5.1191,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49917,0.02644,0.03742]},{"body_a":"attachment","body_b":"peg","contact_count":841.0,"contact_point_centroid":[0.50368,0.01151,0.0419],"force_p95":14.12155,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.1203,"mean_force":4.30909,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49892,0.02316,0.03717]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":486.0,"contact_point_centroid":[0.52506,-0.0068,0.03011],"force_p95":3.26943,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.08818,"mean_force":0.78586,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49902,0.02276,0.03728]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49732,0.1439,0.2103]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.19845,0.29749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50702,-0.09028,0.00999],"force_p95":0.56144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56144,"mean_force":0.56144,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04512,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50439,-0.057,0.04534],"force_p95":0.54748,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54748,"mean_force":0.54748,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04512,0.03669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,-0.07412,0.03562],"force_p95":0.39969,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39969,"mean_force":0.39969,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04512,0.03669]}],"total_contact_groups":13},"final_pose_error":0.03509,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.07417,0.03624],"final_tcp_position":[0.49808,-0.04512,0.03669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":185.95277,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49663,0.09255,0.13087],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09823,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":720.0,"object_pos_end":[0.50457,0.0985,0.0354],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17861,"object_to_goal_dist_start":0.18484,"object_z_max":0.03519,"peak_contact_force":0.69537,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":578.0,"raw_peak_contact_force":185.95277,"tcp_end":[0.50522,0.14185,0.04333],"tcp_start":[0.49663,0.09255,0.13087],"tcp_to_object_dist_end":0.04408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.07417,0.03624],"object_pos_start":[0.50457,0.0985,0.0354],"object_to_goal_dist_end":0.00987,"object_to_goal_dist_start":0.17861,"object_z_max":0.04001,"peak_contact_force":72.46301,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2356.0,"raw_peak_contact_force":77.54584,"tcp_end":[0.49808,-0.04512,0.03669],"tcp_start":[0.50522,0.14185,0.04333],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50701,-0.07417,0.03624],"object_pos_start":[0.50701,-0.07417,0.03624],"object_to_goal_dist_end":0.00987,"object_to_goal_dist_start":0.00987,"object_z_max":0.03624,"peak_contact_force":78.75451,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":78.75451,"tcp_end":[0.49808,-0.04512,0.03669],"tcp_start":[0.49808,-0.04512,0.03669],"tcp_to_object_dist_end":0.0304,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88785,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00434,"align_1.lateral_offset_y":-0.00357,"insert_1.insertion_depth":0.04737,"insert_1.insertion_force":12.80379,"push_1.push_distance":0.08524,"push_1.push_speed":0.09474},"optimized_scores":{"best_composite_score":0.4743,"best_fitness_score":0.50096,"best_task_score":0.97032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":509.0,"contact_point_centroid":[0.54204,-0.02365,0.05999],"force_p95":120.94116,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.51216,"mean_force":70.00588,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49728,-0.02368,0.03685]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54348,-0.05528,0.05998],"force_p95":117.9673,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.9673,"mean_force":117.9673,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49888,-0.05889,0.0365]},{"body_a":"attachment","body_b":"peg","contact_count":862.0,"contact_point_centroid":[0.50295,-0.01488,0.04433],"force_p95":81.20662,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.33216,"mean_force":22.16062,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49676,-0.00353,0.03699]},{"body_a":"peg","body_b":"channel_base_body","contact_count":258.0,"contact_point_centroid":[0.5054,-0.10227,0.05476],"force_p95":82.55848,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.69343,"mean_force":59.46822,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49843,-0.05764,0.03656]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5048,-0.07042,0.04926],"force_p95":70.44414,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.44414,"mean_force":70.44414,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49888,-0.05889,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50462,-0.10294,0.05994],"force_p95":70.10371,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.10371,"mean_force":70.10371,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49888,-0.05889,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.50617,-0.03145,0.00983],"force_p95":16.71009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.07967,"mean_force":5.66915,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49657,0.01082,0.03724]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":403.0,"contact_point_centroid":[0.52512,-0.00384,0.02457],"force_p95":7.92775,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.86411,"mean_force":2.3783,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49599,0.02256,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49741,0.13916,0.22374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50923,-0.10504,0.00997],"force_p95":0.56008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56008,"mean_force":0.56008,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49888,-0.05889,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4965,0.09281,0.09872]}],"total_contact_groups":11},"final_pose_error":0.02143,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50465,-0.08779,0.035],"final_tcp_position":[0.49888,-0.05888,0.0365],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":128.51216,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54788,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49674,0.08267,0.15597],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12328,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":780.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54561,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":378.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49844,0.10397,0.04194],"tcp_start":[0.49674,0.08267,0.15597],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50462,-0.0878,0.035],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.01035,"object_to_goal_dist_start":0.14759,"object_z_max":0.03866,"peak_contact_force":113.80746,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2703.0,"raw_peak_contact_force":128.51216,"tcp_end":[0.49888,-0.05889,0.0365],"tcp_start":[0.49844,0.10397,0.04194],"tcp_to_object_dist_end":0.02951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50465,-0.08779,0.035],"object_pos_start":[0.50462,-0.0878,0.035],"object_to_goal_dist_end":0.01036,"object_to_goal_dist_start":0.01035,"object_z_max":0.035,"peak_contact_force":117.9673,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":117.9673,"tcp_end":[0.49888,-0.05888,0.0365],"tcp_start":[0.49888,-0.05889,0.0365],"tcp_to_object_dist_end":0.02951,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```