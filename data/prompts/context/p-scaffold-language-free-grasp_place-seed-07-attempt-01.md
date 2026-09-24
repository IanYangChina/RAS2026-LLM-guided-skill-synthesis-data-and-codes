## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1727 | 0.18 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.173) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
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
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
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
- id: release_1
  type: release
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: -0.173
- **task_score** (E): 0.185
- **fitness_score**: 0.377  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1572 |
| descend_1 | 1.00 | 1.00 | 0.0875 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 0.67 | 1.00 | 0.0629 |
| transport_1 | 0.00 | 1.00 | 0.1035 |
| release_1 | 1.00 | 1.00 | 0.0234 |
| retract_1 | 1.00 | 1.00 | 0.0695 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.031, 0.152) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.031, 0.152)→(0.506, 0.023, 0.064) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.023, 0.064)→(0.498, 0.023, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.023, 0.026) | 0.273→0.273 | 1.00 / 27.000 | 0.157 | 0.185 |
| lift_1 | lift | 0.67 / step_budget | (0.501, 0.023, 0.108)→(0.503, 0.033, 0.166) | (0.511, 0.023, 0.026)→(0.507, 0.036, 0.052) | 0.273→0.257 | 1.00 / 9.000 | 0.082 | 0.688 |
| transport_1 | approach | 0.00 / step_budget | (0.503, 0.033, 0.166)→(0.553, 0.120, 0.171) | (0.507, 0.036, 0.052)→(0.510, 0.048, 0.016) | 0.257→0.263 | 1.00 / 8.333 | 94250.728 | 0.577 |
| release_1 | release | 1.00 / step_budget | (0.553, 0.120, 0.171)→(0.548, 0.119, 0.193) | (0.510, 0.048, 0.016)→(0.510, 0.048, 0.016) | 0.263→0.263 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.548, 0.119, 0.193)→(0.545, 0.118, 0.263) | (0.510, 0.048, 0.016)→(0.510, 0.048, 0.016) | 0.263→0.263 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.280
- phase_score: 0.433
- phase_breakdown.goal_target_score: 0.268
- phase_breakdown.approach_target_score: 0.819
- grasp_place_fitness: 0.592

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.592
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.280
- **Median Q (composite search score)**: -0.276
- **K-run variance**: 0.0230
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.505


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45699,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.05267,"approach_1.speed":0.04838,"descend_1.speed":0.08034,"grasp_1.grasp_time":1.38418,"lift_1.speed":0.0999,"release_1.release_time":0.72649,"retract_1.speed":0.03378,"transport_1.speed":0.09705},"optimized_scores":{"best_composite_score":0.04179,"best_fitness_score":0.59179,"best_task_score":0.28038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3624.0,"contact_point_centroid":[0.52255,0.0792,-0.00222],"force_p95":0.12392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4853,"mean_force":0.13252,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5513,0.09156,0.14965]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.51114,0.03978,-0.00109],"force_p95":0.21001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33354,"mean_force":0.08065,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49827,0.03971,0.05724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.51269,0.0227,0.15715],"force_p95":0.27155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27634,"mean_force":0.20609,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50802,0.03959,0.16378]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6584.0,"contact_point_centroid":[0.50401,0.0577,0.09893],"force_p95":0.14513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27613,"mean_force":0.09931,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50113,0.03953,0.10299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6183.0,"contact_point_centroid":[0.50351,0.02129,0.09882],"force_p95":0.14571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2638,"mean_force":0.1048,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50116,0.03953,0.10283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":261.0,"contact_point_centroid":[0.51617,0.0559,0.15676],"force_p95":0.19884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24564,"mean_force":0.12973,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5093,0.04149,0.16243]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03975,-0.00202],"force_p95":0.19386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1973,"mean_force":0.15302,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50058,0.03993,0.05675]},{"body_a":"world","body_b":"grasp_target","contact_count":2784.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12908,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50178,0.04944,0.23876]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50642,0.04421,0.10866]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52254,0.0792,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57725,0.12426,0.14573]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52254,0.0792,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57207,0.12303,0.19345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2682.0,"contact_point_centroid":[0.49999,0.05858,0.05237],"force_p95":0.11121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11741,"mean_force":0.08811,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03984,0.05547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2929.0,"contact_point_centroid":[0.49971,0.02116,0.05223],"force_p95":0.10713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11373,"mean_force":0.08034,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03984,0.05547]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3610.0,"contact_point_centroid":[0.55371,0.09388,0.15148],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01573,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55336,0.09386,0.14925]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.58071,0.12503,0.14373],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01005,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58018,0.12501,0.14134]}],"total_contact_groups":15},"final_pose_error":0.04471,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52254,0.0792,0.01602],"final_tcp_position":[0.57215,0.12303,0.22118],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.93834,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2784.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_target","tcp_end":[0.5079,0.04801,0.15314],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50738,0.04054,0.06454],"tcp_start":[0.5079,0.04801,0.15314],"tcp_to_object_dist_end":0.03887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.03987,0.02591],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.19206,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7411.0,"raw_peak_contact_force":0.1973,"tcp_end":[0.49942,0.03984,0.05543],"tcp_start":[0.50738,0.04054,0.06454],"tcp_to_object_dist_end":0.03228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.51374,0.04151,0.12345],"object_pos_start":[0.51245,0.03987,0.02591],"object_to_goal_dist_end":0.17489,"object_to_goal_dist_start":0.21222,"object_z_max":0.12363,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12911.0,"raw_peak_contact_force":0.33354,"tcp_end":[0.50793,0.03956,0.16373],"tcp_start":[0.49942,0.03984,0.05543],"tcp_to_object_dist_end":0.04074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52254,0.0792,0.01602],"object_pos_start":[0.51374,0.04151,0.12345],"object_to_goal_dist_end":0.19074,"object_to_goal_dist_start":0.17489,"object_z_max":0.12345,"peak_contact_force":9748.93834,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7507.0,"raw_peak_contact_force":1.4853,"subtask_id":"goal_target","tcp_end":[0.5817,0.12518,0.14403],"tcp_start":[0.50793,0.03956,0.16373],"tcp_to_object_dist_end":0.14833,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52254,0.0792,0.01602],"object_pos_start":[0.52254,0.0792,0.01602],"object_to_goal_dist_end":0.19074,"object_to_goal_dist_start":0.19074,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5755,0.12382,0.16576],"tcp_start":[0.5817,0.12518,0.14403],"tcp_to_object_dist_end":0.16498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52254,0.0792,0.01602],"object_pos_start":[0.52254,0.0792,0.01602],"object_to_goal_dist_end":0.19074,"object_to_goal_dist_start":0.19074,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57215,0.12303,0.22118],"tcp_start":[0.5755,0.12382,0.16576],"tcp_to_object_dist_end":0.21558,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20435,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08599,"approach_1.speed":0.0974,"descend_1.speed":0.03682,"grasp_1.grasp_time":0.78921,"lift_1.speed":0.09781,"release_1.release_time":0.29766,"retract_1.speed":0.04497,"transport_1.speed":0.02347},"optimized_scores":{"best_composite_score":-0.27604,"best_fitness_score":0.27396,"best_task_score":0.14637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.47854,0.06465,-0.00245],"force_p95":0.34494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93311,"mean_force":0.13727,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4757,0.0509,0.14673]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4679.0,"contact_point_centroid":[0.4713,0.03002,0.08383],"force_p95":0.14095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36353,"mean_force":0.09651,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47029,0.04844,0.0878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5133.0,"contact_point_centroid":[0.47205,0.0667,0.08526],"force_p95":0.12661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26737,"mean_force":0.08943,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47044,0.04843,0.08951]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04873,-0.00202],"force_p95":0.12855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14842,"mean_force":0.1244,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47151,0.04893,0.05763]},{"body_a":"world","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49147,0.06347,0.24579]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47761,0.05378,0.10789]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47813,0.06661,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49791,0.10226,0.17826]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47813,0.06661,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5165,0.13614,0.1935]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47813,0.06661,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51231,0.135,0.25161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2936.0,"contact_point_centroid":[0.47041,0.03005,0.05299],"force_p95":0.0914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09147,"mean_force":0.0701,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47043,0.04883,0.05649]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2924.0,"contact_point_centroid":[0.47039,0.06757,0.05287],"force_p95":0.09134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09139,"mean_force":0.07035,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47043,0.04883,0.05649]},{"body_a":"left_finger","body_b":"right_finger","contact_count":807.0,"contact_point_centroid":[0.4771,0.05241,0.16508],"force_p95":0.01292,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01897,"mean_force":0.01102,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47663,0.05239,0.16289]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4222.0,"contact_point_centroid":[0.49839,0.10239,0.18054],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49799,0.10238,0.1783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.51932,0.13686,0.19037],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01041,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51892,0.13684,0.18823]}],"total_contact_groups":14},"final_pose_error":0.02563,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47813,0.06661,0.01602],"final_tcp_position":[0.51253,0.13503,0.28864],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.93311,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3008.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_target","tcp_end":[0.47968,0.05805,0.15113],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47799,0.04962,0.06457],"tcp_start":[0.47968,0.05805,0.15113],"tcp_to_object_dist_end":0.03884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04877,0.02592],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29005,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12834,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7660.0,"raw_peak_contact_force":0.14842,"tcp_end":[0.4704,0.04882,0.05646],"tcp_start":[0.47799,0.04962,0.06457],"tcp_to_object_dist_end":0.0329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":811.0,"n_steps_budget":780.0,"object_pos_end":[0.47813,0.06661,0.01601],"object_pos_start":[0.48262,0.04877,0.02592],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.29005,"object_z_max":0.09029,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11867.0,"raw_peak_contact_force":0.93311,"tcp_end":[0.47481,0.06135,0.16824],"tcp_start":[0.47829,0.04842,0.1644],"tcp_to_object_dist_end":0.15236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47813,0.06661,0.01602],"object_pos_start":[0.47813,0.06661,0.01602],"object_to_goal_dist_end":0.28824,"object_to_goal_dist_start":0.28824,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8222.0,"raw_peak_contact_force":0.12263,"subtask_id":"goal_target","tcp_end":[0.52019,0.13703,0.19041],"tcp_start":[0.47481,0.06135,0.16824],"tcp_to_object_dist_end":0.19272,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47813,0.06661,0.01602],"object_pos_start":[0.47813,0.06661,0.01602],"object_to_goal_dist_end":0.28824,"object_to_goal_dist_start":0.28824,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51508,0.13573,0.21414],"tcp_start":[0.52019,0.13703,0.19041],"tcp_to_object_dist_end":0.21306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47813,0.06661,0.01602],"object_pos_start":[0.47813,0.06661,0.01602],"object_to_goal_dist_end":0.28824,"object_to_goal_dist_start":0.28824,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51253,0.13503,0.28864],"tcp_start":[0.51508,0.13573,0.21414],"tcp_to_object_dist_end":0.28318,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96109,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.17238,"approach_1.speed":0.08818,"descend_1.speed":0.02924,"grasp_1.grasp_time":0.85641,"lift_1.speed":0.01029,"release_1.release_time":0.70941,"retract_1.speed":0.04846,"transport_1.speed":0.06546},"optimized_scores":{"best_composite_score":-0.28386,"best_fitness_score":0.26614,"best_task_score":0.12744},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3760.0,"contact_point_centroid":[0.52926,-0.00323,-0.00205],"force_p95":0.14105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79853,"mean_force":0.12759,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52328,-0.01188,0.12522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9118.0,"contact_point_centroid":[0.52188,-0.00124,0.07076],"force_p95":0.12572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26448,"mean_force":0.08791,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52176,-0.01989,0.07441]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02122,-0.00211],"force_p95":0.1549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20853,"mean_force":0.1305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52452,-0.01991,0.05564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10370.0,"contact_point_centroid":[0.52219,-0.03832,0.0715],"force_p95":0.1033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20019,"mean_force":0.07628,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52186,-0.01989,0.07529]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51524,0.01284,0.22134]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5301,-0.0165,0.10735]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52945,-0.00099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54167,0.05222,0.17038]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52945,-0.00099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55431,0.0966,0.17993]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52945,-0.00099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5498,0.09572,0.23909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2466.0,"contact_point_centroid":[0.52467,-0.00117,0.05146],"force_p95":0.10476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11213,"mean_force":0.08134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.01989,0.05424]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2943.0,"contact_point_centroid":[0.52392,-0.03855,0.05109],"force_p95":0.09536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09992,"mean_force":0.07039,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.01989,0.05424]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3309.0,"contact_point_centroid":[0.52371,-0.01024,0.13714],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01057,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52333,-0.01023,0.13482]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4247.0,"contact_point_centroid":[0.54201,0.05226,0.17271],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54169,0.05226,0.17039]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.55734,0.09716,0.17736],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01002,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55696,0.09716,0.17517]}],"total_contact_groups":14},"final_pose_error":0.02169,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52945,-0.00099,0.01602],"final_tcp_position":[0.55004,0.09574,0.27872],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273003.1233,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_target","tcp_end":[0.53137,-0.01317,0.15054],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53153,-0.02001,0.06411],"tcp_start":[0.53137,-0.01317,0.15054],"tcp_to_object_dist_end":0.0385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53699,-0.02031,0.02564],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31616,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15095,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7209.0,"raw_peak_contact_force":0.20853,"tcp_end":[0.52331,-0.01989,0.0542],"tcp_start":[0.53153,-0.02001,0.06411],"tcp_to_object_dist_end":0.03167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1765.0,"n_steps_budget":1000.0,"object_pos_end":[0.52932,-0.0008,0.01607],"object_pos_start":[0.53699,-0.02031,0.02564],"object_to_goal_dist_end":0.30889,"object_to_goal_dist_start":0.31616,"object_z_max":0.05659,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26557.0,"raw_peak_contact_force":0.79853,"tcp_end":[0.52524,-0.00162,0.16701],"tcp_start":[0.52506,-0.01999,0.1035],"tcp_to_object_dist_end":0.151,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52945,-0.00099,0.01602],"object_pos_start":[0.52945,-0.00099,0.01602],"object_to_goal_dist_end":0.30902,"object_to_goal_dist_start":0.30902,"object_z_max":0.01602,"peak_contact_force":273003.1233,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8247.0,"raw_peak_contact_force":0.12263,"subtask_id":"goal_target","tcp_end":[0.55831,0.0972,0.17757],"tcp_start":[0.52524,-0.00162,0.16701],"tcp_to_object_dist_end":0.19124,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52945,-0.00099,0.01602],"object_pos_start":[0.52945,-0.00099,0.01602],"object_to_goal_dist_end":0.30902,"object_to_goal_dist_start":0.30902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55276,0.09627,0.20023],"tcp_start":[0.55831,0.0972,0.17757],"tcp_to_object_dist_end":0.20962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52945,-0.00099,0.01602],"object_pos_start":[0.52945,-0.00099,0.01602],"object_to_goal_dist_end":0.30902,"object_to_goal_dist_start":0.30902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55004,0.09574,0.27872],"tcp_start":[0.55276,0.09627,0.20023],"tcp_to_object_dist_end":0.2807,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```