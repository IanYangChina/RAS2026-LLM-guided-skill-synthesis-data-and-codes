## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2787 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.2513 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1062 | 0.17 | ❌ rejected |
| 6 | approach → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | -0.1408 | 0.17 | ❌ rejected |
| 5 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1713 | 0.18 | ❌ rejected |

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

## Current Skill (Q=-0.279) — your mutation base

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

- **Composite score**: -0.279
- **task_score** (E): 0.171
- **fitness_score**: 0.226  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_grasp | 1.00 | 1.00 | 0.1552 |
| descend_grasp | 1.00 | 1.00 | 0.0216 |
| grasp | 1.00 | 1.00 | 0.0432 |
| lift | 1.00 | 1.00 | 0.1302 |
| transport | 1.00 | 1.00 | 0.2235 |
| descend_place | 0.00 | 1.00 | 0.0073 |
| release | 1.00 | 1.00 | 0.0228 |
| retract | 1.00 | 1.00 | 0.0802 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.149) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.494, 0.001, 0.149)→(0.508, -0.010, 0.137) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 519.337 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.508, -0.010, 0.137)→(0.496, -0.017, 0.097) | (0.497, 0.001, 0.026)→(0.496, 0.000, 0.026) | 0.265→0.266 | 1.00 / 8.000 | 0.123 | 0.468 |
| lift | lift | 1.00 / step_budget | (0.496, -0.017, 0.097)→(0.493, -0.017, 0.227) | (0.496, 0.000, 0.026)→(0.496, 0.000, 0.026) | 0.266→0.266 | 1.00 / 8.333 | 0.123 | 0.123 |
| transport | approach | 1.00 / step_budget | (0.493, -0.017, 0.227)→(0.575, 0.172, 0.275) | (0.496, 0.000, 0.026)→(0.496, 0.000, 0.026) | 0.266→0.266 | 1.00 / 8.000 | 0.123 | 0.123 |
| descend_place | descend | 0.00 / step_budget | (0.575, 0.172, 0.275)→(0.580, 0.174, 0.270) | (0.496, 0.000, 0.026)→(0.496, 0.000, 0.026) | 0.266→0.266 | 1.00 / 8.333 | 110.967 | 638.334 |
| release | release | 1.00 / step_budget | (0.580, 0.174, 0.270)→(0.578, 0.173, 0.293) | (0.496, 0.000, 0.026)→(0.496, 0.000, 0.026) | 0.266→0.266 | 1.00 / 4.000 | 0.123 | 30.791 |
| retract | retract | 1.00 / step_budget | (0.578, 0.173, 0.293)→(0.577, 0.173, 0.373) | (0.496, 0.000, 0.026)→(0.496, 0.000, 0.026) | 0.266→0.266 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.197
- phase_score: 0.388
- phase_breakdown.grasp_quality_score: 0.279
- phase_breakdown.reach_grasp_score: 0.675
- phase_breakdown.lift_height_score: 0.312
- phase_breakdown.place_accuracy_score: 0.000
- phase_breakdown.approach_place_score: 0.673
- grasp_place_fitness: 0.268

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.268
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.197
- **Median Q (composite search score)**: -0.287
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27734,"average_solve_count":256.0,"average_success_count":256.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.speed":0.02175,"descend_grasp.descend_force":1.52764,"descend_grasp.speed":0.01001,"descend_place.speed":0.03294,"lift.lift_height":0.10775,"lift.speed":0.0938,"release.release_wait":1.56867,"retract.speed":0.05067,"transport.speed":0.0224},"optimized_scores":{"best_composite_score":-0.28706,"best_fitness_score":0.21794,"best_task_score":0.17014},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":731.0,"contact_point_centroid":[0.56293,0.13087,-0.00056],"force_p95":601.08354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1915.00285,"mean_force":419.83193,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55586,0.15622,0.28545]},{"body_a":"world","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.5769,0.13981,-0.00017],"force_p95":91.72519,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.12835,"mean_force":63.34645,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56389,0.14591,0.29379]},{"body_a":"world","body_b":"grasp_target","contact_count":3460.0,"contact_point_centroid":[0.5136,-0.02307,-0.00204],"force_p95":0.15393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17714,"mean_force":0.12592,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54707,0.16446,0.27541]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.5137,-0.02302,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.50325,-0.00938,0.22604]},{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50998,-0.01962,0.14589]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50525,-0.02101,0.12171]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50089,-0.02085,0.16343]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52367,0.06065,0.25661]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51355,-0.02309,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56393,0.14579,0.30039]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.51355,-0.02309,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56456,0.14541,0.36034]},{"body_a":"grasp_target","body_b":"link5","contact_count":182.0,"contact_point_centroid":[0.53388,-0.00202,0.05447],"force_p95":0.08513,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08578,"mean_force":0.06476,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56026,0.14,0.29353]},{"body_a":"left_finger","body_b":"right_finger","contact_count":339.0,"contact_point_centroid":[0.50426,-0.02094,0.12226],"force_p95":0.01366,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01116,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50396,-0.02093,0.12031]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3692.0,"contact_point_centroid":[0.54764,0.16399,0.27384],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54729,0.16429,0.27566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1208.0,"contact_point_centroid":[0.50115,-0.02086,0.16555],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01045,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5009,-0.02085,0.16325]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.56444,0.14592,0.29117],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56392,0.14598,0.29373]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2778.0,"contact_point_centroid":[0.52385,0.06023,0.2585],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01037,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52354,0.06024,0.25635]}],"total_contact_groups":16},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.51355,-0.02309,0.02602],"final_tcp_position":[0.56502,0.14525,0.40102],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1915.00285,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp","tcp_end":[0.50835,-0.01965,0.14848],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_quality","tcp_end":[0.51371,-0.02033,0.14196],"tcp_start":[0.50835,-0.01965,0.14848],"tcp_to_object_dist_end":0.11597,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2139.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_quality","tcp_end":[0.50396,-0.02093,0.12031],"tcp_start":[0.51371,-0.02033,0.14196],"tcp_to_object_dist_end":0.09481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":283.0,"n_steps_budget":600.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2340.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_height","tcp_end":[0.5008,-0.02085,0.20856],"tcp_start":[0.50396,-0.02093,0.12031],"tcp_to_object_dist_end":0.18301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5362.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_place","tcp_end":[0.54848,0.13952,0.30741],"tcp_start":[0.5008,-0.02085,0.20856],"tcp_to_object_dist_end":0.32681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.51355,-0.02309,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26567,"object_to_goal_dist_start":0.26561,"object_z_max":0.02603,"peak_contact_force":332.65696,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8065.0,"raw_peak_contact_force":1915.00285,"subtask_id":"place_accuracy","tcp_end":[0.56391,0.14611,0.29347],"tcp_start":[0.54848,0.13952,0.30741],"tcp_to_object_dist_end":0.32046,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51355,-0.02309,0.02602],"object_pos_start":[0.51355,-0.02309,0.02602],"object_to_goal_dist_end":0.26567,"object_to_goal_dist_start":0.26567,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1102.0,"raw_peak_contact_force":92.12835,"tcp_end":[0.5641,0.1457,0.32079],"tcp_start":[0.56391,0.14611,0.29347],"tcp_to_object_dist_end":0.34342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":630.0,"object_pos_end":[0.51355,-0.02309,0.02602],"object_pos_start":[0.51355,-0.02309,0.02602],"object_to_goal_dist_end":0.26567,"object_to_goal_dist_start":0.26567,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56502,0.14525,0.40102],"tcp_start":[0.5641,0.1457,0.32079],"tcp_to_object_dist_end":0.41426,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":34.0,"average_failure_rate":0.21118,"average_mean_iterations":45.4472,"average_solve_count":161.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.speed":0.05565,"descend_grasp.descend_force":3.67462,"descend_grasp.speed":0.03671,"descend_place.speed":0.02801,"lift.lift_height":0.16107,"lift.speed":0.05813,"release.release_wait":1.00154,"retract.speed":0.12721,"transport.speed":0.0694},"optimized_scores":{"best_composite_score":-0.2374,"best_fitness_score":0.2676,"best_task_score":0.19724},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":681.0,"contact_point_centroid":[0.51466,0.02705,0.03066],"force_p95":0.17665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.15732,"mean_force":0.08092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51498,-0.01167,0.03565]},{"body_a":"world","body_b":"grasp_target","contact_count":1611.0,"contact_point_centroid":[0.4986,0.04216,-0.00251],"force_p95":0.37111,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64266,"mean_force":0.16376,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51906,-0.0122,0.04106]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.49837,0.01853,0.22536]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.4995,0.04362,-0.00199],"force_p95":0.12267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12305,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51137,-0.01227,0.10533]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50919,0.02935,0.13819]},{"body_a":"world","body_b":"grasp_target","contact_count":2844.0,"contact_point_centroid":[0.4995,0.04362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5343,0.11136,0.20443]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4995,0.04362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55581,0.22896,0.23616]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.4995,0.04362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55319,0.22777,0.29532]},{"body_a":"left_finger","body_b":"right_finger","contact_count":337.0,"contact_point_centroid":[0.51609,-0.01213,0.03808],"force_p95":0.01374,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01472,"mean_force":0.01087,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51522,-0.01221,0.03549]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3127.0,"contact_point_centroid":[0.5351,0.11097,0.20658],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01017,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53421,0.1109,0.20432]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2031.0,"contact_point_centroid":[0.51222,-0.01221,0.10755],"force_p95":0.01085,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01257,"mean_force":0.01011,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51137,-0.01227,0.10531]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.55854,0.23004,0.23445],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55774,0.22996,0.23239]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.4995,0.04362,0.02602],"final_tcp_position":[0.55338,0.22782,0.33591],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":711.17665,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp","tcp_end":[0.49786,0.03849,0.1482],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":711.17665,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":96.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_quality","tcp_end":[0.53425,0.00769,0.1234],"tcp_start":[0.49786,0.03849,0.1482],"tcp_to_object_dist_end":0.10942,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49948,0.0436,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24353,"object_to_goal_dist_start":0.24188,"object_z_max":0.02649,"peak_contact_force":0.12268,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2629.0,"raw_peak_contact_force":1.15732,"subtask_id":"grasp_quality","tcp_end":[0.51522,-0.01221,0.03549],"tcp_start":[0.53425,0.00769,0.1234],"tcp_to_object_dist_end":0.05875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":459.0,"n_steps_budget":870.0,"object_pos_end":[0.4995,0.04362,0.02602],"object_pos_start":[0.49948,0.0436,0.02602],"object_to_goal_dist_end":0.2435,"object_to_goal_dist_start":0.24353,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3867.0,"raw_peak_contact_force":0.12305,"subtask_id":"lift_height","tcp_end":[0.51172,-0.01223,0.17709],"tcp_start":[0.51522,-0.01221,0.03549],"tcp_to_object_dist_end":0.16153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.4995,0.04362,0.02602],"object_pos_start":[0.4995,0.04362,0.02602],"object_to_goal_dist_end":0.2435,"object_to_goal_dist_start":0.2435,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5971.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_place","tcp_end":[0.559,0.22975,0.23517],"tcp_start":[0.51172,-0.01223,0.17709],"tcp_to_object_dist_end":0.28623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.4995,0.04362,0.02602],"object_pos_start":[0.4995,0.04362,0.02602],"object_to_goal_dist_end":0.2435,"object_to_goal_dist_start":0.2435,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_accuracy","tcp_end":[0.559,0.22975,0.23517],"tcp_start":[0.559,0.22975,0.23517],"tcp_to_object_dist_end":0.28623,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4995,0.04362,0.02602],"object_pos_start":[0.4995,0.04362,0.02602],"object_to_goal_dist_end":0.2435,"object_to_goal_dist_start":0.2435,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55474,0.22844,0.25581],"tcp_start":[0.559,0.22975,0.23517],"tcp_to_object_dist_end":0.30002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":600.0,"object_pos_end":[0.4995,0.04362,0.02602],"object_pos_start":[0.4995,0.04362,0.02602],"object_to_goal_dist_end":0.2435,"object_to_goal_dist_start":0.2435,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55338,0.22782,0.33591],"tcp_start":[0.55474,0.22844,0.25581],"tcp_to_object_dist_end":0.36451,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":36.0,"average_failure_rate":0.23226,"average_mean_iterations":49.69677,"average_solve_count":155.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.speed":0.08643,"descend_grasp.descend_force":7.39317,"descend_grasp.speed":0.02108,"descend_place.speed":0.02742,"lift.lift_height":0.18039,"lift.speed":0.05462,"release.release_wait":1.22068,"retract.speed":0.11106,"transport.speed":0.06598},"optimized_scores":{"best_composite_score":-0.31162,"best_fitness_score":0.19338,"best_task_score":0.14623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.48819,-0.00824,0.22625]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47663,-0.01722,0.14842]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47045,-0.01752,0.13666]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46673,-0.01742,0.21517]},{"body_a":"world","body_b":"grasp_target","contact_count":2308.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54222,0.06474,0.2877]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61537,0.14577,0.28295]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61327,0.14493,0.34199]},{"body_a":"left_finger","body_b":"right_finger","contact_count":328.0,"contact_point_centroid":[0.4698,-0.01749,0.13774],"force_p95":0.0143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01149,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46947,-0.01749,0.13556]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2067.0,"contact_point_centroid":[0.46696,-0.01742,0.21749],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01062,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46673,-0.01742,0.21523]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2469.0,"contact_point_centroid":[0.5425,0.06474,0.28999],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54221,0.06474,0.2877]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.61758,0.14649,0.28163],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61704,0.14648,0.27943]}],"total_contact_groups":11},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47616,-0.02015,0.02602],"final_tcp_position":[0.61356,0.14493,0.3826],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":765.69178,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp","tcp_end":[0.47652,-0.01715,0.14931],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":765.69178,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_quality","tcp_end":[0.47717,-0.01754,0.14679],"tcp_start":[0.47652,-0.01715,0.14931],"tcp_to_object_dist_end":0.1208,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_quality","tcp_end":[0.46947,-0.01749,0.13555],"tcp_start":[0.47717,-0.01754,0.14679],"tcp_to_object_dist_end":0.10977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4039.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_height","tcp_end":[0.46716,-0.01743,0.29623],"tcp_start":[0.46947,-0.01749,0.13555],"tcp_to_object_dist_end":0.27037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4777.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_place","tcp_end":[0.61804,0.14622,0.28277],"tcp_start":[0.46716,-0.01743,0.29623],"tcp_to_object_dist_end":0.33724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_accuracy","tcp_end":[0.61804,0.14622,0.28277],"tcp_start":[0.61804,0.14622,0.28277],"tcp_to_object_dist_end":0.33724,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6145,0.1454,0.3024],"tcp_start":[0.61804,0.14622,0.28277],"tcp_to_object_dist_end":0.35061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61356,0.14493,0.3826],"tcp_start":[0.6145,0.1454,0.3024],"tcp_to_object_dist_end":0.41627,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```