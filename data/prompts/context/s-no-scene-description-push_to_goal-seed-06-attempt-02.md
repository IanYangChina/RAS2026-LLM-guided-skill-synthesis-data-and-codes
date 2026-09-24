## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0821 | 0.00 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0824 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0821 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.082) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.082
- **task_score** (E): 0.000
- **fitness_score**: 0.318  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2901 |
| lift_1 | 0.00 | 1.00 | 0.1699 |
| push_1 | 1.00 | 1.00 | 0.1927 |
| approach_1 | 0.33 | 1.00 | 0.1748 |
| approach_2 | 1.00 | 1.00 | 0.1054 |
| descend_1 | 0.00 | 1.00 | 0.1900 |
| grasp_1 | 1.00 | 1.00 | 0.0107 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.104, 0.032) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| lift_1 | lift | 0.00 / step_budget | (0.496, 0.104, 0.032)→(0.435, 0.003, 0.154) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.435, 0.003, 0.154)→(0.493, -0.126, 0.026) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 0.33 / step_budget | (0.493, -0.126, 0.026)→(0.496, 0.048, 0.039) | (0.500, 0.029, 0.025)→(0.511, 0.080, 0.028) | 0.180→0.231 | 1.00 / 2.667 | 37.460 | 62.670 |
| approach_2 | approach | 1.00 / step_budget | (0.496, 0.048, 0.039)→(0.508, 0.151, 0.027) | (0.511, 0.080, 0.028)→(0.538, 0.159, 0.030) | 0.231→0.313 | 1.00 / 2.667 | 36.028 | 78.723 |
| descend_1 | descend | 0.00 / step_budget | (0.508, 0.151, 0.027)→(0.499, -0.038, 0.021) | (0.538, 0.159, 0.030)→(0.521, 0.131, 0.025) | 0.313→0.282 | 1.00 / 4.000 | 0.245 | 66.306 |
| grasp_1 | grasp | 1.00 / step_budget | (0.499, -0.038, 0.021)→(0.491, -0.038, 0.013) | (0.521, 0.131, 0.025)→(0.521, 0.131, 0.025) | 0.282→0.282 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.382
- lateral_force_integral: None
- approach_alignment: 0.578
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.574
- phase_breakdown.push_score: 0.870
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.696

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.345
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.069
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.484


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.0076,"approach_2.speed":0.0364,"lift_1.lift_height":0.05577,"push_1.push_distance":0.11249,"push_1.push_speed":0.04768},"optimized_scores":{"best_composite_score":-0.12175,"best_fitness_score":0.27825,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2480.0,"contact_point_centroid":[0.51307,0.0049,-6e-05],"force_p95":39.19117,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.67291,"mean_force":6.98759,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49343,-0.05809,0.0338]},{"body_a":"attachment","body_b":"push_box","contact_count":477.0,"contact_point_centroid":[0.51017,0.00816,0.05162],"force_p95":78.66789,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.63955,"mean_force":22.28787,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49757,-0.00191,0.03605]},{"body_a":"push_box","body_b":"link7","contact_count":169.0,"contact_point_centroid":[0.53842,0.03772,0.05923],"force_p95":91.78284,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.15427,"mean_force":53.81421,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5015,0.03244,0.0317]},{"body_a":"world","body_b":"push_box","contact_count":1855.0,"contact_point_centroid":[0.5523,0.07274,-0.00029],"force_p95":83.69366,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.14093,"mean_force":24.69378,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51404,0.04385,0.02498]},{"body_a":"push_box","body_b":"link7","contact_count":750.0,"contact_point_centroid":[0.55812,0.08922,0.05483],"force_p95":85.22808,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.67324,"mean_force":55.02437,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51826,0.07998,0.02708]},{"body_a":"push_box","body_b":"link7","contact_count":260.0,"contact_point_centroid":[0.54601,0.07539,0.06072],"force_p95":60.59449,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.85621,"mean_force":25.39773,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51044,0.07365,0.03201]},{"body_a":"attachment","body_b":"push_box","contact_count":697.0,"contact_point_centroid":[0.53185,0.09349,0.04924],"force_p95":47.03576,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.6946,"mean_force":9.82416,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51316,0.09083,0.03386]},{"body_a":"world","body_b":"push_box","contact_count":1262.0,"contact_point_centroid":[0.56187,0.10605,-7e-05],"force_p95":28.67598,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.40462,"mean_force":7.95313,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51335,0.09184,0.03394]},{"body_a":"attachment","body_b":"push_box","contact_count":407.0,"contact_point_centroid":[0.54512,0.11164,0.06069],"force_p95":44.3284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.4846,"mean_force":32.51641,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5208,0.11006,0.0282]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49925,0.02864,0.16605]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46549,0.01415,0.09528]},{"body_a":"world","body_b":"push_box","contact_count":3320.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46272,-0.07733,0.09181]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.51927,0.06136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,-0.03827,0.01458]}],"total_contact_groups":13},"final_pose_error":0.11192,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51927,0.06136,0.02499],"final_tcp_position":[0.50531,-0.03826,0.02146],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":127.67291,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4348,-0.02857,0.16105],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.15322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49246,-0.12518,0.02708],"tcp_start":[0.4348,-0.02857,0.16105],"tcp_to_object_dist_end":0.10708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53074,0.07199,0.03135],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.2242,"object_to_goal_dist_start":0.13127,"object_z_max":0.03144,"peak_contact_force":97.62213,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3126.0,"raw_peak_contact_force":127.67291,"tcp_end":[0.50517,0.04439,0.02997],"tcp_start":[0.49246,-0.12518,0.02708],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":1000.0,"object_pos_end":[0.56281,0.12479,0.0322],"object_pos_start":[0.53074,0.07199,0.03135],"object_to_goal_dist_end":0.28197,"object_to_goal_dist_start":0.2242,"object_z_max":0.03281,"peak_contact_force":32.66917,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2219.0,"raw_peak_contact_force":75.85621,"tcp_end":[0.52532,0.14402,0.02901],"tcp_start":[0.50517,0.04439,0.02997],"tcp_to_object_dist_end":0.04225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51927,0.06136,0.02499],"object_pos_start":[0.56281,0.12479,0.0322],"object_to_goal_dist_end":0.21224,"object_to_goal_dist_start":0.28197,"object_z_max":0.03465,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3012.0,"raw_peak_contact_force":92.14093,"tcp_end":[0.50531,-0.03826,0.02146],"tcp_start":[0.52532,0.14402,0.02901],"tcp_to_object_dist_end":0.10065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51927,0.06136,0.02499],"object_pos_start":[0.51927,0.06136,0.02499],"object_to_goal_dist_end":0.21224,"object_to_goal_dist_start":0.21224,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49806,-0.03822,0.01334],"tcp_start":[0.50531,-0.03826,0.02146],"tcp_to_object_dist_end":0.10247,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92607,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00936,"approach_2.speed":0.09968,"lift_1.lift_height":0.1523,"push_1.push_distance":0.18238,"push_1.push_speed":0.07822},"optimized_scores":{"best_composite_score":-0.05536,"best_fitness_score":0.34464,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":126.0,"contact_point_centroid":[0.55091,0.11595,0.06105],"force_p95":80.21035,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.61821,"mean_force":46.82029,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51576,0.13562,0.03151]},{"body_a":"world","body_b":"push_box","contact_count":918.0,"contact_point_centroid":[0.55255,0.12722,-0.00016],"force_p95":57.92085,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.85344,"mean_force":14.21848,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50928,0.09833,0.03836]},{"body_a":"attachment","body_b":"push_box","contact_count":490.0,"contact_point_centroid":[0.52538,0.10447,0.05598],"force_p95":47.42862,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.61521,"mean_force":14.50242,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5091,0.09709,0.03854]},{"body_a":"world","body_b":"push_box","contact_count":2715.0,"contact_point_centroid":[0.53913,0.11943,-0.00012],"force_p95":71.42404,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.97201,"mean_force":8.9929,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50791,0.02638,0.02315]},{"body_a":"push_box","body_b":"link7","contact_count":408.0,"contact_point_centroid":[0.55447,0.1233,0.05553],"force_p95":73.54357,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.25224,"mean_force":54.6262,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51561,0.1102,0.02741]},{"body_a":"attachment","body_b":"push_box","contact_count":245.0,"contact_point_centroid":[0.54098,0.12876,0.0596],"force_p95":44.11192,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.29283,"mean_force":31.4318,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51665,0.12516,0.02804]},{"body_a":"attachment","body_b":"push_box","contact_count":136.0,"contact_point_centroid":[0.50691,0.03785,0.05039],"force_p95":24.72337,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.61089,"mean_force":10.77256,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50264,0.02604,0.0445]},{"body_a":"world","body_b":"push_box","contact_count":3499.0,"contact_point_centroid":[0.51554,0.05024,-1e-05],"force_p95":1.96202,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.15688,"mean_force":0.68298,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49585,-0.0528,0.03857]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50423,0.06072,0.1639]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47617,0.06905,0.08765]},{"body_a":"world","body_b":"push_box","contact_count":3528.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46899,-0.05615,0.08414]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.53228,0.12149,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4965,-0.04456,0.0146]}],"total_contact_groups":12},"final_pose_error":0.10551,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53228,0.12149,0.02499],"final_tcp_position":[0.50262,-0.04458,0.02142],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":106.61821,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51027,0.12151,0.03099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44615,0.01783,0.14851],"tcp_start":[0.51027,0.12151,0.03099],"tcp_to_object_dist_end":0.14453,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3528.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49346,-0.12729,0.02534],"tcp_start":[0.44615,0.01783,0.14851],"tcp_to_object_dist_end":0.17628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52044,0.0746,0.02703],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.22554,"object_to_goal_dist_start":0.19823,"object_z_max":0.02742,"peak_contact_force":14.75754,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3635.0,"raw_peak_contact_force":25.61089,"tcp_end":[0.50408,0.04195,0.04297],"tcp_start":[0.49346,-0.12729,0.02534],"tcp_to_object_dist_end":0.03984,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":750.0,"object_pos_end":[0.55932,0.14797,0.03094],"object_pos_start":[0.52044,0.0746,0.02703],"object_to_goal_dist_end":0.30387,"object_to_goal_dist_start":0.22554,"object_z_max":0.03205,"peak_contact_force":74.85446,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1534.0,"raw_peak_contact_force":106.61821,"tcp_end":[0.51939,0.14477,0.02907],"tcp_start":[0.50408,0.04195,0.04297],"tcp_to_object_dist_end":0.0401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53228,0.12149,0.02499],"object_pos_start":[0.55932,0.14797,0.03094],"object_to_goal_dist_end":0.2734,"object_to_goal_dist_start":0.30387,"object_z_max":0.03291,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3368.0,"raw_peak_contact_force":85.97201,"tcp_end":[0.50262,-0.04458,0.02142],"tcp_start":[0.51939,0.14477,0.02907],"tcp_to_object_dist_end":0.16873,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53228,0.12149,0.02499],"object_pos_start":[0.53228,0.12149,0.02499],"object_to_goal_dist_end":0.2734,"object_to_goal_dist_start":0.2734,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49539,-0.04449,0.01336],"tcp_start":[0.50262,-0.04458,0.02142],"tcp_to_object_dist_end":0.17043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78819,"average_solve_count":288.0,"average_success_count":288.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00423,"approach_2.speed":0.05751,"lift_1.lift_height":0.12216,"push_1.push_distance":0.19161,"push_1.push_speed":0.07085},"optimized_scores":{"best_composite_score":-0.06908,"best_fitness_score":0.33092,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":548.0,"contact_point_centroid":[0.48442,0.12123,0.04833],"force_p95":25.00495,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.69543,"mean_force":9.87326,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.478,0.10925,0.03893]},{"body_a":"world","body_b":"push_box","contact_count":969.0,"contact_point_centroid":[0.49015,0.16257,-9e-05],"force_p95":14.63281,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.53938,"mean_force":6.39424,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.478,0.10674,0.03899]},{"body_a":"attachment","body_b":"push_box","contact_count":124.0,"contact_point_centroid":[0.48019,0.0497,0.04552],"force_p95":26.14811,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.72563,"mean_force":9.98461,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48061,0.03782,0.04507]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.51707,0.1767,0.05275],"force_p95":23.85626,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.6721,"mean_force":19.25723,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47959,0.16066,0.02623]},{"body_a":"world","body_b":"push_box","contact_count":3510.0,"contact_point_centroid":[0.51107,0.20808,-4e-05],"force_p95":0.58351,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.80373,"mean_force":0.62842,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48292,0.05175,0.02004]},{"body_a":"push_box","body_b":"link7","contact_count":92.0,"contact_point_centroid":[0.51127,0.17165,0.04946],"force_p95":19.80338,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.86494,"mean_force":13.12895,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47821,0.14626,0.02123]},{"body_a":"world","body_b":"push_box","contact_count":3573.0,"contact_point_centroid":[0.47932,0.06094,-1e-05],"force_p95":1.06514,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.13035,"mean_force":0.60325,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48485,-0.04535,0.03929]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48715,0.06586,0.16416]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44808,0.07594,0.09006]},{"body_a":"world","body_b":"push_box","contact_count":3912.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45781,-0.0545,0.08599]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.51221,0.2094,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48212,-0.03181,0.01355]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49723,0.1757,0.05072],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47973,0.1642,0.0244]}],"total_contact_groups":12},"final_pose_error":0.11896,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51221,0.2094,0.02499],"final_tcp_position":[0.48813,-0.03174,0.02001],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":53.69543,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42362,0.02089,0.15291],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.14446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3912.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49282,-0.12635,0.02497],"tcp_start":[0.42362,0.02089,0.15291],"tcp_to_object_dist_end":0.18532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48329,0.0935,0.02507],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.24407,"object_to_goal_dist_start":0.2095,"object_z_max":0.02561,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3697.0,"raw_peak_contact_force":34.72563,"tcp_end":[0.47967,0.05621,0.04297],"tcp_start":[0.49282,-0.12635,0.02497],"tcp_to_object_dist_end":0.04152,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.49293,0.20345,0.02556],"object_pos_start":[0.48329,0.0935,0.02507],"object_to_goal_dist_end":0.35352,"object_to_goal_dist_start":0.24407,"object_z_max":0.02756,"peak_contact_force":0.56052,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1534.0,"raw_peak_contact_force":53.69543,"tcp_end":[0.47973,0.1642,0.0244],"tcp_start":[0.47967,0.05621,0.04297],"tcp_to_object_dist_end":0.04142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51221,0.2094,0.02499],"object_pos_start":[0.49293,0.20345,0.02556],"object_to_goal_dist_end":0.35961,"object_to_goal_dist_start":0.35352,"object_z_max":0.03584,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3603.0,"raw_peak_contact_force":20.80373,"tcp_end":[0.48813,-0.03174,0.02001],"tcp_start":[0.47973,0.1642,0.0244],"tcp_to_object_dist_end":0.2424,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51221,0.2094,0.02499],"object_pos_start":[0.51221,0.2094,0.02499],"object_to_goal_dist_end":0.35961,"object_to_goal_dist_start":0.35961,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48103,-0.03177,0.01238],"tcp_start":[0.48813,-0.03174,0.02001],"tcp_to_object_dist_end":0.24351,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```