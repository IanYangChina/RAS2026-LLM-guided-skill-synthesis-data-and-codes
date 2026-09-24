## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0849 | 0.32 | ❌ rejected |
| 3 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3579 | 0.37 | ❌ rejected |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3580 | 0.37 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.085) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
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
  control: position_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  control: admittance_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.085
- **task_score** (E): 0.319
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1179 |
| descend | 1.00 | 1.00 | 0.1440 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 0.67 | 1.00 | 0.0956 |
| transport | 0.00 | 1.00 | 0.0750 |
| place_descend | 0.33 | 1.00 | 0.0548 |
| release | 1.00 | 1.00 | 0.0230 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.187) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 8.240 | 0.138 |
| descend | descend | 1.00 / step_budget | (0.520, 0.005, 0.187)→(0.521, 0.005, 0.043) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.043)→(0.513, 0.005, 0.034) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.134 | 0.174 |
| lift | lift | 0.67 / step_budget | (0.513, 0.005, 0.034)→(0.518, 0.005, 0.129) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.113) | 0.249→0.209 | 1.00 / 39.000 | 0.077 | 0.538 |
| transport | approach | 0.00 / step_budget | (0.518, 0.005, 0.129)→(0.544, 0.058, 0.175) | (0.526, 0.005, 0.113)→(0.549, 0.058, 0.153) | 0.209→0.144 | 1.00 / 29.000 | 0.105 | 0.142 |
| place_descend | descend | 0.33 / step_budget | (0.544, 0.058, 0.175)→(0.567, 0.104, 0.167) | (0.549, 0.058, 0.153)→(0.568, 0.097, 0.094) | 0.144→0.130 | 1.00 / 22.333 | 0.108 | 0.658 |
| release | release | 1.00 / step_budget | (0.567, 0.104, 0.167)→(0.561, 0.103, 0.189) | (0.568, 0.097, 0.094)→(0.569, 0.101, 0.017) | 0.130→0.187 | 1.00 / 3.667 | 0.242 | 1.023 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.532
- phase_score: 0.539
- phase_breakdown.reach_grasp_score: 0.785
- phase_breakdown.place_object_score: 0.433
- grasp_place_fitness: 0.744

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.744
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.532
- **Median Q (composite search score)**: 0.044
- **K-run variance**: 0.0061
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.291


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21512,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.04069,"descend.depth":0.02577,"lift.lift_height":0.1821,"lift.speed":0.06068,"place_descend.place_depth":0.00376,"place_descend.speed":0.05028,"transport.hover_height":0.15556,"transport.speed":0.08961},"optimized_scores":{"best_composite_score":0.04407,"best_fitness_score":0.59407,"best_task_score":0.24604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3139.0,"contact_point_centroid":[0.58195,0.06174,-0.00229],"force_p95":0.12933,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70473,"mean_force":0.13745,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57706,0.06861,0.18375]},{"body_a":"world","body_b":"grasp_target","contact_count":210.0,"contact_point_centroid":[0.54052,0.00058,-0.00115],"force_p95":0.26288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48409,"mean_force":0.07639,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52911,0.00085,0.04021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18419.0,"contact_point_centroid":[0.53149,-0.0183,0.08874],"force_p95":0.07811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30009,"mean_force":0.05445,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53062,0.00078,0.08649]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18581.0,"contact_point_centroid":[0.53144,0.01985,0.08798],"force_p95":0.07743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28465,"mean_force":0.05422,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53059,0.00078,0.0858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13493.0,"contact_point_centroid":[0.55112,0.04259,0.16168],"force_p95":0.10002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23626,"mean_force":0.07013,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54753,0.02376,0.16042]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14365.0,"contact_point_centroid":[0.55036,0.00418,0.16012],"force_p95":0.10753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23448,"mean_force":0.06616,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54692,0.0229,0.15932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":859.0,"contact_point_centroid":[0.56915,0.03165,0.1826],"force_p95":0.19664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23115,"mean_force":0.13105,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56425,0.04968,0.18617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.56971,0.06757,0.18203],"force_p95":0.13668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.169,"mean_force":0.10015,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56435,0.05002,0.18588]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00102,-0.00203],"force_p95":0.13142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1505,"mean_force":0.12525,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53207,0.00091,0.04008]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51668,0.00047,0.24239]},{"body_a":"world","body_b":"grasp_target","contact_count":3756.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53671,0.001,0.10205]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58198,0.06175,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58289,0.08107,0.18569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4118.0,"contact_point_centroid":[0.5315,-0.01831,0.04135],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11978,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53083,0.00089,0.03862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53149,0.01997,0.04046],"force_p95":0.06815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09388,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53084,0.00089,0.03862]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3063.0,"contact_point_centroid":[0.57826,0.06961,0.186],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01061,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57781,0.0696,0.18377]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.58602,0.08154,0.18336],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.0104,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58555,0.08153,0.18139]}],"total_contact_groups":16},"final_pose_error":0.09819,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58198,0.06175,0.01602],"final_tcp_position":[0.58691,0.08167,0.18404],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":24.47509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":24.47509,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp","tcp_end":[0.5363,0.00097,0.18572],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3756.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53909,0.00104,0.04841],"tcp_start":[0.5363,0.00097,0.18572],"tcp_to_object_dist_end":0.02299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00077,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12978,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.1505,"tcp_end":[0.5308,0.00089,0.03858],"tcp_start":[0.53909,0.00104,0.04841],"tcp_to_object_dist_end":0.01846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54094,0.00076,0.11502],"object_pos_start":[0.5442,0.00077,0.02588],"object_to_goal_dist_end":0.20475,"object_to_goal_dist_start":0.25049,"object_z_max":0.11491,"peak_contact_force":0.08182,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37210.0,"raw_peak_contact_force":0.48409,"tcp_end":[0.53468,0.00075,0.13543],"tcp_start":[0.5308,0.00089,0.03858],"tcp_to_object_dist_end":0.02135,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57133,0.04627,0.16265],"object_pos_start":[0.54094,0.00076,0.11502],"object_to_goal_dist_end":0.13832,"object_to_goal_dist_start":0.20475,"object_z_max":0.16258,"peak_contact_force":0.16147,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27858.0,"raw_peak_contact_force":0.23626,"subtask_id":"place_object","tcp_end":[0.56383,0.04637,0.19012],"tcp_start":[0.53468,0.00075,0.13543],"tcp_to_object_dist_end":0.02848,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58198,0.06175,0.01602],"object_pos_start":[0.57133,0.04627,0.16265],"object_to_goal_dist_end":0.21034,"object_to_goal_dist_start":0.13832,"object_z_max":0.16265,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8185.0,"raw_peak_contact_force":1.70473,"subtask_id":"place_object","tcp_end":[0.58691,0.08167,0.18404],"tcp_start":[0.56383,0.04637,0.19012],"tcp_to_object_dist_end":0.16927,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58198,0.06175,0.01602],"object_pos_start":[0.58198,0.06175,0.01602],"object_to_goal_dist_end":0.21034,"object_to_goal_dist_start":0.21034,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58134,0.0808,0.20568],"tcp_start":[0.58691,0.08167,0.18404],"tcp_to_object_dist_end":0.19062,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17413,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.03832,"descend.depth":0.01608,"lift.lift_height":0.13276,"lift.speed":0.05814,"place_descend.place_depth":0.01444,"place_descend.speed":0.09459,"transport.hover_height":0.12742,"transport.speed":0.03002},"optimized_scores":{"best_composite_score":0.19378,"best_fitness_score":0.74378,"best_task_score":0.53169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.58065,0.15901,-0.0064],"force_p95":1.25388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27352,"mean_force":0.41399,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57356,0.14554,0.13775]},{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.52668,0.02902,-0.00118],"force_p95":0.36974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59397,"mean_force":0.08586,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51548,0.02969,0.03146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":951.0,"contact_point_centroid":[0.58242,0.12833,0.12227],"force_p95":0.09425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30379,"mean_force":0.06047,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57803,0.14682,0.12209]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19263.0,"contact_point_centroid":[0.51866,0.04862,0.07783],"force_p95":0.07732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30125,"mean_force":0.05278,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51804,0.02953,0.07597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":886.0,"contact_point_centroid":[0.5816,0.16589,0.12002],"force_p95":0.13752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29713,"mean_force":0.07898,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57775,0.14674,0.12172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18992.0,"contact_point_centroid":[0.51886,0.01043,0.07996],"force_p95":0.07836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29659,"mean_force":0.05291,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51822,0.02953,0.07786]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03056,-0.00209],"force_p95":0.14831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21878,"mean_force":0.12957,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51838,0.02992,0.03112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14929.0,"contact_point_centroid":[0.56452,0.13303,0.13837],"force_p95":0.09207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1428,"mean_force":0.06366,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56149,0.1141,0.13794]},{"body_a":"world","body_b":"grasp_target","contact_count":1728.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51052,0.01332,0.24293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.51777,0.01064,0.03252],"force_p95":0.07898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13615,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51715,0.02984,0.02974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15660.0,"contact_point_centroid":[0.56505,0.09579,0.13881],"force_p95":0.08279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12795,"mean_force":0.0601,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56184,0.11465,0.13781]},{"body_a":"world","body_b":"grasp_target","contact_count":3756.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52341,0.02907,0.09901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20035.0,"contact_point_centroid":[0.53484,0.07706,0.13941],"force_p95":0.07296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08596,"mean_force":0.04933,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53427,0.05793,0.13897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4949.0,"contact_point_centroid":[0.51777,0.04896,0.03155],"force_p95":0.07142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08517,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51715,0.02984,0.02974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20363.0,"contact_point_centroid":[0.53477,0.03875,0.13951],"force_p95":0.07254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07899,"mean_force":0.04832,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53423,0.05785,0.13892]}],"total_contact_groups":15},"final_pose_error":0.03816,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5913,0.15769,0.01623],"final_tcp_position":[0.58,0.14721,0.12538],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.27352,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1728.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp","tcp_end":[0.52379,0.02741,0.1864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3756.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52534,0.03039,0.03904],"tcp_start":[0.52379,0.02741,0.1864],"tcp_to_object_dist_end":0.01401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02981,0.0257],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18435,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14275,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10830.0,"raw_peak_contact_force":0.21878,"tcp_end":[0.51712,0.02983,0.0297],"tcp_start":[0.52534,0.03039,0.03904],"tcp_to_object_dist_end":0.01386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53187,0.02954,0.11037],"object_pos_start":[0.53039,0.02981,0.0257],"object_to_goal_dist_end":0.16453,"object_to_goal_dist_start":0.18435,"object_z_max":0.11027,"peak_contact_force":0.07021,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38476.0,"raw_peak_contact_force":0.59397,"tcp_end":[0.52304,0.02953,0.12321],"tcp_start":[0.51712,0.02983,0.0297],"tcp_to_object_dist_end":0.01558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55156,0.08165,0.13753],"object_pos_start":[0.53187,0.02954,0.11037],"object_to_goal_dist_end":0.11296,"object_to_goal_dist_start":0.16453,"object_z_max":0.13751,"peak_contact_force":0.0705,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40398.0,"raw_peak_contact_force":0.08596,"subtask_id":"place_object","tcp_end":[0.54679,0.08174,0.15634],"tcp_start":[0.52304,0.02953,0.12321],"tcp_to_object_dist_end":0.0194,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58413,0.14723,0.10139],"object_pos_start":[0.55156,0.08165,0.13753],"object_to_goal_dist_end":0.03648,"object_to_goal_dist_start":0.11296,"object_z_max":0.13753,"peak_contact_force":0.11123,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30589.0,"raw_peak_contact_force":0.1428,"subtask_id":"place_object","tcp_end":[0.58,0.14721,0.12538],"tcp_start":[0.54679,0.08174,0.15634],"tcp_to_object_dist_end":0.02435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5913,0.15769,0.01623],"object_pos_start":[0.58413,0.14723,0.10139],"object_to_goal_dist_end":0.09476,"object_to_goal_dist_start":0.03648,"object_z_max":0.10139,"peak_contact_force":0.21295,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2019.0,"raw_peak_contact_force":1.27352,"tcp_end":[0.57347,0.14552,0.14695],"tcp_start":[0.58,0.14721,0.12538],"tcp_to_object_dist_end":0.13248,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09268,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.03225,"descend.depth":0.01502,"lift.lift_height":0.13827,"lift.speed":0.05914,"place_descend.place_depth":0.00081,"place_descend.speed":0.05157,"transport.hover_height":0.06656,"transport.speed":0.04495},"optimized_scores":{"best_composite_score":0.01686,"best_fitness_score":0.56686,"best_task_score":0.18065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.52882,0.07342,-0.00979],"force_p95":1.43782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67315,"mean_force":0.58072,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52899,0.08212,0.2073]},{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.50051,-0.01524,-0.00115],"force_p95":0.3607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53468,"mean_force":0.07931,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4895,-0.0154,0.0349]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18999.0,"contact_point_centroid":[0.49233,0.00381,0.08381],"force_p95":0.07714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30342,"mean_force":0.05299,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49189,-0.01531,0.08169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19669.0,"contact_point_centroid":[0.4923,-0.0344,0.0835],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2807,"mean_force":0.05147,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49189,-0.01531,0.08159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.53694,0.06388,0.18864],"force_p95":0.08835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21448,"mean_force":0.05987,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53254,0.08275,0.1885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":950.0,"contact_point_centroid":[0.53704,0.10171,0.18839],"force_p95":0.09303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18381,"mean_force":0.06036,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53257,0.08276,0.18855]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01555,-0.00203],"force_p95":0.1316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15298,"mean_force":0.12524,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49211,-0.01544,0.03457]},{"body_a":"world","body_b":"grasp_target","contact_count":1492.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49892,-0.00657,0.24514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16015.0,"contact_point_centroid":[0.52973,0.04689,0.18473],"force_p95":0.08267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12575,"mean_force":0.05886,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52619,0.06586,0.18332]},{"body_a":"world","body_b":"grasp_target","contact_count":3152.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49792,-0.01463,0.11069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.49137,0.00378,0.0361],"force_p95":0.07608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11825,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01543,0.03333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16516.0,"contact_point_centroid":[0.52928,0.08392,0.18373],"force_p95":0.0792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11591,"mean_force":0.05762,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52579,0.065,0.18293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16216.0,"contact_point_centroid":[0.50849,-0.00317,0.15408],"force_p95":0.08792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10391,"mean_force":0.05955,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50676,0.01587,0.15252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17783.0,"contact_point_centroid":[0.50861,0.03591,0.15431],"force_p95":0.07947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10239,"mean_force":0.05421,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50722,0.01702,0.15348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4883.0,"contact_point_centroid":[0.49145,-0.0345,0.03518],"force_p95":0.06825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08911,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01543,0.03333]}],"total_contact_groups":15},"final_pose_error":0.13047,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53275,0.08483,0.01917],"final_tcp_position":[0.53419,0.08295,0.19128],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.67315,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1492.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp","tcp_end":[0.49988,-0.01372,0.18897],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":788.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3152.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49888,-0.01553,0.0418],"tcp_start":[0.49988,-0.01372,0.18897],"tcp_to_object_dist_end":0.01654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01529,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31212,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12963,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10796.0,"raw_peak_contact_force":0.15298,"tcp_end":[0.49091,-0.01543,0.0333],"tcp_start":[0.49888,-0.01553,0.0418],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50508,-0.01507,0.11389],"object_pos_start":[0.5037,-0.01529,0.02588],"object_to_goal_dist_end":0.25637,"object_to_goal_dist_start":0.31212,"object_z_max":0.11379,"peak_contact_force":0.07966,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38851.0,"raw_peak_contact_force":0.53468,"tcp_end":[0.49654,-0.01525,0.12926],"tcp_start":[0.49091,-0.01543,0.0333],"tcp_to_object_dist_end":0.01758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52414,0.04524,0.15751],"object_pos_start":[0.50508,-0.01507,0.11389],"object_to_goal_dist_end":0.17992,"object_to_goal_dist_start":0.25637,"object_z_max":0.15745,"peak_contact_force":0.08424,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33999.0,"raw_peak_contact_force":0.10391,"subtask_id":"place_object","tcp_end":[0.51993,0.04541,0.179],"tcp_start":[0.49654,-0.01525,0.12926],"tcp_to_object_dist_end":0.0219,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53879,0.08289,0.16489],"object_pos_start":[0.52414,0.04524,0.15751],"object_to_goal_dist_end":0.14204,"object_to_goal_dist_start":0.17992,"object_z_max":0.16488,"peak_contact_force":0.09129,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32531.0,"raw_peak_contact_force":0.12575,"subtask_id":"place_object","tcp_end":[0.53419,0.08295,0.19128],"tcp_start":[0.51993,0.04541,0.179],"tcp_to_object_dist_end":0.02678,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53275,0.08483,0.01917],"object_pos_start":[0.53879,0.08289,0.16489],"object_to_goal_dist_end":0.25668,"object_to_goal_dist_start":0.14204,"object_z_max":0.16489,"peak_contact_force":0.38904,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2084.0,"raw_peak_contact_force":1.67315,"tcp_end":[0.52892,0.08212,0.21478],"tcp_start":[0.53419,0.08295,0.19128],"tcp_to_object_dist_end":0.19567,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```