## Search State

- **Seed**: 8
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | descend → grasp → approach → descend → release | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.0443 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.044) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.3
- id: place
  weight: 0.7
phases:
- id: descend_1
  type: descend
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
    - 0.04
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_depth:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
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
- id: lift_transport_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.044
- **task_score** (E): 0.162
- **fitness_score**: 0.284  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2427 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_transport_1 | 0.00 | 1.00 | 0.2846 |
| descend_2 | 1.00 | 1.00 | 0.1266 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.062) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.062)→(0.508, -0.001, 0.053) | (0.522, -0.001, 0.026)→(0.522, 0.000, 0.026) | 0.289→0.289 | 1.00 / 30.667 | 0.145 | 0.186 |
| lift_transport_1 | approach | 0.00 / step_budget | (0.508, -0.001, 0.053)→(0.567, 0.125, 0.299) | (0.522, 0.000, 0.026)→(0.533, 0.019, 0.019) | 0.289→0.276 | 1.00 / 8.333 | 0.123 | 1.140 |
| descend_2 | descend | 1.00 / step_budget | (0.567, 0.125, 0.299)→(0.602, 0.200, 0.207) | (0.533, 0.019, 0.019)→(0.533, 0.019, 0.019) | 0.276→0.276 | 1.00 / 9.000 | 182005.993 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.200, 0.207)→(0.597, 0.199, 0.227) | (0.533, 0.019, 0.019)→(0.533, 0.019, 0.019) | 0.276→0.276 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.205
- phase_score: 0.798
- phase_breakdown.place_score: 0.821
- phase_breakdown.pre_grasp_score: 0.745
- grasp_place_fitness: 0.312

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.312
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.205
- **Median Q (composite search score)**: 0.036
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at lower bound**: lift_transport_1.arc_height
- **Final σ (mean)**: 0.373


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93525,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.grasp_depth":0.03292,"descend_2.place_z_offset":-0.00154,"lift_transport_1.arc_height":0.12972},"optimized_scores":{"best_composite_score":0.02489,"best_fitness_score":0.26489,"best_task_score":0.14469},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48878,0.02254,0.18494]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4731,0.045,0.06469]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.47208,0.04922,0.21877]},{"body_a":"world","body_b":"grasp_target","contact_count":2288.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55012,0.17986,0.27743]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57186,0.22033,0.22863]},{"body_a":"left_finger","body_b":"right_finger","contact_count":329.0,"contact_point_centroid":[0.47224,0.0449,0.06583],"force_p95":0.01476,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01146,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.472,0.04489,0.06351]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4206.0,"contact_point_centroid":[0.47237,0.04939,0.22166],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01059,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.47217,0.04938,0.21939]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2442.0,"contact_point_centroid":[0.55036,0.1798,0.27982],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01045,"phase_index":3.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55007,0.17978,0.27753]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.57444,0.22138,0.22692],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00996,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57392,0.22135,0.22464]}],"total_contact_groups":9},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4827,0.04873,0.02602],"final_tcp_position":[0.5752,0.22164,0.22775],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.13845,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2840.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47955,0.04553,0.07167],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.04587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2129.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.472,0.04489,0.0635],"tcp_start":[0.47955,0.04553,0.07167],"tcp_to_object_dist_end":0.03917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8206.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52574,0.1371,0.33375],"tcp_start":[0.472,0.04489,0.0635],"tcp_to_object_dist_end":0.32305,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4730.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.5752,0.22164,0.22775],"tcp_start":[0.52574,0.1371,0.33375],"tcp_to_object_dist_end":0.28133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57069,0.21974,0.24839],"tcp_start":[0.5752,0.22164,0.22775],"tcp_to_object_dist_end":0.294,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93525,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.grasp_depth":0.02089,"descend_2.place_z_offset":0.01652,"lift_transport_1.arc_height":0.1},"optimized_scores":{"best_composite_score":0.03604,"best_fitness_score":0.27604,"best_task_score":0.13513},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.55237,0.00256,-0.00248],"force_p95":0.26615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55934,"mean_force":0.1447,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.54732,0.05792,0.24927]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5733.0,"contact_point_centroid":[0.52311,0.00011,0.1088],"force_p95":0.14902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31062,"mean_force":0.08683,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.51909,-0.01864,0.10896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6499.0,"contact_point_centroid":[0.52344,-0.03643,0.11221],"force_p95":0.1183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29522,"mean_force":0.07522,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.51933,-0.01799,0.11189]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02124,-0.00211],"force_p95":0.15459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21143,"mean_force":0.13103,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52345,-0.02001,0.04992]},{"body_a":"world","body_b":"grasp_target","contact_count":3104.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12776,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51408,-0.01,0.17782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4340.0,"contact_point_centroid":[0.52337,-0.00079,0.04937],"force_p95":0.07479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12681,"mean_force":0.04953,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52226,-0.01998,0.04852]},{"body_a":"world","body_b":"grasp_target","contact_count":2524.0,"contact_point_centroid":[0.5532,0.0036,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58774,0.17354,0.25176]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5532,0.0036,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60159,0.21975,0.21893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.52326,-0.03915,0.0494],"force_p95":0.07176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07346,"mean_force":0.04423,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52227,-0.01998,0.04853]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1683.0,"contact_point_centroid":[0.55105,0.06749,0.26638],"force_p95":0.01165,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01587,"mean_force":0.01058,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.55073,0.06748,0.26406]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2686.0,"contact_point_centroid":[0.58817,0.17362,0.25386],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01047,"phase_index":3.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58777,0.17361,0.25171]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.60418,0.22081,0.21791],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00989,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60379,0.22079,0.21554]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5532,0.0036,0.01602],"final_tcp_position":[0.60506,0.22102,0.21876],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273009.05632,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":777.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3104.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53049,-0.0201,0.05831],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53699,-0.02043,0.02559],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31628,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15203,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11112.0,"raw_peak_contact_force":0.21143,"tcp_end":[0.52224,-0.01998,0.04849],"tcp_start":[0.53049,-0.0201,0.05831],"tcp_to_object_dist_end":0.02724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5532,0.0036,0.01602],"object_pos_start":[0.53699,-0.02043,0.02559],"object_to_goal_dist_end":0.30023,"object_to_goal_dist_start":0.31628,"object_z_max":0.15435,"peak_contact_force":0.12263,"phase_name":"lift_transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15791.0,"raw_peak_contact_force":1.55934,"tcp_end":[0.57028,0.12072,0.29453],"tcp_start":[0.52224,-0.01998,0.04849],"tcp_to_object_dist_end":0.30262,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":631.0,"n_steps_budget":1000.0,"object_pos_end":[0.5532,0.0036,0.01602],"object_pos_start":[0.5532,0.0036,0.01602],"object_to_goal_dist_end":0.30023,"object_to_goal_dist_start":0.30023,"object_z_max":0.01602,"peak_contact_force":273009.05632,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5210.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.60506,0.22102,0.21876],"tcp_start":[0.57028,0.12072,0.29453],"tcp_to_object_dist_end":0.30177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5532,0.0036,0.01602],"object_pos_start":[0.5532,0.0036,0.01602],"object_to_goal_dist_end":0.30023,"object_to_goal_dist_start":0.30023,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60036,0.21916,0.2383],"tcp_start":[0.60506,0.22102,0.21876],"tcp_to_object_dist_end":0.31321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93382,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.grasp_depth":0.02043,"descend_2.place_z_offset":-0.00484,"lift_transport_1.arc_height":0.29983},"optimized_scores":{"best_composite_score":0.07182,"best_fitness_score":0.31182,"best_task_score":0.20473},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1859.0,"contact_point_centroid":[0.56074,0.00333,-0.00251],"force_p95":0.27417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7389,"mean_force":0.14645,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.57117,0.05444,0.23532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5672.0,"contact_point_centroid":[0.53226,-0.00618,0.10813],"force_p95":0.13563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31622,"mean_force":0.08435,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.52774,-0.02498,0.10756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6415.0,"contact_point_centroid":[0.53253,-0.04293,0.111],"force_p95":0.12364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30852,"mean_force":0.07783,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.52811,-0.02429,0.11036]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54567,-0.02912,-0.00215],"force_p95":0.16502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2229,"mean_force":0.13372,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53141,-0.02742,0.04854]},{"body_a":"world","body_b":"grasp_target","contact_count":3188.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51817,-0.01375,0.17706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4325.0,"contact_point_centroid":[0.53155,-0.0082,0.0483],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1343,"mean_force":0.04957,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5302,-0.02739,0.0471]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.5616,0.00482,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6146,0.13733,0.22024]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5616,0.00482,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6215,0.15723,0.17455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5029.0,"contact_point_centroid":[0.53141,-0.04659,0.04839],"force_p95":0.0738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07604,"mean_force":0.04404,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53021,-0.02739,0.04711]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1661.0,"contact_point_centroid":[0.57699,0.06465,0.25121],"force_p95":0.01193,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01063,"phase_index":2.0,"phase_name":"lift_transport_1","phase_type":"approach","tcp_position_centroid":[0.57664,0.06465,0.24889]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1440.0,"contact_point_centroid":[0.61498,0.13716,0.22287],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01035,"phase_index":3.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6145,0.13715,0.22062]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.62437,0.1581,0.17319],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00989,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62416,0.15809,0.17102]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.5616,0.00482,0.01602],"final_tcp_position":[0.62588,0.15827,0.17473],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273008.80012,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":798.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3188.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.02759,0.05717],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54558,-0.02801,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26034,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16114,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11154.0,"raw_peak_contact_force":0.2229,"tcp_end":[0.53017,-0.02738,0.04706],"tcp_start":[0.53853,-0.02759,0.05717],"tcp_to_object_dist_end":0.02654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5616,0.00482,0.01602],"object_pos_start":[0.54558,-0.02801,0.02546],"object_to_goal_dist_end":0.23791,"object_to_goal_dist_start":0.26034,"object_z_max":0.15149,"peak_contact_force":0.12263,"phase_name":"lift_transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15607.0,"raw_peak_contact_force":1.7389,"tcp_end":[0.60546,0.11735,0.2694],"tcp_start":[0.53017,-0.02738,0.04706],"tcp_to_object_dist_end":0.28069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.5616,0.00482,0.01602],"object_pos_start":[0.5616,0.00482,0.01602],"object_to_goal_dist_end":0.23791,"object_to_goal_dist_start":0.23791,"object_z_max":0.01602,"peak_contact_force":273008.80012,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2776.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.62588,0.15827,0.17473],"tcp_start":[0.60546,0.11735,0.2694],"tcp_to_object_dist_end":0.22994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5616,0.00482,0.01602],"object_pos_start":[0.5616,0.00482,0.01602],"object_to_goal_dist_end":0.23791,"object_to_goal_dist_start":0.23791,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61993,0.15672,0.19395],"tcp_start":[0.62588,0.15827,0.17473],"tcp_to_object_dist_end":0.24111,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```