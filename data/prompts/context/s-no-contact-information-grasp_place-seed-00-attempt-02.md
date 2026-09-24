## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0357 | 0.27 | ✅ accepted |
| 1 | approach → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1914 | 0.17 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1716 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.036) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: descend_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
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
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: reach_grasp
- id: lift_object
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
    tolerance: 0.03
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
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_object
- id: transport_to_goal
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
    - 0.05
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descent_z:
      type: scalar
      range:
      - -0.05
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
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
    release_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_from_place
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
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_z: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract_from_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.036
- **task_score** (E): 0.268
- **fitness_score**: 0.594  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1619 |
| descend_grasp | 1.00 | 0.0872 |
| grasp_object | 0.00 | 0.0000 |
| lift_object | 1.00 | 0.1719 |
| transport_to_goal | 1.00 | 0.1901 |
| descend_to_place | 1.00 | 0.0758 |
| release_object | 1.00 | 0.0211 |
| retract_from_place | 1.00 | 0.1121 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.142) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.001, 0.142)→(0.492, 0.001, 0.055) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 0.00 / guard_failure | (0.488, 0.000, 0.050)→(0.488, 0.000, 0.050) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.488, 0.000, 0.050)→(0.493, 0.001, 0.221) | (0.497, 0.001, 0.026)→(0.507, 0.000, 0.193) | 0.266→0.207 |
| transport_to_goal | approach | 1.00 / step_budget | (0.493, 0.001, 0.221)→(0.573, 0.164, 0.249) | (0.507, 0.000, 0.193)→(0.544, 0.100, 0.087) | 0.207→0.145 |
| descend_to_place | descend | 1.00 / step_budget | (0.573, 0.164, 0.249)→(0.578, 0.178, 0.175) | (0.544, 0.100, 0.087)→(0.551, 0.114, 0.010) | 0.145→0.210 |
| release_object | release | 1.00 / step_budget | (0.578, 0.178, 0.175)→(0.572, 0.176, 0.195) | (0.551, 0.114, 0.010)→(0.551, 0.114, 0.016) | 0.210→0.204 |
| retract_from_place | retract | 1.00 / step_budget | (0.572, 0.176, 0.195)→(0.580, 0.183, 0.307) | (0.551, 0.114, 0.016)→(0.551, 0.114, 0.016) | 0.204→0.204 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.368
- phase_score: 0.468
- phase_breakdown.lift_object_score: 0.198
- phase_breakdown.place_goal_score: 0.700
- phase_breakdown.reach_grasp_score: 0.292
- grasp_place_fitness: 0.644

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.644
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.368
- **Median Q (composite search score)**: -0.043
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.388


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89143,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09729,"approach_object.generator.speed":0.13116,"descend_grasp.grasp_z":0.02017,"descend_to_place.descent_z":-0.01663,"lift_object.lift_height":0.21975,"release_object.release_time":0.26582,"retract_from_place.retract_speed":0.183,"transport_to_goal.arc_height":0.02607,"transport_to_goal.transport_speed":0.08822},"optimized_scores":{"best_composite_score":-0.04332,"best_fitness_score":0.58668,"best_task_score":0.25064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.57786,0.16076,-0.00634],"force_p95":1.57899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84765,"mean_force":1.15453,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5485,0.14032,0.22374]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57696,0.16318,-0.00344],"force_p95":0.3768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9243,"mean_force":0.14203,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54489,0.14058,0.22256]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.51214,-0.02219,-0.0015],"force_p95":0.34775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37699,"mean_force":0.09982,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50246,-0.0223,0.05003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5343.0,"contact_point_centroid":[0.50622,-0.00325,0.12247],"force_p95":0.11226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28093,"mean_force":0.0702,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50442,-0.02229,0.12202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5940.0,"contact_point_centroid":[0.50593,-0.04125,0.12209],"force_p95":0.10904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27828,"mean_force":0.06467,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50439,-0.02229,0.12149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2999.0,"contact_point_centroid":[0.52903,0.05396,0.24805],"force_p95":0.1436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26055,"mean_force":0.09093,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52282,0.0353,0.24791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3538.0,"contact_point_centroid":[0.53003,0.02212,0.24921],"force_p95":0.11828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22347,"mean_force":0.08006,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52411,0.0405,0.24974]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51371,-0.02293,-0.00208],"force_p95":0.14093,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18143,"mean_force":0.12834,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50411,-0.02235,0.0494]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.5137,-0.02302,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50351,-0.00949,0.22423]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4958.0,"contact_point_centroid":[0.50459,-0.00313,0.04961],"force_p95":0.07819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13717,"mean_force":0.0524,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50367,-0.02233,0.0489]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50722,-0.02101,0.09959]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.57701,0.1632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.54665,0.14448,0.29118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5911.0,"contact_point_centroid":[0.50376,-0.04139,0.04974],"force_p95":0.06912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08023,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50367,-0.02233,0.04891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.55282,0.11062,0.26059],"force_p95":0.06755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06755,"mean_force":0.06755,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54526,0.12353,0.26785]},{"body_a":"left_finger","body_b":"right_finger","contact_count":82.0,"contact_point_centroid":[0.54694,0.14106,0.21873],"force_p95":0.01606,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.0119,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54637,0.14104,0.21628]}],"total_contact_groups":15},"final_pose_error":0.02999,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.57701,0.1632,0.01602],"final_tcp_position":[0.55111,0.14918,0.34225],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.5085,-0.01966,0.14609],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12023,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50854,-0.02244,0.0545],"tcp_start":[0.5085,-0.01966,0.14609],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51364,-0.02248,0.02576],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26546,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50365,-0.02233,0.04888],"tcp_start":[0.50365,-0.02233,0.04888],"tcp_to_object_dist_end":0.02519,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.52507,-0.02266,0.18911],"object_pos_start":[0.51364,-0.02247,0.02577],"object_to_goal_dist_end":0.17975,"object_to_goal_dist_start":0.26544,"object_z_max":0.18865,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50965,-0.02236,0.21603],"tcp_start":[0.50365,-0.02233,0.04888],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.55591,0.11975,0.22947],"object_pos_start":[0.52507,-0.02266,0.18911],"object_to_goal_dist_end":0.03282,"object_to_goal_dist_start":0.17975,"object_z_max":0.23715,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.54526,0.12353,0.26785],"tcp_start":[0.50965,-0.02236,0.21603],"tcp_to_object_dist_end":0.04001,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":98.0,"n_steps_budget":1000.0,"object_pos_end":[0.57753,0.16242,-0.00226],"object_pos_start":[0.55591,0.11975,0.22947],"object_to_goal_dist_end":0.22573,"object_to_goal_dist_start":0.03282,"object_z_max":0.22947,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54875,0.14133,0.22126],"tcp_start":[0.54526,0.12353,0.26785],"tcp_to_object_dist_end":0.22635,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57701,0.1632,0.01602],"object_pos_start":[0.57753,0.16242,-0.00226],"object_to_goal_dist_end":0.20756,"object_to_goal_dist_start":0.22573,"object_z_max":0.01676,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.54365,0.14017,0.24296],"tcp_start":[0.54875,0.14133,0.22126],"tcp_to_object_dist_end":0.23053,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":206.0,"n_steps_budget":600.0,"object_pos_end":[0.57701,0.1632,0.01602],"object_pos_start":[0.57701,0.1632,0.01602],"object_to_goal_dist_end":0.20756,"object_to_goal_dist_start":0.20756,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55111,0.14918,0.34225],"tcp_start":[0.54365,0.14017,0.24296],"tcp_to_object_dist_end":0.32756,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17143,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09374,"approach_object.generator.speed":0.1423,"descend_grasp.grasp_z":0.02001,"descend_to_place.descent_z":-0.0336,"lift_object.lift_height":0.20341,"release_object.release_time":0.18117,"retract_from_place.retract_speed":0.1077,"transport_to_goal.arc_height":0.0778,"transport_to_goal.transport_speed":0.11607},"optimized_scores":{"best_composite_score":0.01445,"best_fitness_score":0.64445,"best_task_score":0.36785},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":575.0,"contact_point_centroid":[0.54479,0.17414,-0.00413],"force_p95":0.8871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01847,"mean_force":0.21779,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54457,0.18917,0.24907]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.49932,0.04311,-0.00167],"force_p95":0.34649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38438,"mean_force":0.09927,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49037,0.04319,0.05058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5080.0,"contact_point_centroid":[0.49354,0.02415,0.1186],"force_p95":0.13139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32541,"mean_force":0.06727,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49243,0.0432,0.11839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1617.0,"contact_point_centroid":[0.50871,0.08203,0.22633],"force_p95":0.15954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29195,"mean_force":0.09104,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5027,0.06398,0.22664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5424.0,"contact_point_centroid":[0.49361,0.06191,0.11709],"force_p95":0.11402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28979,"mean_force":0.06477,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49233,0.04319,0.11654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.50791,0.04315,0.22385],"force_p95":0.15701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22761,"mean_force":0.09154,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50199,0.06177,0.22465]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50127,0.04497,-0.0022],"force_p95":0.16991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21717,"mean_force":0.13657,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49202,0.04336,0.04974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4941.0,"contact_point_centroid":[0.4911,0.02416,0.04967],"force_p95":0.09111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14583,"mean_force":0.0566,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49159,0.04332,0.04926]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.50118,0.04505,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49834,0.01868,0.22214]},{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.54445,0.1741,-0.00199],"force_p95":0.1228,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12324,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55702,0.23175,0.17448]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4958,0.04109,0.09762]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54445,0.1741,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55412,0.23662,0.13103]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.54445,0.1741,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.55543,0.23861,0.2079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6011.0,"contact_point_centroid":[0.49165,0.06228,0.04997],"force_p95":0.07334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0752,"mean_force":0.04357,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49159,0.04332,0.04927]},{"body_a":"left_finger","body_b":"right_finger","contact_count":488.0,"contact_point_centroid":[0.54802,0.19768,0.24712],"force_p95":0.01327,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01459,"mean_force":0.01086,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54741,0.19766,0.24497]},{"body_a":"left_finger","body_b":"right_finger","contact_count":656.0,"contact_point_centroid":[0.55742,0.23171,0.17708],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.557,0.23169,0.17491]}],"total_contact_groups":17},"final_pose_error":0.02957,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54445,0.1741,0.01602],"final_tcp_position":[0.56062,0.24241,0.26756],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49777,0.03867,0.14203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11623,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.49635,0.04373,0.05462],"tcp_start":[0.49777,0.03867,0.14203],"tcp_to_object_dist_end":0.02904,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50119,0.04383,0.02533],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24323,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.49157,0.04331,0.04924],"tcp_start":[0.49157,0.04331,0.04924],"tcp_to_object_dist_end":0.02578,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.51126,0.04469,0.17137],"object_pos_start":[0.50121,0.04383,0.02533],"object_to_goal_dist_end":0.20857,"object_to_goal_dist_start":0.24323,"object_z_max":0.17091,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.49708,0.04345,0.19923],"tcp_start":[0.49157,0.04331,0.04924],"tcp_to_object_dist_end":0.03128,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.54445,0.17411,0.01599],"object_pos_start":[0.51126,0.04469,0.17137],"object_to_goal_dist_end":0.15003,"object_to_goal_dist_start":0.20857,"object_z_max":0.21884,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55651,0.22561,0.21802],"tcp_start":[0.49708,0.04345,0.19923],"tcp_to_object_dist_end":0.20884,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.54445,0.1741,0.01602],"object_pos_start":[0.54445,0.17411,0.01599],"object_to_goal_dist_end":0.15001,"object_to_goal_dist_start":0.15003,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55909,0.23866,0.13089],"tcp_start":[0.55651,0.22561,0.21802],"tcp_to_object_dist_end":0.13259,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54445,0.1741,0.01602],"object_pos_start":[0.54445,0.1741,0.01602],"object_to_goal_dist_end":0.15001,"object_to_goal_dist_start":0.15001,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.55247,0.23583,0.15109],"tcp_start":[0.55909,0.23866,0.13089],"tcp_to_object_dist_end":0.14872,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":255.0,"n_steps_budget":870.0,"object_pos_end":[0.54445,0.1741,0.01602],"object_pos_start":[0.54445,0.1741,0.01602],"object_to_goal_dist_end":0.15001,"object_to_goal_dist_start":0.15001,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.56062,0.24241,0.26756],"tcp_start":[0.55247,0.23583,0.15109],"tcp_to_object_dist_end":0.26115,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02591,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08804,"approach_object.generator.speed":0.15939,"descend_grasp.grasp_z":0.02019,"descend_to_place.descent_z":-0.03448,"lift_object.lift_height":0.25308,"release_object.release_time":0.39188,"retract_from_place.retract_speed":0.12354,"transport_to_goal.arc_height":0.08341,"transport_to_goal.transport_speed":0.09419},"optimized_scores":{"best_composite_score":-0.07816,"best_fitness_score":0.55184,"best_task_score":0.1844},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1158.0,"contact_point_centroid":[0.53059,0.00465,-0.00315],"force_p95":0.54322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28185,"mean_force":0.16904,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56518,0.08535,0.30511]},{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.4743,-0.01898,-0.00161],"force_p95":0.32507,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36623,"mean_force":0.09723,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46613,-0.01948,0.05175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4786.0,"contact_point_centroid":[0.47038,-0.0005,0.13327],"force_p95":0.14564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33195,"mean_force":0.08629,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4679,-0.01945,0.13459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6627.0,"contact_point_centroid":[0.46965,-0.0378,0.13748],"force_p95":0.11855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27218,"mean_force":0.06755,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.468,-0.01945,0.13734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":343.0,"contact_point_centroid":[0.4823,0.0024,0.25471],"force_p95":0.20193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25945,"mean_force":0.12548,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47555,-0.01602,0.25602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":579.0,"contact_point_centroid":[0.48317,-0.03196,0.25807],"force_p95":0.15578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24748,"mean_force":0.08485,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47664,-0.01465,0.25839]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.47618,-0.02019,-0.00212],"force_p95":0.15726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17952,"mean_force":0.13143,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46779,-0.01952,0.05083]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.47616,-0.02015,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48796,-0.00836,0.22018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5238.0,"contact_point_centroid":[0.46775,-0.00032,0.0507],"force_p95":0.09686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13599,"mean_force":0.05439,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46739,-0.01951,0.05041]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4729,-0.01843,0.09577]},{"body_a":"world","body_b":"grasp_target","contact_count":608.0,"contact_point_centroid":[0.53054,0.00472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62025,0.14925,0.21726]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53054,0.00472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62001,0.15336,0.17208]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.53054,0.00472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.62225,0.155,0.24957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5901.0,"contact_point_centroid":[0.46743,-0.03834,0.05079],"force_p95":0.06892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08497,"mean_force":0.04334,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46739,-0.01951,0.05041]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1095.0,"contact_point_centroid":[0.5714,0.09201,0.307],"force_p95":0.01269,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01079,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57114,0.09201,0.30463]},{"body_a":"left_finger","body_b":"right_finger","contact_count":650.0,"contact_point_centroid":[0.62058,0.14925,0.21947],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62024,0.14924,0.21734]}],"total_contact_groups":17},"final_pose_error":0.02986,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53054,0.00472,0.01602],"final_tcp_position":[0.62812,0.15771,0.31038],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47621,-0.01733,0.13744],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11146,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47198,-0.01962,0.05526],"tcp_start":[0.47621,-0.01733,0.13744],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01957,0.02547],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28837,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46737,-0.01951,0.05039],"tcp_start":[0.46737,-0.01951,0.05039],"tcp_to_object_dist_end":0.02641,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.48598,-0.02091,0.2182],"object_pos_start":[0.4761,-0.01959,0.02541],"object_to_goal_dist_end":0.23321,"object_to_goal_dist_start":0.28842,"object_z_max":0.21772,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47285,-0.0195,0.2487],"tcp_start":[0.46737,-0.01951,0.05039],"tcp_to_object_dist_end":0.03324,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.53054,0.00472,0.01602],"object_pos_start":[0.48598,-0.02091,0.2182],"object_to_goal_dist_end":0.2536,"object_to_goal_dist_start":0.23321,"object_z_max":0.23464,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.61732,0.14432,0.26149],"tcp_start":[0.47285,-0.0195,0.2487],"tcp_to_object_dist_end":0.29542,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.53054,0.00472,0.01602],"object_pos_start":[0.53054,0.00472,0.01602],"object_to_goal_dist_end":0.2536,"object_to_goal_dist_start":0.2536,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.62473,0.15458,0.17326],"tcp_start":[0.61732,0.14432,0.26149],"tcp_to_object_dist_end":0.23676,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53054,0.00472,0.01602],"object_pos_start":[0.53054,0.00472,0.01602],"object_to_goal_dist_end":0.2536,"object_to_goal_dist_start":0.2536,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.61845,0.15287,0.19161],"tcp_start":[0.62473,0.15458,0.17326],"tcp_to_object_dist_end":0.24598,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":266.0,"n_steps_budget":780.0,"object_pos_end":[0.53054,0.00472,0.01602],"object_pos_start":[0.53054,0.00472,0.01602],"object_to_goal_dist_end":0.2536,"object_to_goal_dist_start":0.2536,"object_z_max":0.01602,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62812,0.15771,0.31038],"tcp_start":[0.61845,0.15287,0.19161],"tcp_to_object_dist_end":0.34579,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```