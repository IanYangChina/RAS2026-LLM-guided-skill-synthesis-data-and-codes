## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2605 | 0.32 | ✅ accepted |
| 6 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.3101 | 0.22 | ✅ accepted |
| 5 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.2710 | 0.20 | ❌ rejected |
| 4 | approach → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.1221 | 0.17 | ❌ rejected |
| 3 | approach → grasp → approach → release → retract | linear_cartesian | — | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 1 | 0.1840 | 0.19 | ❌ rejected |

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

## Current Skill (Q=0.261) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.7
phases:
- id: approach_above
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
    - 0.1
    orientation:
      mode: none
  subtask_id: reach_object
- id: descend_to_grasp
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
      mode: none
  guards:
  - id: contact_detected
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: grasp
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
  guards:
  - id: bilateral_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.003
- id: lift
  type: lift
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
    - 0.25
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: move_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: none
  parameters:
    goal_offset_z:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    move_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
  type: approach
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
    orientation:
      mode: none
  subtask_id: reach_goal
- id: release
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
- id: retract
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
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings: none
- **descend_to_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=contact_detected, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - goal_offset_z: status=consumed; consumers=target.offset.z (replace)
    - move_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.261
- **task_score** (E): 0.325
- **fitness_score**: 0.641  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1655 |
| descend_to_grasp | 1.00 | 1.00 | 0.1043 |
| grasp | 1.00 | 1.00 | 0.0124 |
| lift | 0.00 | 1.00 | 0.0989 |
| move_to_goal | 0.00 | 1.00 | 0.0893 |
| descend_to_place | 0.67 | 1.00 | 0.1206 |
| release | 1.00 | 1.00 | 0.0228 |
| retract | 1.00 | 1.00 | 0.0424 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.139) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.493, 0.001, 0.139)→(0.492, 0.001, 0.034) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.492, 0.001, 0.034)→(0.483, 0.000, 0.025) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.333 | 0.146 | 0.190 |
| lift | lift | 0.00 / step_budget | (0.483, 0.000, 0.025)→(0.485, 0.000, 0.124) | (0.497, 0.000, 0.026)→(0.496, 0.000, 0.114) | 0.266→0.224 | 1.00 / 37.000 | 0.088 | 0.643 |
| move_to_goal | approach | 0.00 / step_budget | (0.485, 0.000, 0.124)→(0.510, 0.057, 0.187) | (0.496, 0.000, 0.114)→(0.517, 0.058, 0.170) | 0.224→0.150 | 1.00 / 30.333 | 0.090 | 0.108 |
| descend_to_place | approach | 0.67 / step_budget | (0.510, 0.057, 0.187)→(0.562, 0.160, 0.180) | (0.517, 0.058, 0.170)→(0.562, 0.162, 0.157) | 0.150→0.047 | 1.00 / 33.333 | 0.120 | 0.178 |
| release | release | 1.00 / step_budget | (0.562, 0.160, 0.180)→(0.556, 0.159, 0.202) | (0.562, 0.162, 0.157)→(0.559, 0.160, 0.017) | 0.047→0.174 | 1.00 / 3.000 | 0.139 | 1.586 |
| retract | retract | 1.00 / step_budget | (0.556, 0.159, 0.202)→(0.578, 0.182, 0.226) | (0.559, 0.160, 0.017)→(0.557, 0.160, 0.019) | 0.174→0.172 | 1.00 / 4.000 | 0.123 | 0.208 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.425
- phase_score: 0.056
- phase_breakdown.reach_goal_score: 0.016
- phase_breakdown.reach_object_score: 0.147
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.425
- **Median Q (composite search score)**: 0.248
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.143


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49143,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.22859,"lift.lift_speed":0.06027,"move_to_goal.goal_offset_z":0.12851,"move_to_goal.move_speed":0.06755},"optimized_scores":{"best_composite_score":0.22318,"best_fitness_score":0.60318,"best_task_score":0.25156},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.5505,0.12983,-0.00801],"force_p95":1.48904,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83806,"mean_force":0.47734,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54177,0.13758,0.22804]},{"body_a":"world","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.50995,-0.0222,-0.00114],"force_p95":0.45326,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65919,"mean_force":0.10606,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49766,-0.0225,0.02629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20501.0,"contact_point_centroid":[0.49989,-0.00357,0.07346],"force_p95":0.0763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2833,"mean_force":0.05048,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49814,-0.02253,0.07193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49901,-0.04172,0.07549],"force_p95":0.08092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27859,"mean_force":0.05883,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49818,-0.02253,0.07284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":563.0,"contact_point_centroid":[0.55267,0.1219,0.20316],"force_p95":0.1398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26036,"mean_force":0.08932,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54496,0.13852,0.20848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":414.0,"contact_point_centroid":[0.54612,0.15739,0.20604],"force_p95":0.15211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26022,"mean_force":0.11151,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.545,0.13853,0.20854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12226.0,"contact_point_centroid":[0.52912,0.10399,0.19655],"force_p95":0.13079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20493,"mean_force":0.07526,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.52868,0.08494,0.197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13636.0,"contact_point_centroid":[0.53408,0.06595,0.19533],"force_p95":0.11536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20031,"mean_force":0.06838,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.52836,0.08393,0.19674]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51369,-0.02307,-0.00204],"force_p95":0.13775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17208,"mean_force":0.12616,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50068,-0.02256,0.02599]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.5137,-0.02302,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50317,-0.01028,0.2192]},{"body_a":"world","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.5527,0.13096,-0.00203],"force_p95":0.12412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12846,"mean_force":0.11937,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54552,0.14419,0.24785]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50704,-0.02183,0.08574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.50047,-0.00348,0.02661],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10429,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15740.0,"contact_point_centroid":[0.50893,-0.01278,0.15589],"force_p95":0.08886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09686,"mean_force":0.06151,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50635,0.00616,0.15464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16855.0,"contact_point_centroid":[0.50796,0.02408,0.15392],"force_p95":0.08236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09526,"mean_force":0.05756,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50606,0.00518,0.15338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.4989,-0.0418,0.02758],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09217,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]}],"total_contact_groups":16},"final_pose_error":0.01092,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.5527,0.13096,0.01602],"final_tcp_position":[0.55024,0.14974,0.26196],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.83806,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50862,-0.02104,0.13838],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50817,-0.02269,0.03408],"tcp_start":[0.50862,-0.02104,0.13838],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51355,-0.0229,0.02584],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26568,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13775,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.17208,"tcp_end":[0.49939,-0.02253,0.02461],"tcp_start":[0.50817,-0.02269,0.03408],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5126,-0.02323,0.11307],"object_pos_start":[0.51355,-0.0229,0.02584],"object_to_goal_dist_end":0.21017,"object_to_goal_dist_start":0.26568,"object_z_max":0.11296,"peak_contact_force":0.08297,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37699.0,"raw_peak_contact_force":0.65919,"tcp_end":[0.50142,-0.02261,0.12239],"tcp_start":[0.49939,-0.02253,0.02461],"tcp_to_object_dist_end":0.01458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52134,0.03225,0.17112],"object_pos_start":[0.5126,-0.02323,0.11307],"object_to_goal_dist_end":0.13386,"object_to_goal_dist_start":0.21017,"object_z_max":0.17104,"peak_contact_force":0.09405,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32595.0,"raw_peak_contact_force":0.09686,"subtask_id":"reach_goal","tcp_end":[0.51416,0.03165,0.1877],"tcp_start":[0.50142,-0.02261,0.12239],"tcp_to_object_dist_end":0.01808,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55194,0.1409,0.1877],"object_pos_start":[0.52134,0.03225,0.17112],"object_to_goal_dist_end":0.036,"object_to_goal_dist_start":0.13386,"object_z_max":0.18769,"peak_contact_force":0.20493,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25862.0,"raw_peak_contact_force":0.20493,"subtask_id":"reach_goal","tcp_end":[0.54662,0.13878,0.2116],"tcp_start":[0.51416,0.03165,0.1877],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55163,0.13339,0.00981],"object_pos_start":[0.55194,0.1409,0.1877],"object_to_goal_dist_end":0.21298,"object_to_goal_dist_start":0.036,"object_z_max":0.1877,"peak_contact_force":0.1067,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1137.0,"raw_peak_contact_force":1.83806,"tcp_end":[0.54172,0.13758,0.23435],"tcp_start":[0.54662,0.13878,0.2116],"tcp_to_object_dist_end":0.2248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":600.0,"object_pos_end":[0.5527,0.13096,0.01602],"object_pos_start":[0.55163,0.13339,0.00981],"object_to_goal_dist_end":0.20701,"object_to_goal_dist_start":0.21298,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1740.0,"raw_peak_contact_force":0.12846,"tcp_end":[0.55024,0.14974,0.26196],"tcp_start":[0.54172,0.13758,0.23435],"tcp_to_object_dist_end":0.24667,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50279,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.23254,"lift.lift_speed":0.05963,"move_to_goal.goal_offset_z":0.14729,"move_to_goal.move_speed":0.06478},"optimized_scores":{"best_composite_score":0.31013,"best_fitness_score":0.69013,"best_task_score":0.42463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.54485,0.22459,-0.00776],"force_p95":1.09303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16123,"mean_force":0.44303,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5489,0.22689,0.15246]},{"body_a":"world","body_b":"grasp_target","contact_count":209.0,"contact_point_centroid":[0.49738,0.04186,-0.00124],"force_p95":0.43545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65382,"mean_force":0.10663,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48545,0.04319,0.02704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.48647,0.06228,0.0758],"force_p95":0.08382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29074,"mean_force":0.05876,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48597,0.04308,0.07307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20729.0,"contact_point_centroid":[0.48807,0.02416,0.0735],"force_p95":0.07943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27458,"mean_force":0.04974,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48591,0.04308,0.0721]},{"body_a":"world","body_b":"grasp_target","contact_count":1665.0,"contact_point_centroid":[0.52877,0.22016,-0.00203],"force_p95":0.18069,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26763,"mean_force":0.1259,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55395,0.23521,0.17479]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.0449,-0.00215],"force_p95":0.16684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2361,"mean_force":0.13431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4885,0.04348,0.02644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.48914,0.02439,0.02654],"force_p95":0.07647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1906,"mean_force":0.04313,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48726,0.04337,0.02515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1266.0,"contact_point_centroid":[0.54852,0.24706,0.14346],"force_p95":0.0721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17451,"mean_force":0.04206,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55302,0.22866,0.13901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1410.0,"contact_point_centroid":[0.55993,0.21051,0.13911],"force_p95":0.07313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16529,"mean_force":0.03965,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55299,0.22865,0.13896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20017.0,"contact_point_centroid":[0.53978,0.15896,0.15283],"force_p95":0.07555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15794,"mean_force":0.05078,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.53398,0.17691,0.15346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15627.0,"contact_point_centroid":[0.53188,0.19815,0.1566],"force_p95":0.09287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14435,"mean_force":0.06308,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.53499,0.17946,0.1529]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49753,0.02011,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49519,0.04252,0.08568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18462.0,"contact_point_centroid":[0.50245,0.05935,0.14673],"force_p95":0.0812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10017,"mean_force":0.05328,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.4984,0.07783,0.14659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4250.0,"contact_point_centroid":[0.4875,0.06271,0.02786],"force_p95":0.08398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09948,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48727,0.04337,0.02515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15394.0,"contact_point_centroid":[0.49813,0.09668,0.14853],"force_p95":0.08978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09464,"mean_force":0.06241,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49829,0.07755,0.14636]}],"total_contact_groups":16},"final_pose_error":0.01174,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52827,0.21999,0.02602],"final_tcp_position":[0.55964,0.24196,0.18645],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.16123,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49718,0.04114,0.13802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49587,0.04414,0.03423],"tcp_start":[0.49718,0.04114,0.13802],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04385,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24315,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16357,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.2361,"tcp_end":[0.48724,0.04336,0.02512],"tcp_start":[0.49587,0.04414,0.03423],"tcp_to_object_dist_end":0.01394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49988,0.04408,0.11236],"object_pos_start":[0.50116,0.04385,0.02548],"object_to_goal_dist_end":0.21369,"object_to_goal_dist_start":0.24315,"object_z_max":0.11225,"peak_contact_force":0.08092,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37938.0,"raw_peak_contact_force":0.65382,"tcp_end":[0.48906,0.04319,0.12207],"tcp_start":[0.48724,0.04336,0.02512],"tcp_to_object_dist_end":0.01457,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51738,0.11212,0.15704],"object_pos_start":[0.49988,0.04408,0.11236],"object_to_goal_dist_end":0.1412,"object_to_goal_dist_start":0.21369,"object_z_max":0.157,"peak_contact_force":0.09287,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33856.0,"raw_peak_contact_force":0.10017,"subtask_id":"reach_goal","tcp_end":[0.51049,0.10999,0.17354],"tcp_start":[0.48906,0.04319,0.12207],"tcp_to_object_dist_end":0.01801,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5513,0.2301,0.12062],"object_pos_start":[0.51738,0.11212,0.15704],"object_to_goal_dist_end":0.03277,"object_to_goal_dist_start":0.1412,"object_z_max":0.15704,"peak_contact_force":0.07297,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35644.0,"raw_peak_contact_force":0.15794,"subtask_id":"reach_goal","tcp_end":[0.55476,0.22912,0.14205],"tcp_start":[0.51049,0.10999,0.17354],"tcp_to_object_dist_end":0.02173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53776,0.22394,0.02841],"object_pos_start":[0.5513,0.2301,0.12062],"object_to_goal_dist_end":0.12312,"object_to_goal_dist_start":0.03277,"object_z_max":0.12062,"peak_contact_force":0.18424,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2833.0,"raw_peak_contact_force":1.16123,"tcp_end":[0.5488,0.22685,0.16383],"tcp_start":[0.55476,0.22912,0.14205],"tcp_to_object_dist_end":0.1359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":600.0,"object_pos_end":[0.52827,0.21999,0.02602],"object_pos_start":[0.53776,0.22394,0.02841],"object_to_goal_dist_end":0.12848,"object_to_goal_dist_start":0.12312,"object_z_max":0.02851,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1665.0,"raw_peak_contact_force":0.26763,"tcp_end":[0.55964,0.24196,0.18645],"tcp_start":[0.5488,0.22685,0.16383],"tcp_to_object_dist_end":0.16493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74419,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.27997,"lift.lift_speed":0.06196,"move_to_goal.goal_offset_z":0.22043,"move_to_goal.move_speed":0.07854},"optimized_scores":{"best_composite_score":0.24822,"best_fitness_score":0.62822,"best_task_score":0.29865},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.57818,0.11785,-0.00966],"force_p95":1.63955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.758,"mean_force":0.63471,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57859,0.11216,0.19908]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.47287,-0.0195,-0.00111],"force_p95":0.42546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.616,"mean_force":0.09735,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46126,-0.0197,0.02806]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20683.0,"contact_point_centroid":[0.46282,-0.00073,0.07769],"force_p95":0.07507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27493,"mean_force":0.04989,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46104,-0.01971,0.0762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17744.0,"contact_point_centroid":[0.46188,-0.0389,0.0789],"force_p95":0.08113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26599,"mean_force":0.05696,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46104,-0.01971,0.07639]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.59034,0.12886,-0.00198],"force_p95":0.13008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2281,"mean_force":0.12194,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60131,0.13435,0.21606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1257.0,"contact_point_centroid":[0.58123,0.13233,0.18552],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2209,"mean_force":0.04934,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58234,0.113,0.18222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19548.0,"contact_point_centroid":[0.55353,0.05919,0.18916],"force_p95":0.07515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1702,"mean_force":0.05131,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.54992,0.07771,0.18893]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02019,-0.00203],"force_p95":0.1352,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16116,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46404,-0.01974,0.02758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15220.0,"contact_point_centroid":[0.54973,0.09674,0.19136],"force_p95":0.09249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15269,"mean_force":0.06414,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.54984,0.07761,0.18898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1307.0,"contact_point_centroid":[0.58674,0.09439,0.18341],"force_p95":0.06783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14421,"mean_force":0.03923,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58252,0.11304,0.18253]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48643,-0.00894,0.21997]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15180.0,"contact_point_centroid":[0.48738,-0.01298,0.16463],"force_p95":0.08922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12652,"mean_force":0.06292,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48421,0.0059,0.16383]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47145,-0.01908,0.08667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5074.0,"contact_point_centroid":[0.46409,-0.00068,0.02795],"force_p95":0.06872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10387,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16055.0,"contact_point_centroid":[0.48582,0.02393,0.16262],"force_p95":0.08496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0992,"mean_force":0.06018,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48341,0.00506,0.16252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4160.0,"contact_point_centroid":[0.46211,-0.03897,0.02884],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]}],"total_contact_groups":16},"final_pose_error":0.01346,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.59055,0.12894,0.01602],"final_tcp_position":[0.62451,0.15506,0.22923],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.758,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47429,-0.01836,0.13938],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47123,-0.01986,0.0347],"tcp_start":[0.47429,-0.01836,0.13938],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47602,-0.02008,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2885,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1352,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11034.0,"raw_peak_contact_force":0.16116,"tcp_end":[0.4628,-0.01972,0.02637],"tcp_start":[0.47123,-0.01986,0.0347],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47552,-0.02042,0.11715],"object_pos_start":[0.47602,-0.02008,0.02587],"object_to_goal_dist_end":0.24874,"object_to_goal_dist_start":0.2885,"object_z_max":0.11704,"peak_contact_force":0.10031,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38596.0,"raw_peak_contact_force":0.616,"tcp_end":[0.46368,-0.01978,0.12837],"tcp_start":[0.4628,-0.01972,0.02637],"tcp_to_object_dist_end":0.01633,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51317,0.02899,0.18079],"object_pos_start":[0.47552,-0.02042,0.11715],"object_to_goal_dist_end":0.17613,"object_to_goal_dist_start":0.24874,"object_z_max":0.18074,"peak_contact_force":0.08326,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31235.0,"raw_peak_contact_force":0.12652,"subtask_id":"reach_goal","tcp_end":[0.50551,0.02845,0.19885],"tcp_start":[0.46368,-0.01978,0.12837],"tcp_to_object_dist_end":0.01962,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58236,0.114,0.16275],"object_pos_start":[0.51317,0.02899,0.18079],"object_to_goal_dist_end":0.07207,"object_to_goal_dist_start":0.17613,"object_z_max":0.18079,"peak_contact_force":0.08113,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34768.0,"raw_peak_contact_force":0.1702,"subtask_id":"reach_goal","tcp_end":[0.58405,0.11324,0.1855],"tcp_start":[0.50551,0.02845,0.19885],"tcp_to_object_dist_end":0.02282,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58757,0.12351,0.01418],"object_pos_start":[0.58236,0.114,0.16275],"object_to_goal_dist_end":0.18471,"object_to_goal_dist_start":0.07207,"object_z_max":0.16275,"peak_contact_force":0.12553,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2690.0,"raw_peak_contact_force":1.758,"tcp_end":[0.57853,0.11215,0.20722],"tcp_start":[0.58405,0.11324,0.1855],"tcp_to_object_dist_end":0.19359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":600.0,"object_pos_end":[0.59055,0.12894,0.01602],"object_pos_start":[0.58757,0.12351,0.01418],"object_to_goal_dist_end":0.18127,"object_to_goal_dist_start":0.18471,"object_z_max":0.01703,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.2281,"tcp_end":[0.62451,0.15506,0.22923],"tcp_start":[0.57853,0.11215,0.20722],"tcp_to_object_dist_end":0.21747,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```