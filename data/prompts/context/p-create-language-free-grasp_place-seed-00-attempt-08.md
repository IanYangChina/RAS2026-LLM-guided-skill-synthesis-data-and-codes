## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1620 | 0.33 | ✅ accepted |
| 7 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2605 | 0.32 | ✅ accepted |
| 6 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.3101 | 0.22 | ✅ accepted |
| 5 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.2710 | 0.20 | ❌ rejected |
| 4 | approach → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.1221 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.162) — your mutation base

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
    - -0.03
    orientation:
      mode: none
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
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
  parameters:
    release_time:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: duration.max_time
        mode: replace
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.25]
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.03]
  - orientation: mode=none
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.162
- **task_score** (E): 0.328
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1655 |
| descend_to_grasp | 1.00 | 1.00 | 0.1043 |
| grasp | 1.00 | 1.00 | 0.0124 |
| lift | 0.00 | 1.00 | 0.1016 |
| move_to_goal | 0.00 | 1.00 | 0.0868 |
| descend_to_place | 0.67 | 1.00 | 0.1363 |
| release | 1.00 | 1.00 | 0.0229 |
| retract | 1.00 | 1.00 | 0.0537 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.139) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.493, 0.001, 0.139)→(0.492, 0.001, 0.034) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.492, 0.001, 0.034)→(0.483, 0.000, 0.025) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.333 | 0.146 | 0.190 |
| lift | lift | 0.00 / step_budget | (0.483, 0.000, 0.025)→(0.479, 0.000, 0.127) | (0.497, 0.000, 0.026)→(0.491, 0.000, 0.116) | 0.266→0.225 | 1.00 / 32.333 | 0.101 | 0.666 |
| move_to_goal | approach | 0.00 / step_budget | (0.479, 0.000, 0.127)→(0.502, 0.048, 0.194) | (0.491, 0.000, 0.116)→(0.510, 0.049, 0.175) | 0.225→0.160 | 1.00 / 26.333 | 0.117 | 0.129 |
| descend_to_place | approach | 0.67 / step_budget | (0.502, 0.048, 0.194)→(0.562, 0.162, 0.163) | (0.510, 0.049, 0.175)→(0.564, 0.164, 0.136) | 0.160→0.062 | 1.00 / 25.000 | 0.128 | 0.251 |
| release | release | 1.00 / step_budget | (0.562, 0.162, 0.163)→(0.556, 0.161, 0.185) | (0.564, 0.164, 0.136)→(0.554, 0.160, 0.021) | 0.062→0.171 | 1.00 / 3.333 | 0.173 | 1.354 |
| retract | retract | 1.00 / step_budget | (0.556, 0.161, 0.185)→(0.578, 0.182, 0.225) | (0.554, 0.160, 0.021)→(0.562, 0.161, 0.019) | 0.171→0.171 | 1.00 / 4.000 | 0.123 | 0.284 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.433
- phase_score: 0.411
- phase_breakdown.reach_goal_score: 0.524
- phase_breakdown.reach_object_score: 0.147
- grasp_place_fitness: 0.694

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.694
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.433
- **Median Q (composite search score)**: 0.148
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.202


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57627,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_z_offset":-0.01706,"lift.lift_height":0.29887,"lift.lift_speed":0.06017,"move_to_goal.goal_offset_z":0.20428,"move_to_goal.move_speed":0.07032,"release.release_time":0.12233},"optimized_scores":{"best_composite_score":0.12379,"best_fitness_score":0.60379,"best_task_score":0.25278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.54521,0.1456,-0.00865],"force_p95":1.67704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80193,"mean_force":0.51427,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54393,0.14552,0.21417]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.5091,-0.02216,-0.00114],"force_p95":0.47392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68375,"mean_force":0.11713,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49747,-0.0225,0.02627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20527.0,"contact_point_centroid":[0.49664,-0.00349,0.07367],"force_p95":0.07622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29363,"mean_force":0.05047,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49491,-0.02245,0.07214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49568,-0.04163,0.07573],"force_p95":0.08093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29053,"mean_force":0.05887,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4949,-0.02245,0.07307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.55482,0.12976,0.18928],"force_p95":0.14138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26143,"mean_force":0.0933,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54721,0.1465,0.19453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13185.0,"contact_point_centroid":[0.53215,0.06681,0.19553],"force_p95":0.11734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25804,"mean_force":0.06844,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.52642,0.08479,0.1969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":427.0,"contact_point_centroid":[0.54778,0.16516,0.1926],"force_p95":0.15218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24354,"mean_force":0.1053,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54741,0.14656,0.19483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11835.0,"contact_point_centroid":[0.52737,0.10556,0.19647],"force_p95":0.12688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23506,"mean_force":0.07516,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.52703,0.08652,0.1969]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51369,-0.02307,-0.00204],"force_p95":0.13775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17208,"mean_force":0.12616,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50068,-0.02256,0.02599]},{"body_a":"world","body_b":"grasp_target","contact_count":1864.0,"contact_point_centroid":[0.54404,0.14636,-0.00201],"force_p95":0.1255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15688,"mean_force":0.11996,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54628,0.14785,0.24009]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.5137,-0.02302,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50317,-0.01028,0.2192]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50704,-0.02183,0.08574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.50047,-0.00348,0.02661],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10429,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15863.0,"contact_point_centroid":[0.50233,-0.01618,0.16282],"force_p95":0.0886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09658,"mean_force":0.06112,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49993,0.00278,0.16146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16958.0,"contact_point_centroid":[0.5016,0.02084,0.16058],"force_p95":0.08228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09551,"mean_force":0.05739,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49965,0.00194,0.16002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.4989,-0.0418,0.02758],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09217,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]}],"total_contact_groups":16},"final_pose_error":0.0118,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54404,0.14635,0.01602],"final_tcp_position":[0.55042,0.15037,0.26085],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.80193,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50862,-0.02104,0.13838],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50817,-0.02269,0.03408],"tcp_start":[0.50862,-0.02104,0.13838],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51355,-0.0229,0.02584],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26568,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13775,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.17208,"tcp_end":[0.49939,-0.02253,0.02461],"tcp_start":[0.50817,-0.02269,0.03408],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50625,-0.02306,0.11358],"object_pos_start":[0.51355,-0.0229,0.02584],"object_to_goal_dist_end":0.21111,"object_to_goal_dist_start":0.26568,"object_z_max":0.11348,"peak_contact_force":0.08246,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37719.0,"raw_peak_contact_force":0.68375,"tcp_end":[0.49506,-0.02245,0.12278],"tcp_start":[0.49939,-0.02253,0.02461],"tcp_to_object_dist_end":0.0145,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51533,0.02608,0.18467],"object_pos_start":[0.50625,-0.02306,0.11358],"object_to_goal_dist_end":0.13661,"object_to_goal_dist_start":0.21111,"object_z_max":0.18462,"peak_contact_force":0.08353,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32821.0,"raw_peak_contact_force":0.09658,"subtask_id":"reach_goal","tcp_end":[0.50788,0.02566,0.20106],"tcp_start":[0.49506,-0.02245,0.12278],"tcp_to_object_dist_end":0.018,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.55429,0.14897,0.17436],"object_pos_start":[0.51533,0.02608,0.18467],"object_to_goal_dist_end":0.04771,"object_to_goal_dist_start":0.13661,"object_z_max":0.18467,"peak_contact_force":0.15038,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25020.0,"raw_peak_contact_force":0.25804,"subtask_id":"reach_goal","tcp_end":[0.54902,0.14683,0.1978],"tcp_start":[0.50788,0.02566,0.20106],"tcp_to_object_dist_end":0.02412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54559,0.1424,0.0099],"object_pos_start":[0.55429,0.14897,0.17436],"object_to_goal_dist_end":0.21246,"object_to_goal_dist_start":0.04771,"object_z_max":0.17436,"peak_contact_force":0.16812,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1187.0,"raw_peak_contact_force":1.80193,"tcp_end":[0.54388,0.14551,0.22045],"tcp_start":[0.54902,0.14683,0.1978],"tcp_to_object_dist_end":0.21057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.54404,0.14635,0.01602],"object_pos_start":[0.54559,0.1424,0.0099],"object_to_goal_dist_end":0.20628,"object_to_goal_dist_start":0.21246,"object_z_max":0.01692,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.15688,"tcp_end":[0.55042,0.15037,0.26085],"tcp_start":[0.54388,0.14551,0.22045],"tcp_to_object_dist_end":0.24495,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53005,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_z_offset":-0.02316,"lift.lift_height":0.27748,"lift.lift_speed":0.06119,"move_to_goal.goal_offset_z":0.21491,"move_to_goal.move_speed":0.05939,"release.release_time":0.12477},"optimized_scores":{"best_composite_score":0.21441,"best_fitness_score":0.69441,"best_task_score":0.43319},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":319.0,"contact_point_centroid":[0.53943,0.22254,-0.00372],"force_p95":0.81207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92748,"mean_force":0.21205,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54684,0.22416,0.13286]},{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.4969,0.04188,-0.00123],"force_p95":0.42226,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67952,"mean_force":0.1103,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48529,0.04319,0.02707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16772.0,"contact_point_centroid":[0.48355,0.0622,0.07631],"force_p95":0.10098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30073,"mean_force":0.06124,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4828,0.04297,0.07407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20650.0,"contact_point_centroid":[0.48513,0.02422,0.07535],"force_p95":0.08344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28522,"mean_force":0.04976,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4828,0.04297,0.07405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":479.0,"contact_point_centroid":[0.55022,0.24582,0.11864],"force_p95":0.14914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28138,"mean_force":0.10138,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55095,0.22587,0.11936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12551.0,"contact_point_centroid":[0.53613,0.15344,0.14361],"force_p95":0.12408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25572,"mean_force":0.07584,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.52911,0.16973,0.14636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":910.0,"contact_point_centroid":[0.55835,0.20955,0.11614],"force_p95":0.12708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24767,"mean_force":0.05987,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5511,0.22594,0.11959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7694.0,"contact_point_centroid":[0.52824,0.18465,0.14772],"force_p95":0.16271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23807,"mean_force":0.1152,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.52717,0.16516,0.14824]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.0449,-0.00215],"force_p95":0.16684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2361,"mean_force":0.13431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4885,0.04348,0.02644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.48914,0.02439,0.02654],"force_p95":0.07647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1906,"mean_force":0.04313,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48726,0.04337,0.02515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11789.0,"contact_point_centroid":[0.49205,0.08937,0.15303],"force_p95":0.1204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15956,"mean_force":0.08172,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49036,0.07009,0.1528]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.53876,0.22235,-0.00198],"force_p95":0.12789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14303,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55211,0.23299,0.16362]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49753,0.02011,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49519,0.04252,0.08568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16194.0,"contact_point_centroid":[0.49511,0.05226,0.1522],"force_p95":0.09107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11199,"mean_force":0.05872,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.4904,0.07017,0.15291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4250.0,"contact_point_centroid":[0.4875,0.06271,0.02786],"force_p95":0.08398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09948,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48727,0.04337,0.02515]}],"total_contact_groups":16},"final_pose_error":0.01297,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53875,0.22235,0.02602],"final_tcp_position":[0.55955,0.24183,0.18514],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.92748,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49718,0.04114,0.13802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49587,0.04414,0.03423],"tcp_start":[0.49718,0.04114,0.13802],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04385,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24315,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16357,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.2361,"tcp_end":[0.48724,0.04336,0.02512],"tcp_start":[0.49587,0.04414,0.03423],"tcp_to_object_dist_end":0.01394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49584,0.04383,0.11486],"object_pos_start":[0.50116,0.04385,0.02548],"object_to_goal_dist_end":0.2148,"object_to_goal_dist_start":0.24315,"object_z_max":0.11475,"peak_contact_force":0.11389,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37619.0,"raw_peak_contact_force":0.67952,"tcp_end":[0.48296,0.04299,0.12588],"tcp_start":[0.48724,0.04336,0.02512],"tcp_to_object_dist_end":0.01697,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50863,0.09725,0.16219],"object_pos_start":[0.49584,0.04383,0.11486],"object_to_goal_dist_end":0.15856,"object_to_goal_dist_start":0.2148,"object_z_max":0.16217,"peak_contact_force":0.15764,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27983.0,"raw_peak_contact_force":0.15956,"subtask_id":"reach_goal","tcp_end":[0.50079,0.09573,0.18233],"tcp_start":[0.48296,0.04299,0.12588],"tcp_to_object_dist_end":0.02166,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55379,0.22698,0.09159],"object_pos_start":[0.50863,0.09725,0.16219],"object_to_goal_dist_end":0.05898,"object_to_goal_dist_start":0.15856,"object_z_max":0.16219,"peak_contact_force":0.14823,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20245.0,"raw_peak_contact_force":0.25572,"subtask_id":"reach_goal","tcp_end":[0.55298,0.22649,0.12274],"tcp_start":[0.50079,0.09573,0.18233],"tcp_to_object_dist_end":0.03116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53864,0.22232,0.02644],"object_pos_start":[0.55379,0.22698,0.09159],"object_to_goal_dist_end":0.12511,"object_to_goal_dist_start":0.05898,"object_z_max":0.09159,"peak_contact_force":0.1397,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1708.0,"raw_peak_contact_force":0.92748,"tcp_end":[0.54672,0.22412,0.14464],"tcp_start":[0.55298,0.22649,0.12274],"tcp_to_object_dist_end":0.11849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.53875,0.22235,0.02602],"object_pos_start":[0.53864,0.22232,0.02644],"object_to_goal_dist_end":0.12549,"object_to_goal_dist_start":0.12511,"object_z_max":0.02644,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.14303,"tcp_end":[0.55955,0.24183,0.18514],"tcp_start":[0.54672,0.22412,0.14464],"tcp_to_object_dist_end":0.16165,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70225,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_z_offset":-0.02538,"lift.lift_height":0.25051,"lift.lift_speed":0.06355,"move_to_goal.goal_offset_z":0.23715,"move_to_goal.move_speed":0.05555,"release.release_time":0.17913},"optimized_scores":{"best_composite_score":0.14773,"best_fitness_score":0.62773,"best_task_score":0.29767},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.57596,0.11106,-0.00934],"force_p95":1.22772,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33153,"mean_force":0.53211,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57748,0.11274,0.17989]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.47286,-0.01959,-0.00112],"force_p95":0.46785,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63572,"mean_force":0.10744,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46119,-0.0197,0.02812]},{"body_a":"world","body_b":"grasp_target","contact_count":1898.0,"contact_point_centroid":[0.60096,0.11441,-0.00216],"force_p95":0.21,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55093,"mean_force":0.13254,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60172,0.13563,0.20801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20323.0,"contact_point_centroid":[0.46041,-0.00072,0.07869],"force_p95":0.07693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28331,"mean_force":0.05078,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45848,-0.01964,0.07732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17636.0,"contact_point_centroid":[0.45939,-0.03883,0.08028],"force_p95":0.08728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27556,"mean_force":0.05782,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45848,-0.01964,0.07804]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1266.0,"contact_point_centroid":[0.57891,0.13238,0.16616],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24392,"mean_force":0.04229,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58154,0.11363,0.16505]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13475.0,"contact_point_centroid":[0.55071,0.05662,0.17926],"force_p95":0.11196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23797,"mean_force":0.07796,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.54491,0.07505,0.17897]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":965.0,"contact_point_centroid":[0.58733,0.09506,0.16511],"force_p95":0.09322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20734,"mean_force":0.05353,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58153,0.11363,0.16505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16310.0,"contact_point_centroid":[0.54724,0.09518,0.17965],"force_p95":0.09078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20093,"mean_force":0.05978,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.54628,0.07644,0.17858]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02019,-0.00203],"force_p95":0.1352,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16116,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46404,-0.01974,0.02758]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48643,-0.00894,0.21997]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13517.0,"contact_point_centroid":[0.48161,-0.01506,0.1656],"force_p95":0.10343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13091,"mean_force":0.0716,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.47757,0.00364,0.16533]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47145,-0.01908,0.08667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13810.0,"contact_point_centroid":[0.4818,0.02226,0.16525],"force_p95":0.09562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11967,"mean_force":0.07021,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.47753,0.00359,0.16525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5074.0,"contact_point_centroid":[0.46409,-0.00068,0.02795],"force_p95":0.06872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10387,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4160.0,"contact_point_centroid":[0.46211,-0.03897,0.02884],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]}],"total_contact_groups":16},"final_pose_error":0.01452,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60335,0.11473,0.01602],"final_tcp_position":[0.62438,0.15509,0.228],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.33153,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47429,-0.01836,0.13938],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47123,-0.01986,0.0347],"tcp_start":[0.47429,-0.01836,0.13938],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47602,-0.02008,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2885,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1352,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11034.0,"raw_peak_contact_force":0.16116,"tcp_end":[0.4628,-0.01972,0.02637],"tcp_start":[0.47123,-0.01986,0.0347],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47143,-0.02016,0.11974],"object_pos_start":[0.47602,-0.02008,0.02587],"object_to_goal_dist_end":0.25041,"object_to_goal_dist_start":0.2885,"object_z_max":0.11962,"peak_contact_force":0.10559,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38121.0,"raw_peak_contact_force":0.63572,"tcp_end":[0.45861,-0.01964,0.13182],"tcp_start":[0.4628,-0.01972,0.02637],"tcp_to_object_dist_end":0.01762,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,0.0241,0.17863],"object_pos_start":[0.47143,-0.02016,0.11974],"object_to_goal_dist_end":0.18423,"object_to_goal_dist_start":0.25041,"object_z_max":0.17856,"peak_contact_force":0.10969,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27327.0,"raw_peak_contact_force":0.13091,"subtask_id":"reach_goal","tcp_end":[0.49725,0.02385,0.19823],"tcp_start":[0.45861,-0.01964,0.13182],"tcp_to_object_dist_end":0.02176,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58488,0.1157,0.14309],"object_pos_start":[0.50668,0.0241,0.17863],"object_to_goal_dist_end":0.07912,"object_to_goal_dist_start":0.18423,"object_z_max":0.17864,"peak_contact_force":0.08552,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29785.0,"raw_peak_contact_force":0.23797,"subtask_id":"reach_goal","tcp_end":[0.58322,0.11386,0.16815],"tcp_start":[0.49725,0.02385,0.19823],"tcp_to_object_dist_end":0.02518,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57856,0.11595,0.0272],"object_pos_start":[0.58488,0.1157,0.14309],"object_to_goal_dist_end":0.17656,"object_to_goal_dist_start":0.07912,"object_z_max":0.14309,"peak_contact_force":0.21164,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2365.0,"raw_peak_contact_force":1.33153,"tcp_end":[0.5774,0.11272,0.18993],"tcp_start":[0.58322,0.11386,0.16815],"tcp_to_object_dist_end":0.16277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.60335,0.11473,0.01602],"object_pos_start":[0.57856,0.11595,0.0272],"object_to_goal_dist_end":0.18177,"object_to_goal_dist_start":0.17656,"object_z_max":0.02938,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1898.0,"raw_peak_contact_force":0.55093,"tcp_end":[0.62438,0.15509,0.228],"tcp_start":[0.5774,0.11272,0.18993],"tcp_to_object_dist_end":0.21681,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```