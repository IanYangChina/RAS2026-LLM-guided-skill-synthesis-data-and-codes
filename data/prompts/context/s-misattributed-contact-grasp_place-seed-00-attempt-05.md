## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1538 | 0.26 | ✅ accepted |
| 4 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1730 | 0.17 | ❌ rejected |
| 3 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1694 | 0.19 | ✅ accepted |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1713 | 0.18 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1716 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.154) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.4
- id: reach_goal
  weight: 0.6
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    grasp_height:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_object
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.002
- id: lift_object
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: transport_goal
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
      mode: keep_current
      tolerance: 0.1
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: descend_place
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
      mode: keep_current
      tolerance: 0.1
  parameters:
    place_height:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release_object
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.002]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.154
- **task_score** (E): 0.257
- **fitness_score**: 0.604  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1228 |
| descend_grasp | 1.00 | 1.00 | 0.1406 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.0991 |
| transport_goal | 0.00 | 1.00 | 0.1116 |
| descend_place | 0.67 | 1.00 | 0.0932 |
| release_object | 1.00 | 1.00 | 0.0224 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.002, 0.182) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.002, 0.182)→(0.492, 0.000, 0.042) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 43.000 | 0.142 | 0.194 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.000, 0.042)→(0.484, 0.000, 0.033) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 24.333 | 55983.986 | 0.591 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.033)→(0.480, 0.000, 0.132) | (0.497, 0.001, 0.026)→(0.496, 0.001, 0.116) | 0.266→0.223 | 1.00 / 12.000 | 3249.755 | 1.034 |
| transport_goal | approach | 0.00 / step_budget | (0.480, 0.000, 0.132)→(0.524, 0.089, 0.177) | (0.496, 0.001, 0.116)→(0.514, 0.079, 0.056) | 0.223→0.195 | 1.00 / 8.000 | 0.123 | 0.580 |
| descend_place | descend | 0.67 / step_budget | (0.524, 0.089, 0.177)→(0.564, 0.165, 0.204) | (0.514, 0.079, 0.056)→(0.520, 0.088, 0.016) | 0.195→0.210 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.564, 0.165, 0.204)→(0.559, 0.163, 0.226) | (0.520, 0.088, 0.016)→(0.520, 0.088, 0.016) | 0.210→0.210 | 1.00 / 4.000 | 10.826 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.370
- phase_score: 0.536
- phase_breakdown.reach_goal_score: 0.522
- phase_breakdown.reach_object_score: 0.557
- grasp_place_fitness: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.652
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.370
- **Median Q (composite search score)**: 0.134
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.548


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88806,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.18989,"descend_grasp.grasp_height":0.00129,"descend_place.place_height":0.03302,"lift_object.lift_height":0.11291,"release_object.release_duration":0.46915,"transport_goal.transport_height":0.05211},"optimized_scores":{"best_composite_score":0.13444,"best_fitness_score":0.58444,"best_task_score":0.21099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2199.0,"contact_point_centroid":[0.51312,0.04907,-0.00238],"force_p95":0.16057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49136,"mean_force":0.14652,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51353,0.04077,0.17518]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.51059,-0.02202,-0.00112],"force_p95":0.51607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68561,"mean_force":0.09129,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49888,-0.02241,0.02854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9510.0,"contact_point_centroid":[0.49875,-0.00343,0.07396],"force_p95":0.10793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33905,"mean_force":0.068,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49623,-0.02233,0.07217]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10393.0,"contact_point_centroid":[0.49885,-0.04111,0.07271],"force_p95":0.10232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31181,"mean_force":0.06319,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49626,-0.02233,0.07147]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3845.0,"contact_point_centroid":[0.50361,0.01422,0.13693],"force_p95":0.14844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30905,"mean_force":0.09427,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.49899,-0.00385,0.13866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3270.0,"contact_point_centroid":[0.50311,-0.02307,0.13666],"force_p95":0.17369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25532,"mean_force":0.10215,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.49873,-0.00471,0.13798]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02282,-0.00205],"force_p95":0.13873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18036,"mean_force":0.12706,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50162,-0.02248,0.0281]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.5137,-0.02302,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50331,-0.00912,0.26408]},{"body_a":"world","body_b":"grasp_target","contact_count":2360.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50734,-0.02086,0.13062]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51319,0.0498,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53382,0.10519,0.21704]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51319,0.0498,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54438,0.14084,0.24395]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.501,-0.00325,0.02958],"force_p95":0.07744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11841,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.02245,0.02682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.50105,-0.04154,0.02865],"force_p95":0.06946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08606,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.02245,0.02683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2139.0,"contact_point_centroid":[0.51446,0.04259,0.17899],"force_p95":0.01161,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51415,0.04259,0.1767]},{"body_a":"left_finger","body_b":"right_finger","contact_count":229.0,"contact_point_centroid":[0.5468,0.14151,0.24168],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.00982,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54646,0.1415,0.23927]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4274.0,"contact_point_centroid":[0.53418,0.10508,0.21923],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53378,0.10507,0.21696]}],"total_contact_groups":16},"final_pose_error":0.01803,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.51319,0.0498,0.01602],"final_tcp_position":[0.54752,0.14157,0.24159],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":32.23268,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2360.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50844,-0.01916,0.22741],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13505,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.18036,"subtask_id":"reach_object","tcp_end":[0.50874,-0.02264,0.03584],"tcp_start":[0.50844,-0.01916,0.22741],"tcp_to_object_dist_end":0.01101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51356,-0.02234,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26534,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.11505,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20038.0,"raw_peak_contact_force":0.68561,"tcp_end":[0.5004,-0.02245,0.02679],"tcp_start":[0.50874,-0.02264,0.03584],"tcp_to_object_dist_end":0.01319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.51346,-0.02221,0.11637],"object_pos_start":[0.51356,-0.02234,0.02581],"object_to_goal_dist_end":0.20745,"object_to_goal_dist_start":0.26534,"object_z_max":0.11627,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11453.0,"raw_peak_contact_force":1.49136,"tcp_end":[0.49632,-0.02233,0.12773],"tcp_start":[0.5004,-0.02245,0.02679],"tcp_to_object_dist_end":0.02057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51319,0.0498,0.01602],"object_pos_start":[0.51346,-0.02221,0.11637],"object_to_goal_dist_end":0.23339,"object_to_goal_dist_start":0.20745,"object_z_max":0.12787,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8274.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5208,0.06204,0.19297],"tcp_start":[0.49632,-0.02233,0.12773],"tcp_to_object_dist_end":0.17754,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51319,0.0498,0.01602],"object_pos_start":[0.51319,0.0498,0.01602],"object_to_goal_dist_end":0.23339,"object_to_goal_dist_start":0.23339,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54752,0.14157,0.24159],"tcp_start":[0.5208,0.06204,0.19297],"tcp_to_object_dist_end":0.24593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51319,0.0498,0.01602],"object_pos_start":[0.51319,0.0498,0.01602],"object_to_goal_dist_end":0.23339,"object_to_goal_dist_start":0.23339,"object_z_max":0.01602,"peak_contact_force":32.23268,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":968.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.54321,0.14046,0.2642],"tcp_start":[0.54752,0.14157,0.24159],"tcp_to_object_dist_end":0.26592,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81343,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.06346,"descend_grasp.grasp_height":0.01697,"descend_place.place_height":0.03954,"lift_object.lift_height":0.10489,"release_object.release_duration":0.53247,"transport_goal.transport_height":0.06021},"optimized_scores":{"best_composite_score":0.20154,"best_fitness_score":0.65154,"best_task_score":0.36999},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3392.0,"contact_point_centroid":[0.54777,0.17514,-0.00225],"force_p95":0.12809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49358,"mean_force":0.13654,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54294,0.20245,0.17084]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.49849,0.0422,-0.00122],"force_p95":0.26701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45523,"mean_force":0.06788,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48647,0.04305,0.04446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9174.0,"contact_point_centroid":[0.48654,0.06174,0.08357],"force_p95":0.10315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30661,"mean_force":0.06502,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48405,0.04284,0.08185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8854.0,"contact_point_centroid":[0.48663,0.02395,0.08667],"force_p95":0.10352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30074,"mean_force":0.06616,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48402,0.04283,0.08446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":407.0,"contact_point_centroid":[0.52882,0.13389,0.16204],"force_p95":0.24063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28187,"mean_force":0.13516,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52314,0.1522,0.16531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":849.0,"contact_point_centroid":[0.53034,0.17108,0.16375],"force_p95":0.1667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26838,"mean_force":0.08793,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52348,0.15389,0.16493]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04482,-0.00215],"force_p95":0.16502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22696,"mean_force":0.13376,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48914,0.0433,0.0438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11953.0,"contact_point_centroid":[0.50777,0.07773,0.15037],"force_p95":0.10861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15431,"mean_force":0.07816,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50195,0.09643,0.14933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.48856,0.02399,0.04537],"force_p95":0.08182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15328,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48801,0.0432,0.04257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12971.0,"contact_point_centroid":[0.50824,0.1161,0.1505],"force_p95":0.09538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15099,"mean_force":0.07172,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50236,0.09748,0.14967]},{"body_a":"world","body_b":"grasp_target","contact_count":2492.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4975,0.02058,0.20028]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4955,0.04273,0.07643]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54781,0.17507,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5533,0.23317,0.17831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.48856,0.06237,0.04438],"force_p95":0.07475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07737,"mean_force":0.04437,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48801,0.0432,0.04258]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3355.0,"contact_point_centroid":[0.54441,0.2049,0.17354],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54399,0.20487,0.17128]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.5565,0.2344,0.17644],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5558,0.23437,0.17415]}],"total_contact_groups":16},"final_pose_error":0.01567,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54781,0.17507,0.01602],"final_tcp_position":[0.55711,0.23476,0.17683],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":684.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49706,0.04174,0.10174],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15743,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10910.0,"raw_peak_contact_force":0.22696,"subtask_id":"reach_object","tcp_end":[0.49592,0.04391,0.0512],"tcp_start":[0.49706,0.04174,0.10174],"tcp_to_object_dist_end":0.02575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04359,0.02549],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24336,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":167951.73011,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18168.0,"raw_peak_contact_force":0.45523,"tcp_end":[0.48798,0.0432,0.04254],"tcp_start":[0.49592,0.04391,0.0512],"tcp_to_object_dist_end":0.02155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":574.0,"n_steps_budget":660.0,"object_pos_end":[0.49688,0.04317,0.11192],"object_pos_start":[0.50115,0.04359,0.02549],"object_to_goal_dist_end":0.21554,"object_to_goal_dist_start":0.24336,"object_z_max":0.1118,"peak_contact_force":0.13554,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24924.0,"raw_peak_contact_force":0.15431,"tcp_end":[0.48403,0.04284,0.13556],"tcp_start":[0.48798,0.0432,0.04254],"tcp_to_object_dist_end":0.02691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52777,0.14805,0.1352],"object_pos_start":[0.49688,0.04317,0.11192],"object_to_goal_dist_end":0.10416,"object_to_goal_dist_start":0.21554,"object_z_max":0.13519,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8003.0,"raw_peak_contact_force":1.49358,"subtask_id":"reach_goal","tcp_end":[0.52246,0.14802,0.1667],"tcp_start":[0.48403,0.04284,0.13556],"tcp_to_object_dist_end":0.03194,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54781,0.17507,0.01602],"object_pos_start":[0.52777,0.14805,0.1352],"object_to_goal_dist_end":0.14914,"object_to_goal_dist_start":0.10416,"object_z_max":0.1352,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55711,0.23476,0.17683],"tcp_start":[0.52246,0.14802,0.1667],"tcp_to_object_dist_end":0.17178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54781,0.17507,0.01602],"object_pos_start":[0.54781,0.17507,0.01602],"object_to_goal_dist_end":0.14914,"object_to_goal_dist_start":0.14914,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2492.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.55184,0.23247,0.19821],"tcp_start":[0.55711,0.23476,0.17683],"tcp_to_object_dist_end":0.19106,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88462,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.17776,"descend_grasp.grasp_height":0.00262,"descend_place.place_height":0.03038,"lift_object.lift_height":0.11433,"release_object.release_duration":0.85531,"transport_goal.transport_height":0.05069},"optimized_scores":{"best_composite_score":0.1255,"best_fitness_score":0.5755,"best_task_score":0.19131},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2203.0,"contact_point_centroid":[0.50021,0.04044,-0.00239],"force_p95":0.16221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45758,"mean_force":0.14337,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51121,0.03757,0.16159]},{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.47289,-0.01934,-0.0011],"force_p95":0.44928,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63278,"mean_force":0.07901,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46269,-0.01961,0.03149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9755.0,"contact_point_centroid":[0.46247,-0.00062,0.07707],"force_p95":0.10506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30454,"mean_force":0.06597,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46018,-0.01954,0.07509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10325.0,"contact_point_centroid":[0.46254,-0.03841,0.07591],"force_p95":0.10223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2949,"mean_force":0.06308,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46019,-0.01954,0.07436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3642.0,"contact_point_centroid":[0.4785,0.01576,0.13717],"force_p95":0.14367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25096,"mean_force":0.09782,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.47312,-0.0025,0.13875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3435.0,"contact_point_centroid":[0.47788,-0.02176,0.13701],"force_p95":0.15978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23866,"mean_force":0.10251,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.47233,-0.00341,0.13831]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02003,-0.00204],"force_p95":0.13601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17612,"mean_force":0.12632,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46519,-0.01967,0.03085]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48832,-0.008,0.25941]},{"body_a":"world","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47319,-0.01832,0.12639]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50026,0.0406,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55943,0.08969,0.18167]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50026,0.0406,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58398,0.11738,0.19544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.46377,-0.00039,0.03235],"force_p95":0.06566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09412,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.01964,0.02975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46364,-0.03889,0.03186],"force_p95":0.06464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08704,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.01964,0.02976]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2054.0,"contact_point_centroid":[0.5137,0.03991,0.16531],"force_p95":0.01149,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01065,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51348,0.03991,0.16297]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4238.0,"contact_point_centroid":[0.55988,0.08976,0.18395],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5595,0.08976,0.1817]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.58688,0.11803,0.19366],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58656,0.11802,0.19131]}],"total_contact_groups":16},"final_pose_error":0.0655,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50026,0.0406,0.01602],"final_tcp_position":[0.58779,0.11814,0.19392],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9749.00575,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47692,-0.01693,0.2171],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13424,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12266.0,"raw_peak_contact_force":0.17612,"subtask_id":"reach_object","tcp_end":[0.47189,-0.01981,0.03752],"tcp_start":[0.47692,-0.01693,0.2171],"tcp_to_object_dist_end":0.01227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01967,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.11284,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20203.0,"raw_peak_contact_force":0.63278,"tcp_end":[0.46405,-0.01964,0.02972],"tcp_start":[0.47189,-0.01981,0.03752],"tcp_to_object_dist_end":0.01261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.47619,-0.01942,0.11904],"object_pos_start":[0.47604,-0.01967,0.02583],"object_to_goal_dist_end":0.24706,"object_to_goal_dist_start":0.28826,"object_z_max":0.11894,"peak_contact_force":9749.00575,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11334.0,"raw_peak_contact_force":1.45758,"tcp_end":[0.46019,-0.01952,0.13269],"tcp_start":[0.46405,-0.01964,0.02972],"tcp_to_object_dist_end":0.02103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50026,0.0406,0.01602],"object_pos_start":[0.47619,-0.01942,0.11904],"object_to_goal_dist_end":0.24808,"object_to_goal_dist_start":0.24706,"object_z_max":0.12344,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8238.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.52874,0.0557,0.17222],"tcp_start":[0.46019,-0.01952,0.13269],"tcp_to_object_dist_end":0.15949,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50026,0.0406,0.01602],"object_pos_start":[0.50026,0.0406,0.01602],"object_to_goal_dist_end":0.24808,"object_to_goal_dist_start":0.24808,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58779,0.11814,0.19392],"tcp_start":[0.52874,0.0557,0.17222],"tcp_to_object_dist_end":0.21289,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50026,0.0406,0.01602],"object_pos_start":[0.50026,0.0406,0.01602],"object_to_goal_dist_end":0.24808,"object_to_goal_dist_start":0.24808,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.5825,0.11701,0.21534],"tcp_start":[0.58779,0.11814,0.19392],"tcp_to_object_dist_end":0.22877,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```