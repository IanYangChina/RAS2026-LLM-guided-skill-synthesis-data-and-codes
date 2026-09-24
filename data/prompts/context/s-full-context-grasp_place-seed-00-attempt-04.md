## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6552 | 0.17 | ❌ rejected |
| 3 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1694 | 0.19 | ✅ accepted |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1713 | 0.18 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1716 | 0.18 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1715 | 0.18 | ✅ accepted |

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

## Current Skill (Q=-0.655) — your mutation base

```yaml
skill: grasp_place
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: insert_2
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
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: -0.655
- **task_score** (E): 0.175
- **fitness_score**: 0.175  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 0.00 | 1.00 | 0.1175 |
| descend_to_grasp | 0.00 | 1.00 | 0.0501 |
| grasp_object | 1.00 | 1.00 | 0.0016 |
| lift_object | 0.00 | 1.00 | 0.1340 |
| approach_goal | 0.33 | 1.00 | 0.1925 |
| descend_to_goal | 0.33 | 1.00 | 0.1027 |
| release_object | 1.00 | 1.00 | 0.0267 |
| retract_after_release | 1.00 | 1.00 | 0.0911 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.440, 0.002, 0.203) | (0.497, 0.001, 0.030)→(0.468, -0.000, 0.019) | 0.263→0.282 | 1.00 / 5.000 | 310.475 | 1423.721 |
| descend_to_grasp | approach | 0.00 / step_budget | (0.440, 0.002, 0.203)→(0.463, -0.009, 0.175) | (0.468, -0.000, 0.019)→(0.468, -0.000, 0.019) | 0.282→0.282 | 1.00 / 5.000 | 91265.370 | 936.252 |
| grasp_object | grasp | 1.00 / step_budget | (0.463, -0.009, 0.175)→(0.463, -0.009, 0.173) | (0.468, -0.000, 0.019)→(0.468, -0.000, 0.019) | 0.282→0.282 | 1.00 / 9.000 | 68.601 | 426.502 |
| lift_object | lift | 0.00 / step_budget | (0.463, -0.009, 0.173)→(0.435, 0.109, 0.149) | (0.468, -0.000, 0.019)→(0.466, -0.001, 0.019) | 0.282→0.283 | 1.00 / 9.667 | 56133.819 | 381.265 |
| approach_goal | approach | 0.33 / step_budget | (0.435, 0.109, 0.149)→(0.522, 0.085, 0.269) | (0.466, -0.001, 0.019)→(0.463, 0.034, 0.019) | 0.283→0.266 | 1.00 / 9.000 | 94368.588 | 664.802 |
| descend_to_goal | approach | 0.33 / step_budget | (0.522, 0.085, 0.269)→(0.590, 0.118, 0.293) | (0.463, 0.034, 0.019)→(0.465, 0.034, 0.019) | 0.266→0.266 | 1.00 / 10.000 | 56200.177 | 685.518 |
| release_object | release | 1.00 / step_budget | (0.590, 0.118, 0.293)→(0.591, 0.118, 0.320) | (0.465, 0.034, 0.019)→(0.465, 0.034, 0.019) | 0.266→0.266 | 1.00 / 4.000 | 0.123 | 124.639 |
| retract_after_release | retract | 1.00 / step_budget | (0.591, 0.118, 0.320)→(0.591, 0.117, 0.411) | (0.465, 0.034, 0.019)→(0.465, 0.034, 0.019) | 0.266→0.266 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.206
- phase_score: 0.244
- phase_breakdown.reach_object_score: 0.257
- phase_breakdown.place_goal_score: 0.238
- grasp_place_fitness: 0.191

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.191
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.206
- **Median Q (composite search score)**: -0.646
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.273


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.33898,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15413,"approach_above.speed":0.15059,"approach_goal.approach_goal_height":0.11993,"approach_goal.speed":0.26356,"descend_to_goal.place_offset":0.0285,"descend_to_goal.speed":0.17102,"descend_to_grasp.descend_offset":0.02924,"descend_to_grasp.speed":0.1453,"lift_object.lift_height":0.22157,"lift_object.speed":0.17993,"release_object.release_time":0.11788,"retract_after_release.retract_height":0.10841,"retract_after_release.speed":0.21444},"optimized_scores":{"best_composite_score":-0.63884,"best_fitness_score":0.19116,"best_task_score":0.2056},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63441,-0.00641,-0.00046],"force_p95":282.7123,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1443.61335,"mean_force":214.28283,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.41613,-0.00795,0.15843]},{"body_a":"world","body_b":"link6","contact_count":973.0,"contact_point_centroid":[0.61674,-0.01942,-0.00023],"force_p95":539.39416,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":954.97018,"mean_force":326.37224,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.43521,-0.0247,0.21088]},{"body_a":"world","body_b":"link6","contact_count":486.0,"contact_point_centroid":[0.54443,0.14195,-0.00037],"force_p95":571.44326,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":681.5141,"mean_force":455.43592,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55314,0.15236,0.29336]},{"body_a":"world","body_b":"link6","contact_count":693.0,"contact_point_centroid":[0.5439,-0.05841,-9e-05],"force_p95":327.49358,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":457.26359,"mean_force":269.46733,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52647,0.02294,0.27144]},{"body_a":"world","body_b":"link6","contact_count":464.0,"contact_point_centroid":[0.60907,-0.07142,-0.00023],"force_p95":311.84831,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":428.68197,"mean_force":246.79299,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45241,0.0721,0.16333]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.67674,-0.03611,-0.00012],"force_p95":72.7794,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":381.36197,"mean_force":70.59506,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46444,-0.042,0.17146]},{"body_a":"link5","body_b":"hand","contact_count":271.0,"contact_point_centroid":[0.49579,-0.08275,0.26083],"force_p95":247.48667,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.30963,"mean_force":136.11505,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52474,0.02375,0.27433]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.55393,0.14739,-0.00019],"force_p95":100.29862,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.79821,"mean_force":67.57286,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55545,0.15377,0.29404]},{"body_a":"grasp_target","body_b":"link7","contact_count":217.0,"contact_point_centroid":[0.497,-0.02554,0.04101],"force_p95":3.31439,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.88972,"mean_force":0.69128,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.39105,-0.00341,0.10225]},{"body_a":"grasp_target","body_b":"hand","contact_count":201.0,"contact_point_centroid":[0.49103,-0.03349,0.05498],"force_p95":2.45565,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.0913,"mean_force":0.64992,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.39058,-0.00335,0.09987]},{"body_a":"world","body_b":"grasp_target","contact_count":3487.0,"contact_point_centroid":[0.48062,-0.02766,-0.00251],"force_p95":0.34514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4297,"mean_force":0.17459,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.42981,-0.00776,0.17037]},{"body_a":"grasp_target","body_b":"link6","contact_count":511.0,"contact_point_centroid":[0.49855,-0.00294,0.03474],"force_p95":0.91078,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.25705,"mean_force":0.32231,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53758,0.03584,0.29168]},{"body_a":"world","body_b":"grasp_target","contact_count":3375.0,"contact_point_centroid":[0.46839,-0.00605,-0.00266],"force_p95":0.44048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65592,"mean_force":0.18449,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5292,0.04969,0.27773]},{"body_a":"grasp_target","body_b":"link6","contact_count":517.0,"contact_point_centroid":[0.49844,0.09159,0.02846],"force_p95":0.25521,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.76416,"mean_force":0.1998,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55299,0.15217,0.29369]},{"body_a":"world","body_b":"grasp_target","contact_count":2276.0,"contact_point_centroid":[0.46353,0.07383,-0.0026],"force_p95":0.32883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48058,"mean_force":0.1658,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55263,0.1518,0.29644]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46535,0.07387,-0.00225],"force_p95":0.24092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25409,"mean_force":0.13635,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55551,0.15357,0.3008]}],"total_contact_groups":27},"final_pose_error":0.01353,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.46555,0.07397,0.01602],"final_tcp_position":[0.55652,0.15249,0.41635],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":272953.23803,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4709,-0.02879,0.01602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.28619,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":351.87891,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4811.0,"raw_peak_contact_force":1443.61335,"subtask_id":"reach_object","tcp_end":[0.45236,-0.01679,0.21287],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19809,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4709,-0.02879,0.01602],"object_pos_start":[0.4709,-0.02879,0.01602],"object_to_goal_dist_end":0.28619,"object_to_goal_dist_start":0.28619,"object_z_max":0.01602,"peak_contact_force":272953.23803,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4973.0,"raw_peak_contact_force":954.97018,"subtask_id":"reach_object","tcp_end":[0.46462,-0.04201,0.17311],"tcp_start":[0.45236,-0.01679,0.21287],"tcp_to_object_dist_end":0.15777,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4709,-0.02879,0.01602],"object_pos_start":[0.4709,-0.02879,0.01602],"object_to_goal_dist_end":0.28619,"object_to_goal_dist_start":0.28619,"object_z_max":0.01602,"peak_contact_force":67.49891,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2599.0,"raw_peak_contact_force":381.36197,"tcp_end":[0.46442,-0.04205,0.17133],"tcp_start":[0.46462,-0.04201,0.17311],"tcp_to_object_dist_end":0.15601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":488.0,"n_steps_budget":600.0,"object_pos_end":[0.4709,-0.02879,0.01602],"object_pos_start":[0.4709,-0.02879,0.01602],"object_to_goal_dist_end":0.28619,"object_to_goal_dist_start":0.28619,"object_z_max":0.01602,"peak_contact_force":229.23435,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4501.0,"raw_peak_contact_force":428.68197,"tcp_end":[0.45863,0.11195,0.15236],"tcp_start":[0.46442,-0.04205,0.17133],"tcp_to_object_dist_end":0.19633,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4609,0.07353,0.01602],"object_pos_start":[0.4709,-0.02879,0.01602],"object_to_goal_dist_end":0.23919,"object_to_goal_dist_start":0.28619,"object_z_max":0.01695,"peak_contact_force":9748.83793,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9299.0,"raw_peak_contact_force":457.26359,"subtask_id":"place_goal","tcp_end":[0.54929,0.14877,0.32608],"tcp_start":[0.45863,0.11195,0.15236],"tcp_to_object_dist_end":0.33107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.46669,0.07539,0.01491],"object_pos_start":[0.4609,0.07353,0.01602],"object_to_goal_dist_end":0.23735,"object_to_goal_dist_start":0.23919,"object_z_max":0.01602,"peak_contact_force":167951.73011,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5773.0,"raw_peak_contact_force":681.5141,"subtask_id":"place_goal","tcp_end":[0.55538,0.15411,0.29366],"tcp_start":[0.54929,0.14877,0.32608],"tcp_to_object_dist_end":0.30292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46554,0.07394,0.01602],"object_pos_start":[0.46669,0.07539,0.01491],"object_to_goal_dist_end":0.23728,"object_to_goal_dist_start":0.23735,"object_z_max":0.01605,"peak_contact_force":0.12301,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1213.0,"raw_peak_contact_force":100.79821,"tcp_end":[0.5557,0.15338,0.32142],"tcp_start":[0.55538,0.15411,0.29366],"tcp_to_object_dist_end":0.32818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.46555,0.07397,0.01602],"object_pos_start":[0.46554,0.07394,0.01602],"object_to_goal_dist_end":0.23727,"object_to_goal_dist_start":0.23728,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12297,"tcp_end":[0.55652,0.15249,0.41635],"tcp_start":[0.5557,0.15338,0.32142],"tcp_to_object_dist_end":0.41798,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.05128,"average_mean_iterations":17.33333,"average_solve_count":117.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.14144,"approach_above.speed":0.178,"approach_goal.approach_goal_height":0.11963,"approach_goal.speed":0.15238,"descend_to_goal.place_offset":0.02658,"descend_to_goal.speed":0.21865,"descend_to_grasp.descend_offset":0.0397,"descend_to_grasp.speed":0.22168,"lift_object.lift_height":0.22629,"lift_object.speed":0.15859,"release_object.release_time":0.34544,"retract_after_release.retract_height":0.0977,"retract_after_release.speed":0.21841},"optimized_scores":{"best_composite_score":-0.64634,"best_fitness_score":0.18366,"best_task_score":0.19822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":880.0,"contact_point_centroid":[0.63268,0.01953,-0.00042],"force_p95":366.85496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1382.32815,"mean_force":231.55191,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.41408,0.01659,0.15634]},{"body_a":"world","body_b":"link6","contact_count":697.0,"contact_point_centroid":[0.61861,0.04202,-0.00022],"force_p95":584.71412,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":934.39028,"mean_force":327.38196,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.43441,0.04525,0.21133]},{"body_a":"world","body_b":"link5","contact_count":44.0,"contact_point_centroid":[0.59651,0.27155,-0.00026],"force_p95":776.28235,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":890.15298,"mean_force":445.37468,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.43039,0.15131,0.18017]},{"body_a":"world","body_b":"link6","contact_count":874.0,"contact_point_centroid":[0.61062,0.13859,-0.0002],"force_p95":511.00552,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":812.89818,"mean_force":331.77672,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.45915,0.16835,0.22165]},{"body_a":"world","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.60208,0.08333,-0.00026],"force_p95":347.48478,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":790.13038,"mean_force":270.33613,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.40332,0.15211,0.17437]},{"body_a":"link5","body_b":"hand","contact_count":24.0,"contact_point_centroid":[0.50187,0.16217,0.22882],"force_p95":680.67122,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":685.27708,"mean_force":442.68604,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.42615,0.12584,0.17427]},{"body_a":"world","body_b":"link6","contact_count":446.0,"contact_point_centroid":[0.66308,0.06241,-0.00013],"force_p95":86.07571,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":638.79593,"mean_force":73.9886,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46118,0.06347,0.18366]},{"body_a":"world","body_b":"link6","contact_count":509.0,"contact_point_centroid":[0.63126,0.06671,-0.00028],"force_p95":228.24128,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.98109,"mean_force":195.24152,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40819,0.07952,0.15577]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.62684,0.18157,-0.0001],"force_p95":80.22043,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.77632,"mean_force":55.24812,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5873,0.19684,0.29122]},{"body_a":"grasp_target","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.49615,0.02996,0.047],"force_p95":1.15793,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.10649,"mean_force":0.38801,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.39567,0.00799,0.115]},{"body_a":"grasp_target","body_b":"hand","contact_count":256.0,"contact_point_centroid":[0.48812,0.02992,0.05709],"force_p95":2.76436,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.03263,"mean_force":0.52433,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.39157,0.00657,0.10168]},{"body_a":"world","body_b":"grasp_target","contact_count":3143.0,"contact_point_centroid":[0.494,0.04704,-0.00256],"force_p95":0.29362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.3941,"mean_force":0.17416,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.43044,0.01699,0.17244]},{"body_a":"grasp_target","body_b":"link7","contact_count":300.0,"contact_point_centroid":[0.49634,0.07941,0.05207],"force_p95":0.20305,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.96177,"mean_force":0.14464,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.38623,0.12633,0.15507]},{"body_a":"grasp_target","body_b":"link7","contact_count":422.0,"contact_point_centroid":[0.5134,0.06492,0.05259],"force_p95":0.27207,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60359,"mean_force":0.20858,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40152,0.08179,0.15161]},{"body_a":"world","body_b":"grasp_target","contact_count":3667.0,"contact_point_centroid":[0.49213,0.04805,-0.00229],"force_p95":0.42313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56671,"mean_force":0.14378,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.40486,0.15393,0.17602]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.49698,0.04605,-0.00254],"force_p95":0.24331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35435,"mean_force":0.15969,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40847,0.07946,0.15594]}],"total_contact_groups":28},"final_pose_error":0.01395,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49357,0.04655,0.02602],"final_tcp_position":[0.58828,0.19608,0.40101],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273041.34065,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49808,0.04658,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24145,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":377.30462,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4677.0,"raw_peak_contact_force":1382.32815,"subtask_id":"reach_object","tcp_end":[0.4495,0.03567,0.21581],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19621,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.4979,0.04661,0.02602],"object_pos_start":[0.49808,0.04658,0.02602],"object_to_goal_dist_end":0.24147,"object_to_goal_dist_start":0.24145,"object_z_max":0.02603,"peak_contact_force":354.91048,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3681.0,"raw_peak_contact_force":934.39028,"subtask_id":"reach_object","tcp_end":[0.46135,0.06338,0.18482],"tcp_start":[0.4495,0.03567,0.21581],"tcp_to_object_dist_end":0.16381,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4979,0.04661,0.02602],"object_pos_start":[0.4979,0.04661,0.02602],"object_to_goal_dist_end":0.24147,"object_to_goal_dist_start":0.24147,"object_z_max":0.02602,"peak_contact_force":69.63715,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2573.0,"raw_peak_contact_force":638.79593,"tcp_end":[0.46118,0.06349,0.18354],"tcp_start":[0.46135,0.06338,0.18482],"tcp_to_object_dist_end":0.16263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49135,0.04466,0.02522],"object_pos_start":[0.4979,0.04661,0.02602],"object_to_goal_dist_end":0.24534,"object_to_goal_dist_start":0.24147,"object_z_max":0.02602,"peak_contact_force":167951.73011,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5152.0,"raw_peak_contact_force":297.98109,"tcp_end":[0.40142,0.08962,0.1626],"tcp_start":[0.46118,0.06349,0.18354],"tcp_to_object_dist_end":0.17024,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49357,0.04655,0.02602],"object_pos_start":[0.49135,0.04466,0.02522],"object_to_goal_dist_end":0.24275,"object_to_goal_dist_start":0.24534,"object_z_max":0.02613,"peak_contact_force":273041.34065,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9206.0,"raw_peak_contact_force":790.13038,"subtask_id":"place_goal","tcp_end":[0.41429,0.16984,0.18675],"tcp_start":[0.40142,0.08962,0.1626],"tcp_to_object_dist_end":0.21753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49357,0.04655,0.02602],"object_pos_start":[0.49357,0.04655,0.02602],"object_to_goal_dist_end":0.24275,"object_to_goal_dist_start":0.24275,"object_z_max":0.02602,"peak_contact_force":327.92116,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9169.0,"raw_peak_contact_force":890.15298,"subtask_id":"place_goal","tcp_end":[0.58746,0.19678,0.2912],"tcp_start":[0.41429,0.16984,0.18675],"tcp_to_object_dist_end":0.31891,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49357,0.04655,0.02602],"object_pos_start":[0.49357,0.04655,0.02602],"object_to_goal_dist_end":0.24275,"object_to_goal_dist_start":0.24275,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1109.0,"raw_peak_contact_force":182.77632,"tcp_end":[0.58748,0.1968,0.31722],"tcp_start":[0.58746,0.19678,0.2912],"tcp_to_object_dist_end":0.34086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49357,0.04655,0.02602],"object_pos_start":[0.49357,0.04655,0.02602],"object_to_goal_dist_end":0.24275,"object_to_goal_dist_start":0.24275,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58828,0.19608,0.40101],"tcp_start":[0.58748,0.1968,0.31722],"tcp_to_object_dist_end":0.41466,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.76724,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.14476,"approach_above.speed":0.23634,"approach_goal.approach_goal_height":0.08565,"approach_goal.speed":0.20345,"descend_to_goal.place_offset":0.00609,"descend_to_goal.speed":0.1614,"descend_to_grasp.descend_offset":0.02035,"descend_to_grasp.speed":0.1657,"lift_object.lift_height":0.24972,"lift_object.speed":0.12776,"release_object.release_time":0.22701,"retract_after_release.retract_height":0.10938,"retract_after_release.speed":0.20679},"optimized_scores":{"best_composite_score":-0.68048,"best_fitness_score":0.14952,"best_task_score":0.12079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.6314,-0.00658,-0.00046],"force_p95":209.20005,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1445.22025,"mean_force":204.57173,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.39825,-0.00657,0.13568]},{"body_a":"world","body_b":"link6","contact_count":970.0,"contact_point_centroid":[0.62162,-0.01514,-0.00022],"force_p95":519.14952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":919.39525,"mean_force":298.54573,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.42718,-0.018,0.19481]},{"body_a":"world","body_b":"link6","contact_count":993.0,"contact_point_centroid":[0.57802,-0.10005,-0.00024],"force_p95":453.25959,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":747.01249,"mean_force":365.76606,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54662,-0.01911,0.2698]},{"body_a":"world","body_b":"link6","contact_count":988.0,"contact_point_centroid":[0.60466,-0.04302,-0.00021],"force_p95":395.76924,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":484.88734,"mean_force":308.32522,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.61459,-0.03263,0.29363]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.52715,0.00115,-0.00331],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":469.7999,"mean_force":22.37142,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.37314,-0.00264,0.04895]},{"body_a":"world","body_b":"link6","contact_count":459.0,"contact_point_centroid":[0.59342,-0.07527,-0.00011],"force_p95":281.79088,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":417.13245,"mean_force":224.97024,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44504,0.08359,0.14715]},{"body_a":"world","body_b":"link6","contact_count":447.0,"contact_point_centroid":[0.67937,-0.01915,-0.00013],"force_p95":74.67283,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":259.34718,"mean_force":71.23675,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46418,-0.04795,0.16542]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.63034,-0.01242,-0.00014],"force_p95":78.79244,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.34355,"mean_force":58.34793,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62843,0.00272,0.2938]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.45597,-0.01626,0.03962],"force_p95":3.61849,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.9772,"mean_force":1.70076,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.38371,-0.0026,0.05137]},{"body_a":"world","body_b":"grasp_target","contact_count":3935.0,"contact_point_centroid":[0.44034,-0.01935,-0.00213],"force_p95":0.13731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3102,"mean_force":0.13797,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.40945,-0.00604,0.14398]},{"body_a":"grasp_target","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.48183,-0.00499,0.01096],"force_p95":0.63609,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68448,"mean_force":0.25963,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.37339,-0.00265,0.05266]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43543,-0.01923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.42811,-0.01828,0.19472]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.43543,-0.01923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46418,-0.04795,0.16543]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.43543,-0.01923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44518,0.07811,0.14856]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43543,-0.01923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54663,-0.01912,0.26977]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43543,-0.01923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.61448,-0.03292,0.29363]}],"total_contact_groups":23},"final_pose_error":0.01484,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43543,-0.01923,0.01602],"final_tcp_position":[0.62928,0.00146,0.41452],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1445.22025,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":202.2407,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4908.0,"raw_peak_contact_force":1445.22025,"subtask_id":"reach_object","tcp_end":[0.41888,-0.01286,0.18],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16493,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.43543,-0.01923,0.01602],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.31705,"object_z_max":0.01602,"peak_contact_force":487.96256,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4970.0,"raw_peak_contact_force":919.39525,"subtask_id":"reach_object","tcp_end":[0.46417,-0.04713,0.1667],"tcp_start":[0.41888,-0.01286,0.18],"tcp_to_object_dist_end":0.15592,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.43543,-0.01923,0.01602],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.31705,"object_z_max":0.01602,"peak_contact_force":68.6682,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2594.0,"raw_peak_contact_force":259.34718,"tcp_end":[0.46416,-0.04795,0.1653],"tcp_start":[0.46417,-0.04713,0.1667],"tcp_to_object_dist_end":0.15471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":487.0,"n_steps_budget":600.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.43543,-0.01923,0.01602],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.31705,"object_z_max":0.01602,"peak_contact_force":220.49301,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4454.0,"raw_peak_contact_force":417.13245,"tcp_end":[0.44622,0.12637,0.13343],"tcp_start":[0.46416,-0.04795,0.1653],"tcp_to_object_dist_end":0.18735,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.43543,-0.01923,0.01602],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.31705,"object_z_max":0.01602,"peak_contact_force":315.58614,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9404.0,"raw_peak_contact_force":747.01249,"subtask_id":"place_goal","tcp_end":[0.6028,-0.06304,0.29339],"tcp_start":[0.44622,0.12637,0.13343],"tcp_to_object_dist_end":0.3269,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.43543,-0.01923,0.01602],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.31705,"object_z_max":0.01602,"peak_contact_force":320.87908,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9354.0,"raw_peak_contact_force":484.88734,"subtask_id":"place_goal","tcp_end":[0.62847,0.00288,0.2935],"tcp_start":[0.6028,-0.06304,0.29339],"tcp_to_object_dist_end":0.33874,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.43543,-0.01923,0.01602],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.31705,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1116.0,"raw_peak_contact_force":90.34355,"tcp_end":[0.62859,0.00249,0.31993],"tcp_start":[0.62847,0.00288,0.2935],"tcp_to_object_dist_end":0.36076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":600.0,"object_pos_end":[0.43543,-0.01923,0.01602],"object_pos_start":[0.43543,-0.01923,0.01602],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.31705,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62928,0.00146,0.41452],"tcp_start":[0.62859,0.00249,0.31993],"tcp_to_object_dist_end":0.44363,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```