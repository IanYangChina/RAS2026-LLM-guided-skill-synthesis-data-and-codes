## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2195 | 0.24 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 6 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.4732 | 0.17 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.3731 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.220) — your mutation base

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

- **Composite score**: 0.220
- **task_score** (E): 0.235
- **fitness_score**: 0.570  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1393 |
| descend_1 | 1.00 | 1.00 | 0.1038 |
| grasp_1 | 1.00 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 1.00 | 0.1304 |
| transport_1 | 1.00 | 1.00 | 0.2556 |
| descend_to_goal | 1.00 | 1.00 | 0.1155 |
| release_1 | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.025, 0.168) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.025, 0.168)→(0.506, 0.022, 0.064) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.064)→(0.497, 0.022, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 29.667 | 0.147 | 0.192 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.022, 0.055)→(0.494, 0.022, 0.185) | (0.511, 0.022, 0.026)→(0.498, 0.022, 0.151) | 0.273→0.227 | 1.00 / 21.667 | 0.119 | 0.250 |
| transport_1 | approach | 1.00 / step_budget | (0.494, 0.022, 0.185)→(0.599, 0.200, 0.329) | (0.498, 0.022, 0.151)→(0.525, 0.112, 0.016) | 0.227→0.220 | 1.00 / 8.000 | 6499.321 | 1.794 |
| descend_to_goal | descend | 1.00 / step_budget | (0.599, 0.200, 0.329)→(0.602, 0.207, 0.213) | (0.525, 0.112, 0.016)→(0.525, 0.112, 0.016) | 0.220→0.220 | 1.00 / 8.000 | 3249.718 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.207, 0.213)→(0.597, 0.205, 0.233) | (0.525, 0.112, 0.016)→(0.525, 0.112, 0.016) | 0.220→0.220 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.297
- phase_score: 0.065
- phase_breakdown.pre_grasp_score: 0.217
- phase_breakdown.reach_goal_score: 0.000
- grasp_place_fitness: 0.601

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.601
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.297
- **Median Q (composite search score)**: 0.219
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.348


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11475,"average_solve_count":305.0,"average_success_count":305.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04179,"descend_to_goal.speed":0.07568,"lift_1.speed":0.01239,"transport_1.speed":0.09305},"optimized_scores":{"best_composite_score":0.25054,"best_fitness_score":0.60054,"best_task_score":0.2972},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1654.0,"contact_point_centroid":[0.54561,0.07382,-0.00266],"force_p95":0.28317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71993,"mean_force":0.14978,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58001,0.12642,0.25036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1460.0,"contact_point_centroid":[0.50755,0.07214,0.19006],"force_p95":0.19664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38934,"mean_force":0.10587,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50877,0.05363,0.19403]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.50913,0.03883,-0.00156],"force_p95":0.22419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24575,"mean_force":0.10138,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49777,0.03859,0.05544]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1921.0,"contact_point_centroid":[0.51224,0.03787,0.19087],"force_p95":0.12743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23526,"mean_force":0.07682,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51046,0.05547,0.19529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5904.0,"contact_point_centroid":[0.49554,0.01975,0.11037],"force_p95":0.12306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2082,"mean_force":0.08121,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49527,0.03839,0.11366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5947.0,"contact_point_centroid":[0.49404,0.05704,0.11112],"force_p95":0.1047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19855,"mean_force":0.07992,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49529,0.03839,0.11392]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0397,-0.00207],"force_p95":0.14367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18221,"mean_force":0.12794,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50017,0.03879,0.05613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3384.0,"contact_point_centroid":[0.50013,0.01982,0.05176],"force_p95":0.09974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15448,"mean_force":0.06163,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49898,0.0387,0.05478]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50247,0.02534,0.23846]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50587,0.03958,0.11585]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.54561,0.0737,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61917,0.16666,0.22394]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54561,0.0737,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61741,0.16852,0.16282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3214.0,"contact_point_centroid":[0.4978,0.0576,0.0521],"force_p95":0.09484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09541,"mean_force":0.06519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49899,0.0387,0.05479]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1572.0,"contact_point_centroid":[0.58476,0.13118,0.25654],"force_p95":0.01146,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01043,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58488,0.1313,0.25427]},{"body_a":"left_finger","body_b":"right_finger","contact_count":892.0,"contact_point_centroid":[0.61901,0.16647,0.22631],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61917,0.16666,0.22407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.61993,0.1691,0.16081],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62,0.16929,0.1586]}],"total_contact_groups":16},"final_pose_error":0.01961,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54561,0.0737,0.01602],"final_tcp_position":[0.62224,0.16988,0.16371],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.71993,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50716,0.03998,0.16891],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.50724,0.03938,0.06425],"tcp_start":[0.50716,0.03998,0.16891],"tcp_to_object_dist_end":0.0386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03924,0.02574],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21267,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14227,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8398.0,"raw_peak_contact_force":0.18221,"subtask_id":"pre_grasp","tcp_end":[0.49895,0.0387,0.05475],"tcp_start":[0.50724,0.03938,0.06425],"tcp_to_object_dist_end":0.03202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.49916,0.03861,0.15071],"object_pos_start":[0.51251,0.03924,0.02574],"object_to_goal_dist_end":0.18562,"object_to_goal_dist_start":0.21267,"object_z_max":0.15044,"peak_contact_force":0.12429,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11955.0,"raw_peak_contact_force":0.24575,"subtask_id":"reach_goal","tcp_end":[0.49545,0.0384,0.18507],"tcp_start":[0.49895,0.0387,0.05475],"tcp_to_object_dist_end":0.03456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.54561,0.0737,0.01602],"object_pos_start":[0.49916,0.03861,0.15071],"object_to_goal_dist_end":0.182,"object_to_goal_dist_start":0.18562,"object_z_max":0.1675,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6607.0,"raw_peak_contact_force":1.71993,"subtask_id":"reach_goal","tcp_end":[0.61738,0.16389,0.28031],"tcp_start":[0.49545,0.0384,0.18507],"tcp_to_object_dist_end":0.28833,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.54561,0.0737,0.01602],"object_pos_start":[0.54561,0.0737,0.01602],"object_to_goal_dist_end":0.182,"object_to_goal_dist_start":0.182,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1728.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62224,0.16988,0.16371],"tcp_start":[0.61738,0.16389,0.28031],"tcp_to_object_dist_end":0.19219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,0.0737,0.01602],"object_pos_start":[0.54561,0.0737,0.01602],"object_to_goal_dist_end":0.182,"object_to_goal_dist_start":0.182,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.61581,0.16804,0.18254],"tcp_start":[0.62224,0.16988,0.16371],"tcp_to_object_dist_end":0.20386,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96615,"average_solve_count":384.0,"average_success_count":384.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04088,"descend_to_goal.speed":0.04702,"lift_1.speed":0.02992,"transport_1.speed":0.04154},"optimized_scores":{"best_composite_score":0.18898,"best_fitness_score":0.53898,"best_task_score":0.17635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2998.0,"contact_point_centroid":[0.48394,0.11844,-0.00235],"force_p95":0.12471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64065,"mean_force":0.13818,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53311,0.15479,0.29545]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47942,0.04727,-0.00156],"force_p95":0.22121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24704,"mean_force":0.09507,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46908,0.04724,0.05679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1234.0,"contact_point_centroid":[0.47307,0.04019,0.19115],"force_p95":0.16376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22131,"mean_force":0.09812,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47246,0.05863,0.19604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1459.0,"contact_point_centroid":[0.47053,0.07778,0.19269],"force_p95":0.10817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20634,"mean_force":0.07797,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47307,0.05971,0.19705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4857.0,"contact_point_centroid":[0.46728,0.02842,0.1148],"force_p95":0.13011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20202,"mean_force":0.09166,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46659,0.047,0.11893]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.0487,-0.00209],"force_p95":0.14899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19146,"mean_force":0.12917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47133,0.04748,0.05729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5438.0,"contact_point_centroid":[0.46456,0.06544,0.11408],"force_p95":0.10658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19114,"mean_force":0.08216,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46662,0.047,0.1175]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2895.0,"contact_point_centroid":[0.47058,0.02867,0.052],"force_p95":0.10842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16239,"mean_force":0.07113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47017,0.04736,0.05607]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49115,0.02886,0.23937]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47901,0.04775,0.11645]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.48391,0.11859,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57626,0.22277,0.30925]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48391,0.11859,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57483,0.22468,0.2498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2975.0,"contact_point_centroid":[0.46853,0.0662,0.05274],"force_p95":0.1025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10299,"mean_force":0.06989,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47018,0.04736,0.05607]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3004.0,"contact_point_centroid":[0.53611,0.15949,0.30287],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01041,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53622,0.15962,0.30053]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.57625,0.22511,0.24783],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57665,0.22547,0.24523]},{"body_a":"left_finger","body_b":"right_finger","contact_count":926.0,"contact_point_centroid":[0.5758,0.22247,0.31104],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01036,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57628,0.2228,0.30868]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48391,0.11859,0.01602],"final_tcp_position":[0.5782,0.2261,0.24982],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9749.01592,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48233,0.04759,0.1697],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.47819,0.04815,0.06467],"tcp_start":[0.48233,0.04759,0.1697],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04809,0.02568],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29059,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14698,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7670.0,"raw_peak_contact_force":0.19146,"subtask_id":"pre_grasp","tcp_end":[0.47015,0.04736,0.05604],"tcp_start":[0.47819,0.04815,0.06467],"tcp_to_object_dist_end":0.03287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.46983,0.04744,0.15104],"object_pos_start":[0.48274,0.04809,0.02568],"object_to_goal_dist_end":0.22754,"object_to_goal_dist_start":0.29059,"object_z_max":0.15076,"peak_contact_force":0.12482,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10387.0,"raw_peak_contact_force":0.24704,"subtask_id":"reach_goal","tcp_end":[0.46676,0.04702,0.18636],"tcp_start":[0.47015,0.04736,0.05604],"tcp_to_object_dist_end":0.03545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.48391,0.11859,0.01602],"object_pos_start":[0.46983,0.04744,0.15104],"object_to_goal_dist_end":0.26029,"object_to_goal_dist_start":0.22754,"object_z_max":0.16901,"peak_contact_force":9749.01592,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8695.0,"raw_peak_contact_force":1.64065,"subtask_id":"reach_goal","tcp_end":[0.57515,0.21996,0.36397],"tcp_start":[0.46676,0.04702,0.18636],"tcp_to_object_dist_end":0.37372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.48391,0.11859,0.01602],"object_pos_start":[0.48391,0.11859,0.01602],"object_to_goal_dist_end":0.26029,"object_to_goal_dist_start":0.26029,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1786.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5782,0.2261,0.24982],"tcp_start":[0.57515,0.21996,0.36397],"tcp_to_object_dist_end":0.27407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48391,0.11859,0.01602],"object_pos_start":[0.48391,0.11859,0.01602],"object_to_goal_dist_end":0.26029,"object_to_goal_dist_start":0.26029,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57377,0.2242,0.26977],"tcp_start":[0.5782,0.2261,0.24982],"tcp_to_object_dist_end":0.28917,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31962,"average_solve_count":316.0,"average_success_count":316.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07248,"descend_to_goal.speed":0.04762,"lift_1.speed":0.02868,"transport_1.speed":0.07637},"optimized_scores":{"best_composite_score":0.21899,"best_fitness_score":0.56899,"best_task_score":0.23247},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2110.0,"contact_point_centroid":[0.54597,0.14265,-0.00245],"force_p95":0.18149,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02027,"mean_force":0.15467,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58149,0.15493,0.29933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2968.0,"contact_point_centroid":[0.53215,-0.00094,0.20082],"force_p95":0.1485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37094,"mean_force":0.09984,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5303,0.0173,0.20527]},{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.53366,-0.02006,-0.00159],"force_p95":0.23654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2563,"mean_force":0.10183,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52144,-0.01995,0.05436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3319.0,"contact_point_centroid":[0.53242,0.04004,0.20425],"force_p95":0.1303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23784,"mean_force":0.08984,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53199,0.02211,0.20841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5998.0,"contact_point_centroid":[0.5198,-0.00139,0.11094],"force_p95":0.11548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20904,"mean_force":0.08184,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51892,-0.0199,0.11415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5647.0,"contact_point_centroid":[0.51927,-0.03857,0.11408],"force_p95":0.11285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2071,"mean_force":0.08576,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51891,-0.0199,0.11683]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.0213,-0.00211],"force_p95":0.15231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2011,"mean_force":0.13084,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52395,-0.01998,0.05503]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51319,0.00118,0.23305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3378.0,"contact_point_centroid":[0.52471,-0.0013,0.05091],"force_p95":0.09743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13051,"mean_force":0.0612,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52273,-0.01996,0.05358]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52846,-0.01585,0.11362]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.54561,0.14363,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60527,0.22025,0.2866]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54561,0.14363,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60288,0.22299,0.22593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3017.0,"contact_point_centroid":[0.52381,-0.03892,0.05132],"force_p95":0.10052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10186,"mean_force":0.06967,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52273,-0.01996,0.05358]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2236.0,"contact_point_centroid":[0.58158,0.15577,0.30233],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01574,"mean_force":0.01046,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58187,0.15594,0.30003]},{"body_a":"left_finger","body_b":"right_finger","contact_count":929.0,"contact_point_centroid":[0.60482,0.21992,0.28934],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01024,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60526,0.22023,0.28703]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.60474,0.22359,0.22407],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60492,0.22385,0.2218]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54561,0.14363,0.01602],"final_tcp_position":[0.60663,0.22447,0.22669],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.90745,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52843,-0.01171,0.1651],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.53119,-0.02004,0.06378],"tcp_start":[0.52843,-0.01171,0.1651],"tcp_to_object_dist_end":0.03823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.537,-0.02065,0.02557],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31646,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15091,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8195.0,"raw_peak_contact_force":0.2011,"subtask_id":"pre_grasp","tcp_end":[0.5227,-0.01996,0.05354],"tcp_start":[0.53119,-0.02004,0.06378],"tcp_to_object_dist_end":0.03142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.52385,-0.02021,0.15061],"object_pos_start":[0.537,-0.02065,0.02557],"object_to_goal_dist_end":0.26868,"object_to_goal_dist_start":0.31646,"object_z_max":0.15035,"peak_contact_force":0.10919,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11751.0,"raw_peak_contact_force":0.2563,"subtask_id":"reach_goal","tcp_end":[0.51912,-0.0199,0.18409],"tcp_start":[0.5227,-0.01996,0.05354],"tcp_to_object_dist_end":0.03382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":973.0,"n_steps_budget":1000.0,"object_pos_end":[0.54561,0.14363,0.01602],"object_pos_start":[0.52385,-0.02021,0.15061],"object_to_goal_dist_end":0.21885,"object_to_goal_dist_start":0.26868,"object_z_max":0.19508,"peak_contact_force":9748.82394,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10633.0,"raw_peak_contact_force":2.02027,"subtask_id":"reach_goal","tcp_end":[0.60479,0.21662,0.34183],"tcp_start":[0.51912,-0.0199,0.18409],"tcp_to_object_dist_end":0.33909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.54561,0.14363,0.01602],"object_pos_start":[0.54561,0.14363,0.01602],"object_to_goal_dist_end":0.21885,"object_to_goal_dist_start":0.21885,"object_z_max":0.01602,"peak_contact_force":9748.90745,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1781.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.60663,0.22447,0.22669],"tcp_start":[0.60479,0.21662,0.34183],"tcp_to_object_dist_end":0.23375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,0.14363,0.01602],"object_pos_start":[0.54561,0.14363,0.01602],"object_to_goal_dist_end":0.21885,"object_to_goal_dist_start":0.21885,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.60168,0.22247,0.24562],"tcp_start":[0.60663,0.22447,0.22669],"tcp_to_object_dist_end":0.24916,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```