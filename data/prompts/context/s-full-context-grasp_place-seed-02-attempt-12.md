## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2399 | 0.76 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3599 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2200 | 0.36 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.0009 | 0.48 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1488 | 0.40 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=0.240) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_object
  target_entity: object
  weight: 0.2
phases:
- id: approach_above_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descent_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: grasp_object
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
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_object
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: lift_object
- id: approach_above_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.240
- **task_score** (E): 0.760
- **fitness_score**: 0.860  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0379 |
| descend_to_grasp | 1.00 | 1.00 | 0.2393 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 0.67 | 1.00 | 0.0992 |
| approach_above_goal | 0.67 | 1.00 | 0.2827 |
| descend_to_place | 1.00 | 1.00 | 0.1136 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.008, 0.273) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.125 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.497, -0.008, 0.273)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.125 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.481, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.140 | 0.201 |
| lift | lift | 0.67 / step_budget | (0.481, -0.015, 0.026)→(0.476, -0.015, 0.125) | (0.493, -0.015, 0.026)→(0.487, -0.015, 0.116) | 0.281→0.251 | 1.00 / 38.333 | 0.084 | 0.679 |
| approach_above_goal | approach | 0.67 / step_budget | (0.476, -0.015, 0.125)→(0.618, 0.157, 0.283) | (0.487, -0.015, 0.116)→(0.605, 0.144, 0.168) | 0.251→0.128 | 1.00 / 23.000 | 0.100 | 0.791 |
| descend_to_place | descend | 1.00 / step_budget | (0.618, 0.157, 0.283)→(0.630, 0.172, 0.172) | (0.605, 0.144, 0.168)→(0.615, 0.157, 0.098) | 0.128→0.073 | 1.00 / 22.333 | 3249.746 | 0.169 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.351
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.476
- phase_breakdown.approach_object_score: 0.120
- phase_breakdown.grasp_object_score: 0.798
- phase_breakdown.lift_object_score: 0.363
- phase_breakdown.approach_goal_score: 0.279
- phase_breakdown.place_object_score: 0.820
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.361
- **K-run variance**: 0.0297
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.364


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27132,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.19,"approach_above_goal.approach_goal_speed":0.04479,"approach_above_object.approach_height":0.24906,"approach_above_object.approach_speed":0.17513,"descend_to_grasp.descent_speed":0.10348,"descend_to_grasp.grasp_z_tolerance":0.01314,"descend_to_place.place_speed":0.06986,"descend_to_place.place_z_tolerance":0.00571,"lift.lift_height":0.10817,"lift.lift_speed":0.05123},"optimized_scores":{"best_composite_score":0.36149,"best_fitness_score":0.98149,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.472,-0.01871,-0.00117],"force_p95":0.49118,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67378,"mean_force":0.11511,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46308,-0.01923,0.02906]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20910.0,"contact_point_centroid":[0.46037,-0.0383,0.07693],"force_p95":0.07105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28082,"mean_force":0.04879,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46054,-0.01916,0.07514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20492.0,"contact_point_centroid":[0.46036,2e-05,0.07756],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27078,"mean_force":0.04927,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46055,-0.01916,0.07554]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01998,-0.00208],"force_p95":0.14607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.224,"mean_force":0.1291,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46576,-0.01929,0.02849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7257.0,"contact_point_centroid":[0.61109,0.15721,0.25366],"force_p95":0.08584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16834,"mean_force":0.05804,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6088,0.13831,0.25341]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6711.0,"contact_point_centroid":[0.6113,0.11974,0.25183],"force_p95":0.09682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1556,"mean_force":0.06151,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60924,0.13878,0.25161]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.47616,-0.02015,-0.00123],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12402,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49507,-0.00327,0.29553]},{"body_a":"world","body_b":"grasp_target","contact_count":3092.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13005,"mean_force":0.12271,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4795,-0.01387,0.15994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19847.0,"contact_point_centroid":[0.52383,0.02984,0.21747],"force_p95":0.07564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1244,"mean_force":0.05013,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52318,0.04891,0.21637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18874.0,"contact_point_centroid":[0.5259,0.07,0.22047],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10826,"mean_force":0.05235,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52507,0.05086,0.21912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5284.0,"contact_point_centroid":[0.46406,-2e-05,0.02913],"force_p95":0.06545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10358,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46464,-0.01926,0.02739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5440.0,"contact_point_centroid":[0.46408,-0.03856,0.029],"force_p95":0.06574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08245,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46465,-0.01926,0.02739]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62852,0.1543,0.17593],"final_tcp_position":[0.62407,0.15433,0.19471],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.67378,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02595],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28842,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.13053,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":172.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48865,-0.00831,0.28868],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02595],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28842,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3092.0,"raw_peak_contact_force":0.13005,"subtask_id":"grasp_object","tcp_end":[0.47249,-0.01942,0.03517],"tcp_start":[0.48865,-0.00831,0.28868],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01934,0.02571],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28812,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14315,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12524.0,"raw_peak_contact_force":0.224,"subtask_id":"grasp_object","tcp_end":[0.46462,-0.01926,0.02736],"tcp_start":[0.47249,-0.01942,0.03517],"tcp_to_object_dist_end":0.01154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46929,-0.01916,0.11515],"object_pos_start":[0.47604,-0.01934,0.02571],"object_to_goal_dist_end":0.25239,"object_to_goal_dist_start":0.28812,"object_z_max":0.11504,"peak_contact_force":0.07446,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41566.0,"raw_peak_contact_force":0.67378,"subtask_id":"lift_object","tcp_end":[0.46059,-0.01915,0.12424],"tcp_start":[0.46462,-0.01926,0.02736],"tcp_to_object_dist_end":0.01258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60482,0.12217,0.30352],"object_pos_start":[0.46929,-0.01916,0.11515],"object_to_goal_dist_end":0.12231,"object_to_goal_dist_start":0.25239,"object_z_max":0.30335,"peak_contact_force":0.09436,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38721.0,"raw_peak_contact_force":0.1244,"subtask_id":"approach_goal","tcp_end":[0.59449,0.12215,0.31967],"tcp_start":[0.46059,-0.01915,0.12424],"tcp_to_object_dist_end":0.01918,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.62852,0.1543,0.17593],"object_pos_start":[0.60482,0.12217,0.30352],"object_to_goal_dist_end":0.01519,"object_to_goal_dist_start":0.12231,"object_z_max":0.30357,"peak_contact_force":0.08949,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13968.0,"raw_peak_contact_force":0.16834,"subtask_id":"place_object","tcp_end":[0.62407,0.15433,0.19471],"tcp_start":[0.59449,0.12215,0.31967],"tcp_to_object_dist_end":0.0193,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16236,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.10042,"approach_above_goal.approach_goal_speed":0.04779,"approach_above_object.approach_height":0.24913,"approach_above_object.approach_speed":0.14527,"descend_to_grasp.descent_speed":0.09618,"descend_to_grasp.grasp_z_tolerance":0.00837,"descend_to_place.place_speed":0.05689,"descend_to_place.place_z_tolerance":0.01382,"lift.lift_height":0.13201,"lift.lift_speed":0.05543},"optimized_scores":{"best_composite_score":0.36215,"best_fitness_score":0.98215,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.45457,-0.02464,-0.00121],"force_p95":0.46663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64549,"mean_force":0.10507,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44607,-0.02528,0.02958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20801.0,"contact_point_centroid":[0.44345,-0.04436,0.08139],"force_p95":0.07132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2944,"mean_force":0.04896,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44358,-0.02518,0.07955]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21172.0,"contact_point_centroid":[0.4434,-0.00601,0.08203],"force_p95":0.07091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28093,"mean_force":0.04785,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44358,-0.02518,0.08016]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02618,-0.00209],"force_p95":0.1485,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21965,"mean_force":0.12959,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44866,-0.02537,0.02894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3530.0,"contact_point_centroid":[0.62362,0.18154,0.16282],"force_p95":0.09434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21455,"mean_force":0.06555,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62027,0.20044,0.16206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3694.0,"contact_point_centroid":[0.62365,0.21924,0.16307],"force_p95":0.09219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20583,"mean_force":0.06417,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6202,0.20035,0.16311]},{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.45856,-0.02632,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1245,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.4879,-0.00682,0.29269]},{"body_a":"world","body_b":"grasp_target","contact_count":3116.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46357,-0.02045,0.15811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5254.0,"contact_point_centroid":[0.44695,-0.00617,0.0292],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11991,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44758,-0.02533,0.02792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16933.0,"contact_point_centroid":[0.53063,0.06584,0.16592],"force_p95":0.08278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09984,"mean_force":0.05694,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52857,0.08469,0.16483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15293.0,"contact_point_centroid":[0.53354,0.10725,0.16738],"force_p95":0.09069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09361,"mean_force":0.06247,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53143,0.08826,0.16602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.44779,-0.04464,0.0298],"force_p95":0.07159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08616,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44759,-0.02533,0.02792]}],"total_contact_groups":12},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63091,0.20459,0.10168],"final_tcp_position":[0.62384,0.20471,0.12094],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.64549,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02593],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30367,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12241,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.47408,-0.01537,0.28423],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02593],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30367,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3116.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.45519,-0.02559,0.03516],"tcp_start":[0.47408,-0.01537,0.28423],"tcp_to_object_dist_end":0.00977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02547,0.02568],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30316,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14655,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12010.0,"raw_peak_contact_force":0.21965,"subtask_id":"grasp_object","tcp_end":[0.44755,-0.02533,0.02789],"tcp_start":[0.45519,-0.02559,0.03516],"tcp_to_object_dist_end":0.01111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45489,-0.0252,0.12231],"object_pos_start":[0.45845,-0.02547,0.02568],"object_to_goal_dist_end":0.29199,"object_to_goal_dist_start":0.30316,"object_z_max":0.12222,"peak_contact_force":0.09325,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42133.0,"raw_peak_contact_force":0.64549,"subtask_id":"lift_object","tcp_end":[0.44355,-0.02516,0.13159],"tcp_start":[0.44755,-0.02533,0.02789],"tcp_to_object_dist_end":0.01466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":985.0,"n_steps_budget":1000.0,"object_pos_end":[0.62618,0.19718,0.18452],"object_pos_start":[0.45489,-0.0252,0.12231],"object_to_goal_dist_end":0.07137,"object_to_goal_dist_start":0.29199,"object_z_max":0.18447,"peak_contact_force":0.08188,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32226.0,"raw_peak_contact_force":0.09984,"subtask_id":"approach_goal","tcp_end":[0.61907,0.19722,0.2022],"tcp_start":[0.44355,-0.02516,0.13159],"tcp_to_object_dist_end":0.01905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.63091,0.20459,0.10168],"object_pos_start":[0.62618,0.19718,0.18452],"object_to_goal_dist_end":0.01298,"object_to_goal_dist_start":0.07137,"object_z_max":0.18452,"peak_contact_force":0.09408,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7224.0,"raw_peak_contact_force":0.21455,"subtask_id":"place_object","tcp_end":[0.62384,0.20471,0.12094],"tcp_start":[0.61907,0.19722,0.2022],"tcp_to_object_dist_end":0.02051,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72165,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.15297,"approach_above_goal.approach_goal_speed":0.14804,"approach_above_object.approach_height":0.20452,"approach_above_object.approach_speed":0.21049,"descend_to_grasp.descent_speed":0.0921,"descend_to_grasp.grasp_z_tolerance":0.01475,"descend_to_place.place_speed":0.06407,"descend_to_place.place_z_tolerance":0.01386,"lift.lift_height":0.17756,"lift.lift_speed":0.06004},"optimized_scores":{"best_composite_score":-0.00391,"best_fitness_score":0.61609,"best_task_score":0.27853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1537.0,"contact_point_centroid":[0.5853,0.1114,-0.00271],"force_p95":0.34349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14966,"mean_force":0.15933,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.61738,0.12132,0.28451]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.53943,0.0007,-0.00113],"force_p95":0.48032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71819,"mean_force":0.11259,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5277,0.00082,0.02553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18503.0,"contact_point_centroid":[0.52623,-0.01831,0.0744],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31982,"mean_force":0.0552,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52517,0.00078,0.07246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18972.0,"contact_point_centroid":[0.52623,0.01985,0.0733],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31069,"mean_force":0.05416,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52519,0.00078,0.0715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5095.0,"contact_point_centroid":[0.55062,0.01473,0.16125],"force_p95":0.15927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2822,"mean_force":0.084,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.54783,0.03347,0.16182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5979.0,"contact_point_centroid":[0.552,0.0532,0.16268],"force_p95":0.15434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27507,"mean_force":0.07692,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.54874,0.0347,0.16344]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16053,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53097,0.00088,0.02539]},{"body_a":"world","body_b":"grasp_target","contact_count":516.0,"contact_point_centroid":[0.54431,0.00113,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12357,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51383,0.00038,0.27468]},{"body_a":"world","body_b":"grasp_target","contact_count":2604.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53281,0.00089,0.13894]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.58495,0.1114,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64187,0.15351,0.26395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53078,-0.01834,0.02665],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1103,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52972,0.00086,0.02396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53071,0.01994,0.02577],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09675,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52972,0.00086,0.02396]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1468.0,"contact_point_centroid":[0.62021,0.12443,0.29117],"force_p95":0.01205,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01066,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.61987,0.12442,0.28887]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1410.0,"contact_point_centroid":[0.64235,0.15354,0.26576],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64189,0.15353,0.2636]}],"total_contact_groups":14},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58495,0.1114,0.01602],"final_tcp_position":[0.64356,0.15624,0.19984],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9749.05359,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":130.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12261,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":516.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52955,0.00078,0.24745],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2604.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53843,0.00102,0.03403],"tcp_start":[0.52955,0.00078,0.24745],"tcp_to_object_dist_end":0.00994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12965,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16053,"subtask_id":"grasp_object","tcp_end":[0.52969,0.00086,0.02393],"tcp_start":[0.53843,0.00102,0.03403],"tcp_to_object_dist_end":0.01459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53683,0.00075,0.11135],"object_pos_start":[0.54415,0.00072,0.02588],"object_to_goal_dist_end":0.2083,"object_to_goal_dist_start":0.25053,"object_z_max":0.11125,"peak_contact_force":0.08439,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37679.0,"raw_peak_contact_force":0.71819,"subtask_id":"lift_object","tcp_end":[0.52532,0.00079,0.12058],"tcp_start":[0.52969,0.00086,0.02393],"tcp_to_object_dist_end":0.01476,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.58495,0.1114,0.01602],"object_pos_start":[0.53683,0.00075,0.11135],"object_to_goal_dist_end":0.19173,"object_to_goal_dist_start":0.2083,"object_z_max":0.19467,"peak_contact_force":0.12263,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14079.0,"raw_peak_contact_force":2.14966,"subtask_id":"approach_goal","tcp_end":[0.64135,0.15135,0.32638],"tcp_start":[0.52532,0.00079,0.12058],"tcp_to_object_dist_end":0.31796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.58495,0.1114,0.01602],"object_pos_start":[0.58495,0.1114,0.01602],"object_to_goal_dist_end":0.19173,"object_to_goal_dist_start":0.19173,"object_z_max":0.01602,"peak_contact_force":9749.05359,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2730.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.64356,0.15624,0.19984],"tcp_start":[0.64135,0.15135,0.32638],"tcp_to_object_dist_end":0.19808,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```