## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=0.270) — your mutation base

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

- **Composite score**: 0.270
- **task_score** (E): 0.170
- **fitness_score**: 0.560  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1809 |
| descend_1 | 1.00 | 1.00 | 0.0808 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1318 |
| release_1 | 1.00 | 1.00 | 0.0257 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.005, 0.123) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.005, 0.123)→(0.492, 0.001, 0.043) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.043)→(0.484, 0.001, 0.034) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.667 | 0.141 | 0.179 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.034)→(0.493, 0.000, 0.165) | (0.497, 0.000, 0.026)→(0.503, 0.000, 0.151) | 0.266→0.212 | 1.00 / 37.000 | 0.080 | 0.581 |
| release_1 | release | 1.00 / step_budget | (0.493, 0.000, 0.165)→(0.487, 0.000, 0.191) | (0.503, 0.000, 0.151)→(0.489, 0.001, 0.027) | 0.212→0.267 | 1.00 / 2.000 | 0.192 | 1.559 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.195
- phase_score: 0.242
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.descend_1_score: 0.841
- phase_breakdown.approach_1_score: 0.129
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.013
- grasp_place_fitness: 0.573

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.573
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.195
- **Median Q (composite search score)**: 0.271
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.209


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89655,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1736,"descend_1.depth":0.07276,"grasp_1.grip_force":23.37211,"lift_1.lift_height":0.15447},"optimized_scores":{"best_composite_score":0.27055,"best_fitness_score":0.56055,"best_task_score":0.17071},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.50404,-0.02395,-0.00821],"force_p95":1.28964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49227,"mean_force":0.46444,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50379,-0.02282,0.18257]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.51099,-0.02248,-0.00109],"force_p95":0.38033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5936,"mean_force":0.07629,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49883,-0.02262,0.03565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17545.0,"contact_point_centroid":[0.50369,-0.00375,0.1001],"force_p95":0.07451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31909,"mean_force":0.04957,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50233,-0.02275,0.09832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14887.0,"contact_point_centroid":[0.50252,-0.04193,0.10126],"force_p95":0.07998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3159,"mean_force":0.0568,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50233,-0.02275,0.09845]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51369,-0.02311,-0.00204],"force_p95":0.13553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16762,"mean_force":0.12581,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50138,-0.02266,0.03524]},{"body_a":"world","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.5137,-0.02302,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50343,-0.00177,0.23858]},{"body_a":"world","body_b":"grasp_target","contact_count":3568.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50731,-0.02027,0.09829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.50831,-0.04215,0.16854],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1208,"mean_force":0.04876,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50767,-0.02291,0.1658]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5087.0,"contact_point_centroid":[0.50131,-0.00358,0.03555],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10121,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50013,-0.02264,0.03388]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.50966,-0.00392,0.16737],"force_p95":0.07372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09879,"mean_force":0.04326,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5077,-0.02291,0.16585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4152.0,"contact_point_centroid":[0.49932,-0.04187,0.03662],"force_p95":0.08035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09255,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50013,-0.02264,0.03388]}],"total_contact_groups":11},"final_pose_error":0.01312,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.50628,-0.02118,0.02666],"final_tcp_position":[0.50918,-0.02295,0.16797],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.49227,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1560.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50877,-0.01677,0.17948],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3568.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50847,-0.0228,0.04303],"tcp_start":[0.50877,-0.01677,0.17948],"tcp_to_object_dist_end":0.0178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51357,-0.02306,0.02585],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26577,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.1355,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11039.0,"raw_peak_contact_force":0.16762,"tcp_end":[0.5001,-0.02264,0.03385],"tcp_start":[0.50847,-0.0228,0.04303],"tcp_to_object_dist_end":0.01568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.51932,-0.02356,0.15345],"object_pos_start":[0.51357,-0.02306,0.02585],"object_to_goal_dist_end":0.19133,"object_to_goal_dist_start":0.26577,"object_z_max":0.15334,"peak_contact_force":0.07954,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32574.0,"raw_peak_contact_force":0.5936,"tcp_end":[0.50918,-0.02295,0.16797],"tcp_start":[0.5001,-0.02264,0.03385],"tcp_to_object_dist_end":0.01772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50628,-0.02118,0.02666],"object_pos_start":[0.51932,-0.02356,0.15345],"object_to_goal_dist_end":0.26517,"object_to_goal_dist_start":0.19133,"object_z_max":0.15349,"peak_contact_force":0.2095,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2443.0,"raw_peak_contact_force":1.49227,"tcp_end":[0.50369,-0.02281,0.19263],"tcp_start":[0.50918,-0.02295,0.16797],"tcp_to_object_dist_end":0.166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89655,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1233,"descend_1.depth":0.01878,"grasp_1.grip_force":24.80716,"lift_1.lift_height":0.14396},"optimized_scores":{"best_composite_score":0.28258,"best_fitness_score":0.57258,"best_task_score":0.19534},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.48712,0.04409,-0.00699],"force_p95":1.21965,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5501,"mean_force":0.36655,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49121,0.04358,0.17184]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.49854,0.04319,-0.00118],"force_p95":0.36308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5802,"mean_force":0.07553,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48656,0.04373,0.03606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13311.0,"contact_point_centroid":[0.49011,0.06298,0.09757],"force_p95":0.08484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32844,"mean_force":0.05881,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49012,0.04378,0.09479]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16412.0,"contact_point_centroid":[0.49189,0.02485,0.09564],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30213,"mean_force":0.04922,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49004,0.04378,0.09403]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04504,-0.0021],"force_p95":0.15075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19803,"mean_force":0.12996,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48905,0.04398,0.03553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5035.0,"contact_point_centroid":[0.48958,0.02486,0.03556],"force_p95":0.07525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17476,"mean_force":0.04317,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48781,0.04386,0.03422]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49751,0.03161,0.21981]},{"body_a":"world","body_b":"grasp_target","contact_count":2728.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49516,0.04499,0.07734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.49773,0.02505,0.15687],"force_p95":0.07723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1109,"mean_force":0.04348,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49517,0.04397,0.1555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1057.0,"contact_point_centroid":[0.49517,0.06321,0.15831],"force_p95":0.08056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10732,"mean_force":0.04917,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49515,0.04397,0.15547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4195.0,"contact_point_centroid":[0.48782,0.06316,0.03681],"force_p95":0.08654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09478,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48782,0.04386,0.03422]}],"total_contact_groups":11},"final_pose_error":0.01289,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49283,0.04321,0.02757],"final_tcp_position":[0.49667,0.0441,0.15754],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.5501,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49716,0.04586,0.13235],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":682.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2728.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49603,0.04461,0.04302],"tcp_start":[0.49716,0.04586,0.13235],"tcp_to_object_dist_end":0.01777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04447,0.02566],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24255,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14952,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11030.0,"raw_peak_contact_force":0.19803,"tcp_end":[0.48779,0.04386,0.03419],"tcp_start":[0.49603,0.04461,0.04302],"tcp_to_object_dist_end":0.01587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50689,0.04497,0.14303],"object_pos_start":[0.50115,0.04447,0.02566],"object_to_goal_dist_end":0.20804,"object_to_goal_dist_start":0.24255,"object_z_max":0.14291,"peak_contact_force":0.08053,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29866.0,"raw_peak_contact_force":0.5802,"tcp_end":[0.49667,0.0441,0.15754],"tcp_start":[0.48779,0.04386,0.03419],"tcp_to_object_dist_end":0.01778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49283,0.04321,0.02757],"object_pos_start":[0.50689,0.04497,0.14303],"object_to_goal_dist_end":0.24495,"object_to_goal_dist_start":0.20804,"object_z_max":0.14307,"peak_contact_force":0.17732,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2477.0,"raw_peak_contact_force":1.5501,"tcp_end":[0.49111,0.04358,0.18256],"tcp_start":[0.49667,0.0441,0.15754],"tcp_to_object_dist_end":0.155,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53398,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05009,"descend_1.depth":0.03373,"grasp_1.grip_force":20.66837,"lift_1.lift_height":0.15686},"optimized_scores":{"best_composite_score":0.25748,"best_fitness_score":0.54748,"best_task_score":0.14359},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.46768,-0.02094,-0.00848],"force_p95":1.30958,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63351,"mean_force":0.49029,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.46665,-0.01971,0.18664]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.47376,-0.0191,-0.0011],"force_p95":0.34157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56933,"mean_force":0.06492,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46179,-0.0195,0.03573]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17667.0,"contact_point_centroid":[0.46664,-0.00063,0.10212],"force_p95":0.07344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3031,"mean_force":0.04917,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46521,-0.01964,0.10034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15027.0,"contact_point_centroid":[0.46543,-0.03883,0.10339],"force_p95":0.07957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29918,"mean_force":0.05628,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46524,-0.01964,0.10069]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02019,-0.00205],"force_p95":0.1392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17093,"mean_force":0.12665,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,-0.01954,0.03506]},{"body_a":"world","body_b":"grasp_target","contact_count":3016.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48521,0.00719,0.17664]},{"body_a":"world","body_b":"grasp_target","contact_count":1620.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47065,-0.0182,0.04541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.47122,-0.03905,0.17153],"force_p95":0.07891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12147,"mean_force":0.04887,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47034,-0.0198,0.16895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.46424,-0.00046,0.0354],"force_p95":0.06785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11073,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.463,-0.01952,0.03386]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1219.0,"contact_point_centroid":[0.47245,-0.00081,0.17047],"force_p95":0.07316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10013,"mean_force":0.04348,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47038,-0.0198,0.169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4272.0,"contact_point_centroid":[0.46236,-0.03877,0.03644],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0875,"mean_force":0.05069,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.463,-0.01952,0.03386]}],"total_contact_groups":11},"final_pose_error":0.01255,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.46932,-0.0189,0.02644],"final_tcp_position":[0.4718,-0.01983,0.17087],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.63351,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3016.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47271,-0.01441,0.0575],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.471,-0.01965,0.04185],"tcp_start":[0.47271,-0.01441,0.0575],"tcp_to_object_dist_end":0.01666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01993,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28842,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13911,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11140.0,"raw_peak_contact_force":0.17093,"tcp_end":[0.46297,-0.01952,0.03383],"tcp_start":[0.471,-0.01965,0.04185],"tcp_to_object_dist_end":0.01535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.48196,-0.02042,0.15576],"object_pos_start":[0.47606,-0.01993,0.02582],"object_to_goal_dist_end":0.23617,"object_to_goal_dist_start":0.28842,"object_z_max":0.15564,"peak_contact_force":0.07969,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32828.0,"raw_peak_contact_force":0.56933,"tcp_end":[0.4718,-0.01983,0.17087],"tcp_start":[0.46297,-0.01952,0.03383],"tcp_to_object_dist_end":0.01822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46932,-0.0189,0.02644],"object_pos_start":[0.48196,-0.02042,0.15576],"object_to_goal_dist_end":0.29112,"object_to_goal_dist_start":0.23617,"object_z_max":0.15579,"peak_contact_force":0.19052,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2430.0,"raw_peak_contact_force":1.63351,"tcp_end":[0.46655,-0.01971,0.19656],"tcp_start":[0.4718,-0.01983,0.17087],"tcp_to_object_dist_end":0.17014,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```