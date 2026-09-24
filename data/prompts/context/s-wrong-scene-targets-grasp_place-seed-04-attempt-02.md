## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1730 | 0.18 | ❌ rejected |
| 1 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 0 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5443056105572368, 0.0011327552814361583, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5443056105572368, 0.0011327552814361583, 0.03]
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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
| `object` | offset from object initial position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.173
- **task_score** (E): 0.183
- **fitness_score**: 0.182  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.095
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1520 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.1209 |
| approach_goal_1 | 0.00 | 1.00 | 0.0597 |
| descend_1 | 0.67 | 1.00 | 0.0007 |
| release_1 | 1.00 | 1.00 | 0.0245 |
| retract_1 | 0.00 | 1.00 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.445, 0.008, 0.162) | (0.526, 0.005, 0.030)→(0.494, 0.008, 0.020) | 0.246→0.263 | 1.00 / 4.667 | 302.647 | 1428.757 |
| grasp_1 | grasp | 1.00 / step_budget | (0.445, 0.008, 0.161)→(0.445, 0.008, 0.161) | (0.494, 0.008, 0.020)→(0.496, 0.009, 0.019) | 0.263→0.263 | 1.00 / 10.000 | 91046.816 | 144.746 |
| lift_1 | lift | 0.67 / step_budget | (0.445, 0.008, 0.161)→(0.500, -0.004, 0.262) | (0.496, 0.009, 0.019)→(0.497, 0.009, 0.019) | 0.263→0.263 | 1.00 / 8.333 | 94257.807 | 155.814 |
| approach_goal_1 | approach | 0.00 / step_budget | (0.500, -0.004, 0.262)→(0.525, 0.033, 0.279) | (0.497, 0.009, 0.019)→(0.497, 0.009, 0.019) | 0.263→0.263 | 1.00 / 8.667 | 143.864 | 343.685 |
| descend_1 | descend | 0.67 / force_exceeded | (0.525, 0.033, 0.279)→(0.525, 0.033, 0.279) | (0.497, 0.009, 0.019)→(0.497, 0.009, 0.019) | 0.263→0.263 | 1.00 / 9.000 | 91034.950 | 146.261 |
| release_1 | release | 1.00 / step_budget | (0.525, 0.033, 0.279)→(0.527, 0.036, 0.303) | (0.497, 0.009, 0.019)→(0.497, 0.009, 0.019) | 0.263→0.263 | 1.00 / 4.667 | 104.016 | 137.631 |
| retract_1 | retract | 0.00 / step_budget | (0.527, 0.036, 0.303)→(0.527, 0.036, 0.304) | (0.497, 0.009, 0.019)→(0.497, 0.009, 0.019) | 0.263→0.263 | 1.00 / 4.667 | 101.868 | 102.743 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.268
- phase_score: 0.189
- phase_breakdown.lift_clearance_score: 0.307
- phase_breakdown.reach_pre_grasp_score: 0.261
- phase_breakdown.reach_goal_score: 0.090
- grasp_place_fitness: 0.222

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.222
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.268
- **Median Q (composite search score)**: -0.155
- **K-run variance**: 0.0064
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 4.7
- **Parameters at lower bound**: approach_1.approach_speed
- **Final σ (mean)**: 0.406


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.64762,0.15808,0.1911]},{"name":"goal","value":[0.54431,0.00113,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":99.0,"average_failure_rate":0.68276,"average_mean_iterations":139.42069,"average_solve_count":145.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13296,"approach_goal_1.goal_approach_speed":0.28569,"descend_1.descent_force":11.77122,"lift_1.lift_height":0.24018,"lift_1.lift_speed":0.1546,"retract_1.retract_speed":0.1585},"optimized_scores":{"best_composite_score":-0.27883,"best_fitness_score":0.17117,"best_task_score":0.16054},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.54411,0.00339,-0.00341],"force_p95":220.06855,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1364.36358,"mean_force":68.09019,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.394,2e-05,0.04467]},{"body_a":"world","body_b":"link6","contact_count":774.0,"contact_point_centroid":[0.65973,0.00055,-0.00042],"force_p95":507.39902,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1341.69893,"mean_force":223.90026,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4322,0.00034,0.14258]},{"body_a":"link5","body_b":"hand","contact_count":368.0,"contact_point_centroid":[0.53146,0.07119,0.16358],"force_p95":161.50011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.30674,"mean_force":111.39724,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49579,-0.03376,0.18815]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.68418,0.00074,-0.0001],"force_p95":188.86162,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.03708,"mean_force":137.412,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46421,-0.00126,0.16167]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68409,0.0008,-0.00013],"force_p95":79.70378,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.24524,"mean_force":68.74056,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46421,-0.00126,0.16173]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.53381,0.05337,0.21578],"force_p95":48.49234,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.49234,"mean_force":48.49234,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.52625,-0.04895,0.23699]},{"body_a":"grasp_target","body_b":"link7","contact_count":203.0,"contact_point_centroid":[0.52173,-0.00068,0.0328],"force_p95":3.62536,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.45609,"mean_force":0.73569,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40697,0.00014,0.09219]},{"body_a":"grasp_target","body_b":"hand","contact_count":135.0,"contact_point_centroid":[0.50759,-0.00378,0.04638],"force_p95":2.11693,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.20754,"mean_force":0.89936,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40369,0.00011,0.08064]},{"body_a":"world","body_b":"grasp_target","contact_count":3311.0,"contact_point_centroid":[0.51422,0.00077,-0.00242],"force_p95":0.37077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16689,"mean_force":0.1639,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44506,0.00037,0.15606]},{"body_a":"grasp_target","body_b":"link6","contact_count":107.0,"contact_point_centroid":[0.55389,0.00444,0.02057],"force_p95":0.61845,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.83879,"mean_force":0.29804,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40107,0.00011,0.08175]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50689,0.00052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46421,-0.00126,0.16173]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.50689,0.00052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49491,-0.03306,0.18674]},{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.50689,0.00052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.53042,-0.05333,0.25197]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.50689,0.00052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53478,-0.05278,0.27113]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50689,0.00052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53431,-0.05291,0.27532]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.50689,0.00052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53433,-0.05321,0.29587]}],"total_contact_groups":21},"final_pose_error":0.24389,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50689,0.00052,0.01602],"final_tcp_position":[0.53447,-0.05325,0.29621],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273024.47705,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,0.00052,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27439,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":236.83871,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4554.0,"raw_peak_contact_force":1364.36358,"subtask_id":"reach_pre_grasp","tcp_end":[0.46419,-0.00111,0.16193],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15204,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50689,0.00052,0.01602],"object_pos_start":[0.50689,0.00052,0.01602],"object_to_goal_dist_end":0.27439,"object_to_goal_dist_start":0.27439,"object_z_max":0.01602,"peak_contact_force":273004.12067,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3525.0,"raw_peak_contact_force":109.24524,"subtask_id":"reach_pre_grasp","tcp_end":[0.4642,-0.00129,0.16163],"tcp_start":[0.4642,-0.00128,0.16163],"tcp_to_object_dist_end":0.15175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50689,0.00052,0.01602],"object_pos_start":[0.50689,0.00052,0.01602],"object_to_goal_dist_end":0.27439,"object_to_goal_dist_start":0.27439,"object_z_max":0.01602,"peak_contact_force":273024.47705,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4451.0,"raw_peak_contact_force":236.30674,"subtask_id":"lift_clearance","tcp_end":[0.52625,-0.04895,0.23699],"tcp_start":[0.4642,-0.00129,0.16163],"tcp_to_object_dist_end":0.22726,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":62.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,0.00052,0.01602],"object_pos_start":[0.50689,0.00052,0.01602],"object_to_goal_dist_end":0.27439,"object_to_goal_dist_start":0.27439,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":522.0,"raw_peak_contact_force":48.49234,"subtask_id":"reach_goal","tcp_end":[0.53475,-0.0529,0.27091],"tcp_start":[0.52625,-0.04895,0.23699],"tcp_to_object_dist_end":0.26191,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,0.00052,0.01602],"object_pos_start":[0.50689,0.00052,0.01602],"object_to_goal_dist_end":0.27439,"object_to_goal_dist_start":0.27439,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53493,-0.05242,0.27175],"tcp_start":[0.53475,-0.0529,0.27091],"tcp_to_object_dist_end":0.26266,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50689,0.00052,0.01602],"object_pos_start":[0.50689,0.00052,0.01602],"object_to_goal_dist_end":0.27439,"object_to_goal_dist_start":0.27439,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53431,-0.05319,0.29576],"tcp_start":[0.53493,-0.05242,0.27175],"tcp_to_object_dist_end":0.28617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":960.0,"object_pos_end":[0.50689,0.00052,0.01602],"object_pos_start":[0.50689,0.00052,0.01602],"object_to_goal_dist_end":0.27439,"object_to_goal_dist_start":0.27439,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53447,-0.05325,0.29621],"tcp_start":[0.53431,-0.05319,0.29576],"tcp_to_object_dist_end":0.28663,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":32.0,"average_failure_rate":0.39506,"average_mean_iterations":83.66667,"average_solve_count":81.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.39418,"approach_goal_1.goal_approach_speed":0.29138,"descend_1.descent_force":6.72774,"lift_1.lift_height":0.26646,"lift_1.lift_speed":0.18243,"retract_1.retract_speed":0.18348},"optimized_scores":{"best_composite_score":-0.08531,"best_fitness_score":0.22184,"best_task_score":0.26776},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":868.0,"contact_point_centroid":[0.6474,0.01448,-0.00043],"force_p95":520.86708,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1490.27704,"mean_force":248.1129,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42829,0.01299,0.15678]},{"body_a":"link5","body_b":"hand","contact_count":47.0,"contact_point_centroid":[0.54226,0.00561,0.22421],"force_p95":684.96822,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":731.38458,"mean_force":543.41171,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.50382,0.08485,0.22188]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.54018,0.00891,0.21407],"force_p95":438.53729,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":438.53729,"mean_force":438.53729,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50948,0.09103,0.22561]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53995,0.01021,0.21527],"force_p95":394.56555,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":412.64907,"mean_force":328.81346,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51181,0.09276,0.23176]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53776,0.00964,-0.00364],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":387.46022,"mean_force":17.61183,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38529,0.00475,0.04707]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.5432,0.01456,0.23528],"force_p95":303.92868,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.9849,"mean_force":267.42272,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51344,0.09646,0.25126]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.6777,0.02802,-0.00013],"force_p95":73.05587,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.08401,"mean_force":69.17617,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46421,0.03182,0.17004]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.6778,0.02802,-0.0001],"force_p95":137.54242,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.97629,"mean_force":107.15849,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46421,0.03183,0.16996]},{"body_a":"grasp_target","body_b":"link7","contact_count":156.0,"contact_point_centroid":[0.50665,0.01661,0.03486],"force_p95":4.06454,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.54399,"mean_force":0.81512,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39718,0.0053,0.08914]},{"body_a":"grasp_target","body_b":"hand","contact_count":136.0,"contact_point_centroid":[0.49932,0.02819,0.04967],"force_p95":2.50361,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.51525,"mean_force":0.82876,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39609,0.00521,0.08566]},{"body_a":"world","body_b":"grasp_target","contact_count":3655.0,"contact_point_centroid":[0.49899,0.04054,-0.00237],"force_p95":0.38241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.50161,"mean_force":0.16522,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44063,0.01282,0.16811]},{"body_a":"grasp_target","body_b":"link6","contact_count":51.0,"contact_point_centroid":[0.54312,0.03099,0.0124],"force_p95":0.71583,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86877,"mean_force":0.44314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38845,0.00493,0.0704]},{"body_a":"left_finger","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.50527,0.0556,0.25214],"force_p95":0.59857,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.59877,"mean_force":0.59672,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51344,0.09646,0.25126]},{"body_a":"left_finger","body_b":"link5","contact_count":56.0,"contact_point_centroid":[0.50423,0.05445,0.24432],"force_p95":0.56554,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.58344,"mean_force":0.5062,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51276,0.09504,0.24284]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49164,0.04252,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46421,0.03182,0.17004]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.49164,0.04252,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47533,0.03969,0.20815]}],"total_contact_groups":25},"final_pose_error":0.12052,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49164,0.04252,0.01602],"final_tcp_position":[0.51343,0.09662,0.25136],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.82008,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49164,0.04252,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":481.24796,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4888.0,"raw_peak_contact_force":1490.27704,"subtask_id":"reach_pre_grasp","tcp_end":[0.46441,0.03183,0.17169],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1584,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49164,0.04252,0.01602],"object_pos_start":[0.49164,0.04252,0.01602],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.19765,"object_z_max":0.01602,"peak_contact_force":67.55954,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3519.0,"raw_peak_contact_force":240.08401,"subtask_id":"reach_pre_grasp","tcp_end":[0.4642,0.03182,0.16992],"tcp_start":[0.4642,0.03182,0.16992],"tcp_to_object_dist_end":0.1567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":479.0,"n_steps_budget":600.0,"object_pos_end":[0.49164,0.04252,0.01602],"object_pos_start":[0.49164,0.04252,0.01602],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.19765,"object_z_max":0.01602,"peak_contact_force":9748.82008,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":141.97629,"subtask_id":"lift_clearance","tcp_end":[0.48804,0.05421,0.24639],"tcp_start":[0.4642,0.03182,0.16992],"tcp_to_object_dist_end":0.23069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":137.0,"n_steps_budget":1000.0,"object_pos_end":[0.49164,0.04252,0.01602],"object_pos_start":[0.49164,0.04252,0.01602],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.19765,"object_z_max":0.01602,"peak_contact_force":431.34786,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1198.0,"raw_peak_contact_force":731.38458,"subtask_id":"reach_goal","tcp_end":[0.50948,0.09103,0.22561],"tcp_start":[0.48804,0.05421,0.24639],"tcp_to_object_dist_end":0.21587,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49164,0.04252,0.01602],"object_pos_start":[0.49164,0.04252,0.01602],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.19765,"object_z_max":0.01602,"peak_contact_force":438.53729,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":438.53729,"subtask_id":"reach_goal","tcp_end":[0.50984,0.09111,0.22611],"tcp_start":[0.50948,0.09103,0.22561],"tcp_to_object_dist_end":0.2164,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49164,0.04252,0.01602],"object_pos_start":[0.49164,0.04252,0.01602],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.19765,"object_z_max":0.01602,"peak_contact_force":311.80401,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1283.0,"raw_peak_contact_force":412.64907,"subtask_id":"reach_goal","tcp_end":[0.51343,0.09644,0.25115],"tcp_start":[0.50984,0.09111,0.22611],"tcp_to_object_dist_end":0.24222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.49164,0.04252,0.01602],"object_pos_start":[0.49164,0.04252,0.01602],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.19765,"object_z_max":0.01602,"peak_contact_force":305.35842,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":12.0,"raw_peak_contact_force":307.9849,"subtask_id":"reach_goal","tcp_end":[0.51343,0.09662,0.25136],"tcp_start":[0.51343,0.09644,0.25115],"tcp_to_object_dist_end":0.24246,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":45.0,"average_failure_rate":0.38462,"average_mean_iterations":81.00855,"average_solve_count":117.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05,"approach_goal_1.goal_approach_speed":0.1114,"descend_1.descent_force":6.60071,"lift_1.lift_height":0.31375,"lift_1.lift_speed":0.20547,"retract_1.retract_speed":0.12887},"optimized_scores":{"best_composite_score":-0.15481,"best_fitness_score":0.15234,"best_task_score":0.12165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63848,-0.00397,-0.00046],"force_p95":198.06231,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1431.63062,"mean_force":198.89557,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39737,-0.00384,0.12223]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53144,0.00104,-0.0032],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.48754,"mean_force":16.71685,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37901,-0.00253,0.04869]},{"body_a":"link5","body_b":"hand","contact_count":354.0,"contact_point_centroid":[0.55401,0.07847,0.26123],"force_p95":200.43692,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.17876,"mean_force":124.2999,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.5157,-0.02491,0.28866]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.63435,-0.00563,-0.0001],"force_p95":67.78116,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.15854,"mean_force":15.46793,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40766,-0.00595,0.15214]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63421,-0.00558,-0.00013],"force_p95":78.06797,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.90917,"mean_force":71.41366,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40754,-0.00591,0.15209]},{"body_a":"grasp_target","body_b":"link7","contact_count":890.0,"contact_point_centroid":[0.49494,-0.01522,0.04633],"force_p95":0.74695,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.2072,"mean_force":0.25879,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39738,-0.00382,0.12138]},{"body_a":"grasp_target","body_b":"hand","contact_count":534.0,"contact_point_centroid":[0.48987,-0.01884,0.05655],"force_p95":1.31557,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.36517,"mean_force":0.36619,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39375,-0.00309,0.10782]},{"body_a":"world","body_b":"grasp_target","contact_count":2226.0,"contact_point_centroid":[0.48543,-0.01743,-0.00402],"force_p95":0.39136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36505,"mean_force":0.27576,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41734,-0.00336,0.13746]},{"body_a":"world","body_b":"grasp_target","contact_count":1742.0,"contact_point_centroid":[0.48814,-0.01732,-0.00253],"force_p95":0.26613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26909,"mean_force":0.15819,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40757,-0.00591,0.15205]},{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.49153,-0.01609,-0.00199],"force_p95":0.12716,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18213,"mean_force":0.12264,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44609,-0.0113,0.23971]},{"body_a":"world","body_b":"grasp_target","contact_count":2872.0,"contact_point_centroid":[0.49152,-0.01609,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.51978,-0.00756,0.30298]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49152,-0.01609,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53102,0.06044,0.33971]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49152,-0.01609,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53221,0.06418,0.34299]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.49152,-0.01609,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53283,0.06379,0.36322]},{"body_a":"grasp_target","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.50063,-0.00976,0.05885],"force_p95":0.09456,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11981,"mean_force":0.07491,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40754,-0.00591,0.15209]},{"body_a":"grasp_target","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.50599,-0.00994,0.05677],"force_p95":0.05346,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.05963,"mean_force":0.01926,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40781,-0.00599,0.15259]}],"total_contact_groups":21},"final_pose_error":0.13951,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49152,-0.01609,0.02602],"final_tcp_position":[0.53279,0.06364,0.3634],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":272666.19016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48494,-0.01788,0.02803],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31779,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":189.85319,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4560.0,"raw_peak_contact_force":1431.63062,"subtask_id":"reach_pre_grasp","tcp_end":[0.40714,-0.00586,0.15254],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14731,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.48926,-0.01703,0.02571],"object_pos_start":[0.48494,-0.01788,0.02803],"object_to_goal_dist_end":0.3175,"object_to_goal_dist_start":0.31779,"object_z_max":0.02803,"peak_contact_force":68.76819,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3590.0,"raw_peak_contact_force":84.90917,"subtask_id":"reach_pre_grasp","tcp_end":[0.40761,-0.00594,0.15195],"tcp_start":[0.40761,-0.00593,0.15195],"tcp_to_object_dist_end":0.15074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":547.0,"n_steps_budget":660.0,"object_pos_end":[0.49152,-0.01609,0.02602],"object_pos_start":[0.4895,-0.01688,0.02572],"object_to_goal_dist_end":0.316,"object_to_goal_dist_start":0.31733,"object_z_max":0.02604,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4517.0,"raw_peak_contact_force":89.15854,"subtask_id":"lift_clearance","tcp_end":[0.48569,-0.01678,0.30347],"tcp_start":[0.40761,-0.00594,0.15195],"tcp_to_object_dist_end":0.27752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.49152,-0.01609,0.02602],"object_pos_start":[0.49152,-0.01609,0.02602],"object_to_goal_dist_end":0.316,"object_to_goal_dist_start":0.316,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6406.0,"raw_peak_contact_force":251.17876,"subtask_id":"reach_goal","tcp_end":[0.53102,0.06044,0.33971],"tcp_start":[0.48569,-0.01678,0.30347],"tcp_to_object_dist_end":0.3253,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49152,-0.01609,0.02602],"object_pos_start":[0.49152,-0.01609,0.02602],"object_to_goal_dist_end":0.316,"object_to_goal_dist_start":0.316,"object_z_max":0.02602,"peak_contact_force":272666.19016,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53114,0.06091,0.33981],"tcp_start":[0.53102,0.06044,0.33971],"tcp_to_object_dist_end":0.32552,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49152,-0.01609,0.02602],"object_pos_start":[0.49152,-0.01609,0.02602],"object_to_goal_dist_end":0.316,"object_to_goal_dist_start":0.316,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1030.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53285,0.06378,0.36313],"tcp_start":[0.53114,0.06091,0.33981],"tcp_to_object_dist_end":0.3489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":690.0,"object_pos_end":[0.49152,-0.01609,0.02602],"object_pos_start":[0.49152,-0.01609,0.02602],"object_to_goal_dist_end":0.316,"object_to_goal_dist_start":0.316,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53279,0.06364,0.3634],"tcp_start":[0.53285,0.06378,0.36313],"tcp_to_object_dist_end":0.34913,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```