## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → push → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0495 | 0.27 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3628 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=0.049) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
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
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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

- **Composite score**: 0.049
- **task_score** (E): 0.271
- **fitness_score**: 0.419  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0643 |
| descend_1 | 1.00 | 1.00 | 0.1836 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.2791 |
| transport_1 | 1.00 | 1.00 | 0.2416 |
| release_1 | 1.00 | 1.00 | 0.0210 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.247) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.014, 0.247)→(0.509, -0.016, 0.064) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.509, -0.016, 0.064)→(0.501, -0.016, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.024) | 0.270→0.270 | 1.00 / 26.000 | 0.217 | 0.227 |
| lift_1 | lift | 1.00 / step_budget | (0.501, -0.016, 0.054)→(0.512, -0.016, 0.333) | (0.515, -0.016, 0.024)→(0.518, -0.018, 0.124) | 0.270→0.289 | 1.00 / 18.000 | 3249.708 | 0.363 |
| transport_1 | push | 1.00 / step_budget | (0.512, -0.016, 0.333)→(0.607, 0.166, 0.220) | (0.518, -0.018, 0.124)→(0.562, 0.031, 0.068) | 0.289→0.203 | 1.00 / 17.333 | 237989.064 | 0.127 |
| release_1 | release | 1.00 / step_budget | (0.607, 0.166, 0.220)→(0.602, 0.165, 0.240) | (0.562, 0.031, 0.068)→(0.557, 0.029, 0.026) | 0.203→0.226 | 1.00 / 3.333 | 0.144 | 0.609 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.519
- phase_score: 0.108
- phase_breakdown.placement_score: 0.203
- phase_breakdown.approach_target_score: 0.077
- phase_breakdown.lift_clearance_score: 0.014
- grasp_place_fitness: 0.726

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.726
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.519
- **Median Q (composite search score)**: -0.090
- **K-run variance**: 0.0470
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.415


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49327,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05029,"grasp_1.grip_force":14.86486,"lift_1.lift_height":0.17264,"lift_1.speed":0.05692,"transport_1.transport_speed":0.08546},"optimized_scores":{"best_composite_score":-0.11686,"best_fitness_score":0.25314,"best_task_score":0.11967},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3706.0,"contact_point_centroid":[0.53568,-0.02219,-0.00202],"force_p95":0.1567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35895,"mean_force":0.12559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52677,-0.02005,0.19799]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53711,-0.02152,-0.00225],"force_p95":0.23214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2608,"mean_force":0.14275,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52381,-0.02052,0.06077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":541.0,"contact_point_centroid":[0.52189,-0.03421,0.0585],"force_p95":0.15916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25468,"mean_force":0.08677,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52101,-0.02045,0.06413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.52804,-0.00558,0.05411],"force_p95":0.21534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24763,"mean_force":0.16356,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5213,-0.02047,0.06202]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.52394,-0.00223,0.05353],"force_p95":0.15581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17362,"mean_force":0.09404,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5226,-0.0205,0.05931]},{"body_a":"world","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.53702,-0.02132,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5143,-0.00889,0.27593]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5281,-0.01909,0.14371]},{"body_a":"world","body_b":"grasp_target","contact_count":2444.0,"contact_point_centroid":[0.53566,-0.02312,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56786,0.09531,0.28779]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53566,-0.02312,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59939,0.20929,0.2546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2812.0,"contact_point_centroid":[0.52203,-0.03832,0.05419],"force_p95":0.11181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11777,"mean_force":0.0688,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5226,-0.0205,0.05931]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3449.0,"contact_point_centroid":[0.52801,-0.02,0.21792],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01559,"mean_force":0.01047,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5277,-0.02001,0.21562]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2622.0,"contact_point_centroid":[0.56757,0.09476,0.29018],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01039,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56771,0.09484,0.28792]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.60093,0.20995,0.25313],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00999,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60128,0.21023,0.25077]}],"total_contact_groups":13},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53566,-0.02312,0.02602],"final_tcp_position":[0.6026,0.20995,0.25396],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273008.70218,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":532.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_target","tcp_end":[0.52739,-0.01709,0.24681],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12264,"subtask_id":"approach_target","tcp_end":[0.53076,-0.02063,0.06923],"tcp_start":[0.52739,-0.01709,0.24681],"tcp_to_object_dist_end":0.04367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53734,-0.01973,0.02365],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.26134,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6744.0,"raw_peak_contact_force":0.2608,"subtask_id":"lift_clearance","tcp_end":[0.52257,-0.0205,0.05928],"tcp_start":[0.53076,-0.02063,0.06923],"tcp_to_object_dist_end":0.03857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.53566,-0.02312,0.02602],"object_pos_start":[0.53734,-0.01973,0.02365],"object_to_goal_dist_end":0.31846,"object_to_goal_dist_start":0.31677,"object_z_max":0.033,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7841.0,"raw_peak_contact_force":0.35895,"subtask_id":"lift_clearance","tcp_end":[0.53454,-0.01972,0.32653],"tcp_start":[0.52257,-0.0205,0.05928],"tcp_to_object_dist_end":0.30053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.53566,-0.02312,0.02602],"object_pos_start":[0.53566,-0.02312,0.02602],"object_to_goal_dist_end":0.31846,"object_to_goal_dist_start":0.31846,"object_z_max":0.02602,"peak_contact_force":273008.70218,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5066.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement","tcp_end":[0.6026,0.20995,0.25396],"tcp_start":[0.53454,-0.01972,0.32653],"tcp_to_object_dist_end":0.3328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53566,-0.02312,0.02602],"object_pos_start":[0.53566,-0.02312,0.02602],"object_to_goal_dist_end":0.31846,"object_to_goal_dist_start":0.31846,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement","tcp_end":[0.59833,0.20878,0.27425],"tcp_start":[0.6026,0.20995,0.25396],"tcp_to_object_dist_end":0.34544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17761,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05005,"grasp_1.grip_force":14.22483,"lift_1.lift_height":0.20561,"lift_1.speed":0.05061,"transport_1.transport_speed":0.05155},"optimized_scores":{"best_composite_score":-0.09031,"best_fitness_score":0.27969,"best_task_score":0.17587},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54616,-0.02918,-0.00203],"force_p95":0.12374,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34812,"mean_force":0.12337,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53417,-0.02766,0.19423]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54572,-0.02937,-0.00247],"force_p95":0.25937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26428,"mean_force":0.15703,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53207,-0.02806,0.06145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1601.0,"contact_point_centroid":[0.53408,-0.01079,0.05332],"force_p95":0.1552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18051,"mean_force":0.09333,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,-0.02803,0.05996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2026.0,"contact_point_centroid":[0.53165,-0.04551,0.05424],"force_p95":0.13444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1632,"mean_force":0.07874,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,-0.02803,0.05996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.53607,-0.03949,0.05309],"force_p95":0.13754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15544,"mean_force":0.05545,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53009,-0.02802,0.0604]},{"body_a":"world","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.5456,-0.02923,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12345,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51781,-0.01217,0.27538]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5359,-0.02623,0.14278]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.54615,-0.02918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.58095,0.05949,0.27708]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54615,-0.02918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61852,0.14752,0.22771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":45.0,"contact_point_centroid":[0.53759,-0.01744,0.05196],"force_p95":0.11331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12101,"mean_force":0.05371,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53038,-0.02803,0.06]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3794.0,"contact_point_centroid":[0.53516,-0.02761,0.21329],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.0104,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53494,-0.02763,0.21094]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2310.0,"contact_point_centroid":[0.58068,0.05948,0.27941],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01028,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.58098,0.05955,0.27705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.6206,0.14816,0.22618],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00993,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62067,0.14829,0.22382]}],"total_contact_groups":13},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54615,-0.02918,0.02602],"final_tcp_position":[0.62228,0.14798,0.22744],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273006.75949,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":596.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_target","tcp_end":[0.53452,-0.02358,0.24533],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12264,"subtask_id":"approach_target","tcp_end":[0.53906,-0.02824,0.07016],"tcp_start":[0.53452,-0.02358,0.24533],"tcp_to_object_dist_end":0.04464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54582,-0.0274,0.02307],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26122,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.2603,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5427.0,"raw_peak_contact_force":0.26428,"subtask_id":"lift_clearance","tcp_end":[0.53083,-0.02804,0.05992],"tcp_start":[0.53906,-0.02824,0.07016],"tcp_to_object_dist_end":0.03979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54615,-0.02918,0.02602],"object_pos_start":[0.54582,-0.0274,0.02307],"object_to_goal_dist_end":0.2607,"object_to_goal_dist_start":0.26122,"object_z_max":0.02612,"peak_contact_force":9748.92455,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7910.0,"raw_peak_contact_force":0.34812,"subtask_id":"lift_clearance","tcp_end":[0.54178,-0.02741,0.33059],"tcp_start":[0.53083,-0.02804,0.05992],"tcp_to_object_dist_end":0.30461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.54615,-0.02918,0.02602],"object_pos_start":[0.54615,-0.02918,0.02602],"object_to_goal_dist_end":0.2607,"object_to_goal_dist_start":0.2607,"object_z_max":0.02602,"peak_contact_force":273006.75949,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4438.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement","tcp_end":[0.62228,0.14798,0.22744],"tcp_start":[0.54178,-0.02741,0.33059],"tcp_to_object_dist_end":0.27884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54615,-0.02918,0.02602],"object_pos_start":[0.54615,-0.02918,0.02602],"object_to_goal_dist_end":0.2607,"object_to_goal_dist_start":0.2607,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement","tcp_end":[0.61726,0.14712,0.24735],"tcp_start":[0.62228,0.14798,0.22744],"tcp_to_object_dist_end":0.29176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17219,"average_solve_count":302.0,"average_success_count":302.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05055,"grasp_1.grip_force":7.31178,"lift_1.lift_height":0.18718,"lift_1.speed":0.04765,"transport_1.transport_speed":0.02939},"optimized_scores":{"best_composite_score":0.35566,"best_fitness_score":0.72566,"best_task_score":0.51857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.58445,0.13654,-0.00681],"force_p95":1.20246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58237,"mean_force":0.3605,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58965,0.13939,0.18773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.59198,0.15944,0.17493],"force_p95":0.08664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40115,"mean_force":0.05429,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59347,0.14048,0.17336]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.46006,-0.00033,-0.00137],"force_p95":0.37382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38188,"mean_force":0.1347,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4497,-0.00029,0.04484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":993.0,"contact_point_centroid":[0.59907,0.12227,0.17175],"force_p95":0.08752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35463,"mean_force":0.05645,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59345,0.14048,0.17332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":22236.0,"contact_point_centroid":[0.45319,0.01881,0.18997],"force_p95":0.06891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24231,"mean_force":0.04685,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45312,-0.00035,0.18746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20751.0,"contact_point_centroid":[0.45306,-0.01957,0.19289],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24059,"mean_force":0.04974,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45326,-0.00035,0.19058]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00015,-0.00202],"force_p95":0.13062,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1563,"mean_force":0.12496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45171,-0.00025,0.04493]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.46286,-7e-05,-0.00173],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12369,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48315,-4e-05,0.27705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10820.0,"contact_point_centroid":[0.52698,0.0478,0.26249],"force_p95":0.09877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13439,"mean_force":0.05988,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52388,0.06658,0.26208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11321.0,"contact_point_centroid":[0.52476,0.08698,0.26197],"force_p95":0.09396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13334,"mean_force":0.05669,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52524,0.06799,0.26045]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46199,-0.00012,0.14528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4612.0,"contact_point_centroid":[0.45097,-0.01955,0.04681],"force_p95":0.06913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08572,"mean_force":0.04717,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00026,0.0438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5605.0,"contact_point_centroid":[0.45092,0.0189,0.04634],"force_p95":0.061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07717,"mean_force":0.03945,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00026,0.0438]}],"total_contact_groups":13},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58948,0.13889,0.0269],"final_tcp_position":[0.59551,0.14057,0.17734],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12249,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_target","tcp_end":[0.46853,-7e-05,0.24924],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12264,"subtask_id":"approach_target","tcp_end":[0.4585,-0.00014,0.05161],"tcp_start":[0.46853,-7e-05,0.24924],"tcp_to_object_dist_end":0.02596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46276,-0.00037,0.02589],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2334,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12961,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12017.0,"raw_peak_contact_force":0.1563,"subtask_id":"lift_clearance","tcp_end":[0.45052,-0.00027,0.04377],"tcp_start":[0.4585,-0.00014,0.05161],"tcp_to_object_dist_end":0.02167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47131,-0.00025,0.32093],"object_pos_start":[0.46276,-0.00037,0.02589],"object_to_goal_dist_end":0.28674,"object_to_goal_dist_start":0.2334,"object_z_max":0.32063,"peak_contact_force":0.07819,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":43063.0,"raw_peak_contact_force":0.38188,"subtask_id":"lift_clearance","tcp_end":[0.46025,-0.00038,0.34252],"tcp_start":[0.45052,-0.00027,0.04377],"tcp_to_object_dist_end":0.02427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.60335,0.14383,0.15137],"object_pos_start":[0.47131,-0.00025,0.32093],"object_to_goal_dist_end":0.03129,"object_to_goal_dist_start":0.28674,"object_z_max":0.32125,"peak_contact_force":167951.73011,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22141.0,"raw_peak_contact_force":0.13439,"subtask_id":"placement","tcp_end":[0.59551,0.14057,0.17734],"tcp_start":[0.46025,-0.00038,0.34252],"tcp_to_object_dist_end":0.02733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58948,0.13889,0.0269],"object_pos_start":[0.60335,0.14383,0.15137],"object_to_goal_dist_end":0.0985,"object_to_goal_dist_start":0.03129,"object_z_max":0.15137,"peak_contact_force":0.18529,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2223.0,"raw_peak_contact_force":1.58237,"subtask_id":"placement","tcp_end":[0.58957,0.13938,0.1981],"tcp_start":[0.59551,0.14057,0.17734],"tcp_to_object_dist_end":0.1712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```