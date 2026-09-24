## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1292 | 0.01 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2043 | 0.53 | ❌ rejected |
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2063 | 0.55 | ✅ accepted |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2061 | 0.55 | ✅ accepted |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2057 | 0.53 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=-0.129) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: align_2
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

```

## Design Metrics

- **Composite score**: -0.129
- **task_score** (E): 0.010
- **fitness_score**: 0.101  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2208 |
| align_to_object | 1.00 | 1.00 | 0.0416 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.473, -0.001, 0.085) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_to_object | align | 1.00 / step_budget | (0.473, -0.001, 0.085)→(0.476, -0.004, 0.044) | (0.474, -0.001, 0.025)→(0.478, -0.001, 0.024) | 0.154→0.153 | 1.00 / 5.000 | 250.373 | 270.514 |
| push_to_goal | push | 0.00 / guard_failure | (0.476, -0.004, 0.044)→(0.477, -0.004, 0.044) | (0.478, -0.001, 0.024)→(0.478, -0.001, 0.024) | 0.153→0.153 | 1.00 / 5.000 | 90.737 | 90.737 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.033
- lateral_force_integral: None
- approach_alignment: 0.531
- goal_progress: 0.018
- terminal_score: 0.018
- phase_score: 0.160
- phase_breakdown.goal_score: 0.000
- phase_breakdown.pre_contact_score: 0.532

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.103
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.018
- **Median Q (composite search score)**: -0.129
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.291


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_object.lateral_offset_x":-0.01965,"align_to_object.lateral_offset_y":-0.0009,"approach.speed":0.32563,"push_to_goal.push_distance":0.19994},"optimized_scores":{"best_composite_score":-0.1316,"best_fitness_score":0.0984,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":213.0,"contact_point_centroid":[0.50438,0.05252,0.04715],"force_p95":258.2746,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":258.82957,"mean_force":201.72806,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.49256,0.05254,0.04742]},{"body_a":"world","body_b":"push_box","contact_count":1484.0,"contact_point_centroid":[0.50212,0.05424,-0.00028],"force_p95":93.38427,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.98586,"mean_force":29.23555,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.49219,0.05168,0.05647]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51339,0.05349,0.04589],"force_p95":92.25748,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.25748,"mean_force":92.25748,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50144,0.05421,0.0448]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50414,0.0547,-0.00066],"force_p95":34.00906,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.38152,"mean_force":23.36746,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50144,0.05421,0.0448]},{"body_a":"world","body_b":"push_box","contact_count":2204.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49824,0.02436,0.19384]}],"total_contact_groups":5},"final_pose_error":0.20039,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50482,0.05471,0.02368],"final_tcp_position":[0.50154,0.05422,0.04482],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":258.82957,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49783,0.0501,0.08506],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":371.0,"n_steps_budget":600.0,"object_pos_end":[0.5048,0.05471,0.02367],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20477,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":256.21368,"phase_name":"align_to_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1697.0,"raw_peak_contact_force":258.82957,"subtask_id":"pre_contact","tcp_end":[0.50144,0.05421,0.0448],"tcp_start":[0.49783,0.0501,0.08506],"tcp_to_object_dist_end":0.0214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50482,0.05471,0.02368],"object_pos_start":[0.5048,0.05471,0.02367],"object_to_goal_dist_end":0.20477,"object_to_goal_dist_start":0.20477,"object_z_max":0.02367,"peak_contact_force":92.25748,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":92.25748,"subtask_id":"goal","tcp_end":[0.50154,0.05422,0.04482],"tcp_start":[0.50144,0.05421,0.0448],"tcp_to_object_dist_end":0.02139,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_object.lateral_offset_x":-0.01998,"align_to_object.lateral_offset_y":-0.00325,"approach.speed":0.39843,"push_to_goal.push_distance":0.07312},"optimized_scores":{"best_composite_score":-0.12885,"best_fitness_score":0.10115,"best_task_score":0.01078},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":212.0,"contact_point_centroid":[0.47532,-0.0258,0.04703],"force_p95":271.00935,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":273.27426,"mean_force":208.83698,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.46349,-0.0262,0.04718]},{"body_a":"world","body_b":"push_box","contact_count":1524.0,"contact_point_centroid":[0.47202,-0.02432,-0.00028],"force_p95":104.00821,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.82994,"mean_force":29.35831,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.46337,-0.02503,0.05684]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48567,-0.02616,0.04569],"force_p95":91.83835,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.83835,"mean_force":91.83835,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47376,-0.0278,0.0443]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47422,-0.02469,-0.00067],"force_p95":40.21107,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.14953,"mean_force":23.3038,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47376,-0.0278,0.0443]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48464,-0.01097,0.19385]}],"total_contact_groups":5},"final_pose_error":0.07319,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47506,-0.02483,0.02366],"final_tcp_position":[0.47388,-0.02781,0.04432],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":273.27426,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.46993,-0.02251,0.08548],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.47504,-0.02483,0.02365],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12765,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":249.77988,"phase_name":"align_to_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1736.0,"raw_peak_contact_force":273.27426,"subtask_id":"pre_contact","tcp_end":[0.47376,-0.0278,0.0443],"tcp_start":[0.46993,-0.02251,0.08548],"tcp_to_object_dist_end":0.0209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.47506,-0.02483,0.02366],"object_pos_start":[0.47504,-0.02483,0.02365],"object_to_goal_dist_end":0.12764,"object_to_goal_dist_start":0.12765,"object_z_max":0.02365,"peak_contact_force":91.83835,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":91.83835,"subtask_id":"goal","tcp_end":[0.47388,-0.02781,0.04432],"tcp_start":[0.47376,-0.0278,0.0443],"tcp_to_object_dist_end":0.02091,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_object.lateral_offset_x":-0.01995,"align_to_object.lateral_offset_y":-0.00476,"approach.speed":0.27322,"push_to_goal.push_distance":0.07311},"optimized_scores":{"best_composite_score":-0.12702,"best_fitness_score":0.10298,"best_task_score":0.01802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":212.0,"contact_point_centroid":[0.45498,-0.03398,0.04694],"force_p95":275.59394,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":279.43847,"mean_force":212.51252,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.44316,-0.03463,0.04701]},{"body_a":"world","body_b":"push_box","contact_count":1556.0,"contact_point_centroid":[0.45089,-0.03177,-0.00028],"force_p95":103.90253,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.10881,"mean_force":29.27619,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.44321,-0.03292,0.05706]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.46579,-0.03394,0.04565],"force_p95":88.11543,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.11543,"mean_force":88.11543,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45412,-0.03691,0.04413]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.45328,-0.0323,-0.00066],"force_p95":40.84834,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.09644,"mean_force":22.40758,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45412,-0.03691,0.04413]},{"body_a":"world","body_b":"push_box","contact_count":2204.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47511,-0.0143,0.19411]}],"total_contact_groups":5},"final_pose_error":0.07173,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45421,-0.0325,0.02368],"final_tcp_position":[0.45425,-0.03693,0.04415],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":279.43847,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.45034,-0.02938,0.08575],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":389.0,"n_steps_budget":600.0,"object_pos_end":[0.45419,-0.03249,0.02367],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12613,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":245.12397,"phase_name":"align_to_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1768.0,"raw_peak_contact_force":279.43847,"subtask_id":"pre_contact","tcp_end":[0.45412,-0.03691,0.04413],"tcp_start":[0.45034,-0.02938,0.08575],"tcp_to_object_dist_end":0.02093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.45421,-0.0325,0.02368],"object_pos_start":[0.45419,-0.03249,0.02367],"object_to_goal_dist_end":0.12612,"object_to_goal_dist_start":0.12613,"object_z_max":0.02367,"peak_contact_force":88.11543,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":88.11543,"subtask_id":"goal","tcp_end":[0.45425,-0.03693,0.04415],"tcp_start":[0.45412,-0.03691,0.04413],"tcp_to_object_dist_end":0.02094,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```