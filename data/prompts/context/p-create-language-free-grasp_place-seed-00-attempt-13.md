## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → approach → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1681 | 0.22 | ❌ rejected |
| 12 | approach → approach → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1315 | 0.31 | ❌ rejected |
| 11 | approach → approach → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5019 | 0.89 | ✅ accepted |
| 10 | approach → approach → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4064 | 0.70 | ❌ rejected |
| 9 | approach → approach → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5307 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.888, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.168) — your mutation base

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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.18
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
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
    - 0.1
    orientation:
      mode: none
  parameters:
    goal_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    move_speed:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
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
    - 0.02
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.18]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - goal_offset_z: status=consumed; consumers=target.offset.z (replace)
    - move_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.168
- **task_score** (E): 0.220
- **fitness_score**: 0.588  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1655 |
| descend_to_grasp | 1.00 | 1.00 | 0.1043 |
| grasp | 1.00 | 1.00 | 0.0124 |
| lift | 0.67 | 1.00 | 0.1108 |
| move_to_goal | 0.00 | 1.00 | 0.1001 |
| descend_to_place | 0.33 | 1.00 | 0.0854 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.139) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.493, 0.001, 0.139)→(0.492, 0.001, 0.034) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.492, 0.001, 0.034)→(0.483, 0.000, 0.025) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.333 | 0.146 | 0.190 |
| lift | lift | 0.67 / step_budget | (0.483, 0.000, 0.025)→(0.475, 0.000, 0.136) | (0.497, 0.000, 0.026)→(0.484, 0.000, 0.117) | 0.266→0.227 | 1.00 / 23.667 | 0.114 | 0.693 |
| move_to_goal | approach | 0.00 / step_budget | (0.475, 0.000, 0.136)→(0.512, 0.081, 0.173) | (0.484, 0.000, 0.117)→(0.507, 0.058, 0.016) | 0.227→0.229 | 1.00 / 8.000 | 0.123 | 1.419 |
| descend_to_place | descend | 0.33 / step_budget | (0.512, 0.081, 0.173)→(0.552, 0.152, 0.191) | (0.507, 0.058, 0.016)→(0.507, 0.058, 0.016) | 0.229→0.229 | 1.00 / 8.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.266
- phase_score: 0.537
- phase_breakdown.reach_goal_score: 0.394
- phase_breakdown.reach_object_score: 0.872
- grasp_place_fitness: 0.611

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.611
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.266
- **Median Q (composite search score)**: 0.161
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.346


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88435,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.descend_speed":0.07598,"descend_to_place.place_z_offset":0.03494,"lift.lift_height":0.17493,"lift.lift_speed":0.0748,"move_to_goal.goal_offset_z":0.08841,"move_to_goal.move_speed":0.1217},"optimized_scores":{"best_composite_score":0.15278,"best_fitness_score":0.57278,"best_task_score":0.19075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4673.0,"contact_point_centroid":[0.4983,0.02342,-0.00222],"force_p95":0.14595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46033,"mean_force":0.13563,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50838,0.03785,0.19224]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.50926,-0.02187,-0.00119],"force_p95":0.45548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72295,"mean_force":0.11443,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49765,-0.0225,0.02617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21498.0,"contact_point_centroid":[0.49778,-0.00386,0.09107],"force_p95":0.1104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30817,"mean_force":0.06571,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49429,-0.02243,0.09091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18209.0,"contact_point_centroid":[0.49682,-0.04136,0.09418],"force_p95":0.11843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30585,"mean_force":0.07526,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49418,-0.02243,0.09308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":937.0,"contact_point_centroid":[0.49271,-0.03494,0.13842],"force_p95":0.1828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22527,"mean_force":0.10527,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49082,-0.01674,0.14361]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.49365,0.00207,0.13879],"force_p95":0.13444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20075,"mean_force":0.08868,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49099,-0.01555,0.14438]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51369,-0.02307,-0.00204],"force_p95":0.13775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17208,"mean_force":0.12616,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50068,-0.02256,0.02599]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.5137,-0.02302,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50317,-0.01028,0.2192]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50704,-0.02183,0.08574]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.49849,0.0242,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53285,0.1103,0.22692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.50047,-0.00348,0.02661],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10429,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.4989,-0.0418,0.02758],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09217,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4973.0,"contact_point_centroid":[0.50952,0.03861,0.19513],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01033,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50865,0.0386,0.19295]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6071.0,"contact_point_centroid":[0.53382,0.11039,0.22917],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.0103,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53287,0.11038,0.22695]}],"total_contact_groups":14},"final_pose_error":0.02247,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.49849,0.0242,0.01602],"final_tcp_position":[0.54521,0.13703,0.24237],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.46033,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50862,-0.02104,0.13838],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50817,-0.02269,0.03408],"tcp_start":[0.50862,-0.02104,0.13838],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51355,-0.0229,0.02584],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26568,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13775,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.17208,"tcp_end":[0.49939,-0.02253,0.02461],"tcp_start":[0.50817,-0.02269,0.03408],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49785,-0.02277,0.11858],"object_pos_start":[0.51355,-0.0229,0.02584],"object_to_goal_dist_end":0.21043,"object_to_goal_dist_start":0.26568,"object_z_max":0.13199,"peak_contact_force":0.13146,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39872.0,"raw_peak_contact_force":0.72295,"tcp_end":[0.4911,-0.02237,0.14118],"tcp_start":[0.49939,-0.02253,0.02461],"tcp_to_object_dist_end":0.02359,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49849,0.0242,0.01602],"object_pos_start":[0.49785,-0.02277,0.11858],"object_to_goal_dist_end":0.24852,"object_to_goal_dist_start":0.21043,"object_z_max":0.12315,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11775.0,"raw_peak_contact_force":1.46033,"subtask_id":"reach_goal","tcp_end":[0.51291,0.05621,0.20594],"tcp_start":[0.4911,-0.02237,0.14118],"tcp_to_object_dist_end":0.19314,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49849,0.0242,0.01602],"object_pos_start":[0.49849,0.0242,0.01602],"object_to_goal_dist_end":0.24852,"object_to_goal_dist_start":0.24852,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11671.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54215,0.1362,0.23522],"tcp_start":[0.51291,0.05621,0.20594],"tcp_to_object_dist_end":0.25,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88636,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.descend_speed":0.08124,"descend_to_place.place_z_offset":0.04967,"lift.lift_height":0.12589,"lift.lift_speed":0.11877,"move_to_goal.goal_offset_z":0.05366,"move_to_goal.move_speed":0.10619},"optimized_scores":{"best_composite_score":0.19065,"best_fitness_score":0.61065,"best_task_score":0.26567},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3337.0,"contact_point_centroid":[0.50768,0.10604,-0.00223],"force_p95":0.13262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41989,"mean_force":0.13728,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.51263,0.13415,0.15463]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.49754,0.04229,-0.00134],"force_p95":0.46464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70298,"mean_force":0.11465,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48552,0.04321,0.02685]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12886.0,"contact_point_centroid":[0.48509,0.06202,0.09604],"force_p95":0.11094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30948,"mean_force":0.07781,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48192,0.04289,0.09404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16124.0,"contact_point_centroid":[0.48634,0.02448,0.09256],"force_p95":0.10116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29592,"mean_force":0.06441,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48192,0.04289,0.09207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3801.0,"contact_point_centroid":[0.49072,0.08745,0.13453],"force_p95":0.16022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24531,"mean_force":0.11205,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48675,0.06876,0.1366]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.0449,-0.00215],"force_p95":0.16684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2361,"mean_force":0.13431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4885,0.04348,0.02644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.48914,0.02439,0.02654],"force_p95":0.07647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1906,"mean_force":0.04313,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48726,0.04337,0.02515]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5258.0,"contact_point_centroid":[0.49178,0.05113,0.1333],"force_p95":0.13664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17282,"mean_force":0.08322,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48679,0.06883,0.13663]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49753,0.02011,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49519,0.04252,0.08568]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.50766,0.10626,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53357,0.18978,0.16523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4250.0,"contact_point_centroid":[0.4875,0.06271,0.02786],"force_p95":0.08398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09948,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48727,0.04337,0.02515]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3319.0,"contact_point_centroid":[0.51425,0.13631,0.1573],"force_p95":0.01114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01046,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.51341,0.1363,0.15511]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6047.0,"contact_point_centroid":[0.53444,0.18975,0.16728],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01033,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53355,0.18972,0.16522]}],"total_contact_groups":14},"final_pose_error":0.04357,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50766,0.10626,0.01602],"final_tcp_position":[0.54518,0.21179,0.17561],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.41989,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49718,0.04114,0.13802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49587,0.04414,0.03423],"tcp_start":[0.49718,0.04114,0.13802],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04385,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24315,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16357,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.2361,"tcp_end":[0.48724,0.04336,0.02512],"tcp_start":[0.49587,0.04414,0.03423],"tcp_to_object_dist_end":0.01394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":623.0,"n_steps_budget":690.0,"object_pos_end":[0.49044,0.04379,0.11482],"object_pos_start":[0.50116,0.04385,0.02548],"object_to_goal_dist_end":0.21662,"object_to_goal_dist_start":0.24315,"object_z_max":0.12629,"peak_contact_force":0.11041,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29171.0,"raw_peak_contact_force":0.70298,"tcp_end":[0.47908,0.04264,0.13255],"tcp_start":[0.48724,0.04336,0.02512],"tcp_to_object_dist_end":0.02109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50766,0.10626,0.01602],"object_pos_start":[0.49044,0.04379,0.11482],"object_to_goal_dist_end":0.19882,"object_to_goal_dist_start":0.21662,"object_z_max":0.12043,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15715.0,"raw_peak_contact_force":1.41989,"subtask_id":"reach_goal","tcp_end":[0.51454,0.14348,0.15409],"tcp_start":[0.47908,0.04264,0.13255],"tcp_to_object_dist_end":0.14316,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50766,0.10626,0.01602],"object_pos_start":[0.50766,0.10626,0.01602],"object_to_goal_dist_end":0.19882,"object_to_goal_dist_start":0.19882,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11647.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54146,0.21034,0.16803],"tcp_start":[0.51454,0.14348,0.15409],"tcp_to_object_dist_end":0.18731,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66447,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.descend_speed":0.11541,"descend_to_place.place_z_offset":0.01444,"lift.lift_height":0.14552,"lift.lift_speed":0.06889,"move_to_goal.goal_offset_z":0.05005,"move_to_goal.move_speed":0.06313},"optimized_scores":{"best_composite_score":0.16082,"best_fitness_score":0.58082,"best_task_score":0.20384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1159.0,"contact_point_centroid":[0.51511,0.04493,-0.0028],"force_p95":0.41793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37816,"mean_force":0.1633,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50965,0.04329,0.15942]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.47209,-0.01924,-0.00111],"force_p95":0.47343,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65283,"mean_force":0.10784,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46125,-0.0197,0.02804]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":25664.0,"contact_point_centroid":[0.46032,-0.00081,0.09281],"force_p95":0.09375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28994,"mean_force":0.05546,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45781,-0.01963,0.09188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22809.0,"contact_point_centroid":[0.45918,-0.03872,0.09507],"force_p95":0.10259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28219,"mean_force":0.06164,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45775,-0.01963,0.09334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11450.0,"contact_point_centroid":[0.48583,-0.00728,0.14672],"force_p95":0.14343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23521,"mean_force":0.082,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48175,0.01151,0.14723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12529.0,"contact_point_centroid":[0.48893,0.03129,0.14663],"force_p95":0.11016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17045,"mean_force":0.07553,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48323,0.01302,0.14805]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02019,-0.00203],"force_p95":0.1352,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16116,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46404,-0.01974,0.02758]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48643,-0.00894,0.21997]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47145,-0.01908,0.08667]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.51511,0.0447,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55253,0.08769,0.16813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5074.0,"contact_point_centroid":[0.46409,-0.00068,0.02795],"force_p95":0.06872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10387,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4160.0,"contact_point_centroid":[0.46211,-0.03897,0.02884],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]},{"body_a":"left_finger","body_b":"right_finger","contact_count":963.0,"contact_point_centroid":[0.51052,0.04329,0.16151],"force_p95":0.01277,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01067,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50961,0.04328,0.15936]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6053.0,"contact_point_centroid":[0.5536,0.08771,0.17022],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01032,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55254,0.0877,0.16813]}],"total_contact_groups":14},"final_pose_error":0.07751,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.51511,0.0447,0.01602],"final_tcp_position":[0.57729,0.1104,0.17808],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.37816,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47429,-0.01836,0.13938],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47123,-0.01986,0.0347],"tcp_start":[0.47429,-0.01836,0.13938],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47602,-0.02008,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2885,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1352,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11034.0,"raw_peak_contact_force":0.16116,"tcp_end":[0.4628,-0.01972,0.02637],"tcp_start":[0.47123,-0.01986,0.0347],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46495,-0.0201,0.1175],"object_pos_start":[0.47602,-0.02008,0.02587],"object_to_goal_dist_end":0.25518,"object_to_goal_dist_start":0.2885,"object_z_max":0.12673,"peak_contact_force":0.09932,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":48621.0,"raw_peak_contact_force":0.65283,"tcp_end":[0.45464,-0.01957,0.13388],"tcp_start":[0.4628,-0.01972,0.02637],"tcp_to_object_dist_end":0.01935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51511,0.0447,0.01602],"object_pos_start":[0.46495,-0.0201,0.1175],"object_to_goal_dist_end":0.23856,"object_to_goal_dist_start":0.25518,"object_z_max":0.14027,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26101.0,"raw_peak_contact_force":1.37816,"subtask_id":"reach_goal","tcp_end":[0.50959,0.04328,0.15933],"tcp_start":[0.45464,-0.01957,0.13388],"tcp_to_object_dist_end":0.14342,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51511,0.0447,0.01602],"object_pos_start":[0.51511,0.0447,0.01602],"object_to_goal_dist_end":0.23856,"object_to_goal_dist_start":0.23856,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11653.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57342,0.10959,0.17027],"tcp_start":[0.50959,0.04328,0.15933],"tcp_to_object_dist_end":0.17722,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```