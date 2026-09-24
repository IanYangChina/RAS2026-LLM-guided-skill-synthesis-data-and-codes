## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.2710 | 0.20 | ❌ rejected |
| 4 | approach → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.1221 | 0.17 | ❌ rejected |
| 3 | approach → grasp → approach → release → retract | linear_cartesian | — | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 1 | 0.1840 | 0.19 | ❌ rejected |
| 2 | approach → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.0797 | 0.17 | ✅ accepted |
| 1 | approach → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0488 | 0.17 | ✅ accepted |

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

## Current Skill (Q=0.271) — your mutation base

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

- **Composite score**: 0.271
- **task_score** (E): 0.200
- **fitness_score**: 0.551  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1549 |
| descend_to_grasp | 1.00 | 1.00 | 0.0845 |
| grasp_object | 1.00 | 1.00 | 0.0116 |
| lift_object | 1.00 | 1.00 | 0.1203 |
| move_to_goal | 1.00 | 1.00 | 0.2261 |
| descend_to_place | 1.00 | 1.00 | 0.0940 |
| release_object | 1.00 | 1.00 | 0.0214 |
| retract_from_goal | 1.00 | 1.00 | 0.0529 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.149) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.494, 0.001, 0.149)→(0.492, 0.001, 0.065) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.065)→(0.485, 0.000, 0.056) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 27.667 | 0.148 | 0.195 |
| lift_object | lift | 1.00 / step_budget | (0.485, 0.000, 0.056)→(0.481, 0.000, 0.176) | (0.497, 0.001, 0.026)→(0.488, 0.000, 0.140) | 0.266→0.219 | 1.00 / 13.667 | 525.951 | 0.304 |
| move_to_goal | approach | 1.00 / step_budget | (0.481, 0.000, 0.176)→(0.574, 0.169, 0.287) | (0.488, 0.000, 0.140)→(0.504, 0.039, 0.016) | 0.219→0.242 | 1.00 / 8.333 | 94254.658 | 1.503 |
| descend_to_place | approach | 1.00 / step_budget | (0.574, 0.169, 0.287)→(0.578, 0.182, 0.194) | (0.504, 0.039, 0.016)→(0.504, 0.039, 0.016) | 0.242→0.242 | 1.00 / 8.333 | 94251.724 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.578, 0.182, 0.194)→(0.573, 0.180, 0.215) | (0.504, 0.039, 0.016)→(0.504, 0.039, 0.016) | 0.242→0.242 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 1.00 / step_budget | (0.573, 0.180, 0.215)→(0.579, 0.183, 0.267) | (0.504, 0.039, 0.016)→(0.504, 0.039, 0.016) | 0.242→0.242 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.230
- phase_score: 0.287
- phase_breakdown.reach_goal_score: 0.121
- phase_breakdown.reach_object_score: 0.674
- grasp_place_fitness: 0.566

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.566
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.230
- **Median Q (composite search score)**: 0.267
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Parameters at lower bound**: move_to_goal.arc_height
- **Final σ (mean)**: 0.162


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89503,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_object.lift_height":0.18174,"move_to_goal.arc_height":0.14273},"optimized_scores":{"best_composite_score":0.26683,"best_fitness_score":0.54683,"best_task_score":0.19024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.51545,0.0172,-0.00253],"force_p95":0.13825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66553,"mean_force":0.14618,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.51529,0.03843,0.3174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5216.0,"contact_point_centroid":[0.50044,-0.04047,0.12649],"force_p95":0.14413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31486,"mean_force":0.09895,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49706,-0.02211,0.13013]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.51155,-0.0221,-0.00136],"force_p95":0.27317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29129,"mean_force":0.06378,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49936,-0.02219,0.05659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5195.0,"contact_point_centroid":[0.50036,-0.00373,0.12556],"force_p95":0.1385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27214,"mean_force":0.09874,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49707,-0.02211,0.12906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.50356,-0.00625,0.2151],"force_p95":0.2243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25931,"mean_force":0.12865,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49661,-0.02243,0.22]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.50433,-0.03996,0.2114],"force_p95":0.20452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21158,"mean_force":0.13053,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49721,-0.02216,0.2178]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51372,-0.023,-0.00206],"force_p95":0.14121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18493,"mean_force":0.12749,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50176,-0.02225,0.05652]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.5137,-0.02302,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.50355,-0.00943,0.22584]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50733,-0.02096,0.10593]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.5155,0.01731,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.54791,0.14069,0.27828]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5155,0.01731,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54663,0.14724,0.23192]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.5155,0.01731,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.54722,0.14832,0.27668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3097.0,"contact_point_centroid":[0.50046,-0.00345,0.05223],"force_p95":0.08882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10598,"mean_force":0.06642,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50062,-0.02222,0.05524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2962.0,"contact_point_centroid":[0.50088,-0.04105,0.05199],"force_p95":0.09318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09349,"mean_force":0.07028,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50062,-0.02222,0.05524]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2331.0,"contact_point_centroid":[0.5168,0.04166,0.32288],"force_p95":0.01147,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01575,"mean_force":0.01054,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.51638,0.04166,0.32053]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1180.0,"contact_point_centroid":[0.54841,0.14068,0.28057],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.5479,0.14068,0.27836]}],"total_contact_groups":17},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.5155,0.01731,0.01602],"final_tcp_position":[0.55031,0.15009,0.30258],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":273015.05549,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1160.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50858,-0.0196,0.14896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50856,-0.0224,0.06431],"tcp_start":[0.50858,-0.0196,0.14896],"tcp_to_object_dist_end":0.03864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51364,-0.02255,0.02577],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26549,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.1401,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7859.0,"raw_peak_contact_force":0.18493,"tcp_end":[0.50059,-0.02222,0.0552],"tcp_start":[0.50856,-0.0224,0.06431],"tcp_to_object_dist_end":0.0322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.50522,-0.0224,0.18022],"object_pos_start":[0.51364,-0.02255,0.02577],"object_to_goal_dist_end":0.18555,"object_to_goal_dist_start":0.26549,"object_z_max":0.18002,"peak_contact_force":1577.56067,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10488.0,"raw_peak_contact_force":0.31486,"tcp_end":[0.49741,-0.02212,0.21722],"tcp_start":[0.50059,-0.02222,0.0552],"tcp_to_object_dist_end":0.03781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.5155,0.01731,0.01602],"object_pos_start":[0.50522,-0.0224,0.18022],"object_to_goal_dist_end":0.24892,"object_to_goal_dist_start":0.18555,"object_z_max":0.18115,"peak_contact_force":273015.05549,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4835.0,"raw_peak_contact_force":1.66553,"subtask_id":"reach_goal","tcp_end":[0.54693,0.1338,0.32655],"tcp_start":[0.49741,-0.02212,0.21722],"tcp_to_object_dist_end":0.33315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.5155,0.01731,0.01602],"object_pos_start":[0.5155,0.01731,0.01602],"object_to_goal_dist_end":0.24892,"object_to_goal_dist_start":0.24892,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5502,0.14821,0.23023],"tcp_start":[0.54693,0.1338,0.32655],"tcp_to_object_dist_end":0.25343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5155,0.01731,0.01602],"object_pos_start":[0.5155,0.01731,0.01602],"object_to_goal_dist_end":0.24892,"object_to_goal_dist_start":0.24892,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54544,0.14685,0.25222],"tcp_start":[0.5502,0.14821,0.23023],"tcp_to_object_dist_end":0.27105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":600.0,"object_pos_end":[0.5155,0.01731,0.01602],"object_pos_start":[0.5155,0.01731,0.01602],"object_to_goal_dist_end":0.24892,"object_to_goal_dist_start":0.24892,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":760.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55031,0.15009,0.30258],"tcp_start":[0.54544,0.14685,0.25222],"tcp_to_object_dist_end":0.31774,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89143,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_object.lift_height":0.1286,"move_to_goal.arc_height":0.19527},"optimized_scores":{"best_composite_score":0.28618,"best_fitness_score":0.56618,"best_task_score":0.23038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2437.0,"contact_point_centroid":[0.48612,0.08573,-0.00236],"force_p95":0.1288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26147,"mean_force":0.13959,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.51612,0.12764,0.25039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.48909,0.0255,0.16209],"force_p95":0.27623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35124,"mean_force":0.15095,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48466,0.04324,0.16763]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.49897,0.0427,-0.00143],"force_p95":0.26848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30276,"mean_force":0.06241,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48736,0.04288,0.0573]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.48705,0.06095,0.09873],"force_p95":0.16545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29664,"mean_force":0.11453,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48517,0.04268,0.10294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.48619,0.02454,0.09927],"force_p95":0.15543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28711,"mean_force":0.10548,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48515,0.04268,0.10331]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":293.0,"contact_point_centroid":[0.48897,0.06055,0.16492],"force_p95":0.16678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2545,"mean_force":0.08364,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48457,0.04381,0.16968]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04497,-0.00214],"force_p95":0.16566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21845,"mean_force":0.13297,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48976,0.04311,0.05698]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.4984,0.01855,0.2253]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49594,0.04097,0.10572]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.48608,0.08595,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55664,0.23349,0.20173]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48608,0.08595,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55513,0.23873,0.15496]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.48608,0.08595,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.55587,0.23985,0.20063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2653.0,"contact_point_centroid":[0.48785,0.02424,0.05234],"force_p95":0.09831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11861,"mean_force":0.0764,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48864,0.04301,0.05575]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3085.0,"contact_point_centroid":[0.48859,0.06178,0.05247],"force_p95":0.09516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09561,"mean_force":0.06771,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48865,0.04301,0.05576]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2344.0,"contact_point_centroid":[0.51967,0.13561,0.25775],"force_p95":0.01118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01055,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5193,0.13559,0.25542]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1162.0,"contact_point_centroid":[0.5571,0.23351,0.20408],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55664,0.23348,0.20181]}],"total_contact_groups":17},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.48608,0.08595,0.01602],"final_tcp_position":[0.55978,0.24235,0.22753],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9749.00417,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4979,0.03848,0.14828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49641,0.04369,0.06443],"tcp_start":[0.4979,0.03848,0.14828],"tcp_to_object_dist_end":0.03873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04378,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2432,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16235,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7538.0,"raw_peak_contact_force":0.21845,"tcp_end":[0.48861,0.04301,0.05572],"tcp_start":[0.49641,0.04369,0.06443],"tcp_to_object_dist_end":0.03273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":345.0,"n_steps_budget":810.0,"object_pos_end":[0.4906,0.04305,0.12791],"object_pos_start":[0.50116,0.04378,0.0255],"object_to_goal_dist_end":0.21571,"object_to_goal_dist_start":0.2432,"object_z_max":0.12764,"peak_contact_force":0.15436,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6304.0,"raw_peak_contact_force":0.30276,"tcp_end":[0.48508,0.04267,0.1649],"tcp_start":[0.48861,0.04301,0.05572],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.48608,0.08595,0.01602],"object_pos_start":[0.4906,0.04305,0.12791],"object_to_goal_dist_end":0.2202,"object_to_goal_dist_start":0.21571,"object_z_max":0.13243,"peak_contact_force":9748.79463,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5235.0,"raw_peak_contact_force":1.26147,"subtask_id":"reach_goal","tcp_end":[0.55566,0.22729,0.25045],"tcp_start":[0.48508,0.04267,0.1649],"tcp_to_object_dist_end":0.28245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.48608,0.08595,0.01602],"object_pos_start":[0.48608,0.08595,0.01602],"object_to_goal_dist_end":0.2202,"object_to_goal_dist_start":0.2202,"object_z_max":0.01602,"peak_contact_force":9749.00417,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2254.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5595,0.24065,0.15413],"tcp_start":[0.55566,0.22729,0.25045],"tcp_to_object_dist_end":0.22,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48608,0.08595,0.01602],"object_pos_start":[0.48608,0.08595,0.01602],"object_to_goal_dist_end":0.2202,"object_to_goal_dist_start":0.2202,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55358,0.23798,0.17491],"tcp_start":[0.5595,0.24065,0.15413],"tcp_to_object_dist_end":0.23004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.48608,0.08595,0.01602],"object_pos_start":[0.48608,0.08595,0.01602],"object_to_goal_dist_end":0.2202,"object_to_goal_dist_start":0.2202,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":852.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55978,0.24235,0.22753],"tcp_start":[0.55358,0.23798,0.17491],"tcp_to_object_dist_end":0.27319,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89385,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_object.lift_height":0.10916,"move_to_goal.arc_height":0.05},"optimized_scores":{"best_composite_score":0.25999,"best_fitness_score":0.53999,"best_task_score":0.17968},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2365.0,"contact_point_centroid":[0.50917,0.01387,-0.00244],"force_p95":0.12972,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58119,"mean_force":0.1434,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54958,0.07571,0.26299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2867.0,"contact_point_centroid":[0.46196,-0.00078,0.09384],"force_p95":0.14608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29572,"mean_force":0.09993,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46125,-0.01933,0.09806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3200.0,"contact_point_centroid":[0.46219,-0.03774,0.0938],"force_p95":0.13673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29282,"mean_force":0.09122,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46127,-0.01933,0.09791]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.4742,-0.01891,-0.00135],"force_p95":0.2664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28256,"mean_force":0.06218,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46336,-0.0194,0.0585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1601.0,"contact_point_centroid":[0.47419,-0.02604,0.16796],"force_p95":0.13686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22902,"mean_force":0.10262,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.46911,-0.00817,0.17257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1418.0,"contact_point_centroid":[0.47377,0.00939,0.16651],"force_p95":0.15191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22444,"mean_force":0.11504,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.46856,-0.00876,0.17138]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.0201,-0.00205],"force_p95":0.14117,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18225,"mean_force":0.12696,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46563,-0.01945,0.05822]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48821,-0.00823,0.22635]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47321,-0.01832,0.10676]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.50921,0.01398,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.62101,0.15069,0.24075]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50921,0.01398,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62163,0.15481,0.19711]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.50921,0.01398,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.62306,0.15586,0.24309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.46407,-0.0006,0.05333],"force_p95":0.09752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10629,"mean_force":0.07663,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46456,-0.01943,0.05711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3200.0,"contact_point_centroid":[0.46483,-0.03811,0.05355],"force_p95":0.08763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08799,"mean_force":0.0648,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46456,-0.01943,0.05711]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2319.0,"contact_point_centroid":[0.55459,0.08057,0.26886],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01538,"mean_force":0.01052,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55427,0.08056,0.26655]},{"body_a":"left_finger","body_b":"right_finger","contact_count":994.0,"contact_point_centroid":[0.62137,0.15069,0.24319],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.621,0.15068,0.24086]}],"total_contact_groups":17},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50921,0.01398,0.01602],"final_tcp_position":[0.6273,0.15768,0.27067],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273006.04394,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47667,-0.01712,0.14971],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47209,-0.0196,0.06496],"tcp_start":[0.47667,-0.01712,0.14971],"tcp_to_object_dist_end":0.03916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01959,0.02579],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14042,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7667.0,"raw_peak_contact_force":0.18225,"tcp_end":[0.46453,-0.01942,0.05708],"tcp_start":[0.47209,-0.0196,0.06496],"tcp_to_object_dist_end":0.03336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":276.0,"n_steps_budget":690.0,"object_pos_end":[0.46876,-0.0196,0.11054],"object_pos_start":[0.4761,-0.01959,0.02579],"object_to_goal_dist_end":0.25444,"object_to_goal_dist_start":0.2882,"object_z_max":0.11026,"peak_contact_force":0.13884,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6141.0,"raw_peak_contact_force":0.29572,"tcp_end":[0.461,-0.01931,0.14671],"tcp_start":[0.46453,-0.01942,0.05708],"tcp_to_object_dist_end":0.037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":867.0,"n_steps_budget":1000.0,"object_pos_end":[0.50921,0.01398,0.01602],"object_pos_start":[0.46876,-0.0196,0.11054],"object_to_goal_dist_end":0.25748,"object_to_goal_dist_start":0.25444,"object_z_max":0.15618,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7703.0,"raw_peak_contact_force":1.58119,"subtask_id":"reach_goal","tcp_end":[0.61798,0.14612,0.28379],"tcp_start":[0.461,-0.01931,0.14671],"tcp_to_object_dist_end":0.31779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.50921,0.01398,0.01602],"object_pos_start":[0.50921,0.01398,0.01602],"object_to_goal_dist_end":0.25748,"object_to_goal_dist_start":0.25748,"object_z_max":0.01602,"peak_contact_force":273006.04394,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1926.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62573,0.15594,0.19753],"tcp_start":[0.61798,0.14612,0.28379],"tcp_to_object_dist_end":0.25822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50921,0.01398,0.01602],"object_pos_start":[0.50921,0.01398,0.01602],"object_to_goal_dist_end":0.25748,"object_to_goal_dist_start":0.25748,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62021,0.15435,0.21651],"tcp_start":[0.62573,0.15594,0.19753],"tcp_to_object_dist_end":0.26874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":600.0,"object_pos_end":[0.50921,0.01398,0.01602],"object_pos_start":[0.50921,0.01398,0.01602],"object_to_goal_dist_end":0.25748,"object_to_goal_dist_start":0.25748,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":932.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6273,0.15768,0.27067],"tcp_start":[0.62021,0.15435,0.21651],"tcp_to_object_dist_end":0.31535,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```