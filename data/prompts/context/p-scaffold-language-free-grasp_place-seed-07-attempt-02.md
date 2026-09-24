## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4331 | 0.19 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1727 | 0.18 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.433) — your mutation base

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

- **Composite score**: -0.433
- **task_score** (E): 0.190
- **fitness_score**: 0.167  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.2399 |
| descend_1 | 0.00 | 1.00 | 0.0274 |
| grasp_1 | 1.00 | 1.00 | 0.0005 |
| lift_1 | 0.33 | 1.00 | 0.1139 |
| transport_1 | 0.33 | 1.00 | 0.1129 |
| release_1 | 1.00 | 1.00 | 0.0239 |
| retract_1 | 0.00 | 1.00 | 0.1013 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.648, 0.118, 0.155) | (0.511, 0.022, 0.030)→(0.555, 0.036, 0.014) | 0.271→0.260 | 1.00 / 5.667 | 349.626 | 1473.850 |
| descend_1 | descend | 0.00 / step_budget | (0.648, 0.118, 0.155)→(0.629, 0.104, 0.167) | (0.555, 0.036, 0.014)→(0.553, 0.035, 0.015) | 0.260→0.261 | 1.00 / 6.000 | 284.175 | 327.278 |
| grasp_1 | grasp | 1.00 / step_budget | (0.629, 0.104, 0.167)→(0.629, 0.104, 0.167) | (0.553, 0.035, 0.015)→(0.553, 0.036, 0.015) | 0.261→0.260 | 1.00 / 10.333 | 83.621 | 114.389 |
| lift_1 | lift | 0.33 / step_budget | (0.629, 0.104, 0.167)→(0.560, 0.052, 0.235) | (0.553, 0.036, 0.015)→(0.551, 0.035, 0.016) | 0.260→0.260 | 1.00 / 8.000 | 3325.898 | 160.800 |
| transport_1 | approach | 0.33 / step_budget | (0.560, 0.052, 0.235)→(0.591, 0.142, 0.288) | (0.551, 0.035, 0.016)→(0.554, 0.040, 0.016) | 0.260→0.256 | 1.00 / 8.000 | 3249.877 | 48.197 |
| release_1 | release | 1.00 / step_budget | (0.591, 0.142, 0.288)→(0.589, 0.141, 0.312) | (0.554, 0.040, 0.016)→(0.554, 0.040, 0.017) | 0.256→0.256 | 1.00 / 3.333 | 0.148 | 0.216 |
| retract_1 | retract | 0.00 / step_budget | (0.589, 0.141, 0.312)→(0.600, 0.175, 0.406) | (0.554, 0.040, 0.017)→(0.553, 0.038, 0.016) | 0.256→0.257 | 1.00 / 4.000 | 27.129 | 0.191 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.274
- phase_score: 0.362
- phase_breakdown.reach_goal_score: 0.484
- phase_breakdown.reach_pre_contact_score: 0.076
- grasp_place_fitness: 0.202

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.202
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.274
- **Median Q (composite search score)**: -0.436
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93514,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.10462,"approach_1.speed":0.02707,"descend_1.speed":0.01898,"grasp_1.grasp_time":1.10874,"lift_1.lift_height":0.14723,"lift_1.speed":0.03787,"release_1.release_time":1.49116,"retract_1.speed":0.05275,"transport_1.speed":0.04354},"optimized_scores":{"best_composite_score":-0.39822,"best_fitness_score":0.20178,"best_task_score":0.27396},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":894.0,"contact_point_centroid":[0.4741,-0.0405,-0.00055],"force_p95":508.3524,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1599.66796,"mean_force":371.66413,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.61357,0.10837,0.18272]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.48814,-0.03763,-0.00033],"force_p95":328.89308,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.96944,"mean_force":303.75902,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.62556,0.10662,0.19252]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.48534,-0.05739,-0.00026],"force_p95":270.87614,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.94381,"mean_force":218.5637,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.59566,0.07978,0.21727]},{"body_a":"world","body_b":"link6","contact_count":61.0,"contact_point_centroid":[0.47677,-0.06538,-0.0001],"force_p95":137.57322,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.34571,"mean_force":90.16592,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55992,0.04431,0.25014]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.49157,-0.04303,-0.00016],"force_p95":105.84728,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.16419,"mean_force":87.09828,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.62438,0.10208,0.19546]},{"body_a":"grasp_target","body_b":"link6","contact_count":55.0,"contact_point_centroid":[0.50177,0.02256,0.05213],"force_p95":3.01671,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.23905,"mean_force":0.71274,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46152,0.17058,0.1482]},{"body_a":"grasp_target","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.49965,0.04598,0.05343],"force_p95":1.56071,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.62312,"mean_force":0.49707,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46437,0.17155,0.15021]},{"body_a":"world","body_b":"grasp_target","contact_count":3834.0,"contact_point_centroid":[0.55443,0.0333,-0.00207],"force_p95":0.17975,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61469,"mean_force":0.13694,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.59909,0.10169,0.18429]},{"body_a":"world","body_b":"grasp_target","contact_count":400.0,"contact_point_centroid":[0.573,0.05699,-0.0044],"force_p95":0.37389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40142,"mean_force":0.27574,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60945,0.14187,0.28005]},{"body_a":"world","body_b":"grasp_target","contact_count":3528.0,"contact_point_centroid":[0.56376,0.03504,-0.00231],"force_p95":0.31681,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35097,"mean_force":0.14736,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58224,0.08945,0.26084]},{"body_a":"world","body_b":"grasp_target","contact_count":3988.0,"contact_point_centroid":[0.56572,0.04125,-0.00201],"force_p95":0.12367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32655,"mean_force":0.12373,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.615,0.15137,0.34136]},{"body_a":"grasp_target","body_b":"link6","contact_count":395.0,"contact_point_centroid":[0.53395,0.03497,0.0398],"force_p95":0.21789,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26527,"mean_force":0.17193,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.6008,0.12441,0.27183]},{"body_a":"grasp_target","body_b":"link6","contact_count":162.0,"contact_point_centroid":[0.5413,0.04974,0.0414],"force_p95":0.20766,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24221,"mean_force":0.16756,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60947,0.14192,0.27669]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56178,0.03233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.62556,0.10662,0.19252]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.56178,0.03233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.62438,0.10208,0.19546]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56178,0.03233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.59566,0.07978,0.21727]}],"total_contact_groups":20},"final_pose_error":0.06323,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56568,0.04119,0.01602],"final_tcp_position":[0.62071,0.16032,0.38337],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1599.66796,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56178,0.03233,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.20156,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":331.01771,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4831.0,"raw_peak_contact_force":1599.66796,"subtask_id":"reach_pre_contact","tcp_end":[0.62812,0.10979,0.18741],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19944,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56178,0.03233,0.01602],"object_pos_start":[0.56178,0.03233,0.01602],"object_to_goal_dist_end":0.20156,"object_to_goal_dist_start":0.20156,"object_z_max":0.01602,"peak_contact_force":294.62563,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":383.96944,"subtask_id":"reach_pre_contact","tcp_end":[0.62401,0.10207,0.1951],"tcp_start":[0.62812,0.10979,0.18741],"tcp_to_object_dist_end":0.20201,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56178,0.03233,0.01602],"object_pos_start":[0.56178,0.03233,0.01602],"object_to_goal_dist_end":0.20156,"object_to_goal_dist_start":0.20156,"object_z_max":0.01602,"peak_contact_force":82.70481,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2600.0,"raw_peak_contact_force":114.16419,"tcp_end":[0.62448,0.10209,0.19551],"tcp_start":[0.62401,0.10207,0.1951],"tcp_to_object_dist_end":0.20252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56178,0.03233,0.01602],"object_pos_start":[0.56178,0.03233,0.01602],"object_to_goal_dist_end":0.20156,"object_to_goal_dist_start":0.20156,"object_z_max":0.01602,"peak_contact_force":228.51055,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9399.0,"raw_peak_contact_force":271.94381,"tcp_end":[0.55772,0.04238,0.25031],"tcp_start":[0.62448,0.10209,0.19551],"tcp_to_object_dist_end":0.23454,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.569,0.04679,0.01743],"object_pos_start":[0.56178,0.03233,0.01602],"object_to_goal_dist_end":0.18847,"object_to_goal_dist_start":0.20156,"object_z_max":0.01742,"peak_contact_force":0.31409,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8337.0,"raw_peak_contact_force":144.34571,"subtask_id":"reach_goal","tcp_end":[0.61039,0.14212,0.27769],"tcp_start":[0.55772,0.04238,0.25031],"tcp_to_object_dist_end":0.28024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56845,0.04554,0.01753],"object_pos_start":[0.569,0.04679,0.01743],"object_to_goal_dist_end":0.18941,"object_to_goal_dist_start":0.18847,"object_z_max":0.01944,"peak_contact_force":0.19753,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":785.0,"raw_peak_contact_force":0.40142,"subtask_id":"reach_goal","tcp_end":[0.60933,0.14163,0.30029],"tcp_start":[0.61039,0.14212,0.27769],"tcp_to_object_dist_end":0.30143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56568,0.04119,0.01602],"object_pos_start":[0.56845,0.04554,0.01753],"object_to_goal_dist_end":0.19422,"object_to_goal_dist_start":0.18941,"object_z_max":0.01753,"peak_contact_force":81.14225,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":0.32655,"tcp_end":[0.62071,0.16032,0.38337],"tcp_start":[0.60933,0.14163,0.30029],"tcp_to_object_dist_end":0.39008,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6747,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.19939,"approach_1.speed":0.07049,"descend_1.speed":0.07719,"grasp_1.grasp_time":1.27784,"lift_1.lift_height":0.24367,"lift_1.speed":0.07698,"release_1.release_time":1.2861,"retract_1.speed":0.08166,"transport_1.speed":0.05343},"optimized_scores":{"best_composite_score":-0.43599,"best_fitness_score":0.16401,"best_task_score":0.17027},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":895.0,"contact_point_centroid":[0.47678,-0.04644,-0.00053],"force_p95":496.8008,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1452.67812,"mean_force":366.16381,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.61979,0.12299,0.16006]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.47694,-0.04988,-0.00028],"force_p95":254.54815,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.48569,"mean_force":233.70303,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.62616,0.13155,0.14714]},{"body_a":"world","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.40935,0.07861,-0.00061],"force_p95":222.02339,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.91656,"mean_force":177.01267,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4173,0.17733,0.12394]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.46706,-0.05818,-0.00012],"force_p95":123.41733,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.21074,"mean_force":95.86965,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.61011,0.12413,0.15248]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.467,-0.05808,-0.00016],"force_p95":108.37351,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.46217,"mean_force":88.75352,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.61005,0.12419,0.15245]},{"body_a":"grasp_target","body_b":"link7","contact_count":619.0,"contact_point_centroid":[0.53524,0.08621,0.03199],"force_p95":1.34258,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.34926,"mean_force":0.38382,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.61243,0.13021,0.15335]},{"body_a":"grasp_target","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.47519,0.04875,0.03392],"force_p95":2.762,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91259,"mean_force":0.63232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41661,0.17701,0.12337]},{"body_a":"world","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.51794,0.08472,-0.00266],"force_p95":0.34802,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77526,"mean_force":0.18468,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.60806,0.11426,0.16379]},{"body_a":"grasp_target","body_b":"link7","contact_count":171.0,"contact_point_centroid":[0.51395,0.07785,0.03524],"force_p95":0.42593,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.6716,"mean_force":0.22419,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.59873,0.1211,0.15852]},{"body_a":"grasp_target","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.53737,0.08695,0.02875],"force_p95":0.38998,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54823,"mean_force":0.31052,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.62616,0.13155,0.14714]},{"body_a":"world","body_b":"grasp_target","contact_count":3684.0,"contact_point_centroid":[0.50549,0.09132,-0.00217],"force_p95":0.25839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49464,"mean_force":0.13769,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56004,0.10895,0.19847]},{"body_a":"grasp_target","body_b":"hand","contact_count":140.0,"contact_point_centroid":[0.5356,0.10386,0.03947],"force_p95":0.20531,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37624,"mean_force":0.13697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60044,0.12161,0.15724]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5184,0.09227,-0.00315],"force_p95":0.2463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34942,"mean_force":0.19865,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.62616,0.13155,0.14714]},{"body_a":"grasp_target","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.52561,0.07863,0.02979],"force_p95":0.2456,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2638,"mean_force":0.23337,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.61005,0.12419,0.15245]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51103,0.09264,-0.00293],"force_p95":0.21333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23854,"mean_force":0.18122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.61005,0.12419,0.15245]},{"body_a":"grasp_target","body_b":"hand","contact_count":652.0,"contact_point_centroid":[0.54945,0.10502,0.03366],"force_p95":0.09288,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14686,"mean_force":0.06776,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.62055,0.12962,0.14932]}],"total_contact_groups":24},"final_pose_error":0.05845,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50641,0.09163,0.01602],"final_tcp_position":[0.57402,0.21411,0.47447],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1452.67812,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52582,0.09108,0.01299],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.26349,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":326.9955,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5305.0,"raw_peak_contact_force":1452.67812,"subtask_id":"reach_pre_contact","tcp_end":[0.64289,0.13599,0.13863],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1775,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51223,0.09134,0.01385],"object_pos_start":[0.52582,0.09108,0.01299],"object_to_goal_dist_end":0.26588,"object_to_goal_dist_start":0.26349,"object_z_max":0.01385,"peak_contact_force":255.61539,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6652.0,"raw_peak_contact_force":274.48569,"subtask_id":"reach_pre_contact","tcp_end":[0.60976,0.12418,0.1526],"tcp_start":[0.64289,0.13599,0.13863],"tcp_to_object_dist_end":0.17276,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51082,0.09265,0.01427],"object_pos_start":[0.51223,0.09134,0.01385],"object_to_goal_dist_end":0.26523,"object_to_goal_dist_start":0.26588,"object_z_max":0.01427,"peak_contact_force":84.98051,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3492.0,"raw_peak_contact_force":118.46217,"tcp_end":[0.61015,0.12412,0.15241],"tcp_start":[0.60976,0.12418,0.1526],"tcp_to_object_dist_end":0.17304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.50641,0.09163,0.01602],"object_pos_start":[0.51082,0.09265,0.01427],"object_to_goal_dist_end":0.26556,"object_to_goal_dist_start":0.26523,"object_z_max":0.01654,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8206.0,"raw_peak_contact_force":126.21074,"tcp_end":[0.51381,0.09423,0.24865],"tcp_start":[0.61015,0.12412,0.15241],"tcp_to_object_dist_end":0.23277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50641,0.09163,0.01602],"object_pos_start":[0.50641,0.09163,0.01602],"object_to_goal_dist_end":0.26556,"object_to_goal_dist_start":0.26556,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8358.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55418,0.17631,0.32372],"tcp_start":[0.51381,0.09423,0.24865],"tcp_to_object_dist_end":0.3227,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50641,0.09163,0.01602],"object_pos_start":[0.50641,0.09163,0.01602],"object_to_goal_dist_end":0.26556,"object_to_goal_dist_start":0.26556,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55281,0.176,0.34872],"tcp_start":[0.55418,0.17631,0.32372],"tcp_to_object_dist_end":0.34635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50641,0.09163,0.01602],"object_pos_start":[0.50641,0.09163,0.01602],"object_to_goal_dist_end":0.26556,"object_to_goal_dist_start":0.26556,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57402,0.21411,0.47447],"tcp_start":[0.55281,0.176,0.34872],"tcp_to_object_dist_end":0.47932,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11538,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.13372,"approach_1.speed":0.05573,"descend_1.speed":0.06572,"grasp_1.grasp_time":1.13335,"lift_1.lift_height":0.23014,"lift_1.speed":0.0443,"release_1.release_time":0.81846,"retract_1.speed":0.04334,"transport_1.speed":0.05068},"optimized_scores":{"best_composite_score":-0.46523,"best_fitness_score":0.13477,"best_task_score":0.12445},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":895.0,"contact_point_centroid":[0.4871,-0.05233,-0.00055],"force_p95":533.82107,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1369.20297,"mean_force":406.92821,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.63729,0.11014,0.15941]},{"body_a":"world","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.41388,0.0754,-0.00053],"force_p95":790.24913,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1089.01194,"mean_force":267.31608,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42151,0.17475,0.12357]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.49713,-0.0663,-0.00031],"force_p95":301.66263,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.37815,"mean_force":275.90399,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.66195,0.10062,0.14757]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.4945,-0.08146,-0.00016],"force_p95":103.37247,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.54208,"mean_force":86.55202,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.65355,0.087,0.15249]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.49454,-0.0816,-0.00011],"force_p95":81.5353,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.24554,"mean_force":66.8267,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.65356,0.08692,0.15256]},{"body_a":"grasp_target","body_b":"link6","contact_count":906.0,"contact_point_centroid":[0.54315,-0.0204,0.03489],"force_p95":0.86673,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.45859,"mean_force":0.60741,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.63456,0.11082,0.15888]},{"body_a":"world","body_b":"grasp_target","contact_count":3148.0,"contact_point_centroid":[0.55195,-0.01939,-0.00483],"force_p95":0.54758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99249,"mean_force":0.32301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.61493,0.10264,0.16518]},{"body_a":"grasp_target","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.55418,-0.02562,0.02792],"force_p95":0.40138,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42908,"mean_force":0.28232,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.66195,0.10062,0.14757]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58309,-0.01625,-0.00309],"force_p95":0.30024,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31527,"mean_force":0.19098,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.66195,0.10062,0.14757]},{"body_a":"grasp_target","body_b":"link6","contact_count":37.0,"contact_point_centroid":[0.55849,-0.03234,0.03304],"force_p95":0.23345,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26805,"mean_force":0.1475,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.652,0.0855,0.15296]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5857,-0.0181,-0.00202],"force_p95":0.13423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24724,"mean_force":0.12451,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.62889,0.05242,0.17677]},{"body_a":"grasp_target","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.57655,-0.0021,0.03634],"force_p95":0.1722,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24189,"mean_force":0.12847,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.64719,0.07999,0.15383]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.58551,-0.01771,-0.00247],"force_p95":0.19381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24062,"mean_force":0.15227,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.65355,0.087,0.15249]},{"body_a":"grasp_target","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.55846,-0.03114,0.03258],"force_p95":0.13394,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20012,"mean_force":0.1256,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.65355,0.087,0.15249]},{"body_a":"grasp_target","body_b":"link7","contact_count":186.0,"contact_point_centroid":[0.58327,0.00465,0.04927],"force_p95":0.13987,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14597,"mean_force":0.11333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.65886,0.10735,0.15238]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58566,-0.01815,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60663,0.06518,0.23296]}],"total_contact_groups":22},"final_pose_error":0.16662,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58566,-0.01815,0.01602],"final_tcp_position":[0.60606,0.14997,0.36012],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9749.19291,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57873,-0.01684,0.01277],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31418,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":390.86469,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5143.0,"raw_peak_contact_force":1369.20297,"subtask_id":"reach_pre_contact","tcp_end":[0.67239,0.10955,0.13896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20167,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58449,-0.01902,0.01483],"object_pos_start":[0.57873,-0.01684,0.01277],"object_to_goal_dist_end":0.31409,"object_to_goal_dist_start":0.31418,"object_z_max":0.01483,"peak_contact_force":302.28335,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6000.0,"raw_peak_contact_force":323.37815,"subtask_id":"reach_pre_contact","tcp_end":[0.65315,0.08704,0.15253],"tcp_start":[0.67239,0.10955,0.13896],"tcp_to_object_dist_end":0.18688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58595,-0.01794,0.01513],"object_pos_start":[0.58449,-0.01902,0.01483],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.31409,"object_z_max":0.01513,"peak_contact_force":83.17694,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3051.0,"raw_peak_contact_force":110.54208,"tcp_end":[0.65365,0.08695,0.15246],"tcp_start":[0.65315,0.08704,0.15253],"tcp_to_object_dist_end":0.18558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58566,-0.01815,0.01602],"object_pos_start":[0.58595,-0.01794,0.01513],"object_to_goal_dist_end":0.31258,"object_to_goal_dist_start":0.31294,"object_z_max":0.01603,"peak_contact_force":9749.06107,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8563.0,"raw_peak_contact_force":84.24554,"tcp_end":[0.60791,0.01971,0.20585],"tcp_start":[0.65365,0.08695,0.15246],"tcp_to_object_dist_end":0.19484,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58566,-0.01815,0.01602],"object_pos_start":[0.58566,-0.01815,0.01602],"object_to_goal_dist_end":0.31258,"object_to_goal_dist_start":0.31258,"object_z_max":0.01602,"peak_contact_force":9749.19291,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8479.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.60724,0.10687,0.26319],"tcp_start":[0.60791,0.01971,0.20585],"tcp_to_object_dist_end":0.27782,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58566,-0.01815,0.01602],"object_pos_start":[0.58566,-0.01815,0.01602],"object_to_goal_dist_end":0.31258,"object_to_goal_dist_start":0.31258,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.60514,0.10671,0.28712],"tcp_start":[0.60724,0.10687,0.26319],"tcp_to_object_dist_end":0.29911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58566,-0.01815,0.01602],"object_pos_start":[0.58566,-0.01815,0.01602],"object_to_goal_dist_end":0.31258,"object_to_goal_dist_start":0.31258,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60606,0.14997,0.36012],"tcp_start":[0.60514,0.10671,0.28712],"tcp_to_object_dist_end":0.38352,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```