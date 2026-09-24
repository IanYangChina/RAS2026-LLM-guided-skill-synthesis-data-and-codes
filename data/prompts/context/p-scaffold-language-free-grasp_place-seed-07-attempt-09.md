## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2195 | 0.24 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 6 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.4732 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.376) — your mutation base

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

- **Composite score**: 0.376
- **task_score** (E): 0.305
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1690 |
| descend_1 | 1.00 | 1.00 | 0.0834 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 0.33 | 1.00 | 0.1157 |
| release_1 | 0.33 | 1.00 | 0.1677 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.025, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 9.441 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.025, 0.138)→(0.505, 0.022, 0.054) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.022, 0.054)→(0.497, 0.022, 0.045) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 47.000 | 0.147 | 0.193 |
| lift_1 | lift | 0.33 / step_budget | (0.497, 0.022, 0.045)→(0.502, 0.022, 0.160) | (0.511, 0.022, 0.026)→(0.509, 0.022, 0.135) | 0.273→0.227 | 1.00 / 38.000 | 0.079 | 0.417 |
| release_1 | release | 0.33 / step_budget | (0.502, 0.022, 0.160)→(0.578, 0.159, 0.205) | (0.509, 0.022, 0.135)→(0.578, 0.172, 0.021) | 0.227→0.183 | 1.00 / 3.333 | 0.199 | 1.539 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.419
- phase_score: 0.329
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.release_1_score: 0.571
- phase_breakdown.approach_1_score: 0.114
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.000
- grasp_place_fitness: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.673
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.419
- **Median Q (composite search score)**: 0.352
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29936,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05793,"grasp_1.grip_force":10.22414,"lift_1.speed":0.05646},"optimized_scores":{"best_composite_score":0.43328,"best_fitness_score":0.67328,"best_task_score":0.419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":478.0,"contact_point_centroid":[0.61129,0.18388,-0.00364],"force_p95":0.65423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13362,"mean_force":0.18926,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60985,0.15952,0.14578]},{"body_a":"world","body_b":"grasp_target","contact_count":205.0,"contact_point_centroid":[0.50824,0.03822,-0.00118],"force_p95":0.2459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38766,"mean_force":0.07839,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49701,0.03866,0.04634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13240.0,"contact_point_centroid":[0.54702,0.06987,0.13209],"force_p95":0.1171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37223,"mean_force":0.07176,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54566,0.08876,0.13348]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15360.0,"contact_point_centroid":[0.54617,0.11068,0.13324],"force_p95":0.09732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24302,"mean_force":0.06056,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54885,0.09218,0.13357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19840.0,"contact_point_centroid":[0.49831,0.05778,0.09154],"force_p95":0.07494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24215,"mean_force":0.0507,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49811,0.0386,0.08909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21006.0,"contact_point_centroid":[0.49963,0.0195,0.08958],"force_p95":0.07862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23782,"mean_force":0.04841,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49803,0.0386,0.08807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03974,-0.00208],"force_p95":0.14432,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18758,"mean_force":0.12855,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49987,0.03891,0.04603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5551.0,"contact_point_centroid":[0.50024,0.01963,0.04683],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1539,"mean_force":0.03975,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49866,0.03881,0.04469]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50231,0.02888,0.22227]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50604,0.04011,0.09598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.49897,0.05812,0.04747],"force_p95":0.07516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07883,"mean_force":0.04417,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49866,0.03881,0.04469]}],"total_contact_groups":11},"final_pose_error":0.02099,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61141,0.18387,0.01605],"final_tcp_position":[0.613,0.16031,0.13613],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.13362,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50746,0.04088,0.13839],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50707,0.03951,0.05414],"tcp_start":[0.50746,0.04088,0.13839],"tcp_to_object_dist_end":0.02864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03933,0.02571],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21266,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14371,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12347.0,"raw_peak_contact_force":0.18758,"tcp_end":[0.49863,0.03881,0.04466],"tcp_start":[0.50707,0.03951,0.05414],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50826,0.03938,0.11113],"object_pos_start":[0.51248,0.03933,0.02571],"object_to_goal_dist_end":0.18196,"object_to_goal_dist_start":0.21266,"object_z_max":0.11104,"peak_contact_force":0.07932,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41051.0,"raw_peak_contact_force":0.38766,"tcp_end":[0.5019,0.03875,0.1364],"tcp_start":[0.49863,0.03881,0.04466],"tcp_to_object_dist_end":0.02607,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61141,0.18387,0.01605],"object_pos_start":[0.50826,0.03938,0.11113],"object_to_goal_dist_end":0.13048,"object_to_goal_dist_start":0.18196,"object_z_max":0.11115,"peak_contact_force":0.12407,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":29078.0,"raw_peak_contact_force":1.13362,"tcp_end":[0.60951,0.15935,0.16197],"tcp_start":[0.5019,0.03875,0.1364],"tcp_to_object_dist_end":0.14798,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29375,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05629,"grasp_1.grip_force":15.37929,"lift_1.speed":0.05747},"optimized_scores":{"best_composite_score":0.3437,"best_fitness_score":0.5837,"best_task_score":0.2418},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.54238,0.19032,-0.00712],"force_p95":1.13243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74241,"mean_force":0.36924,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54719,0.17926,0.2182]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.47877,0.0464,-0.00119],"force_p95":0.24098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38506,"mean_force":0.07509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46815,0.04736,0.04768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20068.0,"contact_point_centroid":[0.46856,0.06645,0.09416],"force_p95":0.07509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2439,"mean_force":0.05008,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46911,0.04732,0.09172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20232.0,"contact_point_centroid":[0.47084,0.02824,0.09263],"force_p95":0.07899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23386,"mean_force":0.05016,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46912,0.04732,0.09186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15751.0,"contact_point_centroid":[0.50426,0.12724,0.16568],"force_p95":0.09911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23052,"mean_force":0.06137,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50644,0.10857,0.16551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15038.0,"contact_point_centroid":[0.50916,0.08874,0.16299],"force_p95":0.10351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2284,"mean_force":0.06592,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50559,0.10716,0.16485]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48273,0.04878,-0.0021],"force_p95":0.15073,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1942,"mean_force":0.12991,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47082,0.04764,0.0472]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5098.0,"contact_point_centroid":[0.47153,0.02834,0.04684],"force_p95":0.07651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16259,"mean_force":0.04366,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46965,0.04753,0.04598]},{"body_a":"world","body_b":"grasp_target","contact_count":2280.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48969,0.03262,0.22391]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47786,0.04863,0.09672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5147.0,"contact_point_centroid":[0.46878,0.06674,0.04957],"force_p95":0.07583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07911,"mean_force":0.04281,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46965,0.04753,0.04599]}],"total_contact_groups":11},"final_pose_error":0.0659,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54844,0.18877,0.02403],"final_tcp_position":[0.54981,0.18016,0.19977],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.74241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48028,0.04915,0.13951],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1072.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4778,0.04834,0.05456],"tcp_start":[0.48028,0.04915,0.13951],"tcp_to_object_dist_end":0.02896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04826,0.02565],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29053,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1503,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12045.0,"raw_peak_contact_force":0.1942,"tcp_end":[0.46962,0.04752,0.04595],"tcp_start":[0.4778,0.04834,0.05456],"tcp_to_object_dist_end":0.02417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47834,0.04846,0.11408],"object_pos_start":[0.4827,0.04826,0.02565],"object_to_goal_dist_end":0.23835,"object_to_goal_dist_start":0.29053,"object_z_max":0.11398,"peak_contact_force":0.07965,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40485.0,"raw_peak_contact_force":0.38506,"tcp_end":[0.47284,0.04754,0.14055],"tcp_start":[0.46962,0.04752,0.04595],"tcp_to_object_dist_end":0.02705,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54844,0.18877,0.02403],"object_pos_start":[0.47834,0.04846,0.11408],"object_to_goal_dist_end":0.21295,"object_to_goal_dist_start":0.23835,"object_z_max":0.1665,"peak_contact_force":0.22084,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":30984.0,"raw_peak_contact_force":1.74241,"tcp_end":[0.54712,0.17923,0.22671],"tcp_start":[0.47284,0.04754,0.14055],"tcp_to_object_dist_end":0.2029,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49701,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04901,"grasp_1.grip_force":26.80325,"lift_1.speed":0.09946},"optimized_scores":{"best_composite_score":0.35194,"best_fitness_score":0.59194,"best_task_score":0.25527},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.56642,0.14684,-0.00724],"force_p95":1.19846,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74164,"mean_force":0.38061,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57614,0.13747,0.21685]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.534,-0.01998,-0.00119],"force_p95":0.31587,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47868,"mean_force":0.07525,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52125,-0.02027,0.04549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19147.0,"contact_point_centroid":[0.52572,-0.03967,0.12495],"force_p95":0.07494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31096,"mean_force":0.05302,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52515,-0.0205,0.12216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20718.0,"contact_point_centroid":[0.52623,-0.00141,0.12037],"force_p95":0.07572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30818,"mean_force":0.04989,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52486,-0.02048,0.11857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16897.0,"contact_point_centroid":[0.5559,0.03629,0.19876],"force_p95":0.0977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22678,"mean_force":0.05923,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55274,0.05495,0.19878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17135.0,"contact_point_centroid":[0.55226,0.07422,0.19882],"force_p95":0.09518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21878,"mean_force":0.058,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55285,0.05531,0.19878]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02135,-0.00209],"force_p95":0.14804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19738,"mean_force":0.12964,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52382,-0.0203,0.04518]},{"body_a":"world","body_b":"grasp_target","contact_count":2452.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51418,0.00179,0.2154]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5789.0,"contact_point_centroid":[0.52322,-0.00113,0.04668],"force_p95":0.06151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13243,"mean_force":0.03802,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52257,-0.02028,0.04373]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52961,-0.01799,0.09416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4691.0,"contact_point_centroid":[0.52284,-0.03961,0.04741],"force_p95":0.07293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07615,"mean_force":0.04686,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52258,-0.02028,0.04374]}],"total_contact_groups":11},"final_pose_error":0.09535,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57364,0.1448,0.02377],"final_tcp_position":[0.57888,0.13815,0.19878],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":28.07767,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":28.07767,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2452.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53048,-0.0157,0.13486],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5312,-0.02037,0.05393],"tcp_start":[0.53048,-0.0157,0.13486],"tcp_to_object_dist_end":0.02853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53698,-0.02089,0.02566],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14685,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12280.0,"raw_peak_contact_force":0.19738,"tcp_end":[0.52255,-0.02028,0.0437],"tcp_start":[0.5312,-0.02037,0.05393],"tcp_to_object_dist_end":0.02311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53998,-0.02127,0.17964],"object_pos_start":[0.53698,-0.02089,0.02566],"object_to_goal_dist_end":0.26025,"object_to_goal_dist_start":0.3166,"object_z_max":0.17946,"peak_contact_force":0.07924,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40011.0,"raw_peak_contact_force":0.47868,"tcp_end":[0.5322,-0.02077,0.20418],"tcp_start":[0.52255,-0.02028,0.0437],"tcp_to_object_dist_end":0.02574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57364,0.1448,0.02377],"object_pos_start":[0.53998,-0.02127,0.17964],"object_to_goal_dist_end":0.20482,"object_to_goal_dist_start":0.26025,"object_z_max":0.17978,"peak_contact_force":0.25325,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":34222.0,"raw_peak_contact_force":1.74164,"tcp_end":[0.57608,0.13743,0.22534],"tcp_start":[0.5322,-0.02077,0.20418],"tcp_to_object_dist_end":0.20171,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```