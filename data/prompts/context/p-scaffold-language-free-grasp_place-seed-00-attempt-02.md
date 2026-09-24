## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2706 | 0.17 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2702 | 0.17 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2701 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=0.271) — your mutation base

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
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
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
- id: release_1
  type: release
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.271
- **task_score** (E): 0.170
- **fitness_score**: 0.561  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2194 |
| descend_1 | 1.00 | 1.00 | 0.0424 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1267 |
| release_1 | 1.00 | 1.00 | 0.0257 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.005, 0.084) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.005, 0.084)→(0.492, 0.001, 0.042) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.042)→(0.484, 0.001, 0.034) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 42.667 | 0.142 | 0.178 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.034)→(0.492, 0.000, 0.160) | (0.497, 0.001, 0.026)→(0.503, 0.000, 0.146) | 0.266→0.213 | 1.00 / 37.000 | 0.080 | 0.587 |
| release_1 | release | 1.00 / step_budget | (0.492, 0.000, 0.160)→(0.487, 0.000, 0.185) | (0.503, 0.000, 0.146)→(0.489, 0.001, 0.027) | 0.213→0.267 | 1.00 / 2.000 | 0.186 | 1.454 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.196
- phase_score: 0.245
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.descend_1_score: 0.834
- phase_breakdown.approach_1_score: 0.195
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.013
- grasp_place_fitness: 0.573

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.573
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.196
- **Median Q (composite search score)**: 0.271
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.287


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61224,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.064,"descend_1.depth":0.05262,"grasp_1.grip_force":19.47768,"lift_1.lift_height":0.14283},"optimized_scores":{"best_composite_score":0.27121,"best_fitness_score":0.56121,"best_task_score":0.17062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":187.0,"contact_point_centroid":[0.50097,-0.02364,-0.00703],"force_p95":1.21094,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53348,"mean_force":0.38148,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50347,-0.02267,0.17021]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.51101,-0.02239,-0.00112],"force_p95":0.40382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61386,"mean_force":0.07818,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4987,-0.02244,0.03431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13541.0,"contact_point_centroid":[0.50245,-0.04178,0.0956],"force_p95":0.08047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31843,"mean_force":0.058,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50229,-0.02259,0.09281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16311.0,"contact_point_centroid":[0.50359,-0.00361,0.09368],"force_p95":0.07493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31828,"mean_force":0.04965,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5022,-0.02259,0.0919]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02308,-0.00205],"force_p95":0.1386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17001,"mean_force":0.1266,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50123,-0.02248,0.03391]},{"body_a":"world","body_b":"grasp_target","contact_count":2936.0,"contact_point_centroid":[0.5137,-0.02302,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50314,0.00489,0.18263]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.50813,-0.042,0.15691],"force_p95":0.07824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12424,"mean_force":0.04904,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50748,-0.02276,0.15418]},{"body_a":"world","body_b":"grasp_target","contact_count":2644.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50704,-0.02083,0.04979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5268.0,"contact_point_centroid":[0.50094,-0.0034,0.03438],"force_p95":0.0683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11112,"mean_force":0.04154,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49997,-0.02246,0.03255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.50951,-0.00377,0.15573],"force_p95":0.07426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10316,"mean_force":0.04338,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50751,-0.02276,0.15422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4167.0,"contact_point_centroid":[0.49922,-0.04172,0.03535],"force_p95":0.08,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09149,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49997,-0.02246,0.03255]}],"total_contact_groups":11},"final_pose_error":0.01313,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.50535,-0.02218,0.02766],"final_tcp_position":[0.50903,-0.0228,0.15634],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.53348,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2936.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50839,-0.0173,0.07023],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5083,-0.02261,0.04165],"tcp_start":[0.50839,-0.0173,0.07023],"tcp_to_object_dist_end":0.01654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51358,-0.02291,0.02582],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.2657,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13846,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11235.0,"raw_peak_contact_force":0.17001,"tcp_end":[0.49994,-0.02246,0.03252],"tcp_start":[0.5083,-0.02261,0.04165],"tcp_to_object_dist_end":0.0152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.5197,-0.02342,0.14337],"object_pos_start":[0.51358,-0.02291,0.02582],"object_to_goal_dist_end":0.19497,"object_to_goal_dist_start":0.2657,"object_z_max":0.14326,"peak_contact_force":0.07966,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29994.0,"raw_peak_contact_force":0.61386,"tcp_end":[0.50903,-0.0228,0.15634],"tcp_start":[0.49994,-0.02246,0.03252],"tcp_to_object_dist_end":0.01681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50535,-0.02218,0.02766],"object_pos_start":[0.5197,-0.02342,0.14337],"object_to_goal_dist_end":0.26525,"object_to_goal_dist_start":0.19497,"object_z_max":0.14341,"peak_contact_force":0.18611,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2470.0,"raw_peak_contact_force":1.53348,"tcp_end":[0.50337,-0.02266,0.18103],"tcp_start":[0.50903,-0.0228,0.15634],"tcp_to_object_dist_end":0.15339,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82222,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10276,"descend_1.depth":0.01056,"grasp_1.grip_force":20.01689,"lift_1.lift_height":0.13997},"optimized_scores":{"best_composite_score":0.28303,"best_fitness_score":0.57303,"best_task_score":0.19559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.48781,0.04391,-0.0066],"force_p95":1.16593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32578,"mean_force":0.3585,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4911,0.04358,0.16744]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.49853,0.04318,-0.00116],"force_p95":0.36989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58667,"mean_force":0.07441,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48655,0.04374,0.03564]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12801.0,"contact_point_centroid":[0.49012,0.06299,0.09534],"force_p95":0.08492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32874,"mean_force":0.05888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4901,0.04379,0.09257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15804.0,"contact_point_centroid":[0.49187,0.02486,0.09342],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30272,"mean_force":0.04923,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49002,0.04378,0.09181]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04503,-0.00209],"force_p95":0.15042,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19776,"mean_force":0.12985,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48903,0.04399,0.03508]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.48956,0.02487,0.03512],"force_p95":0.07517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17432,"mean_force":0.04316,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48779,0.04388,0.03377]},{"body_a":"world","body_b":"grasp_target","contact_count":2456.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49741,0.03327,0.20939]},{"body_a":"world","body_b":"grasp_target","contact_count":3060.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49497,0.04512,0.06747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.49767,0.02505,0.15282],"force_p95":0.07755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11241,"mean_force":0.04355,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4951,0.04397,0.15146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1057.0,"contact_point_centroid":[0.49514,0.06321,0.15426],"force_p95":0.08076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10819,"mean_force":0.04923,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49507,0.04397,0.15143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4194.0,"contact_point_centroid":[0.48781,0.06317,0.03636],"force_p95":0.08647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09495,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4878,0.04388,0.03378]}],"total_contact_groups":11},"final_pose_error":0.01296,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49271,0.04336,0.02777],"final_tcp_position":[0.4966,0.0441,0.1535],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.32578,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49697,0.04626,0.1115],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3060.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49601,0.04462,0.04257],"tcp_start":[0.49697,0.04626,0.1115],"tcp_to_object_dist_end":0.01735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04448,0.02566],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24254,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14925,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11030.0,"raw_peak_contact_force":0.19776,"tcp_end":[0.48777,0.04387,0.03374],"tcp_start":[0.49601,0.04462,0.04257],"tcp_to_object_dist_end":0.01564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50709,0.04497,0.13945],"object_pos_start":[0.50115,0.04448,0.02566],"object_to_goal_dist_end":0.20808,"object_to_goal_dist_start":0.24254,"object_z_max":0.13934,"peak_contact_force":0.08073,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28748.0,"raw_peak_contact_force":0.58667,"tcp_end":[0.4966,0.0441,0.1535],"tcp_start":[0.48777,0.04387,0.03374],"tcp_to_object_dist_end":0.01755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49271,0.04336,0.02777],"object_pos_start":[0.50709,0.04497,0.13945],"object_to_goal_dist_end":0.24476,"object_to_goal_dist_start":0.20808,"object_z_max":0.13949,"peak_contact_force":0.17726,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2480.0,"raw_peak_contact_force":1.32578,"tcp_end":[0.49099,0.04357,0.17853],"tcp_start":[0.4966,0.0441,0.1535],"tcp_to_object_dist_end":0.15077,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06364,"descend_1.depth":0.04768,"grasp_1.grip_force":23.10922,"lift_1.lift_height":0.15588},"optimized_scores":{"best_composite_score":0.25747,"best_fitness_score":0.54747,"best_task_score":0.1442},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.46455,-0.02141,-0.00786],"force_p95":1.28974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50262,"mean_force":0.43113,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.46662,-0.01979,0.18532]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.47376,-0.01914,-0.0011],"force_p95":0.3338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56015,"mean_force":0.06466,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46186,-0.0196,0.03624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17754.0,"contact_point_centroid":[0.46659,-0.00071,0.10208],"force_p95":0.07316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30243,"mean_force":0.04889,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46524,-0.01973,0.10027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15273.0,"contact_point_centroid":[0.46538,-0.03892,0.10307],"force_p95":0.07935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29737,"mean_force":0.05541,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46524,-0.01973,0.10035]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.0202,-0.00204],"force_p95":0.13731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16706,"mean_force":0.12607,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46427,-0.01964,0.03559]},{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48536,0.00635,0.1838]},{"body_a":"world","body_b":"grasp_target","contact_count":2256.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47055,-0.01806,0.05033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.47112,-0.03913,0.17067],"force_p95":0.07855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12104,"mean_force":0.04883,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47032,-0.01987,0.16807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5073.0,"contact_point_centroid":[0.46429,-0.00054,0.03593],"force_p95":0.06835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10797,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46307,-0.01962,0.03439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.47236,-0.00089,0.16959],"force_p95":0.07321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10005,"mean_force":0.04342,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47037,-0.01988,0.16811]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4340.0,"contact_point_centroid":[0.46254,-0.03887,0.03707],"force_p95":0.07765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08921,"mean_force":0.04983,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46307,-0.01962,0.03439]}],"total_contact_groups":11},"final_pose_error":0.01249,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47007,-0.01889,0.02682],"final_tcp_position":[0.47179,-0.01991,0.16998],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.50262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2840.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4729,-0.01435,0.07109],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.04556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47107,-0.01975,0.04239],"tcp_start":[0.4729,-0.01435,0.07109],"tcp_to_object_dist_end":0.01715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.02001,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28846,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13728,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11213.0,"raw_peak_contact_force":0.16706,"tcp_end":[0.46304,-0.01962,0.03436],"tcp_start":[0.47107,-0.01975,0.04239],"tcp_to_object_dist_end":0.01556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.48179,-0.02049,0.15476],"object_pos_start":[0.47605,-0.02001,0.02584],"object_to_goal_dist_end":0.23647,"object_to_goal_dist_start":0.28846,"object_z_max":0.15465,"peak_contact_force":0.07951,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33161.0,"raw_peak_contact_force":0.56015,"tcp_end":[0.47179,-0.01991,0.16998],"tcp_start":[0.46304,-0.01962,0.03436],"tcp_to_object_dist_end":0.01822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47007,-0.01889,0.02682],"object_pos_start":[0.48179,-0.02049,0.15476],"object_to_goal_dist_end":0.29048,"object_to_goal_dist_start":0.23647,"object_z_max":0.1548,"peak_contact_force":0.19442,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2451.0,"raw_peak_contact_force":1.50262,"tcp_end":[0.46652,-0.01979,0.19568],"tcp_start":[0.47179,-0.01991,0.16998],"tcp_to_object_dist_end":0.1689,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```