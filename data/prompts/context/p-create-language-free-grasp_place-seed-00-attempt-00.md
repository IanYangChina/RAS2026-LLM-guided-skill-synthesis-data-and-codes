## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → grasp → approach → release → retract | linear_cartesian | — | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 1 | 0.1893 | 0.20 | ✅ accepted |

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

## Current Skill (Q=0.189) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_goal
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.189
- **task_score** (E): 0.201
- **fitness_score**: 0.329  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.140

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2643 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| approach_2 | 0.00 | 1.00 | 0.1034 |
| release_1 | 1.00 | 1.00 | 0.0259 |
| retract_1 | 0.67 | 1.00 | 0.1617 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.039) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.039)→(0.485, 0.000, 0.030) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.025) | 0.265→0.266 | 1.00 / 41.667 | 0.165 | 0.252 |
| approach_2 | approach | 0.00 / step_budget | (0.485, 0.000, 0.030)→(0.502, 0.039, 0.124) | (0.497, 0.000, 0.025)→(0.515, 0.039, 0.106) | 0.266→0.186 | 1.00 / 23.000 | 0.130 | 0.606 |
| release_1 | release | 1.00 / step_budget | (0.502, 0.039, 0.124)→(0.496, 0.039, 0.149) | (0.515, 0.039, 0.106)→(0.513, 0.037, 0.016) | 0.186→0.241 | 1.00 / 4.000 | 0.113 | 1.305 |
| retract_1 | retract | 0.67 / step_budget | (0.496, 0.039, 0.149)→(0.565, 0.163, 0.215) | (0.513, 0.037, 0.016)→(0.513, 0.037, 0.016) | 0.241→0.241 | 1.00 / 4.000 | 0.123 | 0.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- grasp_place_fitness: 0.340

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.340
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.222
- **Median Q (composite search score)**: 0.184
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: approach_2.arc_height
- **Final σ (mean)**: 0.576


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92174,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.arc_height":0.05},"optimized_scores":{"best_composite_score":0.18396,"best_fitness_score":0.32396,"best_task_score":0.19224},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":246.0,"contact_point_centroid":[0.50812,0.02201,-0.00492],"force_p95":0.92282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36071,"mean_force":0.27312,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49976,0.00923,0.1422]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.51005,-0.02036,-0.0013],"force_p95":0.39711,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63469,"mean_force":0.09391,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49861,-0.02138,0.03092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14632.0,"contact_point_centroid":[0.50207,0.00785,0.07733],"force_p95":0.10858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32858,"mean_force":0.06848,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49918,-0.01098,0.07615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15536.0,"contact_point_centroid":[0.50196,-0.03009,0.07571],"force_p95":0.10436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31384,"mean_force":0.06553,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49908,-0.01135,0.07478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":730.0,"contact_point_centroid":[0.50808,-0.00889,0.12132],"force_p95":0.15828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24332,"mean_force":0.08381,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5038,0.00938,0.12417]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51375,-0.02273,-0.00213],"force_p95":0.16144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23906,"mean_force":0.13295,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50139,-0.02163,0.03058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":747.0,"contact_point_centroid":[0.50789,0.02794,0.12134],"force_p95":0.15911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18711,"mean_force":0.0909,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50346,0.00937,0.12381]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.50086,-0.00239,0.03206],"force_p95":0.08062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14584,"mean_force":0.05193,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50021,-0.0216,0.02931]},{"body_a":"world","body_b":"grasp_target","contact_count":3264.0,"contact_point_centroid":[0.5137,-0.02302,-0.00195],"force_p95":0.12702,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50309,-0.01083,0.16768]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50956,0.02213,-0.00198],"force_p95":0.12292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12647,"mean_force":0.12237,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52031,0.0716,0.1989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5002.0,"contact_point_centroid":[0.50087,-0.04075,0.03116],"force_p95":0.07302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08614,"mean_force":0.04465,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50021,-0.0216,0.02932]}],"total_contact_groups":11},"final_pose_error":0.03141,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.50956,0.02213,0.01602],"final_tcp_position":[0.54392,0.13232,0.24942],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.36071,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3264.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50844,-0.02175,0.03828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02163,0.02555],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26506,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15347,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10864.0,"raw_peak_contact_force":0.23906,"tcp_end":[0.50018,-0.0216,0.02928],"tcp_start":[0.50844,-0.02175,0.03828],"tcp_to_object_dist_end":0.01392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51821,0.00933,0.10793],"object_pos_start":[0.5136,-0.02163,0.02555],"object_to_goal_dist_end":0.18589,"object_to_goal_dist_start":0.26506,"object_z_max":0.10788,"peak_contact_force":0.16655,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30323.0,"raw_peak_contact_force":0.63469,"subtask_id":"reach_goal","tcp_end":[0.50562,0.00933,0.12646],"tcp_start":[0.50018,-0.0216,0.02928],"tcp_to_object_dist_end":0.02241,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50954,0.02175,0.01595],"object_pos_start":[0.51821,0.00933,0.10793],"object_to_goal_dist_end":0.24761,"object_to_goal_dist_start":0.18589,"object_z_max":0.10793,"peak_contact_force":0.1079,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1723.0,"raw_peak_contact_force":1.36071,"tcp_end":[0.49965,0.00923,0.15158],"tcp_start":[0.50562,0.00933,0.12646],"tcp_to_object_dist_end":0.13656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50956,0.02213,0.01602],"object_pos_start":[0.50954,0.02175,0.01595],"object_to_goal_dist_end":0.24735,"object_to_goal_dist_start":0.24761,"object_z_max":0.01645,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12647,"tcp_end":[0.54392,0.13232,0.24942],"tcp_start":[0.49965,0.00923,0.15158],"tcp_to_object_dist_end":0.26038,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92105,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.arc_height":0.06773},"optimized_scores":{"best_composite_score":0.19968,"best_fitness_score":0.33968,"best_task_score":0.22234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":249.0,"contact_point_centroid":[0.50849,0.07086,-0.00488],"force_p95":1.081,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29556,"mean_force":0.29567,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49542,0.0853,0.13786]},{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.49805,0.0408,-0.00145],"force_p95":0.37371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63228,"mean_force":0.09554,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.487,0.04192,0.03182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14612.0,"contact_point_centroid":[0.49312,0.03852,0.07842],"force_p95":0.10817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35546,"mean_force":0.06842,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49042,0.05744,0.07678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16117.0,"contact_point_centroid":[0.4927,0.07522,0.07591],"force_p95":0.09858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.341,"mean_force":0.06336,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49006,0.05643,0.07447]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50132,0.0445,-0.00231],"force_p95":0.21102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29091,"mean_force":0.14544,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48976,0.04183,0.03111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":706.0,"contact_point_centroid":[0.50497,0.06719,0.11886],"force_p95":0.15799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2769,"mean_force":0.08987,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49928,0.08602,0.12]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":719.0,"contact_point_centroid":[0.50434,0.10464,0.11892],"force_p95":0.11783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26996,"mean_force":0.07567,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49951,0.08606,0.1202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3488.0,"contact_point_centroid":[0.49014,0.02244,0.03331],"force_p95":0.09527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17183,"mean_force":0.05949,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48861,0.04172,0.02989]},{"body_a":"world","body_b":"grasp_target","contact_count":3276.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49721,0.02111,0.16774]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51012,0.06931,-0.00198],"force_p95":0.12303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12884,"mean_force":0.12247,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52394,0.15843,0.1643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5468.0,"contact_point_centroid":[0.48856,0.06098,0.03245],"force_p95":0.07968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08701,"mean_force":0.04237,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48862,0.04173,0.0299]}],"total_contact_groups":11},"final_pose_error":0.02112,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51012,0.0693,0.01602],"final_tcp_position":[0.55506,0.23002,0.18502],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.29556,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3276.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49665,0.04238,0.03848],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04199,0.02501],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24492,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19124,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10756.0,"raw_peak_contact_force":0.29091,"tcp_end":[0.48858,0.04172,0.02986],"tcp_start":[0.49665,0.04238,0.03848],"tcp_to_object_dist_end":0.01348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51441,0.08629,0.10477],"object_pos_start":[0.50115,0.04199,0.02501],"object_to_goal_dist_end":0.17149,"object_to_goal_dist_start":0.24492,"object_z_max":0.10472,"peak_contact_force":0.11532,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30903.0,"raw_peak_contact_force":0.63228,"subtask_id":"reach_goal","tcp_end":[0.50126,0.08623,0.12247],"tcp_start":[0.48858,0.04172,0.02986],"tcp_to_object_dist_end":0.02205,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51011,0.06966,0.01627],"object_pos_start":[0.51441,0.08629,0.10477],"object_to_goal_dist_end":0.22512,"object_to_goal_dist_start":0.17149,"object_z_max":0.10477,"peak_contact_force":0.11948,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1674.0,"raw_peak_contact_force":1.29556,"tcp_end":[0.49531,0.08529,0.14753],"tcp_start":[0.50126,0.08623,0.12247],"tcp_to_object_dist_end":0.13301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51012,0.0693,0.01602],"object_pos_start":[0.51011,0.06966,0.01627],"object_to_goal_dist_end":0.22554,"object_to_goal_dist_start":0.22512,"object_z_max":0.0165,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12884,"tcp_end":[0.55506,0.23002,0.18502],"tcp_start":[0.49531,0.08529,0.14753],"tcp_to_object_dist_end":0.23751,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92241,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.arc_height":0.05485},"optimized_scores":{"best_composite_score":0.18438,"best_fitness_score":0.32438,"best_task_score":0.18823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":242.0,"contact_point_centroid":[0.51239,0.01891,-0.00484],"force_p95":0.95455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25972,"mean_force":0.29158,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49316,0.02139,0.13745]},{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.47447,-0.01714,-0.00129],"force_p95":0.3781,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55094,"mean_force":0.10964,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4644,-0.01819,0.03325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17367.0,"contact_point_centroid":[0.47837,-0.0211,0.07763],"force_p95":0.0972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27506,"mean_force":0.05898,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47678,-0.00212,0.07601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16778.0,"contact_point_centroid":[0.47899,0.01729,0.07878],"force_p95":0.09303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26654,"mean_force":0.05961,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4772,-0.00168,0.07699]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.01997,-0.00212],"force_p95":0.1562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22493,"mean_force":0.13169,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46641,-0.01888,0.0327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.5014,0.00281,0.12054],"force_p95":0.09991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19364,"mean_force":0.06491,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49724,0.02164,0.11955]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":978.0,"contact_point_centroid":[0.50171,0.0404,0.11997],"force_p95":0.09952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18929,"mean_force":0.06265,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49724,0.02164,0.11954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4790.0,"contact_point_centroid":[0.46546,0.00033,0.03351],"force_p95":0.07198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14432,"mean_force":0.04481,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4653,-0.01886,0.0316]},{"body_a":"world","body_b":"grasp_target","contact_count":3164.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48549,-0.00945,0.1684]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51822,0.01895,-0.00199],"force_p95":0.12271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12434,"mean_force":0.12243,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54355,0.07474,0.17719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.46549,-0.03811,0.03349],"force_p95":0.07241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08451,"mean_force":0.0447,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46531,-0.01886,0.0316]}],"total_contact_groups":11},"final_pose_error":0.05608,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.51822,0.01895,0.01602],"final_tcp_position":[0.5962,0.12678,0.21079],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.25972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3164.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4731,-0.019,0.03941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01905,0.02558],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28801,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15156,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11574.0,"raw_peak_contact_force":0.22493,"tcp_end":[0.46528,-0.01885,0.03157],"tcp_start":[0.4731,-0.019,0.03941],"tcp_to_object_dist_end":0.01233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51283,0.02155,0.1057],"object_pos_start":[0.47606,-0.01905,0.02558],"object_to_goal_dist_end":0.20029,"object_to_goal_dist_start":0.28801,"object_z_max":0.10563,"peak_contact_force":0.10939,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34299.0,"raw_peak_contact_force":0.55094,"subtask_id":"reach_goal","tcp_end":[0.49899,0.02161,0.12173],"tcp_start":[0.46528,-0.01885,0.03157],"tcp_to_object_dist_end":0.02118,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51863,0.01897,0.01582],"object_pos_start":[0.51283,0.02155,0.1057],"object_to_goal_dist_end":0.25046,"object_to_goal_dist_start":0.20029,"object_z_max":0.10572,"peak_contact_force":0.11152,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2140.0,"raw_peak_contact_force":1.25972,"tcp_end":[0.49304,0.02138,0.14709],"tcp_start":[0.49899,0.02161,0.12173],"tcp_to_object_dist_end":0.13376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51822,0.01895,0.01602],"object_pos_start":[0.51863,0.01897,0.01582],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25046,"object_z_max":0.01627,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12434,"tcp_end":[0.5962,0.12678,0.21079],"tcp_start":[0.49304,0.02138,0.14709],"tcp_to_object_dist_end":0.23589,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```