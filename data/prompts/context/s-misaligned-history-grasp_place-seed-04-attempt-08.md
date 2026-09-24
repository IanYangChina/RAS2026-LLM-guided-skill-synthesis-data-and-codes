## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6  | 0.0580 | 0.20 | ❌ rejected |
| 7 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.0580 | 0.20 | ❌ rejected |
| 6 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.0580 | 0.20 | ❌ rejected |
| 5 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.0580 | 0.20 | ❌ rejected |
| 4 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | -0.0288 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
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
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
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

## Current Skill (Q=-0.029) — your mutation base

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

- **Composite score**: -0.029
- **task_score** (E): 0.203
- **fitness_score**: 0.278  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.2150 |
| descend | 1.00 | 1.00 | 0.0030 |
| grasp | 1.00 | 1.00 | 0.0127 |
| lift | 1.00 | 1.00 | 0.0788 |
| approach_goal | 0.00 | 1.00 | 0.0980 |
| descend_place | 1.00 | 1.00 | 0.0976 |
| release | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.088) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.520, 0.005, 0.088)→(0.519, 0.005, 0.085) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 153.350 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.519, 0.005, 0.085)→(0.511, 0.005, 0.076) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 0.123 | 0.123 |
| lift | lift | 1.00 / step_budget | (0.511, 0.005, 0.076)→(0.521, 0.005, 0.154) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 6499.351 | 0.123 |
| approach_goal | approach | 0.00 / step_budget | (0.521, 0.005, 0.154)→(0.560, 0.084, 0.194) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 6499.271 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.560, 0.084, 0.194)→(0.600, 0.161, 0.178) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.600, 0.161, 0.178)→(0.594, 0.159, 0.199) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.295
- phase_score: 0.692
- phase_breakdown.reach_object_score: 0.385
- phase_breakdown.reach_goal_score: 0.824
- grasp_place_fitness: 0.327

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.327
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.295
- **Median Q (composite search score)**: -0.037
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: approach_obj.approach_height
- **Final σ (mean)**: 0.296


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
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85185,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_height":0.05281,"approach_obj.approach_height":0.05,"descend.grasp_force_threshold":6.05297,"descend.grasp_z_offset":-0.00341,"descend_place.place_z_offset":0.01441,"lift.lift_height":0.1175},"optimized_scores":{"best_composite_score":-0.0365,"best_fitness_score":0.27064,"best_task_score":0.18872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12901,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51732,0.00048,0.19242]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53711,0.00098,0.08671]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53009,0.00084,0.07763]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53223,0.00089,0.10297]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55934,0.03581,0.15091]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60299,0.10141,0.17728]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62186,0.13175,0.18882]},{"body_a":"left_finger","body_b":"right_finger","contact_count":342.0,"contact_point_centroid":[0.5296,0.00082,0.07851],"force_p95":0.0136,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01107,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52889,0.00082,0.07611]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4283.0,"contact_point_centroid":[0.55958,0.03577,0.15326],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01041,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55933,0.03579,0.15089]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4282.0,"contact_point_centroid":[0.60292,0.10128,0.17966],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60298,0.10139,0.17727]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2176.0,"contact_point_centroid":[0.53256,0.00089,0.10494],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01038,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53221,0.00089,0.10288]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.62449,0.13229,0.18708],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.00998,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62449,0.1324,0.18513]}],"total_contact_groups":12},"final_pose_error":0.03786,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54431,0.00113,0.02602],"final_tcp_position":[0.62581,0.13259,0.18798],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.67718,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":699.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2792.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53711,0.00098,0.08671],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":297.76597,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53701,0.00098,0.08647],"tcp_start":[0.53711,0.00098,0.08671],"tcp_to_object_dist_end":0.06089,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2142.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52889,0.00082,0.07611],"tcp_start":[0.53701,0.00098,0.08647],"tcp_to_object_dist_end":0.05241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":506.0,"n_steps_budget":600.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4200.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53899,0.00103,0.13246],"tcp_start":[0.52889,0.00082,0.07611],"tcp_to_object_dist_end":0.10657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":9748.67718,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8283.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57953,0.06494,0.17092],"tcp_start":[0.53899,0.00103,0.13246],"tcp_to_object_dist_end":0.1622,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8282.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62581,0.13259,0.18798],"tcp_start":[0.57953,0.06494,0.17092],"tcp_to_object_dist_end":0.22395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62034,0.13137,0.20842],"tcp_start":[0.62581,0.13259,0.18798],"tcp_to_object_dist_end":0.23667,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83621,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_height":0.08959,"approach_obj.approach_height":0.05008,"descend.grasp_force_threshold":7.04342,"descend.grasp_z_offset":0.00767,"descend_place.place_z_offset":0.00185,"lift.lift_height":0.13995},"optimized_scores":{"best_composite_score":0.01961,"best_fitness_score":0.32675,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2740.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51088,0.01419,0.19281]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.5234,0.02872,0.08525]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51589,0.0283,0.07453]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51831,0.02919,0.11201]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54741,0.07988,0.16204]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58047,0.14704,0.13695]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58921,0.17107,0.10878]},{"body_a":"left_finger","body_b":"right_finger","contact_count":347.0,"contact_point_centroid":[0.51531,0.02822,0.07531],"force_p95":0.01431,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01094,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5147,0.02822,0.07307]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4298.0,"contact_point_centroid":[0.54779,0.07996,0.16449],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01038,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54746,0.07999,0.16207]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1648.0,"contact_point_centroid":[0.58058,0.14684,0.13936],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01058,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58043,0.14696,0.13705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2240.0,"contact_point_centroid":[0.51878,0.02918,0.11427],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01023,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51828,0.02919,0.11184]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.59257,0.1719,0.10695],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59237,0.17205,0.10459]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5305,0.03079,0.02602],"final_tcp_position":[0.59417,0.17234,0.10758],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.95992,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2740.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52415,0.02866,0.08741],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52274,0.02873,0.08295],"tcp_start":[0.52415,0.02866,0.08741],"tcp_to_object_dist_end":0.0575,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2147.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5147,0.02822,0.07307],"tcp_start":[0.52274,0.02873,0.08295],"tcp_to_object_dist_end":0.0497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":9748.95992,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52545,0.03036,0.15336],"tcp_start":[0.5147,0.02822,0.07307],"tcp_to_object_dist_end":0.12744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8298.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56821,0.12041,0.17338],"tcp_start":[0.52545,0.03036,0.15336],"tcp_to_object_dist_end":0.17655,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3216.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59417,0.17234,0.10758],"tcp_start":[0.56821,0.12041,0.17338],"tcp_to_object_dist_end":0.17533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58731,0.17049,0.1287],"tcp_start":[0.59417,0.17234,0.10758],"tcp_to_object_dist_end":0.18244,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.872,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_height":0.10025,"approach_obj.approach_height":0.05179,"descend.grasp_force_threshold":3.68849,"descend.grasp_z_offset":-0.00117,"descend_place.place_z_offset":5e-05,"lift.lift_height":0.16104},"optimized_scores":{"best_composite_score":-0.06954,"best_fitness_score":0.23761,"best_task_score":0.12474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.49851,-0.0072,0.19503]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4985,-0.01467,0.08872]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49123,-0.01464,0.07885]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49286,-0.01509,0.12521]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51471,0.02751,0.20635]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55603,0.12559,0.23652]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57615,0.17574,0.24138]},{"body_a":"left_finger","body_b":"right_finger","contact_count":338.0,"contact_point_centroid":[0.4908,-0.01463,0.07947],"force_p95":0.01459,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01122,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49007,-0.01463,0.0775]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4329.0,"contact_point_centroid":[0.55605,0.12556,0.23896],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01031,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55606,0.12567,0.23652]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2736.0,"contact_point_centroid":[0.4935,-0.01509,0.12733],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01033,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49285,-0.01509,0.12507]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4336.0,"contact_point_centroid":[0.51502,0.02755,0.20873],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.0103,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51473,0.02755,0.20638]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57802,0.1763,0.23932],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01087,"mean_force":0.00989,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57824,0.17649,0.23712]}],"total_contact_groups":12},"final_pose_error":0.01563,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50382,-0.01567,0.02602],"final_tcp_position":[0.57938,0.17662,0.23977],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9749.01249,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49923,-0.01462,0.09056],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":68.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49793,-0.01469,0.08665],"tcp_start":[0.49923,-0.01462,0.09056],"tcp_to_object_dist_end":0.06092,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2138.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49007,-0.01463,0.0775],"tcp_start":[0.49793,-0.01469,0.08665],"tcp_to_object_dist_end":0.0533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":9748.96925,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5268.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49934,-0.01557,0.17508],"tcp_start":[0.49007,-0.01463,0.0775],"tcp_to_object_dist_end":0.14912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":9749.01249,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8336.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53122,0.06534,0.23813],"tcp_start":[0.49934,-0.01557,0.17508],"tcp_to_object_dist_end":0.2287,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8329.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57938,0.17662,0.23977],"tcp_start":[0.53122,0.06534,0.23813],"tcp_to_object_dist_end":0.29728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57497,0.17531,0.26135],"tcp_start":[0.57938,0.17662,0.23977],"tcp_to_object_dist_end":0.31132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```