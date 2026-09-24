## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.4118 | 0.17 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.4799 | 0.15 | ❌ rejected |
| 11 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 10 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

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

## Current Skill (Q=-0.221) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: -0.221
- **task_score** (E): 0.190
- **fitness_score**: 0.199  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.420

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| descend_1 | 1.00 | 0.2466 |
| insert_1 | 0.67 | 0.1618 |
| grasp_1 | 1.00 | 0.0145 |
| approach_1 | 1.00 | 0.1217 |
| align_1 | 1.00 | 0.1533 |
| retract_1 | 1.00 | 0.0968 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.021, 0.058) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 |
| insert_1 | insert | 0.67 / step_budget | (0.506, 0.021, 0.058)→(0.577, 0.161, 0.084) | (0.511, 0.022, 0.026)→(0.513, 0.054, 0.019) | 0.273→0.256 |
| grasp_1 | grasp | 1.00 / step_budget | (0.577, 0.161, 0.084)→(0.569, 0.160, 0.072) | (0.513, 0.054, 0.019)→(0.513, 0.054, 0.019) | 0.256→0.256 |
| approach_1 | approach | 1.00 / step_budget | (0.569, 0.160, 0.072)→(0.512, 0.061, 0.110) | (0.513, 0.054, 0.019)→(0.513, 0.054, 0.019) | 0.256→0.256 |
| align_1 | align | 1.00 / step_budget | (0.512, 0.061, 0.110)→(0.590, 0.190, 0.093) | (0.513, 0.054, 0.019)→(0.513, 0.054, 0.019) | 0.256→0.256 |
| retract_1 | retract | 1.00 / step_budget | (0.590, 0.190, 0.093)→(0.602, 0.208, 0.181) | (0.513, 0.054, 0.019)→(0.513, 0.054, 0.019) | 0.256→0.256 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.276
- phase_score: 0.240
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.approach_1_score: 0.155
- phase_breakdown.descend_1_score: 0.820
- grasp_place_fitness: 0.248

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.248
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.276
- **Median Q (composite search score)**: -0.237
- **K-run variance**: 0.0013
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90116,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00451,"align_1.lateral_offset_y":0.00247,"approach_1.speed":0.07076,"insert_1.insertion_depth":0.08245,"insert_1.insertion_force":10.36409,"retract_1.retract_height":0.09299},"optimized_scores":{"best_composite_score":-0.17151,"best_fitness_score":0.24849,"best_task_score":0.27599},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3317.0,"contact_point_centroid":[0.51277,0.06833,-0.00238],"force_p95":0.35503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5548,"mean_force":0.14823,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.54485,0.11036,0.07075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":616.0,"contact_point_centroid":[0.53309,0.03281,0.05309],"force_p95":0.08261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22945,"mean_force":0.03881,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5222,0.07136,0.06097]},{"body_a":"world","body_b":"grasp_target","contact_count":3044.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50242,0.01843,0.1781]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51218,0.08688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.57599,0.17484,0.07628]},{"body_a":"world","body_b":"grasp_target","contact_count":2564.0,"contact_point_centroid":[0.51218,0.08688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5409,0.13208,0.08798]},{"body_a":"world","body_b":"grasp_target","contact_count":3132.0,"contact_point_centroid":[0.51218,0.08688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.55051,0.1432,0.09737]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.51218,0.08688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60449,0.18231,0.11015]},{"body_a":"left_finger","body_b":"right_finger","contact_count":337.0,"contact_point_centroid":[0.57496,0.17431,0.07676],"force_p95":0.01396,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.57477,0.17448,0.0744]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2203.0,"contact_point_centroid":[0.60455,0.18211,0.11254],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01039,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60448,0.18231,0.11014]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2763.0,"contact_point_centroid":[0.54115,0.13174,0.09049],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01035,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54071,0.13182,0.0881]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3393.0,"contact_point_centroid":[0.55076,0.14304,0.09983],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.0103,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.55046,0.14315,0.09737]}],"total_contact_groups":11},"final_pose_error":0.01389,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51218,0.08688,0.01602],"final_tcp_position":[0.62075,0.17278,0.13292],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":762.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50714,0.0372,0.05798],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0325,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51218,0.08688,0.01602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.19311,"object_to_goal_dist_start":0.21222,"object_z_max":0.02771,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.58268,0.17655,0.08665],"tcp_start":[0.50714,0.0372,0.05798],"tcp_to_object_dist_end":0.13416,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51218,0.08688,0.01602],"object_pos_start":[0.51218,0.08688,0.01602],"object_to_goal_dist_end":0.19311,"object_to_goal_dist_start":0.19311,"object_z_max":0.01602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.57477,0.17448,0.0744],"tcp_start":[0.58268,0.17655,0.08665],"tcp_to_object_dist_end":0.12247,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.51218,0.08688,0.01602],"object_pos_start":[0.51218,0.08688,0.01602],"object_to_goal_dist_end":0.19311,"object_to_goal_dist_start":0.19311,"object_z_max":0.01602,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.51188,0.09173,0.10737],"tcp_start":[0.57477,0.17448,0.0744],"tcp_to_object_dist_end":0.09148,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.51218,0.08688,0.01602],"object_pos_start":[0.51218,0.08688,0.01602],"object_to_goal_dist_end":0.19311,"object_to_goal_dist_start":0.19311,"object_z_max":0.01602,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.59119,0.19343,0.09247],"tcp_start":[0.51188,0.09173,0.10737],"tcp_to_object_dist_end":0.15311,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51218,0.08688,0.01602],"object_pos_start":[0.51218,0.08688,0.01602],"object_to_goal_dist_end":0.19311,"object_to_goal_dist_start":0.19311,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62075,0.17278,0.13292],"tcp_start":[0.59119,0.19343,0.09247],"tcp_to_object_dist_end":0.1812,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81373,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00044,"align_1.lateral_offset_y":-0.00155,"approach_1.speed":0.06627,"insert_1.insertion_depth":0.07639,"insert_1.insertion_force":5.81521,"retract_1.retract_height":0.10903},"optimized_scores":{"best_composite_score":-0.25482,"best_fitness_score":0.16518,"best_task_score":0.14704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3693.0,"contact_point_centroid":[0.4859,0.05156,-0.0021],"force_p95":0.25854,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44865,"mean_force":0.13224,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52633,0.11076,0.07027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":418.0,"contact_point_centroid":[0.50984,0.03959,0.05367],"force_p95":0.11555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3433,"mean_force":0.05534,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50018,0.07781,0.06181]},{"body_a":"world","body_b":"grasp_target","contact_count":2996.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48849,0.02259,0.17848]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48663,0.05049,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5672,0.16965,0.07515]},{"body_a":"world","body_b":"grasp_target","contact_count":3436.0,"contact_point_centroid":[0.48663,0.05049,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52423,0.11233,0.09234]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48663,0.05049,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53522,0.12213,0.10337]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.48663,0.05049,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58041,0.20594,0.15288]},{"body_a":"left_finger","body_b":"right_finger","contact_count":332.0,"contact_point_centroid":[0.56619,0.16915,0.07561],"force_p95":0.0143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01138,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56599,0.1693,0.07332]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3470.0,"contact_point_centroid":[0.58044,0.20575,0.1554],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01045,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5804,0.20597,0.15299]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3697.0,"contact_point_centroid":[0.52453,0.11211,0.0948],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01037,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52413,0.11217,0.09241]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4330.0,"contact_point_centroid":[0.5354,0.12175,0.1058],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01031,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53497,0.12182,0.10341]}],"total_contact_groups":11},"final_pose_error":0.01475,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48663,0.05049,0.02602],"final_tcp_position":[0.57891,0.2257,0.21638],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.47914,0.04563,0.0586],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03292,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48663,0.05049,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28756,"object_to_goal_dist_start":0.28998,"object_z_max":0.02701,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.57386,0.17133,0.08523],"tcp_start":[0.47914,0.04563,0.0586],"tcp_to_object_dist_end":0.16037,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48663,0.05049,0.02602],"object_pos_start":[0.48663,0.05049,0.02602],"object_to_goal_dist_end":0.28756,"object_to_goal_dist_start":0.28756,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.56598,0.1693,0.07331],"tcp_start":[0.57386,0.17133,0.08523],"tcp_to_object_dist_end":0.1505,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.48663,0.05049,0.02602],"object_pos_start":[0.48663,0.05049,0.02602],"object_to_goal_dist_end":0.28756,"object_to_goal_dist_start":0.28756,"object_z_max":0.02602,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.48657,0.05615,0.11784],"tcp_start":[0.56598,0.1693,0.07331],"tcp_to_object_dist_end":0.092,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48663,0.05049,0.02602],"object_pos_start":[0.48663,0.05049,0.02602],"object_to_goal_dist_end":0.28756,"object_to_goal_dist_start":0.28756,"object_z_max":0.02602,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.58612,0.18668,0.09378],"tcp_start":[0.48657,0.05615,0.11784],"tcp_to_object_dist_end":0.18177,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.48663,0.05049,0.02602],"object_pos_start":[0.48663,0.05049,0.02602],"object_to_goal_dist_end":0.28756,"object_to_goal_dist_start":0.28756,"object_z_max":0.02602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.57891,0.2257,0.21638],"tcp_start":[0.58612,0.18668,0.09378],"tcp_to_object_dist_end":0.27469,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65714,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00215,"align_1.lateral_offset_y":0.00238,"approach_1.speed":0.04149,"insert_1.insertion_depth":0.09645,"insert_1.insertion_force":10.81546,"retract_1.retract_height":0.10612},"optimized_scores":{"best_composite_score":-0.23708,"best_fitness_score":0.18292,"best_task_score":0.14756},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3538.0,"contact_point_centroid":[0.53942,0.01101,-0.00243],"force_p95":0.38523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59313,"mean_force":0.1517,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.55195,0.06249,0.06693]},{"body_a":"world","body_b":"grasp_target","contact_count":3120.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51394,-0.01001,0.17735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1815.0,"contact_point_centroid":[0.5373,-0.02448,0.05261],"force_p95":0.06721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13366,"mean_force":0.03244,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53673,0.01547,0.05791]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54029,0.02564,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56859,0.1352,0.07062]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54029,0.02564,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55004,0.08258,0.08482]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54029,0.02564,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.56331,0.11282,0.09626]},{"body_a":"world","body_b":"grasp_target","contact_count":2772.0,"contact_point_centroid":[0.54029,0.02564,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.597,0.20651,0.14043]},{"body_a":"left_finger","body_b":"right_finger","contact_count":337.0,"contact_point_centroid":[0.56766,0.13481,0.07117],"force_p95":0.0143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56735,0.13491,0.06882]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2948.0,"contact_point_centroid":[0.59696,0.20631,0.14294],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01048,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59702,0.20655,0.14055]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4293.0,"contact_point_centroid":[0.55041,0.08253,0.08721],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01039,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55004,0.08258,0.08482]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4304.0,"contact_point_centroid":[0.56351,0.11254,0.09869],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01037,"phase_index":4.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.56325,0.11263,0.09627]}],"total_contact_groups":11},"final_pose_error":0.01552,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54029,0.02564,0.01602],"final_tcp_position":[0.60589,0.22441,0.19291],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.53023,-0.02014,0.05705],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03179,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54029,0.02564,0.01602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.28703,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.5754,0.13651,0.08051],"tcp_start":[0.53023,-0.02014,0.05705],"tcp_to_object_dist_end":0.13298,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54029,0.02564,0.01602],"object_pos_start":[0.54029,0.02564,0.01602],"object_to_goal_dist_end":0.28703,"object_to_goal_dist_start":0.28703,"object_z_max":0.01602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.56734,0.13491,0.06881],"tcp_start":[0.5754,0.13651,0.08051],"tcp_to_object_dist_end":0.12433,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54029,0.02564,0.01602],"object_pos_start":[0.54029,0.02564,0.01602],"object_to_goal_dist_end":0.28703,"object_to_goal_dist_start":0.28703,"object_z_max":0.01602,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.53806,0.03465,0.10563],"tcp_start":[0.56734,0.13491,0.06881],"tcp_to_object_dist_end":0.09009,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54029,0.02564,0.01602],"object_pos_start":[0.54029,0.02564,0.01602],"object_to_goal_dist_end":0.28703,"object_to_goal_dist_start":0.28703,"object_z_max":0.01602,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.59184,0.18906,0.09243],"tcp_start":[0.53806,0.03465,0.10563],"tcp_to_object_dist_end":0.18762,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54029,0.02564,0.01602],"object_pos_start":[0.54029,0.02564,0.01602],"object_to_goal_dist_end":0.28703,"object_to_goal_dist_start":0.28703,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.60589,0.22441,0.19291],"tcp_start":[0.59184,0.18906,0.09243],"tcp_to_object_dist_end":0.27405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```